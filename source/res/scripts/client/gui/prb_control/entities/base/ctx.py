# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/ctx.py
from external_strings_utils import truncate_utf8
from gui.prb_control.settings import FUNCTIONAL_FLAG, CTRL_ENTITY_TYPE, convertFlagsToNames, CTRL_ENTITY_TYPE_NAMES, INVITE_COMMENT_MAX_LENGTH, REQUEST_TYPE
from gui.shared.utils.decorators import ReprInjector
from gui.shared.utils.requesters import RequestCtx

@ReprInjector.withParent(('getCtrlTypeName', 'ctrlType'), ('getEntityType', 'entityType'), ('getWaitingID', 'waitingID'), ('getFlagsToStrings', 'flags'), ('isForced', 'forced'))
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
        if 'flags' in kwargs:
            self.__flags = kwargs['flags']
        else:
            self.__flags = FUNCTIONAL_FLAG.UNDEFINED

    def getCtrlType(self):
        return self.__ctrlType

    def getCtrlTypeName(self):
        return CTRL_ENTITY_TYPE_NAMES[self.__ctrlType] if self.__ctrlType in CTRL_ENTITY_TYPE_NAMES else 'CTRL_ENTITY_TYPE_{}'.format(self.__ctrlType)

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

    def addFlags(self, flags):
        self.__flags |= flags

    def hasFlags(self, flags):
        return self.__flags & flags == flags

    def removeFlags(self, flags):
        result = self.__flags & flags
        if result:
            self.__flags ^= result

    def clearFlags(self):
        self.__flags = FUNCTIONAL_FLAG.UNDEFINED

    def getFlagsToStrings(self):
        return ', '.join(convertFlagsToNames(self.__flags))


@ReprInjector.simple('actionName', 'mmData', 'accountsToInvite', 'isCommander')
class PrbAction(object):
    __slots__ = ('actionName', 'mmData', 'accountsToInvite')

    def __init__(self, actionName, mmData=0, accountsToInvite=None):
        self.actionName = actionName if actionName is not None else ''
        self.mmData = mmData
        self.accountsToInvite = accountsToInvite or ()
        return


@ReprInjector.simple('isExit')
class LeavePrbAction(object):
    __slots__ = ('isExit', 'ignoreConfirmation')

    def __init__(self, isExit=True, ignoreConfirmation=False):
        self.isExit = isExit
        self.ignoreConfirmation = ignoreConfirmation


@ReprInjector.withParent(('getDatabaseIDs', 'databaseIDs'), ('getComment', 'comment'))
class SendInvitesCtx(PrbCtrlRequestCtx):

    def __init__(self, databaseIDs, comment, waitingID=''):
        super(SendInvitesCtx, self).__init__(waitingID=waitingID)
        self.__databaseIDs = databaseIDs[:300]
        if comment:
            self.__comment = truncate_utf8(comment, INVITE_COMMENT_MAX_LENGTH)
        else:
            self.__comment = ''

    def getDatabaseIDs(self):
        return self.__databaseIDs[:]

    def getComment(self):
        return self.__comment

    def getRequestType(self):
        return REQUEST_TYPE.SEND_INVITE


class CreatePrbEntityCtx(PrbCtrlRequestCtx):
    __slots__ = ('__initCtx',)

    def __init__(self, ctrlType=CTRL_ENTITY_TYPE.UNKNOWN, entityType=0, flags=FUNCTIONAL_FLAG.UNDEFINED, initCtx=None):
        super(CreatePrbEntityCtx, self).__init__(ctrlType=ctrlType, entityType=entityType, flags=flags)
        self.__initCtx = initCtx

    def getInitCtx(self):
        return self.__initCtx

    def clear(self):
        self.__initCtx = None
        super(CreatePrbEntityCtx, self).clear()
        return
