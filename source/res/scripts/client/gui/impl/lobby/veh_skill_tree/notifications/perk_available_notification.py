# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_skill_tree/notifications/perk_available_notification.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import VEH_SKILL_TREE_POPUP_SHOWN
from helpers import dependency
from gui.impl.gen.view_models.views.lobby.veh_skill_tree.notifications.perk_available_view_model import PerkAvailableViewModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.gf_notifications import NotificationBase
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.shared.event_dispatcher import showVehicleHubVehSkillTree
from skeletons.gui.shared import IItemsCache
TRAINING_FLAGS = FUNCTIONAL_FLAG.TRAINING | FUNCTIONAL_FLAG.EPIC_TRAINING

class PerkAvailableNotification(IGlobalListener, NotificationBase):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, resId, *args, **kwargs):
        model = PerkAvailableViewModel()
        super(PerkAvailableNotification, self).__init__(resId, model, *args, **kwargs)
        payload = self._getPayload()
        self.__vehCD = payload['vehCD']

    @property
    def viewModel(self):
        return super(PerkAvailableNotification, self).getViewModel()

    def _update(self):
        if self._isPopUp:
            settings = AccountSettings.getUIFlag(VEH_SKILL_TREE_POPUP_SHOWN)
            settings.add(self.__vehCD)
            AccountSettings.setUIFlag(VEH_SKILL_TREE_POPUP_SHOWN, settings)
        vehicle = self.__itemsCache.items.getItemByCD(self.__vehCD)
        with self.viewModel.transaction() as vm:
            vm.setIsPopUp(self._isPopUp)
            vm.setIsDisabled(self.__isButtonDisabled())
            fillVehicleModel(vm.vehicle, vehicle)

    def _getEvents(self):
        events = super(PerkAvailableNotification, self)._getEvents()
        return events + ((self.viewModel.onClose, self.__onClose), (self.viewModel.onGoToProgression, self.__onGoToProgression))

    def __onClose(self):
        self.destroyWindow()

    def __onGoToProgression(self):
        showVehicleHubVehSkillTree(self.__vehCD)

    def _onLoading(self, *args, **kwargs):
        self.startGlobalListening()
        super(PerkAvailableNotification, self)._onLoading(*args, **kwargs)

    def _finalize(self):
        self.stopGlobalListening()
        super(PerkAvailableNotification, self)._finalize()

    def onPrbEntitySwitched(self):
        self._update()

    def onUnitPlayerRemoved(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.viewModel.setIsDisabled(False)

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.viewModel.setIsDisabled(pInfo.isReady)

    def __isButtonDisabled(self):
        if self.prbEntity and self.prbEntity.isInQueue():
            return True
        else:
            if self.prbDispatcher is not None and self.prbDispatcher.getFunctionalState().isInUnit():
                if self.prbEntity and self.prbEntity.getPlayerInfo().isReady:
                    return True
            return False
