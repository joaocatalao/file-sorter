import logging

logger = logging.getLogger(__name__)

class SerializableMixin:
    def to_dict(self):
        logger.debug(f"[Serializable] Serializing {self.__class__.__name__}")
        return {
            "name": getattr(self, "name", None),
            "config": getattr(self, "config", {}),
            "rule_type": self.__class__.__name__,
        }

    @classmethod
    def from_dict(cls, data):
        logger.debug(f"[Serializable] Deserializing into {cls.__name__}: {data.get('name')}")
        return cls(data["name"], data.get("config", {}))
