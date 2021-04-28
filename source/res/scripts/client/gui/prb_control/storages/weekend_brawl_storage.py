# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/storages/weekend_brawl_storage.py
from gui.battle_control.arena_visitor import createByAvatar
from gui.prb_control.storages.local_storage import LocalStorage
from helpers import dependency
from skeletons.gui.game_control import IWeekendBrawlController

class WeekendBrawlStorage(LocalStorage):
    __slots__ = ('_isSelected',)
    wBrawlController = dependency.descriptor(IWeekendBrawlController)

    def __init__(self):
        super(WeekendBrawlStorage, self).__init__()
        self._isSelected = False

    def clear(self):
        self._isSelected = False

    def release(self):
        self._isSelected = True

    def suspend(self):
        self.clear()

    def isModeSelected(self):
        return self._isSelected and self.wBrawlController.isModeActive()

    def onAvatarBecomePlayer(self):
        arenaVisitor = createByAvatar()
        self._isSelected = arenaVisitor.gui.isWeekendBrawlBattle()
