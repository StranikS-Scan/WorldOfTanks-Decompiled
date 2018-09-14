# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/RankedBattlesView.py
import BigWorld
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.RankedBattlesViewMeta import RankedBattlesViewMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.ranked_battles.ranked_models import RANK_STATUS
from gui.server_events.events_dispatcher import showMissionDetails
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events, g_eventBus
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import i18n, dependency, int2roman
from helpers import time_utils
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IRankedBattlesController
from gui.ranked_battles.ranked_models import VehicleRank
from skeletons.gui.shared import IItemsCache

class _AWARD_BLOCK_IDS():
    WEB_LEAGUE = 'web_league'
    BOOBY_QUEST = 'booby_quest'
    SEASON_AWARDS = 'season_awards'


class RankedBattlesView(LobbySubView, RankedBattlesViewMeta):
    __background_alpha__ = 0.5
    itemsCache = dependency.descriptor(IItemsCache)
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, ctx=None):
        super(RankedBattlesView, self).__init__()

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
                showMissionDetails(eventID=consolationQuest.getID(), groupID=consolationQuest.getGroupID())
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
        hasProgress = self.rankedController.hasProgress() or self.itemsCache.items.getAccountDossier().getRankedStats().hasAchievedRank()
        season = self.rankedController.getCurrentSeason()
        self.as_setDataS({'isHasProgress': hasProgress,
         'header': text_styles.superPromoTitle(RANKED_BATTLES.RANKEDBATTLEVIEW_TITLE) % {'cycle': season.getCycleOrdinalNumber()},
         'closeLbl': RANKED_BATTLES.RANKEDBATTLEVIEW_CLOSEBTN,
         'closeDescr': RANKED_BATTLES.RANKEDBATTLEVIEW_CLOSEBTNDESCR,
         'calendarStatus': self.__getStatusBlock(),
         'progressBlock': self.__buildProgressData(),
         'awardsBlock': self.__getAwardsBlock(leagueData) if hasProgress else [],
         'notRankedBlock': self.__getNotRankedBlock() if not hasProgress else {},
         'bgImgPath': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_BG_RANK_BLUR,
         'isUpdateProgress': False})

    def __updateData(self):
        self.__setData()
        self.rankedController.getLeagueData()(self.__setData)

    def __updateProgress(self):
        self.as_setDataS({'progressBlock': self.__buildProgressData(),
         'isUpdateProgress': True})

    def __getNotRankedBlock(self):
        return {'imageWin': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKEDBATTESVIEW_ICON_TOP12_106X98,
         'imageLose': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKEDBATTESVIEW_ICON_TOP3_106X98,
         'headerText': text_styles.promoSubTitle(RANKED_BATTLES.RANKEDBATTLEVIEW_NOTRANKEDBLOCK_HEADER),
         'orText': text_styles.promoSubTitle(RANKED_BATTLES.RANKEDBATTLEVIEW_NOTRANKEDBLOCK_OR),
         'okLabel': RANKED_BATTLES.RANKEDBATTLEVIEW_NOTRANKEDBLOCK_OKLABEL,
         'winText': self.__getNotRankedBlockText(),
         'loseText': self.__getNotRankedBlockText(False)}

    def __close(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def __getStatusBlock(self):
        return {'statusText': self.__getStatusText(),
         'calendarTooltip': makeTooltip(RANKED_BATTLES.RANKEDBATTLEVIEW_STATUSBLOCK_CALENDARBTNTOOLTIP_HEADER, RANKED_BATTLES.RANKEDBATTLEVIEW_STATUSBLOCK_CALENDARBTNTOOLTIP_BODY),
         'calendarIcon': RES_ICONS.MAPS_ICONS_BUTTONS_CALENDAR}

    def __buildProgressData(self):
        result = []
        subBlockArrow = {'linkage': 'DisabledRankArrowUI'}
        if self.rankedController.isAccountMastered():
            vehicle = g_currentVehicle.item
            currentRank = self.rankedController.getCurrentRank(vehicle)
            nextRank = self.rankedController.getRank(currentRank.getID() + 1, vehicle)
            result.append(self.__packRank(currentRank, True))
            progress = nextRank.getProgress()
            result.append(self.__getStepsProgressSubBlock(len(progress.getAcquiredSteps()), len(progress.getSteps())))
            awards = nextRank.getAwardsVOs()
            result.append(self.__packRank(nextRank, True, awards=awards))
        else:
            currentRank = self.rankedController.getCurrentRank()
            nextRank = self.rankedController.getRank(currentRank.getID() + 1)
            for rank in self.rankedController.getRanksChain():
                if rank.getID() == 0:
                    continue
                isBig = rank.isCurrent()
                awards = []
                if rank.getID() == nextRank.getID():
                    isBig = True
                    progress = nextRank.getProgress()
                    result.append(self.__getStepsProgressSubBlock(len(progress.getAcquiredSteps()), len(progress.getSteps()), showDescription=bool(rank.getID() > 1)))
                    if not rank.isRewardClaimed():
                        awards = rank.getAwardsVOs()
                elif rank.getID() > 1:
                    result.append(subBlockArrow)
                result.append(self.__packRank(rank, isBig, awards=awards))

        return result

    def __packRank(self, rank, isBig, awards=None):
        descriptionIcon = RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICONFILLED
        isAchieved = rank.getStatus() == RANK_STATUS.ACHIEVED
        isMaster = isinstance(rank, VehicleRank)
        imageBG = ''
        description = ''
        if awards is None:
            awards = []
        imageBig = ''
        imageSmall = ''
        rankCount = ''
        if isBig:
            imageBig = rank.getIcon('big')
            isTransparent = False
            if isAchieved:
                imageBG = RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKEDBATTESVIEW_PIC_ICON_RANK_SHINE_364X364
                if isMaster:
                    rankCount = BigWorld.wg_getIntegralFormat(rank.getSerialID())
                else:
                    description = text_styles.standard(RANKED_BATTLES.RANKEDBATTLEVIEW_PROGRESSBLOCK_CURRENTRANK)
            elif isMaster:
                description = text_styles.standard(rank.getUserName())
        else:
            imageSmall = rank.getIcon('small')
            isTransparent = True
        if rank.isMax() and description == '' and not isMaster:
            description = text_styles.standard(RANKED_BATTLES.RANKEDBATTLEVIEW_PROGRESSBLOCK_BESTRANK)
        return {'linkage': 'RankUI',
         'rankData': {'rankVO': {'rankID': str(rank.getID()),
                                 'imageSrc': imageBig,
                                 'smallImageSrc': imageSmall,
                                 'isEnabled': isAchieved,
                                 'isMaster': isMaster,
                                 'rankCount': rankCount},
                      'isBig': isBig,
                      'imageBG': imageBG,
                      'description': description,
                      'awardPreviews': awards,
                      'isTransparent': isTransparent,
                      'curIcon': descriptionIcon if description and rank.isCurrent() and rank.canBeLost() else ''}}

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
        seasonInfo = self.rankedController.getCurrentSeason()
        seasonData = {'passedCycles': seasonInfo.getPassedCyclesNumber(),
         'totalCycles': len(seasonInfo.getAllCycles())}
        return _AwardsBlockBuilder.pack(leagueData, consolationQuestBattlesLeft, seasonData)

    def __getNotRankedBlockText(self, isWin=True):
        if isWin:
            key = RANKED_BATTLES.RANKEDBATTLEVIEW_NOTRANKEDBLOCK_WINTEXT
        else:
            key = RANKED_BATTLES.RANKEDBATTLEVIEW_NOTRANKEDBLOCK_LOSETEXT
        if isWin:
            keyword = text_styles.bonusAppliedText(RANKED_BATTLES.RANKEDBATTLEVIEW_NOTRANKEDBLOCK_WINTEXT_HIGHLIGHTED)
        else:
            keyword = text_styles.error(RANKED_BATTLES.RANKEDBATTLEVIEW_NOTRANKEDBLOCK_LOSETEXT_HIGHLIGHTED)
        return i18n.makeString(key, team=keyword)

    def __getStatusText(self):
        season = self.rankedController.getCurrentSeason()
        endTimeStr = self.__getTillTimeString(season.getCycleEndDate())
        cycleNumber = season.getCycleOrdinalNumber()
        key = RANKED_BATTLES.RANKEDBATTLEVIEW_STATUSBLOCK_STATUSTEXT
        return text_styles.stats(i18n.makeString(key, cycleNumber=cycleNumber)) + endTimeStr

    def __getTillTimeString(self, endTime):
        timeDelta = time_utils.getTimeDeltaFromNow(endTime)
        if timeDelta > time_utils.ONE_DAY:
            formatter = text_styles.neutral
        else:
            formatter = text_styles.alert
        return formatter(time_utils.getTillTimeString(timeDelta, RANKED_BATTLES.STATUS_TIMELEFT))


class _AwardsBlockBuilder(object):

    @classmethod
    def pack(cls, leagueData, battlesLeft, seasonData):
        return [cls.__packWebLeagueBlock(leagueData), cls.__packQuestAwardBlock(battlesLeft), cls.__packSeasonAwardBlock(seasonData)]

    @classmethod
    def __packWebLeagueBlock(cls, leagueData):
        if leagueData is not None:
            leagueNumber = leagueData.get('league', 0)
            if leagueNumber > 0:
                leagueNumber = int2roman(leagueNumber)
            else:
                leagueNumber = _ms(RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_EMPTYLEAGUE)
            description = text_styles.main(RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_POINTS_DESCRIPTION)
            value = text_styles.promoTitle(leagueNumber)
        else:
            description = text_styles.main(RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_POINTSALT_DESCRIPTION)
            value = ''
        return cls.__packBlockData(_AWARD_BLOCK_IDS.WEB_LEAGUE, {'image': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKEDBATTESVIEW_ICON_RANKS_LADDERS_208X100,
         'header': text_styles.highTitle(RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_POINTS_HEADER),
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
    def __packSeasonAwardBlock(cls, seasonData):
        passedCycles = text_styles.promoTitle(seasonData['passedCycles'])
        totalCycles = text_styles.highTitle(seasonData['totalCycles'])
        delimiter = text_styles.highTitle(' / ')
        value = passedCycles + delimiter + totalCycles
        return cls.__packBlockData(_AWARD_BLOCK_IDS.SEASON_AWARDS, {'image': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKEDBATTESVIEW_GIFT_BOX_208X100,
         'header': text_styles.highTitle(RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_SEASONAWARD_HEADER),
         'description': text_styles.main(RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_SEASONAWARD_DESCRIPTION),
         'value': text_styles.promoTitle(value)})

    @classmethod
    def __packBlockData(cls, blockID, data):
        result = {'image': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKEDBATTESVIEW_ICON_RANKS_LADDERS_208X100,
         'header': text_styles.highTitle(RANKED_BATTLES.RANKEDBATTLEVIEW_AWARDBLOCK_POINTS_HEADER),
         'awardID': blockID}
        result.update(data)
        return result
