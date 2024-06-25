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



# def fetch_url_from_filename(filename, df_bfa, df_cifar):
#     metadata = {}
#     case = ""

#     # Regular expressions to match filename patterns
#     uuid_pattern = re.compile(r'^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.txt$')
#     post_id_pattern = re.compile(r'^(\d+)\.txt$')
#     post_id_pdf_pattern = re.compile(r'^(\d+)_(.+)\.pdf$')
#     soq_pattern = re.compile(r'^([a-zA-Z]+)[0-9]+\.txt$')
#     num_pdf_title_pattern = re.compile(r'^(\d+)([a-zA-Z]+.*)\.pdf$')  # New pattern for numbers followed by pdf title



#     # Check which pattern the filename matches
#     if uuid_match := uuid_pattern.match(filename):
#         case = "cifarPost"
#         # UUID pattern for Cifar Wix
#         uuid = uuid_match.group(1)
#         # Filter the dataframe on ID
#         result = df_cifar[df_cifar['ID'] == uuid]
#     elif post_id_match := post_id_pattern.match(filename):
#         case = "bfaPost"
#         # Post ID pattern for BFA
#         post_id = post_id_match.group(1)
#         # Filter the dataframe on ID
#         result = df_bfa[df_bfa['ID'] == post_id]
#     elif post_id_pdf_match := post_id_pdf_pattern.match(filename):
#         case = "cifarPdf"
#         # Post ID with PDF title for BFA
#         post_id = post_id_pdf_match.group(1)
#         pdf_title = post_id_pdf_match.group(2).replace('-', ' ').lower()
#         # Normalize the pdf_title by replacing underscores with spaces and removing the file extension
#         readable_pdf_title = pdf_title.replace('_', ' ')
#         # metadata['title'] = readable_pdf_title
#         # Filter the dataframe on both ID and pdf_title
#         result = df_cifar[df_cifar['pdf_title'].str.lower() == pdf_title]
#     elif num_pdf_title_match := num_pdf_title_pattern.match(filename):  # Handle the new pattern
#         case = "bfaPdf"
#         post_id = num_pdf_title_match.group(1)
#         pdf_title = num_pdf_title_match.group(2).replace('-', ' ').lower()
#         # metadata['title'] = pdf_title
#         result = df_bfa[(df_bfa['ID'] == post_id) & (df_bfa['pdf_title'].str.lower() == pdf_title)]
#     #we're assuming its a soq if it doesnt fith the other patterns
#     else:
#         case = "soq"
#         project_code = filename.split('.')[0]
#         result=[]
#         result.append(project_code)
        
#     # else:
#     #     metadata["title"] = "Filename not supported for url references: " + filename
#     #     metadata["link"] = ""

#     # Check if there is exactly one matching row
#     if len(result) == 1:
#         if case == "bfaPdf":
#             # Return the pdf_url from the filtered row
#             metadata["link"] = result.iloc[0]['pdf_url']
#             metadata["title"] = result.iloc[0]['pdf_title']
#         elif case == "bfaPost":
#             metadata["link"] = result.iloc[0]['guid']
#             metadata["title"] = result.iloc[0]['post_title']
#         elif case == "cifarPost":
#             metadata["link"] = result.iloc[0]['URL']
#             metadata["title"] = result.iloc[0]['Title']
#             metadata["title"] = result.iloc[0]['post_title']
#         elif case == "cifarPdf":
#             metadata["link"] = result.iloc[0]['pdf_url']
#             metadata["title"] = result.iloc[0]['pdf_title']
#         elif case == "soq":
#             metadata["title"] = "See project details for project:  " + project_code + "  "
#             metadata["link"] = "https://docs.google.com/spreadsheets/d/1syWFDXt0BwjkjnVfd6kYl0YSbQTVcLW2E2YWV5lzrsw/edit#gid=393530796"
#         return metadata
#     # If there's no match for the document in the databases
#     elif len(result) == 0:
#         metadata["title"] = "Failed to fetch the reference original url"
#         metadata["link"] = ""
#         return metadata
import re

def fetch_url_from_filename(filename, list_bfa, list_cifar):
    metadata = {}
    case = ""
    result = []

    # Define regex patterns
    uuid_pattern = re.compile(r'^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.txt$')
    post_id_pattern = re.compile(r'^(\d+)\.txt$')
    post_id_pdf_pattern = re.compile(r'^(\d+)_(.+)\.pdf$')
    soq_pattern = re.compile(r'^([a-zA-Z]+)[0-9]+\.txt$')
    num_pdf_title_pattern = re.compile(r'^(\d+)([a-zA-Z]+.*)\.pdf$')

    # Matching patterns
    if uuid_match := uuid_pattern.match(filename):
        case = "cifarPost"
        uuid = uuid_match.group(1)
        result = [item for item in list_cifar if item['ID'] == uuid]
    elif post_id_match := post_id_pattern.match(filename):
        case = "bfaPost"
        post_id = post_id_match.group(1)
        result = [item for item in list_bfa if item['ID'] == post_id]
    elif post_id_pdf_match := post_id_pdf_pattern.match(filename):
        case = "cifarPdf"
        post_id = post_id_pdf_match.group(1)
        # fetch the title from DB. Right now is ugly title, so we're deleting it till further notice
        # pdf_title = post_id_pdf_match.group(2).replace('-', ' ').lower()
        pdf_title =  ""
        result = [item for item in list_cifar if item['pdf_title'].lower() == pdf_title]
    elif num_pdf_title_match := num_pdf_title_pattern.match(filename):
        case = "bfaPdf"
        post_id = num_pdf_title_match.group(1)
        # fetch the title from DB. Right now is ugly title, so we're deleting it till further notice
        # pdf_title = num_pdf_title_match.group(2).replace('-', ' ').lower()
        pdf_title =  ""
        result = [item for item in list_bfa if item['ID'] == post_id and item['pdf_title'].lower() == pdf_title]
    else:
        case = "soq"
        project_code = filename.split('.')[0]
        # metadata["title"] = "See project details for project: " + project_code
        metadata["title"] = ""
        metadata["link"] = "See project details for project: " + project_code + "https://docs.google.com/spreadsheets/d/1syWFDXt0BwjkjnVfd6kYl0YSbQTVcLW2E2YWV5lzrsw/edit#gid=393530796"
        print ("in fetch_url_from_filename,in the pattern matching code, case soq, creating metadata from project code + soq spreadsheet link "
               + "title: "+ metadata["title"] + "  link: " + metadata["link"])
        return metadata

    # Check results
    if len(result) == 1:
        item = result[0]  # The only item in the list
        if case in ["bfaPost", "cifarPost", "cifarPdf", "bfaPdf"]:
            if case in ["cifarPdf", "bfaPdf"]:
                metadata["link"] = item.get('pdf_url', item.get('guid', item.get('URL', '')))
                metadata["title"] = ""
            else:
                metadata["link"] = item.get('pdf_url', item.get('guid', item.get('URL', '')))
                metadata["title"] = item.get('pdf_title', item.get('post_title', item.get('Title', '')))
                print ("in post case for some reason, title:" + metadata["title"])
        print ("in fetch_url_from_filename, when theres exactly one row parsed, creating metadata from result list:  " 
               + "title: "+ metadata["title"] + "  link: " + metadata["link"])
        return metadata
    else:
        metadata["title"] = "Failed to fetch the reference original url"
        metadata["link"] = ""
        print ("in fetch_url_from_filename, when theres no match with database, creating metadata with error message:" 
               + "title: "+ metadata["title"] + "  link: " + metadata["link"])
        return metadata

        

# Sample dataframes (you'll replace these with actual loaded data)
# Assume df_bfa and df_cifar are already loaded appropriately
# # Test the function
# filename = "1234.txt"
# url = fetch_url_from_filename(filename, df_bfa, df_cifar)
# print("URL:", url)

def read_csv(filepath):
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)  # or process rows as needed 
# def read_csv(filepath):
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     full_path = os.path.join(base_dir, filepath)
#     with open(full_path, newline='') as csvfile:
#         reader = csv.DictReader(csvfile)
#         return list(reader)  # or process rows as needed 
        

def parseMasterDBData(citations_metadata):
    print("in parseMasterDBData")
    modified_citations =[]
    #load master DB
    # Path to the CSV file
    BFA_master_db_file_path = 'data/BFA_master_db.csv'
    CifarWIX_master_db_file_path = 'data/CifarWIX_master_db.csv'
    # BFA_master_db_file_path = os.path.join(os.path.dirname(__file__), 'data/', 'BFA_master_db.csv')
    # CifarWIX_master_db_file_path = os.path.join(os.path.dirname(__file__), 'data/', 'CifarWIX_master_db.csv')
    # Load the DataFrame
    df_BFA = read_csv(BFA_master_db_file_path)
    print("number of rows in BFA database: "+ str(len(df_BFA)))
    df_CifarWIX = read_csv(CifarWIX_master_db_file_path)
    print("number of rows in CifarWix database: "+ str(len(df_CifarWIX)))



    i=0
    for citation in citations_metadata:
        if 'file_name' in citation:
            print(f"Citation {i}: {citation['file_name']}")
            print("in parseMasterDBData, citations_metadata[i]['file_name']: " + citation["file_name"])
        else: 
            print(f"Error: 'file_name' key not found in citation {i}: {citation}")
            print("citations_metadata[i]['file_name']:  is None")
            i += 1
            continue  # Skip the rest of the loop for this iteration if 'file_name' is missing

        reference = fetch_url_from_filename(citation["file_name"], df_BFA, df_CifarWIX)
        modified_citation = citation["reference_id"] + "  " + reference["title"] + "  " + reference["link"]
        modified_citations.append(modified_citation)
        i += 1

    return modified_citations


    

def check_filename(filename):
    # Check if the filename matches numbers followed by .txt
    if re.fullmatch(r'\d+\.txt', filename):
        return "txt"
    # Check if the filename matches letters and numbers followed by .txt
    elif re.fullmatch(r'\w+\d+\.txt', filename):
        return "SOQ"
    else:
        return "Invalid format"


def referenceToLink(citations):
    print("in referenceToLink")
    for index, citation in enumerate(citations, start=1):
        print(f"{index}. {citation}")
    citationsAsLinks = []
    if len(citations) > 0:
        for text in citations:
            # Extract the reference id
            ref_id = re.search(r"\[\d+\]", text).group(0)
            if text.endswith(".txt"):
                file_name = re.search(r"\b\w+\.txt\b", text).group(0)
                file_type=check_filename(file_name)
                citationsAsLinks.append({
                    "reference_id": ref_id,
                    "file_name": file_name,
                    "file_type": file_type
                })
            
            elif text.endswith(".pdf"):
                # Extract the full name of the pdf
                pdf_name_match = re.search(r"from (\d+_.+)\.pdf", text)
                if pdf_name_match:
                    pdf_name_full = pdf_name_match.group(1)
                    # Extract the post_id and the pdf name
                    post_id = pdf_name_full.split('_', 1)[0]
                    pdf_name = pdf_name_full.split('_', 1)[1]
                    file_type = "pdf"
                    citationsAsLinks.append({
                        "reference_id": ref_id,
                        "post_id": post_id,
                        "pdf_name": pdf_name,
                        "file_type": file_type
                    })
    #fetch master DB and swap citations file names for link to post/pdf
        citations = parseMasterDBData(citationsAsLinks)
        print("citationsAsLinks lenght:" + str(len(citationsAsLinks)))
        print("citations lenght:" + str(len(citations)))
    else:
        print("there were no citations as links")
    return citations               


def parseAndSubstituteReferences(message_content):
    print("in parseAndSubstituteReferences")

    # Extract the message content
    annotations = message_content.annotations
    print("number of annotations: " + str(len(annotations)))
    citations = []
    # Iterate over the annotations and add footnotes
    for index, annotation in enumerate(annotations):
        # Replace the text with a footnote
        message_content.value = message_content.value.replace(annotation.text, f' [{index}]')
        # Gather citations based on annotation attributes
        if (file_citation := getattr(annotation, 'file_citation', None)):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f'[{index}] {file_citation.quote} from {cited_file.filename}')
        elif (file_path := getattr(annotation, 'file_path', None)):
            cited_file = client.files.retrieve(file_path.file_id)
            citations.append(f'[{index}] Click <here> to download {cited_file.filename}')
            # Note: File download functionality not implemented above for brevity
    #transform citations to links
    citations = referenceToLink(citations)
    print("citations with links lenght:" + str(len(citations)))
    message_content.value = message_content.value + '\n' + '\n'.join(citations)
    # Add footnotes to the end of the message before displaying to user
    print(message_content.value)
    return message_content.value 

def assistant_process(dict_from_dataset):
    assistant = client.beta.assistants.retrieve(assistant_id)
    # Create a new thread
    thread = client.beta.threads.create()
    
    # Add a user message to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=dict_from_dataset["question"],

    )

    # Create a run and wait for its completion
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,  

    )

    if run.status == 'completed':
        # Retrieve all messages from the thread
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        # Assuming the last message contains the assistant's response
        message_content = messages.data[0].content[0].text
        message_content_with_references = parseAndSubstituteReferences(message_content)
        messages.data[0].content[0].text = message_content_with_references
        print("messages.data[0].content[0].text:" + messages.data[0].content[0].text)
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
