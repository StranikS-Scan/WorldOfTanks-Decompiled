# Embedded file name: scripts/client/gui/prb_control/context/__init__.py
from constants import QUEUE_TYPE
from debug_utils import LOG_ERROR
from external_strings_utils import truncate_utf8
from gui.Scaleform.Waiting import Waiting
from gui.prb_control import isInRandomQueue, isInTutorialQueue, getPrebattleID
from gui.prb_control import isInHistoricalQueue, isInEventBattlesQueue
from gui.prb_control.settings import INVITE_COMMENT_MAX_LENGTH, REQUEST_TYPE
from gui.shared.utils.requesters.rqs_by_id import RequestCtx

class StartDispatcherCtx(object):
    __slots__ = ['isInRandomQueue',
     'isInTutorialQueue',
     'isInHistoricalQueue',
     'isInEventBattles',
     'prebattleID',
     'preQueueStates']

    def __init__(self, **kwargs):
        super(StartDispatcherCtx, self).__init__()
        self.isInRandomQueue = kwargs.get('isInRandomQueue', False)
        self.isInTutorialQueue = kwargs.get('isInTutorialQueue', False)
        self.isInHistoricalQueue = kwargs.get('isInHistoricalQueue', False)
        self.isInEventBattles = kwargs.get('isInEventBattles', False)
        self.prebattleID = kwargs.get('prebattleID', 0L)
        self.preQueueStates = kwargs.get('preQueueStates')

    def __repr__(self):
        return 'StartDispatcherCtx(inRandomQueue = {0!r:s}, inTutorialQueue = {1!r:s}, isInHistoricalQueue = {2!r:s}, prebattleID = {3:n}, preQueueStates = {4!r:s})'.format(self.isInRandomQueue, self.isInTutorialQueue, self.isInHistoricalQueue, self.prebattleID, self.preQueueStates)

    def getQueueType(self):
        if self.isInRandomQueue:
            return QUEUE_TYPE.RANDOMS
        elif self.isInHistoricalQueue:
            return QUEUE_TYPE.HISTORICAL
        elif self.isInEventBattles:
            return QUEUE_TYPE.EVENT_BATTLES
        else:
            return None

    @classmethod
    def fetch(cls, **kwargs):
        ctxArgs = {'isInRandomQueue': isInRandomQueue(),
         'isInTutorialQueue': isInTutorialQueue(),
         'isInHistoricalQueue': isInHistoricalQueue(),
         'isInEventBattles': isInEventBattlesQueue(),
         'prebattleID': getPrebattleID()}
        ctxArgs.update(**kwargs)
        return StartDispatcherCtx(**ctxArgs)


class PrbCtrlRequestCtx(RequestCtx):

    def getEntityType(self):
        return 0


class PrebattleAction(object):
    __slots__ = ('actionName', 'mapID')

    def __init__(self, actionName, mapID = 0):
        self.actionName = actionName if actionName is not None else ''
        self.mapID = mapID
        return

    def __repr__(self):
        return 'PrebattleAction(name = {0:>s}, mapID = {1:n}'.format(self.actionName, self.mapID)


class SendInvitesCtx(PrbCtrlRequestCtx):

    def __init__(self, databaseIDs, comment, waitingID = ''):
        super(SendInvitesCtx, self).__init__(waitingID)
        self.__databaseIDs = databaseIDs[:300]
        if comment:
            self.__comment = truncate_utf8(comment, INVITE_COMMENT_MAX_LENGTH)
        else:
            self.__comment = ''

    def __repr__(self):
        return 'SendInvitesCtx(databaseIDs = {0!r:s}, comment = {1:>s})'.format(self.__databaseIDs, self.__comment)

    def getDatabaseIDs(self):
        return self.__databaseIDs[:]

    def getComment(self):
        return self.__comment

    def getRequestType(self):
        return REQUEST_TYPE.SEND_INVITE


class CreateFunctionalCtx(object):
    __slots__ = ('__entityType', '__createParams', '__initParams')

    def __init__(self, entityType = 0, create = None, init = None):
        super(CreateFunctionalCtx, self).__init__()
        self.__entityType = entityType
        self.__createParams = create or {}
        self.__initParams = init or {}

    def __repr__(self):
        return 'CreateFunctionalCtx(entityType = {0!r:s}, create = {1!r:s}, init = {2!r:s})'.format(self.__entityType, self.__createParams, self.__initParams)

    def getEntityType(self):
        return self.__entityType

    def setEntityType(self, entityType):
        self.__entityType = entityType

    def getCreateParams(self):
        return self.__createParams.copy()

    def getInitParams(self):
        return self.__initParams.copy()

    def clear(self):
        self.__createParams.clear()
        self.__initParams.clear()


__all__ = ('StartDispatcherCtx', 'PrebattleAction', 'SendInvitesCtx', 'CreateFunctionalCtx')
