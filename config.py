from dataclasses import dataclass
from typing import Any, Optional
import yaml

@dataclass
class Config:
    model_name: str = "gpt-4o"
    llm_provider: str = "openai"
    api_key: Optional[str] = None
    ollama_host: str = "http://localhost:11434"
    stream: bool = True

    @classmethod
    def load_from_yaml(cls, file_path: str) -> "Config":
        """
        Load configuration from a YAML file and return a Config instance.
        """
        try:
            with open(file_path, "r") as file:
                data = yaml.safe_load(file)
                return cls(**data)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}")
    
    def save_to_yaml(self, file_path: str) -> None:
        """
        Save the current configuration to a YAML file.
        """
        try:
            with open(file_path, "w") as file:
                yaml.safe_dump(self.to_dict(), file, default_flow_style=False)
        except Exception as e:
            raise ValueError(f"Error saving to YAML file: {e}")
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the dataclass instance to a dictionary.
        """
        return {
            key: (value.to_dict() if isinstance(value, Config) else value)
            for key, value in self.__dict__.items()
        }