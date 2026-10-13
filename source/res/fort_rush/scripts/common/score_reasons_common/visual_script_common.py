# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/common/score_reasons_common/visual_script_common.py
from __future__ import absolute_import
import typing
from visual_script.block import Block, Meta, InitParam
from visual_script.misc import errorVScript, ASPECT, EDITOR_TYPE
from visual_script.slot_types import SLOT_TYPE
if typing.TYPE_CHECKING:
    from score_reasons_common.manager import ScoreReasonsModelsManager
_BLOCK_ALL_SCOPE_FILTER = '[all]'

def _getScoreReasonsChoices(modelsMgr):
    if not modelsMgr:
        return []
    choices = {scopeKey:[ name.split('.')[-1] for name in sorted(uniqueNames) ] for scopeKey, uniqueNames in modelsMgr.reasonsByScope.items()}
    allScope = [(_BLOCK_ALL_SCOPE_FILTER, sorted(modelsMgr.getAllUniqueNames()))]
    return allScope + [ (scope, choices[scope]) for scope in sorted(choices) ]


class ScoreReasonsMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass


class BaseSelectScoreReason(Block, ScoreReasonsMeta):

    def __init__(self, *args, **kwargs):
        super(BaseSelectScoreReason, self).__init__(*args, **kwargs)
        selected = self._getInitParams()
        if selected.startswith(_BLOCK_ALL_SCOPE_FILTER + '.'):
            self._uniqueReason = selected[len(_BLOCK_ALL_SCOPE_FILTER) + 1:]
        else:
            self._uniqueReason = selected
        if not self._uniqueReason:
            errorVScript(self, 'No score reasons to select.')
            return
        else:
            self._name = self._makeDataOutputSlot('uniqueName', SLOT_TYPE.STR, None)
            self._name.setValue(self._uniqueReason)
            return

    def validate(self):
        modelsManager = self._getModelsManager(initialize=False)
        if not modelsManager:
            return 'No score reasons models manager initialized.'
        return 'Score reason [{}] does not exist.'.format(self._uniqueReason) if not modelsManager.getScoreReasonModel(self._uniqueReason) else super(BaseSelectScoreReason, self).validate()

    @classmethod
    def initParams(cls):
        return [InitParam(name='scope, reasonName', slotType=SLOT_TYPE.STR, defaultValue='', editorType=EDITOR_TYPE.COMPLEX_KEY_SELECTOR, editorData=_getScoreReasonsChoices(cls._getModelsManager(initialize=True)))]

    def captionText(self):
        return 'Score reason: {}'.format(self._uniqueReason)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER]

    @classmethod
    def _getModelsManager(cls, initialize=False):
        raise NotImplementedError
