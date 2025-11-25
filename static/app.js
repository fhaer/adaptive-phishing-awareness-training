// Chatbox class handles all chat functionality
class Chatbox {

    constructor() {
        // Initialize DOM references for chat components
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        }

        this.state = false; // Track if chat is open or closed
        this.messages = []; // Store chat messages

        // Cache DOM elements for better performance
        this.chatboxContainer = document.querySelector('.chatbox__support');
        this.sendButton = document.querySelector('.send__button');
    }

    // Set up event listeners for chat functionality
    display() {
        const { openButton, chatBox, sendButton } = this.args;

        // Toggle chatbox visibility on button click
        openButton.addEventListener('click', () => this.toggleState(chatBox))
        // Send message when send button is clicked
        sendButton.addEventListener('click', () => this.onSendButton(chatBox))

        const node = chatBox.querySelector('input');
        // Also send message when Enter key is pressed
        node.addEventListener("keyup", ({ key }) => {
            if (key === "Enter") {
                this.onSendButton(chatBox)
            }
        })
    }

    // Toggle chat visibility state
    toggleState(chatbox) {

        let element = document.getElementById('generating');
        if (element && !element.checkVisibility()) {
            this.state = !this.state;

            // Add or remove active class based on state
            if (this.state) {
                chatbox.classList.add('chatbox--active')
            } else {
                chatbox.classList.remove('chatbox--active')
            }
        }
    }

    // Handle flagging actions (report/allow)
    handleAction(action, messageId) {
        let is_phishing = false;
        if (action === "report") {
            is_phishing = true;
        }

        // Show chatbox if it's not already visible
        if (!this.chatboxContainer.classList.contains('chatbox--active')) {
            this.chatboxContainer.classList.add('chatbox--active');
        }

        // Disable input while processing
        var textField = this.chatboxContainer.querySelector('input');
        textField.disabled = true;
        this.sendButton.disabled = true;

        // Add user message based on action
        let user_message = { name: "User", message: "Flag as Legitimate" }
        if (is_phishing) {
            user_message = { name: "User", message: "Flag as Phishing" }
        }
        this.messages.push(user_message);

        // Show loading indicator
        let msgLoading = { name: "Coach", message: "Generating ..." };
        this.messages.push(msgLoading);
        this.updateChatText(this.chatboxContainer);

        // Send flag request to server after UI updates
        setTimeout(() => {
            fetch('/messages/flag', {
                method: 'POST',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ "message_id": messageId, "is_phishing": is_phishing })
            })
                .then(r => r.json())
                .then(r => {
                    // Remove loading message and add server response
                    this.messages.pop(); // Remove last message (Generating ...)
                    let msgCoach = { name: "Coach", message: r.response };
                    this.messages.push(msgCoach);
                    this.updateChatText(this.chatboxContainer);
                    textField.value = '';
                })
                .catch((error) => {
                    console.error('Error:', error);
                    this.messages.pop(); // Remove "Generating ..."
                    this.messages.push({ name: "Coach", message: "An error occurred. Please try again." });
                    this.updateChatText(this.chatboxContainer);
                })
                .finally(() => {
                    // Re-enable input controls
                    this.sendButton.disabled = false;
                    textField.disabled = false;
                });
        }, 0);
    }

    // Handle sending user messages
    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let user_query = textField.value
        if (user_query === "") {
            return; // Don't send empty messages
        }

        // Add user message to chat history
        let msg1 = { name: "User", message: user_query }
        this.messages.push(msg1);

        // Get currently visible email ID if available
        const visibleEmail = document.querySelector('.visible-email');
        const email_id = visibleEmail ? visibleEmail.id : undefined;

        // Disable input while processing
        this.sendButton.disabled = true;
        textField.disabled = true;

        // Show loading indicator
        let msgLoading = { name: "Coach", message: "Generating ..." };
        this.messages.push(msgLoading);
        this.updateChatText(chatbox);

        // Send query to server
        setTimeout(() => {
            fetch('/query', {
                method: 'POST',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ "user_query": user_query, "email_id": email_id })
            })
                .then(r => r.json())
                .then(r => {
                    // Remove loading message and add server response
                    this.messages.pop(); // Remove last message (Generating ...)
                    let msgCoach = { name: "Coach", message: r.response };
                    this.messages.push(msgCoach);
                    this.updateChatText(chatbox);
                    textField.value = '';
                })
                .catch((error) => {
                    console.error('Error:', error);
                    this.messages.pop(); // Remove "Generating ..."
                    this.messages.push({ name: "Coach", message: "An error occurred. Please try again." });
                    this.updateChatText(chatbox);
                })
                .finally(() => {
                    // Re-enable input controls
                    this.sendButton.disabled = false;
                    textField.disabled = false;
                });
        }, 0);
    }

    // Refresh the chat UI with current messages
    updateChatText(chatbox) {
        var html = '<div>';
        this.messages.slice().forEach(function (item, index) {
            if (item.name === "User") {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>'
            }
            else {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
            }
        });
        html += "</div>"

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    }
}

// EmailHandler manages email list and display
class EmailHandler {
    constructor() {
        // Cache DOM elements
        this.emailListContainer = document.querySelector(".email-list");
        this.emailContentContainer = document.querySelector(".email-content");
    }

    // Load emails from server
    loadEmails() {

        // Helper function to truncate long text
        function truncateText(text, maxLength = 54) {
            return text.length > maxLength ? text.slice(0, maxLength) + " ..." : text;
        }

        // Helper function to truncate text at first parenthesis
        function truncateAfterParenthesis(text) {
            let index = text.indexOf("(");
            return index !== -1 ? text.slice(0, index).trim() : text;
        }

        // Recursive function to fetch generated emails in batches
        const fetchNext = () => {
            fetch("/messages/get")
                .then(response => response.json())
                .then(data => {
                    if (data.messages.length === 0) {
                        console.log("No more messages to fetch.");
                        document.getElementById("generating").style.display = "none";
                        document.getElementById("starting").style.display = "block";
                        return;
                    }
                    data.messages.forEach((email, index) => {

                        // Validate email data
                        if (!email || !email.sender || !email.subject || !email.content) {
                            console.warn("Skipping invalid email:", email);
                            return;
                        }
                        // Avoid duplicates
                        if (document.getElementById(email.id)) {
                            console.log(`Email with ID ${email.id} is already added.`);
                            return;
                        }

                        // Create email list item
                        const inboxItemId = `inbox-entry-${email.id}`
                        const inboxItem = document.createElement("div");
                        inboxItem.className = "email-item";
                        inboxItem.id = inboxItemId;
                        inboxItem.onclick = () => this.showEmail(email.id);
                        inboxItem.innerHTML = `<h3>${truncateAfterParenthesis(email.sender)}</h3><p>` + truncateText(email.subject) + `</p>`;
                        this.emailListContainer.appendChild(inboxItem);

                        // Create email content div (hidden initially)
                        const emailDetail = document.createElement("div");
                        emailDetail.id = email.id;
                        emailDetail.className = "email-detail";
                        emailDetail.style.display = "none";
                        emailDetail.innerHTML = `
                            <h3 style="color: black; border-bottom: 2px solid black; padding-bottom: 5px;">${email.subject}</h3>
                            <h4 class="email-sender" style="margin-top: 10px;">
                                <img src="https://img.icons8.com/color/48/000000/email.png" alt="Email Icon">Sender: ${email.sender}
                            </h4>
                            <p style="margin-top: 20px;">${email.content}</p>
                            <div style="margin-top: 20px;">
                                <button class="btn btn-danger" onclick="chatbox.handleAction('report', '${email.id}')">Flag as Phishing</button>
                                <button class="btn btn-success" onclick="chatbox.handleAction('allow', '${email.id}')">Flag as Legitimate</button>
                            </div>
                        `;
                        this.emailContentContainer.appendChild(emailDetail);
                    });

                    // Continue fetching if not done
                    if (!data.generation_completed) {
                        // Get new messages after a short delay
                        new Promise(r => setTimeout(r, 100)).then(t => fetchNext());
                    } else {
                        // Hide loading, show start message
                        document.getElementById("generating").style.display = "none";
                        document.getElementById("starting").style.display = "block";
                    }
                })
                .catch(error => console.error("Error loading emails:", error));
        };

        // Start fetching emails
        fetchNext();
    }

    // Display a selected email
    showEmail(emailId) {

        let element = document.getElementById('generating');
        if (element && !element.checkVisibility()) {

            // Hide start messages
            document.getElementById('generating').style.display = 'none';
            document.getElementById('starting').style.display = 'none';

            // Update active state in email list
            const inboxItemId = `inbox-entry-${emailId}`
            document.querySelectorAll('.email-item').forEach(email => email.classList.remove('active'));
            document.getElementById(inboxItemId).classList.add('active');

            // Hide all emails and show the selected one
            document.querySelectorAll('.email-detail').forEach(email => { email.style.display = 'none'; email.classList.remove('visible-email') });
            document.getElementById(emailId).style.display = 'block';
            document.getElementById(emailId).classList.add('visible-email');

            // Notify server about email being viewed
            fetch('/messages/show', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ "email_id": emailId })
            }).catch(error => console.error('Error:', error));
        }

    }
}

// Initialize EmailHandler when DOM is loaded
const emailHandler = new EmailHandler();
document.addEventListener("DOMContentLoaded", () => emailHandler.loadEmails());

// Initialize Chatbox
const chatbox = new Chatbox();
chatbox.display();
