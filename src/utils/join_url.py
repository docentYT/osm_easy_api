def join_url(*args) -> str:
    """Joins args with '/'

    Returns:
        str: url (without anything in front of)
    """
    temp = ""
    for i in args: temp = temp + '/' + str(i)
    temp = temp[1:]
    return temp