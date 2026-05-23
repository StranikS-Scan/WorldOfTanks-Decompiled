# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/stat_track_component.py
import collections
import typing
import BigWorld
import CGF
from Event import EventsSubscriber
from GenericComponents import DecalComponent, EntityGOSync, AnimatorComponent
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister
from constants import ARENA_BONUS_TYPE
from helpers import isPlayerAccount, isPlayerAvatar
from debug_utils import LOG_WARNING, LOG_ERROR
from items.components.c11n_constants import STAT_TRACK_PROHIBITED_VALUES
if typing.TYPE_CHECKING:
    from typing import Any

@registerComponent
class StatTrackNumberComponent(object):
    domain = CGF.DomainOption.DomainClient
    statTrackCounterType = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Type of statistic to display', value='frags', annotations={'comboBox': {'frags': 'frags'}})
    digitNumber = ComponentProperty(type=CGFMetaTypes.INT, editorName='Number of digits in decal', value=4)
    decalComponent = ComponentProperty(type=CGFMetaTypes.LINK, editorName='DecalLink', value=DecalComponent)
    animatorComponent = ComponentProperty(type=CGFMetaTypes.LINK, editorName='AnimatorLink', value=AnimatorComponent)


@autoregister(presentInAllWorlds=True)
class StatTrackComponentManager(CGF.ComponentManager):
    _MAX_DIGIT = '9'
    _DARK_ZERO = '*'

    def __init__(self, *args):
        super(StatTrackComponentManager, self).__init__(*args)
        self.__eventSubscriber = EventsSubscriber()
        self.__vehWithStatTrack = collections.defaultdict(set)
        self.__componentGOToVehicleID = {}
        self.__shouldCountKillOnArena = False
        self.__isInHangar = False

    def activate(self):
        self.__isInHangar = isPlayerAccount()
        if self.__isInHangar or not isPlayerAvatar():
            return
        self.__shouldCountKillOnArena = BigWorld.player().arena.bonusType == ARENA_BONUS_TYPE.REGULAR
        if self.__shouldCountKillOnArena:
            self.__eventSubscriber.subscribeToEvent(BigWorld.player().arena.onVehicleKilled, self.__onVehicleKilled)

    def deactivate(self):
        self.__eventSubscriber.unsubscribeFromAllEvents()
        self.__vehWithStatTrack.clear()
        self.__componentGOToVehicleID.clear()

    @onAddedQuery(StatTrackNumberComponent, CGF.GameObject)
    def onAdded(self, statTrackComponent, gameObject):
        vehicleID = self.__getVehicleID(gameObject)
        counterValue = self.__getFragsCount(vehicleID)
        counterValue = STAT_TRACK_PROHIBITED_VALUES.get(counterValue, counterValue)
        counterValue = self.__formatValue(counterValue, statTrackComponent.digitNumber)
        self.__updateComponentCounter(statTrackComponent, counterValue)
        self.__vehWithStatTrack[vehicleID].add(statTrackComponent)

    @onRemovedQuery(StatTrackNumberComponent, CGF.GameObject)
    def onRemoved(self, statTrackComponent, gameObject):
        vehicleID = self.__componentGOToVehicleID.get(gameObject.id)
        if vehicleID is not None:
            self.__vehWithStatTrack[vehicleID].discard(statTrackComponent)
        if self.__isInHangar and vehicleID:
            self.__componentGOToVehicleID.pop(gameObject.id)
        return

    def __getVehicleID(self, gameObject):
        vehicleID = self.__componentGOToVehicleID.get(gameObject.id, None)
        if vehicleID is not None:
            return vehicleID
        else:
            hierarchy = CGF.HierarchyManager(self.spaceID)
            rootGameObject = hierarchy.getTopMostParent(gameObject)
            goSyncComponent = rootGameObject.findComponentByType(EntityGOSync)
            if goSyncComponent is None:
                LOG_ERROR('No vehicle GO found!')
                return
            vehicleID = goSyncComponent.entity.id
            self.__componentGOToVehicleID[gameObject.id] = vehicleID
            return vehicleID

    def __getFragsCount(self, vehicleID):
        if self.__isInHangar:
            vehicle = BigWorld.entities[vehicleID]
            counterValue = vehicle.appearance.getThisVehicleDossierStatTrackFrags()
        else:
            clientArena = BigWorld.player().arena
            counterValue = clientArena.vehicles[vehicleID]['statTrackFrags']
            if self.__shouldCountKillOnArena:
                vehicleStatistics = clientArena.statistics[vehicleID]
                killedOnArena = vehicleStatistics['frags'] + vehicleStatistics['teamKillFrags']
                counterValue += killedOnArena
        return counterValue

    def __formatValue(self, counterValue, digitNumber):
        if counterValue == -1:
            LOG_WARNING('No info about vehicle frags from server')
            counterValue = 0
        counterValueStr = str(counterValue)
        if len(counterValueStr) > digitNumber:
            counterValueStr = self._MAX_DIGIT * digitNumber
        elif len(counterValueStr) < digitNumber:
            counterValueStr = counterValueStr.zfill(digitNumber)
        return counterValueStr

    def __onVehicleKilled(self, victimID, killerID, *_):
        if killerID not in self.__vehWithStatTrack:
            return
        vehiclesInfo = BigWorld.player().arena.vehicles
        if vehiclesInfo[victimID]['team'] == vehiclesInfo[killerID]['team']:
            return
        counterValue = self.__getFragsCount(killerID)
        decalComponents = self.__vehWithStatTrack[killerID]
        for component in decalComponents:
            if counterValue in STAT_TRACK_PROHIBITED_VALUES or counterValue > int(component.digitNumber * self._MAX_DIGIT):
                continue
            counterValueStr = self.__formatValue(counterValue, component.digitNumber)
            self.__startAnimatorEffect(component)
            self.__updateComponentCounter(component, counterValueStr)

    @staticmethod
    def __updateComponentCounter(component, counterValue):
        if component.decalComponent is None or component.decalComponent() is None:
            return
        else:
            mainKillDigits = False
            for i in xrange(0, len(counterValue)):
                mainKillDigits = mainKillDigits or int(counterValue[i]) > 0
                if mainKillDigits:
                    value = counterValue[i]
                else:
                    value = StatTrackComponentManager._DARK_ZERO
                component.decalComponent().setCounterStickerValue(i, value)

            return

    @staticmethod
    def __startAnimatorEffect(component):
        if component.animatorComponent is None or component.animatorComponent() is None:
            return
        else:
            component.animatorComponent().stop()
            component.animatorComponent().start()
            return
