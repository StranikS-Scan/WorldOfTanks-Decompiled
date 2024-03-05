# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/account_helpers/settings_core/settings_disable/cosmic_disable_settings_controller.py
from account_helpers.settings_core.settings_constants import GAME
from account_helpers.settings_core.settings_disable import aop as daop
from account_helpers.settings_core.settings_disable.disable_settings_ctrl import DisableSettingsController
from constants import QUEUE_TYPE, ARENA_GUI_TYPE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class CosmicDisableSettingsController(DisableSettingsController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def init(self):
        super(CosmicDisableSettingsController, self).init()
        self.registerRecord(name=GAME.DYNAMIC_CAMERA, value=1, storages=('game',), guiPath=('GameSettings',))
        self.registerRecord(name=GAME.COMMANDER_CAM, value=0, storages=('game', 'extendedGame'), guiPath=('GameSettings',))
        self.registerRecord(name=GAME.PRE_COMMANDER_CAM, value=0, storages=('game', 'extendedGame'), guiPath=('GameSettings',))

    def _disable(self):
        if self._weaver.findPointcut(daop.DisableAltModeTogglePointcut) == -1:
            self._weaver.weave(pointcut=daop.DisableAltModeTogglePointcut, avoid=True)
        super(CosmicDisableSettingsController, self)._disable()

    def _canBeApplied(self):
        canBeApplied = False
        if self.prbDispatcher is not None:
            canBeApplied = self.prbDispatcher.getFunctionalState().isQueueSelected(QUEUE_TYPE.COSMIC_EVENT)
        if not canBeApplied:
            canBeApplied = self.__sessionProvider.arenaVisitor.gui.guiType == ARENA_GUI_TYPE.COSMIC_EVENT
        return canBeApplied
