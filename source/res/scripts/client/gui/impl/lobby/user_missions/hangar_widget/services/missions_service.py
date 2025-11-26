# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/services/missions_service.py
from PlayerEvents import g_playerEvents
from config_schemas.umg_config import umgConfigSchema
from gui.impl.lobby.user_missions.hangar_widget.services import IMissionsService
from gui.impl.lobby.user_missions.hangar_widget.services.service_events import ServiceEvents
from helpers import dependency
from skeletons.gui.game_control import IHangarGuiController

class MissionsService(IMissionsService, ServiceEvents):
    __hangarGuiCtrl = dependency.descriptor(IHangarGuiController)

    def __init__(self):
        super(MissionsService, self).__init__()
        self.startServiceEvents()

    def onPrbEntitySwitched(self):
        self._onMissionsChangedEvent()

    def isVisible(self):
        return umgConfigSchema.getModel().enableAllDaily and self.__hangarGuiCtrl.currentGuiProvider.getMissionsHelper().isDailyMissionsSupported()

    def startListening(self):
        self.startGlobalListening()
        g_playerEvents.onConfigModelUpdated += self.__onConfigModelUpdated

    def stopListening(self):
        self.stopGlobalListening()
        g_playerEvents.onConfigModelUpdated -= self.__onConfigModelUpdated

    def finalize(self):
        self.stopListening()
        self.stopServiceEvents()
        self.stopListening()

    def __onConfigModelUpdated(self, gpKey):
        if umgConfigSchema.gpKey == gpKey:
            self._onMissionsChangedEvent()

    def _onMissionsChangedEvent(self, *_):
        self.onMissionsChanged()
