# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/mapbox/mapbox_helpers.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.bonuses import getServiceBonuses
from helpers import dependency
from helpers.time_utils import getTimestampFromISO
from skeletons.gui.game_control import IMapboxController
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array, ViewEvent
    from frameworks.wulf.windows_system.window import Window
    from gui.impl.pub import WindowImpl
    from gui.shared.missions.packers.bonus import BonusUIPacker

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


def packMapboxRewardModelAndTooltip(rewardsList, bonusList, packer, numBattles, tooltipsList=None):
    groupStartIdx = len(tooltipsList)
    groupIdx = 0
    mapboxCtrl = dependency.instance(IMapboxController)
    for bonusItem in bonusList:
        totalIdx = groupStartIdx + groupIdx
        tooltipsData = packer.getToolTip(bonusItem)
        for bonusIdx, bonusModel in enumerate(packer.pack(bonusItem)):
            bonusModel.setTooltipId(str(totalIdx))
            bonusModel.setIndex(groupIdx)
            storedReward = mapboxCtrl.getStoredReward(numBattles, totalIdx)
            if storedReward:
                bonusModel.setPreviousIcon(mapboxCtrl.getStoredReward(numBattles, totalIdx))
            if tooltipsList is not None:
                tooltipsList.append(tooltipsData[bonusIdx])
            groupIdx += 1
            rewardsList.addViewModel(bonusModel)
            if bonusItem.getName() == 'selectableCrewbook':
                mapboxCtrl.storeReward(numBattles, totalIdx, bonusModel.getIcon())

    return


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


def convertTimeFromISO(timeStr):
    return getTimestampFromISO(timeStr) if timeStr else 0


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


def _adaptUniversalCrewbook(crewbookItems):
    for crewbook in crewbookItems:
        options = crewbook['options']
        valueAdapter = _BONUS_FORMAT_ADAPTERS.get(options['name'])
        if valueAdapter is not None:
            crewbook['options']['value'] = valueAdapter(options['value'])

    return crewbookItems


_BONUS_FORMAT_ADAPTERS = {'dossier': _adaptMapboxDossierFormat,
 'goodies': _adaptCDKeys,
 'items': _adaptCDKeys,
 'selectableCrewbook': _adaptUniversalCrewbook,
 'randomCrewbook': _adaptUniversalCrewbook}
