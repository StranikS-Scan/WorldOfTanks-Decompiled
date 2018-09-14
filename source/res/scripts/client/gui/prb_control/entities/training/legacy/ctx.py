# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/training/legacy/ctx.py
from constants import PREBATTLE_TYPE, OBSERVER_VEH_INVENTORY_ID
from gui.prb_control import settings as prb_settings
from gui.prb_control import prb_getters
from gui.prb_control.entities.base.legacy.ctx import TeamSettingsCtx, JoinLegacyCtx, SetPlayerStateCtx, LegacyRequestCtx
from gui.shared.utils.decorators import ReprInjector
_REQUEST_TYPE = prb_settings.REQUEST_TYPE
_FUNCTIONAL_FLAG = prb_settings.FUNCTIONAL_FLAG

@ReprInjector.withParent(('__arenaTypeID', 'arenaTypeID'), ('__roundLen', 'roundLen'))
class TrainingSettingsCtx(TeamSettingsCtx):
    __slots__ = ('__arenaTypeID', '__roundLen')

    def __init__(self, waitingID='', isOpened=True, comment='', isRequestToCreate=True, arenaTypeID=0, roundLen=900, flags=_FUNCTIONAL_FLAG.UNDEFINED):
        super(TrainingSettingsCtx, self).__init__(PREBATTLE_TYPE.TRAINING, waitingID=waitingID, isOpened=isOpened, comment=comment, isRequestToCreate=isRequestToCreate, flags=flags)
        self.__arenaTypeID = arenaTypeID
        self.__roundLen = int(roundLen)

    @classmethod
    def fetch(cls, settings):
        """
        Fetches training settings and creates context for them
        Args:
            settings: training prebattle settings
        
        Returns:
            set settings context
        """
        return TrainingSettingsCtx(isOpened=settings['isOpened'], comment=settings['comment'], isRequestToCreate=False, arenaTypeID=settings['arenaTypeID'], roundLen=settings['roundLength'])

    def getArenaTypeID(self):
        """
        Gets selected map ID
        """
        return self.__arenaTypeID

    def setArenaTypeID(self, arenaTypeID):
        """
        Sets selected map ID
        Args:
            arenaTypeID: new arena type ID
        """
        self.__arenaTypeID = arenaTypeID

    def getRoundLen(self):
        """
        Gets round length
        """
        return self.__roundLen

    def setRoundLen(self, roundLen):
        """
        Sets round length
        Args:
            roundLen: new round length
        """
        self.__roundLen = int(roundLen)

    def isArenaTypeIDChanged(self, settings):
        """
        Was map changed
        Args:
            settings: prebattle settings like PREBATTLE_SETTING_NAME -> value
        """
        return self.__arenaTypeID != settings[prb_settings.PREBATTLE_SETTING_NAME.ARENA_TYPE_ID]

    def isRoundLenChanged(self, settings):
        """
        Was round length
        Args:
            settings: prebattle settings like PREBATTLE_SETTING_NAME -> value
        """
        return self.__roundLen != settings[prb_settings.PREBATTLE_SETTING_NAME.ROUND_LENGTH]

    def areSettingsChanged(self, settings):
        """
        Were settings changed
        Args:
            settings: prebattle settings like PREBATTLE_SETTING_NAME -> value
        """
        return super(TrainingSettingsCtx, self).areSettingsChanged(settings) or self.isArenaTypeIDChanged(settings) or self.isRoundLenChanged(settings)


class JoinTrainingCtx(JoinLegacyCtx):
    """
    Join training request context
    """
    __slots__ = ()

    def __init__(self, prbID, waitingID='', flags=_FUNCTIONAL_FLAG.UNDEFINED):
        super(JoinTrainingCtx, self).__init__(prbID, PREBATTLE_TYPE.TRAINING, waitingID=waitingID, flags=flags)


@ReprInjector.withParent(('__channels', 'channels'))
class ChangeArenaVoipCtx(LegacyRequestCtx):
    """
    Change arena VOIP settigns request context
    """
    __slots__ = ('__channels',)

    def __init__(self, channels, waitingID=''):
        super(ChangeArenaVoipCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__channels = channels

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_ARENA_VOIP

    def getChannels(self):
        """
        Gets selected channels
        """
        return self.__channels


@ReprInjector.withParent(('__isObserver', 'isObserver'))
class SetPlayerObserverStateCtx(SetPlayerStateCtx):
    """
    Set/unset player as observer request context
    """
    __slots__ = ('__isObserver',)

    def __init__(self, isObserver, isReadyState, isInitial=False, waitingID=''):
        super(SetPlayerObserverStateCtx, self).__init__(isReadyState, isInitial=isInitial, waitingID=waitingID)
        self.__isObserver = isObserver

    def doVehicleValidation(self):
        return False

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_USER_STATUS

    def getVehicleInventoryID(self):
        return OBSERVER_VEH_INVENTORY_ID

    def isObserver(self):
        """
        Should this player be observer or not
        """
        return self.__isObserver
