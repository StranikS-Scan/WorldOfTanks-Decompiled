# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/session_stats/shared.py
import BigWorld
import nations
from gui import makeHtmlString
from gui.Scaleform.genConsts.SESSION_STATS_CONSTANTS import SESSION_STATS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
_INFOTIP_PRECISION = 4
_POPOVER_PRECISION = 2
_ZERO_TUPLE = (0, 0, 0)
_LABLE_TEXTS = {SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_INCOME_CREDITS: backport.text(R.strings.tooltips.credits.header()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_XP: backport.text(R.strings.session_stats.label.gamingXp()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_INCOME_CRYSTAL: backport.text(R.strings.menu.crystals.promoWindow.title()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_FREE_XP: backport.text(R.strings.session_stats.label.freeXp()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_WTR: backport.text(R.strings.session_stats.label.wtr()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_DAMAGE: backport.text(R.strings.session_stats.label.damaged()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_KILL: backport.text(R.strings.session_stats.label.destroyed()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_WIN: backport.text(R.strings.session_stats.label.victory()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_DAMAGE: backport.text(R.strings.session_stats.label.averageDamage()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_ASSIST: backport.text(R.strings.session_stats.label.assist()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_BLOCKED_DAMAGE: backport.text(R.strings.session_stats.label.blockedDamage()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_XP: backport.text(R.strings.session_stats.label.averageXP())}
_TITLE_TEXTS = {SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_WTR: backport.text(R.strings.session_stats.propertyInfo.prop.label.wtr()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_DAMAGE: backport.text(R.strings.session_stats.propertyInfo.prop.label.ratioDamage()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_KILL: backport.text(R.strings.session_stats.propertyInfo.prop.label.ratioKill()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_WIN: backport.text(R.strings.session_stats.propertyInfo.prop.label.winRatio()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_DAMAGE: backport.text(R.strings.session_stats.propertyInfo.prop.label.averageDamage()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_ASSIST: backport.text(R.strings.session_stats.propertyInfo.prop.label.helpDamage()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_BLOCKED_DAMAGE: backport.text(R.strings.session_stats.propertyInfo.prop.label.blockedDamage()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_XP: backport.text(R.strings.session_stats.propertyInfo.prop.label.averageXp())}
_DESCR_INFO_TEXTS = {SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_WTR: backport.text(R.strings.session_stats.propertyInfo.prop.descr.wtr()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_DAMAGE: backport.text(R.strings.session_stats.propertyInfo.prop.descr.ratioDamage()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_KILL: backport.text(R.strings.session_stats.propertyInfo.prop.descr.ratioKill()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_WIN: backport.text(R.strings.session_stats.propertyInfo.prop.descr.winRatio()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_DAMAGE: backport.text(R.strings.session_stats.propertyInfo.prop.descr.averageDamage()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_ASSIST: backport.text(R.strings.session_stats.propertyInfo.prop.descr.helpDamage()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_BLOCKED_DAMAGE: backport.text(R.strings.session_stats.propertyInfo.prop.descr.blockedDamage()),
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_XP: backport.text(R.strings.session_stats.propertyInfo.prop.descr.averageXp())}
_PROP_ID_ACCOUNT_RANDOM_STATS_GETTERS_MAP = {SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_WTR: None,
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_DAMAGE: 'getDamageEfficiency',
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_XP: 'getXP',
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_KILL: 'getFragsEfficiency',
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_WIN: 'getWinsCount',
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_DAMAGE: 'getAvgDamage',
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_ASSIST: 'getDamageAssistedEfficiency',
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_BLOCKED_DAMAGE: 'getAvgDamageBlocked',
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_XP: 'getAvgXP'}
_TOOLTIP_RES_ID_ACCESSORS = {SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_INCOME_CREDITS: R.strings.session_stats.tooltip.statValue.credits.body,
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_XP: R.strings.session_stats.tooltip.statValue.xp.body,
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_INCOME_CRYSTAL: R.strings.session_stats.tooltip.statValue.crystals.body,
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_FREE_XP: R.strings.session_stats.tooltip.statValue.freeXp.body}
_PROP_ID_TO_DETAILS_MAP = {SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_NET_CREDITS: 'creditsDetails',
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_NET_CRYSTAL: 'crystalDetails'}
_PROP_ID_TO_POSITIVE_VALUE_STYLE_MAP = {SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_NET_CREDITS: text_styles.credits,
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_NET_CRYSTAL: text_styles.crystal}

def packTotalPropData(sessionStats, propId):
    totalValue = getattr(sessionStats, propId)
    detailsData = getattr(sessionStats, _PROP_ID_TO_DETAILS_MAP[propId])
    params = []
    for paramName in detailsData._fields:
        param = getattr(detailsData, paramName)
        if param:
            params.append({'label': text_styles.standard(backport.text(getattr(R.strings.session_stats.propertyInfo.total.label, paramName)())),
             'value': _PROP_ID_TO_POSITIVE_VALUE_STYLE_MAP[propId](toIntegral(param)) if param > 0 else text_styles.error(toIntegral(param))})

    return {'title': text_styles.promoSubTitle(backport.text(getattr(R.strings.session_stats.propertyInfo.total.label, propId)())),
     'description': text_styles.main(backport.text(R.strings.session_stats.propertyInfo.total.descr())),
     'params': params,
     'icon': getSessionStatsPropImage(propId),
     'total': {'label': text_styles.mainBig(backport.text(R.strings.session_stats.propertyInfo.total.total())),
               'value': text_styles.highlightText(toIntegral(totalValue))}}


def packEfficiencyPropData(randomStats, sessionStats, accountWtr, propId):
    isWtr = propId == SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_WTR
    if isWtr:
        totalValue = toNiceNumber(accountWtr)
        currentValue = toNiceNumber(sessionStats.wtr.value)
        dynamicValue = sessionStats.wtr.delta
    else:
        totalValue = toNiceNumber(getattr(randomStats, _PROP_ID_ACCOUNT_RANDOM_STATS_GETTERS_MAP[propId])())
        sessStatValue = getattr(sessionStats, propId)
        if propId in (SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_KILL, SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_DAMAGE):
            currentValue = processRatioValue(sessStatValue.value)
        else:
            currentValue = toNiceNumber(sessStatValue.value)
        dynamicValue = sessStatValue.delta
    if not dynamicValue:
        dynamicValue = text_styles.highlightText('-')
        diffIconSource = None
    elif dynamicValue > 0.0:
        precisionValue = precisionFormat(dynamicValue, showIntegerOnly=isWtr)
        dynamicValue = precisionValue and text_styles.success(precisionValue)
        diffIconSource = backport.image(R.images.gui.maps.icons.vehParams.icon_increase())
    else:
        precisionValue = precisionFormat(dynamicValue, showIntegerOnly=isWtr)
        dynamicValue = precisionValue and text_styles.error(precisionValue)
        diffIconSource = backport.image(R.images.gui.maps.icons.vehParams.icon_decrease())
    return {'title': text_styles.promoSubTitle(_TITLE_TEXTS[propId]),
     'description': text_styles.main(_DESCR_INFO_TEXTS[propId]),
     'params': [{'label': text_styles.standard(backport.text(R.strings.session_stats.propertyInfo.total())),
                 'value': text_styles.main(totalValue)}, {'label': text_styles.standard(backport.text(R.strings.session_stats.propertyInfo.current())),
                 'value': text_styles.stats(currentValue)}, {'label': text_styles.standard(backport.text(R.strings.session_stats.propertyInfo.dynamic())),
                 'value': dynamicValue,
                 'delta': {'icon': diffIconSource}}],
     'icon': getSessionStatsPropImage(propId)}


def packLastBattleData(data):
    return [{'label': text_styles.main(_LABLE_TEXTS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_INCOME_CREDITS]),
      'icon': RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_23X22,
      'value': text_styles.highTitle(toIntegral(data.incomeCredits)),
      'tooltip': makeTooltipData(_LABLE_TEXTS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_INCOME_CREDITS], _TOOLTIP_RES_ID_ACCESSORS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_INCOME_CREDITS], toNiceNumber(data.incomeCredits))},
     {'label': text_styles.main(_LABLE_TEXTS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_XP]),
      'icon': RES_ICONS.MAPS_ICONS_LIBRARY_XPICON_23X22,
      'value': text_styles.highTitle(toIntegral(data.xp)),
      'tooltip': makeTooltipData(_LABLE_TEXTS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_XP], _TOOLTIP_RES_ID_ACCESSORS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_XP], toNiceNumber(data.xp))},
     {'label': text_styles.main(_LABLE_TEXTS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_INCOME_CRYSTAL]),
      'icon': RES_ICONS.MAPS_ICONS_LIBRARY_CRYSTAL_23X22,
      'value': text_styles.highTitle(toIntegral(data.incomeCrystal)),
      'tooltip': makeTooltipData(_LABLE_TEXTS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_INCOME_CRYSTAL], _TOOLTIP_RES_ID_ACCESSORS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_INCOME_CRYSTAL], toNiceNumber(data.incomeCrystal))},
     {'label': text_styles.main(_LABLE_TEXTS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_FREE_XP]),
      'icon': RES_ICONS.MAPS_ICONS_LIBRARY_FREEXPICON_23X22,
      'value': text_styles.highTitle(toIntegral(data.freeXP)),
      'tooltip': makeTooltipData(_LABLE_TEXTS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_FREE_XP], _TOOLTIP_RES_ID_ACCESSORS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_FREE_XP], toNiceNumber(data.freeXP))}]


def packTotalData(data):
    return [{'label': backport.text(R.strings.session_stats.label.totalCredits()),
      'icon': backport.image(R.images.gui.maps.icons.library.CreditsIcon_2()),
      'value': toIntegral(data.netCredits),
      'id': SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_NET_CREDITS}, {'label': backport.text(R.strings.session_stats.label.totalCrystal()),
      'icon': backport.image(R.images.gui.maps.icons.library.crystal_16x16()),
      'value': toIntegral(data.netCrystal),
      'id': SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_NET_CRYSTAL}]


def packBattleEfficiencyData(data):
    return [{'icon': backport.image(R.images.gui.maps.icons.library.wtrIcon_24()),
      'label': text_styles.main(_LABLE_TEXTS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_WTR]),
      'value': text_styles.stats(toNiceNumber(data.wtr.value)),
      'delta': getDeltaAsData(data.wtr.delta),
      'id': SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_WTR},
     {'icon': backport.image(R.images.gui.maps.icons.eventBoards.ratio_damage()),
      'label': text_styles.main(_LABLE_TEXTS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_DAMAGE]),
      'value': text_styles.stats(processRatioValue(data.ratioDamage.value)),
      'delta': getDeltaAsData(data.ratioDamage.delta),
      'id': SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_DAMAGE},
     {'icon': backport.image(R.images.gui.maps.icons.eventBoards.vehicle_destroyed()),
      'label': text_styles.main(_LABLE_TEXTS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_KILL]),
      'value': text_styles.stats(processRatioValue(data.ratioKill.value)),
      'delta': getDeltaAsData(data.ratioKill.delta),
      'id': SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_KILL},
     {'icon': backport.image(R.images.gui.maps.icons.statistic.wins24()),
      'label': text_styles.main(_LABLE_TEXTS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_WIN]),
      'value': text_styles.stats(toNiceNumber(data.winRatio.value)),
      'delta': getDeltaAsData(0),
      'id': SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_WIN},
     {'icon': backport.image(R.images.gui.maps.icons.statistic.avgDamage24()),
      'label': text_styles.main(_LABLE_TEXTS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_DAMAGE]),
      'value': text_styles.stats(toNiceNumber(data.averageDamage.value)),
      'delta': getDeltaAsData(data.averageDamage.delta),
      'id': SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_DAMAGE},
     {'icon': backport.image(R.images.gui.maps.icons.eventBoards.battle_damage_average_assist()),
      'label': text_styles.main(_LABLE_TEXTS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_ASSIST]),
      'value': text_styles.stats(toNiceNumber(data.helpDamage.value)),
      'delta': getDeltaAsData(data.helpDamage.delta),
      'id': SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_ASSIST},
     {'icon': backport.image(R.images.gui.maps.icons.eventBoards.blocked_damage_average()),
      'label': text_styles.main(_LABLE_TEXTS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_BLOCKED_DAMAGE]),
      'value': text_styles.stats(toNiceNumber(data.blockedDamage.value)),
      'delta': getDeltaAsData(data.blockedDamage.delta),
      'id': SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_BLOCKED_DAMAGE},
     {'icon': backport.image(R.images.gui.maps.icons.statistic.avgExp24()),
      'label': text_styles.main(_LABLE_TEXTS[SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_XP]),
      'value': text_styles.stats(toNiceNumber(data.averageXp.value)),
      'delta': getDeltaAsData(data.averageXp.delta),
      'id': SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_XP}]


def makeTooltipData(header, resId, total):
    body = backport.text(resId(), total=total, lastBattle=total)
    return makeTooltip(header, body)


def toIntegral(value):
    return '-' if value is None else BigWorld.wg_getIntegralFormat(value)


def toNiceNumber(value):
    return '-' if value is None else BigWorld.wg_getNiceNumberFormat(float(value))


def precisionFormat(value, showIntegerOnly=False):
    if showIntegerOnly:
        if abs(value) >= 1:
            return BigWorld.wg_getIntegralFormat(value)
        return ''
    if abs(value) >= 10:
        return BigWorld.wg_getFractionalFormat(value)
    return '%.*f' % (_INFOTIP_PRECISION, value) if abs(value) >= 10 ** (-_INFOTIP_PRECISION) else ''


def getDeltaAsData(deltaVal):
    data = {}
    if deltaVal:
        if deltaVal < 0:
            data['icon'] = backport.image(R.images.gui.maps.icons.vehParams.icon_decrease())
        else:
            data['icon'] = backport.image(R.images.gui.maps.icons.vehParams.icon_increase())
    return data


def getNationIcon(nationID, width, height):
    return '../maps/icons/nations/{0}x{1}/{2}.png'.format(width, height, nations.NAMES[nationID])


def getSessionStatsPropImage(propId, width=54, height=54):
    return '../maps/icons/statistic/{0}x{1}/{2}.png'.format(width, height, propId)


def processRatioValue(value):
    if value.ratio:
        return BigWorld.wg_getNiceNumberFormat(float(value.ratio))
    elif value.dealt is not None and value.received is not None:
        ctx = {'numerator': BigWorld.wg_getIntegralFormat(value.dealt),
         'denominator': BigWorld.wg_getIntegralFormat(value.received)}
        sourceKey = 'inverse' if value.dealt == 0 else 'normal'
        return makeHtmlString('html_templates:lobby/session_stats/', 'ratio', ctx, sourceKey=sourceKey)
    else:
        return '-'
