# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/account_helpers/settings_core/settings_disable/races_disable_settings_controller.py
from account_helpers.settings_core.settings_constants import GAME
from account_helpers.settings_core.settings_disable import aop as daop
from account_helpers.settings_core.settings_disable.disable_settings_ctrl import DisableSettingsController
from constants import QUEUE_TYPE, ARENA_GUI_TYPE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class RacesDisableSettingsController(DisableSettingsController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def init(self):
        super(RacesDisableSettingsController, self).init()
        self.registerRecord(name=GAME.DYNAMIC_CAMERA, value=1, storages=('game',), guiPath=('GameSettings',))
        self.registerRecord(name=GAME.COMMANDER_CAM, value=0, storages=('game', 'extendedGame'), guiPath=('GameSettings',))
        self.registerRecord(name=GAME.PRE_COMMANDER_CAM, value=0, storages=('game', 'extendedGame'), guiPath=('GameSettings',))

    def _disable(self):
        if self._weaver.findPointcut(daop.DisableAltModeTogglePointcut) == -1:
            self._weaver.weave(pointcut=daop.DisableAltModeTogglePointcut, avoid=True)
        super(RacesDisableSettingsController, self)._disable()

    def _canBeApplied(self):
        canBeApplied = False
        if self.prbDispatcher is not None:
            canBeApplied = self.prbDispatcher.getFunctionalState().isQueueSelected(QUEUE_TYPE.RACES)
        if not canBeApplied:
            canBeApplied = self.__sessionProvider.arenaVisitor.gui.guiType == ARENA_GUI_TYPE.RACES
        return canBeApplied
