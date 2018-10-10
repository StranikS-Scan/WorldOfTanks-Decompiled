# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/RankedBattlesCyclesView.py
from CurrentVehicle import g_currentVehicle
from adisp import process
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.meta.RankedBattlesCyclesViewMeta import RankedBattlesCyclesViewMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.ranked_battles.awards_formatters import getRankedQuestsOrderedAwards
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles as _ts
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers.i18n import makeString as _ms
from shared_utils import first
from skeletons.gui.game_control import IRankedBattlesController
from gui.shared.formatters.icons import makeImageTag
FINAL_TAB = 'final'

class RankedBattlesCyclesView(LobbySubView, RankedBattlesCyclesViewMeta):
    __background_alpha__ = 1
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, ctx=None):
        super(RankedBattlesCyclesView, self).__init__(ctx)
        self.__leagueData = None
        self.__leagueDataReceived = False
        self.__currentTab = None
        self.__currentRank = None
        self.__currentAccRank = None
        return

    def onEscapePress(self):
        self.__close()

    def onCloseBtnClick(self):
        self.__close()

    def onTabClick(self, tabID):
        self.__currentTab = tabID
        self.as_updateTabContentS(self.__buildCycleData())

    def onLadderBtnClick(self):
        self.rankedController.openWebLeaguePage(ctx={'returnAlias': RANKEDBATTLES_ALIASES.RANKED_BATTLES_CYCLES_VIEW_ALIAS})

    def _populate(self):
        self.__currentRank = self.rankedController.getCurrentRank(g_currentVehicle.item)
        self.__currentAccRank = self.rankedController.getCurrentRank()
        self.as_setDataS(self.__getStartData())
        self.__requestWebLeagueData()
        super(RankedBattlesCyclesView, self)._populate()

    @process
    def __requestWebLeagueData(self):
        self.__leagueData = yield self.rankedController.getLeagueData()
        self.__leagueDataReceived = True
        if self.__currentTab == FINAL_TAB:
            self.as_updateTabContentS(self.__buildCycleData())

    def __getStartData(self):
        staticData = {'statusText': _ts.superPromoTitle(_ms(RANKED_BATTLES.RANKEDBATTLECYCLESVIEW_TITLE)),
         'closeBtn': _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_BTNCLOSE),
         'bgImage': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_BG_RANK_BLUR}
        self.__currentTab = self.__getSeason().getCycleID()
        staticData.update(self.__buildCycleData())
        return staticData

    def __getTabs(self):
        cycleIDS = sorted([ cycle.ID for cycle in self.__getSeason().getAllCycles().values() ])
        cycleIDS.append(FINAL_TAB)
        return [ self.__getHeaderTab(cycleID) for cycleID in cycleIDS ]

    def __getHeaderTab(self, cycleID):
        if cycleID == FINAL_TAB:
            title = _ms(RANKED_BATTLES.RANKEDBATTLECYCLESVIEW_TABS_FINAL)
        else:
            title = _ms(RANKED_BATTLES.RANKEDBATTLECYCLESVIEW_TABS_RANKS)
        return {'title': title,
         'id': str(cycleID)}

    def __close(self):
        self.fireEvent(events.LoadViewEvent(RANKEDBATTLES_ALIASES.RANKED_BATTLES_VIEW_ALIAS), scope=EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def __buildCycleData(self):
        return self.__buildFinalBlock() if self.__currentTab == FINAL_TAB else self.__getCurrentCycle()

    def __getCurrentCycle(self):
        return {'contentID': RANKEDBATTLES_ALIASES.CURRENT,
         'currentCycle': self.__getCurrentCycleData()}

    def __getCurrentCycleData(self):
        items = [ self.__packRankRow(rank) for rank in self.rankedController.getRanksChain() if rank.getID() > 0 ]
        items.append(self.__getCurrentCycleVehicleRankRow())
        return {'items': items,
         'rank': _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_CURRENTCYCLE_TABLEHEADER_RANK),
         'rankAward': _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_CURRENTCYCLE_TABLEHEADER_RANKAWARD),
         'selectedIdx': self.__currentAccRank.getID() - 1}

    def __packRankRow(self, rank):
        rankIcon = {'imageSrc': rank.getIcon('small'),
         'isEnabled': rank.isAcquired(),
         'rankID': str(rank.getID())}
        rankAwards = rank.getAwardsVOs()
        if rank.getQuest():
            rankAwards = getRankedQuestsOrderedAwards([rank.getQuest()])
        if rank.isRewardClaimed() and rank.getQuest():
            receivedStr = ''.join([makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OKICON), _ts.statInfo(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_CURRENTCYCLE_ITEM_AWARDRECIEVED)])
        else:
            receivedStr = ''
        rankID = rank.getID()
        isCurrent = rankID == self.__currentAccRank.getID()
        if rank.isMax() and rankID != 1:
            rankDescr = _ts.main(RANKED_BATTLES.RANKEDBATTLEVIEW_PROGRESSBLOCK_BESTRANK)
        else:
            rankDescr = ''
        return {'rankIcon': rankIcon,
         'rankDescr': rankDescr,
         'rankAwards': rankAwards,
         'receivedStatus': receivedStr,
         'isCurrent': isCurrent,
         'rankNumber': _ts.main(str(rankID))}

    def __getCurrentCycleVehicleRankRow(self):
        isMaxRank = self.__currentRank == self.rankedController.getMaxRank()
        isAccountMastered = self.rankedController.isAccountMastered()
        if isAccountMastered:
            status = _ts.statInfo(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_CURRENTCYCLE_VEHICLERANKCOMMENT)
        else:
            status = ''
        if isAccountMastered and not isMaxRank:
            vehicleRank = self.__currentRank
        else:
            vehicleRank = first(self.rankedController.getVehicleRanksChain(g_currentVehicle.item))
        rankIcon = {'imageSrc': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_ICON_FINAL_CUP_100X100,
         'isEnabled': True,
         'rankID': str(self.rankedController.getAccRanksTotal() + 1)}
        return {'rankIcon': rankIcon,
         'rankDescr': '',
         'rankAwards': vehicleRank.getAwardsVOs(),
         'receivedStatus': status,
         'isCurrent': False,
         'rankNumber': ''}

    def __buildFinalBlock(self):
        return {'contentID': RANKEDBATTLES_ALIASES.FINAL,
         'seasonAwards': self.__getSeasonAwardsData()}

    def __getSeasonAwardsData(self):
        items = []
        for cohortData in self.rankedController.getLeagueAwards():
            items.append(self.__packLeagueAwardsRow(cohortData))

        result = {'ladderPosition': _ts.middleTitle(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_TABLEHEADER_POSITION),
         'seasonAward': _ts.middleTitle(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_TABLEHEADER_SEASONAWARD),
         'items': items}
        if not self.__leagueData:
            result['ladderPosition'] += ' ' + makeImageTag(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_ALERT_ICON)
            result['noDataTooltip'] = _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_TABLEHEADER_NOLEAGUEDATATOOLTIP)
        return result

    def __packLeagueAwardsRow(self, cohortData):
        cohortNumber = cohortData['cohortNumber']
        icon = RES_ICONS.getRankedLeagueCohortIcon(cohortNumber)
        if cohortNumber > 0:
            count = '{}%'.format(cohortData['playersPercent'])
            if cohortNumber == 1:
                description = _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_FIRST, count=count)
            else:
                description = _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_INTERMEDIATE, count=count)
        else:
            description = _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_LAST)
        result = {'icon': icon,
         'iconDescr': _ts.counter(description),
         'awards': cohortData['awards']}
        if cohortNumber == 0:
            result['noLeagueText'] = _ts.main(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_LASTCOMMENT)
        if self.__leagueDataReceived and self.__leagueData is not None:
            if self.__leagueData['league'] == cohortNumber:
                result.update({'highlighted': True,
                 'ladderBtn': _ms(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_BTNLADDER),
                 'ladderBtnTooltip': makeTooltip(RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_BTNLADDERTOOLTIP_HEADER, RANKED_BATTLES.RANKEDBATTLESCYCLESVIEW_FINAL_BTNLADDERTOOLTIP_BODY)})
        return result

    def __getSeason(self):
        return self.rankedController.getCurrentSeason()
