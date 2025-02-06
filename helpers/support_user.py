class support_user:
    def __init__(self, name: str, relationship: str, permissions: dict[str: bool], contributions: dict[str: str]):
        self.name = name
        self.relationship = relationship
        self.permissions = permissions
        self.contributions = contributions