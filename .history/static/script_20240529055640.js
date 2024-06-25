window.onload = function () {
  document.getElementById("chat-input").focus();
};

let currentThreadId = null; // Variable to store the current thread ID

function showLoadingOnButton() {
  const sendButton = document.getElementById("send-btn");
  sendButton.innerHTML = '<div class="loader"></div>'; // Replace button text with loader
  sendButton.disabled = true; // Disable the button
}

function hideLoadingOnButton() {
  const sendButton = document.getElementById("send-btn");
  sendButton.innerHTML = `<button id="send-btn">
          <i class="fa-solid fa-circle-arrow-up"></i>
        </button>`; // Restore button text
  sendButton.disabled = false; // Enable the button
}

// Function to send user input to the backend
function sendUserInput(threadId, userInput, files = []) {
  // Show loading indicator while waiting for the response
  showLoadingOnButton();
  // Immediately display the user's message in the chat history
  addToChatHistory("User", userInput);

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
      // document.getElementById('logs').innerText = data;
      addToChatHistory("Assistant", data); // Add assistant's response to the chat history
    })
    .catch((error) => {
      hideLoadingOnButton();
      console.error("Error:", error);
      document.getElementById("logs").innerText = "Error sending message.";
    });
}

function formatMessage(message) {
  // Replace spaces with &nbsp; and newlines with <br>
  return message.replace(/ /g, "&nbsp;").replace(/\n/g, "<br>");
}

// Function to add messages to the chat history
// Function to add messages to the chat history
// function addToChatHistory(role, message) {
//   const messagesContainer = document.getElementById("chat-container");
//   const messageDiv = document.createElement("div");
//   let roleClass = role === "User" ? "user-message" : "assistant-message";
//   messageDiv.className = "message " + roleClass; // Apply general message class and specific role class

//   if (role === "Assistant") {
//     // message = formatAssistantResponse(message); // Format the message if it's from the assistant
//     // Add an image instead of "Assistant" label
//     messageDiv.innerHTML = `${message}`;
//   } else if (role === "User") {
//     // Removed label for user
//     // message = formatMessage(message); // This should maintain spaces and line breaks
//     messageDiv.innerHTML = `${message}`;
//   }
//   messagesContainer.appendChild(messageDiv);
//   // Scroll to the latest message
//   messagesContainer.scrollTop = messagesContainer.scrollHeight;
// }
function addToChatHistory(role, message) {
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
  // Escape HTML to prevent injection issues
  message = escapeHtml(message);

  // Replace new lines with <br> tags
  message = message.replace(/\n/g, '<br>');

  // Find URLs and replace them with anchor tags
  const urlPattern = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
  message = message.replace(urlPattern, '<a href="$1" target="_blank">$1</a>');

  return message;
}

function formatMessage(message) {
  // Escape HTML to prevent injection issues
  message = escapeHtml(message);

  // Replace new lines with <br> tags
  message = message.replace(/\n/g, '<br>');

  return message;
}

// Example Usage:
const sampleMessage = `Here are some of the projects that have been conducted in Kenya:\n
1. **Expanding Employment and Opportunity through Digital Centers in Kenya (2020-2021)**\n
- This project aimed to create a social franchise system of digital centers throughout Kenya, staffed with trained youth as digital translators. It focused on providing internet access and IT training to underserved youth in urban areas outside of Nairobi [0].\n
2. **Opportunity Leads Umbrella Fund (2023-2025)**\n
- This project involves working with organizations to improve women's livelihood through job creation or improvement. It includes conducting research and providing technical assistance to help these organizations scale their solutions [1].\n
3. **Support to Donor Seeking to Catalyze Further Development in Keny





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
  // var threadDisplayText = document.getElementById('thread-id').innerText;
  // var threadId = threadDisplayText.includes("None") ? "" : threadDisplayText.split(": ")[1];
  var threadId = currentThreadId; // Get the current thread ID

  if (!threadId) {
    // If no thread ID, create a new thread first
    fetch("/create_thread")
      .then((response) => response.json())
      .then((data) => {
        if (data.thread_id) {
          // document.getElementById('thread-id').innerText = `Thread ID: ${data.thread_id}`;
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
    //sendUserInput(transcript); // Function to handle sending of the input
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

// Change file input label when files are selected
// document.getElementById("file-input").addEventListener("change", function () {
//   var label = document.getElementById("file-input-label");
//   var fileCount = this.files.length;
//   label.textContent = `📂 ${fileCount} File${fileCount !== 1 ? "s" : ""}`;
// });

// function to reset file input label
function resetFileInputLabel() {
  var label = document.getElementById("file-input-label");
  label.innerHTML = paperclipIcon;
}

function formatAssistantResponse(responseText) {
  // First, replace triple backtick blocks with <pre><code> tags
  let formattedText = responseText.replace(
    /```(.*?)```/gs,
    "<pre><code>$1</code></pre>"
  );

  // Then, replace single backticks with <code> tags for inline code
  // Ensure we don't touch already replaced triple backticks code blocks
  formattedText = formattedText.replace(/`([^`]+)`/g, "<code>$1</code>");

  // Convert line breaks to <br> tags for the remaining text
  formattedText = formattedText.replace(/\n/g, "<br>");

  return formattedText;
}
