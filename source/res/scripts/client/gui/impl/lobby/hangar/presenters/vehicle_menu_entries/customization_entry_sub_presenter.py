# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_menu_entries/customization_entry_sub_presenter.py
from __future__ import absolute_import
from CurrentVehicle import g_currentVehicle
from gui.impl.gen.view_models.views.lobby.hangar.vehicle_menu_model import VehicleMenuModel
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries import isVehicleUnavailable
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.base_menu_entry_sub_presenter import BaseMenuEntrySubPresenter
from gui.prb_control.entities.base.listener import IPrbListener
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency, server_settings
from items.components.c11n_constants import ItemTags
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class CustomizationEntrySubPresenter(BaseMenuEntrySubPresenter, IPrbListener):
    __customizationService = dependency.descriptor(ICustomizationService)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def onNavigate(self):
        self.__customizationService.showCustomization()

    def _getEvents(self):
        return ((self.__platoonCtrl.onMembersUpdate, self.__onPlatoonMembersUpdate), (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingChanged), (self._cameraController.onEnabledChange, self.__onCameraEnabledChange))

    def _getListeners(self):
        return ((events.PrebattleEvent.SWITCHED, self.__onPrbEntitySwitched, EVENT_BUS_SCOPE.LOBBY),)

    def _getState(self):
        if isVehicleUnavailable() or g_currentVehicle.isBroken() or not self.__lobbyContext.getServerSettings().isCustomizationEnabled():
            return VehicleMenuModel.DISABLED
        if g_currentVehicle.item.isOutfitLocked:
            return VehicleMenuModel.DISABLED
        if g_currentVehicle.item.isProgressionDecalsOnly:
            return VehicleMenuModel.ENABLED
        requestCriteria = ~REQ_CRITERIA.CUSTOMIZATION.HAS_TAGS([ItemTags.IS_3D])
        criteria = requestCriteria | REQ_CRITERIA.CUSTOMIZATION.FOR_VEHICLE(g_currentVehicle.item)
        hasStyle = bool(self.__itemsCache.items.getItems(GUI_ITEM_TYPE.STYLE, criteria, limit=1))
        return VehicleMenuModel.ENABLED if g_currentVehicle.isCustomizationEnabled() and hasStyle else VehicleMenuModel.DISABLED

    def __onPrbEntitySwitched(self, _):
        self.packEntry()

    def __onPlatoonMembersUpdate(self, *_):
        self.packEntry()

    @server_settings.serverSettingsChangeListener('isCustomizationEnabled')
    def __onServerSettingChanged(self, _):
        self.packEntry()

    def __onCameraEnabledChange(self, _):
        self.packEntry()
