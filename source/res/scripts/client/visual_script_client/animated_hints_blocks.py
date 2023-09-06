# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/animated_hints_blocks.py
import BigWorld
import aih_constants
from animated_hints.constants import HintType
from visual_script.block import Block, Meta
from visual_script.slot_types import SLOT_TYPE
from visual_script.misc import ASPECT, EDITOR_TYPE, errorVScript
from constants import IS_VS_EDITOR
if not IS_VS_EDITOR:
    from animated_hints.manager import HintManager

class AnimatedHintMeta(Meta):

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
        return [ASPECT.CLIENT]


class InitAnimatedHint(Block, AnimatedHintMeta):

    def __init__(self, *args, **kwargs):
        super(InitAnimatedHint, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._onInit)
        self._typeId = self._makeDataInputSlot('typeId', SLOT_TYPE.STR, EDITOR_TYPE.ENUM_SELECTOR)
        self._typeId.setEditorData([ t.name for t in HintType ])
        self._text = self._makeDataInputSlot('text', SLOT_TYPE.STR)
        self._text.setDefaultValue('')
        self._voiceover = self._makeDataInputSlot('voiceover', SLOT_TYPE.STR)
        self._timeCooldownAfter = self._makeDataInputSlot('cooldownAfter', SLOT_TYPE.FLOAT)
        self._timeCompleteDuration = self._makeDataInputSlot('completeDuration', SLOT_TYPE.FLOAT)
        self._out = self._makeEventOutputSlot('out')
        self._id = self._makeDataOutputSlot('id', SLOT_TYPE.ID, None)
        return

    def _onInit(self):
        avatar = BigWorld.player()
        hintTypeId = HintType[self._typeId.getValue()]
        timeCompleted = self._timeCompleteDuration.getValue() if self._timeCompleteDuration.hasValue() else 1.0
        cooldownAfter = self._timeCooldownAfter.getValue() if self._timeCooldownAfter.hasValue() else 0.0
        message = self._text.getValue()
        voiceover = self._voiceover.getValue() if self._voiceover.hasValue() else None
        hintParam = (avatar,
         hintTypeId,
         timeCompleted,
         cooldownAfter,
         message,
         voiceover)
        hint = HintManager.instance().addHint(hintParam)
        hint.start()
        self._id.setValue(hint.id)
        self._out.call()
        return

    def validate(self):
        return 'TypeId is required' if not self._typeId.hasValue() else super(InitAnimatedHint, self).validate()


class ProcessAnimatedHint(Block, AnimatedHintMeta):

    def __init__(self, *args, **kwargs):
        super(ProcessAnimatedHint, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self.__execute)
        self._id = self._makeDataInputSlot('id', SLOT_TYPE.ID)
        self._out = self._makeEventOutputSlot('out')

    def validate(self):
        return 'id value is required' if not self._id.hasValue() else super(ProcessAnimatedHint, self).validate()

    def _processHint(self, hint):
        pass

    def __execute(self):
        if not IS_VS_EDITOR:
            hintId = self._id.getValue()
            hint = HintManager.instance().getHint(hintId)
            if hint is not None:
                self._processHint(hint)
            else:
                errorVScript(self, 'Unknown hint id')
        self._out.call()
        return


class ShowAnimatedHint(ProcessAnimatedHint):

    def _processHint(self, hint):
        if not hint.isActive():
            hint.show()


class HideAnimatedHint(ProcessAnimatedHint):

    def _processHint(self, hint):
        if hint.isActive():
            hint.hide()


class CompleteAnimatedHint(ProcessAnimatedHint):

    def _processHint(self, hint):
        if not hint.isComplete():
            hint.complete()


class IsAnimatedHintVisible(Block, AnimatedHintMeta):

    def __init__(self, *args, **kwargs):
        super(IsAnimatedHintVisible, self).__init__(*args, **kwargs)
        self._id = self._makeDataInputSlot('id', SLOT_TYPE.ID)
        self._visible = self._makeDataOutputSlot('visible', SLOT_TYPE.BOOL, self._isVisible)

    def _isVisible(self):
        hintId = self._id.getValue()
        hint = HintManager.instance().getHint(hintId)
        if hint is not None:
            visible = hint.isActive()
            self._visible.setValue(visible)
        else:
            errorVScript(self, 'Unknown hint id')
        return


class HideAllAnimatedHints(Block, AnimatedHintMeta):

    def __init__(self, *args, **kwargs):
        super(HideAllAnimatedHints, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self.__onHide)
        self._out = self._makeEventOutputSlot('out')

    def __onHide(self):
        for hint in HintManager.instance().getHints().itervalues():
            if hint.isActive():
                hint.hide()

        self._out.call()


class SetAnimatedHintPenetrationString(Block, AnimatedHintMeta):
    _SHOT_RESULT_TO_PIERCING_CHANCE_HINT = {aih_constants.SHOT_RESULT.UNDEFINED: '',
     aih_constants.SHOT_RESULT.NOT_PIERCED: 'low',
     aih_constants.SHOT_RESULT.LITTLE_PIERCED: 'medium',
     aih_constants.SHOT_RESULT.GREAT_PIERCED: 'high'}

    def __init__(self, *args, **kwargs):
        super(SetAnimatedHintPenetrationString, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._penetration = self._makeDataInputSlot('crosshairPenetration', SLOT_TYPE.INT)
        self._penetration.setEditorData([aih_constants.SHOT_RESULT.UNDEFINED, aih_constants.SHOT_RESULT.GREAT_PIERCED])
        self._isColorBlind = self._makeDataInputSlot('isColorBlind', SLOT_TYPE.BOOL)
        self._isColorBlind.setDefaultValue(False)
        self._out = self._makeEventOutputSlot('out')

    def validate(self):
        return 'crosshairPenetration value is required' if not self._penetration.hasValue() else super(SetAnimatedHintPenetrationString, self).validate()

    def _execute(self):
        penetrationType = self._SHOT_RESULT_TO_PIERCING_CHANCE_HINT.get(self._penetration.getValue())
        if penetrationType is not None:
            HintManager.instance().setPenetration(penetrationType, self._isColorBlind.getValue())
        else:
            errorVScript(self, 'Unexpected crosshairPenetration given')
        self._out.call()
        return


def regBlocks(blockRegistrar):
    blockRegistrar.regBlock(InitAnimatedHint)
    blockRegistrar.regBlock(ShowAnimatedHint)
    blockRegistrar.regBlock(HideAnimatedHint)
    blockRegistrar.regBlock(CompleteAnimatedHint)
    blockRegistrar.regBlock(IsAnimatedHintVisible)
    blockRegistrar.regBlock(HideAllAnimatedHints)
    blockRegistrar.regBlock(SetAnimatedHintPenetrationString)
