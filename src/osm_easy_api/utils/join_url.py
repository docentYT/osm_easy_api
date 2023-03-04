def join_url(*args) -> str:
    """Joins args with '/'

    Returns:
        str: url (without anything in front of)
    """
    return "/".join(map(str, args))