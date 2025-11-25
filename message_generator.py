import os
import json
import html
import re
import sys

# Path to the JSON file containing message sample
MESSAGE_SAMPLES_FILE = "prompting/message_samples.json"
# Path to the JSON file containing context of users and environments
MESSAGE_GENERATION_CONTEXT_FILE = "prompting/message_generation_context.json"

class MessageGenerator():
    """
    A class responsible for generating email messages, including phishing simulations.
    """

    def __init__(self, ui, llm_api):
        """
        Initialize the MessageGenerator with UI and LLM API interfaces.
        
        Args:
            ui: User interface object for displaying messages
            llm_api: Language model API for generating content
        """
        self.ui = ui
        self.llm_api = llm_api
        self.n_generated_messages = 0
        self.sample_messages = []
        self.generated_messages = []
        self.message_generation_context = {}


    def extract_sample_messages(self, filename=MESSAGE_SAMPLES_FILE):
        """
        Extracts messages from JSON files located the given directory.
        
        Args:
            filename: Path to the message samples JSON file
        """

        message_samples = []
        
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)

                message_id = 0
                
                for object in data:
                    # Extract relevant fields if they exist
                    subject = object.get("subject")
                    sender = object.get("sender")
                    content = object.get("content")
                    is_phishing = object.get("is_phishing")
                    analysis = object.get("analysis")
                    
                    if subject and sender and content:
                        message_samples.append({
                            "subject": subject,
                            "sender": sender,
                            "content": content,
                            "is_phishing": is_phishing,
                            "analysis": analysis,
                            "id": message_id
                    })
                    
                    message_id += 1
        except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
            print(f"Error processing {filename}: {e}")
        
        self.sample_messages = message_samples


    def get_sample_messages(self):
        """
        Loads message samples from file, if not loaded already, and returns them.
        
        Returns:
            List of sample messages
        """
        if not self.sample_messages:
            self.extract_sample_messages()
        return self.sample_messages
    

    def extract_message_generation_context(self, file_path=MESSAGE_GENERATION_CONTEXT_FILE):
        """
        Extracts context for message generation in the form environments and users from the given JSON file.
        
        Args:
            file_path: Path to the context JSON file
        """
        extracted_data = {"environments": {}, "users": {}}

        if not os.path.exists(file_path):
            print(f"File '{file_path}' does not exist.")
            return extracted_data

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                for env_dict in data.get("environments", []):
                    for env_id, description in env_dict.items():
                        extracted_data["environments"][env_id] = description
                
                for user_dict in data.get("users", []):
                    for user_id, description in user_dict.items():
                        extracted_data["users"][user_id] = description

        except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
            print(f"Error processing {file_path}: {e}")

        self.message_generation_context = extracted_data


    def get_message_generation_context(self):
        """
        Loads context for message generation in the form environments and users from file, 
        if not loaded already, and returns them.
        
        Returns:
            Dictionary containing environments and users context
        """
        if not self.message_generation_context:
            self.extract_message_generation_context()
        return self.message_generation_context
    

    def get_message_generation_prompts(self, sample_messages, environment_id, user_id):
        """
        Creates prompts for message generation based on templates and context.
        
        Args:
            sample_messages: List of sample messages to base generation on
            environment_id: ID of the environment context to use
            user_id: ID of the user context to use
            
        Returns:
            List of prompts for message generation
        """
        
        message_prompts = []

        templates = self.llm_api.get_prompt_templates()
        prompt_template_phishing = templates.get("message-generation-phishing")
        prompt_template_no_phishing = templates.get("message-generation-no-phishing")

        generation_context = self.get_message_generation_context()
        env_context = generation_context.get("environments").get(environment_id)
        user_context = generation_context.get("users").get(user_id, "")

        # get phishing sample messages
        #phishing_messages = [entry for entry in sample_messages if entry.get("is_phishing", False)]

        for s in sample_messages:

            subject = s.get("subject")
            sender = s.get("sender")
            content = s.get("content")
            is_phishing = s.get("is_phishing")

            prompt = ""

            if is_phishing:
                prompt = prompt_template_phishing.format(environment_context=env_context, user_context=user_context, subject=subject, sender=sender, content=content)
            else:
                prompt = prompt_template_no_phishing.format(environment_context=env_context, user_context=user_context, subject=subject, sender=sender, content=content)
            
            message_prompts.append(prompt)

        return message_prompts

    def convert_text_to_html(self, text):
        """
        This function replaces new lines and finds all HTTP/HTTPS links in a given text and converts them into clickable HTML links.
        
        Args:
            text: Plain text to convert to HTML
            
        Returns:
            Text with HTML formatting
        """

        # Escape special HTML characters
        escaped_text = html.escape(text)

        # Convert multiple spaces to &nbsp;
        escaped_text = re.sub(r' {2,}', lambda m: '&nbsp;' * len(m.group(0)), escaped_text)

        # Convert tabs to &emsp;
        escaped_text = escaped_text.replace("\t", "&emsp;")

        # Convert newlines to <br>
        escaped_text = escaped_text.replace("\n", "<br>")

        return text
    
    def generate_message_batch(self, environment_id, user_id, batch_size):
        """
        Generates a batch of messages based on environment and user context.
        
        Args:
            environment_id: ID of the environment context to use
            user_id: ID of the user context to use
            batch_size: Number of messages to generate
            
        Returns:
            List of newly generated messages
        """

        sample_messages = self.get_sample_messages()
        generated_messages = []

        message_prompts = self.get_message_generation_prompts(sample_messages, environment_id, user_id)

        # Generate messages in batches: calculate start and end index
        start_index = self.n_generated_messages
        end_index = self.n_generated_messages + batch_size - 1

        # No more messages to generate
        if start_index >= len(message_prompts):
            return []

        # Get prompts
        for i, prompt in enumerate(message_prompts[start_index:], start=start_index):

            # Generate one message
            response = self.llm_api.llm_query(prompt)
            self.llm_api.reset_conversation()
            message = self.llm_api.extract_json_code_block(response)

            if "content" in message:
                # Adjust to html line breaks
                message["content"] = self.convert_text_to_html(message["content"])

                # Add properties from the original message
                message["id"] = i
                message["is_phishing"] = sample_messages[i]["is_phishing"]
                message["analysis"] = sample_messages[i]["analysis"]

                # Store generated messages and collect for returning the new batch
                self.generated_messages.append(message)
                generated_messages.append(message)

                # Generate the specified number of messages at once
                self.n_generated_messages += 1

            if i >= end_index:
                break

        return generated_messages


    def get_generated_messages(self):
        """
        Returns previously generated messages.
        
        Returns:
            List of all generated messages
        """
        return self.generated_messages
    

    def generate_message_batch_reset(self):
        """
        Resets the message generation state, clearing counters and message lists.
        """
        self.n_generated_messages = 0
        self.generated_messages = []
