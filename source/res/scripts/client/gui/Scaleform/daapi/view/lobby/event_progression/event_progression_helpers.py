# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_progression/event_progression_helpers.py
import typing
from collections import namedtuple
from gui.impl.gen.resources import R
from gui.impl import backport
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_meta_level_icon import getEpicMetaIconVODict
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.tooltips import formatters
from gui.shared.formatters import text_styles, icons
from helpers.dependency import replace_none_kwargs
from helpers import dependency, int2roman
from skeletons.gui.game_control import IEventProgressionController, IEpicBattleMetaGameController, IQuestsController
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.locale.MENU import MENU
from helpers import time_utils
EpicBattlesWidgetTooltipVO = namedtuple('EpicBattlesWidgetTooltipVO', 'progressBarData')

@replace_none_kwargs(itemsCache=IItemsCache, eventProgressionController=IEventProgressionController)
def getRewardVehicles(itemsCache=None, eventProgressionController=None):
    rewardVehiclesIds = [ intCD for intCD, _ in eventProgressionController.rewardVehicles ]
    rewardVehicles = itemsCache.items.getVehicles(REQ_CRITERIA.IN_CD_LIST(rewardVehiclesIds))
    return [ rewardVehicles[intCD] for intCD in rewardVehiclesIds ]


def getLevelStr(level):
    txtId = R.strings.tooltips.eventProgression.level()
    return backport.text(txtId, level=level)


def getLevelData(plLevel):
    items = []
    levelMsgStr = text_styles.stats(getLevelStr(plLevel))
    items.append(formatters.packTextBlockData(text=levelMsgStr, useHtml=True, padding=formatters.packPadding(left=20, right=20, top=-10)))
    return formatters.packBuildUpBlockData(items)


def getTimeTo(timeStamp, textId):
    timeLeft = time_utils.getTillTimeString(timeStamp, MENU.HEADERBUTTONS_BATTLE_TYPES_RANKED_AVAILABILITY, removeLeadingZeros=True)
    return backport.text(textId, value=text_styles.stats(timeLeft))


def getTimeToStartStr(timeStamp):
    return getTimeTo(timeStamp, R.strings.tooltips.eventProgression.timeToStart())


def getTimeToLeftStr(timeStamp):
    return getTimeTo(timeStamp, R.strings.tooltips.eventProgression.timeToLeft())


def getCycleRomanNumberStr(cycleNumber):
    txtId = R.strings.tooltips.eventProgression.season()
    return backport.text(txtId, season=int2roman(cycleNumber))


class EventProgressionTooltipHelpers(object):
    __instance = None
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __questController = dependency.descriptor(IQuestsController)
    __eventProgressionController = dependency.descriptor(IEventProgressionController)

    @staticmethod
    def getInstance():
        if EventProgressionTooltipHelpers.__instance is None:
            EventProgressionTooltipHelpers()
        return EventProgressionTooltipHelpers.__instance

    __slots__ = ()

    def __init__(self):
        if EventProgressionTooltipHelpers.__instance is None:
            EventProgressionTooltipHelpers.__instance = self
        return

    def isCurrentSeasonInPrimeTime(self):
        season = self.__epicController.getCurrentSeason()
        if season is None or season.getCycleInfo() is None:
            return False
        else:
            isInPrime = not self.__epicController.isInPrimeTime()
            isEnable = self.__epicController.isEnabled()
            isAvailable = self.__epicController.isAvailable()
            return isInPrime and isEnable and not isAvailable and season.getCycleInfo()

    def getHeaderTooltipPack(self):
        items = []
        items.append(self.getTopBackgroundTooltipWithTextData())
        bottom = -30
        if not self.isCurrentSeasonInPrimeTime() and not self.__epicController.isAvailable():
            items.append(self.getRewardVehiclesData())
            bottom = 0
        return formatters.packBuildUpBlockData(items, padding=formatters.packPadding(bottom=bottom))

    def getSeasonInfoPack(self):
        season = self.__epicController.getCurrentSeason() or self.__epicController.getNextSeason()
        currentTime = time_utils.getCurrentLocalServerTimestamp()
        isPrimeTime = self.isCurrentSeasonInPrimeTime()
        if isPrimeTime or self.__epicController.isAvailable():
            cycle = season.getCycleInfo()
            getDate = lambda c: c.endDate
            getTimeToStr = getTimeToLeftStr
        else:
            cycle = season.getNextByTimeCycle(currentTime) if season else None
            getDate = lambda c: c.startDate
            getTimeToStr = getTimeToStartStr
        if cycle is not None:
            cycleNumber = self.__epicController.getCurrentOrNextActiveCycleNumber(season)
            title = getCycleRomanNumberStr(cycleNumber)
            description = getTimeToStr(getDate(cycle) - currentTime) if self.__epicController.isEnabled() else backport.text(R.strings.tooltips.eventProgression.disabled())
        else:
            title = backport.text(R.strings.tooltips.eventProgression.allSeasonsAreOver())
            description = backport.text(R.strings.tooltips.eventProgression.allSeasonsAreOver())
        return formatters.packBuildUpBlockData([formatters.packImageTextBlockData(title=text_styles.middleTitle(title), txtPadding=formatters.packPadding(top=8, left=94), desc=text_styles.main(description), descPadding=formatters.packPadding(top=8, left=94), txtOffset=1, txtGap=-1, img=backport.image(R.images.gui.maps.icons.battleTypes.c_64x64.frontline()), imgPadding=formatters.packPadding(top=1, left=18))])

    def getCycleStatusPack(self):
        items = []
        season = self.__epicController.getCurrentSeason() or self.__epicController.getNextSeason()
        _, plLevel, pFamePts = self.__epicController.getPlayerLevelInfo()
        cycleNumber = self.__epicController.getCurrentOrNextActiveCycleNumber(season)
        seasonDescr = text_styles.middleTitle(getCycleRomanNumberStr(cycleNumber))
        items.append(formatters.packTextBlockData(text=seasonDescr, useHtml=True, padding=formatters.packPadding(left=20, right=20)))
        currentCycle = season.getCycleInfo()
        tDiff = currentCycle.endDate - time_utils.getCurrentLocalServerTimestamp() if currentCycle is not None else 0
        timeLeft = text_styles.main(getTimeToLeftStr(tDiff))
        items.append(formatters.packTextBlockData(text=timeLeft, useHtml=True, padding=formatters.packPadding(left=20, right=20)))
        items.append(formatters.packBuildUpBlockData(blocks=[formatters.packBlockDataItem(linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_META_LEVEL_ICON_BLOCK_LINKAGE, data=getEpicMetaIconVODict(seasonLevel=cycleNumber, playerLevel=plLevel))], layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        items.append(getLevelData(plLevel))
        if plLevel < self.__epicController.getMaxPlayerLevel():
            items.append(self.__getCurrentMaxProgress(playerLevel=plLevel, playerFamePts=pFamePts))
            items.append(self.__getPlayerProgressToLevelBlock(playerLevel=plLevel, playerFamePts=pFamePts))
        else:
            unlockedStr = backport.text(R.strings.tooltips.eventProgression.unlockedDailyMissions())
            items.append(formatters.packTextBlockData(text=text_styles.main(unlockedStr), useHtml=True, padding=formatters.packPadding(left=20, right=20, top=-7)))
        return formatters.packBuildUpBlockData(items)

    def getTopBackgroundTooltipWithTextData(self):
        header = text_styles.bonusLocalText(backport.text(R.strings.tooltips.eventProgression.header()))
        iconSrc = backport.image(R.images.gui.maps.icons.epicBattles.rewardPoints.c_16x16())
        iconCurrency = icons.makeImageTag(source=iconSrc, width=16, height=16, vSpace=-3)
        currency = text_styles.concatStylesWithSpace(self.__getCurrencyCurrentStr(), iconCurrency)
        background = R.images.gui.maps.icons.epicBattles.backgrounds.widget_tooltip_background()
        return formatters.packImageTextBlockData(title=header, txtPadding=formatters.packPadding(top=16, left=20), desc=currency, descPadding=formatters.packPadding(top=6, left=20), txtOffset=1, txtGap=-1, img=backport.image(background))

    def getRewardVehiclesData(self):
        rewardVehiclesNames = [ text_styles.stats(v.shortUserName) for v in getRewardVehicles() ]
        promo = R.strings.event_progression.selectorTooltip.eventProgression.promo
        text = backport.text(promo.multi() if len(rewardVehiclesNames) > 1 else promo.single(), vehicles=', '.join(rewardVehiclesNames[:-1]), vehicle=rewardVehiclesNames[-1])
        return formatters.packTextBlockData(text_styles.main(text), padding=formatters.packPadding(top=-10, left=20, right=25))

    def __getCurrencyCurrentStr(self):
        res = text_styles.main(backport.text(R.strings.tooltips.eventProgression.currency()) + ' ') + text_styles.stats(int(self.__eventProgressionController.actualRewardPoints))
        return res

    def __getPlayerProgressToLevelBlock(self, playerLevel, playerFamePts):
        famePtsToProgress = self.__epicController.getPointsProgressForLevel(playerLevel)
        data = EpicBattlesWidgetTooltipVO(progressBarData={'value': playerFamePts,
         'maxValue': famePtsToProgress})._asdict()
        res = formatters.packBlockDataItem(linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_META_LEVEL_PROGRESS_BLOCK_LINKAGE, data=data, padding=formatters.packPadding(left=20))
        return res

    def __getCurrentMaxProgress(self, playerLevel, playerFamePts):
        items = []
        famePtsToProgress = self.__epicController.getPointsProgressForLevel(playerLevel)
        currentPoint = text_styles.stats(str(playerFamePts))
        fameTo = text_styles.main(str(famePtsToProgress))
        currentPointMaxPoint = text_styles.concatStylesWithSpace(currentPoint, text_styles.main('/'), fameTo)
        iconSrc = backport.image(R.images.gui.maps.icons.epicBattles.fame_point_tiny())
        icon = icons.makeImageTag(source=iconSrc, width=24, height=24)
        items.append(formatters.packAlignedTextBlockData(text=text_styles.concatStylesWithSpace(text_styles.main(currentPointMaxPoint), icon), align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT, padding=formatters.packPadding(left=20, right=20, top=-35)))
        return formatters.packBuildUpBlockData(items)
