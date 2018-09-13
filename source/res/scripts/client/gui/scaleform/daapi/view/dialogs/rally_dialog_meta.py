# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/rally_dialog_meta.py
from constants import PREBATTLE_TYPE, PREBATTLE_TYPE_NAMES
from debug_utils import LOG_ERROR, LOG_WARNING
from gui.Scaleform.daapi.view.dialogs import I18nDialogMeta, I18nInfoDialogMeta, I18nConfirmDialogMeta
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.shared.events import ShowDialogEvent
from gui.Scaleform.framework.ScopeTemplates import VIEW_SCOPE, SimpleScope
_VIEW_SCOPES = {PREBATTLE_TYPE.UNIT: SimpleScope(CYBER_SPORT_ALIASES.UNIT_VIEW_PY, VIEW_SCOPE),
 PREBATTLE_TYPE.SORTIE: SimpleScope(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_VIEW_PY, VIEW_SCOPE)}
_EVENT_TYPES = {PREBATTLE_TYPE.UNIT: ShowDialogEvent.SHOW_CYBER_SPORT_DIALOG,
 PREBATTLE_TYPE.SORTIE: ShowDialogEvent.SHOW_CYBER_SPORT_DIALOG}

def _makeI18nKey(prbType, prefix):
    if prbType in PREBATTLE_TYPE_NAMES:
        prbName = PREBATTLE_TYPE_NAMES[prbType]
    else:
        LOG_ERROR('Prebattle type is not valid', prbType)
        prbName = PREBATTLE_TYPE_NAMES[PREBATTLE_TYPE.UNIT]
    return '{0}/{1}'.format(prbName, prefix)


class RallyInfoDialogMeta(I18nInfoDialogMeta):

    def __init__(self, prbType, prefix):
        super(RallyInfoDialogMeta, self).__init__(_makeI18nKey(prbType, prefix))


class RallyConfirmDialogMeta(I18nConfirmDialogMeta):

    def __init__(self, prbType, prefix, titleCtx = None, messageCtx = None, focusedID = None):
        super(RallyConfirmDialogMeta, self).__init__(_makeI18nKey(prbType, prefix), titleCtx=titleCtx, messageCtx=messageCtx, focusedID=focusedID)


class _RallyScopeDialogMeta(I18nDialogMeta):

    def __init__(self, prbType, meta):
        super(_RallyScopeDialogMeta, self).__init__('', None, meta=meta)
        self.__prbType = prbType
        return

    def getEventType(self):
        if self.__prbType in _EVENT_TYPES:
            eventType = _EVENT_TYPES[self.__prbType]
        else:
            LOG_WARNING('Event type is not defined', self.__prbType)
            eventType = super(_RallyScopeDialogMeta, self).getEventType()
        return eventType

    def getViewScopeType(self):
        if self.__prbType in _VIEW_SCOPES:
            scopeType = _VIEW_SCOPES[self.__prbType]
        else:
            LOG_WARNING('View scope is not defined', self.__prbType)
            scopeType = super(_RallyScopeDialogMeta, self).getViewScopeType()
        return scopeType


class RallyScopeInfoDialogMeta(_RallyScopeDialogMeta):

    def __init__(self, prbType, prefix):
        super(RallyScopeInfoDialogMeta, self).__init__(prbType, RallyInfoDialogMeta(prbType, prefix))


class RallyScopeConfirmDialogMeta(_RallyScopeDialogMeta):

    def __init__(self, prbType, prefix):
        super(RallyScopeConfirmDialogMeta, self).__init__(prbType, RallyConfirmDialogMeta(prbType, prefix))
