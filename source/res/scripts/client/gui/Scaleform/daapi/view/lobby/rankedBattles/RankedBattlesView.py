# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/RankedBattlesView.py
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.RankedBattlesViewMeta import RankedBattlesViewMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.ranked_battles.constants import PRIME_TIME_STATUS
from gui.ranked_battles.ranked_helpers import buildRankVO
from gui.server_events.events_dispatcher import showMissionDetails
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events, g_eventBus
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip
from helpers import i18n, dependency
from helpers import time_utils
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.shared import IItemsCache

class _AWARD_BLOCK_IDS(object):
    WEB_LEAGUE = 'web_league'
    BOOBY_QUEST = 'booby_quest'
    SEASON_AWARDS = 'season_awards'


class RankedBattlesView(LobbySubView, RankedBattlesViewMeta):
    __background_alpha__ = 0.5
    itemsCache = dependency.descriptor(IItemsCache)
    rankedController = dependency.descriptor(IRankedBattlesController)

    def onEscapePress(self):
        self.__close()

    def onCloseBtnClick(self):
        self.__close()

    def onAwardClick(self, blockID):
        if blockID == _AWARD_BLOCK_IDS.WEB_LEAGUE:
            self.rankedController.openWebLeaguePage(ctx={'returnAlias': RANKEDBATTLES_ALIASES.RANKED_BATTLES_VIEW_ALIAS})
        elif blockID == _AWARD_BLOCK_IDS.BOOBY_QUEST:
            consolationQuest = self.rankedController.getConsolationQuest()
            if consolationQuest is not None:
                showMissionDetails(missionID=consolationQuest.getID(), groupID=consolationQuest.getGroupID())
        elif blockID == _AWARD_BLOCK_IDS.SEASON_AWARDS:
            g_eventBus.handleEvent(events.LoadViewEvent(RANKEDBATTLES_ALIASES.RANKED_BATTLES_CYCLES_VIEW_ALIAS), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def _populate(self):
        super(RankedBattlesView, self)._populate()
        self.rankedController.onUpdated += self.__updateData
        self.__updateData()

    def _dispose(self):
        self.rankedController.onUpdated -= self.__updateData
        super(RankedBattlesView, self)._dispose()

    def __setData(self, leagueData=None):
        self.as_setDataS({'header': text_styles.superPromoTitle(RANKED_BATTLES.RANKEDBATTLEVIEW_TITLE),
         'closeLbl': RANKED_BATTLES.RANKEDBATTLEVIEW_CLOSEBTN,
         'closeDescr': RANKED_BATTLES.RANKEDBATTLEVIEW_CLOSEBTNDESCR,
         'playVideoLbl': RANKED_BATTLES.RANKEDBATTLEVIEW_PLAYVIDEOBTN,
         'playVideoBtnEnabled': False,
         'calendarStatus': self.__getStatusBlock(),
         'progressBlock': self.__buildProgressData(),
         'awardsBlock': self.__getAwardsBlock(leagueData),
         'bgImgPath': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_BG_RANK_BLUR,
         'isUpdateProgress': False})

    def __updateData(self):
        self.__setData()
        self.rankedController.getLeagueData()(self.__setData)

    def __updateProgress(self):
        self.as_setDataS({'progressBlock': self.__buildProgressData(),
         'isUpdateProgress': True})

    def __close(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def __getStatusBlock(self):
        status, timeLeft, _ = self.rankedController.getPrimeTimeStatus()
        showPrimeTimeAlert = status != PRIME_TIME_STATUS.AVAILABLE
        return {'alertIcon': RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON if showPrimeTimeAlert else None,
         'buttonIcon': RES_ICONS.MAPS_ICONS_BUTTONS_CALENDAR,
         'buttonLabel': '',
         'buttonVisible': True,
         'buttonTooltip': makeTooltip(RANKED_BATTLES.RANKEDBATTLEVIEW_STATUSBLOCK_CALENDARBTNTOOLTIP_HEADER, RANKED_BATTLES.RANKEDBATTLEVIEW_STATUSBLOCK_CALENDARBTNTOOLTIP_BODY),
         'statusText': self.__getAlertStatusText(timeLeft) if showPrimeTimeAlert else self.__getStatusText(),
         'popoverAlias': RANKEDBATTLES_ALIASES.RANKED_BATTLES_CALENDAR_POPOVER,
         'bgVisible': False,
         'shadowFilterVisible': showPrimeTimeAlert}

    def __buildProgressData(self):
        rank = self.rankedController.getCurrentRank()
        rankID = rank.getID()
        rankLabel = ''
        if self.rankedController.isAccountMastered():
            blocks = [self.__packProgressInfo(RES_ICONS.MAPS_ICONS_RANKEDBATTLES_ICON_VICTORY, text_styles.vehicleName(_ms(RANKED_BATTLES.RANKEDBATTLEVIEW_PROGRESSBLOCK_FINALRANK, rank=rankID))), self.__packRank(rank), self.__packProgressInfo(RES_ICONS.MAPS_ICONS_RANKEDBATTLES_ICON_FINAL_CUP_150X100, text_styles.vehicleName(_ms(RANKED_BATTLES.RANKEDBATTLEVIEW_PROGRESSBLOCK_CONTINUE)))]
        else:
            blocks = [ self.__packRank(rank) for rank in self.rankedController.getRanksChain() if rank.getID() != 0 ]
            if rankID > 0:
                rankLabel = text_styles.neutral(_ms(RANKED_BATTLES.RANKEDBATTLEVIEW_PROGRESSBLOCK_CURRENTRANK, rank=text_styles.stats(rankID)))
        return {'blocks': blocks,
         'currentRankLabel': rankLabel}

    def __packRank(self, rank):
        isCurrent = rank.isCurrent()
        isFinal = isCurrent and rank.getID() == self.rankedController.getAccRanksTotal()
        bgImage = ''
        if isCurrent or isFinal:
            bgImage = RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKEDBATTESVIEW_PIC_ICON_RANK_SHINE_364X364
        imageSize = RANKEDBATTLES_ALIASES.WIDGET_SMALL
        if isCurrent:
            imageSize = RANKEDBATTLES_ALIASES.WIDGET_HUGE if isFinal else RANKEDBATTLES_ALIASES.WIDGET_BIG
        shieldStatus = self.rankedController.getShieldStatus(rank=rank, isStatic=True) if not isFinal else None
        return {'linkage': 'RankUI',
         'rankData': {'rankVO': buildRankVO(rank, isEnabled=rank.isAcquired(), imageSize=imageSize, shieldStatus=shieldStatus, showShieldLabel=False, showLadderPoints=True),
                      'isBig': isCurrent or isFinal,
                      'isFinal': isFinal,
                      'imageBG': bgImage,
                      'description': '',
                      'isTransparent': not isCurrent,
                      'curIcon': ''}}

    def __packProgressInfo(self, image, description):
        return {'linkage': 'ProgressInfoBlockUI',
         'infoData': {'image': image,
                      'description': description}}

    def __getStepsProgressSubBlock(self, completedSteps, totalSteps, showDescription=True):
        if showDescription:
            stepsStr = text_styles.stats(completedSteps)
            description = text_styles.main(_ms(RANKED_BATTLES.RANKEDBATTLEVIEW_PROGRESSBLOCK_STEPS, numbers='{} / {}'.format(stepsStr, totalSteps)))
        else:
            description = ''
        steps = []
        for idx in xrange(1, totalSteps + 1):
            if idx <= completedSteps:
                steps.append({'state': RANKEDBATTLES_ALIASES.STEP_RECEIVED_STATE})
            steps.append({'state': RANKEDBATTLES_ALIASES.STEP_NOT_RECEIVED_STATE})

        return {'linkage': 'StepsContainerUI',
         'stepsData': {'countText': description,
                       'nextCountText': '',
                       'steps': steps}}

    def __getAwardsBlock(self, leagueData=None):
        consolationQuest = self.rankedController.getConsolationQuest()
        consolationQuestBattlesLeft = None
        if consolationQuest is not None and not consolationQuest.isCompleted():
            battlesCondition = consolationQuest.bonusCond.getConditions().find('battles')
            if battlesCondition is not None:
                progress = battlesCondition.getProgressPerGroup()
                if None in progress:
                    currCount, total, _, _ = progress[None]
                    consolationQuestBattlesLeft = total - currCount
        battlesPlayed = self.rankedController.getCurrentCycleStats()['battlesCount']
        return _AwardsBlockBuilder.pack(leagueData, consolationQuestBattlesLeft, battlesPlayed)

    def __getStatusText(self):
        season = self.rankedController.getCurrentSeason()
        endTimeStr = self.__getTillTimeString(season.getCycleEndDate())
        key = RANKED_BATTLES.RANKEDBATTLEVIEW_STATUSBLOCK_STATUSTEXT
        return text_styles.stats(i18n.makeString(key)) + endTimeStr

    def __getAlertStatusText(self, timeLeft):
        timeLeftStr = time_utils.getTillTimeString(timeLeft, RANKED_BATTLES.STATUS_TIMELEFT)
        return text_styles.vehicleStatusCriticalText(_ms(RANKED_BATTLES.PRIMETIMEALERTMESSAGEBLOCK_MESSAGE, time=timeLeftStr))

    def __getTillTimeString(self, endTime):
        timeDelta = time_utils.getTimeDeltaFromNow(endTime)
        if timeDelta > time_utils.ONE_DAY:
            formatter = text_styles.neutral
        else:
            formatter = text_styles.alert
        return formatter(time_utils.getTillTimeString(timeDelta, RANKED_BATTLES.STATUS_TIMELEFT))


class _AwardsBlockBuilder(object):

    @classmethod
    def pack(cls, leagueData, battlesLeft, battlesPlayed):
        return [cls.__packWebLeagueBlock(leagueData, battlesPlayed), cls.__packQuestAwardBlock(battlesLeft), cls.__packSeasonAwardBlock()]

    @classmethod
    def __packWebLeagueBlock(cls, leagueData, battlesPlayed):
        if battlesPlayed > 0:
            if leagueData is not None and 'league' in leagueData:
                leagueNumber = leagueData['league']
                image = RES_ICONS.getRankedWebLeagueIcon('medium', leagueNumber)
                if leagueNumber > 0:
                    headerKey = RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_POINTS_CURRLEAGUEHEADER
                else:
                    headerKey = RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_POINTS_NOPRISEHEADER
            else:
                image = RES_ICONS.MAPS_ICONS_RANKEDBATTLES_ICON_FINAL_CUP_150X100
                headerKey = RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_POINTS_NOLEAGUEHEADER
            description = ''
            value = '{} {} {}'.format(text_styles.main(RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_POINTS_TOTALLABEL), text_styles.stats(dependency.instance(IItemsCache).items.ranked.ladderPoints), icons.makeImageTag(RES_ICONS.MAPS_ICONS_RANKEDBATTLES_LADDER_POINT, 24, 24, -7, 0))
        else:
            image = RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKEDBATTESVIEW_ICON_RANKS_LADDERS_208X100
            headerKey = RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_POINTS_HEADER
            description = text_styles.main(RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_POINTSALT_DESCRIPTION)
            value = ''
        return cls.__packBlockData(_AWARD_BLOCK_IDS.WEB_LEAGUE, {'image': image,
         'header': text_styles.highTitle(headerKey),
         'description': description,
         'value': value})

    @classmethod
    def __packQuestAwardBlock(cls, battlesLeft):
        if battlesLeft is not None:
            value = text_styles.promoTitle(battlesLeft)
            description = RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_QUEST_DESCRIPTION_BATTLESLEFT
        else:
            description = RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_QUEST_DESCRIPTION_NOQUEST
            value = ''
        return cls.__packBlockData(_AWARD_BLOCK_IDS.BOOBY_QUEST, {'image': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKEDBATTESVIEW_ICON_RANKS_TASK_208X100,
         'header': text_styles.highTitle(RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_QUEST_HEADER),
         'description': text_styles.main(description),
         'value': value,
         'isAvailable': battlesLeft is not None})

    @classmethod
    def __packSeasonAwardBlock(cls):
        return cls.__packBlockData(_AWARD_BLOCK_IDS.SEASON_AWARDS, {'image': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKEDBATTESVIEW_GIFT_BOX_208X100,
         'header': text_styles.highTitle(RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_SEASONAWARD_HEADER),
         'description': text_styles.main(RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_SEASONAWARD_DESCRIPTION),
         'value': ''})

    @classmethod
    def __packBlockData(cls, blockID, data):
        result = {'image': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKEDBATTESVIEW_ICON_RANKS_LADDERS_208X100,
         'header': text_styles.highTitle(RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_POINTS_HEADER),
         'awardID': blockID}
        result.update(data)
        return result
