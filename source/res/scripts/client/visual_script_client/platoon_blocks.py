# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/platoon_blocks.py
from skeletons.gui.game_control import IPlatoonController
from visual_script.block import Meta, Block
from visual_script.dependency import dependencyImporter
from visual_script.misc import ASPECT
from visual_script.slot_types import SLOT_TYPE
dependency, shared, events = dependencyImporter('helpers.dependency', 'gui.shared', 'gui.shared.events')

class PlatoonMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.HANGAR]


class OnPlatoonStateChanged(Block, PlatoonMeta):
    _PLAYER_INDEX = -1
    _platoonController = dependency.descriptor(IPlatoonController)

    def __init__(self, *args, **kwargs):
        super(OnPlatoonStateChanged, self).__init__(*args, **kwargs)
        self._subscribe = self._makeEventInputSlot('subscribe', self.__subscribe)
        self._unsubscribe = self._makeEventInputSlot('unsubscribe', self.__unsubscribe)
        self._subscribeOut = self._makeEventOutputSlot('subscribeOut')
        self._unsubscribeOut = self._makeEventOutputSlot('unsubscribeOut')
        self._onPlatoonEnter = self._makeEventOutputSlot('onPlatoonEnter')
        self._onPlatoonExit = self._makeEventOutputSlot('onPlatoonExit')
        self._onPlayerEnter = self._makeEventOutputSlot('onPlayerEnter')
        self._onPlayerExit = self._makeEventOutputSlot('onPlayerExit')
        self._index = self._makeDataOutputSlot('index', SLOT_TYPE.INT, None)
        return

    def __subscribe(self):
        shared.g_eventBus.addListener(events.HangarVehicleEvent.ON_PLATOON_TANK_LOADED, self.__onPlatoonTankEnter, scope=shared.EVENT_BUS_SCOPE.LOBBY)
        shared.g_eventBus.addListener(events.HangarVehicleEvent.ON_PLATOON_TANK_DESTROY, self.__onPlatoonTankLeave, scope=shared.EVENT_BUS_SCOPE.LOBBY)
        self._platoonController.onPlatoonTankVisualizationChanged += self.__enablePlatoonLighting
        self._subscribeOut.call()

    def __unsubscribe(self):
        shared.g_eventBus.removeListener(events.HangarVehicleEvent.ON_PLATOON_TANK_LOADED, self.__onPlatoonTankEnter, scope=shared.EVENT_BUS_SCOPE.LOBBY)
        shared.g_eventBus.removeListener(events.HangarVehicleEvent.ON_PLATOON_TANK_DESTROY, self.__onPlatoonTankLeave, scope=shared.EVENT_BUS_SCOPE.LOBBY)
        self._platoonController.onPlatoonTankVisualizationChanged -= self.__enablePlatoonLighting
        self._unsubscribeOut.call()

    def __onPlatoonTankEnter(self, event):
        entity = event.ctx['entity']
        self._index.setValue(entity.slotIndex)
        self._onPlatoonEnter.call()

    def __onPlatoonTankLeave(self, event):
        entity = event.ctx['entity']
        self._index.setValue(entity.slotIndex)
        self._onPlatoonExit.call()

    def __enablePlatoonLighting(self, isEnabled):
        self._index.setValue(self._PLAYER_INDEX)
        if isEnabled:
            self._onPlayerEnter.call()
        else:
            self._onPlayerExit.call()
