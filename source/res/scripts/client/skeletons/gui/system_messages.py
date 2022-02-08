# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/system_messages.py


class ISystemMessages(object):

    def init(self):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    def pushMessage(self, text, type, priority=None, messageData=None, savedData=None):
        raise NotImplementedError

    def pushI18nMessage(self, key, *args, **kwargs):
        raise NotImplementedError
