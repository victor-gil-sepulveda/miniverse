
def parse_status(status):
    """
    Returns an integer status (input can be an integer, a string, or a string of type "201 CREATED")
    """
    if isinstance(status, int):
        return status

    if isinstance(status, basestring):
        return int(status.split()[0])


def py_to_flask(url):
    new = url.replace("{", "<").replace("}", ">")
    return new
