# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/ActionButtonStateVO.py
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.settings import UNIT_RESTRICTION

class ActionButtonStateVO(dict):

    def __init__(self, unitFunctional):
        super(ActionButtonStateVO, self).__init__()
        self.__playerInfo = unitFunctional.getPlayerInfo()
        self.__unitIsValid, self.__restrictionType = unitFunctional.canPlayerDoAction()
        self.__stats = unitFunctional.getStats()
        self.__settings = unitFunctional.getRosterSettings()
        self.__INVALID_UNIT_MESSAGES = {UNIT_RESTRICTION.UNIT_IS_FULL: FORTIFICATIONS.SORTIE_ROOM_MESSAGE_CANDIDATE_UNITISFULL,
         UNIT_RESTRICTION.VEHICLE_NOT_FOUND: FORTIFICATIONS.SORTIE_ROOM_MESSAGE_CANDIDATE_INVALIDVEHICLES,
         UNIT_RESTRICTION.UNIT_IS_LOCKED: FORTIFICATIONS.SORTIE_ROOM_MESSAGE_CANDIDATE_LOCKEDUNITS,
         UNIT_RESTRICTION.VEHICLE_NOT_SELECTED: self.__vehNotSelectedMessage(),
         UNIT_RESTRICTION.VEHICLE_NOT_VALID: FORTIFICATIONS.SORTIE_ROOM_MESSAGE_VEHICLEINNOTREADY,
         UNIT_RESTRICTION.MIN_SLOTS: self.__minSlotsMessage(),
         UNIT_RESTRICTION.NOT_READY_IN_SLOTS: FORTIFICATIONS.SORTIE_ROOM_MESSAGE_WAITING,
         UNIT_RESTRICTION.MIN_TOTAL_LEVEL: self.__minTotalLevelMessage(),
         UNIT_RESTRICTION.MAX_TOTAL_LEVEL: CYBERSPORT.WINDOW_UNIT_MESSAGE_MAXLEVELERROR,
         UNIT_RESTRICTION.INVALID_TOTAL_LEVEL: ActionButtonStateVO.getInvalidVehicleLevelsMessage(unitFunctional),
         UNIT_RESTRICTION.IS_IN_IDLE: FORTIFICATIONS.SORTIE_ROOM_MESSAGE_READY,
         UNIT_RESTRICTION.IS_IN_ARENA: '',
         UNIT_RESTRICTION.NEED_PLAYERS_SEARCH: '',
         UNIT_RESTRICTION.ZERO_TOTAL_LEVEL: ''}
        self['stateString'] = self.__stateString
        self['label'] = self.__label
        self['isEnabled'] = self.__unitIsValid
        self['isReady'] = self.__playerInfo.isReady
        self['toolTipData'] = self.__toolTipData

    @property
    def __stateString(self):
        if self.__unitIsValid:
            if self.__playerInfo.isInSlot:
                if self.__playerInfo.isCreator():
                    if self.__stats.occupiedSlotsCount < self.__settings.getMinSlots():
                        return FORTIFICATIONS.SORTIE_ROOM_MESSAGE_NOTFULLUNIT
                if self.__playerInfo.isReady:
                    return FORTIFICATIONS.SORTIE_ROOM_MESSAGE_WAITING
                else:
                    return FORTIFICATIONS.SORTIE_ROOM_MESSAGE_GETREADY
            else:
                return FORTIFICATIONS.SORTIE_ROOM_MESSAGE_CANDIDATE
        else:
            return self.__INVALID_UNIT_MESSAGES[self.__restrictionType]

    @property
    def __toolTipData(self):
        if not self.__playerInfo.isInSlot:
            return TOOLTIPS.FORTIFICATION_FORTCLANBATTLEROOM_FIGHTBTN_NOTINSLOT
        elif self.__restrictionType == UNIT_RESTRICTION.VEHICLE_NOT_VALID:
            return TOOLTIPS.FORTIFICATION_FORTCLANBATTLEROOM_FIGHTBTN_VEHICLENOTVALID
        elif self.__unitIsValid and not self.__playerInfo.isReady:
            return TOOLTIPS.FORTIFICATION_FORTCLANBATTLEROOM_FIGHTBTN_PRESSFORREADY
        elif self.__unitIsValid and self.__playerInfo.isReady:
            return TOOLTIPS.FORTIFICATION_FORTCLANBATTLEROOM_FIGHTBTN_PRESSFORNOTREADY
        else:
            return ''

    @property
    def __label(self):
        label = FORTIFICATIONS.SORTIE_ROOM_READY
        if self.__playerInfo.isCreator():
            label = FORTIFICATIONS.SORTIE_ROOM_FIGHT
        if self.__playerInfo.isReady and self.__restrictionType != UNIT_RESTRICTION.IS_IN_IDLE:
            label = FORTIFICATIONS.SORTIE_ROOM_NOTREADY
        return label

    def __minTotalLevelMessage(self):
        if self.__playerInfo.isInSlot:
            return CYBERSPORT.WINDOW_UNIT_MESSAGE_MINLEVELERROR
        else:
            return FORTIFICATIONS.SORTIE_ROOM_MESSAGE_CANDIDATE

    def __minSlotsMessage(self):
        if self.__playerInfo.isInSlot:
            return FORTIFICATIONS.SORTIE_ROOM_MESSAGE_NOTFULLUNIT
        else:
            return FORTIFICATIONS.SORTIE_ROOM_MESSAGE_CANDIDATE

    def __vehNotSelectedMessage(self):
        if self.__playerInfo.isInSlot:
            return FORTIFICATIONS.SORTIE_ROOM_MESSAGE_NOVEHICLE
        else:
            return FORTIFICATIONS.SORTIE_ROOM_MESSAGE_CANDIDATE

    @staticmethod
    def getInvalidVehicleLevelsMessage(unitFunctional):
        stats = unitFunctional.getStats()
        vehLevels = unitFunctional.getUnitInvalidLevels(stats=stats)
        stateString = CYBERSPORT.WINDOW_UNIT_MESSAGE_INVALIDLEVELERROR_UNRESOLVED
        if len(vehLevels):
            stateStringCandidate = CYBERSPORT.window_unit_message_invalidlevelerror('_'.join(map(lambda level: str(level), vehLevels)))
            if stateStringCandidate is not None:
                stateString = stateStringCandidate
        return stateString
