# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/vehicle_selector.py
from collections import OrderedDict
import BigWorld
import SoundGroups
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.battle.event.team_info import makeTeamVehiclesInfo
from helpers import dependency, i18n
from gui.Scaleform.daapi.view.meta.BattleVehicleSelectorMeta import BattleVehicleSelectorMeta
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.EVENT import EVENT
from gui.shared.gui_items.Vehicle import getIconShopPath
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
HEADER_LIST = (EVENT.VEHICLE_SELECT_HEADER_1,
 EVENT.VEHICLE_SELECT_HEADER_2,
 EVENT.VEHICLE_SELECT_HEADER_3,
 EVENT.VEHICLE_SELECT_HEADER_4)
_VEHICLES_TAB = 0
_MAP_TAB = 1

class BattleVehicleSelector(BattleVehicleSelectorMeta, GameEventGetterMixin):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    itemsFactory = dependency.descriptor(IGuiItemsFactory)
    _VEHICLE_SELECTION_SOUND = 'ev_2019_secret_event_ui_tank_selection'
    _TIMER_START_SOUND_EVENT = 'timer'
    _TIMER_STOP_SOUND_EVENT = 'timer_stop'

    def __init__(self):
        super(BattleVehicleSelector, self).__init__()
        self.__headerList = iter(HEADER_LIST)
        self.__vehSelectorHeader = i18n.makeString(EVENT.VEHICLE_SELECT_HEADER_1)
        self.__vehicleList = OrderedDict()
        self.__timerCallback = None
        self.__isTimerSoundActive = False
        return

    def onVehicleSelect(self, identifier):
        ctrl = self.guiSessionProvider.dynamic.respawn
        if ctrl is not None:
            periodCtrl = self.guiSessionProvider.shared.arenaPeriod
            intCD = self.__vehicleList.keys()[identifier]
            for i, v in enumerate(self.__vehicleList.values()):
                v['selected'] = i == identifier
                v['vehicleState'] = self.__getVehicleState(v['enabled'], v['selected'])

            self.as_setDataS({'vehicleList': self.__vehicleList.values(),
             'header': self.__vehSelectorHeader})
            if periodCtrl.getPeriod() == ARENA_PERIOD.PREBATTLE:
                ctrl.setSwapVehicle(intCD)
            else:
                ctrl.chooseVehicleForRespawn(intCD)
            SoundGroups.g_instance.playSound2D(self._VEHICLE_SELECTION_SOUND)
        return

    def _populate(self):
        super(BattleVehicleSelector, self)._populate()
        ctrl = self.guiSessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onEventRespawnVehiclesUpdated += self.__onEventRespawnVehiclesUpdated
            ctrl.onRespawnInfoUpdated += self.__updateRespawnInfo
            ctrl.onPlayerRespawnLivesUpdated += self.__onPlayerRespawnLivesUpdated
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        periodCtrl = self.guiSessionProvider.shared.arenaPeriod
        if periodCtrl.getPeriod() == ARENA_PERIOD.PREBATTLE and self.__timerCallback is None:
            self.__updateTimer(periodCtrl.getEndTime())
        generals = self.generals
        if generals:
            generals.onUpdated += self.__onGeneralsUpdated
            self.__onGeneralsUpdated()
        return

    def setMapTab(self, mapTab):
        self.as_setTabsSelectedIndexS(_MAP_TAB if mapTab else _VEHICLES_TAB)
        self.as_setHelpVisibleS(mapTab)

    def enableCountdownSound(self):
        periodCtrl = self.guiSessionProvider.shared.arenaPeriod
        if not self.__isTimerSoundActive and not periodCtrl.getPeriod() == ARENA_PERIOD.PREBATTLE:
            SoundGroups.g_instance.playSound2D(self._TIMER_START_SOUND_EVENT)
            self.__isTimerSoundActive = True

    def disableCountdownSound(self):
        if self.__isTimerSoundActive:
            SoundGroups.g_instance.playSound2D(self._TIMER_STOP_SOUND_EVENT)
            self.__isTimerSoundActive = False

    def _dispose(self):
        ctrl = self.guiSessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onEventRespawnVehiclesUpdated -= self.__onEventRespawnVehiclesUpdated
            ctrl.onRespawnInfoUpdated -= self.__updateRespawnInfo
            ctrl.onPlayerRespawnLivesUpdated -= self.__onPlayerRespawnLivesUpdated
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        generals = self.generals
        if generals:
            generals.onUpdated -= self.__onGeneralsUpdated
        self.__stopTimer()
        super(BattleVehicleSelector, self)._dispose()
        return

    def __onEventRespawnVehiclesUpdated(self, newVehicleList):
        self.__vehicleList = OrderedDict()
        wasSelected = False
        for invID, vehicleType in enumerate(newVehicleList):
            enabled = bool(vehicleType.isEnable)
            selected = not wasSelected and enabled
            if selected:
                wasSelected = True
            vehicle = self.itemsFactory.createVehicle(typeCompDescr=vehicleType.intCD, inventoryID=invID)
            self.__vehicleList[vehicleType.intCD] = {'vehicleName': vehicleType.type.shortUserString,
             'vehicleIcon': getIconShopPath(vehicle.name, size=STORE_CONSTANTS.ICON_SIZE_SMALL),
             'vehicleState': self.__getVehicleState(enabled, selected),
             'vehicleTypeIcon': vehicle.type,
             'selected': selected,
             'enabled': enabled}

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.PREBATTLE:
            self.__updateTimer(periodEndTime)
            self.onVehicleSelect(0)
        if period == ARENA_PERIOD.BATTLE:
            self.__stopTimer()

    def __updateRespawnInfo(self, respawnInfo):
        self.__updateTimer(respawnInfo.autoRespawnTime)

    def __updateTimer(self, timeEnd):
        diffTime = timeEnd - BigWorld.serverTime()
        if diffTime <= 0:
            self.__stopTimer()
            return
        self.as_setTimerS(int(diffTime))
        self.__timerCallback = BigWorld.callback(1, lambda : self.__updateTimer(timeEnd))

    def __stopTimer(self):
        if self.__timerCallback is not None:
            BigWorld.cancelCallback(self.__timerCallback)
            self.__timerCallback = None
        return

    def __getVehicleState(self, enabled, selected):
        if not enabled:
            result = EVENT.VEHICLE_SELECT_DESTROYED
        else:
            result = EVENT.VEHICLE_SELECT_SELECTED if selected else EVENT.VEHICLE_SELECT_SELECT
        return i18n.makeString(result)

    def __onPlayerRespawnLivesUpdated(self, playerLives):
        try:
            self.__vehSelectorHeader = i18n.makeString(next(self.__headerList))
        except StopIteration:
            self.__vehSelectorHeader = ''

        self.as_setDataS({'vehicleList': self.__vehicleList.values(),
         'header': self.__vehSelectorHeader})

    def __onGeneralsUpdated(self):
        vehiclesInfo = makeTeamVehiclesInfo(self.generals, self.sessionProvider.getArenaDP(), self.itemsFactory)
        if vehiclesInfo:
            self.as_setTeamMissionsVehiclesS({'dataprovider': vehiclesInfo})
