# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/__init__.py
from soft_exception import SoftException

class WebCommandException(SoftException):

    def __init__(self, description):
        super(WebCommandException, self).__init__(description)
