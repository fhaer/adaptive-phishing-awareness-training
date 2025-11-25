from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

import message_generator
import interaction_controller

class TrainingEnvironmentUI():
    """
    A class that provides a web-based UI for a phishing email training environment.
    Handles the Flask application setup and routes for user interaction.
    """

    def __init__(self, message_generator, interaction_controller):
        """
        Initialize the UI with message generator and interaction controller.
        Set up Flask application and register all routes.
        
        Args:
            message_generator: Component that generates training email messages
            interaction_controller: Component that manages application state and user interactions
        """
        self.message_generator = message_generator
        self.interaction_controller = interaction_controller

        # initialize flask and register routes
        self.flask = Flask(__name__)
        CORS(self.flask)
        self.flask.add_url_rule('/', view_func=self.index, methods=['GET'])
        self.flask.add_url_rule('/messages/get', view_func=self.messages_get, methods=['GET'])
        self.flask.add_url_rule('/messages/flag', view_func=self.messages_flag, methods=['POST'])
        self.flask.add_url_rule('/messages/show', view_func=self.messages_show, methods=['POST'])
        self.flask.add_url_rule('/query', view_func=self.query, methods=['POST'])
        self.flask.after_request(self.after_request)

    
    def start_ui(self):
        """
        Start the Flask web server.
        Catches SystemExit exceptions that occur during Flask shutdown.
        """
        try:
            self.flask.run(debug=True, port=8081)
        except SystemExit as e:
            pass

    def index(self):
        """
        Handle requests to the root URL.
        If in initial state, transition to message generation state.
        
        Returns:
            Rendered HTML template for the base page
        """
        if self.interaction_controller.is_in_init_state():
            # Enter state: generate messages
            self.interaction_controller.enter_state_generate_messages()

        return render_template("base.html")
    
    def messages_get(self):
        """
        API endpoint to retrieve generated messages.
        If in message generation state, generates a batch of messages.
        Otherwise, returns all previously generated messages.
        
        Returns:
            JSON response with messages and generation status
        """
        if self.interaction_controller.is_in_generate_messages_state():
            # Generate in batches as long as messages are available
            messages = self.message_generator.generate_message_batch("e3", "u3", 1)
            # No more messages
            generation_completed = False
            if not messages:
                generation_completed = True
                # Enter state: engage with user
                self.interaction_controller.enter_state_engage_with_user()
            return jsonify( { "messages": messages, "generation_completed": generation_completed } )
        else:
            # Return all generated messages
            messages = self.message_generator.get_generated_messages()
            # Enter state: engage with user
            self.interaction_controller.enter_state_engage_with_user()
            return jsonify( { "messages": messages, "generation_completed": True } )

    def messages_flag(self):
        """
        API endpoint to handle user flagging a message as phishing or legitimate.
        Transitions to coaching state and provides feedback on user's decision.
        
        Returns:
            JSON response with feedback on the user's decision
        """

        response = ""
        if not self.interaction_controller.is_in_generate_messages_state():
            # Enter state: coaching
            self.interaction_controller.enter_state_coaching()

            # React to user decision on phishing
            data = request.get_json()
            message_id = data.get("message_id")
            is_phishing_user_decision = data.get("is_phishing")

            # Get corresponding message
            generated_messages = self.message_generator.get_generated_messages()
            message = next((m for m in generated_messages if str(m.get('id')) == str(message_id)), None)
            is_phishing_actual = message.get("is_phishing")

            response = self.interaction_controller.flag_message(message, is_phishing_actual, is_phishing_user_decision)
        else:
            response = "Messages are being generated. One moment please."

        return jsonify({"response": response})

    def messages_show(self):
        """
        API endpoint to handle showing a specific message.
        Transitions to engage with user state.
        
        Returns:
            JSON response (empty in this case)
        """
        message_id = request.get_json().get("email_id")

        if not self.interaction_controller.is_in_generate_messages_state():
            # Enter state: engage with user
            self.interaction_controller.enter_state_engage_with_user()

        return jsonify({"response": ""})

    def query(self):
        """
        API endpoint to handle user queries about messages.
        Processes the query and returns a response from the interaction controller.
        
        Returns:
            JSON response with answer to the user's query
        """
        user_query = request.get_json().get("user_query")
        message_id = request.get_json().get("email_id")

        message = None
        if message_id:
            generated_messages = self.message_generator.get_generated_messages()
            message = next((m for m in generated_messages if str(m.get('id')) == str(message_id)), None)

        response = self.interaction_controller.user_query(user_query, message)

        return jsonify({"response": response})

    @staticmethod
    def after_request(response):
        """
        Flask after-request handler to ensure proper content type for JSON responses.
        
        Args:
            response: The Flask response object
            
        Returns:
            Modified response with proper charset for JSON responses
        """
        if 'application/json' in response.headers['Content-Type']:
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response

