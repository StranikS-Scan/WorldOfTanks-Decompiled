# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/battle_hints_blocks.py
import typing
from visual_script.slot_types import SLOT_TYPE
from visual_script.misc import ASPECT, errorVScript
from visual_script.block import Block
from visual_script.dependency import dependencyImporter
from visual_script.battle_hints_common import BaseSelectHint, BaseHintAction, HintActionParamsMixin, HintsMeta
from hints.battle import manager as battleHintsModelsMgr
from skeletons.gui.battle_session import IBattleSessionProvider
dependency = dependencyImporter('helpers.dependency')
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.battle_hints.controller import BattleHintsController
    from hints.battle.schemas.base import CHMType
    from hints_common.battle.manager import CommonBattleHintsModelsManager

class SelectHint(BaseSelectHint):

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    @classmethod
    def _getModelsManager(cls, initialize=False):
        if initialize:
            battleHintsModelsMgr.init()
        return battleHintsModelsMgr.get()


class CanShowHint(Block, HintsMeta):

    def __init__(self, *args, **kwargs):
        super(CanShowHint, self).__init__(*args, **kwargs)
        self._hintId = self._makeDataInputSlot('hintId', SLOT_TYPE.STR)
        self._result = self._makeDataOutputSlot('result', SLOT_TYPE.BOOL, self._execute)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    def _execute(self):
        modelsMgr = battleHintsModelsMgr.get()
        if not modelsMgr:
            self._result.setValue(False)
            return
        hintId = self._hintId.getValue()
        model = modelsMgr.get(hintId)
        if not model:
            self._result.setValue(False)
            errorVScript(self, 'Hint [{}] does not exist.'.format(hintId))
            return
        self._result.setValue(model.canBeShown())


class ReceiverMixin(object):

    def _getReceivers(self):
        provider = dependency.instance(IBattleSessionProvider)
        controller = provider.dynamic.battleHints
        if not controller:
            errorVScript(self, 'Can not access the BattleHintsController.')
            return []
        return [controller]

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class ShowHint(ReceiverMixin, HintActionParamsMixin, BaseHintAction):
    RESERVED = HintActionParamsMixin.RESERVED + ('immediately',)

    def __init__(self, *args, **kwargs):
        super(ShowHint, self).__init__(*args, **kwargs)
        self._immediately = self._makeDataInputSlot('immediately', SLOT_TYPE.BOOL)
        self._immediately.setDefaultValue(False)

    def _doAction(self, controller, hintId):
        controller.showHint(hintId, self._getParams(), self._immediately.getValue())


class HideHint(ReceiverMixin, BaseHintAction):

    def _doAction(self, controller, hintId):
        controller.hideHint(hintId)


class RemoveHint(ReceiverMixin, BaseHintAction):

    def __init__(self, *args, **kwargs):
        super(RemoveHint, self).__init__(*args, **kwargs)
        self._hide = self._makeDataInputSlot('hide', SLOT_TYPE.BOOL)
        self._hide.setDefaultValue(False)

    def _doAction(self, controller, hintId):
        controller.removeHint(hintId, self._hide.getValue())
