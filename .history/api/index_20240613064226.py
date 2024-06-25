from flask import Flask, render_template, request, jsonify
import openai, time, paramiko, json
import re
from openai import OpenAI
import os
import nest_asyncio
import langchain
import csv


os.environ["OPENAI_API_KEY"] = "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"
os.environ["ASSISTANTS_VECTOR_STORE_ID"] = "vs_MYM8E6bcdRTLPPVPClXbPmIu"
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_ENDPOINT"]="https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"]="ls__d37e0f8f47024e0da2178e6988062018"
os.environ["LANGCHAIN_PROJECT"]="BFA RAG PROD"
os.environ["COHERE_API_KEY"]="SOWFrKx5FKSSxmbXXrFvFVHJJtyUiOtlWknP2uu6"

nest_asyncio.apply()
print(f"LangChain Version: {langchain.__version__}")

os.environ["OPENAI_API_KEY"] = "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"
os.environ["OPENAI_ASSISTANT_ID"] = "asst_iH4BNc2lFDzn5bjI6n8DkGgs"

assistant_id =  "asst_iH4BNc2lFDzn5bjI6n8DkGgs"
client =  OpenAI()

#placeholder to save and use the intial thread
initial_thread=None

def fetch_url_from_filename(filename, list_bfa, list_cifar):
    """
    Fetch URL from filename based on predefined patterns and lookup in provided lists.


    Args:
    - filename (str): The filename to parse.
    - list_bfa (list): List of BFA records.
    - list_cifar (list): List of CIFAR records.

    Returns:
    - dict: Metadata containing title and link.
    """
    metadata = {}
    case = ""
    result = []

    # Define regex patterns
    uuid_pattern = re.compile(r'^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.txt$')
    post_id_pattern = re.compile(r'^(\d+)\.txt$')
    bfa_pdf_pattern = re.compile(r'^\d{4,}_.+\.pdf$')  # Pattern for bfaPdf
    cifar_pdf_pattern = re.compile(r'^(?!\d{4,}_).+\.pdf$')  # Pattern for cifarPdf
    soq_pattern = re.compile(r'^([a-zA-Z]+)[0-9]+\.txt$')

    # Matching patterns
    if uuid_match := uuid_pattern.match(filename):
        case = "cifarPost"
        uuid = uuid_match.group(1)
        result = [item for item in list_cifar if item['ID'] == uuid]
    elif post_id_match := post_id_pattern.match(filename):
        case = "bfaPost"
        post_id = post_id_match.group(1)
        result = [item for item in list_bfa if item['ID'] == post_id]
    elif bfa_pdf_match := bfa_pdf_pattern.match(filename):
        case = "bfaPdf"
        # Remove the post_id and the underscore
        pdf_title_with_extension = filename.split('_', 1)[1]
        # Remove the file extension
        pdf_title = pdf_title_with_extension.rsplit('.', 1)[0]
        result = [item for item in list_bfa if item['pdf_title'].lower() == pdf_title.lower()]

        # If no matches are found, perform the second search
        if not result:
            result = [item for item in list_bfa if pdf_title.lower() in item['pdf_url'].lower()]

    elif cifar_pdf_match := cifar_pdf_pattern.match(filename):
        case = "cifarPdf"
        pdf_title = filename.rsplit('.', 1)[0]
        result = [item for item in list_cifar if item['pdf_title'].lower() == pdf_title.lower()]
    else:
        case = "soq"
        project_code = filename.split('.')[0]
        metadata["title"] = ""
        metadata["link"] = "See project details for project: " + project_code + " https://docs.google.com/spreadsheets/d/1syWFDXt0BwjkjnVfd6kYl0YSbQTVcLW2E2YWV5lzrsw/edit#gid=393530796"
        return metadata

    # Check results
    if len(result) >= 1:
        item = result[0]  # The only item in the list

        # Set default values
        metadata["link"] = ""
        metadata["title"] = item.get('title', '')

        if case == "bfaPost":
            # If post, fetch URL to post
            metadata["link"] = item.get('guid', '')  # Set default as empty string if 'guid' is not found
        elif case == "cifarPost":
            metadata["link"] = item.get('URL', '')  # Set default as empty string if 'guid' is not found
        elif case in ["cifarPdf", "bfaPdf"]:
            # If PDF, fetch URL to PDF
            metadata["link"] = item.get('pdf_url', '')  # Set default as empty string if 'pdf_url' is not found
        return metadata
    else:
        metadata["title"] = "Failed to fetch the reference original url"
        metadata["link"] = ""  # Explicitly setting link to an empty string
        return metadata

def read_csv(filepath):
    """
    Read a CSV file and return its contents as a list of dictionaries.

    Args:
    - filepath (str): Path to the CSV file.

    Returns:
    - list: List of rows as dictionaries.
    """
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)
    
def consolidate_references(reference_list):
    # Dictionary to track URLs and their reference IDs
    references_by_url = {}
    
    # Define the URL to exclude from grouping
    exclude_url = "https://docs.google.com/spreadsheets/d/1syWFDXt0BwjkjnVfd6kYl0YSbQTVcLW2E2YWV5lzrsw/edit#gid=393530796"
    
    # List to store entries with the excluded URL
    excluded_entries = []
    
    for entry in reference_list:
        parts = entry.split()
        ref_id = parts[0].strip(',')
        url = parts[-1]
        
        # Check if the URL should be excluded
        if url == exclude_url:
            excluded_entries.append(entry)
        else:
            # Collect all unique reference IDs for the same URL
            if url in references_by_url:
                if ref_id not in references_by_url[url]:
                    references_by_url[url].append(ref_id)
            else:
                references_by_url[url] = [ref_id]
    
    # Create a new list for consolidated references
    new_reference_list = []
    for url, ref_ids in sorted(references_by_url.items()):
        # Sort reference IDs to ensure they are ordered numerically
        sorted_ref_ids = sorted(ref_ids, key=int)
        # Format the reference IDs as a comma-separated list, without brackets
        formatted_ref_ids = ", ".join(sorted_ref_ids)
        new_reference_list.append(f"{formatted_ref_ids}  {url}")
    
    # Add excluded entries directly to the final list
    new_reference_list.extend(sorted(excluded_entries))
    
    return new_reference_list



def parseMasterDBData(citations_metadata):
    """
    Parse master database data and update citations metadata.

    Args:
    - citations_metadata (list): List of citation metadata.

    Returns:
    - list: Modified citations.
    """
    modified_citations = []
    BFA_master_db_file_path = 'data/BFA_final_master_pdfs_ok_db.csv'
    CifarWIX_master_db_file_path = 'data/CifarWIX_master_pdfs_ok_db.csv'
    df_BFA = read_csv(BFA_master_db_file_path)
    df_CifarWIX = read_csv(CifarWIX_master_db_file_path)

    for i, citation in enumerate(citations_metadata):
        if 'file_name' in citation:
            reference = fetch_url_from_filename(citation["file_name"], df_BFA, df_CifarWIX)
            modified_citation = citation["reference_id"] + "  " + reference["title"] + "  " + reference["link"]
            #we group all references to the same document on one line
            modified_citations.append(modified_citation)
        else:
            continue
    modified_citations_formatted = consolidate_references(modified_citations)
    return modified_citations_formatted

def check_filename(filename):
    """
    Check the format of the filename.

    Args:
    - filename (str): The filename to check.

    Returns:
    - str: Type of the file ('txt', 'SOQ', 'Invalid format').
    """
    if re.fullmatch(r'\d+\.txt', filename):
        return "txt"
    elif re.fullmatch(r'\w+\d+\.txt', filename):
        return "SOQ"
    else:
        return "Invalid format"


## refactor needed, filename should not have extension since im passing it as a separate variable
def referenceToLink(citations):
    """
    Convert references to links by fetching master DB data.

    Args:
    - citations (list): List of citations.

    Returns:
    - list: Citations with links.
    """
    citationsAsLinks = []
    if len(citations) > 0:
        for text in citations:
            # Splitting the text to easily extract parts
            parts = text.split(' from ')
            ref_id = re.search(r"\[\d+\]", parts[0]).group(0)
            filename_with_extension = parts[-1]  # Last part after 'from' should be the filename with extension
            file_name, file_type = filename_with_extension.rsplit('.', 1)
            
            # Depending on the file type, process the text and collect data
            if file_type == "txt":
                # Process TXT files
                data_dict = {
                    "reference_id": ref_id,
                    "file_name": filename_with_extension,
                    "file_type": file_type
                }
            elif file_type == "pdf":
                # Extract post_id for PDF files
                post_id = file_name.split('_', 1)[0]
                data_dict = {
                    "reference_id": ref_id,
                    "post_id": post_id,
                    "file_name": filename_with_extension,  
                    "file_type": file_type
                }

            # Append the dictionary to the list
            citationsAsLinks.append(data_dict)


        citations = parseMasterDBData(citationsAsLinks)
    return citations

def parseAndSubstituteReferences(message_content):
    """
    Parse and substitute references in the message content.


    Args:
    - message_content (object): The message content object containing annotations.


    Returns:
    - str: Message content with substituted references.
    """
    annotations = message_content.annotations
    citations = []
    for index, annotation in enumerate(annotations):
        message_content.value = message_content.value.replace(annotation.text, f' [{index}]')
        if (file_citation := getattr(annotation, 'file_citation', None)):
            cited_file = client.files.retrieve(file_citation.file_id)
            # if file_citation.quote is not None:
            citations.append(f'[{index}] from {cited_file.filename}')
                # citations.append(f'[{index}] {file_citation.quote} from {cited_file.filename}')
            # else:
            citations.append(f'[{index}] Reference from {cited_file.filename}')
        elif (file_path := getattr(annotation, 'file_path', None)):
            cited_file = client.files.retrieve(file_path.file_id)
            citations.append(f'[{index}] Click <here> to download {cited_file.filename}')
    citations = referenceToLink(citations)
    message_content.value = message_content.value + '\n' + '\n'.join(citations)
    return message_content.value

def assistant_process(dict_from_dataset):
    """
    Process a user question using the assistant.

    Args:
    - dict_from_dataset (dict): Dictionary containing the user's question.

    Returns:
    - str: Assistant's response.
    """
    assistant = client.beta.assistants.retrieve(assistant_id)
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=dict_from_dataset["question"],
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        message_content = messages.data[0].content[0].text
        message_content_with_references = parseAndSubstituteReferences(message_content)
        messages.data[0].content[0].text = message_content_with_references
        print("Assistant:  " +messages.data[0].content[0].text)
        return messages.data[0].content[0].text
    else:
        return f"Run failed with status: {run.status}"

# Initialize Flask app
app = Flask(__name__)

# Set OpenAI API key
openai.api_key =  os.getenv("OPENAI_API_KEY")

# Route to serve the index page
@app.route('/')
def index():
    return render_template('index.html')

# New Route to create a new thread
@app.route('/create_thread', methods=['GET'])
def create_thread():
    try:
        # Create a new chat thread
        thread = openai.beta.threads.create()
        return jsonify({"thread_id": thread.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to handle POST requests
@app.route('/ask', methods=['POST'])
def ask_openai():
    
    data = request.json
    app.logger.info(data)
    thread_id = data.get('thread_id')
    user_input = data.get('input')
    user_files = data.get('file_ids')
    app.logger.info(user_files)
    # Ensure user input is provided
    if not user_input and not user_files:
        return jsonify("No input provided"), 400
    if thread_id == 'None':
        return jsonify("No thread provided"), 400
    try:
        print(f"'User files: '{user_files}")
        # Create message on thread
        if user_files:
        # TBD: This has changed, code needs to be adapted. If 'user_files' is not empty, include it in the call
          thread_message = openai.beta.threads.messages.create(
          thread_id=thread_id,
          role="user",
          content=user_input,
          file_ids=user_files
          )
        else:
        # If 'user_files' is empty, omit it from the call
          thread_message = openai.beta.threads.messages.create(
          thread_id=thread_id,
          role="user",
          content=user_input
          )
        dict_question = {}
        dict_question["question"]=user_input
        response = assistant_process(dict_question)
        # print(jsonify(msgs.data[0].content[0].text))
        return jsonify(response), 200
    except Exception as e:
        print(jsonify(str(e)))
        return jsonify(str(e)), 500

# Route to fetch thread messages
@app.route('/get_thread_messages', methods=['POST'])
def get_thread_messages():
    data = request.json
    thread_id = data.get('thread_id')

    if not thread_id:
        return jsonify("No thread ID provided"), 400

    try:
        # Fetch thread messages
        thread_messages = openai.beta.threads.messages.list(thread_id=thread_id)
        return jsonify(thread_messages.model_dump()['data'])
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/upload_file', methods=['POST'])
def upload_file():
    list_files = []
    for uploaded_file in request.files.getlist('files'):
        print("Uploading file: " + uploaded_file.filename)
        try:
            # Read the file content
            file_content = uploaded_file.read()

            # Upload the file to OpenAI
            openai_file = openai.files.create(
                file=file_content,
                purpose="assistants"
            )

            list_files.append(openai_file.id)

            # Attach the file to the assistant
            # assistant_file = openai.beta.assistants.files.create(
            #     assistant_id="asst_abc123",  # Replace with your assistant's ID
            #     file_id=file_id
            # )
        except Exception as e:
            print(str(e))
            return jsonify({"error": str(e)}), 500
    return jsonify({"file_id": list_files}), 200


    
def run_command(hostname, command):
# Configuration variables
    username = os.environ.get('USERNAME_ENV_VAR')   # Replace with the SSH password
    password = os.environ.get('PASSWORD_ENV_VAR')   # Replace with the SSH username
          
    port = 22   # Replace with the SSH port if different from the default
    # Create the SSH client
    ssh_client = paramiko.SSHClient()
    # Automatically add the server's SSH key (not recommended for production use)
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Connect to the server
    try:
        ssh_client.connect(hostname, port, username, password)
        #print(f"Successfully connected to {hostname}")
        # Execute the uptime command
        stdin, stdout, stderr = ssh_client.exec_command(command)
        # Read the standard output and print it
        output = stdout.read().decode().strip()
        if output != "":           
          return (f"Success: {output}")
        else:
          output = stderr.read().decode().strip()
          return (f"Failure: {output}")
    except paramiko.AuthenticationException:
        print("Authentication failed, please verify your credentials.")
        return ("Authentication failed, please verify your credentials.")
    except paramiko.SSHException as sshException:
        print(f"Could not establish SSH connection: {sshException}")
        return (f"Could not establish SSH connection: {sshException}")
    except Exception as e:
        print(e)
    finally:
        # Close the SSH client
        ssh_client.close()

# Given a path, return string of files and directories
def print_working_dir_files(path=""):
    # If path is empty, set it to the current directory
    if path == "":
        path = os.getcwd()
    # if absolute path, it must contain openai-assistants-ui
    if path[0] == "/":
        if "openai-assistants-ui" not in path:
            return "Invalid path"
    # Initialize empty dict
    files = {}
    # Loop through files in the given path
    for file in os.listdir(path):
        # If file is a directory, add it to the dict
        if os.path.isdir(os.path.join(path, file)):
            files[file] = "directory"
        # If file is a file, add it to the dict
        elif os.path.isfile(os.path.join(path, file)):
            files[file] = "file"
    return str(files)

# Read contents of a given file path and return them
def read_file(path):
    try:
        file = open(path, "r")
        return file.read()
    except Exception as e:
        print(str(e))
        return str(e)
    
# Write contents to a given file path and return success or failure message
def write_file(path, contents):
    try:
        file = open(path, "w")
        file.write(contents)
        return "Success"
    except Exception as e:
        print(str(e))
        return str(e)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
