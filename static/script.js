window.onload = function () {
    /*
    Place the focus on text input area when the app is loaded
   */
  document.getElementById("chat-input").focus();
};

let currentThreadId = null; // Variable to store the current thread ID


function showLoadingOnButton() {
   /*
    This function Shows the spinner inplace of the send button (upward arrow) when the question is being processed by ChatGPT.
   */
  const sendButton = document.getElementById("send-btn");
  sendButton.innerHTML = '<div class="loader"></div>'; // Replace button text with loader
  sendButton.disabled = true; // Disable the button
}

function hideLoadingOnButton() {
  /*
    This function hides the spinner inplace of the send button (upward arrow) when the answer from ChatGPT is received.
  */

  const sendButton = document.getElementById("send-btn");
  sendButton.innerHTML = `<button id="send-btn">
          <i class="fa-solid fa-circle-arrow-up"></i>
        </button>`; // Restore button text
  sendButton.disabled = false; // Enable the button
}


function sendUserInput(threadId, userInput, files = []) {
   /*
    The function sends the user input to chatGPT, waits for an answer and prints it using addToChatHistory()

    Args:
    - threadId (str): The current thread we're using (needed for context history).
    - userInput (str): the user question text
    - files (list): A list with the uploaded files (currently not working)

    Returns:
    - list: Citations with links.
   */

  //Update current thread to threadID
  currentThreadId = threadId
  // Show loading indicator while waiting for the response
  showLoadingOnButton();
  // Immediately display the user's message in the chat history
  addToChatHistory("User", userInput,currentThreadId);

  fetch("/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      input: userInput,
      thread_id: threadId,
      file_ids: files,
    }),
  })
    .then((response) => console.log(response))
    .then((data) => {
      hideLoadingOnButton(); // Hide loading indicator when data is received
      addToChatHistory("Assistant", data); // Add assistant's response to the chat history
    })
    .catch((error) => {
      hideLoadingOnButton();
      console.error("Error:", error);
      document.getElementById("logs").innerText = "Error sending message.";
    });
}

function formatMessage(message) {

  // Escape HTML to prevent injection issues
  message = escapeHtml(message);

  // Replace new lines with <br> tags
  message = message.replace(/\n/g, '<br>');

  return message;

}


function addToChatHistory(role, message,currentThread) {
   /*
    The function sends the user input to chatGPT, waits for an answer and prints it using addToChatHistory()

    Args:
    - role (str): Either "user" or "system"
    - message (str): the user or assistant message text
    - currentThread (str): the current thread (for debugging purposes only)

    Returns: nothing
  
   */

  console.log("current thread ID:"  + currentThread)
  const messagesContainer = document.getElementById("chat-container");
  const messageDiv = document.createElement("div");
  let roleClass = role === "User" ? "user-message" : "assistant-message";
  messageDiv.className = "message " + roleClass; // Apply general message class and specific role class

  if (role === "Assistant") {
    message = formatAssistantResponse(message); // Format the message if it's from the assistant
  } else if (role === "User") {
    message = formatMessage(message); // This should maintain spaces and line breaks
  }
  messageDiv.innerHTML = message;
  messagesContainer.appendChild(messageDiv);
  // Scroll to the latest message
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatAssistantResponse(message) {
   /*
    The function formats the ASsistant message for better readability and usability

    Args:
    - 
    - message (str):  assistant message text


    Returns: the formatted message
  
   */
  

  // Escape HTML to prevent injection issues
  console.log(message)
  
  message = escapeHtml(message);
  
  // Replace new lines with <br> tags
  message = message.replace(/\n/g, '<br>');
  
  // Find URLs and replace them with anchor tags
  const urlPattern = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
  message = message.replace(urlPattern, '<a href="$1" target="_blank">$1</a>');
  
  console.log(message)
  return message;
}








function adjustLayout() {
  var chatHistory = document.getElementById("chat-history");
  var inputArea = document.getElementById("input-area");

  if (chatHistory && chatHistory.scrollHeight > window.innerHeight) {
    inputArea.style.position = "static";
  } else if (inputArea) {
    inputArea.style.position = "sticky";
  }
}

// Call adjustLayout whenever new messages are added or the window is resized
window.addEventListener("resize", adjustLayout);

document.getElementById("send-btn").addEventListener("click", function () {
  var userInputField = document.getElementById("chat-input");
  var userInput = userInputField.value;
  var fileInput = document.getElementById("file-input");
  if (!userInput && fileInput.files.length === 0) {
    return; // If no user input and no files, do nothing
  }
  var threadId = currentThreadId; // Get the current thread ID

  if (!threadId) {
    // If no thread ID, create a new thread first
    fetch("/create_thread")
      .then((response) => response.json())
      .then((data) => {
        if (data.thread_id) {
          currentThreadId = data.thread_id; // Update the thread ID in JavaScript
          if (fileInput.files.length > 0) {
            var files = fileInput.files;
            uploadFile(files)
              .then((fileIds) => {
                // add filenames to chat history
                for (let i = 0; i < fileIds.length; i++) {
                  addToChatHistory(
                    "User",
                    `File uploaded: ${fileInput.files[i].name}`
                  );
                }
                // Once the file is uploaded, send the user input along with the file IDs
                sendUserInput(data.thread_id, userInput, fileIds); // Send the user input after creating the thread
              })
              .finally(() => {
                // Clear the file input after processing
                resetFileInputLabel();
              });
          } else {
            sendUserInput(data.thread_id, userInput); // Send the user input after creating the thread
          }
        } else {
          document.getElementById("logs").innerText = "Error creating thread";
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        document.getElementById("logs").innerText = "Error creating thread";
      });
  } else {
    if (fileInput.files.length > 0) {
      var files = fileInput.files;
      // add filenames to chat history
      for (let i = 0; i < fileIds.length; i++) {
        addToChatHistory("User", `File uploaded: ${fileInput.files[i].name}`);
      }
      uploadFile(files)
        .then((fileIds) => {
          // Once the file is uploaded, send the user input along with the file IDs
          sendUserInput(currentThreadId, userInput, fileIds); // Send the user input after creating the thread
        })
        .finally(() => {
          // Clear the file input after processing
          resetFileInputLabel();
        });
    } else {
      sendUserInput(currentThreadId, userInput); // Send the user input with existing thread ID and no files
    }
  }

  // Clear the user input field after the message has been sent
  userInputField.value = "";
});

function uploadFile(file) {
    /*
    Upload a file to use in the query

    Args:
    - file: the file to be added

    note: currently not working

   */
  
  return new Promise((resolve, reject) => {
    let formData = new FormData();
    const input = document.getElementById("file-input");
    for (let i = 0; i < input.files.length; i++) {
      formData.append("files", input.files[i]);
    }
    fetch("/upload_file", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.file_id) {
          resolve(data.file_id);
        } else {
          reject("File upload failed");
        }
      })
      .catch((error) => {
        console.error("Error uploading file:", error);
        reject(error);
      });
  });
}

document
  .getElementById("chat-input")
  .addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
      event.preventDefault(); // Prevent the default action (new line)
      document.getElementById("send-btn").click(); // Trigger the send button click
    }
  });

document.getElementById("new-chat-btn").addEventListener("click", function () {
  fetch("/create_thread")
    .then((response) => response.json())
    .then((data) => {
      if (data.thread_id) {
        currentThreadId = data.thread_id; // Update the thread ID in JavaScript
        // Clearing out the user input, response area, and thread history
        document.getElementById("chat-input").value = "";
        document.getElementById("chat-container").innerHTML = "";
      } else {
        document.getElementById("thread-id").innerText =
          "Thread ID: Error creating thread";
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      document.getElementById("thread-id").innerText = "Thread ID: Error";
    });
});


function fetchThreadMessages(threadId) {
  /*
  Fetch all history messages from an Assistant's thread. 

    note: It's currently unused. It will be needed to create a multi-thread chatbot

  Args: 
  - threadId: thread identifier for OpenAI's API

  Returns:
  - all thread messages
  */

  fetch("/get_thread_messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ thread_id: threadId }),
  })
    .then((response) => response.json())
    .then((data) => {
      const messagesContainer = document.getElementById("chat-container");
      messagesContainer.innerHTML = ""; // Clear previous messages
      if (data && Array.isArray(data)) {
        data.reverse().forEach((message) => {
          // Reversing the array
          const messageDiv = document.createElement("div");
          const role = message.role; // Role of the message sender
          const content = message.content[0].text.value; // Assuming first element in content array is the message

          messageDiv.innerHTML = `<strong>${role}:</strong> ${content}`;
          messagesContainer.appendChild(messageDiv);
        });
      } else {
        messagesContainer.innerText =
          "No messages found or error fetching messages.";
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      document.getElementById("chat-container").innerText =
        "Error fetching messages.";
    });
}

// Check if the browser supports speech recognition
const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.lang = "en-US";

  // Add the voice-recording class when recognition starts
  document
    .getElementById("voice-input-btn")
    .addEventListener("click", function () {
      recognition.start();
      this.classList.add("voice-recording"); // Start the animation
    });

  // Remove the voice-recording class when recognition ends
  recognition.onend = function () {
    document
      .getElementById("voice-input-btn")
      .classList.remove("voice-recording"); // Stop the animation
  };

  recognition.onresult = function (event) {
    const transcript = event.results[0][0].transcript;
    document.getElementById("chat-input").value = transcript;
  };

  // Add error handling for recognition errors
  recognition.onerror = function (event) {
    console.error("Speech recognition error:", event.error);
    document
      .getElementById("voice-input-btn")
      .classList.remove("voice-recording"); // Stop the animation in case of error
  };
} else {
  document.getElementById("voice-input-btn").style.display = "none"; // Hide the button if not supported
}

const paperclipIcon = `<i class="fa-solid fa-paperclip"></i>`;


// function to reset file input label
function resetFileInputLabel() {
  var label = document.getElementById("file-input-label");
  label.innerHTML = paperclipIcon;
}


