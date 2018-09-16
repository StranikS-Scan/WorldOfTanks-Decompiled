# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/event_boards_vos.py
import BigWorld
import nations
from gui import GUI_NATIONS_ORDER_INDEX_REVERSED
from gui.shared.gui_items.Vehicle import getSmallIconPath, Vehicle, VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED
from helpers import int2roman
from helpers.i18n import makeString as _ms
from debug_utils import LOG_ERROR
from items.vehicles import getVehicleType
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from gui.server_events.awards_formatters import QuestsBonusComposer, getEventBoardsAwardPacker
from gui.Scaleform.genConsts.EVENTBOARDS_ALIASES import EVENTBOARDS_ALIASES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.EVENT_BOARDS import EVENT_BOARDS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import formatErrorTextWithIcon, formatOkTextWithIcon, formatNotAvailableTextWithIcon, formatParameters, getFullName, getString, getClanTag
from gui.event_boards.event_boards_items import EVENT_TYPE, ExcelItem, PlayerEventsData, EventSettings, OBJECTIVE_PARAMETERS as _op, PLAYER_STATE_REASON as _psr, CALCULATION_METHODS as _cm
from gui.Scaleform import getNationsFilterAssetPath
from nations import AVAILABLE_NAMES
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import getStatusTitleStyle

class EVENT_BOARDS_GROUP_TYPES(object):
    GOLD = 1
    SILVER = 2
    BRONZE = 3
    IRON = 4
    WOOD = 5


_CATEGORY_NAMES = {EVENT_BOARDS_GROUP_TYPES.GOLD: 'gold',
 EVENT_BOARDS_GROUP_TYPES.SILVER: 'silver',
 EVENT_BOARDS_GROUP_TYPES.BRONZE: 'bronze',
 EVENT_BOARDS_GROUP_TYPES.IRON: 'iron',
 EVENT_BOARDS_GROUP_TYPES.WOOD: 'wood'}
FORMATS = {EVENT_TYPE.NATION: ('#nations:{}', '../maps/icons/filters/nationsMedium/{}.png'),
 EVENT_TYPE.LEVEL: ('#menu:levels/{}', '../maps/icons/filters/levels/level_{}.png'),
 EVENT_TYPE.CLASS: ('#quests:classes/{}', '../maps/icons/filters/tanks/{}.png')}

def _vehicleHeaderCreator(vehicleCDStr):
    vehicleCD = int(vehicleCDStr)
    vehicle = getVehicleType(vehicleCD)
    title = vehicle.shortUserString
    iconPath = 'premium' if bool('premium' in vehicle.tags) else 'simple'
    txtLevel = int2roman(vehicle.level)
    return (title, iconPath, txtLevel)


def makeTableViewHeaderVO(eType, value, eventName, status=None, statusTooltip=None):
    if eType == EVENT_TYPE.VEHICLE:
        title, icon, level = _vehicleHeaderCreator(value)
        popoverAlias = EVENTBOARDS_ALIASES.RESULT_FILTER_POPOVER_VEHICLES_ALIAS
    else:
        _title, _icon = FORMATS[eType]
        title = _ms(_title.format(value))
        icon = _icon.format(value)
        level = None
        popoverAlias = EVENTBOARDS_ALIASES.RESULT_FILTER_POPOVER_ALIAS
    return {'title': title,
     'icon': icon,
     'name': text_styles.main(_ms(EVENT_BOARDS.EXCEL_SUBHEADER, eventName=eventName)),
     'level': level,
     'popoverAlias': popoverAlias,
     'status': status,
     'statusTooltip': statusTooltip}


_LEADERBOARD_BG_CREATORS = {EVENT_TYPE.NATION: RES_ICONS.getEventBoardBg,
 EVENT_TYPE.VEHICLE: lambda _: RES_ICONS.getEventBoardBg('vehicle'),
 EVENT_TYPE.LEVEL: lambda _: RES_ICONS.getEventBoardBg('level'),
 EVENT_TYPE.CLASS: lambda _: RES_ICONS.getEventBoardBg('class')}

def makeTableViewBackgroundVO(eType, value):
    return _LEADERBOARD_BG_CREATORS[eType](value)


_OBJECTIVE_STRINGS = {_op.ORIGINALXP: 'exp',
 _op.XP: 'exp',
 _op.DAMAGEDEALT: 'damage',
 _op.DAMAGEASSISTED: 'damage'}
_METHOD_ICON_NAMES = {_cm.MAX: ('battle_%s_max', 'calendar', 'battle_quantity'),
 _cm.SUMN: ('battle_%s_total', 'battle_%s', 'battle_quantity'),
 _cm.SUMSEQN: ('battle_%s_total', 'battle_%s', 'battle_quantity'),
 _cm.SUMMSEQN: ('battle_%s_total', 'battle_%s', 'battle_quantity'),
 _cm.SUMALL: ('battle_%s_total', 'battle_exp_average', 'battle_quantity')}

def makeTableHeaderVO(method, objective, eventType):
    if objective == _op.WINS:
        icons = (RES_ICONS.getEventBoardIcon('win_quantity'), RES_ICONS.getEventBoardIcon('battle_exp_average'), RES_ICONS.getEventBoardIcon('battle_quantity'))
    else:
        try:
            icons = [ (RES_ICONS.getEventBoardIcon(icon) if '%s' not in icon else RES_ICONS.getEventBoardIcon(icon % _OBJECTIVE_STRINGS[objective])) for icon in _METHOD_ICON_NAMES[method] ]
        except KeyError:
            LOG_ERROR('WGELEN: Wrong method/objective: %s/%s!' % (method, objective))
            return None

    return {'columns': [{'tooltip': makeTooltip(TOOLTIPS.elen_excel_objparam_all_all_header(method, objective), TOOLTIPS.elen_excel_objparam_all_all_body(method, objective)),
                  'icon': icons[0]}, {'tooltip': makeTooltip(TOOLTIPS.elen_excel_addparam_all_all_header(method, objective), TOOLTIPS.elen_excel_addparam_all_all_body(method, objective)),
                  'icon': icons[1]}, {'tooltip': makeTooltip(TOOLTIPS.ELEN_EXCEL_INFOPARAM_WINS_HEADER, TOOLTIPS.elen_excel_infoparam_wins_all_body(eventType)),
                  'icon': icons[2]}],
     'positionTooltip': makeTooltip(TOOLTIPS.ELEN_EXCEL_POSITION_HEADER, TOOLTIPS.ELEN_EXCEL_POSITION_BODY),
     'playerTooltip': makeTooltip(TOOLTIPS.ELEN_EXCEL_PLAYER_HEADER, TOOLTIPS.ELEN_EXCEL_PLAYER_BODY)}


def makeEventBoardsTableDataVO(rewardCategories, method):
    rewardsFormatter = QuestsBonusComposer(getEventBoardsAwardPacker())
    data = []
    stripes = []
    for categoryNumber, category in rewardCategories.iteritems():
        players = category.get('players')
        if not players:
            continue
        rewards = category['rewards']
        isIndividual = len(rewards) > 1 and categoryNumber == EVENT_BOARDS_GROUP_TYPES.GOLD
        stripeVO = {'rendererLinkage': EVENTBOARDS_ALIASES.AWARD_STRIPE_RENDERER,
         'id': categoryNumber,
         'groupIcon': RES_ICONS.getEventBoardGroup(categoryNumber),
         'tooltip': _ms(TOOLTIPS.ELEN_ANCOR_ALLGROUPS_HEADER, group=int2roman(categoryNumber), min=category.get('rank_min'), max=category.get('rank_max'))}
        if not isIndividual and rewards:
            stripeVO['icons'] = rewardsFormatter.getFormattedBonuses(rewards[0])
        data.append(stripeVO)
        stripes.append(stripeVO)
        for currentPlayerData in players:
            name = currentPlayerData.getName()
            clanAbbrev = currentPlayerData.getClanTag()
            clanColor = currentPlayerData.getClanColor()
            rank = currentPlayerData.getRank()
            formattedParameters = formatParameters(method, (currentPlayerData.getP1(), currentPlayerData.getP2(), currentPlayerData.getP3()))
            player = {'position': rank,
             'value1': formattedParameters[0],
             'value2': formattedParameters[1],
             'value3': formattedParameters[2],
             'userVO': {'dbID': currentPlayerData.getSpaId(),
                        'fullName': getFullName(name, clanAbbrev, clanColor),
                        'userName': name,
                        'clanAbbrev': getClanTag(clanAbbrev, clanColor)}}
            if isIndividual:
                player['icons'] = rewardsFormatter.getFormattedBonuses(rewards[min(rank, len(rewards)) - 1])
                player['rendererLinkage'] = EVENTBOARDS_ALIASES.TOP_PLAYER_AWARD_RENDERER
            else:
                player['rendererLinkage'] = EVENTBOARDS_ALIASES.BASE_PLAYER_AWARD_RENDERER
            data.append(player)

    return ({'tableDP': data}, {'tableDP': stripes})


def makeParameterTooltipVO(method, amount, parameter):
    parametersWithTooltip = [_op.ORIGINALXP, _op.XP]
    maxOrSum = 'max' if method == _cm.MAX else 'sum'
    return makeTooltip(header=_ms(EVENT_BOARDS.TOOLTIP_TOP_NOREWARDGROUP), body=_ms(EVENT_BOARDS.tooltip_top_description_all(maxOrSum, parameter), number=int(amount))) if parameter in parametersWithTooltip and amount is not None else None


def makeEventBoardsTableViewStatusVO(title, tooltip, info, value1, value2, value3, showPoints, buttonLabel, buttonTooltip, buttonVisible, buttonEnabled, titleTooltip):
    buttonTop = not title
    result = {'title': title,
     'titleTooltip': tooltip,
     'buttonLabel': buttonLabel,
     'buttonTooltip': buttonTooltip,
     'buttonVisible': buttonVisible,
     'buttonEnabled': buttonEnabled,
     'buttonTop': buttonTop,
     'informationTooltip': titleTooltip}
    if showPoints:
        result.update({'info': text_styles.playerOnline(info),
         'value1': text_styles.vehicleStatusSimpleText(getString(value1)),
         'value2': text_styles.main(getString(value2)),
         'value3': text_styles.main(getString(value3, '0'))})
    return result


def makeAwardGroupDataTooltipVO(rewardCategories, enabledAncors):
    result = []
    for idx, enable in enumerate(enabledAncors):
        v = idx + 1
        if v in rewardCategories:
            body = TOOLTIPS.ELEN_ANCOR_ALLGROUPS_BODY if enable else TOOLTIPS.ELEN_ANCOR_NOTOCCUPIED_BODY
            header = _ms(TOOLTIPS.ELEN_ANCOR_ALLGROUPS_HEADER, group=int2roman(v), min=rewardCategories[v].get('rank_min'), max=rewardCategories[v].get('rank_max'))
            tooltip = makeTooltip(header, body)
            result.append(tooltip)

    return result


def makeFiltersVO(eventType, filters, selected=None, category=None):
    tooltip, value = FORMATS[eventType]
    data = [ {'id': str(lid),
     'value': value.format(f),
     'tooltip': makeTooltip(tooltip.format(f), '#event_boards:{0}/tooltip/{1}'.format(category, eventType)) if category else _ms(tooltip.format(f)),
     'selected': lid == selected} for lid, f in filters ]
    return data


def _makeCantJoinReasonTooltip(stateReasons, playerData, limits):

    def _addItem(name, error):
        formatter = formatNotAvailableTextWithIcon if error else formatOkTextWithIcon
        return (error, formatter(name))

    header = TOOLTIPS.ELEN_STATUS_REQUIREMENTS_HEADER
    body = ''
    date = BigWorld.wg_getShortDateFormat(limits.getRegistrationDateMaxTs())
    winRateMin = limits.getWinRateMin()
    winRateMax = limits.getWinRateMax()
    battlesCount = limits.getBattlesCountMin()
    winRate = playerData.getWinRate()
    items = list()
    items.append(_addItem(_ms(TOOLTIPS.ELEN_STATUS_CANTJOIN_REASON_BYAGE, date=date), _psr.BYAGE in stateReasons))
    items.append(_addItem(_ms(TOOLTIPS.ELEN_STATUS_CANTJOIN_REASON_BYVEHICLE), _psr.VEHICLESMISSING in stateReasons))
    if battlesCount:
        items.append(_addItem(_ms(TOOLTIPS.ELEN_STATUS_CANTJOIN_REASON_BYBATTLESCOUNT, number=battlesCount), _psr.BYBATTLESCOUNT in stateReasons))
    if winRateMin:
        items.append(_addItem(_ms(TOOLTIPS.ELEN_STATUS_CANTJOIN_REASON_BYWINRATELOW, number=winRateMin), _psr.BYWINRATE in stateReasons and winRate < winRateMin))
    if winRateMax:
        items.append(_addItem(_ms(TOOLTIPS.ELEN_STATUS_CANTJOIN_REASON_BYWINRATEHIGH, number=winRateMax), _psr.BYWINRATE in stateReasons and winRate > winRateMax))
    items.sort(key=lambda item: item[0], reverse=True)
    body = '\n'.join([ item[1] for item in items ])
    return makeTooltip(header, body)


def makeCantJoinReasonTextVO(event, playerData):
    playerState = playerData.getPlayerStateByEventId(event.getEventID())
    stateReasons = playerState.getPlayerStateReasons() if playerState else []
    stateReason = stateReasons[0] if stateReasons else None
    tooltip = None
    buttonVisible = False
    if event.isRegistrationFinished():
        result = formatErrorTextWithIcon(EVENT_BOARDS.STATUS_CANTJOIN_REASON_ENDREGISTRATION)
    elif _psr.SPECIALACCOUNT in stateReasons:
        result = getStatusTitleStyle(_ms(EVENT_BOARDS.STATUS_CANTJOIN_REASON_SPECIAL))
    elif stateReason is _psr.WASUNREGISTERED:
        result = getStatusTitleStyle(_ms(EVENT_BOARDS.STATUS_CANTJOIN_REASON_LEFTEVENT))
        tooltip = makeTooltip(EVENT_BOARDS.STATUS_CANTJOIN_REASON_LEFTEVENT, EVENT_BOARDS.STATUS_CANTJOIN_REASON_LEFTEVENT_TOOLTIP)
    else:
        limits = event.getLimits()
        if len(stateReasons) > 1:
            reasonText = _ms(EVENT_BOARDS.STATUS_CANTJOIN_REASON_MANY, number=len(stateReasons))
            tooltip = _makeCantJoinReasonTooltip(stateReasons, playerData, limits)
        elif stateReason is _psr.BYWINRATE:
            winRate = playerData.getWinRate()
            winRateMin = limits.getWinRateMin()
            winRateMax = limits.getWinRateMax()
            if winRate < winRateMin:
                reasonText = _ms(EVENT_BOARDS.STATUS_CANTJOIN_REASON_BYWINRATELOW, number=str(winRateMin))
            else:
                reasonText = _ms(EVENT_BOARDS.STATUS_CANTJOIN_REASON_BYWINRATEHIGH, number=str(winRateMax))
        elif stateReason is _psr.BYAGE:
            date = BigWorld.wg_getShortDateFormat(limits.getRegistrationDateMaxTs())
            reasonText = _ms(EVENT_BOARDS.STATUS_CANTJOIN_REASON_BYAGE, date=date)
        elif stateReason is _psr.BYBATTLESCOUNT:
            battlesCount = playerData.getBattlesCount()
            reasonText = _ms(EVENT_BOARDS.STATUS_CANTJOIN_REASON_BYBATTLESCOUNT, number=battlesCount)
        elif stateReason is _psr.BYBAN:
            reasonText = _ms(EVENT_BOARDS.STATUS_CANTJOIN_REASON_BANNED)
        elif stateReason is _psr.VEHICLESMISSING:
            reasonText = _ms(EVENT_BOARDS.STATUS_CANTJOIN_REASON_VEHICLESMISSING)
        else:
            reasonText = ''
        notAvailableText = formatErrorTextWithIcon(EVENT_BOARDS.STATUS_CANTJOIN_NOTAVAILABLE)
        reasonText = text_styles.main(reasonText)
        result = '{} {}'.format(notAvailableText, reasonText)
        buttonVisible = True
    return (result, tooltip, buttonVisible)


def makeVehicleVO(vehicle):
    icon = RES_ICONS.maps_icons_vehicletypes_elite if vehicle.isPremium else RES_ICONS.maps_icons_vehicletypes
    return {'id': vehicle.intCD,
     'vehicleName': text_styles.main(vehicle.shortUserName),
     'smallVehicleIconPath': vehicle.iconSmall,
     'nationIconPath': getNationsFilterAssetPath(AVAILABLE_NAMES[vehicle.nationID]),
     'typeIconPath': icon(vehicle.type + '.png'),
     'level': vehicle.level,
     'isInHangar': vehicle.isInInventory}


def makeVehiclePopoverVO(vehicle):
    iconFunc = RES_ICONS.maps_icons_vehicletypes_elite if vehicle.isPremium else RES_ICONS.maps_icons_vehicletypes
    return {'dbID': vehicle.intCD,
     'level': vehicle.level,
     'shortUserName': vehicle.shortUserName,
     'smallIconPath': getSmallIconPath(vehicle.name),
     'nationID': vehicle.nationID,
     'type': vehicle.type,
     'typeIcon': iconFunc(vehicle.type + '.png'),
     'inHangar': vehicle.isInInventory,
     'selected': False}


def vehicleValueGetter(vehicle, field):
    if isinstance(vehicle, Vehicle):
        vehicle = makeVehiclePopoverVO(vehicle)
    sortMapping = {'nations': GUI_NATIONS_ORDER_INDEX_REVERSED[nations.NAMES[vehicle['nationID']]],
     'type': VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED[vehicle['type']],
     'level': vehicle['level'],
     'name': vehicle['shortUserName'],
     'hangar': vehicle['inHangar']}
    return sortMapping[field]


def makePrimeTimesTooltipVO(primeTimes, currentPeripheryID, getNameFunc):
    ptList = []
    for pt in primeTimes:
        peripheryID = int(pt.getServer())
        name = str(getNameFunc(peripheryID, False))
        current = peripheryID == currentPeripheryID
        if current:
            formatter = text_styles.neutral
        elif pt.isActive():
            formatter = text_styles.main
        else:
            formatter = text_styles.standard
        ptList.append('{} {} - {}'.format(name, pt.getStartLocalTime(), pt.getEndLocalTime()))

    body = '\n'.join([ formatter(msg) for msg in sorted(ptList) ])
    return makeTooltip(_ms(TOOLTIPS.ELEN_CONDITION_PRIMETIME), body)
