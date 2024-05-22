class RemoveStatus:
    def filter(self, record):
        mssg = record.getMessage()
        if "/home/get_status/" in mssg:
            return False
        
        if "/home/get_wallet/" in mssg:
            return False
        
        if "/home/get_user_info/" in mssg:
            return False
        
        return True