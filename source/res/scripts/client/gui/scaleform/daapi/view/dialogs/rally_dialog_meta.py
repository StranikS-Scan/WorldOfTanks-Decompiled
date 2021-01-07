# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/rally_dialog_meta.py
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.dialogs import I18nDialogMeta, I18nInfoDialogMeta, I18nConfirmDialogMeta, I18nConfirmDialogButtons, I18nInfoDialogButtons, DIALOG_BUTTON_ID
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.prb_control.formatters.messages import makeEntityI18nKey
from gui.prb_control.settings import FUNCTIONAL_FLAG, CTRL_ENTITY_TYPE
from gui.shared.events import ShowDialogEvent
from gui.Scaleform.framework.ScopeTemplates import VIEW_SCOPE, WINDOW_SCOPE, SimpleScope
_P_TYPE = PREBATTLE_TYPE
_Q_TYPE = QUEUE_TYPE
_C_TYPE = CTRL_ENTITY_TYPE
_VIEW_SCOPES = {(_C_TYPE.UNIT, _P_TYPE.UNIT): SimpleScope(CYBER_SPORT_ALIASES.UNIT_VIEW_PY, VIEW_SCOPE),
 (_C_TYPE.LEGACY, _P_TYPE.CLAN): SimpleScope(PREBATTLE_ALIASES.BATTLE_SESSION_ROOM_WINDOW_PY, WINDOW_SCOPE),
 (_C_TYPE.LEGACY, _P_TYPE.TOURNAMENT): SimpleScope(PREBATTLE_ALIASES.BATTLE_SESSION_ROOM_WINDOW_PY, WINDOW_SCOPE),
 (_C_TYPE.LEGACY, _P_TYPE.TRAINING): SimpleScope(PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY, VIEW_SCOPE),
 (_C_TYPE.LEGACY, _P_TYPE.EPIC): SimpleScope(PREBATTLE_ALIASES.EPIC_TRAINING_ROOM_VIEW_PY, VIEW_SCOPE)}

class _RallyInfoDialogMeta(I18nInfoDialogMeta):

    def __init__(self, ctrlType, entityType, prefix):
        super(_RallyInfoDialogMeta, self).__init__(makeEntityI18nKey(ctrlType, entityType, prefix))


class _RallyConfirmDialogMeta(I18nConfirmDialogMeta):

    def __init__(self, ctrlType, entityType, prefix, titleCtx=None, messageCtx=None, focusedID=None):
        super(_RallyConfirmDialogMeta, self).__init__(makeEntityI18nKey(ctrlType, entityType, prefix), titleCtx=titleCtx, messageCtx=messageCtx, focusedID=focusedID)


class UnitConfirmDialogMeta(I18nConfirmDialogMeta):

    def __init__(self, prbType, prefix, titleCtx=None, messageCtx=None, focusedID=None):
        super(UnitConfirmDialogMeta, self).__init__(makeEntityI18nKey(_C_TYPE.UNIT, prbType, prefix), titleCtx=titleCtx, messageCtx=messageCtx, focusedID=focusedID)


class StrongholdConfirmDialogMeta(I18nDialogMeta):

    def __init__(self, key, subKey='', titleCtx=None, messageCtx=None, focusedID=None):
        _key = 'stronghold/{0}{1}'
        buttons = I18nConfirmDialogButtons(_key.format(key, ''), focusedID)
        super(StrongholdConfirmDialogMeta, self).__init__(_key.format(key, subKey), buttons, titleCtx, messageCtx, scope=VIEW_SCOPE)


class _RallyScopeDialogMeta(I18nDialogMeta):

    def __init__(self, ctrlType, entityType, meta):
        super(_RallyScopeDialogMeta, self).__init__('', None, meta=meta)
        self.__key = (ctrlType, entityType)
        return

    def getEventType(self):
        return ShowDialogEvent.SHOW_CYBER_SPORT_DIALOG

    def getViewScopeType(self):
        if self.__key in _VIEW_SCOPES:
            scopeType = _VIEW_SCOPES[self.__key]
        else:
            LOG_DEBUG('View scope is not defined', self.__key)
            scopeType = super(_RallyScopeDialogMeta, self).getViewScopeType()
        return scopeType


class RallyScopeInfoDialogMeta(_RallyScopeDialogMeta):

    def __init__(self, ctrlType, entityType, prefix):
        super(RallyScopeInfoDialogMeta, self).__init__(ctrlType, entityType, _RallyInfoDialogMeta(ctrlType, entityType, prefix))


class RallyLeaveDisabledDialogMeta(RallyScopeInfoDialogMeta):

    def __init__(self, ctrlType, entityType):
        super(RallyLeaveDisabledDialogMeta, self).__init__(ctrlType, entityType, 'leaveDisabled')


class RallyScopeConfirmDialogMeta(_RallyScopeDialogMeta):

    def __init__(self, ctrlType, entityType, prefix):
        super(RallyScopeConfirmDialogMeta, self).__init__(ctrlType, entityType, _RallyConfirmDialogMeta(ctrlType, entityType, prefix))


_ENTITY_TO_ANOTHER_PREFIX = {(_C_TYPE.PREQUEUE, _Q_TYPE.RANDOMS): ('', 'goToAnother'),
 (_C_TYPE.PREQUEUE, _Q_TYPE.UNKNOWN): ('', 'goToAnother'),
 (_C_TYPE.PREQUEUE, _Q_TYPE.SANDBOX): ('', 'goToAnother'),
 (_C_TYPE.PREQUEUE, _Q_TYPE.TUTORIAL): ('', 'goToBattleTutorial'),
 (_C_TYPE.LEGACY, _P_TYPE.TRAINING): ('goToIntro', 'goToAnother'),
 (_C_TYPE.LEGACY, _P_TYPE.CLAN): ('', 'goToAnother'),
 (_C_TYPE.LEGACY, _P_TYPE.TOURNAMENT): ('', 'goToAnother'),
 (_C_TYPE.UNIT, _P_TYPE.UNIT): ('goToIntro', 'goToAnother'),
 (_C_TYPE.UNIT, _P_TYPE.SQUAD): ('goToSquad', 'goToAnother'),
 (_C_TYPE.UNIT, _P_TYPE.EVENT): ('goToSquad', 'goToAnother'),
 (_C_TYPE.PREQUEUE, _Q_TYPE.EPIC): ('', 'goToAnother')}
_DEFAULT_CONFIRM = 'leave'

def _createLeaveRallyMeta(unlockCtx, leftCtrlType, leftEntityType, isSwitching=False):
    key = (unlockCtx.getCtrlType(), unlockCtx.getEntityType())
    if key in _ENTITY_TO_ANOTHER_PREFIX and (unlockCtx.hasFlags(FUNCTIONAL_FLAG.SWITCH) or isSwitching):
        switch, another = _ENTITY_TO_ANOTHER_PREFIX[key]
        if switch and isSwitching:
            prefix = switch
        else:
            prefix = another
    else:
        prefix = _DEFAULT_CONFIRM
    return RallyScopeConfirmDialogMeta(leftCtrlType, leftEntityType, prefix)


_INTRO_TO_ANOTHER_PREFIX = {(_C_TYPE.UNIT, _P_TYPE.SQUAD): 'goToSquad',
 (_C_TYPE.UNIT, _P_TYPE.EVENT): 'goToSquad'}

def _createLeaveIntroMeta(unlockCtx, leftCtrlType, leftEntityType, isSwitching=False):
    key = (unlockCtx.getCtrlType(), unlockCtx.getEntityType())
    return RallyScopeConfirmDialogMeta(leftCtrlType, leftEntityType, _INTRO_TO_ANOTHER_PREFIX[key]) if key in _INTRO_TO_ANOTHER_PREFIX else None


def createPrbIntroLeaveMeta(unlockCtx, leftPrbType, isSwitching=False):
    return _createLeaveIntroMeta(unlockCtx, _C_TYPE.LEGACY, leftPrbType, isSwitching)


def createPrbLeaveMeta(unlockCtx, leftPrbType, isSwitching=False):
    return _createLeaveRallyMeta(unlockCtx, _C_TYPE.LEGACY, leftPrbType, isSwitching)


def createUnitIntroLeaveMeta(unlockCtx, leftPrbType, isSwitching=False):
    return _createLeaveIntroMeta(unlockCtx, _C_TYPE.UNIT, leftPrbType, isSwitching)


def createUnitLeaveMeta(unlockCtx, leftPrbType, isSwitching=False):
    return _createLeaveRallyMeta(unlockCtx, _C_TYPE.UNIT, leftPrbType, isSwitching)


def createLeavePreQueueMeta(unlockCtx, leftQueueType, isSwitching=False):
    return _createLeaveRallyMeta(unlockCtx, _C_TYPE.PREQUEUE, leftQueueType, isSwitching)


def createLeaveInfoMeta(unlockCtx, prefix):
    key = makeEntityI18nKey(unlockCtx.getCtrlType(), unlockCtx.getEntityType(), prefix)
    return I18nDialogMeta(key, buttons=I18nInfoDialogButtons(key, buttonID=DIALOG_BUTTON_ID.SUBMIT))
