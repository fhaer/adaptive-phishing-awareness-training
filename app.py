import training_environment_ui
import message_generator
import interaction_controller
import llm_api

class TrainingApp():
    """
    Initializes and starts the application.
    """

    def __init__(self):        
        self.llm_api = llm_api.LLMAPI()
        self.message_generator = message_generator.MessageGenerator(self, self.llm_api)
        self.interaction_controller = interaction_controller.InteractionController(self, self.llm_api)
        self.training_environment_ui = training_environment_ui.TrainingEnvironmentUI(self.message_generator, self.interaction_controller)

        self.training_environment_ui.start_ui()


if __name__ == "__main__":
    app = TrainingApp()

