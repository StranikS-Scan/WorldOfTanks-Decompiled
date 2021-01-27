# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/api.py
import json
import weakref
_TYPE = 'type'
_DATA = 'data'

class C2WHandler(object):

    def __init__(self, sender):
        super(C2WHandler, self).__init__()
        self.__sender = weakref.proxy(sender)
        self.__previous = {}

    def init(self):
        pass

    def fini(self):
        self.__sender = None
        return

    def sendWebEvent(self, webEvent):
        if self.__sender is not None:
            eType, eData = self.__hashedEvent(webEvent)
            if not self.__isDuplicate(eType, eData):
                try:
                    self.__sender.sendEvent(json.dumps(webEvent))
                    self.__cachePrevious(eType, eData)
                except ReferenceError:
                    return

        return

    def __isDuplicate(self, eType, eData):
        return self.__previous.get(eType) == eData

    def __cachePrevious(self, eType, eData):
        self.__previous[eType] = eData

    @staticmethod
    def __hashedEvent(webEvent):
        return (hash(json.dumps(webEvent[_TYPE])), hash(json.dumps(webEvent[_DATA], ensure_ascii=False)))


def c2w(name):

    def decorator(method):

        def wrapped(self, *args, **kwargs):
            self.sendWebEvent({_TYPE: name,
             _DATA: method(self, *args, **kwargs) or {}})

        return wrapped

    return decorator
