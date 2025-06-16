import logging
from model.serializable import SerializableMixin

logger = logging.getLogger(__name__)

class RuleGroup(SerializableMixin):
    def __init__(self, name):
        self.name = name
        self.rules = []
        self.is_group = True

    @classmethod
    def from_dict(cls, data):
        logger.debug(f"[RuleGroup] Deserializing group: {data.get('name')}")
        return cls(data["name"])
