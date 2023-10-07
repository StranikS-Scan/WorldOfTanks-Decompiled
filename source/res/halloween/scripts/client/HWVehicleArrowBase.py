# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWVehicleArrowBase.py
import BigWorld
from Event import EventsSubscriber
from items import vehicles
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from halloween.gui.shared import events as hw_events
from HWVehicleEffect import SequenceEffect

class HWVehicleArrowBase(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(HWVehicleArrowBase, self).__init__()
        self.__boostEffect = None
        self.__boostContext = {}
        self.__boostIsWorking = False
        self._es = EventsSubscriber()
        self._es.subscribeToEvent(self.entity.onAppearanceReady, self._onAppearanceReady)
        self.set_isBoosted(self.isBoosted)
        return

    def onDestroy(self):
        self._es.unsubscribeFromAllEvents()
        if self.__boostIsWorking:
            self.__stopSequences()
            self.__boostIsWorking = False
        self.__boostEffect = None
        return

    def onLeaveWorld(self):
        self.onDestroy()

    def _onAppearanceReady(self):
        self.set_isBoosted(1)

    def set_isBoosted(self, prev):
        if self.equipmentID <= 0:
            return
        if not self.__boostContext:
            self._init()
        event = hw_events.BuffGUIEvent.ON_APPLY if self.isBoosted else hw_events.BuffGUIEvent.ON_UNAPPLY
        g_eventBus.handleEvent(hw_events.BuffGUIEvent(event, ctx=self.__boostContext), scope=EVENT_BUS_SCOPE.BATTLE)
        if self.isBoosted and not self.__boostIsWorking:
            self.__playBoostSequences()
            self.__boostIsWorking = True

    def set_equipmentID(self, prev):
        if self.equipmentID > 0:
            self._init()

    def _init(self):
        equipment = vehicles.g_cache.equipments()[self.equipmentID]
        tooltip = {'params': {},
         'tag': equipment.name}
        self.__boostContext = {'id': equipment.name,
         'iconName': equipment.name,
         'tooltip': tooltip,
         'vehicleID': self.entity.id}
        self.__boostEffect = self.__getBoostSequenceEffect()

    def __getBoostSequenceEffect(self):
        equipment = vehicles.g_cache.equipments()[self.equipmentID]
        effects = equipment.boostParams.get('effects')
        if effects and 'sequences' in effects:
            sequence = effects.get('sequences').get('owner')
            if sequence:
                return [ SequenceEffect(self.entity, data) for data in sequence ]
        return None

    def __playBoostSequences(self):
        if self.__boostEffect:
            for sequence in self.__boostEffect:
                sequence.apply(BigWorld.serverTime())

    def __stopSequences(self):
        if self.__boostEffect:
            for sequence in self.__boostEffect:
                sequence.unapply()
                sequence.destroy()
