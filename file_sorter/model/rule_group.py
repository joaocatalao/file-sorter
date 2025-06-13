class RuleGroup:
    def __init__(self, name):
        self.name = name
        self.rules = []
        self.is_group = True

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"])

