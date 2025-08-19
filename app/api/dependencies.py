def get_query_param(param: str = None):
    return param

def get_current_user(user: str = Depends(get_query_param)):
    return user