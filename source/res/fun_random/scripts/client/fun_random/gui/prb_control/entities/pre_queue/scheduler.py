# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/prb_control/entities/pre_queue/scheduler.py
from fun_random_common.fun_constants import UNKNOWN_EVENT_ID
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasDesiredSubMode, hasSpecifiedSubMode
from gui.impl import backport
from gui.periodic_battles.models import PrimeTimeStatus
from gui.periodic_battles.prb_control.scheduler import PeriodicScheduler

class FunRandomScheduler(PeriodicScheduler, FunAssetPacksMixin, FunSubModesWatcher):

    def _hasConfiguredNotification(self):
        return False

    def _getController(self):
        return self.getDesiredSubMode()

    def _getMessageParams(self, subModeID=None):
        return {'subModeName': self.__getSubModeName(subModeID or self.__getDesiredSubModeID())}

    def _getResRoot(self):
        return self.getModeLocalsResRoot().scheduler

    def _startListening(self):
        self.startSubStatusListening(self.__onDesiredSubUpdate, desiredOnly=True)
        self.startSubSettingsListening(self.__onDesiredSubUpdate, desiredOnly=True)
        self.startSubSelectionListening(self.__onDesiredSubSelection)

    def _stopListening(self):
        self.stopSubSelectionListening(self.__onDesiredSubSelection)
        self.stopSubSettingsListening(self.__onDesiredSubUpdate, desiredOnly=True)
        self.stopSubStatusListening(self.__onDesiredSubUpdate, desiredOnly=True)

    def _getPrimeTimeStatus(self, controller=None):
        status = super(FunRandomScheduler, self)._getPrimeTimeStatus(controller)
        if status != PrimeTimeStatus.AVAILABLE:
            controller = controller or self._getController()
            status = controller.hasAvailablePrimeTimeServers()
        return status

    @hasDesiredSubMode(defReturn=UNKNOWN_EVENT_ID)
    def __getDesiredSubModeID(self):
        return self.getDesiredSubMode().getSubModeID()

    @hasSpecifiedSubMode(defReturn='')
    def __getSubModeName(self, subModeID):
        return backport.text(self.getSubMode(subModeID).getLocalsResRoot().userName.quoted())

    def __onDesiredSubUpdate(self, *_):
        self._updateScheduler(self._getPrimeTimeStatus())

    def __onDesiredSubSelection(self, *_):
        self._initScheduler()
