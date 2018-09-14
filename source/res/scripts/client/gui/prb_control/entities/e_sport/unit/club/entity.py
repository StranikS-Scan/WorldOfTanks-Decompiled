# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/e_sport/unit/club/entity.py
from adisp import process
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.clubs.club_helpers import ClubListener
from gui.clubs.contexts import JoinUnitCtx
from gui.prb_control import settings, prb_getters
from gui.prb_control.entities.e_sport.unit.public.actions_validator import ESportActionsValidator
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.e_sport.unit.club.actions_validator import ClubsActionsValidator
from gui.prb_control.entities.e_sport.unit.entity import ESportBrowserEntity, ESportEntity, ESportBrowserEntryPoint, ESportEntryPoint
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
_PAN = settings.PREBATTLE_ACTION_NAME
_RT = settings.REQUEST_TYPE

class ClubBrowserEntryPoint(ESportBrowserEntryPoint):
    """
    Clubs list entry point
    """

    def __init__(self):
        super(ClubBrowserEntryPoint, self).__init__(PREBATTLE_TYPE.CLUBS)


class ClubEntryPoint(ESportEntryPoint, ClubListener):
    """
    Clubs entry point
    """

    def create(self, ctx, callback=None):
        self.__createOrJoin(ctx, callback)

    def join(self, ctx, callback=None):
        self.__createOrJoin(ctx, callback)

    @process
    def __createOrJoin(self, ctx, callback=None):
        """
        Request to create or join club battle.
        Args:
            ctx: join club request context
            callback: operation callback
        """
        yield lambda callback: callback(None)
        if not prb_getters.hasModalEntity() or ctx.isForced():
            yield self.clubsCtrl.sendRequest(JoinUnitCtx(ctx.getClubDbID(), ctx.getJoiningTime()), allowDelay=ctx.isAllowDelay())
        else:
            LOG_ERROR('First, player has to confirm exit from the current prebattle/unit')
            if callback is not None:
                callback(False)
        return


class ClubBrowserEntity(ESportBrowserEntity):
    """
    Clubs list entity
    """

    def __init__(self):
        super(ClubBrowserEntity, self).__init__(PREBATTLE_TYPE.CLUBS)
        self.__paginator = None
        return

    def init(self, ctx=None):
        from gui.clubs.club_helpers import ClubPaginatorComposite
        self.__paginator = ClubPaginatorComposite()
        self.__paginator.init()
        return super(ClubBrowserEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        if self.__paginator is not None:
            self.__paginator.fini()
            self.__paginator = None
        return super(ClubBrowserEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def getBrowser(self):
        return self.__paginator

    def doSelectAction(self, action):
        actionName = action.actionName
        if actionName == PREBATTLE_ACTION_NAME.E_SPORT:
            g_eventDispatcher.showUnitWindow(self._prbType)
            return SelectResult(True)
        return super(ClubBrowserEntity, self).doSelectAction(action)


class ClubEntity(ESportEntity):
    """
    Club battle entity
    """

    def __init__(self):
        super(ClubEntity, self).__init__(PREBATTLE_TYPE.CLUBS)

    def getQueueType(self):
        return QUEUE_TYPE.CLUBS

    def doSelectAction(self, action):
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.E_SPORT:
            g_eventDispatcher.showUnitWindow(self._prbType)
            return SelectResult(True)
        return super(ClubEntity, self).doSelectAction(action)

    def isRated(self):
        extra = self.getExtra()
        if extra is None or not hasattr(extra, 'isRatedBattle'):
            LOG_DEBUG('Unit has no extra data or extra does not contain isRanked', extra)
            return
        else:
            return extra.isRatedBattle

    def changeRated(self, ctx, callback=None):
        """
        Request to change rated state for club
        Args:
            ctx: change rated club request context
            callback: operation callback
        """
        isRated = self.isRated()
        if isRated is None:
            if callback:
                callback(False)
            return
        elif isRated is ctx.isRated():
            LOG_DEBUG('Unit already is rated/not rated', ctx)
            if callback:
                callback(True)
            return
        elif self._isInCoolDown(_RT.CHANGE_RATED, coolDown=ctx.getCooldown()):
            return
        else:
            pPermissions = self.getPermissions()
            if not pPermissions.canChangeRated():
                LOG_ERROR('Player can not change rated', pPermissions)
                if callback:
                    callback(False)
                return
            self._requestsProcessor.doRequest(ctx, 'setRatedBattle', isRatedBattle=ctx.isRated())
            self._cooldown.process(_RT.CHANGE_RATED, coolDown=ctx.getCooldown())
            return

    def _createActionsValidator(self):
        return ClubsActionsValidator(self) if self.isRated() else ESportActionsValidator(self)

    def _getRequestHandlers(self):
        handlers = super(ClubEntity, self)._getRequestHandlers()
        handlers.update({_RT.CHANGE_RATED: self.changeRated})
        return handlers

    def unit_onUnitExtraChanged(self, extras):
        self._switchActionsValidator()
        super(ClubEntity, self).unit_onUnitExtraChanged(extras)
