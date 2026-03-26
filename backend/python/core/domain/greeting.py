class GreetingService:
    
    def get_full_name(self, first_name: str = None, last_name: str = None) -> str:
        return " ".join(filter(None, [first_name, last_name])).strip()