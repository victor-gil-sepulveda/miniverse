
class NotEnoughMoneyException(BaseException):
    def __init__(self, message):
        super(NotEnoughMoneyException, self).__init__(message)
