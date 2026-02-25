# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_menu_entries/vehicle_skill_tree_entry_sub_presenter.py
from __future__ import absolute_import
from CurrentVehicle import g_currentVehicle
from gui.impl.gen.view_models.views.lobby.hangar.vehicle_menu_model import VehicleMenuModel
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.base_menu_entry_sub_presenter import BaseMenuEntrySubPresenter
from gui.prb_control.entities.base.listener import IPrbListener
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showVehicleHubVehSkillTree
from gui.veh_post_progression.helpers import needToShowCounter
from gui.veh_post_progression.models.ext_money import ExtendedMoney
from helpers import dependency
from skeletons.gui.game_control import IVehiclePostProgressionController, IPlatoonController

class VehicleSkillTreeEntrySubPresenter(BaseMenuEntrySubPresenter, IPrbListener):
    __postProgressionCtrl = dependency.descriptor(IVehiclePostProgressionController)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def onNavigate(self):
        showVehicleHubVehSkillTree(g_currentVehicle.item.intCD)

    def _getEvents(self):
        return ((self.__platoonCtrl.onMembersUpdate, self.__onPlatoonMembersUpdate), (self._cameraController.onEnabledChange, self.__onCameraEnabledChange))

    def _getListeners(self):
        return ((events.PrebattleEvent.SWITCHED, self.__onPrbEntitySwitched, EVENT_BUS_SCOPE.LOBBY),)

    def _getState(self):
        if not g_currentVehicle.item.postProgression.isVehSkillTree():
            return VehicleMenuModel.UNAVAILABLE
        elif not self.__postProgressionCtrl.isExistsFor(g_currentVehicle.item.descriptor.type):
            return VehicleMenuModel.UNAVAILABLE
        else:
            purchasableStep = g_currentVehicle.item.postProgression.getFirstPurchasableStep(ExtendedMoney(xp=g_currentVehicle.item.xp))
            return VehicleMenuModel.WARNING if purchasableStep is not None and needToShowCounter(g_currentVehicle.item) else VehicleMenuModel.ENABLED

    def __onPlatoonMembersUpdate(self, *_):
        self.packEntry()

    def __onPrbEntitySwitched(self, _):
        self.packEntry()

    def __onCameraEnabledChange(self, _):
        self.packEntry()
