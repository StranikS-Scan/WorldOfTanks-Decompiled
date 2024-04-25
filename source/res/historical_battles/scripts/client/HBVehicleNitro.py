# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBVehicleNitro.py
import BigWorld
from items import vehicles
from Event import EventsSubscriber

class Exhaust(object):

    def __init__(self, entity, exhaustType):
        self._owner = entity
        self._exhaustType = exhaustType
        self._appearance = self._owner.appearance

    def apply(self):
        self._setType(self._exhaustType)

    def unapply(self):
        self._setType(0)

    def destroy(self):
        self._owner = None
        self._appearance = None
        return

    def _setType(self, exhaustType):
        if self._appearance is not None:
            effectMgr = self._appearance.customEffectManager
            if effectMgr is not None:
                effectMgr.variables['Nitro'] = exhaustType
        return


class HBVehicleNitro(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(HBVehicleNitro, self).__init__()
        self.__exhaust = None
        self._es = EventsSubscriber()
        self._es.subscribeToEvent(BigWorld.player().onVehicleEnterWorld, self.__onVehicleEnterWorld)
        self._activate()
        return

    def set_eqId(self, prev):
        if self.eqId > 0:
            self._activate()

    def onDestroy(self):
        if self._es is not None:
            self._es.unsubscribeFromAllEvents()
            self._es = None
        self.__stop()
        self.__destroy()
        return

    def onLeaveWorld(self):
        self.onDestroy()

    def _activate(self):
        if self.eqId <= 0:
            return
        if not self.entity.isStarted:
            return
        self.__initExhaustData()
        self.__startExhausts()

    def _getEffectData(self):
        equipment = vehicles.g_cache.equipments()[self.eqId]
        return equipment.effects

    def __onVehicleEnterWorld(self, v):
        self._activate()

    def __stop(self):
        if self.__exhaust is not None:
            self.__exhaust.unapply()
        return

    def __destroy(self):
        if self.__exhaust is not None:
            self.__exhaust.destroy()
        self.__exhaust = None
        return

    def __startExhausts(self):
        if self.__exhaust is not None:
            self.__exhaust.apply()
        return

    def __initExhaustData(self):
        if self.__exhaust is None:
            equipment = vehicles.g_cache.equipments()[self.eqId]
            exhaust = equipment.effects.get('exhaust')
            if exhaust:
                self.__exhaust = Exhaust(self.entity, exhaust)
        return
