# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/pet_system_blocks.py
import typing
import skeletons.gui.pet_system
from pet_system_common.pet_constants import AnimationStateName, PetHangarObject, PetStateBehavior, PetStaticTrigger, PetTrigger, StorageStaticTrigger
from visual_script.misc import EDITOR_TYPE
from visual_script.type import VScriptEnum
from visual_script.slot_types import SLOT_TYPE
from visual_script import ASPECT
from visual_script.block import Block, Meta
from visual_script.dependency import dependencyImporter
Event, dependency, game_control, event_dispatcher, lobby_entry, ps_states, state_machine, GenericComponents, guiShared = dependencyImporter('Event', 'helpers.dependency', 'skeletons.gui.game_control', 'gui.shared.event_dispatcher', 'gui.Scaleform.lobby_entry', 'gui.impl.lobby.pet_system.states', 'frameworks.state_machine', 'GenericComponents', 'gui.shared')

class PetSystemMeta(Meta):

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


class OnEventShow(Block, PetSystemMeta):
    __petController = dependency.descriptor(skeletons.gui.pet_system.IPetSystemController)

    def __init__(self, agent):
        super(OnEventShow, self).__init__(agent)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._fullscreenNeeded = self._makeDataInputSlot('fullscreenNeeded', SLOT_TYPE.BOOL)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        if self.__petController.getActiveEvent():
            self.__petController.showEventView(self._fullscreenNeeded.getValue())
            self._out.call()


class OnFirstClickSend(Block, PetSystemMeta):
    __petController = dependency.descriptor(skeletons.gui.pet_system.IPetSystemController)

    def __init__(self, agent):
        super(OnFirstClickSend, self).__init__(agent)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        self.__petController.sendFirstClick()
        self._out.call()


class OnPetStorageOpen(Block, PetSystemMeta):
    __petController = dependency.descriptor(skeletons.gui.pet_system.IPetSystemController)

    def __init__(self, agent):
        super(OnPetStorageOpen, self).__init__(agent)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        if self.__petController.getStateBehavior() == PetStateBehavior.HIDDEN and self.__petController.getActiveEvent():
            self.__petController.showEventView()
        else:
            event_dispatcher.showPetStorageView()
        self._out.call()


class IsInPetStorageView(Block, PetSystemMeta):
    __petController = dependency.descriptor(skeletons.gui.pet_system.IPetSystemController)

    def __init__(self, agent):
        super(IsInPetStorageView, self).__init__(agent)
        self._state = self._makeDataOutputSlot('inState', SLOT_TYPE.BOOL, self._execute)

    def _execute(self):
        self._state.setValue(self.__petController.isInStorage)


class IsInPetFullscreenEventView(Block, PetSystemMeta):
    __petController = dependency.descriptor(skeletons.gui.pet_system.IPetSystemController)

    def __init__(self, agent):
        super(IsInPetFullscreenEventView, self).__init__(agent)
        self._state = self._makeDataOutputSlot('inState', SLOT_TYPE.BOOL, self._execute)

    def _execute(self):
        self._state.setValue(self.__petController.isInEventFulscreen)


class PetTriggerEnum(VScriptEnum):

    @classmethod
    def vs_name(cls):
        pass

    @classmethod
    def vs_enum(cls):
        return PetTrigger

    @classmethod
    def nameToIndex(cls, value):
        return cls.vs_enum().ALL.index(value)

    @classmethod
    def _vs_collectEnumEntries(cls):
        entriesData = {}
        for index, name in enumerate(cls.vs_enum().ALL):
            entriesData[name] = index

        return entriesData


class StorageStaticTriggerEnum(VScriptEnum):

    @classmethod
    def vs_name(cls):
        pass

    @classmethod
    def vs_enum(cls):
        return StorageStaticTrigger


class PetStaticTriggerEnum(VScriptEnum):

    @classmethod
    def vs_name(cls):
        pass

    @classmethod
    def vs_enum(cls):
        return PetStaticTrigger


class AnimationStateNameEnum(VScriptEnum):

    @classmethod
    def vs_name(cls):
        pass

    @classmethod
    def vs_enum(cls):
        return AnimationStateName

    @classmethod
    def nameToIndex(cls, value):
        return cls.vs_enum().ALL.index(value)

    @classmethod
    def _vs_collectEnumEntries(cls):
        entriesData = {}
        for index, name in enumerate(cls.vs_enum().ALL):
            entriesData[name] = index

        return entriesData


class GetPetState(Block, PetSystemMeta):
    __petController = dependency.descriptor(skeletons.gui.pet_system.IPetSystemController)

    def __init__(self, agent):
        super(GetPetState, self).__init__(agent)
        self._state = self._makeDataOutputSlot('state', AnimationStateNameEnum.slotType(), self._execute)

    def _execute(self):
        self._state.setValue(AnimationStateNameEnum.nameToIndex(self.__petController.petProxy.petPrefabState))


class OnStateChanged(Block, PetSystemMeta):
    __petController = dependency.descriptor(skeletons.gui.pet_system.IPetSystemController)

    def __init__(self, agent):
        super(OnStateChanged, self).__init__(agent)
        self._out = self._makeEventOutputSlot('out')
        self._state = self._makeDataOutputSlot('state', AnimationStateNameEnum.slotType(), None)
        return

    def onStartScript(self):
        self.__petController.petProxy.onUpdatePetPrefabState += self._onUpdatePetState

    def onFinishScript(self):
        self.__petController.petProxy.onUpdatePetPrefabState -= self._onUpdatePetState

    def _onUpdatePetState(self, state):
        self._state.setValue(AnimationStateNameEnum.nameToIndex(state))
        self._out.call()


class OnPetAnimationTriggered(Block, PetSystemMeta):
    __petController = dependency.descriptor(skeletons.gui.pet_system.IPetSystemController)

    def __init__(self, agent):
        super(OnPetAnimationTriggered, self).__init__(agent)
        self._out = self._makeEventOutputSlot('out')
        self._trigger = self._makeDataOutputSlot('trigger', PetTriggerEnum.slotType(), None)
        return

    def onStartScript(self):
        self.__petController.petProxy.onTrigger += self._onTrigger

    def onFinishScript(self):
        self.__petController.petProxy.onTrigger -= self._onTrigger

    def _onTrigger(self, trigger):
        self._trigger.setValue(PetTriggerEnum.nameToIndex(trigger))
        self._out.call()


class GetStorageStaticTrigger(Block, PetSystemMeta):
    __petController = dependency.descriptor(skeletons.gui.pet_system.IPetSystemController)

    def __init__(self, agent):
        super(GetStorageStaticTrigger, self).__init__(agent)
        self._staticTrigger = self._makeDataOutputSlot('staticTrigger', StorageStaticTriggerEnum.slotType(), self._execute)

    def _execute(self):
        self._staticTrigger.setValue(self.__petController.storageProxy.storageStaticTrigger)


class OnStorageStaticTriggerChanged(Block, PetSystemMeta):
    __petController = dependency.descriptor(skeletons.gui.pet_system.IPetSystemController)

    def __init__(self, agent):
        super(OnStorageStaticTriggerChanged, self).__init__(agent)
        self._out = self._makeEventOutputSlot('out')
        self._staticTrigger = self._makeDataOutputSlot('staticTrigger', StorageStaticTriggerEnum.slotType(), None)
        return

    def onStartScript(self):
        self.__petController.storageProxy.onUpdateStorageStaticTrigger += self._onUpdateStorageStaticTrigger

    def onFinishScript(self):
        self.__petController.storageProxy.onUpdateStorageStaticTrigger -= self._onUpdateStorageStaticTrigger

    def _onUpdateStorageStaticTrigger(self, staticTrigger):
        self._staticTrigger.setValue(staticTrigger)
        self._out.call()


class GetPetStaticTrigger(Block, PetSystemMeta):
    __petController = dependency.descriptor(skeletons.gui.pet_system.IPetSystemController)

    def __init__(self, agent):
        super(GetPetStaticTrigger, self).__init__(agent)
        self._staticTrigger = self._makeDataOutputSlot('staticTrigger', PetStaticTriggerEnum.slotType(), self._execute)

    def _execute(self):
        self._staticTrigger.setValue(self.__petController.petProxy.petStaticTrigger)


class OnPetStaticTriggerChanged(Block, PetSystemMeta):
    __petController = dependency.descriptor(skeletons.gui.pet_system.IPetSystemController)

    def __init__(self, agent):
        super(OnPetStaticTriggerChanged, self).__init__(agent)
        self._out = self._makeEventOutputSlot('out')
        self._staticTrigger = self._makeDataOutputSlot('staticTrigger', PetStaticTriggerEnum.slotType(), None)
        return

    def onStartScript(self):
        self.__petController.petProxy.onUpdatePetStaticTrigger += self._onUpdatePetStaticTrigger

    def onFinishScript(self):
        self.__petController.petProxy.onUpdatePetStaticTrigger -= self._onUpdatePetStaticTrigger

    def _onUpdatePetStaticTrigger(self, staticTrigger):
        self._staticTrigger.setValue(staticTrigger)
        self._out.call()


class GetSynergy(Block, PetSystemMeta):
    __petController = dependency.descriptor(skeletons.gui.pet_system.IPetSystemController)

    def __init__(self, agent):
        super(GetSynergy, self).__init__(agent)
        self._synergy = self._makeDataOutputSlot('synergy', SLOT_TYPE.INT, self._execute)

    def _execute(self):
        self._synergy.setValue(self.__petController.petProxy.petSynergyLevel)


class GetIsFirstClickAvailable(Block, PetSystemMeta):
    __petController = dependency.descriptor(skeletons.gui.pet_system.IPetSystemController)

    def __init__(self, agent):
        super(GetIsFirstClickAvailable, self).__init__(agent)
        self._isAvailable = self._makeDataOutputSlot('isAvailable', SLOT_TYPE.BOOL, self._execute)

    def _execute(self):
        self._isAvailable.setValue(self.__petController.isFirstClickEnable())


class OnSynergyChanged(Block, PetSystemMeta):
    __petController = dependency.descriptor(skeletons.gui.pet_system.IPetSystemController)

    def __init__(self, agent):
        super(OnSynergyChanged, self).__init__(agent)
        self._out = self._makeEventOutputSlot('out')
        self._synergy = self._makeDataOutputSlot('synergy', SLOT_TYPE.INT, None)
        return

    def onStartScript(self):
        self.__petController.petProxy.onUpdatePetSynergy += self._onUpdatePetSynergy

    def onFinishScript(self):
        self.__petController.petProxy.onUpdatePetSynergy -= self._onUpdatePetSynergy

    def _onUpdatePetSynergy(self, synergy):
        self._synergy.setValue(synergy)
        self._out.call()


class OnPetObjectHover(Block, PetSystemMeta):

    def __init__(self, agent):
        super(OnPetObjectHover, self).__init__(agent)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')
        self._isHoverIn = self._makeDataInputSlot('isHoverIn', SLOT_TYPE.BOOL)
        self._objectName = self._makeDataInputSlot('objectName', SLOT_TYPE.STR, EDITOR_TYPE.ENUM_SELECTOR)
        self._objectName.setEditorData(list(PetHangarObject.ALL))

    def _execute(self):
        if self._isHoverIn.getValue():
            eventType = guiShared.events.PetObjectHoverEvent.HOVER_IN
        else:
            eventType = guiShared.events.PetObjectHoverEvent.HOVER_OUT
        guiShared.g_eventBus.handleEvent(guiShared.events.PetObjectHoverEvent(eventType=eventType, ctx={'objectName': self._objectName.getValue()}), scope=guiShared.EVENT_BUS_SCOPE.DEFAULT)
        self._out.call()


class OnPetCanInteractInHangarStateChanged(Block, PetSystemMeta):
    __petController = dependency.descriptor(skeletons.gui.pet_system.IPetSystemController)

    def __init__(self, agent):
        super(OnPetCanInteractInHangarStateChanged, self).__init__(agent)
        self._out = self._makeEventOutputSlot('out')
        self._canInteract = self._makeDataOutputSlot('canInteract', SLOT_TYPE.BOOL, None)
        return

    def onStartScript(self):
        self.__petController.onUpdateCanInteractInHangar += self._onUpdateCanInteractInHangar
        self._execute()

    def onFinishScript(self):
        self.__petController.onUpdateCanInteractInHangar -= self._onUpdateCanInteractInHangar

    def _execute(self):
        self._canInteract.setValue(self.__petController.canInteractInHangar)
        self._out.call()

    def _onUpdateCanInteractInHangar(self, canInteract):
        self._canInteract.setValue(canInteract)
        self._out.call()
