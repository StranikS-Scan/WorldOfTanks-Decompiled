# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/entity.py
from constants import QUEUE_TYPE
from debug_utils import LOG_ERROR
from gui.prb_control.entities.base.actions_validator import NotSupportedActionsValidator, BaseActionsValidator
from gui.prb_control.entities.base.actions_validator import IActionsValidator
from gui.prb_control.entities.base.permissions import IPrbPermissions
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.items import SelectResult, ValidationResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, CTRL_ENTITY_TYPE
from gui.shared.utils.listeners_collection import IListenersCollection

class PrbFunctionalFlags(object):
    """
    Base class for any prebattle instance that has functional flags.
    """
    __slots__ = ('_entityFlags', '_modeFlags')

    def __init__(self, entityFlags, modeFlags, **kwargs):
        super(PrbFunctionalFlags, self).__init__()
        self._entityFlags = entityFlags
        self._modeFlags = modeFlags

    def getModeFlags(self):
        """
        Getter for flags that related to prebattle mode: FORT, RANDOM or other.
        """
        return self._modeFlags

    def getEntityFlags(self):
        """
        Getter for flags that related to prebattle entity: INTRO, BROWSER, ROOM etc.
        """
        return self._entityFlags

    def getFunctionalFlags(self):
        """
        Getter for unique combination of flags.
        """
        return self._modeFlags | self._entityFlags


class BasePrbEntryPoint(PrbFunctionalFlags):
    """
    Base class for prebatle entry point:
    - processes action come from UI components;
    - creates prebattle;
    - joins to prebattle.
    """

    def isVisualOnly(self):
        """
        Is this entry visual only and has no entity to invoke.
        """
        return False

    def makeDefCtx(self):
        """
        Makes default context for given entry.
        """
        return None

    def create(self, ctx, callback=None):
        """
        Request to create prebattle.
        Args:
            ctx: create request context
            callback: operation callback
        """
        pass

    def canCreate(self):
        """
        Can this entry point create
        """
        return True

    def join(self, ctx, callback=None):
        """
        Request to join prebattle.
        Args:
            ctx: create request context
            callback: operation callback
        """
        pass

    def canJoin(self):
        """
        Can this entry point join
        """
        return True

    def select(self, ctx, callback=None):
        """
        Request to select any prebattle.
        Args:
            ctx: create request context
            callback: operation callback
        """
        pass

    def setAccountsToInvite(self, accountsToInvite):
        """
        Sets accounts to invite if it is supported.
        Args:
            accountsToInvite: list of accounts DB IDs to invite.
        """
        pass


class BasePrbEntity(IActionsValidator, PrbFunctionalFlags):
    """
    Interface which describes shared functionality shared for prebattle/unit in GUI.
    It provides the following:
    - adds/removes listener;
    - processes action come from UI components;
    - leave legacy/unit/prequeue;
    - send request to server to some actions. For example, send request to server to assign player in team 1.
    """

    def __init__(self, entityFlags, modeFlags):
        super(BasePrbEntity, self).__init__(entityFlags=entityFlags, modeFlags=modeFlags)
        self._actionsValidator = self._createActionsValidator()
        self._scheduler = self._createScheduler()
        self._isActive = False

    def init(self, **kwargs):
        """
        Initialization.
        Returns:
            functional flags of initialization
        """
        self._scheduler.init()
        self._isActive = True
        return FUNCTIONAL_FLAG.UNDEFINED

    def fini(self, **kwargs):
        """
        Finalization.
        Returns:
            functional flags of finalization
        """
        self._scheduler.fini()
        self._isActive = False
        return FUNCTIONAL_FLAG.UNDEFINED

    def restore(self):
        """
        Prebattle entity restoration. Is called when some entity was restored
        after center disconnection or smth.
        """
        pass

    def rejoin(self):
        """
        Prebattle rejoin. Called when player is already joined some prebattle
        and he gets another join event.
        """
        pass

    def canSwitch(self, ctx):
        """
        Can current entity switch to another entity with given context.
        Args:
            ctx: another entity join/create context.
        
        Returns:
            can it be switched
        """
        return ctx is not None and self.getModeFlags() & FUNCTIONAL_FLAG.MODES_BITMASK > 0 and ctx.hasFlags(self.getModeFlags())

    def isActive(self):
        """
        Is this entity currently active.
        """
        return self._isActive

    def isPlayerJoined(self, ctx):
        """
        Is player joined to prebattle/unit that in ctx.
        Args:
            ctx: another entity join/create context.
        """
        return False

    def isInQueue(self):
        """
        Is player is in queue.
        """
        return False

    def canKeepMode(self):
        """
        Can this functional be switched to intro.
        """
        return True

    def resetPlayerState(self):
        """
        Resets state of current player.
        """
        pass

    def canPlayerDoAction(self):
        """
        Can current player set ready state or go into battle.
        Validates it with actions validators.
        Returns:
            validation result object
        """
        return self._actionsValidator.canPlayerDoAction() or ValidationResult()

    def doAction(self, action=None):
        """
        Processes action come from GUI: set ready or start battle.
        Args:
            action: prebattle action
        
        Returns:
            was this action processed
        """
        return False

    def doSelectAction(self, action):
        """
        Processes action come from GUI selector to switch to another mode.
        Args:
            action: prebattle select action
        
        Returns:
            select result object
        """
        return SelectResult()

    def showGUI(self, ctx=None):
        """
        Dispatch event.
        Args:
            ctx: prebattle init context
        
        Returns:
            False - if showGUI isn't overridden, else: call events_dispatcher
        """
        return False

    def getConfirmDialogMeta(self, ctx):
        """
        Gets meta for leave confirmation dialog.
        Args:
            ctx: leave request context
        
        Returns:
            leave confirm dialog meta
        """
        return None

    def getID(self):
        """
        Gets prebattle ID/unit index. The 0 means prebattle/unit is not defined.
        """
        pass

    def getCtrlType(self):
        """
        Gets type for entity's control.
        """
        return CTRL_ENTITY_TYPE.UNKNOWN

    def getEntityType(self):
        """
        Gets type of prebattle. The 0 means type of prebattle/unit is not defined.
        Returns:
            entity type, one from queue/prebattle type.
        """
        pass

    def getIntroType(self):
        """
        Gets type of intro entity if it is supported. For example:
        eSport entity has eSport common entity as intro.
        Returns:
            intro entity type
        """
        pass

    def getQueueType(self):
        """
        Gets queue type for entity. It means, which queue entity will get
        into after start battle action.
        Returns:
            entity queue type
        """
        return QUEUE_TYPE.UNKNOWN

    def hasLockedState(self):
        """
        Is entity in locked state and client can not leave prebattle.
        """
        return False

    def getPermissions(self, pID=None, **kwargs):
        """
        Gets player's permissions.
        Args:
            pID: player's identifier
            **kwargs:
        
        Returns:
            player's permissions object
        """
        return IPrbPermissions()

    def isCommander(self, dbID=None):
        """
        Is player - entity's commander.
        Args:
            dbID: player's database ID to check.
        """
        return False

    def leave(self, ctx, callback=None):
        """
        Leaves prebattle.
        Args:
            ctx: leave request context
            callback: operation callback
        """
        pass

    def request(self, ctx, callback=None):
        """
        Sends request to prebattle entity.
        Args:
            ctx: request context
            callback: operation callback
        """
        pass

    def _createActionsValidator(self):
        """
        Creates actions validator object.
        """
        return BaseActionsValidator(self)

    def _createScheduler(self):
        """
        Creates scheduler object.
        """
        return BaseScheduler(self)


class NotSupportedEntryPoint(BasePrbEntryPoint):
    """
    Entry point that is not supported buy our system. Used for default or
    unavailable prebattle system state.
    """

    def __init__(self):
        super(NotSupportedEntryPoint, self).__init__(entityFlags=FUNCTIONAL_FLAG.UNDEFINED, modeFlags=FUNCTIONAL_FLAG.UNDEFINED)

    def create(self, ctx, callback=None):
        LOG_ERROR('NotSupportedEntry.create', ctx)

    def join(self, ctx, callback=None):
        LOG_ERROR('NotSupportedEntry.join', ctx)


class NotSupportedEntity(BasePrbEntity, IListenersCollection):
    """
    Entity that is not supported buy our system. Used for default or
    unavailable prebattle system state.
    """

    def __init__(self):
        super(NotSupportedEntity, self).__init__(entityFlags=FUNCTIONAL_FLAG.UNDEFINED, modeFlags=FUNCTIONAL_FLAG.UNDEFINED)

    def _createActionsValidator(self):
        return NotSupportedActionsValidator()
