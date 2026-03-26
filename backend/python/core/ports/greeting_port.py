from abc import ABC, abstractmethod

class GreetingPort(ABC):
    @abstractmethod
    def greet(self, name: str) -> str:
        pass