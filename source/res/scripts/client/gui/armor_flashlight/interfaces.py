# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/armor_flashlight/interfaces.py


class IArmorFlashlightBattleController(object):

    def toggle(self):
        raise NotImplementedError

    def addHideReason(self, reason):
        raise NotImplementedError

    def removeHideReason(self, reason):
        raise NotImplementedError
