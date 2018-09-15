# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/ctx.py
from external_strings_utils import truncate_utf8
from gui.prb_control.settings import FUNCTIONAL_FLAG, CTRL_ENTITY_TYPE, convertFlagsToNames, CTRL_ENTITY_TYPE_NAMES, INVITE_COMMENT_MAX_LENGTH, REQUEST_TYPE
from gui.shared.utils.decorators import ReprInjector
from gui.shared.utils.requesters import RequestCtx

@ReprInjector.withParent(('getCtrlTypeName', 'ctrlType'), ('getEntityType', 'entityType'), ('getWaitingID', 'waitingID'), ('getFlagsToStrings', 'flags'), ('isForced', 'forced'))
class PrbCtrlRequestCtx(RequestCtx):
    """
    Base prebattle request context.
    """
    __slots__ = ('__ctrlType', '__entityType', '__entityID', '__isForced', '__flags')

    def __init__(self, **kwargs):
        if 'waitingID' in kwargs:
            waitingID = kwargs['waitingID']
        else:
            waitingID = ''
        super(PrbCtrlRequestCtx, self).__init__(waitingID)
        if 'ctrlType' in kwargs:
            self.__ctrlType = kwargs['ctrlType']
            assert self.__ctrlType in CTRL_ENTITY_TYPE_NAMES
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
        """
        Getter for control type: one from CTRL_ENTITY_TYPE
        """
        return self.__ctrlType

    def getCtrlTypeName(self):
        return CTRL_ENTITY_TYPE_NAMES[self.__ctrlType] if self.__ctrlType in CTRL_ENTITY_TYPE_NAMES else 'CTRL_ENTITY_TYPE_{}'.format(self.__ctrlType)

    def getEntityType(self):
        """
        Getter for entity type: QUEUE_TYPE, PREBATTLE_TYPE, etc.
        """
        return self.__entityType

    def getEnityID(self):
        """
        Getter for entity identifier: unit ID, prebattle ID
        """
        return self.__entityID

    def setForced(self, flag):
        """
        Set this request to be forced.
        Args:
            flag: new flag value
        """
        self.__isForced = flag

    def isForced(self):
        return self.__isForced

    def getFlags(self):
        """
        Getter for request functional flags: any combination of FUNCTIONA_FLAG
        """
        return self.__flags

    def addFlags(self, flags):
        """
        Adds new flags to that already set.
        Args:
            flags: flags mask to add
        """
        self.__flags |= flags

    def hasFlags(self, flags):
        """
        Checks flag mask total inclusion in current funcitonal flags.
        Args:
            flags: flags mask to check
        """
        return self.__flags & flags == flags

    def removeFlags(self, flags):
        """
        Removes flags from context.
        Args:
            flags: flags to remove
        """
        result = self.__flags & flags
        if result:
            self.__flags ^= result

    def clearFlags(self):
        """
        Sets functional flags to default.
        """
        self.__flags = FUNCTIONAL_FLAG.UNDEFINED

    def getFlagsToStrings(self):
        """
        Converts flags into string representation.
        """
        return ', '.join(convertFlagsToNames(self.__flags))


@ReprInjector.simple('actionName', 'mapID', 'accountsToInvite')
class PrbAction(object):
    """
    Class for player'r prebattle action data.
    """
    __slots__ = ('actionName', 'mapID', 'accountsToInvite')

    def __init__(self, actionName, mapID=0, accountsToInvite=None):
        self.actionName = actionName if actionName is not None else ''
        self.mapID = mapID
        self.accountsToInvite = accountsToInvite or ()
        return


@ReprInjector.simple('isExit')
class LeavePrbAction(object):
    """
    Class for player'r prebattle leave action data.
    """
    __slots__ = ('isExit',)

    def __init__(self, isExit=True):
        self.isExit = isExit


@ReprInjector.withParent(('getDatabaseIDs', 'databaseIDs'), ('getComment', 'comment'))
class SendInvitesCtx(PrbCtrlRequestCtx):
    """
    Context for send invitations request.
    """

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
        """
        Reference to new prebattle init context.
        """
        return self.__initCtx

    def clear(self):
        self.__initCtx = None
        super(CreatePrbEntityCtx, self).clear()
        return
