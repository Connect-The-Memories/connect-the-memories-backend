from .support_user import support_user

class primary_user:
    def __init__(self, name: str, 
                 date_of_birth: int, cognitive_baseline: dict[str: int], preferred_exercises: list[str],accessibility_info: dict[str: str], support_users: list[support_user]):
        self.name = name
        self.date_of_birth = date_of_birth
        self.cognitive_baseline = cognitive_baseline
        self.preferred_exercises = preferred_exercises
        self.accessibility_info = accessibility_info
        self.support_users = support_users