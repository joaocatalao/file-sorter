from abc import ABC, abstractmethod

class BaseRule(ABC):
    def __init__(self, name, config):
        self.name = name
        self.config = config  # Dict: pattern, destination, etc.

    @abstractmethod
    def match(self, file_path):
        """Return True if the file matches the rule's condition."""
        pass

    @abstractmethod
    def action(self, file_path):
        """Perform the rule's action on the file."""
        pass

    def to_dict(self):
        return {
            "name": self.name,
            "config": self.config,
            "rule_type": self.__class__.__name__,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["config"])
