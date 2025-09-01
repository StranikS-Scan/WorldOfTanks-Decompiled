# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/stats_display_components.py
import logging
import math
import typing
import BigWorld
import CGF
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from gui.shared.vehicle_stats_helper import getStatTrackersVehicleStats
from items.components.c11n_components import adjustToAllowedStatTrackerNumber
from items.components.c11n_constants import StatTrackerStatistic
from skeletons.gui.shared.utils import IHangarSpace
from PlayerEvents import g_playerEvents
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency, isPlayerAccount, isPlayerAvatar
from GenericComponents import AnimatorComponent, DecalComponent
from cgf_script.component_meta_class import CGFMetaTypes, ComponentProperty, registerComponent
from cgf_script.managers_registrator import autoregister, onAddedQuery, onProcessQuery
from vehicle_systems.vehicle_composition import findParentVehicle
if typing.TYPE_CHECKING:
    from typing import Optional
_logger = logging.getLogger(__name__)

@registerComponent
class StatisticDisplayComponent(object):
    domain = CGF.DomainOption.DomainClient
    delayList = ComponentProperty(type=CGFMetaTypes.FLOAT_LIST, editorName='Delays List', value=(0.25, 0.75, 1.25, 1.75))
    trackedStatistic = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Tracked statistic', value=StatTrackerStatistic.KILLS)

    def __init__(self):
        self.cachedValue = -1


class DelayDisplayUpdater(object):

    def __init__(self, symbolsList):
        self.symbolsList = symbolsList
        self.time = 0.0
        self.updatedIndexes = set()


def vehicleKillsStatsGetter(vehicle, arenaDP):
    from SimulatedVehicle import SimulatedVehicle
    vID = vehicle.id if not isinstance(vehicle, SimulatedVehicle) else vehicle.realVehicleID
    vStats = arenaDP.getVehicleStats(vID)
    return vStats.enemyKills if vStats is not None else 0


def roundDown(value, digitAfterDecimal):
    digitsFactor = 10 ** digitAfterDecimal
    return math.floor(value * digitsFactor) / digitsFactor


MAGNITUDE_SYMBOL_LIST = ['', 'K', 'M']
OVERFLOW_SYMBOL = '!'

def numberStatsFormatter(value, digitLimit):
    if value >= 1000 ** len(MAGNITUDE_SYMBOL_LIST):
        return OVERFLOW_SYMBOL * digitLimit
    magnitude = 0
    if abs(value) >= 10 ** digitLimit:
        while abs(value) >= 1000:
            magnitude += 1
            value /= 1000.0

    digitAfterDecimal = 0
    if magnitude:
        digitAfterDecimal = digitLimit - len(str(int(value))) - 1
    value = roundDown(value, digitAfterDecimal) if digitAfterDecimal else int(value)
    formattedValue = '{:.{}f}'.format(value, digitAfterDecimal)
    return '{}{}'.format(formattedValue, MAGNITUDE_SYMBOL_LIST[magnitude]).rjust(digitLimit, '0')


def displaySymbolsIterator(formattedNum):
    return [ (first if second != '.' else first + second) for first, second in zip(formattedNum, formattedNum[1:] + ' ') if first != '.' ]


def _isAvatarReady():
    return isPlayerAvatar() and BigWorld.player().userSeesWorld()


@autoregister(presentInAllWorlds=True)
class TrackedStatisticComponentManager(CGF.ComponentManager):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __availableStats = (StatTrackerStatistic.KILLS,)
    statisticDisplayQuery = CGF.QueryConfig(CGF.GameObject, StatisticDisplayComponent, DecalComponent)

    def activate(self):
        if _isAvatarReady():
            self.__onAvatarReady()
        elif not isPlayerAccount():
            g_playerEvents.onAvatarReady += self.__onAvatarReady
        else:
            g_playerEvents.onDossiersResync += self.__onDossierResync

    def deactivate(self):
        if isPlayerAvatar() and BigWorld.player().arena:
            BigWorld.player().arena.onVehicleStatisticsUpdate -= self.__onVehicleStatisticsUpdate
        g_playerEvents.onDossiersResync -= self.__onDossierResync
        g_playerEvents.onAvatarReady -= self.__onAvatarReady

    @onAddedQuery(StatisticDisplayComponent, DecalComponent, CGF.GameObject)
    def onAdded(self, statisticDisplay, decalComponent, gameObject):
        vehicle = findParentVehicle(gameObject)
        if vehicle:
            if isPlayerAvatar():
                self.__inBattleUpdate(statisticDisplay, vehicle, decalComponent)
            else:
                self.__hangarUpdate(statisticDisplay, vehicle, decalComponent)

    @onProcessQuery(CGF.GameObject, DelayDisplayUpdater, StatisticDisplayComponent, DecalComponent)
    def onProcess(self, go, updater, delayConfig, decal):
        updater.time += self.clock.gameDelta
        for i, symbols in enumerate(updater.symbolsList):
            if i in updater.updatedIndexes:
                continue
            if delayConfig.delayList[i] <= updater.time:
                decal.setCounterStickerValue(i, symbols)
                updater.updatedIndexes.add(i)

        if len(updater.updatedIndexes) == len(delayConfig.delayList):
            go.removeComponent(updater)

    @staticmethod
    def updateCounterValue(value, statisticDisplay, decalComponent, animatorCtx=None):
        allowedNum = adjustToAllowedStatTrackerNumber(value)
        if statisticDisplay.cachedValue == allowedNum:
            _logger.info('statistic display ignore cached value %s', allowedNum)
            return
        else:
            statisticDisplay.cachedValue = allowedNum
            decalLength = decalComponent.getStickerCount()
            formattedNumber = numberStatsFormatter(allowedNum, decalLength)
            symbolsList = displaySymbolsIterator(formattedNumber)
            if animatorCtx:
                go, animator = animatorCtx
                animator.start()
                if len(statisticDisplay.delayList) != len(symbolsList):
                    _logger.info('symbolsList length not equal to delayList length')
                    return
                if go.findComponentByType(DelayDisplayUpdater) is not None:
                    go.removeComponentByType(DelayDisplayUpdater)
                go.createComponent(DelayDisplayUpdater, symbolsList)
                return
            for i, symbols in enumerate(symbolsList):
                decalComponent.setCounterStickerValue(i, symbols)

            return

    def __onAvatarReady(self):
        if isPlayerAvatar() and BigWorld.player().arena:
            if BONUS_CAPS.checkAny(BigWorld.player().arena.bonusType, BONUS_CAPS.STAT_TRACKERS_STATS):
                BigWorld.player().arena.onVehicleStatisticsUpdate += self.__onVehicleStatisticsUpdate

    def __onDossierResync(self, *_):
        if not self.__hangarSpace.spaceInited:
            return
        for gameObject, statisticDisplay, decalComponent in self.statisticDisplayQuery:
            if statisticDisplay.trackedStatistic in self.__availableStats:
                vehicle = findParentVehicle(gameObject)
                self.__hangarUpdate(statisticDisplay, vehicle, decalComponent)

    def __onVehicleStatisticsUpdate(self, vehicleID):
        for gameObject, statisticDisplay, decalComponent in self.statisticDisplayQuery:
            vehicle = findParentVehicle(gameObject)
            if vehicle.id == vehicleID and statisticDisplay.trackedStatistic in self.__availableStats:
                animator = gameObject.findComponentByType(AnimatorComponent)
                animatorCtx = (gameObject, animator) if animator else None
                self.__inBattleUpdate(statisticDisplay, vehicle, decalComponent, animatorCtx)

        return

    def __inBattleUpdate(self, statisticDisplay, vehicle, decalComponent, animatorCtx=None):
        arena = BigWorld.player().arena
        arenaDP = self.__sessionProvider.getArenaDP()
        if not arena:
            _logger.error('arena is None')
            return
        if not arenaDP:
            _logger.error('arenaDP is None')
            return
        if statisticDisplay.trackedStatistic == StatTrackerStatistic.KILLS:
            enemyFrags = 0
            if BONUS_CAPS.checkAny(arena.bonusType, BONUS_CAPS.STAT_TRACKERS_STATS):
                enemyFrags = vehicleKillsStatsGetter(vehicle, arenaDP)
            value = vehicle.publicInfo.stFrags + enemyFrags
        else:
            _logger.error('Unknown tracked statistics type: %s', statisticDisplay.trackedStatistic)
            return
        self.updateCounterValue(value, statisticDisplay, decalComponent, animatorCtx)

    def __hangarUpdate(self, statisticDisplay, vehicle, decalComponent):
        vehCD = vehicle.typeDescriptor.type.compactDescr
        value = 0
        if statisticDisplay.trackedStatistic == StatTrackerStatistic.KILLS:
            value = getStatTrackersVehicleStats(vehCD, vehicle)
        else:
            _logger.error('Unknown tracked statistics type: %s', statisticDisplay.trackedStatistic)
        self.updateCounterValue(value, statisticDisplay, decalComponent)
