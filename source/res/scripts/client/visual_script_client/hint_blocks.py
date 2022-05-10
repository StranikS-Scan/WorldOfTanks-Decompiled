# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/hint_blocks.py
import BigWorld
import aih_constants
from bootcamp.BootcampConstants import HINT_NAMES, HINT_TYPE
from visual_script.block import Block, Meta, EDITOR_TYPE
from visual_script.slot_types import SLOT_TYPE
from visual_script.misc import ASPECT, errorVScript
from constants import IS_VS_EDITOR
from hint_common import ProcessHint
if not IS_VS_EDITOR:
    from HintManager import HintManager
    from frameworks.wulf import WindowLayer
    from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
    from gui.Scaleform.framework.entities.View import ViewKey

class HintMeta(Meta):

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
        return [ASPECT.CLIENT, ASPECT.HANGAR]


class InitHint(Block, HintMeta):

    def __init__(self, *args, **kwargs):
        super(InitHint, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._onInit)
        self._typeValues = {name:value for value, name in enumerate(HINT_NAMES)}
        self._typeId = self._makeDataInputSlot('typeId', SLOT_TYPE.STR, EDITOR_TYPE.ENUM_SELECTOR)
        self._typeId.setEditorData([ name for name in HINT_NAMES if self._typeValues[name] not in HINT_TYPE.SECONDARY_HINTS ])
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
        hintTypeId = self.__getHintTypeId()
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
        hint = HintManager.hintManager().addHint(hintParam)
        hint.start()
        self._id.setValue(hint.id)
        self._out.call()
        return

    def __getHintTypeId(self):
        return self._typeValues[self._typeId.getValue()]

    def validate(self):
        return 'TypeId is required' if not self._typeId.hasValue() else super(InitHint, self).validate()


class InitSecondaryHint(Block, HintMeta):

    def __init__(self, *args, **kwargs):
        super(InitSecondaryHint, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._onInit)
        self._text = self._makeDataInputSlot('text', SLOT_TYPE.STR)
        self._text.setDefaultValue('')
        self._out = self._makeEventOutputSlot('out')
        self._id = self._makeDataOutputSlot('id', SLOT_TYPE.ID, None)
        return

    def _onInit(self):
        avatar = BigWorld.player()
        message = self._text.getValue()
        hintParam = (avatar,
         HINT_TYPE.HINT_WAIT_RELOAD,
         0.0,
         0.0,
         message,
         None)
        hint = HintManager.hintManager().addHint(hintParam, secondary=True)
        hint.start()
        self._id.setValue(hint.id)
        self._out.call()
        return

    def validate(self):
        return super(InitSecondaryHint, self).validate()


class ShowHint(ProcessHint, HintMeta):

    def _processHint(self, hint):
        if not hint.isActive():
            hint.show()


class HideHint(ProcessHint, HintMeta):

    def _processHint(self, hint):
        if hint.isActive():
            hint.hide()


class CompleteHint(ProcessHint, HintMeta):

    def _processHint(self, hint):
        if not hint.isComplete():
            hint.complete()


class IsHintVisible(Block, HintMeta):

    def __init__(self, *args, **kwargs):
        super(IsHintVisible, self).__init__(*args, **kwargs)
        self._id = self._makeDataInputSlot('id', SLOT_TYPE.ID)
        self._visible = self._makeDataOutputSlot('visible', SLOT_TYPE.BOOL, self._isVisible)

    def _isVisible(self):
        hintId = self._id.getValue()
        hint = HintManager.hintManager().getHint(hintId)
        if hint is not None:
            visible = hint.isActive()
            self._visible.setValue(visible)
        else:
            errorVScript(self, 'Unknown hint id')
        return


class HideAllHints(Block, HintMeta):

    def __init__(self, *args, **kwargs):
        super(HideAllHints, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self.__onHide)
        self._out = self._makeEventOutputSlot('out')

    def __onHide(self):
        for hint in HintManager.hintManager().getHints().itervalues():
            if hint.isActive():
                hint.hide()

        self._out.call()


class SetBootCampHintPenetrationString(Block, HintMeta):
    _SHOT_RESULT_TO_PIERCING_CHANCE_HINT = {aih_constants.SHOT_RESULT.UNDEFINED: '',
     aih_constants.SHOT_RESULT.NOT_PIERCED: 'low',
     aih_constants.SHOT_RESULT.LITTLE_PIERCED: '',
     aih_constants.SHOT_RESULT.GREAT_PIERCED: 'high'}

    def __init__(self, *args, **kwargs):
        super(SetBootCampHintPenetrationString, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._penetration = self._makeDataInputSlot('crosshairPenetration', SLOT_TYPE.INT)
        self._isColorBlind = self._makeDataInputSlot('isColorBlind', SLOT_TYPE.BOOL)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        topHint = self._getBattleTopHint()
        if topHint is not None:
            penetration = self._penetration.getValue()
            value = self._SHOT_RESULT_TO_PIERCING_CHANCE_HINT[penetration]
            topHint.as_setPenetrationS(value, self._isColorBlind.getValue())
        else:
            errorVScript(self, "Can't get the Boot Camp hint")
        self._out.call()
        return

    @staticmethod
    def _getBattleTopHint():
        avatar = BigWorld.player()
        if avatar is not None:
            app = avatar.appLoader.getApp()
            bcPageContainer = app.containerManager.getContainer(WindowLayer.VIEW)
            bcPage = bcPageContainer.findView(ViewKey(VIEW_ALIAS.BOOTCAMP_BATTLE_PAGE))
            return bcPage.topHint
        else:
            return
