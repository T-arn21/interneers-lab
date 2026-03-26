from core.ports.greeting_port import GreetingPort

class GreetUserUseCase:
    def __init__(self, greeting_service: GreetingPort):
        self.greeting_service = greeting_service

    def execute(self, first_name: str = None, last_name: str = None) -> str:
        return self.greeting_service.get_full_name(first_name, last_name)