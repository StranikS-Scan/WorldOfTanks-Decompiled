# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/session_stats/shared.py
import nations
from account_helpers.settings_core.settings_constants import SESSION_STATS
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.session_stats.session_stats_settings_controller import SessionStatsSettingsController
from gui.Scaleform.genConsts.SESSION_STATS_CONSTANTS import SESSION_STATS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
_INFOTIP_PRECISION = 4

def toNiceNumber(value, coef=1):
    return '-' if value is None else backport.getNiceNumberFormat(float(value * coef))


_EFFICIENT_DATA = {SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_WTR: {'title': R.strings.session_stats.propertyInfo.prop.label.wtr(),
                                                   'label': R.strings.session_stats.label.wtr(),
                                                   'descr': R.strings.session_stats.propertyInfo.prop.descr.wtr(),
                                                   'icon': R.images.gui.maps.icons.library.wtrIcon_24(),
                                                   'totalValue': toNiceNumber,
                                                   'currentValue': lambda data: toNiceNumber(data.wtr.value),
                                                   'delta': lambda data: data.wtr.delta,
                                                   'settings': SESSION_STATS.SHOW_WTR},
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_DAMAGE: {'title': R.strings.session_stats.propertyInfo.prop.label.ratioDamage(),
                                                            'label': R.strings.session_stats.label.damaged(),
                                                            'descr': R.strings.session_stats.propertyInfo.prop.descr.ratioDamage(),
                                                            'icon': R.images.gui.maps.icons.eventBoards.ratio_damage(),
                                                            'totalValue': lambda stats: toNiceNumber(stats.getDamageEfficiency()),
                                                            'currentValue': lambda data: processRatioValue(data.ratioDamage.value),
                                                            'delta': lambda data: data.ratioDamage.delta,
                                                            'settings': SESSION_STATS.SHOW_RATIO_DAMAGE},
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_RATIO_KILL: {'title': R.strings.session_stats.propertyInfo.prop.label.ratioKill(),
                                                          'label': R.strings.session_stats.label.destroyed(),
                                                          'descr': R.strings.session_stats.propertyInfo.prop.descr.ratioKill(),
                                                          'icon': R.images.gui.maps.icons.eventBoards.vehicle_destroyed(),
                                                          'totalValue': lambda stats: toNiceNumber(stats.getFragsEfficiency()),
                                                          'currentValue': lambda data: processRatioValue(data.ratioKill.value),
                                                          'delta': lambda data: data.ratioKill.delta,
                                                          'settings': SESSION_STATS.SHOW_RATIO_KILL},
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_WINS: {'title': R.strings.session_stats.propertyInfo.prop.label.wins(),
                                                    'label': R.strings.session_stats.label.victory(),
                                                    'descr': R.strings.session_stats.propertyInfo.prop.descr.wins(),
                                                    'icon': R.images.gui.maps.icons.statistic.wins24(),
                                                    'totalValue': lambda stats: toNiceNumber(stats.getWinsCount()),
                                                    'currentValue': lambda data: toNiceNumber(data.wins.value),
                                                    'delta': lambda _: 0,
                                                    'settings': SESSION_STATS.SHOW_WINS},
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_DAMAGE: {'title': R.strings.session_stats.propertyInfo.prop.label.averageDamage(),
                                                              'label': R.strings.session_stats.label.averageDamage(),
                                                              'descr': R.strings.session_stats.propertyInfo.prop.descr.averageDamage(),
                                                              'icon': R.images.gui.maps.icons.statistic.avgDamage24(),
                                                              'totalValue': lambda stats: toNiceNumber(stats.getAvgDamage()),
                                                              'currentValue': lambda data: toNiceNumber(data.averageDamage.value),
                                                              'delta': lambda data: data.averageDamage.delta,
                                                              'settings': SESSION_STATS.SHOW_AVERAGE_DAMAGE},
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_HELP_DAMAGE: {'title': R.strings.session_stats.propertyInfo.prop.label.helpDamage(),
                                                           'label': R.strings.session_stats.label.assist(),
                                                           'descr': R.strings.session_stats.propertyInfo.prop.descr.helpDamage(),
                                                           'icon': R.images.gui.maps.icons.statistic.assist24(),
                                                           'totalValue': lambda stats: toNiceNumber(stats.getDamageAssistedEfficiencyWithStan()),
                                                           'currentValue': lambda data: toNiceNumber(data.helpDamage.value),
                                                           'delta': lambda data: data.helpDamage.delta,
                                                           'settings': SESSION_STATS.SHOW_HELP_DAMAGE},
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_BLOCKED_DAMAGE: {'title': R.strings.session_stats.propertyInfo.prop.label.blockedDamage(),
                                                              'label': R.strings.session_stats.label.blockedDamage(),
                                                              'descr': R.strings.session_stats.propertyInfo.prop.descr.blockedDamage(),
                                                              'icon': R.images.gui.maps.icons.eventBoards.blocked_damage_average(),
                                                              'totalValue': lambda stats: toNiceNumber(stats.getAvgDamageBlocked()),
                                                              'currentValue': lambda data: toNiceNumber(data.blockedDamage.value),
                                                              'delta': lambda data: data.blockedDamage.delta,
                                                              'settings': SESSION_STATS.SHOW_BLOCKED_DAMAGE},
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_XP: {'title': R.strings.session_stats.propertyInfo.prop.label.averageXp(),
                                                          'label': R.strings.session_stats.label.averageXP(),
                                                          'descr': R.strings.session_stats.propertyInfo.prop.descr.averageXp(),
                                                          'icon': R.images.gui.maps.icons.statistic.avgExp24(),
                                                          'totalValue': lambda stats: toNiceNumber(stats.getAvgXP()),
                                                          'currentValue': lambda data: toNiceNumber(data.averageXp.value),
                                                          'delta': lambda data: data.averageXp.delta,
                                                          'settings': SESSION_STATS.SHOW_AVERAGE_XP},
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_WIN_RATE: {'title': R.strings.session_stats.propertyInfo.prop.label.winRate(),
                                                        'label': R.strings.session_stats.label.winRate(),
                                                        'descr': R.strings.session_stats.propertyInfo.prop.descr.winRate(),
                                                        'icon': R.images.gui.maps.icons.statistic.wins24(),
                                                        'totalValue': lambda stats: toNiceNumber(stats.getWinsEfficiency(), 100),
                                                        'currentValue': lambda data: processRatioValue(data.winRate.value),
                                                        'delta': lambda data: data.winRate.delta,
                                                        'settings': SESSION_STATS.SHOW_WIN_RATE},
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_VEHICLE_LEVEL: {'title': R.strings.session_stats.propertyInfo.prop.label.averageVehiclesLevel(),
                                                                     'label': R.strings.session_stats.label.averageVehiclesLevel(),
                                                                     'descr': R.strings.session_stats.propertyInfo.prop.descr.averageVehiclesLevel(),
                                                                     'icon': R.images.gui.maps.icons.statistic.c_2_sr_ur_tech32(),
                                                                     'totalValue': lambda _: None,
                                                                     'currentValue': lambda data: toNiceNumber(data.averageVehicleLevel),
                                                                     'delta': lambda _: None,
                                                                     'settings': SESSION_STATS.SHOW_AVERAGE_VEHICLE_LEVEL},
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_FRAGS: {'title': R.strings.session_stats.propertyInfo.prop.label.averageFrags(),
                                                             'label': R.strings.session_stats.label.averageFrags(),
                                                             'descr': R.strings.session_stats.propertyInfo.prop.descr.averageFrags(),
                                                             'icon': R.images.gui.maps.icons.statistic.c_3_sr_kill32(),
                                                             'totalValue': lambda stats: toNiceNumber(stats.getAvgFrags()),
                                                             'currentValue': lambda data: toNiceNumber(data.averageFrags),
                                                             'delta': lambda _: 0,
                                                             'settings': SESSION_STATS.SHOW_AVERAGE_FRAGS},
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_SURVIVED_RATIO: {'title': R.strings.session_stats.propertyInfo.prop.label.survivedRate(),
                                                              'label': R.strings.session_stats.label.survivedRate(),
                                                              'descr': R.strings.session_stats.propertyInfo.prop.descr.survivedRate(),
                                                              'icon': R.images.gui.maps.icons.statistic.c_4_alive32(),
                                                              'totalValue': lambda stats: toNiceNumber(stats.getSurvivalEfficiency(), 100),
                                                              'currentValue': lambda data: processRatioValue(data.survivedRatio.value),
                                                              'delta': lambda data: data.survivedRatio.delta,
                                                              'settings': SESSION_STATS.SHOW_SURVIVED_RATE},
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_SPOTTED: {'title': R.strings.session_stats.propertyInfo.prop.label.spotted(),
                                                       'label': R.strings.session_stats.label.spotted(),
                                                       'descr': R.strings.session_stats.propertyInfo.prop.descr.spotted(),
                                                       'icon': R.images.gui.maps.icons.statistic.c_5_obnaruzh32(),
                                                       'totalValue': lambda stats: toNiceNumber(stats.getAvgEnemiesSpotted()),
                                                       'currentValue': lambda data: toNiceNumber(data.spotted.value),
                                                       'delta': lambda data: data.spotted.delta,
                                                       'settings': SESSION_STATS.SHOW_SPOTTED}}
_VIEW_ECONOMIC_DATA_WITH_SPENIDNG = (SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_NET_CREDITS, SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_NET_CRYSTAL)
_VIEW_ECONOMIC_DATA_WITHOUT_SPENIDNG = (SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_INCOME_CREDITS,
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_INCOME_CRYSTAL,
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_XP,
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_FREE_XP)
_ECONOMIC_DATA = {SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_NET_CREDITS: {'label': R.strings.session_stats.label.totalCredits(),
                                                           'tooltip': lambda _: '',
                                                           'detail': lambda data: data.creditsDetails,
                                                           'value': lambda data: toIntegral(data.netCredits),
                                                           'bigIcon': R.images.gui.maps.icons.library.creditsIcon_23x22(),
                                                           'smallIcon': R.images.gui.maps.icons.library.CreditsIcon_2()},
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_NET_CRYSTAL: {'label': R.strings.session_stats.label.totalCrystal(),
                                                           'tooltip': lambda _: '',
                                                           'detail': lambda data: data.crystalDetails,
                                                           'value': lambda data: toIntegral(data.netCrystal),
                                                           'bigIcon': R.images.gui.maps.icons.library.crystal_23x22(),
                                                           'smallIcon': R.images.gui.maps.icons.library.crystal_16x16()},
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_INCOME_CREDITS: {'label': R.strings.tooltips.credits.header(),
                                                              'tooltip': lambda data: makeTooltipData(backport.text(R.strings.tooltips.credits.header()), R.strings.session_stats.tooltip.statValue.credits.body, toNiceNumber(data.incomeCredits)),
                                                              'detail': lambda _: None,
                                                              'value': lambda data: toIntegral(data.incomeCredits),
                                                              'bigIcon': R.images.gui.maps.icons.library.creditsIcon_23x22(),
                                                              'smallIcon': R.images.gui.maps.icons.library.CreditsIcon_2()},
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_INCOME_CRYSTAL: {'label': R.strings.menu.crystals.promoWindow.title(),
                                                              'tooltip': lambda data: makeTooltipData(backport.text(R.strings.menu.crystals.promoWindow.title()), R.strings.session_stats.tooltip.statValue.crystals.body, toNiceNumber(data.incomeCrystal)),
                                                              'detail': lambda _: None,
                                                              'value': lambda data: toIntegral(data.incomeCrystal),
                                                              'bigIcon': R.images.gui.maps.icons.library.crystal_23x22(),
                                                              'smallIcon': R.images.gui.maps.icons.library.crystal_16x16()},
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_XP: {'label': R.strings.session_stats.label.gamingXp(),
                                                  'tooltip': lambda data: makeTooltipData(backport.text(R.strings.session_stats.label.gamingXp()), R.strings.session_stats.tooltip.statValue.xp.body, toNiceNumber(data.xp)),
                                                  'detail': lambda data: data.crystalDetails,
                                                  'value': lambda data: toIntegral(data.xp),
                                                  'bigIcon': R.images.gui.maps.icons.library.xpIcon_23x22(),
                                                  'smallIcon': R.images.gui.maps.icons.library.XpIcon()},
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_FREE_XP: {'label': R.strings.session_stats.label.freeXp(),
                                                       'tooltip': lambda data: makeTooltipData(backport.text(R.strings.session_stats.label.freeXp()), R.strings.session_stats.tooltip.statValue.freeXp.body, toNiceNumber(data.freeXP)),
                                                       'detail': lambda data: data.crystalDetails,
                                                       'value': lambda data: toIntegral(data.freeXP),
                                                       'bigIcon': R.images.gui.maps.icons.library.freeXpIcon_23x22(),
                                                       'smallIcon': R.images.gui.maps.icons.library.FreeXpIcon_2()}}
_PROP_ID_TO_POSITIVE_VALUE_STYLE_MAP = {SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_NET_CREDITS: text_styles.credits,
 SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_NET_CRYSTAL: text_styles.crystal}

def packTotalPropData(sessionStats, propId):
    value = _ECONOMIC_DATA[propId]['value'](sessionStats)
    detailsData = _ECONOMIC_DATA[propId]['detail'](sessionStats)
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
               'value': text_styles.highlightText(value)}}


def packEfficiencyPropData(randomStats, sessionStats, accountWtr, propId):
    data = _EFFICIENT_DATA[propId]
    isWtr = propId == SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_WTR
    isInteger = propId in (SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_WTR,)
    isWithoutTotalValue = propId in (SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_VEHICLE_LEVEL,)
    isWithoutDelta = propId in (SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_WINS, SESSION_STATS_CONSTANTS.SESSION_STATS_PROPS_AVERAGE_FRAGS)
    if isWtr:
        totalValue = data['totalValue'](accountWtr)
    else:
        totalValue = data['totalValue'](randomStats)
    currentValue = data['currentValue'](sessionStats)
    dynamicValue = data['delta'](sessionStats)
    if not dynamicValue:
        dynamicValue = text_styles.highlightText('-')
        diffIconSource = None
    elif dynamicValue > 0.0:
        precisionValue = precisionFormat(dynamicValue, showIntegerOnly=isInteger)
        dynamicValue = precisionValue and text_styles.success(precisionValue)
        diffIconSource = backport.image(R.images.gui.maps.icons.vehParams.icon_increase())
    else:
        precisionValue = precisionFormat(dynamicValue, showIntegerOnly=isInteger)
        dynamicValue = precisionValue and text_styles.error(precisionValue)
        diffIconSource = backport.image(R.images.gui.maps.icons.vehParams.icon_decrease())
    params = []
    if not isWithoutTotalValue:
        params.append({'label': text_styles.standard(backport.text(R.strings.session_stats.propertyInfo.total())),
         'value': text_styles.main(totalValue)})
    params.append({'label': text_styles.standard(backport.text(R.strings.session_stats.propertyInfo.current())),
     'value': text_styles.main(currentValue)})
    if not isWithoutTotalValue and not isWithoutDelta:
        params.append({'label': text_styles.standard(backport.text(R.strings.session_stats.propertyInfo.dynamic())),
         'value': dynamicValue,
         'delta': {'icon': diffIconSource}})
    return {'title': text_styles.promoSubTitle(backport.text(data['title'])),
     'description': text_styles.main(backport.text(data['descr'])),
     'params': params,
     'icon': getSessionStatsPropImage(propId)}


def packLastBattleData(data):
    settings = SessionStatsSettingsController().getSettings()
    isViewWithSpending = settings[SESSION_STATS.ECONOMIC_BLOCK_VIEW] == SESSION_STATS.ECONOMIC_BLOCK_VIEW_WITH_SPENDING
    result = []
    if isViewWithSpending:
        for idWithoutSpending in _VIEW_ECONOMIC_DATA_WITHOUT_SPENIDNG:
            economicData = _ECONOMIC_DATA[idWithoutSpending]
            result.append({'label': text_styles.main(backport.text(economicData['label'])),
             'icon': backport.image(economicData['bigIcon']),
             'value': economicData['value'](data),
             'tooltip': economicData['tooltip'](data)})

    else:
        for idWithSpending in _VIEW_ECONOMIC_DATA_WITH_SPENIDNG:
            economicData = _ECONOMIC_DATA[idWithSpending]
            result.append({'label': backport.text(economicData['label']),
             'icon': backport.image(economicData['bigIcon']),
             'value': economicData['value'](data),
             'id': idWithSpending})

    return result


def packTotalData(data):
    settings = SessionStatsSettingsController().getSettings()
    isViewWithSpending = settings[SESSION_STATS.ECONOMIC_BLOCK_VIEW] == SESSION_STATS.ECONOMIC_BLOCK_VIEW_WITH_SPENDING
    result = []
    if isViewWithSpending:
        for idWithSpending in _VIEW_ECONOMIC_DATA_WITH_SPENIDNG:
            economicData = _ECONOMIC_DATA[idWithSpending]
            result.append({'label': backport.text(economicData['label']),
             'icon': backport.image(economicData['smallIcon']),
             'value': economicData['value'](data),
             'id': idWithSpending})

    else:
        for idWithoutSpending in _VIEW_ECONOMIC_DATA_WITHOUT_SPENIDNG:
            economicData = _ECONOMIC_DATA[idWithoutSpending]
            result.append({'label': text_styles.main(backport.text(economicData['label'])),
             'icon': backport.image(economicData['smallIcon']),
             'value': economicData['value'](data),
             'tooltip': economicData['tooltip'](data)})

    return result


def packBattleEfficiencyData(data, parameters):
    settings = SessionStatsSettingsController().getSettings()
    view = []
    for parameter in parameters:
        for idEfficientData, efficient in _EFFICIENT_DATA.iteritems():
            if efficient['settings'] == parameter and settings[efficient['settings']]:
                view.append({'icon': backport.image(efficient['icon']),
                 'label': text_styles.main(backport.text(efficient['label'])),
                 'value': text_styles.stats(efficient['currentValue'](data)),
                 'delta': getDeltaAsData(efficient['delta'](data)),
                 'id': idEfficientData})

    return view


def makeTooltipData(header, resId, total):
    body = backport.text(resId(), total=total, lastBattle=total)
    return makeTooltip(header, body)


def toIntegral(value):
    return '-' if value is None else backport.getIntegralFormat(value)


def precisionFormat(value, showIntegerOnly=False):
    if showIntegerOnly:
        if abs(value) >= 1:
            return backport.getIntegralFormat(value)
        return ''
    if abs(value) >= 10:
        return backport.getFractionalFormat(value)
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
    if value.ratio is not None:
        return backport.getNiceNumberFormat(float(value.ratio))
    elif value.dealt is not None and value.received is not None:
        ctx = {'numerator': backport.getIntegralFormat(value.dealt),
         'denominator': backport.getIntegralFormat(value.received)}
        sourceKey = 'inverse' if value.dealt == 0 else 'normal'
        return makeHtmlString('html_templates:lobby/session_stats/', 'ratio', ctx, sourceKey=sourceKey)
    else:
        return '-'
