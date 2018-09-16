# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/event_summary.py
from helpers.time_utils import ONE_MINUTE
from helpers import dependency
from helpers import int2roman
from helpers.i18n import makeString as _ms
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import formatVehicleNameWithTypeIcon, getNationTextWithIcon, formatVehicleNationAndTypeIcon, vehicleTypeText, getFullName, formatTimeAndDate, formatUpdateTime
from gui.Scaleform.genConsts.EVENTBOARDS_ALIASES import EVENTBOARDS_ALIASES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.EVENT_BOARDS import EVENT_BOARDS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.event_boards.event_boards_items import CALCULATION_METHODS as _cm, OBJECTIVE_PARAMETERS as _op, EVENT_TYPE as _et
from skeletons.gui.shared import IItemsCache
_PARAMETER_VALUE_GETTER = {_op.ORIGINALXP: 'getExp',
 _op.XP: 'getExp',
 _op.DAMAGEDEALT: 'getDamage',
 _op.DAMAGEASSISTED: 'getAssistedDamage'}
_AVERAGE_ICON_BY_PARAMETER = {_op.ORIGINALXP: RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_EXP_POPUP,
 _op.XP: RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_EXP_POPUP,
 _op.DAMAGEDEALT: RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_DAMAGE_POPUP,
 _op.DAMAGEASSISTED: RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_ASSIST_POPUP}
_MAX_ICON_BY_PARAMETER = {_op.ORIGINALXP: RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_EXP_MAX_POPUP,
 _op.XP: RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_EXP_MAX_POPUP,
 _op.DAMAGEDEALT: RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_DAMAG_MAX_POPUP,
 _op.DAMAGEASSISTED: RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_ASSIST_MAX_POPUP}
_SUM_ICON_BY_PARAMETER = {_op.ORIGINALXP: RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_EXP_SUM_POPUP,
 _op.XP: RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_EXP_SUM_POPUP,
 _op.DAMAGEDEALT: RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_DAMAG_SUM_POPUP,
 _op.DAMAGEASSISTED: RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_ASSIST_POPUP}
_ICON_BY_PARAMETER = {_op.ORIGINALXP: RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_EXP2_POPUP,
 _op.XP: RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_EXP2_POPUP,
 _op.DAMAGEDEALT: RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_DAMAG2_POPUP,
 _op.DAMAGEASSISTED: RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_ASSIST2_POPUP}
ICON_ALPHA_USED_IN_CALCULATION = 1.0
ICON_ALPHA_NOT_USED_IN_CALCULATION = 0.2

def _getParameterValue(op, info):
    methodName = _PARAMETER_VALUE_GETTER[op]
    method = getattr(info, methodName)
    value = method()
    return value


class _Summary(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, event, leaderboard, excelItem, descriptionByType, iconByType):
        self._excelItem = excelItem
        self._event = event
        self._leaderboard = leaderboard
        self._leaderboardId = leaderboard.getLeaderboardID()
        self._value = event.getLeaderboard(self._leaderboardId)
        self._descriptionByType = descriptionByType
        self._iconByType = iconByType

    def isTable(self):
        return False

    def getHeader(self):
        recalculationTS = self._leaderboard.getLastLeaderboardRecalculationTS()
        status = formatUpdateTime(recalculationTS) if not self._event.isFinished() else ''
        title = getFullName(self._excelItem.getName(), self._excelItem.getClanTag(), self._excelItem.getClanColor())
        return {'title': title,
         'description': self._getDescription(),
         'description2': self._getDescription2(),
         'status': status,
         'isTable': self.isTable(),
         'isSquad': self._event.getIsSquadAllowed(),
         'statusTooltip': self._getStatusTooltip() if not self._event.isFinished() else ''}

    def getExperienceBlock(self):
        event = self._event
        infos = self._excelItem.getInfo()
        eventType = self._event.getType()
        method = event.getMethod()
        op = event.getObjectiveParameter()
        opName = EVENT_BOARDS.summary_param_all(method, op)
        infos = infos if type(infos) is list else [infos]
        opValue = sum((_getParameterValue(op, info) for info in infos))
        rank = self._excelItem.getRank()
        battles = self._excelItem.getP3()
        battleIcon = self._iconByType[op]
        groupPos = self.__getGroupPos()
        positionTooltip = makeTooltip(TOOLTIPS.elen_summary_rank(groupPos) if groupPos else TOOLTIPS.ELEN_SUMMARY_RANK_NORANK)
        battleTooltip = makeTooltip(TOOLTIPS.ELEN_SUMMARY_BATTLES_HEADER, TOOLTIPS.elen_summary_battles_all_body(eventType))
        experienceTooltip = makeTooltip(TOOLTIPS.elen_summary_objparam_all_all_header(method, op), TOOLTIPS.elen_summary_objparam_all_all_body(method, op))
        return {'experienceValue': str(opValue),
         'experience': opName,
         'position': _ms(EVENT_BOARDS.SUMMARY_POSITION, position=str(rank)),
         'battleValue': str(battles),
         'battle': _ms(EVENT_BOARDS.SUMMARY_BATTLES),
         'experienceIcon': battleIcon,
         'ribbon': groupPos,
         'battleIcon': RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_BATTLE_POPUP,
         'experienceTooltip': experienceTooltip,
         'positionTooltip': positionTooltip,
         'battleTooltip': battleTooltip}

    def getStatisticsBlock(self):
        return self._getStatisticsBlock()

    def getTableData(self):
        return self._getTableData()

    def getTableHeaderData(self):
        return self._getTableHeaderData()

    def _getStatisticsBlock(self):
        return {}

    def _getDescription(self):
        eventType = self._event.getType()
        items = self.itemsCache.items
        desc = self._descriptionByType(eventType)
        if eventType == _et.VEHICLE:
            vehicle = items.getItemByCD(self._value)
            value = formatVehicleNameWithTypeIcon(vehicle, 'html_templates:lobby/elen/summary')
        elif eventType == _et.LEVEL:
            value = int2roman(self._value)
        elif eventType == _et.CLASS:
            value = vehicleTypeText(self._value)
        else:
            value = getNationTextWithIcon(self._value)
        return _ms(desc, value=value)

    def _getDescription2(self):
        pass

    def _getTableData(self):
        return {}

    def _getTableHeaderData(self):
        return {}

    def __getGroupPos(self):
        reward = self._event.getRewardsByRank().getRewardByRank(self._leaderboardId)
        return reward.getRewardCategoryNumber(self._excelItem.getRank())

    def _getStatusTooltip(self):
        leaderboard = self._leaderboard
        recalculationInterval = leaderboard.getRecalculationInterval()
        if recalculationInterval is None:
            recalculationInterval = 0
        interval = int(recalculationInterval / ONE_MINUTE)
        return makeTooltip(body=_ms(TOOLTIPS.SUMMARY_STATUS_TOOLTIP, interval=interval))


class _SummaryMax(_Summary):
    _ParameterOrder = ((_op.ORIGINALXP, _op.XP), (_op.DAMAGEDEALT,), (_op.DAMAGEASSISTED,))

    def __init__(self, event, leaderboard, excelItem):
        super(_SummaryMax, self).__init__(event, leaderboard, excelItem, EVENT_BOARDS.summary_description_max, _MAX_ICON_BY_PARAMETER)

    def _getStatisticsBlock(self):
        event = self._event
        method = event.getMethod()
        op = event.getObjectiveParameter()
        order = list(filter(lambda t: op not in t, self._ParameterOrder))
        info = self._excelItem.getInfo()
        param1 = order[0][0]
        statistic1 = EVENT_BOARDS.summary_param_all(method, param1)
        statistic1Value = str(_getParameterValue(param1, info))
        statistic1Icon = _ICON_BY_PARAMETER[param1]
        param2 = order[1][0]
        statistic2 = EVENT_BOARDS.summary_param_all(method, param2)
        statistic2Value = str(_getParameterValue(param2, info))
        statistic2Icon = _ICON_BY_PARAMETER[param2]
        return {'statistic1Value': statistic1Value,
         'statistic1': statistic1,
         'statistic1Icon': statistic1Icon,
         'statistic1Tooltip': makeTooltip(TOOLTIPS.elen_summary_param_all_all_header(method, param1), TOOLTIPS.elen_summary_param_all_all_body(method, param1)),
         'statistic2Value': statistic2Value,
         'statistic2': statistic2,
         'statistic2Icon': statistic2Icon,
         'statistic2Tooltip': makeTooltip(TOOLTIPS.elen_summary_param_all_all_header(method, param2), TOOLTIPS.elen_summary_param_all_all_body(method, param2)),
         'statistic3Value': str(info.getBlockedDamage()),
         'statistic3': EVENT_BOARDS.SUMMARY_DAMAGEBLOCKED,
         'statistic3Icon': RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_BLOCKED_DMG_POPUP,
         'statistic3Tooltip': makeTooltip(TOOLTIPS.ELEN_SUMMARY_ADDPARAM_DAMAGEBLOCKED_HEADER, TOOLTIPS.ELEN_SUMMARY_ADDPARAM_DAMAGEBLOCKED_BODY),
         'statistic4Value': str(info.getFrags()),
         'statistic4': _ms(EVENT_BOARDS.SUMMARY_DESTROYEDVEHICLES),
         'statistic4Icon': RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_VEHICLE_POPUP,
         'statistic4Tooltip': makeTooltip(TOOLTIPS.ELEN_SUMMARY_ADDPARAM_FRAGS_HEADER, TOOLTIPS.ELEN_SUMMARY_ADDPARAM_FRAGS_BODY)}

    def _getDescription2(self):
        info = self._excelItem.getInfo()
        timeValue = info.getBattleTs()
        date = formatTimeAndDate(timeValue)
        inSquad = info.getIsInSquad()
        squadInfo = _ms(EVENT_BOARDS.SUMMARY_FIGHTINSQUAAD) if inSquad else _ms(EVENT_BOARDS.SUMMARY_FIGHTNOTINSQUAAD)
        result = _ms(EVENT_BOARDS.summary_result(info.getBattleResult()))
        return '{}. {} {}'.format(result, squadInfo, date)


class _SummarySumAll(_Summary):

    def __init__(self, event, leaderboard, excelItem):
        super(_SummarySumAll, self).__init__(event, leaderboard, excelItem, EVENT_BOARDS.summary_description_sum, _SUM_ICON_BY_PARAMETER)

    def _getStatisticsBlock(self):
        info = self._excelItem.getInfo()
        return {'statistic1Value': str(info.getExp()),
         'statistic1': _ms(EVENT_BOARDS.SUMMARY_AVERAGEXP),
         'statistic1Icon': RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_EXP_POPUP,
         'statistic1Tooltip': makeTooltip(TOOLTIPS.ELEN_SUMMARY_PARAM_SUMALL_XP_HEADER, TOOLTIPS.ELEN_SUMMARY_PARAM_SUMALL_XP_BODY),
         'statistic2Value': str(info.getWinRate()),
         'statistic2': _ms(EVENT_BOARDS.SUMMARY_WINRATE),
         'statistic2Icon': RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_WIN_POPUP,
         'statistic2Tooltip': makeTooltip(TOOLTIPS.ELEN_SUMMARY_ADDPARAM_WINRATE_HEADER, TOOLTIPS.ELEN_SUMMARY_ADDPARAM_WINRATE_BODY),
         'statistic3Value': str(info.getAvgDamageDealt()),
         'statistic3': _ms(EVENT_BOARDS.SUMMARY_AVERAGEDAMAGE),
         'statistic3Icon': RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_DAMAGE_POPUP,
         'statistic3Tooltip': makeTooltip(TOOLTIPS.ELEN_SUMMARY_PARAM_SUMALL_DAMAGEDEALT_HEADER, TOOLTIPS.ELEN_SUMMARY_PARAM_SUMALL_DAMAGEDEALT_BODY),
         'statistic4Value': str(info.getAvgAssistedDamage()),
         'statistic4': _ms(EVENT_BOARDS.SUMMARY_AVERAGEDAMAGEASSISTED),
         'statistic4Icon': RES_ICONS.MAPS_ICONS_EVENTBOARDS_POPUPICONS_ASSIST_POPUP,
         'statistic4Tooltip': makeTooltip(TOOLTIPS.ELEN_SUMMARY_PARAM_SUMALL_DAMAGEASSISTED_HEADER, TOOLTIPS.ELEN_SUMMARY_PARAM_SUMALL_DAMAGEASSISTED_BODY)}


class _SummaryTable(_Summary):
    _ParameterOrder = ((_op.ORIGINALXP, _op.XP), (_op.DAMAGEDEALT,), (_op.DAMAGEASSISTED,))
    _TableIconByParameter = {_op.ORIGINALXP: RES_ICONS.MAPS_ICONS_EVENTBOARDS_TABLEICONS_EXP2,
     _op.XP: RES_ICONS.MAPS_ICONS_EVENTBOARDS_TABLEICONS_EXP2,
     _op.DAMAGEDEALT: RES_ICONS.MAPS_ICONS_EVENTBOARDS_TABLEICONS_DAMAG2,
     _op.DAMAGEASSISTED: RES_ICONS.MAPS_ICONS_EVENTBOARDS_TABLEICONS_ASSIST2}

    def isTable(self):
        return True

    def _getTableHeaderData(self):
        result = [{'tooltip': makeTooltip(TOOLTIPS.ELEN_SUMMARY_TABLE_PLATOON_HEADER, TOOLTIPS.ELEN_SUMMARY_TABLE_PLATOON_BODY),
          'icon': RES_ICONS.MAPS_ICONS_EVENTBOARDS_TABLEICONS_PLATOON}]
        params = self.__getSortedParams()
        for p in params:
            result.append({'tooltip': makeTooltip(TOOLTIPS.elen_summary_table_all_header(p), TOOLTIPS.elen_summary_table_all_body(p)),
             'icon': self._TableIconByParameter[p]})

        result.append({'tooltip': makeTooltip(TOOLTIPS.ELEN_SUMMARY_TABLE_FRAGS_HEADER, TOOLTIPS.ELEN_SUMMARY_TABLE_FRAGS_BODY),
         'icon': RES_ICONS.MAPS_ICONS_EVENTBOARDS_TABLEICONS_VEHICLE})
        return {'dateTooltip': makeTooltip(TOOLTIPS.ELEN_SUMMARY_TABLE_DATE_HEADER),
         'technicsTooltip': makeTooltip(TOOLTIPS.ELEN_SUMMARY_TABLE_VEHICLES_HEADER),
         'resultTooltip': makeTooltip(TOOLTIPS.ELEN_SUMMARY_TABLE_RESULT_HEADER),
         'columns': result}

    def _getTableData(self):
        data = []
        items = self.itemsCache.items
        params = self.__getSortedParams()
        infos = self._excelItem.getInfo()
        infos = sorted(infos, key=lambda info: info.getBattleTs())
        for info in infos:
            vehicleCd = info.getVehicleCd()
            vehicle = items.getItemByCD(vehicleCd)
            timeValue = info.getBattleTs()
            date = formatTimeAndDate(timeValue)
            methodType = info.getMethodType()
            if methodType != _cm.SUMMSEQN or methodType == _cm.SUMMSEQN and info.getUsedInCalculations():
                isEnable = True
                iconAlpha = ICON_ALPHA_USED_IN_CALCULATION
                date = text_styles.main(date)
                technicsName = text_styles.main(vehicle.shortUserName)
                result = text_styles.main(EVENT_BOARDS.summary_result(info.getBattleResult()))
                platoonIcon = RES_ICONS.MAPS_ICONS_EVENTBOARDS_BATTLE_TYPE_PLATOON
            else:
                isEnable = False
                iconAlpha = ICON_ALPHA_NOT_USED_IN_CALCULATION
                date = text_styles.disabled(date)
                technicsName = text_styles.disabled(vehicle.shortUserName)
                result = text_styles.disabled(EVENT_BOARDS.summary_result(info.getBattleResult()))
                platoonIcon = RES_ICONS.MAPS_ICONS_EVENTBOARDS_BATTLE_TYPE_PLATOON_DARK
            icon = platoonIcon if info.getIsInSquad() else None
            technics = formatVehicleNationAndTypeIcon(vehicle, 'html_templates:lobby/elen/summary')
            player = {'icon': icon,
             'date': date,
             'technics': technics,
             'vehicle': vehicle.iconSmall,
             'technicsName': technicsName,
             'result': result,
             'value1': str(_getParameterValue(params[0], info)),
             'value2': str(_getParameterValue(params[1], info)),
             'value3': str(_getParameterValue(params[2], info)),
             'value4': str(info.getFrags()),
             'rendererLinkage': EVENTBOARDS_ALIASES.BASE_PLAYER_BATTLE_RENDERER,
             'isEnable': isEnable,
             'iconAlpha': iconAlpha}
            data.append(player)

        return {'tableDP': data}

    def __getSortedParams(self):
        op = self._event.getObjectiveParameter()
        order = filter(lambda t: op not in t, self._ParameterOrder)
        params = [op]
        params.extend([ p[0] for p in order ])
        return params


class _SummarySumN(_SummaryTable):

    def __init__(self, event, leaderboard, excelItem):
        super(_SummarySumN, self).__init__(event, leaderboard, excelItem, EVENT_BOARDS.summary_description_sumn, _SUM_ICON_BY_PARAMETER)


class _SummarySumSeqN(_SummaryTable):

    def __init__(self, event, leaderboard, excelItem):
        super(_SummarySumSeqN, self).__init__(event, leaderboard, excelItem, EVENT_BOARDS.summary_description_sumseqn, _SUM_ICON_BY_PARAMETER)


class _SummarySumMSeqN(_SummaryTable):

    def __init__(self, event, leaderboard, excelItem):
        super(_SummarySumMSeqN, self).__init__(event, leaderboard, excelItem, EVENT_BOARDS.summary_description_sumseqn, _SUM_ICON_BY_PARAMETER)


summaryByMethod = {_cm.MAX: _SummaryMax,
 _cm.SUMN: _SummarySumN,
 _cm.SUMSEQN: _SummarySumSeqN,
 _cm.SUMALL: _SummarySumAll,
 _cm.SUMMSEQN: _SummarySumMSeqN}

def getSummaryInfoData(event, leaderboard, data):
    method = event.getMethod()
    return summaryByMethod[method](event, leaderboard, data)
