# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/RankedBattlesCyclesView.py
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.meta.RankedBattlesCyclesViewMeta import RankedBattlesCyclesViewMeta
from gui.Scaleform.genConsts.TEXT_ALIGN import TEXT_ALIGN
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.ranked_battles.ranked_models import CYCLE_STATUS
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles, time_formatters
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, int2roman
from helpers.i18n import makeString as _ms
from shared_utils import first
from skeletons.gui.game_control import IRankedBattlesController
from gui.shared.formatters.icons import makeImageTag
FINAL_TAB = 'final'
_FINAL_CURRENT_TAB = 'final_current'

class RankedBattlesCyclesView(LobbySubView, RankedBattlesCyclesViewMeta):
    __background_alpha__ = 1
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, ctx=None):
        super(RankedBattlesCyclesView, self).__init__()

    def onEscapePress(self):
        self.__close()

    def onCloseBtnClick(self):
        self.__close()

    def onTabClick(self, tabID):
        self.as_updateTabContentS(self.__buildCycleData(tabID))

    def onLadderBtnClick(self):
        self.rankedController.openWebLeaguePage(ctx={'returnAlias': RANKEDBATTLES_ALIASES.RANKED_BATTLES_CYCLES_VIEW_ALIAS})

    def _populate(self):
        self.as_setDataS(self.__getStartData())
        super(RankedBattlesCyclesView, self)._populate()

    def __getStartData(self):
        staticData = {'status': self.__getStatusBlock(),
         'cyclesHeader': self.__getHeaderBlock(),
         'closeBtn': _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_BTNCLOSE),
         'bgImage': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_BG_RANK_BLUR}
        cycleID = self.__getSeason().getCycleID()
        staticData.update(self.__buildCycleData(cycleID))
        return staticData

    def __getStatusBlock(self):
        return {'statusText': self.__getStatusText(),
         'calendarTooltip': makeTooltip(RANKED_BATTLES.RANKEDBATTLEVIEW_STATUSBLOCK_CALENDARBTNTOOLTIP_HEADER, RANKED_BATTLES.RANKEDBATTLEVIEW_STATUSBLOCK_CALENDARBTNTOOLTIP_BODY),
         'calendarIcon': RES_ICONS.MAPS_ICONS_BUTTONS_CALENDAR}

    def __getStatusText(self):
        season = self.__getSeason()
        seasonName = season.getUserName()
        if seasonName is None:
            seasonNumber = season.getNumber()
            if seasonNumber and (isinstance(seasonNumber, int) or seasonNumber.isdigit()):
                seasonName = int2roman(int(seasonNumber))
        return text_styles.superPromoTitle(_ms(RANKED_BATTLES.RANKEDBATTLECYCLESVIEW_TITLE, season=seasonName))

    def __getHeaderBlock(self):
        """
        Status possible values: "past", "current", "future", "final"
        id - id for content tab, used to understand which content-tab display
        :return:
        """
        result = []
        allCycles = self.__getSeason().getAllCycles()
        totalPoints = 0
        for cycle in sorted(allCycles.values()):
            points = cycle.points
            totalPoints += points
            result.append(self.__getHeaderTab(cycle.ID, cycle.status, points, cycle))

        result.append(self.__getHeaderTab(FINAL_TAB, FINAL_TAB, totalPoints))
        return result

    def __getHeaderTab(self, cycleID, status, points, cycle=None):
        result = ''
        titleFormatter = text_styles.main
        if status == CYCLE_STATUS.CURRENT or status == _FINAL_CURRENT_TAB:
            result = text_styles.stats(RANKED_BATTLES.RANKEDBATTLEHEADER_POINTS_CURRENT)
            titleFormatter = text_styles.neutral
        elif not status == CYCLE_STATUS.FUTURE:
            result = text_styles.main(_ms(RANKED_BATTLES.RANKEDBATTLEHEADER_POINTS + status, points=points))
        if status == FINAL_TAB:
            titleStr = RANKED_BATTLES.RANKEDBATTLEHEADER_FINAL
        else:
            titleStr = _ms(RANKED_BATTLES.RANKEDBATTLEHEADER_CYCLE, cycle=cycle.ordinalNumber)
        title = titleFormatter(titleStr)
        return {'title': title,
         'id': str(cycleID),
         'tooltip': self.__makeHeaderTooltip(status, cycle, points),
         'status': status,
         'result': result}

    def __makeHeaderTooltip(self, status, cycle, points):
        tooltipPrefix = RANKED_BATTLES.RANKEDBATTLEHEADER_TOOLTIP_CYCLE + status
        headerPrefix = tooltipPrefix + '/header'
        bodyPrefix = tooltipPrefix + '/body'
        number = '' if status == FINAL_TAB else cycle.ordinalNumber
        if status == CYCLE_STATUS.CURRENT:
            date = cycle.endDate
        elif status == CYCLE_STATUS.FUTURE:
            date = cycle.startDate
        elif status == FINAL_TAB:
            date = self.__getSeason().getEndDate()
        else:
            date = None
        dateStr = time_formatters.formatDate(RANKED_BATTLES.RANKEDBATTLEHEADER_TOOLTIP_DATE, date) if date else ''
        return makeTooltip(_ms(headerPrefix, cycle=number), _ms(bodyPrefix, date=dateStr, points=points))

    def __close(self):
        self.fireEvent(events.LoadViewEvent(RANKEDBATTLES_ALIASES.RANKED_BATTLES_VIEW_ALIAS), scope=EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def __getAwardsRibbonBlock(self, cycle):
        rank = self.rankedController.getMaxRankForCycle(cycle.ID)
        awardsForTheLastRankVO = self.__packAwards(cycle)
        titleTxtStr = _ms(RANKED_BATTLES.RANKEDAWARDS_AWARDSBLOCK_TITLE, cycleNumber=cycle.ordinalNumber)
        allAwardsForCycleDict = self.rankedController.getAllAwardsForCycle(cycleID=cycle.ID)
        crystalCount = allAwardsForCycleDict.pop(Currency.CRYSTAL, {'count': 0}).get('count')
        allAwardsForCycleVO = self.__formatBonusVO(allAwardsForCycleDict)
        return {'descriptionTxt': text_styles.stats(RANKED_BATTLES.RANKEDAWARDS_AWARDSBLOCK_DESCRIPTION),
         'titleTxt': text_styles.promoSubTitle(titleTxtStr),
         'pointsTxt': text_styles.superPromoTitle(str(cycle.points)),
         'crystalsTxt': text_styles.superPromoTitle(str(crystalCount)),
         'rankIcon': {'imageSrc': rank.getIcon('medium'),
                      'smallImageSrc': rank.getIcon('small'),
                      'isEnabled': True,
                      'isMaster': rank.isMax(),
                      'rankID': str(rank.getID()),
                      'rankCount': str(getattr(rank, 'getSerialID', lambda : '')()),
                      'hasTooltip': False},
         'awards': awardsForTheLastRankVO,
         'awardsHeaderTxt': text_styles.highTitle(RANKED_BATTLES.RANKEDAWARDS_AWARDSBLOCK_AWARDSHEADERTXT),
         'crystalsImage': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_ICON_RANK_FINAL_PROXY_80X80,
         'pointsImage': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_ICON_FINAL_CUP_80X80,
         'pointsLabelTxt': text_styles.stats(RANKED_BATTLES.RANKEDAWARDS_AWARDSBLOCK_POINTS),
         'crystalsLabelTxt': text_styles.stats(RANKED_BATTLES.RANKEDAWARDS_AWARDSBLOCK_CRYSTAL),
         'boxImage': rank.getBoxIcon(size='120x100', isOpened=False),
         'ribbonAwards': allAwardsForCycleVO}

    def __buildCycleData(self, cycleID):
        if cycleID == FINAL_TAB:
            return self.__buildFinalBlock()
        cycle = self.__getCycle(int(cycleID))
        if cycle.status == CYCLE_STATUS.CURRENT:
            return self.__getCurrentCycle()
        return self.__getCycleWithoutAchievements(cycle) if cycle.points == 0 else self.__getPastCycleWithPoints(cycle)

    def __getCycleWithoutAchievements(self, cycle):
        if cycle.status == CYCLE_STATUS.PAST:
            text = _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_NOACHIEVEMENTS_PAST_FOOTER, points=text_styles.critical(0))
            isDateOff = True
            contentID = RANKEDBATTLES_ALIASES.PAST_MISSED
        else:
            dateFormatKey = RANKED_BATTLES.RANKEDBATTLEHEADER_TOOLTIP_DATE
            text = _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_NOACHIEVEMENTS_FUTURE_FOOTER, start=time_formatters.formatDate(dateFormatKey, cycle.startDate), end=time_formatters.formatDate(dateFormatKey, cycle.endDate))
            isDateOff = False
            contentID = RANKEDBATTLES_ALIASES.FUTURE
        return {'contentID': contentID,
         'nextStage': {'header': text_styles.promoSubTitle(_ms(RANKED_BATTLES.RANKEDBATTLEVIEW_NEXTSTAGEBLOCK_STAGE, cycleNumber=cycle.ordinalNumber)),
                       'calendarDay': time_formatters.formatDate('%d', cycle.startDate),
                       'dateOff': isDateOff,
                       'points': text_styles.main(text)},
         'awardsRibbon': None}

    def __getPastCycleWithPoints(self, cycle):
        return {'contentID': RANKEDBATTLES_ALIASES.PAST_COMPLETED,
         'awardsRibbon': self.__getAwardsRibbonBlock(cycle)}

    def __getCurrentCycle(self):
        return {'contentID': RANKEDBATTLES_ALIASES.CURRENT,
         'currentCycle': self.__getCurrentCycleData()}

    def __getCurrentCycleData(self):
        items = []
        for rank in self.rankedController.getRanksChain():
            if rank.getID() > 0:
                items.append(self.__getCurrentCycleRankRow(rank))

        items.append(self.__getCurrentCycleVehicleRankRow())
        cycleAwardInfo = makeTooltip(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_CURRENTCYCLE_TOOLTIP_CYCLEAWARD_HEADER, RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_CURRENTCYCLE_TOOLTIP_CYCLEAWARD_BODY)
        return {'items': items,
         'rank': _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_CURRENTCYCLE_TABLEHEADER_RANK),
         'rankAward': _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_CURRENTCYCLE_TABLEHEADER_RANKAWARD),
         'cycleAward': _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_CURRENTCYCLE_TABLEHEADER_CYCLEAWARD),
         'points': _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_CURRENTCYCLE_TABLEHEADER_POINTS),
         'pointsInfo': makeTooltip(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_CURRENTCYCLE_TOOLTIP_POINTS_HEADER, RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_CURRENTCYCLE_TOOLTIP_POINTS_BODY),
         'cycleAwardInfo': cycleAwardInfo}

    def __getCurrentCycleRankRow(self, rank):
        rankIcon = {'imageSrc': rank.getIcon('small'),
         'isEnabled': rank.isAcquired(),
         'rankID': str(rank.getID())}
        rankAwards = []
        if rank.isRewardClaimed() and rank.getQuest():
            receivedStr = ''.join([makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OKICON), text_styles.statInfo(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_CURRENTCYCLE_ITEM_AWARDRECIEVED)])
        else:
            receivedStr = ''
            rankAwards = rank.getAwardsVOs()
        if rank.isMax() and rank.getID() != 1:
            rankDescr = text_styles.main(RANKED_BATTLES.RANKEDBATTLEVIEW_PROGRESSBLOCK_BESTRANK)
        else:
            rankDescr = ''
        return {'awardReceived': receivedStr,
         'points': str(rank.getPoints()),
         'rankIcon': rankIcon,
         'rankDescr': rankDescr,
         'rankAwards': rankAwards,
         'cycleAwards': rank.getAwardsVOs(forCycleFinish=True)}

    def __getCurrentCycleVehicleRankRow(self):
        isMaxRank = self.rankedController.getCurrentRank(g_currentVehicle.item) == self.rankedController.getMaxRank()
        if self.rankedController.isAccountMastered() and not isMaxRank:
            vehicleRank = self.rankedController.getCurrentRank(g_currentVehicle.item)
        else:
            vehicleRank = first(self.rankedController.getVehicleRanksChain(g_currentVehicle.item))
        rankIcon = {'imageSrc': vehicleRank.getIcon('small'),
         'isEnabled': vehicleRank.isAcquired(),
         'rankID': str(vehicleRank.getID())}
        cycleColumnComment = text_styles.highlightText(_ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_CURRENTCYCLE_VEHICLERANKPOINTS))
        return {'awardReceived': '',
         'points': str(vehicleRank.getPoints()),
         'rankIcon': rankIcon,
         'rankDescr': '',
         'rankAwards': vehicleRank.getAwardsVOs(),
         'cycleAwards': [],
         'masterDescr': cycleColumnComment}

    def __buildFinalBlock(self):
        return {'contentID': RANKEDBATTLES_ALIASES.FINAL,
         'seasonAwards': self.__getSeasonAwardsData()}

    def __getSeasonAwardsData(self):
        header = text_styles.highTitle(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_DESCRIPTION_HEADER)
        body = text_styles.main(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_DESCRIPTION_BODY)
        items = []
        for cohortData in self.rankedController.getLeagueAwards():
            items.append(self.__packLeagueAwardsRow(cohortData))

        ladderBtnTooltip = makeTooltip(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_BTNLADDERTOOLTIP_HEADER, RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_BTNLADDERTOOLTIP_BODY)
        return {'description': header + '\n' + body,
         'ladderBtn': _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_BTNLADDER),
         'ladderBtnTooltip': ladderBtnTooltip,
         'ladderPosition': text_styles.stats(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_TABLEHEADER_POSITION),
         'seasonAward': text_styles.stats(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_TABLEHEADER_SEASONAWARD),
         'items': items}

    def __packLeagueAwardsRow(self, cohortData):
        cohortNumber = cohortData['cohortNumber']
        if cohortNumber < 4:
            icon = RES_ICONS.getRankedLeagueCohortIcon(cohortNumber)
            count = '{}%'.format(cohortData['playersPercent'])
            if cohortNumber == 1:
                description = _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_FIRST, count=count)
            else:
                description = _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_INTERMEDIATE, count=count)
        else:
            icon = ''
            description = _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_LAST)
        return {'icon': icon,
         'iconDescr': text_styles.hightlight(description),
         'awards': cohortData['awards']}

    def __getSeason(self):
        return self.rankedController.getCurrentSeason()

    def __getCycles(self):
        return self.__getSeason().getAllCycles()

    def __getCycle(self, cycleID):
        return self.__getCycles().get(cycleID)

    def __packAwards(self, cycle):
        quests = self.rankedController.getQuestsForCycle(cycle.ID, completedOnly=True).values()
        bonusesDict = self.__extractBonusesForAwardRibbon(quests)
        vehicleQuest = self.rankedController.getVehicleQuestForCycle(cycle.ID)
        vehBonuses = self.__extractBonusesForAwardRibbon([vehicleQuest] if vehicleQuest else [])
        mastersCount = self.rankedController.getVehicleMastersCount(cycle.ID)
        for imgSource, bonusInfo in vehBonuses.iteritems():
            if imgSource not in bonusesDict:
                bonusesDict[imgSource] = bonusInfo
            bonusesDict[imgSource]['count'] = bonusInfo['count'] * mastersCount

        return self.__formatBonusVO(bonusesDict)

    @staticmethod
    def __formatBonusVO(bonusesDict):
        result = []
        for bonusVO in bonusesDict.values():
            bonusVO['label'] = text_styles.hightlight('x{}'.format(bonusVO.pop('count')))
            bonusVO['align'] = TEXT_ALIGN.RIGHT
            result.append(bonusVO)

        return result

    @staticmethod
    def __extractBonusesForAwardRibbon(quests):
        bonusesDict = {}
        for quest in quests:
            for bonus in quest.getBonuses():
                for awardVO in bonus.getRankedAwardVOs(iconSize='big', withCounts=True, withKey=True):
                    itemKey = awardVO.pop('itemKey')
                    if itemKey in bonusesDict:
                        bonusesDict[itemKey]['count'] += awardVO['count']
                    bonusesDict[itemKey] = awardVO

        return bonusesDict
