# Embedded file name: scripts/client/gui/prb_control/context/__init__.py
from external_strings_utils import truncate_utf8
from gui.prb_control.settings import FUNCTIONAL_FLAG, CTRL_ENTITY_TYPE, convertFlagsToNames, CTRL_ENTITY_TYPE_NAMES, INVITE_COMMENT_MAX_LENGTH, REQUEST_TYPE
from gui.shared.utils.decorators import ReprInjector
from gui.shared.utils.requesters import RequestCtx
__all__ = ('PrbCtrlRequestCtx', 'PrebattleAction', 'SendInvitesCtx', 'CreateFunctionalCtx')

@ReprInjector.simple(('getCtrlTypeName', 'ctrlType'), ('getEntityType', 'entityType'), ('getWaitingID', 'waitingID'), ('getFlagsToStrings', 'flags'), ('isForced', 'forced'))

class PrbCtrlRequestCtx(RequestCtx):
    __slots__ = ('__ctrlType', '__entityType', '__entityID', '__isForced', '__flags')

    def __init__(self, **kwargs):
        if 'waitingID' in kwargs:
            waitingID = kwargs['waitingID']
        else:
            waitingID = ''
        super(PrbCtrlRequestCtx, self).__init__(waitingID)
        if 'ctrlType' in kwargs:
            self.__ctrlType = kwargs['ctrlType']
            if not self.__ctrlType in CTRL_ENTITY_TYPE_NAMES:
                raise AssertionError
            else:
                self.__ctrlType = CTRL_ENTITY_TYPE.UNKNOWN
            if 'entityType' in kwargs:
                self.__entityType = kwargs['entityType']
            else:
                self.__entityType = 0
            if 'entityID' in kwargs:
                self.__entityID = kwargs['entityID']
            else:
                self.__entityID = 0
            if 'isForced' in kwargs:
                self.__isForced = kwargs['isForced']
            else:
                self.__isForced = False
            self.__flags = 'flags' in kwargs and kwargs['flags']
        else:
            self.__flags = FUNCTIONAL_FLAG.UNDEFINED

    def getCtrlType(self):
        return self.__ctrlType

    def getCtrlTypeName(self):
        if self.__ctrlType in CTRL_ENTITY_TYPE_NAMES:
            return CTRL_ENTITY_TYPE_NAMES[self.__ctrlType]
        else:
            return 'CTRL_ENTITY_TYPE_{}'.format(self.__ctrlType)

    def getEntityType(self):
        return self.__entityType

    def getEnityID(self):
        return self.__entityID

    def setForced(self, flag):
        self.__isForced = flag

    def isForced(self):
        return self.__isForced

    def getFlags(self):
        return self.__flags

    def addFlags(self, flag):
        self.__flags |= flag

    def hasFlags(self, flag):
        return self.__flags & flag > 0

    def removeFlags(self, flags):
        result = self.__flags & flags
        if result:
            self.__flags ^= result

    def clearFlags(self):
        self.__flags = FUNCTIONAL_FLAG.UNDEFINED

    def getFlagsToStrings(self):
        return ', '.join(convertFlagsToNames(self.__flags))


@ReprInjector.simple('actionName', 'mapID', 'accountsToInvite')

class PrebattleAction(object):
    __slots__ = ('actionName', 'mapID', 'accountsToInvite')

    def __init__(self, actionName, mapID = 0, accountsToInvite = None):
        self.actionName = actionName if actionName is not None else ''
        self.mapID = mapID
        self.accountsToInvite = accountsToInvite or ()
        return


class SendInvitesCtx(PrbCtrlRequestCtx):

    def __init__(self, databaseIDs, comment, waitingID = ''):
        super(SendInvitesCtx, self).__init__(waitingID=waitingID)
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


@ReprInjector.withParent()

class CreateFunctionalCtx(PrbCtrlRequestCtx):
    __slots__ = ('__initCtx',)

    def __init__(self, ctrlType = CTRL_ENTITY_TYPE.UNKNOWN, entityType = 0, flags = FUNCTIONAL_FLAG.UNDEFINED, initCtx = None):
        super(CreateFunctionalCtx, self).__init__(ctrlType=ctrlType, entityType=entityType, flags=flags)
        self.__initCtx = initCtx

    def getInitCtx(self):
        return self.__initCtx

    def clear(self):
        self.__initCtx = None
        super(CreateFunctionalCtx, self).clear()
        return
