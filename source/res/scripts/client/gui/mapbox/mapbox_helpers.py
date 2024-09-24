# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/mapbox/mapbox_helpers.py
import typing
import ArenaType
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import AlertData
from gui.periodic_battles.models import PrimeTimeStatus, PeriodType
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.server_events.bonuses import getServiceBonuses
from gui.shared.formatters import text_styles
from helpers import dependency, time_utils
from helpers.time_utils import getTimestampFromISO
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IMapboxController
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewEvent
    from frameworks.wulf.windows_system.window import Window
SPECIAL_CARDS = ('all',)
_MECHANICS_CARDS = ('fog', 'heavy_rain', 'fire', 'sandstorm')
_ALL_NON_MAPS_CARDS = set(SPECIAL_CARDS + _MECHANICS_CARDS)
_BATTLE_ENDED_PERIODS = frozenset((PeriodType.NOT_AVAILABLE_END, PeriodType.STANDALONE_NOT_AVAILABLE_END, PeriodType.ALL_NOT_AVAILABLE_END))

def convertTimeFromISO(timeStr):
    return getTimestampFromISO(timeStr) if timeStr else 0


def getMapboxRewardTooltip(event, tooltipData, parentWindow):
    if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        tooltipData = tooltipData[int(tooltipId)]
        window = backport.BackportTooltipWindow(tooltipData, parentWindow)
        window.load()
        return window
    else:
        return


def getPrimeTimeStatusVO():
    mapboxCtrl = dependency.instance(IMapboxController)
    connectionMgr = dependency.instance(IConnectionManager)
    showPrimeTimeAlert = False
    alertMessage = ''
    status, isBattleEnded = getMapboxBattlesStatus()
    if status != PrimeTimeStatus.AVAILABLE:
        showPrimeTimeAlert = True
        if isBattleEnded:
            alertMessage = backport.text(R.strings.mapbox.primeTimes.statusText.battlesEnded())
        else:
            alertMessage = backport.text(R.strings.mapbox.primeTimes.statusText.notAvailable(), serverName=connectionMgr.serverUserNameShort)
    return AlertData(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()) if showPrimeTimeAlert else None, buttonIcon='', buttonLabel=backport.text(R.strings.mapbox.serverAlertMessage.button()), buttonVisible=showPrimeTimeAlert and mapboxCtrl.hasAvailablePrimeTimeServers(), buttonTooltip=None, statusText=text_styles.vehicleStatusCriticalText(alertMessage), popoverAlias=None, bgVisible=True, shadowFilterVisible=showPrimeTimeAlert, tooltip=TOOLTIPS_CONSTANTS.MAPBOX_CALENDAR_DAY, isSimpleTooltip=False)


def getTillTimeString(timeStamp):
    timeLeft = time_utils.getTimeDeltaFromNow(timeStamp)
    modeStrBase = R.strings.menu.headerButtons.battle.types.mapbox.availability
    if timeLeft < time_utils.ONE_HOUR:
        res = backport.text(modeStrBase.lessThanHour())
    else:
        res = backport.backport_time_utils.getTillTimeStringByRClass(timeLeft, modeStrBase)
    return res


@dependency.replace_none_kwargs(mapboxCtrl=IMapboxController)
def getMapboxBattlesStatus(mapboxCtrl=None):
    now = time_utils.getCurrentTimestamp()
    status, _, _ = mapboxCtrl.getPrimeTimeStatus(now)
    isBattlesEnded = status != PrimeTimeStatus.AVAILABLE and mapboxCtrl.getPeriodInfo(now).periodType in _BATTLE_ENDED_PERIODS
    return (status, isBattlesEnded)


def prepareProgressionData(mapsData, validMaps):
    mapIDs = ArenaType.g_geometryNamesToIDs
    filteredMaps = {k:v for k, v in mapsData.items() if k in _ALL_NON_MAPS_CARDS or mapIDs.get(k) in validMaps}
    return sorted(filteredMaps.items(), key=lambda item: item[0] in _MECHANICS_CARDS and _MECHANICS_CARDS.index(item[0]))


def formatMapboxBonuses(reward):
    result = []
    for bonusItemData in formatMapboxRewards(reward):
        result += getServiceBonuses(bonusItemData['name'], bonusItemData['value'])

    return result


def formatMapboxRewards(reward):
    result = []
    for bonusItemData in reward:
        name = bonusItemData['name']
        value = bonusItemData['value']
        valueAdapter = _BONUS_FORMAT_ADAPTERS.get(name)
        if valueAdapter is not None:
            value = valueAdapter(bonusItemData['value'])
        result.append({'name': name,
         'value': value})

    return result


def _adaptMapboxDossierFormat(dossierValue):
    result = {}
    for bonus in dossierValue:
        result.setdefault(bonus['dossierType'], {})
        result[bonus['dossierType']].update({(bonus['achievementType'], bonus['achievementName']): {'value': bonus['value'],
                                                                'unique': bonus['unique'],
                                                                'type': bonus['type']}})

    return result


def _adaptCDKeys(itemValue):
    return {int(key):value for key, value in itemValue.iteritems()}


_BONUS_FORMAT_ADAPTERS = {'dossier': _adaptMapboxDossierFormat,
 'goodies': _adaptCDKeys,
 'items': _adaptCDKeys,
 'blueprints': _adaptCDKeys}
