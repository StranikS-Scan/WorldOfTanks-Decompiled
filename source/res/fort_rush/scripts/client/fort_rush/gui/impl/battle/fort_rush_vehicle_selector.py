# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/battle/fort_rush_vehicle_selector.py
from __future__ import absolute_import
import logging
import math
import time
from gui import InputHandler
from gui.battle_control import avatar_getter
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.hangar.base.account_styles import AccountStyles
from gui.impl.pub.view_component import ViewComponent
from gui.shared import EVENT_BUS_SCOPE, EventPriority
from gui.shared.gui_items.Vehicle import Vehicle
from gui.veh_post_progression.helpers import getInstalledShells, updateInvInstalled
from helpers import dependency
from items import vehicles as vehiclesCache
from post_progression_common import TankSetups, TankSetupLayouts, TankSetupGroupsId
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IVehiclePlaylistsController
from skeletons.gui.shared import IItemsCache
import BigWorld
import typing
from IndividualRespawnTimerComponent import IndividualRespawnTimerComponent
from event_platform.respawns.helpers import getRespawnPolicyComponent
from fort_rush.gui.fort_rush_gui_constants import BATTLE_CTRL_ID
from fort_rush.gui.impl.battle.fort_rush_battle_loadout_presenter import FortRushBattleLoadoutPresenter
from fort_rush.gui.impl.battle.presenters.fort_rush_respawn_vehicle_filter import FortRushRespawnVehicleFilter
from fort_rush.gui.impl.battle.presenters.fort_rush_vehicle_filters_presenter import FortRushVehicleFiltersPresenter
from fort_rush.gui.impl.battle.presenters.fort_rush_vehicle_info_presenter import FortRushVehiclesInfoPresenter
from fort_rush.gui.impl.battle.presenters.fort_rush_vehicle_statistics_presenter import FortRushVehicleStatisticsPresenter
from fort_rush.gui.impl.gen.view_models.views.battle.views.fort_rush_playlist_item_model import FortRushPlaylistItemModel
from fort_rush.gui.impl.gen.view_models.views.battle.views.fort_rush_vehicle_selector_view_model import FortRushVehicleSelectorViewModel, AnnouncementTypeEnum
from fort_rush.helpers.utils import retrievePlayerRespawnComponent
from fort_rush.skeletons.battle_controller import IFortRushBattleController
import CommandMapping
from event_platform.gui.shared.events import RespawnFrameworkEvent
from gui.impl import backport
if typing.TYPE_CHECKING:
    from typing import Optional
    from RespawnFrameworkVehicleComponent import RespawnFrameworkVehicleComponent
_logger = logging.getLogger(__name__)
_SETUP_NAME_TO_LAYOUT = {TankSetups.SHELLS: TankSetupLayouts.SHELLS,
 TankSetups.EQUIPMENT: TankSetupLayouts.EQUIPMENT,
 TankSetups.OPTIONAL_DEVICES: TankSetupLayouts.OPTIONAL_DEVICES,
 TankSetups.BATTLE_BOOSTERS: TankSetupLayouts.BATTLE_BOOSTERS}

class FortRushVehicleSelectorView(ViewComponent):
    LAYOUT_ID = R.views.fort_rush.mono.battle.fort_rush_vehicle_selector()
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _itemsCache = dependency.descriptor(IItemsCache)
    _vehPlaylistsCtrl = dependency.descriptor(IVehiclePlaylistsController)
    _fortRushCtrl = dependency.descriptor(IFortRushBattleController)

    def __init__(self):
        super(FortRushVehicleSelectorView, self).__init__(layoutID=self.LAYOUT_ID, model=FortRushVehicleSelectorViewModel)
        self._loadoutPresenter = None
        self._currentVehicleCD = 0
        self._currentVehicleItem = None
        self._vehPlaylistsCtrl.initPlayLists()
        self._respawnVehicleFilter = FortRushRespawnVehicleFilter()
        self._accountStyles = AccountStyles()
        return

    @property
    def viewModel(self):
        return super(FortRushVehicleSelectorView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self._accountStyles.initialize()
        self._respawnVehicleFilter.initialize()
        super(FortRushVehicleSelectorView, self)._onLoading(*args, **kwargs)
        self._setVehicleEligibilityConfig(self.viewModel)
        self.viewModel.onTankSelected += self._onTankSelected
        InputHandler.g_instance.onKeyDown += self._handleSetupSwitchKey

    def _setVehicleEligibilityConfig(self, viewModel):
        eligibleVehicleTiers = self._fortRushCtrl.getEligibleVehicleTiers()
        tiers = viewModel.getEligibleVehicleTiers()
        tiers.clear()
        tiers.reserve(len(eligibleVehicleTiers))
        for tier in eligibleVehicleTiers:
            tiers.addNumber(tier)

        tiers.invalidate()
        forbiddenVehClasses = self._fortRushCtrl.getForbiddenVehClasses()
        vehClasses = viewModel.getForbiddenVehClasses()
        vehClasses.clear()
        vehClasses.reserve(len(forbiddenVehClasses))
        for vehClass in forbiddenVehClasses:
            vehClasses.addString(vehClass)

        vehClasses.invalidate()

    def _finalize(self):
        self.viewModel.onTankSelected -= self._onTankSelected
        InputHandler.g_instance.onKeyDown -= self._handleSetupSwitchKey
        self._accountStyles.destroy()
        self._accountStyles = None
        self._respawnVehicleFilter.destroy()
        self._respawnVehicleFilter = None
        super(FortRushVehicleSelectorView, self)._finalize()
        return

    def _getChildComponents(self):
        hangar = R.aliases.hangar.shared
        self._loadoutPresenter = FortRushBattleLoadoutPresenter(None)
        self._loadoutPresenter.setOnSwitchCallback(self._onLoadoutSwitch)
        return {hangar.VehiclesInfo(): lambda : FortRushVehiclesInfoPresenter(self._respawnVehicleFilter),
         hangar.Loadout(): lambda : self._loadoutPresenter,
         hangar.VehicleFilters(): FortRushVehicleFiltersPresenter,
         hangar.VehiclesStatistics(): lambda : FortRushVehicleStatisticsPresenter(self._respawnVehicleFilter, self._accountStyles)}

    def _getListeners(self):
        listeners = [(RespawnFrameworkEvent.VEHICLES_LOADED,
          self._updateRespawnVehiclesModel,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.HIGH)]
        return listeners

    def _getEvents(self):
        spawnCtrl = self._sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.FORT_RUSH_GUI_CTRL)
        return [] if not spawnCtrl else [(spawnCtrl.onShowSpawnPoints, self._onShowSpawnPoints), (spawnCtrl.onCloseSpawnPoints, self._onCloseSpawnPoints)]

    @property
    def _respawnCtrl(self):
        return self._sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.FORT_RUSH_GUI_CTRL)

    def _updateSelectedRespawnVehicle(self, respawnComponent):
        respawnComponent.updateSelectedRespawnVehicle(self._currentVehicleCD)
        self._currentVehicleItem = self._buildVehicleFromSetups(self._currentVehicleCD, respawnComponent)
        if self._loadoutPresenter:
            self._loadoutPresenter.updateVehicle(self._currentVehicleItem)

    @args2params(int)
    def _onTankSelected(self, id):
        if id == self._currentVehicleCD:
            return
        else:
            respawnComponent = retrievePlayerRespawnComponent()
            if respawnComponent is None:
                return
            self.viewModel.setSelectedTankId(id)
            self._currentVehicleCD = id
            self._updateSelectedRespawnVehicle(respawnComponent)
            return

    def _onShowSpawnPoints(self, points):
        vehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
        if vehicle is None:
            _logger.warning('[FORT_RUSH][RESPAWN][vehicle_selector] _onShowSpawnPoints: playerVehicle is None')
            return
        else:
            timerComponent = getRespawnPolicyComponent(vehicle.spaceID, vehicle.id, IndividualRespawnTimerComponent)
            if timerComponent is None:
                _logger.warning('[FORT_RUSH][RESPAWN][vehicle_selector] _onShowSpawnPoints: timerComponent is None')
                return
            delta = math.ceil(BigWorld.serverTime() - timerComponent.timeOfDeath)
            with self.viewModel.transaction():
                self.viewModel.setSelectedTankId(self._currentVehicleCD)
                self.viewModel.setIsAnnouncementVisible(True)
                self.viewModel.setAnnouncementCountdownTargetTime(time.time() + (timerComponent.respawnDelay - delta))
                self.viewModel.setAnnouncementHeading(backport.text(R.strings.fort_rush.respawnTimer.title()))
                self.viewModel.setAnnouncementDescription(backport.text(R.strings.fort_rush.respawnTimer.description()))
                self.viewModel.setAnnouncementType(AnnouncementTypeEnum.RESPAWN)
            return

    def _onCloseSpawnPoints(self, *args, **kwargs):
        self.viewModel.setIsAnnouncementVisible(False)

    def _updateRespawnVehiclesModel(self, _):
        vehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
        respawnComponent = retrievePlayerRespawnComponent()
        if respawnComponent is None:
            return
        else:
            with self.viewModel.transaction() as viewModel:
                self._setPlaylists(viewModel)
            self._currentVehicleCD = vehicle.typeDescriptor.type.compactDescr
            self._updateSelectedRespawnVehicle(respawnComponent)
            return

    def _setPlaylists(self, model):
        playlists = model.getPlaylists()
        playlists.clear()
        for playlistID, playlistStrData in self._vehPlaylistsCtrl.iterPlaylists():
            playlistData = self._vehPlaylistsCtrl.simplePlayListParser(playlistStrData)
            if playlistData is None:
                continue
            playlistModel = FortRushPlaylistItemModel()
            playlistModel.setId(playlistID)
            playlistModel.setName(playlistData.title)
            for vehID in playlistData.list:
                playlistModel.getVehicleIds().addNumber(vehID)

            playlists.addViewModel(playlistModel)

        playlists.invalidate()
        return

    def _buildVehicleFromSetups(self, vehicleCD, respawnComponent):
        vehData = respawnComponent.respawnVehicles.get(vehicleCD) if respawnComponent.respawnVehicles else None
        if not vehData:
            return
        else:
            compDescr = vehData['compDescr']
            vehSetups = vehData.get('vehSetups', {})
            vehSetupsIndexes = vehData.get('vehSetupsIndexes', {})
            invData = {_SETUP_NAME_TO_LAYOUT[key]:value for key, value in vehSetups.items() if key in _SETUP_NAME_TO_LAYOUT}
            invData['layoutIndexes'] = vehSetupsIndexes
            vehDescr = vehiclesCache.VehicleDescr(compactDescr=compDescr)
            shellsLayoutKey = (vehDescr.turret.compactDescr, vehDescr.gun.compactDescr)
            shellsLayoutRaw = invData.get(TankSetupLayouts.SHELLS, [])
            shellsCDs = [ shot.shell.compactDescr for shot in vehDescr.gun.shots ]
            invData['shells'] = getInstalledShells(shellsCDs, shellsLayoutRaw)
            invData[TankSetupLayouts.SHELLS] = {shellsLayoutKey: shellsLayoutRaw}
            updateInvInstalled(invData, vehSetupsIndexes)
            vehicleItem = Vehicle(strCompactDescr=compDescr, invData=invData)
            _logger.debug('[FORT_RUSH][LOADOUT] Built vehicle=%s consumables=%s optDevices=%s setups=%s', vehicleItem.shortUserName, [ (c.intCD if c else None) for c in vehicleItem.consumables.installed.getItems(ignoreEmpty=False) ], [ (d.intCD if d else None) for d in vehicleItem.optDevices.installed.getItems(ignoreEmpty=False) ], vehicleItem.setupLayouts.groups)
            return vehicleItem

    def _onLoadoutSwitch(self, groupId, newIndex):
        respawnComponent = retrievePlayerRespawnComponent()
        if respawnComponent is None:
            _logger.warning('[FORT_RUSH][RESPAWN][vehicle_selector] _onLoadoutSwitch: respawn component not found for vehicle %s', avatar_getter.getPlayerVehicleID())
            return
        else:
            vehData = respawnComponent.respawnVehicles.get(self._currentVehicleCD)
            if not vehData:
                _logger.warning('[FORT_RUSH][RESPAWN][vehicle_selector] _onLoadoutSwitch: vehData is None for vehicle %s', avatar_getter.getPlayerVehicleID())
                return
            vehSetupsIndexes = dict(vehData.get('vehSetupsIndexes', {}))
            vehSetupsIndexes[groupId] = newIndex
            vehData['vehSetupsIndexes'] = vehSetupsIndexes
            self._updateSelectedRespawnVehicle(respawnComponent)
            return

    def _handleSetupSwitchKey(self, event):
        spawnController = self._sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.FORT_RUSH_GUI_CTRL)
        if not spawnController.isSpawnPointsVisible:
            return
        else:
            cmdMap = CommandMapping.g_instance
            if cmdMap.isFired(CommandMapping.CMD_AMMUNITION_SHORTCUT_SWITCH_SETUP_1, event.key):
                groupId = TankSetupGroupsId.OPTIONAL_DEVICES_AND_BOOSTERS
            elif cmdMap.isFired(CommandMapping.CMD_AMMUNITION_SHORTCUT_SWITCH_SETUP_2, event.key):
                groupId = TankSetupGroupsId.EQUIPMENT_AND_SHELLS
            else:
                return
            battleVehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
            if battleVehicle is None:
                _logger.warning('[FORT_RUSH][RESPAWN][vehicle_selector] _handleSetupSwitchKey: battleVehicle is None')
                return
            if groupId in battleVehicle.disabledSwitches:
                _logger.warning('[FORT_RUSH][RESPAWN][vehicle_selector] _handleSetupSwitchKey: switch is disabled for groupID %s', groupId)
                return
            respawnComponent = retrievePlayerRespawnComponent()
            if respawnComponent is None or not respawnComponent.respawnVehicles:
                _logger.warning('[FORT_RUSH][RESPAWN][vehicle_selector] _handleSetupSwitchKey: respawn component not found for vehicle %s', avatar_getter.getPlayerVehicleID())
                return
            vehData = respawnComponent.respawnVehicles.get(self._currentVehicleCD)
            if not vehData:
                _logger.warning('[FORT_RUSH][RESPAWN][vehicle_selector] _handleSetupSwitchKey: vehData is None for vehicle %s', avatar_getter.getPlayerVehicleID())
                return
            vehSetupsIndexes = vehData.get('vehSetupsIndexes', {})
            currentIndex = vehSetupsIndexes.get(groupId, 0)
            if self._currentVehicleItem is None:
                return
            totalSetups = self._currentVehicleItem.setupLayouts.getGroupCapacity(groupId)
            if totalSetups <= 1:
                return
            newIndex = 0 if currentIndex >= totalSetups - 1 else currentIndex + 1
            self._onLoadoutSwitch(groupId, newIndex)
            return
