# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/rally_dialog_meta.py
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from debug_utils import LOG_WARNING
from gui.Scaleform.daapi.view.dialogs import I18nDialogMeta, I18nInfoDialogMeta, I18nConfirmDialogMeta
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.prb_control.settings import FUNCTIONAL_EXIT, CTRL_ENTITY_TYPE
from gui.shared.events import ShowDialogEvent
from gui.Scaleform.framework.ScopeTemplates import VIEW_SCOPE, WINDOW_SCOPE, SimpleScope
_P_TYPE = PREBATTLE_TYPE
_Q_TYPE = QUEUE_TYPE
_C_TYPE = CTRL_ENTITY_TYPE
_VIEW_SCOPES = {(_C_TYPE.PREBATTLE, _P_TYPE.SQUAD): SimpleScope(PREBATTLE_ALIASES.SQUAD_VIEW_PY, VIEW_SCOPE),
 (_C_TYPE.PREBATTLE, _P_TYPE.COMPANY): SimpleScope(PREBATTLE_ALIASES.COMPANY_ROOM_VIEW_PY, VIEW_SCOPE),
 (_C_TYPE.UNIT, _P_TYPE.UNIT): SimpleScope(CYBER_SPORT_ALIASES.UNIT_VIEW_PY, VIEW_SCOPE),
 (_C_TYPE.UNIT, _P_TYPE.SORTIE): SimpleScope(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_VIEW_PY, VIEW_SCOPE),
 (_C_TYPE.UNIT, _P_TYPE.FORT_BATTLE): SimpleScope(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_VIEW_PY, VIEW_SCOPE),
 (_C_TYPE.PREBATTLE, _P_TYPE.CLAN): SimpleScope(PREBATTLE_ALIASES.BATTLE_SESSION_ROOM_WINDOW_PY, WINDOW_SCOPE),
 (_C_TYPE.PREBATTLE, _P_TYPE.TOURNAMENT): SimpleScope(PREBATTLE_ALIASES.BATTLE_SESSION_ROOM_WINDOW_PY, WINDOW_SCOPE),
 (_C_TYPE.PREBATTLE, _P_TYPE.TRAINING): SimpleScope(PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY, VIEW_SCOPE),
 (_C_TYPE.PREQUEUE, _Q_TYPE.HISTORICAL): SimpleScope(PREBATTLE_ALIASES.HISTORICAL_BATTLES_LIST_WINDOW_PY, WINDOW_SCOPE)}

def makeI18nKey(ctrlType, entityType, prefix):
    if ctrlType in [_C_TYPE.PREBATTLE, _C_TYPE.UNIT]:
        if entityType == _P_TYPE.SQUAD:
            name = 'squad'
        else:
            name = 'rally'
    else:
        name = 'rally'
    return '{0}/{1}'.format(name, prefix)


class _RallyInfoDialogMeta(I18nInfoDialogMeta):

    def __init__(self, ctrlType, entityType, prefix):
        super(_RallyInfoDialogMeta, self).__init__(makeI18nKey(ctrlType, entityType, prefix))


class _RallyConfirmDialogMeta(I18nConfirmDialogMeta):

    def __init__(self, ctrlType, entityType, prefix, titleCtx = None, messageCtx = None, focusedID = None):
        super(_RallyConfirmDialogMeta, self).__init__(makeI18nKey(ctrlType, entityType, prefix), titleCtx=titleCtx, messageCtx=messageCtx, focusedID=focusedID)


class UnitConfirmDialogMeta(I18nConfirmDialogMeta):

    def __init__(self, prbType, prefix, titleCtx = None, messageCtx = None, focusedID = None):
        super(UnitConfirmDialogMeta, self).__init__(makeI18nKey(_C_TYPE.UNIT, prbType, prefix), titleCtx=titleCtx, messageCtx=messageCtx, focusedID=focusedID)


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
            LOG_WARNING('View scope is not defined', self.__key)
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


_EXIT_TO_PREFIX = {FUNCTIONAL_EXIT.SWITCH: 'goToAnother',
 FUNCTIONAL_EXIT.RANDOM: 'goToAnother',
 FUNCTIONAL_EXIT.SQUAD: 'goToSquad',
 FUNCTIONAL_EXIT.BATTLE_TUTORIAL: 'goToBattleTutorial',
 FUNCTIONAL_EXIT.INTRO_PREBATTLE: 'goToIntro',
 FUNCTIONAL_EXIT.INTRO_UNIT: 'goToIntro'}
_DEFAULT_PREFIX = 'leave'

def _createLeaveRallyMeta(funcExit, ctrlType, entityType):
    if funcExit in _EXIT_TO_PREFIX:
        prefix = _EXIT_TO_PREFIX[funcExit]
    else:
        prefix = _DEFAULT_PREFIX
    return RallyScopeConfirmDialogMeta(ctrlType, entityType, prefix)


def _createLeaveIntroMeta(funcExit, ctrlType, entityType):
    if funcExit == FUNCTIONAL_EXIT.SQUAD:
        meta = RallyScopeConfirmDialogMeta(ctrlType, entityType, _EXIT_TO_PREFIX[funcExit])
    else:
        meta = None
    return meta


def createPrbIntroLeaveMeta(funcExit, prbType):
    return _createLeaveIntroMeta(funcExit, _C_TYPE.PREBATTLE, prbType)


def createPrbLeaveMeta(funcExit, prbType):
    return _createLeaveRallyMeta(funcExit, _C_TYPE.PREBATTLE, prbType)


def createUnitIntroLeaveMeta(funcExit, prbType):
    return _createLeaveIntroMeta(funcExit, _C_TYPE.UNIT, prbType)


def createUnitLeaveMeta(funcExit, prbType):
    return _createLeaveRallyMeta(funcExit, _C_TYPE.UNIT, prbType)


def createLeavePreQueueMeta(funcExit, queueType):
    return _createLeaveRallyMeta(funcExit, _C_TYPE.UNIT, queueType)
