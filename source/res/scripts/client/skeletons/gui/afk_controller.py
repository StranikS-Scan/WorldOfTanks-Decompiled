# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/afk_controller.py


class IAFKController(object):
    onBanUpdated = None

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    @property
    def isBanned(self):
        return False

    @property
    def banExpiryTime(self):
        pass

    def showBanWindow(self):
        raise NotImplementedError

    def showWarningWindow(self):
        raise NotImplementedError

    def showQuest(self):
        raise NotImplementedError

    def questFilter(self, quest):
        raise NotImplementedError

    def showAFKWindows(self):
        raise NotImplementedError
