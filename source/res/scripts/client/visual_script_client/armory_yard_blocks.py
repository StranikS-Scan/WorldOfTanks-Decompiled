# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/armory_yard_blocks.py
from visual_script.block import Block, Meta
from visual_script.slot_types import SLOT_TYPE
from visual_script.misc import ASPECT
from visual_script.dependency import dependencyImporter
dependency, sound_constants, aySkeleton, settings, guiShared = dependencyImporter('helpers.dependency', 'armory_yard.gui.Scaleform.daapi.view.lobby.hangar.sound_constants', 'armory_yard.gui.game_control.armory_yard_controller', 'Settings', 'gui.shared')

class AYMeta(Meta):

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


class GetStageSoundEventName(Block, AYMeta):

    def __init__(self, *args, **kwargs):
        super(GetStageSoundEventName, self).__init__(*args, **kwargs)
        self._stageIndex = self._makeDataInputSlot('stageIndex', SLOT_TYPE.INT)
        self._soundEventName = self._makeDataOutputSlot('soundEventName', SLOT_TYPE.STR, self._execute)

    def _execute(self):
        stageIndex = self._stageIndex.getValue()
        eventName = sound_constants.getStageVoTapeRecorderName(stageIndex)
        self._soundEventName.setValue(eventName)


class IsStageSoundValid(Block, AYMeta):

    def __init__(self, *args, **kwargs):
        super(IsStageSoundValid, self).__init__(*args, **kwargs)
        self._stageIndex = self._makeDataInputSlot('stageIndex', SLOT_TYPE.INT)
        self._isSoundValid = self._makeDataOutputSlot('isSoundValid', SLOT_TYPE.BOOL, self._execute)

    def _execute(self):
        from gui.impl.gen import R
        stageIndex = self._stageIndex.getValue()
        eventName = sound_constants.getStageVoTapeRecorderName(stageIndex)
        if R.sounds.dyn(eventName).isValid():
            self._isSoundValid.setValue(True)
            return
        self._isSoundValid.setValue(False)


class GetNextValidSoundStageIndex(Block, AYMeta):
    __ayController = dependency.descriptor(aySkeleton.IArmoryYardController)

    def __init__(self, *args, **kwargs):
        super(GetNextValidSoundStageIndex, self).__init__(*args, **kwargs)
        self._inStageIndex = self._makeDataInputSlot('inStageIndex', SLOT_TYPE.INT)
        self._outStageIndex = self._makeDataOutputSlot('outStageIndex', SLOT_TYPE.INT, self._execute)

    def _execute(self):
        from gui.impl.gen import R
        stageIndex = self._inStageIndex.getValue()
        progress = self.__ayController.getCurrentProgress()
        totalStages = self.__ayController.getTotalSteps()
        if progress > totalStages:
            progress = totalStages
        for index in range(stageIndex, progress + 1):
            eventName = sound_constants.getStageVoTapeRecorderName(index)
            if R.sounds.dyn(eventName).isValid():
                self._outStageIndex.setValue(index)
                return

        if stageIndex == 0:
            self._outStageIndex.setValue(0)
        else:
            self._outStageIndex.setValue(1)


class GetLastValidSound(Block, AYMeta):
    __ayController = dependency.descriptor(aySkeleton.IArmoryYardController)

    def __init__(self, *args, **kwargs):
        super(GetLastValidSound, self).__init__(*args, **kwargs)
        self._inStageIndex = self._makeDataInputSlot('inStageIndex', SLOT_TYPE.INT)
        self._outStageIndex = self._makeDataOutputSlot('outStageIndex', SLOT_TYPE.INT, self._execute)

    def _execute(self):
        from gui.impl.gen import R
        progress = self.__ayController.getCurrentProgress()
        totalStages = self.__ayController.getTotalSteps()
        if progress > totalStages:
            progress = totalStages
        for index in range(progress, 0, -1):
            eventName = sound_constants.getStageVoTapeRecorderName(index)
            if R.sounds.dyn(eventName).isValid():
                self._outStageIndex.setValue(index)
                return

        self._outStageIndex.setValue(0)


class NeedToUpdateRecorderLamp(Block, AYMeta):
    __ayController = dependency.descriptor(aySkeleton.IArmoryYardController)

    def __init__(self, *args, **kwargs):
        super(NeedToUpdateRecorderLamp, self).__init__(*args, **kwargs)
        self._inlastListenedMessage = self._makeDataInputSlot('lastListenedMessage', SLOT_TYPE.INT)
        self._needToUpdate = self._makeDataOutputSlot('needToUpdate', SLOT_TYPE.BOOL, self._execute)

    def _execute(self):
        from gui.impl.gen import R
        lastListenedMessage = self._inlastListenedMessage.getValue()
        progress = self.__ayController.getCurrentProgress()
        totalStages = self.__ayController.getTotalSteps()
        if progress > totalStages:
            progress = totalStages
        for index in range(progress, lastListenedMessage, -1):
            eventName = sound_constants.getStageVoTapeRecorderName(index)
            if R.sounds.dyn(eventName).isValid():
                self._needToUpdate.setValue(True)
                return

        self._needToUpdate.setValue(False)


class GetTotalCountOfStages(Block, AYMeta):
    __ayController = dependency.descriptor(aySkeleton.IArmoryYardController)

    def __init__(self, *args, **kwargs):
        super(GetTotalCountOfStages, self).__init__(*args, **kwargs)
        self._totalCount = self._makeDataOutputSlot('totalCount', SLOT_TYPE.INT, self._execute)

    def _execute(self):
        totalCount = self.__ayController.getTotalSteps()
        self._totalCount.setValue(totalCount)


class GetCurrentProgress(Block, AYMeta):
    __ayController = dependency.descriptor(aySkeleton.IArmoryYardController)

    def __init__(self, *args, **kwargs):
        super(GetCurrentProgress, self).__init__(*args, **kwargs)
        self._progress = self._makeDataOutputSlot('progress', SLOT_TYPE.INT, self._execute)

    def _execute(self):
        progress = self.__ayController.getCurrentProgress()
        totalStages = self.__ayController.getTotalSteps()
        if progress > totalStages:
            progress = totalStages
        self._progress.setValue(progress)


AY_SECTION_TEMPLATE = 'armory_yard'
AY_SECTION_LAST_LISTENED_MESSAGE = 'lastListenedMessage'

class GetLastListenedMessage(Block, AYMeta):
    __ayController = dependency.descriptor(aySkeleton.IArmoryYardController)

    def __init__(self, *args, **kwargs):
        super(GetLastListenedMessage, self).__init__(*args, **kwargs)
        self._index = self._makeDataOutputSlot('index', SLOT_TYPE.INT, self._execute)

    def _execute(self):
        currentSeason = self.__ayController.serverSettings.getCurrentSeason()
        if currentSeason is None:
            return
        else:
            sectionName = AY_SECTION_TEMPLATE + '_' + str(currentSeason.getSeasonID())
            section = settings.g_instance.userPrefs
            if not section.has_key(sectionName):
                self._index.setValue(0)
                return
            subsec = section[sectionName]
            value = subsec.readInt(AY_SECTION_LAST_LISTENED_MESSAGE, 0)
            self._index.setValue(value)
            return


class SaveLastListenedMessage(Block, AYMeta):
    __ayController = dependency.descriptor(aySkeleton.IArmoryYardController)

    def __init__(self, *args, **kwargs):
        super(SaveLastListenedMessage, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._index = self._makeDataInputSlot('index', SLOT_TYPE.INT)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        currentSeason = self.__ayController.serverSettings.getCurrentSeason()
        if currentSeason is None:
            return
        else:
            sectionName = AY_SECTION_TEMPLATE + '_' + str(currentSeason.getSeasonID())
            section = settings.g_instance.userPrefs
            section.deleteSection(sectionName)
            subsec = section.createSection(sectionName)
            subsec.writeInt(AY_SECTION_LAST_LISTENED_MESSAGE, self._index.getValue())
            settings.g_instance.save()
            self._out.call()
            return


class OnStageMuteSound(Block, AYMeta):
    __ayController = dependency.descriptor(aySkeleton.IArmoryYardController)

    def __init__(self, *args, **kwargs):
        super(OnStageMuteSound, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('out')

    def onStartScript(self):
        guiShared.g_eventBus.addListener(guiShared.events.ArmoryYardEvent.STAGE_MUTE_SOUND, self._execute, guiShared.EVENT_BUS_SCOPE.DEFAULT)

    def onFinishScript(self):
        guiShared.g_eventBus.removeListener(guiShared.events.ArmoryYardEvent.STAGE_MUTE_SOUND, self._execute, guiShared.EVENT_BUS_SCOPE.DEFAULT)

    def _execute(self, event):
        self._out.call()


class OnStageUnmuteSound(Block, AYMeta):
    __ayController = dependency.descriptor(aySkeleton.IArmoryYardController)

    def __init__(self, *args, **kwargs):
        super(OnStageUnmuteSound, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('out')

    def onStartScript(self):
        guiShared.g_eventBus.addListener(guiShared.events.ArmoryYardEvent.STAGE_UNMUTE_SOUND, self._execute, guiShared.EVENT_BUS_SCOPE.DEFAULT)

    def onFinishScript(self):
        guiShared.g_eventBus.removeListener(guiShared.events.ArmoryYardEvent.STAGE_UNMUTE_SOUND, self._execute, guiShared.EVENT_BUS_SCOPE.DEFAULT)

    def _execute(self, event):
        self._out.call()


class OnStageFinish(Block, AYMeta):
    __ayController = dependency.descriptor(aySkeleton.IArmoryYardController)

    def __init__(self, *args, **kwargs):
        super(OnStageFinish, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('out')
        self._index = self._makeDataOutputSlot('index', SLOT_TYPE.INT, None)
        return

    def onStartScript(self):
        guiShared.g_eventBus.addListener(guiShared.events.ArmoryYardEvent.STAGE_FINISHED, self._execute, guiShared.EVENT_BUS_SCOPE.DEFAULT)

    def onFinishScript(self):
        guiShared.g_eventBus.removeListener(guiShared.events.ArmoryYardEvent.STAGE_FINISHED, self._execute, guiShared.EVENT_BUS_SCOPE.DEFAULT)

    def _execute(self, event):
        index = event.ctx['index']
        totalStages = self.__ayController.getTotalSteps()
        if index > totalStages:
            index = totalStages
        self._index.setValue(index)
        self._out.call()


class ActivatePOI(Block, AYMeta):

    def __init__(self, *args, **kwargs):
        super(ActivatePOI, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._name = self._makeDataInputSlot('name', SLOT_TYPE.STR)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        ctx = {}
        ctx['name'] = self._name.getValue()
        guiShared.g_eventBus.handleEvent(guiShared.events.ArmoryYardEvent(guiShared.events.ArmoryYardEvent.POI_ACTIVATED, ctx=ctx))
        self._out.call()
