# Embedded file name: scripts/client/gui/prb_control/context/__init__.py
from constants import QUEUE_TYPE
from external_strings_utils import truncate_utf8
from gui.prb_control import isInRandomQueue, isInTutorialQueue, getPrebattleID
from gui.prb_control import isInHistoricalQueue, isInEventBattlesQueue
from gui.prb_control import settings as prb_settings
from gui.shared.utils.decorators import ReprInjector
from gui.shared.utils.requesters.rqs_by_id import RequestCtx

class StartDispatcherCtx(object):
    __slots__ = ['isInRandomQueue',
     'isInTutorialQueue',
     'isInHistoricalQueue',
     'isInEventBattles',
     'prebattleID',
     'prbSettings']

    def __init__(self, **kwargs):
        super(StartDispatcherCtx, self).__init__()
        self.isInRandomQueue = kwargs.get('isInRandomQueue', False)
        self.isInTutorialQueue = kwargs.get('isInTutorialQueue', False)
        self.isInHistoricalQueue = kwargs.get('isInHistoricalQueue', False)
        self.isInEventBattles = kwargs.get('isInEventBattles', False)
        self.prebattleID = kwargs.get('prebattleID', 0L)
        self.prbSettings = kwargs.get('prbSettings')

    def __repr__(self):
        return 'StartDispatcherCtx(inRandomQueue = {0!r:s}, inTutorialQueue = {1!r:s}, isInHistoricalQueue = {2!r:s}, prebattleID = {3:n}, prbSettings = {4!r:s})'.format(self.isInRandomQueue, self.isInTutorialQueue, self.isInHistoricalQueue, self.prebattleID, self.prbSettings)

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


@ReprInjector.simple(('getWaitingID', 'waitingID'), ('__isForced', 'forced'))

class PrbCtrlRequestCtx(RequestCtx):

    def __init__(self, **kwargs):
        if 'waitingID' in kwargs:
            waitingID = kwargs['waitingID']
        else:
            waitingID = ''
        super(PrbCtrlRequestCtx, self).__init__(waitingID)
        if 'isForced' in kwargs:
            self.__isForced = kwargs['isForced']
        else:
            self.__isForced = False
        if 'funcExit' in kwargs:
            self.__funcExit = kwargs['funcExit']
        else:
            self.__funcExit = prb_settings.FUNCTIONAL_EXIT.NO_FUNC

    def getCtrlType(self):
        return 0

    def getPrbType(self):
        return 0

    def setForced(self, flag):
        self.__isForced = flag

    def isForced(self):
        return self.__isForced

    def getFuncExit(self):
        return self.__funcExit

    def setFuncExit(self, funcExit):
        self.__funcExit = funcExit


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
        super(SendInvitesCtx, self).__init__(waitingID=waitingID)
        self.__databaseIDs = databaseIDs[:300]
        if comment:
            self.__comment = truncate_utf8(comment, prb_settings.INVITE_COMMENT_MAX_LENGTH)
        else:
            self.__comment = ''

    def __repr__(self):
        return 'SendInvitesCtx(databaseIDs = {0!r:s}, comment = {1:>s})'.format(self.__databaseIDs, self.__comment)

    def getDatabaseIDs(self):
        return self.__databaseIDs[:]

    def getComment(self):
        return self.__comment

    def getRequestType(self):
        return prb_settings.REQUEST_TYPE.SEND_INVITE


class CreateFunctionalCtx(PrbCtrlRequestCtx):
    __slots__ = ('__ctrlType', '__prbType', '__createParams', '__initParams')

    def __init__(self, ctrlType, prbType = 0, create = None, init = None):
        super(CreateFunctionalCtx, self).__init__()
        self.__ctrlType = ctrlType
        self.__prbType = prbType
        self.__createParams = create or {}
        self.__initParams = init or {}

    def __repr__(self):
        return 'CreateFunctionalCtx(ctrlType = {0:n}, prbType = {1:n}, create = {2!r:s}, init = {3!r:s})'.format(self.__ctrlType, self.__prbType, self.__createParams, self.__initParams)

    def getCtrlType(self):
        return self.__ctrlType

    def getPrbType(self):
        return self.__prbType

    def getCreateParams(self):
        return self.__createParams.copy()

    def getInitParams(self):
        return self.__initParams.copy()

    def clear(self):
        self.__createParams.clear()
        self.__initParams.clear()


__all__ = ('StartDispatcherCtx', 'PrebattleAction', 'SendInvitesCtx', 'CreateFunctionalCtx')
