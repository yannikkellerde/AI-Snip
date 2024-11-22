import ollama
from config import Config
from model_wrapper import ModelWrapper

class OllamaModelWrapper(ModelWrapper):
    client: ollama.Client

    def __init__(
        self, config:Config
    ):
        assert config.llm_provider == "ollama"
        client = ollama.Client(config.ollama_host)
        super().__init__(client, config.model_name)
        
    def _ollama_reformat_messages(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        ollama_messages = []
        for msg_raw in messages:
            msg = {m['type'] : m[m['type']] for m in msg_raw['content']}
            ollama_msg = {
                'role' : msg_raw['role'],
                'content' : msg['text']
            }
            if 'image_url' in msg:
                ollama_msg['images'] = [msg['image_url']['url']]
                #ollama_msg['images'] = [msg['image_url']['url']]
            ollama_messages.append(ollama_msg)
        return ollama_messages
    
    def complete(self, messages: dict[str, str], **kwargs) -> str:
        ollama_messages = self._ollama_reformat_messages(messages)
        response = self.client.chat(
            model=self.model_name,
            messages=ollama_messages,
            **kwargs
        )
        resp_msg = response['message']
        resp_content = resp_msg['content']
        return resp_content
    
    def stream_complete(self, messages: list[dict[str, str]], **kwargs) -> str:
        ollama_messages = self._ollama_reformat_messages(messages)
        stream = self.client.chat(
            model=self.model_name,
            messages=ollama_messages,
            stream=True,
            **kwargs
        )
        for chunk in stream:
            yield chunk['message']['content']