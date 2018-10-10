# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/epic_battle_training/ctx.py
from constants import PREBATTLE_TYPE, OBSERVER_VEH_INVENTORY_ID
from gui.prb_control import settings as prb_settings
from gui.prb_control import prb_getters
from gui.prb_control.entities.base.legacy.ctx import TeamSettingsCtx, JoinLegacyCtx, SetPlayerStateCtx, LegacyRequestCtx
from gui.shared.utils.decorators import ReprInjector
_REQUEST_TYPE = prb_settings.REQUEST_TYPE
_FUNCTIONAL_FLAG = prb_settings.FUNCTIONAL_FLAG

@ReprInjector.withParent(('__arenaTypeID', 'arenaTypeID'), ('__roundLen', 'roundLen'))
class EpicTrainingSettingsCtx(TeamSettingsCtx):
    __slots__ = ('__arenaTypeID', '__roundLen')

    def __init__(self, waitingID='', isOpened=True, comment='', isRequestToCreate=True, arenaTypeID=0, roundLen=900, flags=_FUNCTIONAL_FLAG.UNDEFINED):
        super(EpicTrainingSettingsCtx, self).__init__(PREBATTLE_TYPE.EPIC_TRAINING, waitingID=waitingID, isOpened=isOpened, comment=comment, isRequestToCreate=isRequestToCreate, flags=flags)
        self.__arenaTypeID = arenaTypeID
        self.__roundLen = int(roundLen)

    @classmethod
    def fetch(cls, settings):
        return EpicTrainingSettingsCtx(isOpened=settings['isOpened'], comment=settings['comment'], isRequestToCreate=False, arenaTypeID=settings['arenaTypeID'], roundLen=settings['roundLength'])

    def getArenaTypeID(self):
        return self.__arenaTypeID

    def setArenaTypeID(self, arenaTypeID):
        self.__arenaTypeID = arenaTypeID

    def getRoundLen(self):
        return self.__roundLen

    def setRoundLen(self, roundLen):
        self.__roundLen = int(roundLen)

    def isArenaTypeIDChanged(self, settings):
        return self.__arenaTypeID != settings[prb_settings.PREBATTLE_SETTING_NAME.ARENA_TYPE_ID]

    def isRoundLenChanged(self, settings):
        return self.__roundLen != settings[prb_settings.PREBATTLE_SETTING_NAME.ROUND_LENGTH]

    def areSettingsChanged(self, settings):
        return super(EpicTrainingSettingsCtx, self).areSettingsChanged(settings) or self.isArenaTypeIDChanged(settings) or self.isRoundLenChanged(settings)


class JoinEpicBattleTrainingCtx(JoinLegacyCtx):
    __slots__ = ()

    def __init__(self, prbID, waitingID='', flags=_FUNCTIONAL_FLAG.UNDEFINED):
        super(JoinEpicBattleTrainingCtx, self).__init__(prbID, PREBATTLE_TYPE.EPIC_TRAINING, waitingID=waitingID, flags=flags)


@ReprInjector.withParent(('__channels', 'channels'))
class ChangeArenaVoipCtx(LegacyRequestCtx):
    __slots__ = ('__channels',)

    def __init__(self, channels, waitingID=''):
        super(ChangeArenaVoipCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__channels = channels

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_ARENA_VOIP

    def getChannels(self):
        return self.__channels


@ReprInjector.withParent(('__isObserver', 'isObserver'))
class SetPlayerObserverStateCtx(SetPlayerStateCtx):
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
        return self.__isObserver
