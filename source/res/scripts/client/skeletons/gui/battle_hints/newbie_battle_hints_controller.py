# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/battle_hints/newbie_battle_hints_controller.py
import typing

class INewbieBattleHintsController(object):

    def fini(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isUserSettingEnabled(self):
        raise NotImplementedError

    def getDisplayCount(self, uniqueName):
        raise NotImplementedError

    def resetHistory(self):
        raise NotImplementedError
