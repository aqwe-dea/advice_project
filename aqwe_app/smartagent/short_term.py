class ShortTermMemory:
    def __init__(self, max_messages: int = 50):
        self.messages = []
        self.max_messages = max_messages
    
    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)  # Удаляем старейшее
    
    def get_context(self) -> list:
        return self.messages