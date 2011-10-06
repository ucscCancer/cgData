

def get_session():
    return Session()
    


class Session(object):
    
    def write(self, obj):
        print obj.get_name(), obj.DATA_FORM