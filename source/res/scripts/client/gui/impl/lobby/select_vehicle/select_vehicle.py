# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/select_vehicle/select_vehicle.py
from __future__ import absolute_import
from enum import Enum
import typing
from account_helpers.AccountSettings import AccountSettings, SELECT_VEHICLES_PLAYLIST, SELECT_VEHICLES_IS_ALL_VEHICLES
from frameworks.wulf import WindowFlags
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.select_vehicle.select_vehicle_model import SelectVehicleModel
from gui.impl.lobby.hangar.base.account_styles import AccountStyles
from gui.impl.lobby.hangar.base.vehicles_filter_component import VehiclesFilterComponent
from gui.impl.lobby.hangar.presenters.vehicle_filters_presenter import VehicleFiltersDataProvider
from gui.impl.lobby.hangar.presenters.vehicle_inventory_presenter import VehicleInventoryPresenter
from gui.impl.lobby.hangar.presenters.vehicle_playlists_presenter import VehiclePlaylistsPresenter
from gui.impl.lobby.hangar.presenters.vehicle_statistics_presenter import VehiclesStatisticsPresenter
from gui.impl.lobby.common.presenters.vehicles_info_presenter import VehiclesInfoPresenter
from gui.impl.lobby.select_vehicle.filter import SelectVehiclesCarouselFilter
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.pub.view_component import ViewComponent
from gui.shared.utils.requesters import REQ_CRITERIA
ALL_VEHICLES_CRITERIA = ~REQ_CRITERIA.VEHICLE.MODE_HIDDEN | ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE | ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE | ~REQ_CRITERIA.VEHICLE.SECRET | ~REQ_CRITERIA.VEHICLE.EPIC_BATTLE | ~REQ_CRITERIA.VEHICLE.CLAN_WARS

class SelectVehicleTitles(Enum):
    SELECT_ATTACKER = 'selectAttackerTitle'


class VehiclePlaylistsPresenterSession(VehiclePlaylistsPresenter):

    def _getSelectedID(self):
        return AccountSettings.getSessionSettings(SELECT_VEHICLES_PLAYLIST)

    def _setSelectedID(self, plID):
        AccountSettings.setSessionSettings(SELECT_VEHICLES_PLAYLIST, plID)
        return True


class SelectVehicleView(ViewComponent[SelectVehicleModel]):

    def __init__(self, title, onSelectCallback, currentVehicleCD=0):
        super(SelectVehicleView, self).__init__(R.views.mono.lobby.select_vehicle(), SelectVehicleModel)
        self._onSelectCallback = onSelectCallback
        self._randomVehicleFilter = VehiclesFilterComponent(ALL_VEHICLES_CRITERIA)
        self._randomInvVehicleFilter = VehiclesFilterComponent(REQ_CRITERIA.INVENTORY | ALL_VEHICLES_CRITERIA)
        self._carouselFilter = SelectVehiclesCarouselFilter()
        self._accountStyles = AccountStyles()
        self._title = title
        self._currentVehicleCD = currentVehicleCD

    @property
    def viewModel(self):
        return super(SelectVehicleView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self._randomVehicleFilter.initialize()
        self._randomInvVehicleFilter.initialize()
        self._accountStyles.initialize()
        self.viewModel.setTitle(backport.text(R.strings.dialogs.selectVehicle.dyn(self._title.value)()))
        self.viewModel.setCurrentVehicleCD(self._currentVehicleCD)
        self.viewModel.setIsAllVehicles(AccountSettings.getSessionSettings(SELECT_VEHICLES_IS_ALL_VEHICLES))
        super(SelectVehicleView, self)._onLoading(*args, **kwargs)

    def _getChildComponents(self):
        selectVehicles = R.aliases.select_vehicle.select_vehicle
        return {selectVehicles.VehiclesInfo(): lambda : VehiclesInfoPresenter(self._randomVehicleFilter),
         selectVehicles.VehiclesStatistics(): lambda : VehiclesStatisticsPresenter(self._randomInvVehicleFilter, self._accountStyles),
         selectVehicles.VehiclesInventory(): lambda : VehicleInventoryPresenter(self._randomInvVehicleFilter),
         selectVehicles.VehicleFilters(): lambda : VehicleFiltersDataProvider(self._carouselFilter),
         selectVehicles.VehiclePlaylists(): VehiclePlaylistsPresenterSession}

    def _getEvents(self):
        return ((self.viewModel.onSelect, self._onSelect), (self.viewModel.onIsAllVehiclesChange, self._onIsAllVehiclesChange))

    def _onIsAllVehiclesChange(self, args):
        value = args.get('value', False) if args else False
        AccountSettings.setSessionSettings(SELECT_VEHICLES_IS_ALL_VEHICLES, value)
        self.viewModel.setIsAllVehicles(value)

    def _onSelect(self, args):
        id = args.get('id', None) if args else None
        if id is not None:
            self._onSelectCallback(int(id))
            self.destroyWindow()
        return


class SelectVehicleWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, title, onSelectCallback, currentVehicleCD=0):
        super(SelectVehicleWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=SelectVehicleView(title, onSelectCallback, currentVehicleCD))
