# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/services/battle_pass_service.py
from gui.impl.lobby.user_missions.hangar_widget.services import IBattlePassService
from gui.prb_control.dispatcher import g_prbLoader
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.resource_well import IResourceWellController
from gui.impl.lobby.user_missions.hangar_widget.services.service_events import ServiceEvents

class BattlePassService(IBattlePassService, ServiceEvents):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self):
        super(BattlePassService, self).__init__()
        self.startServiceEvents()

    def onPrbEntitySwitched(self):
        self._onBattlePassEvent()

    def isVisible(self):
        isVisible = not self.__battlePassController.isDisabled()
        isVisible &= self._isValidBattleTypeForBattlePass()
        return isVisible

    def startListening(self):
        self.startGlobalListening()
        self.__battlePassController.onBattlePassSettingsChange += self._onBattlePassEvent
        self.__battlePassController.onSeasonStateChanged += self._onBattlePassEvent
        self.__resourceWell.onEventUpdated += self._onBattlePassEvent

    def stopListening(self):
        self.stopGlobalListening()
        self.__battlePassController.onBattlePassSettingsChange -= self._onBattlePassEvent
        self.__battlePassController.onSeasonStateChanged -= self._onBattlePassEvent
        self.__resourceWell.onEventUpdated -= self._onBattlePassEvent

    def finalize(self):
        self.stopListening()
        self.stopServiceEvents()

    def _isValidBattleTypeForBattlePass(self):
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher is None:
            return False
        else:
            prbEntity = prbDispatcher.getEntity()
            return False if prbEntity is None else self.__battlePassController.isValidBattleType(prbEntity)

    def _onBattlePassEvent(self, *_):
        self.onBattlePassChanged()
