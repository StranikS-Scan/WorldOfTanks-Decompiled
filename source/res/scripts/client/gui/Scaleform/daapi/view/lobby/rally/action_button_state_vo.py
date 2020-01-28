# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/action_button_state_vo.py
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.shared.formatters import text_styles, icons
from helpers import i18n
from shared_utils import BoundMethodWeakref

class ActionButtonStateVO(dict):
    __NOT_CRITICAL_STATES = (UNIT_RESTRICTION.UNDEFINED,
     UNIT_RESTRICTION.IS_IN_IDLE,
     UNIT_RESTRICTION.IS_IN_PRE_ARENA,
     UNIT_RESTRICTION.VEHICLE_NOT_VALID_FOR_EVENT,
     UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED)

    def __init__(self, unitEntity):
        super(ActionButtonStateVO, self).__init__()
        self._playerInfo = unitEntity.getPlayerInfo()
        result = unitEntity.canPlayerDoAction()
        self.__unitIsValid, self.__restrictionType = result.isValid, result.restriction
        self.__validationCtx = result.ctx
        self.__isEnabled = self._isEnabled(self.__unitIsValid, self.__restrictionType)
        self.__stats = unitEntity.getStats()
        self.__flags = unitEntity.getFlags()
        self.__settings = unitEntity.getRosterSettings()
        self.__canTakeSlot = not self._playerInfo.isLegionary()
        self.__INVALID_UNIT_MESSAGES = {UNIT_RESTRICTION.UNDEFINED: ('', {}),
         UNIT_RESTRICTION.UNIT_IS_FULL: (CYBERSPORT.WINDOW_UNIT_MESSAGE_UNITISFULL, {}),
         UNIT_RESTRICTION.UNIT_IS_LOCKED: (CYBERSPORT.WINDOW_UNIT_MESSAGE_UNITISLOCKED, {}),
         UNIT_RESTRICTION.VEHICLE_NOT_SELECTED: (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLENOTSELECTED, {}),
         UNIT_RESTRICTION.VEHICLE_NOT_VALID: (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLENOTVALID, {}),
         UNIT_RESTRICTION.VEHICLE_BROKEN: (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLEINNOTREADY_BROKEN, {}),
         UNIT_RESTRICTION.VEHICLE_CREW_NOT_FULL: (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLEINNOTREADY_CREWNOTFULL, {}),
         UNIT_RESTRICTION.VEHICLE_RENT_IS_OVER: (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLEINNOTREADY_RENTISOVER, {}),
         UNIT_RESTRICTION.VEHICLE_IS_IN_BATTLE: (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLEINNOTREADY_ISINBATTLE, {}),
         UNIT_RESTRICTION.MIN_SLOTS: (CYBERSPORT.WINDOW_UNIT_MESSAGE_MINSLOTS, {}),
         UNIT_RESTRICTION.NOT_READY_IN_SLOTS: (CYBERSPORT.WINDOW_UNIT_MESSAGE_WAITING, {}),
         UNIT_RESTRICTION.MIN_TOTAL_LEVEL: (CYBERSPORT.WINDOW_UNIT_MESSAGE_LEVEL, self.__validationCtx),
         UNIT_RESTRICTION.MAX_TOTAL_LEVEL: (CYBERSPORT.WINDOW_UNIT_MESSAGE_LEVEL, self.__validationCtx),
         UNIT_RESTRICTION.INVALID_TOTAL_LEVEL: ActionButtonStateVO.getInvalidVehicleLevelsMessage(self.__validationCtx),
         UNIT_RESTRICTION.IS_IN_IDLE: BoundMethodWeakref(self._getIdleStateStr),
         UNIT_RESTRICTION.IS_IN_ARENA: BoundMethodWeakref(self._getArenaStateStr),
         UNIT_RESTRICTION.NEED_PLAYERS_SEARCH: ('', {}),
         UNIT_RESTRICTION.ZERO_TOTAL_LEVEL: ('', {}),
         UNIT_RESTRICTION.IS_IN_PRE_ARENA: (CYBERSPORT.WINDOW_UNIT_MESSAGE_WAITCOMMANDER, {}),
         UNIT_RESTRICTION.NOT_IN_SLOT: BoundMethodWeakref(self._notInSlotMessage),
         UNIT_RESTRICTION.VEHICLE_NOT_VALID_FOR_EVENT: (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLENOTVALID, {}),
         UNIT_RESTRICTION.CURFEW: (CYBERSPORT.WINDOW_UNIT_MESSAGE_CURFEW, {}),
         UNIT_RESTRICTION.VEHICLE_WRONG_MODE: (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLEINNOTREADY_WRONGMODE, {}),
         UNIT_RESTRICTION.FORT_DISABLED: (CYBERSPORT.WINDOW_UNIT_MESSAGE_FORTIFICATIONNOTAVAILABLE, {}),
         UNIT_RESTRICTION.VEHICLE_INVALID_LEVEL: (self.__getNotAvailableIcon() + i18n.makeString(MESSENGER.DIALOGS_SQUAD_MESSAGE_INVALIDVEHICLELEVEL), {}),
         UNIT_RESTRICTION.SPG_IS_FORBIDDEN: (self.__getNotAvailableIcon() + i18n.makeString(MESSENGER.DIALOGS_SQUAD_MESSAGE_SPGFORBIDDEN), {}),
         UNIT_RESTRICTION.SPG_IS_FULL: (self.__getNotAvailableIcon() + i18n.makeString(MESSENGER.DIALOGS_SQUAD_MESSAGE_SPGFULL), {}),
         UNIT_RESTRICTION.ROTATION_GROUP_LOCKED: BoundMethodWeakref(self._rotationGroupBlockMessage),
         UNIT_RESTRICTION.UNIT_MAINTENANCE: (CYBERSPORT.WINDOW_UNIT_MESSAGE_MAINTENANCE, {}),
         UNIT_RESTRICTION.UNIT_INACTIVE_PERIPHERY_UNDEF: (CYBERSPORT.WINDOW_UNIT_MESSAGE_INACTIVEPERIPHERY, {}),
         UNIT_RESTRICTION.UNIT_INACTIVE_PERIPHERY_SORTIE: (CYBERSPORT.WINDOW_UNIT_MESSAGE_INACTIVEPERIPHERYSORTIE, {}),
         UNIT_RESTRICTION.UNIT_INACTIVE_PERIPHERY_BATTLE: (CYBERSPORT.WINDOW_UNIT_MESSAGE_INACTIVEPERIPHERYBATTLE, {}),
         UNIT_RESTRICTION.UNIT_WAITINGFORDATA: (TOOLTIPS.STRONGHOLDS_TIMER_WAITINGFORDATA, {}),
         UNIT_RESTRICTION.UNIT_MIN_CLAN_MEMBERS: BoundMethodWeakref(self._clanMembersNotEnoughMessage),
         UNIT_RESTRICTION.UNIT_IS_IN_PLAYERS_MATCHING: (CYBERSPORT.WINDOW_UNIT_MESSAGE_IN_PLAYERS_MATCHING, {}),
         UNIT_RESTRICTION.BOB_TEAM_MISMATCH: (CYBERSPORT.WINDOW_UNIT_MESSAGE_BOB_TEAM_MISMATCH, {}),
         UNIT_RESTRICTION.BOB_LEADER_FORBIDDEN: (CYBERSPORT.WINDOW_UNIT_MESSAGE_BOB_LEADER_FORBIDDEN, {})}
        self.__WARNING_UNIT_MESSAGES = {UNIT_RESTRICTION.XP_PENALTY_VEHICLE_LEVELS: (MESSENGER.DIALOGS_SQUAD_MESSAGE_VEHICLES_DIFFERENTLEVELS, {})}
        self.__NEUTRAL_UNIT_MESSAGES = {UNIT_RESTRICTION.UNIT_WILL_SEARCH_PLAYERS: (FORTIFICATIONS.UNIT_WINDOW_WILLSEARCHPLAYERS, {})}
        stateKey, stateCtx = self.__getState()
        self['stateString'] = self.__stateTextStyleFormatter(i18n.makeString(stateKey, **stateCtx))
        self['label'] = self._getLabel()
        self['isEnabled'] = self.__isEnabled
        self['isReady'] = self._playerInfo.isReady
        self['toolTipData'] = self.__toolTipData

    def __getNotAvailableIcon(self):
        return icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_REDNOTAVAILABLE, 12, 12, 0, 0) + ' '

    def _getReadyValidInSlotStateStr(self):
        return (CYBERSPORT.WINDOW_UNIT_MESSAGE_WAITING, {})

    def _getIdleStateStr(self):
        return (CYBERSPORT.WINDOW_UNIT_MESSAGE_READY, {})

    def _getArenaStateStr(self):
        return ('', {})

    def _isEnabled(self, isValid, restriction):
        return isValid

    def _getLabel(self):
        label = CYBERSPORT.WINDOW_UNIT_READY
        if self._playerInfo.isCommander():
            label = CYBERSPORT.WINDOW_UNIT_FIGHT
        if self._playerInfo.isReady and self.__restrictionType != UNIT_RESTRICTION.IS_IN_IDLE:
            label = CYBERSPORT.WINDOW_UNIT_NOTREADY
        return label

    def _rotationGroupBlockMessage(self):
        from CurrentVehicle import g_currentVehicle
        return (CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLEINNOTREADY_ROTATIONGROUPLOCKED, {'groupNum': g_currentVehicle.item.rotationGroupNum})

    def _notInSlotMessage(self):
        return (CYBERSPORT.WINDOW_UNIT_MESSAGE_CANDIDATE, {}) if self.__canTakeSlot else (CYBERSPORT.WINDOW_UNIT_MESSAGE_UNITISFULL, {})

    def _getUnitReadyMessage(self):
        return (CYBERSPORT.WINDOW_UNIT_MESSAGE_GETREADY, {})

    def __getState(self):
        if self.__isEnabled:
            if self._playerInfo.isInSlot:
                if self._playerInfo.isReady:
                    if self.__restrictionType in self.__WARNING_UNIT_MESSAGES:
                        return self.__WARNING_UNIT_MESSAGES[self.__restrictionType]
                    return self._getReadyValidInSlotStateStr()
                if self.__restrictionType in self.__NEUTRAL_UNIT_MESSAGES:
                    return self.__NEUTRAL_UNIT_MESSAGES[self.__restrictionType]
                return self._getUnitReadyMessage()
            if self.__canTakeSlot:
                return (CYBERSPORT.WINDOW_UNIT_MESSAGE_CANDIDATE, {})
            if self.__flags.isLocked():
                return (CYBERSPORT.WINDOW_UNIT_MESSAGE_UNITISLOCKED, {})
            return (CYBERSPORT.WINDOW_UNIT_MESSAGE_UNITISFULL, {})
        return self.__INVALID_UNIT_MESSAGES[self.__restrictionType]() if callable(self.__INVALID_UNIT_MESSAGES[self.__restrictionType]) else self.__INVALID_UNIT_MESSAGES[self.__restrictionType]

    @property
    def __toolTipData(self):
        if not self._playerInfo.isInSlot:
            return TOOLTIPS.CYBERSPORT_UNIT_FIGHTBTN_NOTINSLOT
        if self.__restrictionType == UNIT_RESTRICTION.VEHICLE_NOT_VALID:
            return TOOLTIPS.CYBERSPORT_UNIT_FIGHTBTN_VEHICLENOTVALID
        if self.__restrictionType == UNIT_RESTRICTION.VEHICLE_WRONG_MODE:
            return TOOLTIPS.CYBERSPORT_UNIT_FIGHTBTN_EVENTVEHICLEWRONGMODE
        if self.__isEnabled and not self._playerInfo.isReady:
            return TOOLTIPS.CYBERSPORT_UNIT_FIGHTBTN_PRESSFORREADY
        return TOOLTIPS.CYBERSPORT_UNIT_FIGHTBTN_PRESSFORNOTREADY if self.__isEnabled and self._playerInfo.isReady else ''

    def _clanMembersNotEnoughMessage(self):
        actualClanMembers = self.__stats.clanMembersInRoster
        minClanMembers = self.__settings.getMinClanMembersCount()
        return (FORTIFICATIONS.ROSTER_CLANMEMBERSNOTENOUGH, {'minClanMembers': minClanMembers,
          'actualClanMembers': actualClanMembers})

    def __stateTextStyleFormatter(self, state):
        if self.__restrictionType in self.__WARNING_UNIT_MESSAGES and self._playerInfo.isReady:
            return ' '.join((icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON, vSpace=-3), text_styles.alert(state)))
        if self.__restrictionType in self.__NEUTRAL_UNIT_MESSAGES:
            return text_styles.neutral(state)
        return text_styles.error(state) if self.__restrictionType not in self.__NOT_CRITICAL_STATES else text_styles.main(state)

    @staticmethod
    def getInvalidVehicleLevelsMessage(ctx):
        if ctx is None:
            return ('', {})
        else:
            vehLevels = ctx.get('vehLevels', ())
            stateString = CYBERSPORT.WINDOW_UNIT_MESSAGE_INVALIDLEVELERROR_UNRESOLVED
            if vehLevels:
                stateStringCandidate = CYBERSPORT.window_unit_message_invalidlevelerror('_'.join((str(l) for l in vehLevels)))
                if stateStringCandidate is not None:
                    stateString = stateStringCandidate
            return (stateString, {})
