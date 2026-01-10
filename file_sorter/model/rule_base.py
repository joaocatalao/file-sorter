from abc import ABC, abstractmethod
import logging
from model.serializable import SerializableMixin

logger = logging.getLogger(__name__)

class BaseRule(ABC, SerializableMixin):
    def __init__(self, name, config, enabled=True):
        self.name = name
        self.config = config
        self.enabled = enabled

    @abstractmethod
    def match(self, file_path):
        pass

    @abstractmethod
    def action(self, file_path):
        pass
