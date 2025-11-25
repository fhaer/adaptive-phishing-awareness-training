import random
import json

# Define constants for different states of the interaction
STATE_INIT = 0                  # Initial state
STATE_GENERATE_MESSAGES = 1     # State for generating messages
STATE_ENGAGE_WITH_USER = 2      # State for user interaction
STATE_COACHING = 3              # State for providing coaching feedback

class InteractionController():
    """
    Controller class that manages the interaction flow between the UI, 
    the language model, and the user.
    """

    def __init__(self, ui, llm_api):
        """
        Initialize the controller with UI and LLM API components.
        
        Args:
            ui: User interface component
            llm_api: Language model API interface
        """
        self.ui = ui
        self.llm_api = llm_api

        self.state = STATE_INIT


    def user_query(self, query, message):
        """
        Constructs a prompt with appropriate context, sends the user query to the LLM and returns the response.
        
        Args:
            query: The user's input query
            message: The current message being displayed (if any)
            
        Returns:
            str: The LLM's response to the user query
        """

        response = ""
        prompt = ""

        # Get prompt templates from the LLM API
        templates = self.llm_api.get_prompt_templates()

        # Handle different states with appropriate prompt templates
        if self.state == STATE_INIT:
            prompt_template = templates.get("conversation-training-context")
            prompt = prompt_template.format(query=query)

        elif self.state == STATE_GENERATE_MESSAGES:
            response = "Messages are being generated. One moment please."

        elif self.state == STATE_ENGAGE_WITH_USER:
            if message:
                # A message is visible
                prompt_template = templates.get("conversation-phishing-context-with-message")
                prompt = prompt_template.format(query=query, subject=message["subject"], sender=message["sender"], content=message["content"])
            else:
                # No message is visible
                prompt_template = templates.get("conversation-training-context")
                prompt = prompt_template.format(query=query)

        elif self.state == STATE_COACHING:
            prompt_template = templates.get("conversation-phishing-context-with-message")
            prompt = prompt_template.format(query=query, subject=message["subject"], sender=message["sender"], content=message["content"])

        # If a prompt was constructed, query the LLM
        if prompt:
            response = self.llm_api.llm_query(prompt)

        return response
    
    def enter_state_generate_messages(self):
        """
        Transition to the message generation state and reset the conversation.
        """        
        self.state = STATE_GENERATE_MESSAGES
        self.llm_api.reset_conversation()

    def enter_state_engage_with_user(self):
        """
        Transition to the user engagement state and reset the conversation.
        """
        self.state = STATE_ENGAGE_WITH_USER
        self.llm_api.reset_conversation()

    def enter_state_coaching(self):
        """
        Transition to the coaching state.
        """
        self.state = STATE_COACHING

    def get_state(self):
        """
        Get the current state of the controller.
        
        Returns:
            int: The current state
        """
        return self.state
    
    def is_in_init_state(self):
        """
        Check if controller is in the initial state.
        
        Returns:
            bool: True if in initial state, False otherwise
        """
        return self.state == STATE_INIT

    def is_in_generate_messages_state(self):
        """
        Check if controller is in the message generation state.
        
        Returns:
            bool: True if in message generation state, False otherwise
        """
        return self.state == STATE_GENERATE_MESSAGES
    
    def is_in_engagte_with_user_state(self):
        """
        Check if controller is in the user engagement state.
        Note: There's a typo in the method name ('engagte' instead of 'engage')
        
        Returns:
            bool: True if in user engagement state, False otherwise
        """
        return self.state == STATE_ENGAGE_WITH_USER
    
    def is_in_coaching_state(self):
        """
        Check if controller is in the coaching state.
        
        Returns:
            bool: True if in coaching state, False otherwise
        """
        return self.state == STATE_COACHING
    
    # report the user decision on a message and returns the response of the coach
    def flag_message(self, message, is_phishing_actual, is_phishing_user_decision):
        """
        Report the user decision on a message and return the coaching response.
        
        Args:
            message: The message being evaluated
            is_phishing_actual: Boolean indicating if the message is actually phishing
            is_phishing_user_decision: Boolean indicating user's decision about the message
            
        Returns:
            str: Coaching response based on the user's decision
        """        

        # Get prompt templates from the LLM API
        templates = self.llm_api.get_prompt_templates()

        prompt_template = ""

        # Select appropriate coaching template based on true/false positive/negative
        if is_phishing_actual and is_phishing_user_decision:
            prompt_template = templates.get("coaching-true-positive")
        elif not is_phishing_actual and is_phishing_user_decision:
            prompt_template = templates.get("coaching-false-positive")
        elif is_phishing_actual and not is_phishing_user_decision:
            prompt_template = templates.get("coaching-false-negative")
        elif not is_phishing_actual and not is_phishing_user_decision:
            prompt_template = templates.get("coaching-true-negative")
        
        # Format the prompt with message details and analysis
        prompt = prompt_template.format(subject=message.get("subject"), sender=message.get("sender"), content=message.get("content"), analysis=message.get("analysis"))
        
        # Query the LLM for coaching response
        response = self.llm_api.llm_query(prompt)

        return response
