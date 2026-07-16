# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/perk_ctrl.py
from __future__ import absolute_import
from copy import deepcopy
from future.utils import viewitems
from typing import TYPE_CHECKING
import BigWorld
import Event
import BattleReplay
from helpers import dependency
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
from skeletons.gui.battle_session import IBattleSessionProvider
from items.tankmen import getSkillsConfig
from skeletons.account_helpers.settings_core import ISettingsCore, ISettingsCache
from account_helpers.settings_core import settings_constants
from items.components.perks_constants import PerkState
if TYPE_CHECKING:
    from Vehicle import Vehicle
_UPDATE_FUN_PREFIX = '_updatePerk'
_DATA_KEY_PERK_ID = 'perkID'
_INTERVAL_FOR_SAME_NOTIFICATION = 6
_CREW_SETTING = set(settings_constants.SITUATIONAL_PERKS.ALL())
_CREW_SETTING.add(settings_constants.BATTLE_EVENTS.CREW_PERKS)

class PerksController(ViewComponentsController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)
    settingsCache = dependency.descriptor(ISettingsCache)

    def __init__(self):
        super(PerksController, self).__init__()
        self.onPerkChanged = Event.Event()
        self._prevPanelState = {}
        self._prevRibbonsState = {}
        self._prevArenaPeriod = None
        self.__hiddenPerks = set()
        self.__hiddenAllPerks = False
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.PERKS

    def updatePerks(self, perks):
        if not (BattleReplay.isPlaying() or self.settingsCache.isSynced()):
            return
        else:
            changes, currentPanelState = self._getCurrentState(self.__checkPerksBySettings(perks), self._prevPanelState)
            if self._isInBattle():
                for viewCmp in self._viewComponents:
                    viewCmp.updatePerks(changes, self._prevPanelState)

            for perkID, data in viewitems(changes):
                updater = getattr(self, _UPDATE_FUN_PREFIX + str(perkID), None)
                if updater is not None:
                    updater(perkID=perkID, **data)

            self._prevPanelState = deepcopy(currentPanelState)
            return

    def notifyRibbonChanges(self, ribbons):
        if not self._isInBattle():
            return
        changes, currentRibbonsState = self._getCurrentState(self.__checkRibbonsBySettings(ribbons), self._prevRibbonsState)
        for perkID, perkData in sorted(viewitems(changes), key=lambda item: item[1]['endTime']):
            if perkData['endTime'] > BigWorld.serverTime() and perkData.get('state', PerkState.ACTIVE):
                prevPerkEndTime = self._prevRibbonsState.get(perkID, {}).get('endTime', 0)
                if perkData['endTime'] - prevPerkEndTime > _INTERVAL_FOR_SAME_NOTIFICATION:
                    self.onPerkChanged({_DATA_KEY_PERK_ID: perkID})

        self._prevRibbonsState = deepcopy(currentRibbonsState)

    def startControl(self, *args):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling += self._onVehicleControlling
        g_playerEvents.onArenaPeriodChange += self._onArenaPeriodChange
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.settingsCache.onSyncCompleted += self.__onSettingsSyncCompleted
        return

    def stopControl(self, *args):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling -= self._onVehicleControlling
        self.onPerkChanged.clear()
        g_playerEvents.onArenaPeriodChange -= self._onArenaPeriodChange
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.settingsCache.onSyncCompleted -= self.__onSettingsSyncCompleted
        return

    def _canShowPerk(self, perkID):
        return not self.__hiddenAllPerks and getSkillsConfig().vsePerkToSkill.get(perkID) not in self.__hiddenPerks

    def _onVehicleControlling(self, vehicle):
        for perkID, data in viewitems(self._prevPanelState):
            updater = getattr(self, _UPDATE_FUN_PREFIX + str(perkID), None)
            if updater is not None:
                updater(vehicle=vehicle, perkID=perkID, **data)

        if self._isInBattle():
            perks = self.__checkPerksBySettings(vehicle.perks)
            for viewCmp in self._viewComponents:
                viewCmp.setPerks(perks)

        return

    def _isInBattle(self):
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        return periodCtrl is not None and periodCtrl.getPeriod() == ARENA_PERIOD.BATTLE

    def _onArenaPeriodChange(self, period, *args):
        if self._prevArenaPeriod == period:
            return
        self._prevArenaPeriod = period
        if period != ARENA_PERIOD.BATTLE:
            return
        ctrl = self.sessionProvider.shared.vehicleState
        vehicle = ctrl.getControllingVehicle()
        if not vehicle:
            return
        perks = self.__checkPerksBySettings(vehicle.perks)
        for viewCmp in self._viewComponents:
            viewCmp.setPerks(perks)
            viewCmp.updatePerks(self._prevPanelState, {})

        for perkID in self._prevPanelState:
            if self._canShowPerk(perkID):
                self.onPerkChanged({_DATA_KEY_PERK_ID: perkID})

    def _getCurrentState(self, source, prevState):
        currentState = {item[_DATA_KEY_PERK_ID]:{key:item[key] for key in set(item.keys()) ^ {_DATA_KEY_PERK_ID}} for item in source}
        changes = {}
        for perkID, data in viewitems(currentState):
            if perkID not in prevState or prevState[perkID] != data:
                changes[perkID] = data

        return (changes, currentState)

    def _updatePerk403(self, perkID, state, coolDown, lifeTime, vehicle=None):
        isActive = bool(state)
        if vehicle is None:
            vehicle = BigWorld.player().getVehicleAttached()
        if vehicle is not None:
            BigWorld.player().updateVehicleQuickShellChanger(vehicle.id, isActive)
        return

    def __checkPerksBySettings(self, perks):
        data = deepcopy(perks)
        for perk in data:
            if not self._canShowPerk(perk['perkID']):
                perk['state'] = PerkState.INACTIVE

        return data

    def __checkRibbonsBySettings(self, ribbons):
        return {perk for perk in ribbons if self._canShowPerk(perk['perkID'])}

    def __onSettingsSyncCompleted(self):
        self.settingsCache.onSyncCompleted -= self.__onSettingsSyncCompleted
        self.__updateHiddenPerks()

    def __onSettingsChanged(self, diff):
        if any((name in _CREW_SETTING for name in diff)):
            self.__updateHiddenPerks()
            vehicle = self.sessionProvider.shared.vehicleState.getControllingVehicle()
            if vehicle:
                self.updatePerks(vehicle.perks)

    def __updateHiddenPerks(self):
        self.__hiddenPerks.clear()
        perksVisibleOptions = self.settingsCore.packSettings(settings_constants.SITUATIONAL_PERKS.ALL())
        self.__hiddenAllPerks = not self.settingsCore.getSetting(settings_constants.BATTLE_EVENTS.CREW_PERKS)
        for perkName, isVisible in viewitems(perksVisibleOptions):
            if not isVisible:
                self.__hiddenPerks.add(perkName)
