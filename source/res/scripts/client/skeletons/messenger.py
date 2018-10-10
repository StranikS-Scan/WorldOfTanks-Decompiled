# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/messenger.py


class IMessengerEntry(object):

    @property
    def protos(self):
        raise NotImplementedError

    @property
    def storage(self):
        raise NotImplementedError

    @property
    def gui(self):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def onAccountShowGUI(self):
        raise NotImplementedError

    def onAvatarInitGUI(self):
        raise NotImplementedError

    def onAvatarShowGUI(self):
        raise NotImplementedError
