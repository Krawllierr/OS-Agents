from abc import ABC, abstractmethod

class AgentBase(ABC):
    def __init__(self, name):
        self.name = name
        self.memory = {}

    @abstractmethod
    def process(self, input_data):
        pass

    def update_memory(self, key, value):
        self.memory[key] = value

    def get_memory(self, key):
        return self.memory.get(key)

    def clear_memory(self):
        self.memory.clear()