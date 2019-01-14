# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_prestige_progress.py
from gui import makeHtmlString
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import icons, text_styles
from gui.shared.gui_items import Vehicle
from helpers import dependency, int2roman, i18n
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.shared import IItemsCache
PRESTIGE_TOKEN_TEMPLATE = 'epicmetagame:prestige:%d'
_ICON_NAME_TO_PRESTIGE_LEVEL = {'1': range(0, 3),
 '2': range(3, 6),
 '3': range(6, 9),
 '4': range(9, 11)}

class PrestigeBonusType(object):
    VEHICLE = 'vehicles'
    BADGE = 'dossier'


class LineSeparatorUI(object):
    GREY_LINE = 'greyLineSeparatorUI'
    GREEN_LINE = 'greenLineSeparatorUI'
    YELLOW_LINE = 'yellowLineSeparatorUI'


class PrestigeBlockIconPostfix(object):
    CURRENT = 'current'
    REACHED = 'reached'
    PRESTIGE = 'prestige'
    LOCKED = 'locked'
    UNLOCKED = 'unlocked'


class PrestigeBlockIconState(object):
    NORMAL = 'normal'
    SPECIAL = 'special'


class PrestigeProgressBlockUI(object):
    DEFAULT = 'PrestigeProgressBlockUI'
    CURRENT = 'CurrentPrestigeProgressBlockUI'
    VEHICLE_REWARD = 'VehicleRewardBlockUI'


_AVAILABLE_LEVELS = sum(_ICON_NAME_TO_PRESTIGE_LEVEL.values(), [])

def getPrestigeProgressVO(allQuests, metaLevel, pPrestigeLevel, isMaxMetaLevel):
    maxPrestigeLevel = metaLevel.get('maxPrestigeRewardLevel', 0)
    prestigeAwards = _getPrestigeLevelUpAwards(allQuests, maxPrestigeLevel)
    epicMetaGameCtrl = dependency.instance(IEpicBattleMetaGameController)
    _, maxRewardClaimed = epicMetaGameCtrl.getSeasonData()
    blocksVO = []
    for index, prestigeAward in enumerate(prestigeAwards):
        isSpecialReward = prestigeAward is not None
        isVehicleReward = isSpecialReward and prestigeAward > 0
        isNextBlockFinalReward = index + 1 == maxPrestigeLevel
        isCurrentOrNextToCurrentBlock = index == pPrestigeLevel or pPrestigeLevel > 0 and index == pPrestigeLevel - 1
        icon = _getPrestigeBlockIconPath(index, pPrestigeLevel, isMaxMetaLevel, isSpecialReward)
        lineStyle = _getLineSeparatorLinkageForPrestigeLevel(index, pPrestigeLevel, isMaxMetaLevel) if not isNextBlockFinalReward else ''
        tankText = ''
        levelText = int2roman(index + 1)
        if isVehicleReward:
            itemsCache = dependency.instance(IItemsCache)
            vehicle = itemsCache.items.getItemByCD(prestigeAward)
            icon = _getTankIconPath(vehicle)
            tankText = _formatVehicleNameWithTypeIcon(vehicle)
            levelText = '' if not maxRewardClaimed else _rewardClaimedText()
            lineStyle = ''
        blocksVO.append({'prestigeLevel': index + 1,
         'levelText': levelText,
         'descText': tankText,
         'canClaimVehicleReward': pPrestigeLevel == maxPrestigeLevel - 1 and isMaxMetaLevel and not maxRewardClaimed,
         'blockStyle': _getBlockStyle(index, pPrestigeLevel, isVehicleReward),
         'useShortSeparatorLine': isCurrentOrNextToCurrentBlock,
         'lineSeparatorStyle': lineStyle,
         'iconPath': icon})

    return {'titleHtmlText': text_styles.promoSubTitle(EPIC_BATTLE.PRESTIGEPROGRESS_HEADERTITLE),
     'progressBlocks': blocksVO}


def getPrestigeLevelAwardsVOs(allQuests, pPrestigeLevel, iconSize):
    currentPrestigeQuest = allQuests.get(PRESTIGE_TOKEN_TEMPLATE % pPrestigeLevel, None)
    awardsVO = []
    if currentPrestigeQuest:
        bonuses = currentPrestigeQuest.getBonuses()
        awardsVO = sum([ bonus.getEpicAwardVOs(withDescription=False, iconSize=iconSize) for bonus in bonuses ], [])
    return awardsVO


def getFinalTankRewardVehicleID(allQuests, maxPrestigeLevel):
    prestigeAwards = _getPrestigeLevelUpAwards(allQuests, maxPrestigeLevel)
    vehID = 0
    for prestigeAward in prestigeAwards:
        isSpecialReward = prestigeAward != []
        isVehicleReward = isSpecialReward and prestigeAward > 0
        if isVehicleReward:
            vehID = prestigeAward

    return vehID


def getFinalTankRewardIconPath(allQuests, maxPrestigeLevel):
    prestigeAwards = _getPrestigeLevelUpAwards(allQuests, maxPrestigeLevel)
    resultingPath = ''
    for prestigeAward in prestigeAwards:
        isSpecialReward = prestigeAward != []
        isVehicleReward = isSpecialReward and prestigeAward > 0
        if isVehicleReward:
            itemsCache = dependency.instance(IItemsCache)
            vehicle = itemsCache.items.getItemByCD(prestigeAward)
            resultingPath = _getTankIconPath(vehicle)

    return resultingPath


def getBlockBackgroundIndexForPrestigeLevel(pLevel):
    return next((k for k, v in _ICON_NAME_TO_PRESTIGE_LEVEL.iteritems() if pLevel in v))


def _getPrestigeLevelUpAwards(allQuests, maxPrestigeLevel):
    awards = []
    for i in xrange(0, maxPrestigeLevel + 1):
        currentPrestigeQuest = allQuests.get(PRESTIGE_TOKEN_TEMPLATE % i, None)
        specialAwardValue = None
        if currentPrestigeQuest:
            bonuses = currentPrestigeQuest.getBonuses()
            for bonus in bonuses:
                bonusName = bonus.getName()
                if bonusName == PrestigeBonusType.VEHICLE:
                    bonusVehicles = bonus.getVehicles()
                    if bonusVehicles is not None:
                        specialAwardValue = bonusVehicles[0][0].intCD
                if specialAwardValue is None and bonusName == PrestigeBonusType.BADGE:
                    if bonus.getBadges() is not None:
                        specialAwardValue = 0

        awards.append(specialAwardValue)

    return awards


def _getLineSeparatorLinkageForPrestigeLevel(currentBlock, prestigeLevel, canPrestige):
    if currentBlock < prestigeLevel:
        lineStyle = LineSeparatorUI.GREEN_LINE
    elif canPrestige and currentBlock == prestigeLevel:
        lineStyle = LineSeparatorUI.YELLOW_LINE
    else:
        lineStyle = LineSeparatorUI.GREY_LINE
    return lineStyle


def _getPrestigeBlockIconPath(currentBlock, currentPrestigeLevel, canPrestige, isSpecial):
    if canPrestige and currentBlock == currentPrestigeLevel + 1:
        path = PrestigeBlockIconState.SPECIAL if isSpecial else PrestigeBlockIconState.NORMAL
        postfix = PrestigeBlockIconPostfix.UNLOCKED
    elif canPrestige and currentBlock == currentPrestigeLevel:
        path = getBlockBackgroundIndexForPrestigeLevel(currentBlock)
        postfix = PrestigeBlockIconPostfix.PRESTIGE
    elif currentBlock == currentPrestigeLevel:
        path = getBlockBackgroundIndexForPrestigeLevel(currentBlock)
        postfix = PrestigeBlockIconPostfix.CURRENT
    elif currentBlock < currentPrestigeLevel:
        path = getBlockBackgroundIndexForPrestigeLevel(currentBlock)
        postfix = PrestigeBlockIconPostfix.REACHED
    else:
        path = PrestigeBlockIconState.SPECIAL if isSpecial else PrestigeBlockIconState.NORMAL
        postfix = PrestigeBlockIconPostfix.LOCKED
    return RES_ICONS.getEpicPrestigeBlockIcon(path, postfix)


def _getBlockStyle(currentBlock, currentPrestigeLevel, isVehicleReward):
    blockName = PrestigeProgressBlockUI.DEFAULT
    if isVehicleReward:
        blockName = PrestigeProgressBlockUI.VEHICLE_REWARD
    elif currentBlock == currentPrestigeLevel:
        blockName = PrestigeProgressBlockUI.CURRENT
    return blockName


def _getTankIconPath(vehicle):
    return RES_ICONS.getEpicBattlesIcon(vehicle.name.replace(':', '_'))


def _formatVehicleNameWithTypeIcon(vehicle):
    icon = icons.makeImageTag(Vehicle.getTypeSmallIconPath(vehicle.type, vehicle.isElite))
    level = int2roman(vehicle.level)
    return text_styles.statInfo('{} {}{}'.format(level, icon, vehicle.userName))


def _rewardClaimedText():
    text = i18n.makeString(EPIC_BATTLE.PRESTIGEPROGRESS_TANKREWARDRECEIVEDLABEL)
    icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_BUTTONS_CHECKMARK)
    rewardClaimedText = makeHtmlString('html_templates:battle/epicBattle', 'prestigeProgressRewardClaimed', {'msg': '{} {}'.format(icon, text)})
    return rewardClaimedText
