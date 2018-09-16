# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/event_helpers.py
from io import BufferedIOBase, TextIOWrapper
from functools import wraps
import BigWorld
from ResMgr import DataSection
from constants import ARENA_GUI_TYPE, MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL
from debug_utils import LOG_ERROR, LOG_DEBUG
from helpers.i18n import makeString as _ms
from helpers import xmltodict, int2roman, dependency
from nations import NAMES as NationNames
from bonus_readers import readBonusSection
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.shared.utils.functions import makeTooltip
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from gui.server_events.bonuses import getEventBoardsBonusObj
from gui.event_boards import event_boards_timer
from gui.event_boards.event_boards_items import CALCULATION_METHODS as _cm, OBJECTIVE_PARAMETERS as _op, EVENT_TYPE as _et, PLAYER_STATE_REASON as _psr, EVENT_STATE as _es, EVENT_DATE_TYPE, WOODEN_RIBBON
from gui.Scaleform.genConsts.EVENTBOARDS_ALIASES import EVENTBOARDS_ALIASES
from gui.Scaleform.locale.EVENT_BOARDS import EVENT_BOARDS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_vos import makeCantJoinReasonTextVO, makeParameterTooltipVO, makePrimeTimesTooltipVO
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import formatVehicleNameWithTypeIcon, getNationEmblemIcon, getNationBigFlagIcon, getNationText, vehicleTypeText, formatTimeToEnd, formatErrorTextWithIcon, formatOkTextWithIcon, formatTimeAndDate, formatUpdateTime, formatAllertTextWithIcon, formatAttentionTextWithIcon, timeEndStyle, getLevelBackgroundIcon
from gui import GUI_NATIONS
from helpers.time_utils import ONE_MINUTE
LEVELS_RANGE = range(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1)

class _Task(object):

    def __init__(self, event):
        super(_Task, self).__init__()
        self._event = event

    def getInfo(self):
        raise NotImplementedError

    def getTooltip(self):
        return NotImplementedError


class _ObjectiveTask(_Task):
    _tooltipParameterMap = {_op.ORIGINALXP: TOOLTIPS.ELEN_TASK_OBJECTIVE_ORIGINALXP,
     _op.XP: TOOLTIPS.ELEN_TASK_OBJECTIVE_XP,
     _op.DAMAGEDEALT: None,
     _op.DAMAGEASSISTED: None,
     _op.WINS: None}

    def getInfo(self):
        event = self._event
        method = event.getMethod()
        parameter = event.getObjectiveParameter()
        maxOrSum = 'max' if method == _cm.MAX else 'sum'
        return text_styles.main(_ms(EVENT_BOARDS.task_objective_all(maxOrSum, parameter)))

    def getTooltip(self):
        parameter = self._event.getObjectiveParameter()
        return makeTooltip(body=self._tooltipParameterMap[parameter])


class _SelectionTask(_Task):
    selectionWithCardinality = (_cm.SUMSEQN, _cm.SUMN, _cm.SUMMSEQN)

    def getInfo(self):
        event = self._event
        method = event.getMethod()
        result = _ms(EVENT_BOARDS.task_selection(method))
        if method in self.selectionWithCardinality:
            cardinality = event.getCardinality()
            distance = event.getDistance()
            result = result % {'cardinality': str(cardinality),
             'distance': str(distance)}
        return text_styles.main(result)

    def getTooltip(self):
        event = self._event
        method = event.getMethod()
        result = _ms(TOOLTIPS.elen_task_selection(method))
        if method in self.selectionWithCardinality:
            cardinality = event.getCardinality()
            distance = event.getDistance()
            result = result % {'cardinality': str(cardinality),
             'distance': str(distance)}
        return makeTooltip(body=result)


class _EventTypeTask(_Task):

    def getInfo(self):
        eventType = self._event.getType()
        return text_styles.main(_ms(EVENT_BOARDS.task_eventtype(eventType)))

    def getTooltip(self):
        eventType = self._event.getType()
        limits = self._event.getLimits()
        if eventType == _et.NATION:
            nationsList = limits.getNations()
            full = set(NationNames) == set(nationsList)
            nations = ', \n'.join([ getNationText(value) for value in GUI_NATIONS if value in nationsList ])
            result = TOOLTIPS.elen_task_eventtype_full(eventType) if full else _ms(TOOLTIPS.elen_task_eventtype_notfull(eventType), nations=nations)
        elif eventType == _et.CLASS:
            typeList = limits.getVehiclesClasses()
            full = set(VEHICLE_CLASS_NAME.ALL()) == set(typeList)
            types = ', \n'.join([ vehicleTypeText(value) for value in typeList ])
            result = TOOLTIPS.elen_task_eventtype_full(eventType) if full else _ms(TOOLTIPS.elen_task_eventtype_notfull(eventType), classes=types)
        elif eventType == _et.LEVEL:
            levelList = limits.getVehiclesLevels()
            full = set(LEVELS_RANGE) == set(limits.getVehiclesLevels())
            levels = ', '.join([ int2roman(value) for value in levelList ])
            result = TOOLTIPS.elen_task_eventtype_full(eventType) if full else _ms(TOOLTIPS.elen_task_eventtype_notfull(eventType), levels=levels)
        else:
            result = _ms(TOOLTIPS.elen_task_eventtype_notfull(eventType))
        return makeTooltip(body=result)


class _Condition(object):

    def __init__(self, event):
        super(_Condition, self).__init__()
        self._event = event

    def getInfo(self):
        raise NotImplementedError

    def getTooltip(self):
        return NotImplementedError


class _BattleTypeCondition(_Condition):

    def getInfo(self):
        cType = _ms(EVENT_BOARDS.CONDITION_BATTLETYPE_RANDOM)
        squadAlloweed = self._event.getIsSquadAllowed()
        squadInfo = _ms(EVENT_BOARDS.CONDITION_BATTLETYPE_SQUADALLOWED) if squadAlloweed else _ms(EVENT_BOARDS.CONDITION_BATTLETYPE_SQUADNOTALLOWED)
        return text_styles.main('{0}. {1}'.format(cType, squadInfo))

    def getTooltip(self):
        return makeTooltip(body=TOOLTIPS.ELEN_CONDITION_BATTLETYPE_RANDOM) if self._event.getBattleType() == ARENA_GUI_TYPE.RANDOM else makeTooltip(body=TOOLTIPS.ELEN_CONDITION_BATTLETYPE_NOTRANDOM)


class _PrimeTimeCondition(_Condition):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _connectionMgr = dependency.descriptor(IConnectionManager)

    def getInfo(self):
        primeTimes = self._event.getPrimeTimes().getPrimeTimes()
        count = len(primeTimes)
        if count is 0:
            result = _ms(EVENT_BOARDS.CONDITION_PRIMETIME_ANY)
        elif count is 1:
            pt = primeTimes[0]
            periphery = int(pt.getServer())
            name = self._lobbyContext.getPeripheryName(periphery, False)
            result = '{0} {1}-{2}'.format(name, pt.getStartLocalTime(), pt.getEndLocalTime())
        else:
            result = _ms(EVENT_BOARDS.CONDITION_PRIMETIME_CHOSEN)
        return text_styles.main(result)

    def getTooltip(self):
        primeTimes = self._event.getPrimeTimes().getPrimeTimes()
        currentPeripheryID = self._connectionMgr.peripheryID
        showTooltip = len(primeTimes) > 1
        return makePrimeTimesTooltipVO(primeTimes, currentPeripheryID, self._lobbyContext.getPeripheryName) if showTooltip else None


class _VehiclesCondition(_Condition):
    itemsCache = dependency.descriptor(IItemsCache)

    def getInfo(self):
        info = _ms(EVENT_BOARDS.CONDITION_VEHICLE_CHOSEN)
        vehicles = self._event.getLimits().getVehiclesWhiteList()
        allCount = len(vehicles)
        available = 0
        availableVehicle = None
        items = self.itemsCache.items
        for vehCD in vehicles:
            if items.doesVehicleExist(vehCD):
                vehicle = items.getItemByCD(vehCD)
                if vehicle.isInInventory:
                    availableVehicle = vehicle
                    available += 1

        singleVehicle = allCount is 1
        vehicleMissing = available is 0
        if singleVehicle:
            vehicle = availableVehicle or items.getItemByCD(vehicles[0])
            vehicleName = formatVehicleNameWithTypeIcon(vehicle, 'html_templates:lobby/elen/objective')
            result = _ms(EVENT_BOARDS.CONDITION_VEHICLE_SINGLE, vehicle=vehicleName)
            if vehicleMissing:
                result = '{}. {}'.format(result, text_styles.error(_ms(EVENT_BOARDS.CONDITION_VEHICLE_MISSING)))
            else:
                result = '{}. {}'.format(result, _ms(EVENT_BOARDS.CONDITION_VEHICLE_EXIST))
        else:
            myCount = text_styles.error(str(available)) if vehicleMissing else text_styles.neutral(str(available))
            result = '{} {}/{}'.format(info, myCount, allCount)
        return text_styles.main(result)

    def getTooltip(self):
        return None


class _TopLeaderboard(object):

    def __init__(self, event, top):
        super(_TopLeaderboard, self).__init__()
        self.itemsCache = dependency.instance(IItemsCache)
        self._event = event
        self._top = top
        self.__eventType = event.getType()
        self.__leaderboardId = self._top.getLeaderboardID()
        self.__value = event.getLeaderboard(self.__leaderboardId)
        self.__rewardByRank = self._event.getRewardsByRank().getRewardByRank(self.__leaderboardId)
        cardinality = event.getCardinality()
        leaderboardViewSize = event.getLeaderboardViewSize()
        myPosition = top.getMyPosition()
        battleCount = top.getBattlesCount()
        self.__notFull = cardinality is not None and battleCount < cardinality
        self.__notInTop = myPosition is None or myPosition > leaderboardViewSize
        return

    def getValue(self):
        return self.__value

    def getInfo(self):
        top = self._top
        reward = self._event.getRewardsByRank().getRewardByRank(self.__leaderboardId)
        category = reward.getRewardCategoryNumber(top.getMyPosition())
        return {'eventID': top.getEventID(),
         'title': text_styles.highlightText(self.__getTitle()),
         'isAvailable': True,
         'ribbonTooltip': self.__getRibbonTooltip(),
         'descriptionTooltip': self.__getDescriptionTooltip(),
         'amountTooltip': self.__getAmountTooltip(),
         'awards': None,
         'ribbon': self.__getRibbon(),
         'status': None,
         'background': 'marathon' if category else 'default',
         'amount': str(top.getMyValue()),
         'type': self.__getRaitingType(),
         'description1': self.__getMyPosititon(),
         'description2': self.__getStatusValue(),
         'uiDecoration': self.__getDecoration(),
         'uiPicture': self.__getPicture(),
         'cardID': str(top.getLeaderboardID())}

    def __getTitle(self):
        if self.__eventType == _et.NATION:
            return getNationText(self.__value)
        if self.__eventType == _et.VEHICLE:
            items = self.itemsCache.items
            vehicle = items.getItemByCD(self.__value)
            return formatVehicleNameWithTypeIcon(vehicle, 'html_templates:lobby/elen/top')
        if self.__eventType == _et.CLASS:
            return vehicleTypeText(self.__value)
        return _ms(EVENT_BOARDS.VEHICLES_LEVEL, level=int2roman(self.__value)) if self.__eventType == _et.LEVEL else 'ERROR'

    def __getDecoration(self):
        if self.__eventType == _et.NATION:
            return getNationBigFlagIcon(self.__value, False)
        elif self.__eventType == _et.VEHICLE:
            items = self.itemsCache.items
            vehicle = items.getItemByCD(self.__value)
            return getNationBigFlagIcon(vehicle.nationName, True)
        else:
            return getLevelBackgroundIcon() if self.__eventType in (_et.LEVEL, _et.CLASS) else None

    def __getRibbonTooltip(self):
        category = self.__rewardByRank.getRewardCategoryNumber(self._top.getMyPosition())
        if category:
            minimum, maximum = self.__rewardByRank.getCategoryMinMax(category)
            return makeTooltip(body=_ms(EVENT_BOARDS.TOOLTIP_TOP_REWARDGROUP, group=int2roman(category), min=minimum, max=maximum))
        method = self._event.getMethod()
        amount = self._top.getLastInLeaderboardValue()
        parameter = self._event.getObjectiveParameter()
        return makeParameterTooltipVO(method, amount, parameter)

    def __getDescriptionTooltip(self):
        category = self.__rewardByRank.getRewardCategoryNumber(self._top.getMyPosition())
        if category is not None:
            return
        else:
            method = self._event.getMethod()
            amount = self._top.getLastInLeaderboardValue()
            parameter = self._event.getObjectiveParameter()
            return makeParameterTooltipVO(method, amount, parameter)

    def __getAmountTooltip(self):
        parametersWithTooltip = [_op.ORIGINALXP, _op.XP]
        parameter = self._event.getObjectiveParameter()
        return makeTooltip(body=_ms(EVENT_BOARDS.tooltip_top_amount(parameter))) if parameter in parametersWithTooltip else None

    def __getPicture(self):
        if self.__eventType == _et.NATION:
            return getNationEmblemIcon(self.__value)
        elif self.__eventType == _et.CLASS:
            return RES_ICONS.getEventBoardVehicleClass(self.__value)
        elif self.__eventType == _et.LEVEL:
            return RES_ICONS.getEventBoardVehicleLevel(self.__value)
        elif self.__eventType == _et.VEHICLE:
            vehicle = self.itemsCache.items.getItemByCD(self.__value)
            name = vehicle.name.split(':', 1)[-1].lower()
            return RES_ICONS.getEventBoardTank(name) or RES_ICONS.MAPS_ICONS_EVENTBOARDS_TANKS_DEFAULT_IMAGE
        else:
            return None

    def __getRaitingType(self):
        method = self._event.getMethod()
        op = self._event.getObjectiveParameter()
        return _ms(TOOLTIPS.elen_excel_objparam_all_all_header(method, op))

    def __getRibbon(self):
        rank = self._top.getMyPosition()
        rewards = self._event.getRewardsByRank().getRewardByRank(self.__leaderboardId)
        ribbon = rewards.getRewardCategoryNumber(rank)
        return WOODEN_RIBBON if ribbon is None and rank <= self._event.getLeaderboardViewSize() else ribbon

    def __getMyPosititon(self):
        event = self._event
        if event.isFinished() and self.__notFull:
            return text_styles.neutral(_ms(EVENT_BOARDS.TOP_PARTICIPATION_NOTPARTICIPATED))
        if self.__notFull:
            return text_styles.neutral(_ms(EVENT_BOARDS.TOP_PARTICIPATION_NOTFULL))
        return text_styles.neutral(_ms(EVENT_BOARDS.TOP_PARTICIPATION_NOTINTOP)) if self.__notInTop else text_styles.main('{} {}'.format(_ms(EVENT_BOARDS.TOP_POSITION), self._top.getMyPosition()))

    def __getStatusValue(self):
        event = self._event
        if self.__notFull and not event.isFinished():
            count = text_styles.stats(str(event.getCardinality() - self._top.getBattlesCount()))
            text = text_styles.standard(_ms(EVENT_BOARDS.TOP_REASON_NOTFULL))
            return '{} {}'.format(text, count)
        else:
            return None


class EventInfo(object):
    _connectionMgr = dependency.descriptor(IConnectionManager)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, event, playerData, eventsTop):
        eventID = event.getEventID()
        self._event = event
        self._playerData = playerData
        playerState = playerData.getPlayerStateByEventId(eventID)
        self._playerState = playerState
        top = eventsTop.getMyEventTop(eventID)
        self._top = top
        self._topMeta = eventsTop.getMyEventsTopMeta(eventID)
        self.topInfos = [ _TopLeaderboard(self._event, top) for top in self._top ]
        self._objectiveTask = _ObjectiveTask(event)
        self._selectionTask = _SelectionTask(event)
        self._eventTypeTask = _EventTypeTask(event)
        self._battleTypeCondition = _BattleTypeCondition(event)
        self._primeTimeCondition = _PrimeTimeCondition(event)
        self._vehiclesCondition = _VehiclesCondition(event)
        self._state = playerState.getPlayerState() if playerState else None
        self._stateReasons = playerState.getPlayerStateReasons() if playerState else []
        self._canJoin = playerState.getCanJoin() if playerState else True
        self._joined = self._state is _es.JOINED
        return

    def getTopInfo(self):
        return [ top.getInfo() for top in self.topInfos ]

    def getTaskInfo(self):
        return {'title': text_styles.highTitle(_ms(EVENT_BOARDS.BLOCK_TASK)),
         'uiIcon1': self.__getTaskIcon(1),
         'uiIcon2': self.__getTaskIcon(2),
         'uiIcon3': self.__getTaskIcon(3),
         'description1': self._objectiveTask.getInfo(),
         'description2': self._selectionTask.getInfo(),
         'description3': self._eventTypeTask.getInfo(),
         'label': _ms(EVENT_BOARDS.BUTTON_REGULATIONS),
         'buttonTooltip': makeTooltip(EVENT_BOARDS.BUTTON_REGULATIONS, EVENT_BOARDS.BUTTON_REGULATIONS_TOOLTIP),
         'description1Tooltip': self._objectiveTask.getTooltip(),
         'description2Tooltip': self._selectionTask.getTooltip(),
         'description3Tooltip': self._eventTypeTask.getTooltip(),
         'buttonVisible': bool(self._event.getManual())}

    def getConditionInfo(self):
        return {'title': text_styles.highTitle(_ms(EVENT_BOARDS.BLOCK_OBJECTIVE)),
         'uiIcon1': self.__getConditionIcon(1),
         'uiIcon2': self.__getConditionIcon(2),
         'uiIcon3': self.__getConditionIcon(3),
         'description1': self._battleTypeCondition.getInfo(),
         'description2': self._primeTimeCondition.getInfo(),
         'description3': self._vehiclesCondition.getInfo(),
         'label': _ms(EVENT_BOARDS.VEHICLES_VEHICLE),
         'buttonTooltip': makeTooltip(EVENT_BOARDS.VEHICLES_VEHICLE, EVENT_BOARDS.VEHICLES_VEHICLE_TOOLTIP),
         'description1Tooltip': self._battleTypeCondition.getTooltip(),
         'description2Tooltip': self._primeTimeCondition.getTooltip(),
         'description3Tooltip': self._vehiclesCondition.getTooltip(),
         'buttonVisible': bool(len(self._event.getLimits().getVehiclesWhiteList()) > 1)}

    def getAwardInfo(self):
        return {'title': text_styles.highTitle(_ms(EVENT_BOARDS.BLOCK_AWARD)),
         'label': _ms(EVENT_BOARDS.BUTTON_AWARDS),
         'buttonTooltip': makeTooltip(EVENT_BOARDS.BUTTON_AWARDS, EVENT_BOARDS.BUTTON_AWARDS_TOOLTIP),
         'iconTooltip': makeTooltip(body=EVENT_BOARDS.TOOLTIP_AWARDICON),
         'uiIcon': self._event.getPromoBonuses()}

    def isRegistration(self):
        event = self._event
        isRegistrationFinished = event.isRegistrationFinished()
        return not self._joined and self._canJoin and not isRegistrationFinished

    def getServerData(self):
        event = self._event
        finished = event.isFinished()
        peripheryID = str(self._connectionMgr.peripheryID)
        primeTimes = event.getPrimeTimes().getPrimeTimes()
        availableServers = event.getAvailableServers()
        isAvailableServer = event.isAvailableServer(peripheryID)
        isAvailableAnyServer = any(availableServers)
        title = formatAllertTextWithIcon(text_styles.alert(EVENT_BOARDS.SERVER_LIST))
        result = {}
        if not finished and not self._canJoin and _psr.SPECIALACCOUNT in self._stateReasons:
            result = {'reloginBlock': {'title': formatAllertTextWithIcon(text_styles.alert(EVENT_BOARDS.STATUS_CANTJOIN_REASON_SPECIAL)),
                              'description': ''},
             'isRelogin': True}
            return result
        if finished or event.getPrimeTimes().isEmpty():
            return result
        availableServers = sorted(availableServers, key=lambda p: int(p.getServer()))
        if not isAvailableServer and isAvailableAnyServer and self._playerState.getPlayerState() == _es.JOINED:
            buttons = [ {'label': str(self._lobbyContext.getPeripheryName(int(pt.getServer()), False)),
             'server': pt.getServer(),
             'tooltip': makeTooltip(self._lobbyContext.getPeripheryName(int(pt.getServer()), False), TOOLTIPS.ELEN_BUTTON_SERVER_BODY)} for pt in availableServers ]
            result = {'serverBlock': {'title': title,
                             'buttons': buttons},
             'isUnsuitableServer': True}
        elif not isAvailableServer and self._playerState.getPlayerState() == _es.JOINED:
            primeTime = min(primeTimes, key=lambda pt: pt.timeToActive())
            server = str(self._lobbyContext.getPeripheryName(int(primeTime.getServer()), False))
            nonSuitableServer = text_styles.neutral(_ms(EVENT_BOARDS.SERVER_NOSUITABLE_SERVER, time=primeTime.getStartLocalTime(), server=server))
            description = text_styles.main(_ms(EVENT_BOARDS.SERVER_NOSUITABLE_BODY, data=nonSuitableServer))
            result = {'reloginBlock': {'title': EVENT_BOARDS.SERVER_NOSUITABLE_HEADER,
                              'description': description,
                              'descriptionTooltip': self.__getPrimeTimesTooltip()},
             'isRelogin': True}
        return result

    def getStatusData(self):
        event = self._event
        playerData = self._playerData
        anyTops = any(self.topInfos)
        title = ''
        registrationTooltip = ''
        description1 = ''
        description2 = ''
        isRegistration = self.isRegistration()
        isRegistrationButtonEnabled = True
        isRegistrationTop = False
        started = self._event.isStarted()
        titleTooltip = None
        buttonRegistrationLabel = ''
        description1Tooltip = ''
        description2Tooltip = ''
        if event.isFinished() and not anyTops:
            title = text_styles.main(EVENT_BOARDS.STATUS_PARTICIPATE_NOTPARTICIPATED)
        elif self._joined:
            title = text_styles.highTitle(EVENT_BOARDS.STATUS_BESTRESULTS_MANY)
            if self._topMeta:
                recalculationTS = self._topMeta.getLastLeaderboardRecalculationTS()
                if recalculationTS is not None:
                    if not event.isFinished():
                        description1 = text_styles.standard(formatUpdateTime(recalculationTS))
                    recalculationInterval = self._topMeta.getRecalculationInterval()
                    if recalculationInterval is not None:
                        interval = int(recalculationInterval / ONE_MINUTE)
                        description1Tooltip = makeTooltip(_ms(TOOLTIPS.SUMMARY_STATUS_TOOLTIP, interval=interval))
            if not anyTops:
                description2 = formatAttentionTextWithIcon(text_styles.neutral(EVENT_BOARDS.STATUS_PARTICIPATE_NEEDMOREBATTLES))
        elif not self._canJoin:
            title, titleTooltip, isRegistration = makeCantJoinReasonTextVO(event, playerData)
            if _psr.SPECIALACCOUNT in self._stateReasons or _psr.WASUNREGISTERED in self._stateReasons:
                title = ''
                titleTooltip = None
            buttonRegistrationLabel = EVENT_BOARDS.EXCEL_PARTICIPATE_JOIN
            isRegistrationButtonEnabled = False
        else:
            isRegistrationTop = True
            if started:
                buttonRegistrationLabel = EVENT_BOARDS.EXCEL_PARTICIPATE_JOIN
                registrationTooltip = TOOLTIPS.ELEN_BUTTON_REGISTRATION_STARTED
            else:
                buttonRegistrationLabel = EVENT_BOARDS.TABLE_SELECTREGISTRATIONBTN
                registrationTooltip = TOOLTIPS.ELEN_BUTTON_REGISTRATION_NOTSTARTED
        return {'title': title,
         'description1': description1,
         'description2': description2,
         'isRegistrationTop': isRegistrationTop,
         'isRegistration': isRegistration,
         'isRegistrationEnabled': isRegistrationButtonEnabled,
         'registrationTooltip': registrationTooltip,
         'titleTooltip': titleTooltip,
         'ratingTooltip': makeTooltip(TOOLTIPS.ELEN_BUTTON_RAITING_HEADER, TOOLTIPS.ELEN_BUTTON_RAITING_BODY),
         'isRating': started,
         'buttonRegistrationLabel': buttonRegistrationLabel,
         'description1Tooltip': description1Tooltip,
         'description2Tooltip': description2Tooltip}

    def getPopoverAlias(self):
        return EVENTBOARDS_ALIASES.RESULT_FILTER_POPOVER_VEHICLES_ALIAS if self._event.getType() == _et.VEHICLE else EVENTBOARDS_ALIASES.RESULT_FILTER_POPOVER_ALIAS

    def __getTaskIcon(self, iconNum):
        method = self._event.getMethod()
        if iconNum == 1:
            parameter = self._event.getObjectiveParameter()
            if parameter == _op.WINS:
                return RES_ICONS.MAPS_ICONS_EVENTBOARDS_LANDINGICONS_SIGNIFICATIVE_WINS_COUNT
            parameter = 'xp' if parameter == _op.ORIGINALXP else parameter
            maxOrSum = 'max' if method == _cm.MAX else 'sum'
            return RES_ICONS.getEventBoardSignificative(parameter, maxOrSum)
        elif iconNum == 2:
            cardinality = self._event.getCardinality()
            if method == _cm.SUMMSEQN:
                return RES_ICONS.MAPS_ICONS_EVENTBOARDS_LANDINGICONS_EVENTTYPE_BATTLE_M_N
            if method == _cm.MAX:
                return RES_ICONS.MAPS_ICONS_EVENTBOARDS_LANDINGICONS_EVENTTYPE_BATTLE_1
            if cardinality is None or cardinality <= 0 or cardinality > 20:
                return RES_ICONS.MAPS_ICONS_EVENTBOARDS_LANDINGICONS_EVENTTYPE_BATTLE_SUM
            return RES_ICONS.getEventBoardBattleNum(cardinality)
        else:
            eventType = self._event.getType()
            return RES_ICONS.getEventBoardRating(eventType)

    def __getConditionIcon(self, iconNum):
        if iconNum == 1:
            bt = self._event.getBattleType()
            if bt == ARENA_GUI_TYPE.RANKED:
                return RES_ICONS.MAPS_ICONS_EVENTBOARDS_LANDINGICONS_CONDITIONS_RANKED_BATTLE
            return RES_ICONS.MAPS_ICONS_EVENTBOARDS_LANDINGICONS_CONDITIONS_RANDOM_BATTLE
        elif iconNum == 2:
            return RES_ICONS.MAPS_ICONS_EVENTBOARDS_LANDINGICONS_CONDITIONS_SERVER
        else:
            return RES_ICONS.MAPS_ICONS_EVENTBOARDS_LANDINGICONS_CONDITIONS_VEHICLE

    def __getPrimeTimesTooltip(self):
        primeTimes = self._event.getPrimeTimes().getPrimeTimes()
        currentPeripheryID = self._connectionMgr.peripheryID
        return makePrimeTimesTooltipVO(primeTimes, currentPeripheryID, self._lobbyContext.getPeripheryName)


class EventHeader(object):
    _cantJoinReason = {_psr.BYWINRATE: EVENT_BOARDS.HEADER_PARTICIPATE_REASON_CANTJOIN,
     _psr.BYAGE: EVENT_BOARDS.HEADER_PARTICIPATE_REASON_CANTJOIN,
     _psr.BYBATTLESCOUNT: EVENT_BOARDS.HEADER_PARTICIPATE_REASON_CANTJOIN,
     _psr.BYBAN: EVENT_BOARDS.HEADER_PARTICIPATE_REASON_CANTJOIN,
     _psr.WASUNREGISTERED: EVENT_BOARDS.HEADER_PARTICIPATE_REASON_LEFTEVENT,
     _psr.SPECIALACCOUNT: EVENT_BOARDS.HEADER_PARTICIPATE_REASON_CANTJOIN,
     _psr.VEHICLESMISSING: EVENT_BOARDS.HEADER_PARTICIPATE_REASON_CANTJOIN}

    def __init__(self, event, playerData):
        self._event = event
        self._playerData = playerData
        playerState = playerData.getPlayerStateByEventId(event.getEventID())
        if playerState is not None:
            self._playerState = playerState
            self._state = playerState.getPlayerState()
            self._joined = self._state is _es.JOINED
            self._stateReasons = playerState.getPlayerStateReasons()
            self._canJoin = playerState.getCanJoin() and (not event.isRegistrationFinished() or not event.isFinished())
        else:
            self._playerState = None
            self._state = None
            self._canJoin = False
            self._joined = False
            self._stateReasons = []
        return

    def getInfo(self):
        result = self.getTimerInfo()
        result.update(self.getParticipateInfo())
        return result

    def getTimerInfo(self):

        def formatToEnd(iconPath, text, dateType, isEndSoon):
            iconPath = icons.makeImageTag(iconPath)
            timeData = event.getFormattedRemainingTime(dateType)
            text = _ms(text, time=formatTimeToEnd(timeData[0], timeData[1]))
            if isEndSoon:
                formatedText = timeEndStyle(text)
            else:
                formatedText = text_styles.vehicleStatusInfoText(text)
            return '{} {}'.format(iconPath, formatedText)

        event = self._event
        sday, smonth, _ = event_boards_timer.getDayMonthYear(event.getStartDate())
        eday, emonth, _ = event_boards_timer.getDayMonthYear(event.getEndDate())
        finished = event.isFinished()
        if not finished:
            icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_DATE_ICON)
            timePeriod = '{} {} {} - {} {} {}'.format(str(sday), _ms(MENU.datetime_months(str(smonth))), event_boards_timer.getShortTimeString(event.getStartDate()), str(eday), _ms(MENU.datetime_months(str(emonth))), event_boards_timer.getShortTimeString(event.getEndDate()))
            result = '{} {}    '.format(icon, text_styles.vehicleStatusInfoText(timePeriod))
            startSoon = event.isStartSoon()
            if startSoon:
                result += formatToEnd(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_TIME_ICON, EVENT_BOARDS.TIME_TIMETO_START, EVENT_DATE_TYPE.START, startSoon)
            elif not self._joined and not event.isRegistrationFinished():
                finishSoon = event.isRegistrationFinishSoon()
                if finishSoon:
                    result += formatToEnd(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_TIME_ICON, EVENT_BOARDS.TIME_TIMETO_ENDREGISTRATION, EVENT_DATE_TYPE.PARTICIPANTS_FREEZE, finishSoon)
                else:
                    result += formatToEnd(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_ICON_FLAG, EVENT_BOARDS.TIME_TIMETO_ENDREGISTRATION, EVENT_DATE_TYPE.PARTICIPANTS_FREEZE, finishSoon)
            else:
                endSoon = event.isEndSoon()
                if endSoon:
                    result += formatToEnd(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_TIME_ICON, EVENT_BOARDS.TIME_TIMETO_END, EVENT_DATE_TYPE.END, endSoon)
                else:
                    result += formatToEnd(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_ICON_FLAG, EVENT_BOARDS.TIME_TIMETO_END, EVENT_DATE_TYPE.END, endSoon)
        else:
            date = BigWorld.wg_getLongDateFormat(event.getEndDateTs())
            result = text_styles.main(_ms(EVENT_BOARDS.TIME_EVENTFINISHED, date=date))
        return {'timer': result}

    def getParticipateInfo(self):
        event = self._event
        playerData = self._playerData
        started = event.isStarted()
        isRegistrationFinished = event.isRegistrationFinished()
        participateTooltip = None
        buttonTooltip = None
        participate = ''
        buttonLabel = ''
        title = ''
        titleTooltip = ''
        isButton = False
        isButtonRegistration = not self._joined and self._canJoin and not isRegistrationFinished
        isButtonEnabled = True
        isButtonRegistrationEnabled = True
        dateTs = event.getParticipantsFreezeDeadlineTs()
        date = formatTimeAndDate(dateTs)
        if event.isFinished():
            return {}
        else:
            if started:
                buttonRegistrationLabel = EVENT_BOARDS.EXCEL_PARTICIPATE_JOIN
                buttonRegistrationTooltip = makeTooltip(TOOLTIPS.ELEN_BUTTON_REGISTRATION_STARTED_HEADER, TOOLTIPS.ELEN_BUTTON_REGISTRATION_STARTED_BODY)
            else:
                buttonRegistrationLabel = EVENT_BOARDS.TABLE_SELECTREGISTRATIONBTN
                buttonRegistrationTooltip = makeTooltip(TOOLTIPS.ELEN_BUTTON_REGISTRATION_NOTSTARTED_HEADER, TOOLTIPS.ELEN_BUTTON_REGISTRATION_NOTSTARTED_BODY)
            if self._joined:
                isButton = True
                buttonLabel = EVENT_BOARDS.HEADER_PARTICIPATE_BUTTON_LEAVE
                if isRegistrationFinished:
                    participate = formatOkTextWithIcon(EVENT_BOARDS.HEADER_PARTICIPATE_STARTED)
                    participateTooltip = makeTooltip(EVENT_BOARDS.STATUS_CANTJOIN_REASON_ENDREGISTRATION, TOOLTIPS.ELEN_BUTTON_HEADER_PARTICIPATE_CANTLEAVE_HEADER)
                    buttonTooltip = makeTooltip(TOOLTIPS.ELEN_BUTTON_HEADER_PARTICIPATE_LEAVE_HEADER, _ms(TOOLTIPS.ELEN_BUTTON_HEADER_PARTICIPATE_CANTLEAVE_BODY, date=date))
                    isButtonEnabled = False
                    isButtonRegistrationEnabled = False
                elif started:
                    participate = formatOkTextWithIcon(EVENT_BOARDS.HEADER_PARTICIPATE_STARTED)
                    participateTooltip = makeTooltip(TOOLTIPS.ELEN_HEADER_PARTICIPATE_STARTED_HEADER, TOOLTIPS.ELEN_HEADER_PARTICIPATE_STARTED_BODY)
                    buttonTooltip = makeTooltip(TOOLTIPS.ELEN_BUTTON_HEADER_PARTICIPATE_LEAVE_HEADER, _ms(TOOLTIPS.ELEN_BUTTON_HEADER_PARTICIPATE_LEAVE_BODY, date=date))
                else:
                    participate = formatOkTextWithIcon(EVENT_BOARDS.HEADER_PARTICIPATE_NOTSTARTED)
                    participateTooltip = makeTooltip(TOOLTIPS.ELEN_HEADER_PARTICIPATE_NOTSTARTED_HEADER, TOOLTIPS.ELEN_HEADER_PARTICIPATE_NOTSTARTED_BODY)
                    buttonTooltip = makeTooltip(TOOLTIPS.ELEN_HEADER_PARTICIPATE_BUTTON_LEAVENOTSTARTED_HEADER, _ms(TOOLTIPS.ELEN_HEADER_PARTICIPATE_BUTTON_LEAVENOTSTARTED_BODY, date=date))
            elif isRegistrationFinished:
                participate = formatErrorTextWithIcon(EVENT_BOARDS.STATUS_CANTJOIN_REASON_ENDREGISTRATION)
                participateTooltip = makeTooltip(EVENT_BOARDS.STATUS_CANTJOIN_REASON_ENDREGISTRATION, EVENT_BOARDS.STATUS_CANTJOIN_REASON_ENDREGISTRATION_TOOLTIP)
                isButtonEnabled = False
                isButtonRegistrationEnabled = False
            elif not self._canJoin:
                if self._stateReasons:
                    title, titleTooltip, isButtonRegistration = makeCantJoinReasonTextVO(event, playerData)
                    if _psr.SPECIALACCOUNT in self._stateReasons or _psr.WASUNREGISTERED in self._stateReasons:
                        title = ''
                        titleTooltip = None
                    elif _psr.WASUNREGISTERED in self._stateReasons:
                        participateTooltip = makeTooltip(EVENT_BOARDS.STATUS_CANTJOIN_REASON_LEFTEVENT, EVENT_BOARDS.STATUS_CANTJOIN_REASON_LEFTEVENT_TOOLTIP)
                    isButtonRegistrationEnabled = False
                    reasonText = self._cantJoinReason[self._stateReasons[0]]
                    participate = formatErrorTextWithIcon(reasonText)
            result = {'participate': participate,
             'participateTooltip': participateTooltip,
             'buttonLabel': buttonLabel,
             'buttonTooltip': buttonTooltip,
             'isButton': isButton,
             'isButtonEnabled': isButtonEnabled,
             'eventID': event.getEventID(),
             'title': title,
             'isButtonRegistration': isButtonRegistration,
             'isButtonRegistrationEnabled': isButtonRegistrationEnabled,
             'titleTooltip': titleTooltip,
             'buttonRegistrationTooltip': buttonRegistrationTooltip,
             'buttonRegistrationLabel': buttonRegistrationLabel}
            return result


BONUS_PRIORITY = ('gold', 'crystal', 'tokens', 'battleToken', 'vehicles', 'badgesGroup', 'dossier', 'lootbox', 'credits', 'items', 'goodies', 'customizations', 'tankmen', 'premium', 'slots', 'berths')

def _readEventBoardsRewards(rewards):
    badgesGroupData = rewards.pop('badgesGroup', None)
    return {'badgesGroup': int(badgesGroupData['value'])} if badgesGroupData is not None else {}


class CustomXMLGenerator(xmltodict.XMLGenerator):

    def __init__(self, out=None, encoding='iso-8859-1', short_empty_elements=False):
        xmltodict.XMLGenerator.__bases__.__init__(self)
        buf = BufferedIOBase()
        buf.writable = lambda : True
        buf.write = out.write
        ioWrapper = TextIOWrapper(buf, encoding=encoding, errors='xmlcharrefreplace', newline='\n')
        self._write = ioWrapper.write
        self._flush = ioWrapper.flush
        self._ns_contexts = [{}]
        self._current_context = self._ns_contexts[-1]
        self._undeclared_ns_maps = []
        self._encoding = encoding

    def startDocument(self):
        pass


def convertRewardsDictToBonusObjects(dictData, key='rewards'):
    try:
        bonuses = _readEventBoardsRewards(dictData[key])
        xmlData = xmltodict.unparse({key: dictData[key]}, xml_generator_cls=CustomXMLGenerator).encode('utf-8')
        dataSection = DataSection()
        dataSection.createSectionFromString(xmlData)
        bonuses.update(readBonusSection(dictData[key].keys(), dataSection[key]))
        bonusObjects = []
        for bKey, bValue in bonuses.iteritems():
            bonusObjects.extend(getEventBoardsBonusObj(bKey, bValue))

        bonusObjects.sort(key=lambda b: BONUS_PRIORITY.index(b.getName()) if b.getName() in BONUS_PRIORITY else len(BONUS_PRIORITY))
        return bonusObjects
    except Exception:
        LOG_ERROR('WGELEN: Failed to parse rewards data!')
        return []


def checkEventExist(method):

    @wraps(method)
    def methodWrapper(self, eventID, *args):
        if self.eventsController.getEventsSettingsData().getEvent(eventID) is not None:
            return method(self, eventID, *args)
        else:
            LOG_DEBUG('WGELEN: Event with id "%s" does not exist.' % eventID)
            self._setMaintenance(True)
            return

    return methodWrapper
