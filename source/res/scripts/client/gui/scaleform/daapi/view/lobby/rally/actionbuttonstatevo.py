# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/ActionButtonStateVO.py
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.shared.formatters import text_styles
from helpers import i18n

class ActionButtonStateVO(dict):
    __NOT_CRITICAL_STATES = (UNIT_RESTRICTION.UNDEFINED,
     UNIT_RESTRICTION.IS_IN_IDLE,
     UNIT_RESTRICTION.IS_IN_PRE_ARENA,
     UNIT_RESTRICTION.VEHICLE_NOT_VALID_FOR_EVENT,
     UNIT_RESTRICTION.FALLOUT_NOT_ENOUGH_PLAYERS)

    def __init__(self, unitFunctional):
        super(ActionButtonStateVO, self).__init__()
        self._playerInfo = unitFunctional.getPlayerInfo()
        self._extra = unitFunctional.getExtra()
        self.__unitIsValid, self.__restrictionType = unitFunctional.canPlayerDoAction()
        self.__isEnabled = self._isEnabled(self.__unitIsValid, self.__restrictionType)
        self.__stats = unitFunctional.getStats()
        self.__flags = unitFunctional.getFlags()
        self.__settings = unitFunctional.getRosterSettings()
        self.__canTakeSlot = not self._playerInfo.isLegionary()
        self.__INVALID_UNIT_MESSAGES = {UNIT_RESTRICTION.UNIT_IS_FULL: (CYBERSPORT.WINDOW_UNIT_MESSAGE_UNITISFULL, {}),
         UNIT_RESTRICTION.VEHICLE_NOT_FOUND: (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLENOTFOUND, {}),
         UNIT_RESTRICTION.UNIT_IS_LOCKED: (CYBERSPORT.WINDOW_UNIT_MESSAGE_UNITISLOCKED, {}),
         UNIT_RESTRICTION.VEHICLE_NOT_SELECTED: (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLENOTSELECTED, {}),
         UNIT_RESTRICTION.VEHICLE_NOT_VALID: (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLENOTVALID, {}),
         UNIT_RESTRICTION.VEHICLE_BROKEN: (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLEINNOTREADY_BROKEN, {}),
         UNIT_RESTRICTION.VEHICLE_CREW_NOT_FULL: (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLEINNOTREADY_CREWNOTFULL, {}),
         UNIT_RESTRICTION.VEHICLE_RENT_IS_OVER: (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLEINNOTREADY_RENTISOVER, {}),
         UNIT_RESTRICTION.VEHICLE_IS_IN_BATTLE: (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLEINNOTREADY_ISINBATTLE, {}),
         UNIT_RESTRICTION.MIN_SLOTS: (CYBERSPORT.WINDOW_UNIT_MESSAGE_MINSLOTS, {}),
         UNIT_RESTRICTION.NOT_READY_IN_SLOTS: (CYBERSPORT.WINDOW_UNIT_MESSAGE_WAITING, {}),
         UNIT_RESTRICTION.MIN_TOTAL_LEVEL: self.__levelMessage(),
         UNIT_RESTRICTION.MAX_TOTAL_LEVEL: self.__levelMessage(),
         UNIT_RESTRICTION.INVALID_TOTAL_LEVEL: ActionButtonStateVO.getInvalidVehicleLevelsMessage(unitFunctional),
         UNIT_RESTRICTION.IS_IN_IDLE: self._getIdleStateStr(),
         UNIT_RESTRICTION.IS_IN_ARENA: self._getArenaStateStr(),
         UNIT_RESTRICTION.NEED_PLAYERS_SEARCH: ('', {}),
         UNIT_RESTRICTION.ZERO_TOTAL_LEVEL: ('', {}),
         UNIT_RESTRICTION.IS_IN_PRE_ARENA: (CYBERSPORT.WINDOW_UNIT_MESSAGE_WAITCOMMANDER, {}),
         UNIT_RESTRICTION.NOT_IN_SLOT: self.__notInSlotMessage(),
         UNIT_RESTRICTION.VEHICLE_NOT_VALID_FOR_EVENT: (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLENOTVALID, {}),
         UNIT_RESTRICTION.CURFEW: (CYBERSPORT.WINDOW_UNIT_MESSAGE_CURFEW, {}),
         UNIT_RESTRICTION.VEHICLE_WRONG_MODE: (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLEINNOTREADY_WRONGMODE, {}),
         UNIT_RESTRICTION.FALLOUT_NOT_ENOUGH_PLAYERS: ('', {}),
         UNIT_RESTRICTION.FALLOUT_VEHICLE_LEVEL_REQUIRED: self._getFalloutVehLevelStr(),
         UNIT_RESTRICTION.FALLOUT_VEHICLE_MIN: self._getFalloutVehMinStr(),
         UNIT_RESTRICTION.FALLOUT_VEHICLE_MAX: ('', {}),
         UNIT_RESTRICTION.FALLOUT_VEHICLE_BROKEN: self._getFalloutVehBrokenStr()}
        stateKey, stateCtx = self.__getState()
        self['stateString'] = self.__stateTextStyleFormatter(i18n.makeString(stateKey, **stateCtx))
        self['label'] = self._getLabel()
        self['isEnabled'] = self.__isEnabled
        self['isReady'] = self._playerInfo.isReady
        self['toolTipData'] = self.__toolTipData

    def _getReadyValidInSlotStateStr(self):
        return (CYBERSPORT.WINDOW_UNIT_MESSAGE_WAITING, {})

    def _getIdleStateStr(self):
        return (CYBERSPORT.WINDOW_UNIT_MESSAGE_READY, {})

    def _getArenaStateStr(self):
        return ('', {})

    def _getFalloutVehLevelStr(self):
        return ('', {})

    def _getFalloutVehMinStr(self):
        return ('', {})

    def _getFalloutVehBrokenStr(self):
        return ('', {})

    def _isEnabled(self, isValid, restriction):
        return isValid

    def _getLabel(self):
        label = CYBERSPORT.WINDOW_UNIT_READY
        if self._playerInfo.isCreator():
            label = CYBERSPORT.WINDOW_UNIT_FIGHT
        if self._playerInfo.isReady and self.__restrictionType != UNIT_RESTRICTION.IS_IN_IDLE:
            label = CYBERSPORT.WINDOW_UNIT_NOTREADY
        return label

    def __getState(self):
        if self.__isEnabled:
            if self._playerInfo.isInSlot:
                if self._playerInfo.isReady:
                    return self._getReadyValidInSlotStateStr()
                else:
                    return (CYBERSPORT.WINDOW_UNIT_MESSAGE_GETREADY, {})
            elif self.__canTakeSlot:
                return (CYBERSPORT.WINDOW_UNIT_MESSAGE_CANDIDATE, {})
            elif self.__flags.isLocked():
                return (CYBERSPORT.WINDOW_UNIT_MESSAGE_UNITISLOCKED, {})
            else:
                return (CYBERSPORT.WINDOW_UNIT_MESSAGE_UNITISFULL, {})
        else:
            return self.__INVALID_UNIT_MESSAGES[self.__restrictionType]

    @property
    def __toolTipData(self):
        if not self._playerInfo.isInSlot:
            return TOOLTIPS.CYBERSPORT_UNIT_FIGHTBTN_NOTINSLOT
        elif self.__restrictionType == UNIT_RESTRICTION.VEHICLE_NOT_VALID:
            return TOOLTIPS.CYBERSPORT_UNIT_FIGHTBTN_VEHICLENOTVALID
        elif self.__isEnabled and not self._playerInfo.isReady:
            return TOOLTIPS.CYBERSPORT_UNIT_FIGHTBTN_PRESSFORREADY
        elif self.__isEnabled and self._playerInfo.isReady:
            return TOOLTIPS.CYBERSPORT_UNIT_FIGHTBTN_PRESSFORNOTREADY
        else:
            return ''

    def __stateTextStyleFormatter(self, state):
        if self.__restrictionType not in self.__NOT_CRITICAL_STATES:
            return text_styles.error(state)
        return text_styles.main(state)

    def __notInSlotMessage(self):
        if self.__canTakeSlot:
            return (CYBERSPORT.WINDOW_UNIT_MESSAGE_CANDIDATE, {})
        else:
            return (CYBERSPORT.WINDOW_UNIT_MESSAGE_UNITISFULL, {})

    def __levelMessage(self):
        if self.__restrictionType == UNIT_RESTRICTION.MAX_TOTAL_LEVEL:
            return (CYBERSPORT.WINDOW_UNIT_MESSAGE_LEVEL, {'level': self.__stats.maxTotalLevel})
        if self.__restrictionType == UNIT_RESTRICTION.MIN_TOTAL_LEVEL:
            return (CYBERSPORT.WINDOW_UNIT_MESSAGE_LEVEL, {'level': self.__stats.minTotalLevel})
        return ('', {})

    @staticmethod
    def getInvalidVehicleLevelsMessage(unitFunctional):
        stats = unitFunctional.getStats()
        vehLevels = unitFunctional.getUnitInvalidLevels(stats=stats)
        stateString = CYBERSPORT.WINDOW_UNIT_MESSAGE_INVALIDLEVELERROR_UNRESOLVED
        if len(vehLevels):
            stateStringCandidate = CYBERSPORT.window_unit_message_invalidlevelerror('_'.join(map(lambda level: str(level), vehLevels)))
            if stateStringCandidate is not None:
                stateString = stateStringCandidate
        return (stateString, {})
