from abc import ABC, abstractmethod
import logging
from model.serializable import SerializableMixin

logger = logging.getLogger(__name__)

class BaseRule(ABC, SerializableMixin):
    def __init__(self, name, config):
        self.name = name
        self.config = config

    @abstractmethod
    def match(self, file_path):
        pass

    @abstractmethod
    def action(self, file_path):
        pass
