from abc import ABC, abstractmethod

class GreetingPort(ABC):
    @abstractmethod
    def get_full_name(self, first_name: str = None, last_name: str = None) -> str:
        pass