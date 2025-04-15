# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/minimap/plugins.py
import typing
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.battle.classic.minimap import GlobalSettingsPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap import plugins
from gui.Scaleform.daapi.view.battle.shared.minimap.entries import VehicleEntry
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import ADDITIONAL_FEATURES, SettingsTypes
from fall_tanks.gui.battle_control.arena_info.arena_vos import FallTanksKeys
from fall_tanks.gui.battle_control.mixins import FallTanksBattleMixin, PostmortemMixin
from fall_tanks.gui.fall_tanks_gui_constants import FALL_TANKS_GUI_PROPS_NAME
if typing.TYPE_CHECKING:
    from fall_tanks.gui.battle_control.arena_info.interfaces import IFallTanksVehicleInfo

class FallTanksVehicleEntry(VehicleEntry):
    __slots__ = ('__isPermanentInactive',)

    def __init__(self, entryID, active, matrix=None):
        super(FallTanksVehicleEntry, self).__init__(entryID, active, matrix=matrix)
        self.__isPermanentInactive = False

    def setActive(self, active):
        active = active if not self.__isPermanentInactive else False
        return super(FallTanksVehicleEntry, self).setActive(active)

    def isPermanentInactive(self):
        return self.__isPermanentInactive

    def setIsPermanentInactive(self, isPermanentInactive):
        self.__isPermanentInactive = isPermanentInactive


class FallTanksGlobalSettingsPlugin(GlobalSettingsPlugin, FallTanksBattleMixin, PostmortemMixin):

    def start(self):
        super(FallTanksGlobalSettingsPlugin, self).start()
        self.startFallTanksAttachedListening(self.__onFallTanksAttachedInfoUpdate)
        self.startPostmortemListening(self.__onPostMortemSwitched, self.__onRespawnBaseMoving)
        self.__invalidateVisibility()

    def stop(self):
        self.stopPostmortemListening(self.__onPostMortemSwitched, self.__onRespawnBaseMoving)
        self.stopFallTanksAttachedListening(self.__onFallTanksAttachedInfoUpdate)
        super(FallTanksGlobalSettingsPlugin, self).stop()

    def _toogleVisible(self):
        if self.__canBeShown():
            super(FallTanksGlobalSettingsPlugin, self)._toogleVisible()

    def __canBeShown(self, attachedInfo=None):
        attachedInfo = attachedInfo or self.getFallTanksAttachedVehicleInfo()
        return not (attachedInfo.isPlayerVehicle and attachedInfo.isFinished and self.isInPostmortem())

    def __onFallTanksAttachedInfoUpdate(self, attachedInfo):
        self.__invalidateVisibility(attachedInfo)

    def __onPostMortemSwitched(self, _, __):
        self.__invalidateVisibility()

    def __onRespawnBaseMoving(self):
        self.__invalidateVisibility()

    def __invalidateVisibility(self, attachedInfo=None):
        self._parentObj.as_setVisibleS(self._isVisible and self.__canBeShown(attachedInfo))


class FallTanksPersonalEntriesPlugin(plugins.PersonalEntriesPlugin):

    def _canShowViewRangeCircle(self):
        return False

    def _canShowMaxViewRangeCircle(self):
        return False

    def _canShowMinSpottingRangeCircle(self):
        return False

    def _canShowDrawRangeCircle(self):
        return False


class FallTanksArenaVehiclesPlugin(plugins.ArenaVehiclesPlugin):
    __VEHICLE_SYMBOL_NAME = 'FallTanksVehicleMinimapEntryUI'

    def __init__(self, parent):
        super(FallTanksArenaVehiclesPlugin, self).__init__(parent=parent, clazz=FallTanksVehicleEntry)

    def _getSymbolName(self):
        return self.__VEHICLE_SYMBOL_NAME

    def _getGuiPropsName(self, guiProps):
        return FALL_TANKS_GUI_PROPS_NAME

    def _convertSettingToFeatures(self, value, previous, settingsType):
        if settingsType == SettingsTypes.MinimapHitPoint:
            return ADDITIONAL_FEATURES.OFF
        return ADDITIONAL_FEATURES.BY_REQUEST if settingsType == SettingsTypes.MinimapVehicles else super(FallTanksArenaVehiclesPlugin, self)._convertSettingToFeatures(value, previous, settingsType)

    def updateVehiclesStats(self, updated, arenaDP):
        for vStats in (vStats for _, vStats in updated if vStats.vehicleID in self._entries):
            vehicleID = vStats.vehicleID
            vStats = self.sessionProvider.getArenaDP().getVehicleStats(vehicleID)
            if vStats.gameModeSpecific.getValue(FallTanksKeys.IS_LEAVER):
                entry = self._entries[vehicleID]
                entry.setIsPermanentInactive(True)

    def _hideVehicle(self, entry):
        super(FallTanksArenaVehiclesPlugin, self)._hideVehicle(entry)
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        if periodCtrl.getPeriod() in (ARENA_PERIOD.PREBATTLE, ARENA_PERIOD.WAITING):
            entry.setIsPermanentInactive(True)
