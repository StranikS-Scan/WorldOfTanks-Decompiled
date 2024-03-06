# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/battle_hints_common.py
import typing
from abc import ABCMeta
from visual_script.block import Block, Meta, InitParam
from visual_script.misc import errorVScript, ASPECT, EDITOR_TYPE
from visual_script.slot_types import SLOT_TYPE
from hints_common.battle.schemas.const import BLOCK_ALL_HINTS_SCOPE_FILTER
if typing.TYPE_CHECKING:
    from hints_common.battle.manager import CommonBattleHintsModelsManager

def _getHintsChoices(modelsMgr):
    if not modelsMgr:
        return []
    choices, allHintIds = {}, set()
    for hint in modelsMgr.getAll():
        choices.setdefault(hint.props.scope, []).append(hint.uniqueName)
        allHintIds.add(hint.uniqueName)

    allHintsScope = [(BLOCK_ALL_HINTS_SCOPE_FILTER, sorted(allHintIds))]
    return allHintsScope + [ (scope, sorted(choices[scope])) for scope in sorted(choices) ]


class HintsMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass


class BaseSelectHint(Block, HintsMeta):

    def __init__(self, *args, **kwargs):
        super(BaseSelectHint, self).__init__(*args, **kwargs)
        selected = self._getInitParams()
        _, self._hintId = selected.split('.', 1)
        if not self._hintId:
            errorVScript(self, 'No hints to select.')
            return
        else:
            self._id = self._makeDataOutputSlot('id', SLOT_TYPE.STR, None)
            self._id.setValue(self._hintId)
            return

    def validate(self):
        modelsMgr = self._getModelsManager(initialize=False)
        if not modelsMgr:
            return 'No hints models manager initialized.'
        return 'Hint [{}] does not exist.'.format(self._hintId) if not modelsMgr.get(self._hintId) else super(BaseSelectHint, self).validate()

    @classmethod
    def initParams(cls):
        return [InitParam(name='scope, hintId', slotType=SLOT_TYPE.STR, defaultValue='', editorType=EDITOR_TYPE.COMPLEX_KEY_SELECTOR, editorData=_getHintsChoices(cls._getModelsManager(initialize=True)))]

    def captionText(self):
        return 'Hint: {}'.format(self._hintId)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER]

    @classmethod
    def _getModelsManager(cls, initialize=False):
        raise NotImplementedError


class BaseHintAction(Block, HintsMeta):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        super(BaseHintAction, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._hintId = self._makeDataInputSlot('hintId', SLOT_TYPE.STR)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        hintId = self._hintId.getValue()
        for receiver in self._getReceivers():
            self._doAction(receiver, hintId)

        self._out.call()

    def _getReceivers(self):
        raise NotImplementedError

    def _doAction(self, receiver, hintId):
        raise NotImplementedError


class HintActionParamsMixin(object):
    RESERVED = ('hintId',)

    def __init__(self, *args, **kwargs):
        super(HintActionParamsMixin, self).__init__(*args, **kwargs)
        paramsString = self._getInitParams()[-1:]
        params = self._prepareParams(paramsString)
        self._params = [ (name, self._makeDataInputSlot(name, SLOT_TYPE.STR)) for name in params ]

    @classmethod
    def initParams(cls):
        param = InitParam('Parameters names separated by " ". Example: magic test', SLOT_TYPE.STR, '')
        return super(HintActionParamsMixin, cls).initParams() + [param]

    def _prepareParams(self, paramsString):
        params = []
        for name in paramsString.split():
            if name in params:
                errorVScript(self, 'Name <{}> already in use.'.format(name))
                continue
            elif name in self.RESERVED:
                errorVScript(self, 'Name <{}> reserved and can be used in params.'.format(name))
                continue
            params.append(name)

        return params

    def _getParams(self):
        return {name:slot.getValue() for name, slot in self._params}
