from abc import ABC, abstractmethod

class ModelWrapper(ABC):
    def __init__(
        self, client, model_name: str
    ):
        self.client = client
        self.model_name = model_name
    
    @abstractmethod
    def complete(self, messages: list[dict[str, str]], **kwargs) -> str:
        pass
    
    @abstractmethod
    def stream_complete(self, messages: list[dict[str, str]], **kwargs) -> str:
        pass