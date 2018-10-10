# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/formaters.py
import BigWorld
import nations
from gui import makeHtmlString
from helpers import int2roman
from gui.event_boards.event_boards_items import CALCULATION_METHODS
from gui.event_boards import event_boards_timer
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.NATIONS import NATIONS
from gui.shared.gui_items import Vehicle
from gui.shared.formatters import icons, text_styles
from gui.Scaleform.locale.EVENT_BOARDS import EVENT_BOARDS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.event_boards.event_boards_timer import FORMAT_MINUTE_STR

def formatNotAvailableTextWithIcon(text):
    icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_CYBERSPORT_NOTAVAILABLEICON)
    return '{} {}'.format(icon, text_styles.main(_ms(text)))


def formatErrorTextWithIcon(text):
    icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_TOOLTIP_DUPLICATED_OPTIONAL, 16, 16, -3, 0)
    return '{} {}'.format(icon, text_styles.error(_ms(text)))


def formatAllertTextWithIcon(text):
    icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_CYBERSPORT_ALERTICON)
    return '{} {}'.format(icon, text_styles.error(_ms(text)))


def formatAttentionTextWithIcon(text):
    icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICON, 16, 16, -4, 0)
    return '{} {}'.format(icon, text_styles.error(_ms(text)))


def formatOkTextWithIcon(text):
    icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_BUTTONS_CHECKMARK, 16, 16, -3, 0)
    return '{} {}'.format(icon, text_styles.success(_ms(text)))


def formatVehicleNameWithTypeIcon(vehicle, path):
    icon = icons.makeImageTag(Vehicle.getTypeSmallIconPath(vehicle.type, vehicle.isPremium))
    level = int2roman(vehicle.level)
    key = 'vehicle_prem' if vehicle.isPremium else 'vehicle'
    return makeHtmlString(path, key, {'msg': '{} {}{}'.format(level, icon, vehicle.userName)})


def formatVehicleNationAndTypeIcon(vehicle, path):
    iconType = icons.makeImageTag(Vehicle.getTypeSmallIconPath(vehicle.type, vehicle.isPremium))
    iconNation = icons.makeImageTag(RES_ICONS.getFilterNation(vehicle.nationName), width=26, height=16)
    level = int2roman(vehicle.level)
    return makeHtmlString(path, 'vehicle', {'msg': '{}{}{}'.format(iconNation, iconType, level)})


def getNationEmblemIcon(nation):
    return RES_ICONS.getNationEmblemIcon(nation) if nation in nations.AVAILABLE_NAMES else None


def getNationBigFlagIcon(nation, forVehicle):
    if nation in nations.AVAILABLE_NAMES:
        if forVehicle:
            return RES_ICONS.getEventBoardNationTankFlagIcon(nation)
        return RES_ICONS.getEventBoardNationFlagIcon(nation)
    else:
        return None


def getLevelBackgroundIcon():
    return RES_ICONS.MAPS_ICONS_EVENTBOARDS_BACKGROUNDS_LEVEL_TYPE_BACKGROUND


def getNationText(nation):
    return _ms(NATIONS.all(nation))


def getNationTextWithIcon(nation):
    iconNation = icons.makeImageTag(RES_ICONS.getFilterNation(nation), width=26, height=16)
    return '{}{}'.format(iconNation, getNationText(nation))


def vehicleTypeText(vType):
    return _ms('#quests:classes/{}'.format(vType))


def formatTimeToEnd(timeValue, period):
    if timeValue is 0:
        timeValue = 1
        period = FORMAT_MINUTE_STR
    timeName = EVENT_BOARDS.time_period(period)
    text = '{} {}'.format(timeValue, _ms(timeName))
    return text


def getClanTag(abbrev, color):
    if isinstance(color, int):
        color = '#{}'.format(hex(color)[2:].zfill(6))
    return '<font color="{color}">[{abbrev}]</font>'.format(abbrev=abbrev, color=color) if abbrev else ''


def getFullName(name, clanAbbrev, clanColor):
    return '{name} {clanTag}'.format(name=name, clanTag=getClanTag(clanAbbrev, clanColor)) if clanAbbrev else name


def getString(value, default='--'):
    return str(value) if value is not None else default


def getStatusTitleStyle(text):
    return makeHtmlString('html_templates:lobby/elen/status', 'title', {'msg': text})


def getStatusCountStyle(text):
    return makeHtmlString('html_templates:lobby/elen/status', 'count', {'msg': text})


def timeEndStyle(text):
    return makeHtmlString('html_templates:lobby/elen/status', 'time', {'msg': text})


def formatDate(ts, default='--'):
    return str(BigWorld.wg_getShortDateFormat(ts)) if ts is not None else default


def formatTime(ts):
    return str(BigWorld.wg_getShortTimeFormat(ts))


def formatTimeAndDate(ts):
    return '{0:>s} {1:>s}'.format(formatDate(ts), formatTime(ts))


def niceNumberFormatter(param):
    return BigWorld.wg_getNiceNumberFormat(param)


_defaultFormatter = niceNumberFormatter
_specialFormatters = {CALCULATION_METHODS.MAX: {1: formatDate}}
_additionalFormatters = {CALCULATION_METHODS.MAX: {1: {'valueTime': formatTime}}}

def formatParameters(method, params):
    if method in _specialFormatters:
        special = _specialFormatters[method]
        return [ (special[idx](params[idx]) if idx in special else _defaultFormatter(params[idx])) for idx in range(3) ]
    return [ _defaultFormatter(params[idx]) for idx in range(3) ]


def formatAdditionalParameters(method, params):
    if method in _additionalFormatters:
        additional = _additionalFormatters[method]
        result = {}
        for idx in range(3):
            if idx in additional:
                result.update({name:func(params[idx]) for name, func in additional[idx].iteritems()})

        return result
    return {}


def formatUpdateTime(recalculationTS):
    statusDay = event_boards_timer.getUpdateStatus_ts(recalculationTS)
    statusTime = BigWorld.wg_getShortTimeFormat(recalculationTS)
    day = _ms(EVENT_BOARDS.time_day(statusDay)) if statusDay else BigWorld.wg_getLongDateFormat(recalculationTS)
    status = _ms(EVENT_BOARDS.SUMMARY_STATUS, day=day, time=statusTime)
    return status
