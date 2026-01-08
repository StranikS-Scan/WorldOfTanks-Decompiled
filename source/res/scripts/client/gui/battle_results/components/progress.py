# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/progress.py
import logging
import operator
from collections import namedtuple
from copy import deepcopy
from itertools import chain
import typing
import personal_missions
from battle_pass_common import BattlePassConsts, isPostProgressionChapter
from constants import EVENT_TYPE
from gui.Scaleform.daapi.view.lobby.customization.progression_helpers import getC11nProgressionLinkBtnParams, parseEventID, getC11n2dProgressionLinkBtnParams, getProgressiveCustomizationProgress
from gui.Scaleform.daapi.view.lobby.server_events.awards_formatters import BattlePassTextBonusesPacker
from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import getEventPostBattleInfo, get2dProgressionStylePostBattleInfo
from gui.Scaleform.genConsts.MISSIONS_STATES import MISSIONS_STATES
from gui.Scaleform.genConsts.PROGRESSIVEREWARD_CONSTANTS import PROGRESSIVEREWARD_CONSTANTS as prConst
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.battle_results.components import base
from gui.battle_results.progress.progress_helpers import getDogTagsProgress, getPrestigeProgress, isQuestCompleted, packQuestProgressData, PrestigeProgress
from gui.battle_results.progress.research import MIN_BATTLES_TO_SHOW_PROGRESS, VehicleProgressHelper
from gui.battle_results.progress.progress_filters import battleMattersProgressFilter
from gui.battle_results.settings import PROGRESS_ACTION
from gui.dog_tag_composer import dogTagComposer
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import getProgressiveRewardVO
from gui.impl.gen import R
from gui.server_events import formatters
from gui.server_events.awards_formatters import QuestsBonusComposer
from gui.server_events.events_helpers import getDataByC11nQuest, isC11nQuest
from gui.shared.formatters import getItemUnlockPricesVO, text_styles
from gui.shared.gui_items import Tankman
from gui.shared.gui_items.Vehicle import getLevelIconPath
from gui.shared.gui_items.crew_skin import localizedFullName
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, Tuple
    from gui.battle_results.reusable import _ReusableInfo
    from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import BattlePassProgress
_POST_BATTLE_RES = R.strings.battle_pass.reward.postBattle
_logger = logging.getLogger(__name__)

def _makeTankmanDescription(roleName, fullName):
    role = text_styles.main(roleName)
    name = text_styles.standard(fullName)
    return _ms(BATTLE_RESULTS.COMMON_CREWMEMBER_DESCRIPTION, name=name, role=role)


def _makeVehicleDescription(vehicle):
    vehicleType = text_styles.standard(vehicle.typeUserName)
    vehicleName = text_styles.main(vehicle.userName)
    return _ms(BATTLE_RESULTS.COMMON_VEHICLE_DETAILS, vehicle=vehicleName, type=vehicleType)


def _makeTankmanVO(tman, newSkillEarned, bonusSkillsAmount, avgBattles2NewSkill, skinItem):
    prediction = ''
    if 0 < avgBattles2NewSkill <= MIN_BATTLES_TO_SHOW_PROGRESS:
        prediction = _ms(BATTLE_RESULTS.COMMON_NEWSKILLPREDICTION, battles=backport.getIntegralFormat(avgBattles2NewSkill))
    data = {'linkId': tman.invID}
    if newSkillEarned:
        data.update({'title': _ms(BATTLE_RESULTS.COMMON_CREWMEMBER_NEWSKILL),
         'prediction': prediction,
         'linkEvent': PROGRESS_ACTION.NEW_SKILL_UNLOCK_TYPE,
         'bonusSkillsAmount': bonusSkillsAmount})
    if skinItem is not None:
        data['tankmenIcon'] = Tankman.getCrewSkinIconBig(skinItem.getIconID())
        fullTankmanName = localizedFullName(skinItem)
    else:
        data['tankmenIcon'] = Tankman.getBarracksIconPath(tman.nationID, tman.descriptor.iconID)
        fullTankmanName = tman.fullUserName
    data['description'] = _makeTankmanDescription(tman.roleUserName, fullTankmanName)
    return data


def _makeUnlockModuleVO(item, unlockProps):
    return {'title': _ms(BATTLE_RESULTS.COMMON_FITTING_RESEARCH),
     'description': text_styles.main(item.userName),
     'fittingType': item.getGUIEmblemID(),
     'lvlIcon': getLevelIconPath(item.level),
     'price': getItemUnlockPricesVO(unlockProps),
     'linkEvent': PROGRESS_ACTION.RESEARCH_UNLOCK_TYPE,
     'linkId': unlockProps.parentID}


def _makeUnlockVehicleVO(item, unlockProps, avgBattlesTillUnlock):
    prediction = ''
    if avgBattlesTillUnlock > 0:
        prediction = _ms(BATTLE_RESULTS.COMMON_RESEARCHPREDICTION, battles=avgBattlesTillUnlock)
    return {'title': _ms(BATTLE_RESULTS.COMMON_VEHICLE_RESEARCH),
     'description': _makeVehicleDescription(item),
     'vehicleIcon': item.iconSmall,
     'lvlIcon': getLevelIconPath(item.level),
     'prediction': prediction,
     'price': getItemUnlockPricesVO(unlockProps),
     'linkEvent': PROGRESS_ACTION.RESEARCH_UNLOCK_TYPE,
     'linkId': unlockProps.parentID}


class VehicleProgressBlock(base.StatsBlock):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    def getVO(self):
        vo = super(VehicleProgressBlock, self).getVO()
        for item in vo:
            isNewEarnedSkill = item.get('linkEvent') == PROGRESS_ACTION.NEW_SKILL_UNLOCK_TYPE
            if not isNewEarnedSkill:
                continue
            tankman = self._itemsCache.items.getTankman(item['linkId'])
            item['linkBtnEnabled'] = tankman.canLearnSkills()

        return vo

    def setRecord(self, result, reusable):
        xpEarnings = reusable.personal.xpProgress
        for intCD, _ in reusable.personal.getVehicleCDsIterator(result):
            xpEarningsForVehicle = xpEarnings.get(intCD, {})
            vehicleBattleXp = xpEarningsForVehicle.get('xp', 0)
            tmenXps = dict(xpEarningsForVehicle.get('xpByTmen', []))
            helper = VehicleProgressHelper(intCD)
            unlockVehicles, unlockModules = helper.getReady2UnlockItems(vehicleBattleXp)
            newTankmen = helper.getNewSkilledTankmen(tmenXps)
            for item in chain((_makeUnlockModuleVO(*item) for item in unlockModules if item), (_makeTankmanVO(*item) for item in newTankmen if item), (_makeUnlockVehicleVO(*item) for item in unlockVehicles if unlockVehicles)):
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', item))

            helper.clear()


PMComplete = namedtuple('PMComplete', ['isMainComplete', 'isAddComplete'])

class BattlePassProgressBlock(base.StatsBlock):
    __battlePass = dependency.descriptor(IBattlePassController)

    def setRecord(self, result, reusable):
        bpp = reusable.battlePassProgress
        if not bpp.hasProgress:
            return
        isNewPoints = bpp.pointsAux > 0 or bpp.questPoints > 0 or bpp.bonusCapPoints > 0 or bpp.bpTopPoints > 0
        if isNewPoints:
            self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem(*self.__formatBattlePassPoints(bpp)))
        if bpp.previousChapterID:
            chapterID = bpp.previousChapterID
            for lvl in xrange(bpp.getPreviousLevel(chapterID), bpp.getCurrentLevel(chapterID)):
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem(*self.__formatBattlePassProgress(bpp, lvl, chapterID)))

        if bpp.previousChapterID != bpp.currentChapterID and bpp.currentChapterID:
            chapterID = bpp.currentChapterID
            for lvl in xrange(bpp.getPreviousLevel(chapterID), bpp.getCurrentLevel(chapterID)):
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem(*self.__formatBattlePassProgress(bpp, lvl, chapterID)))

        chapterID = bpp.currentChapterID
        levelProgressPresents = bpp.getCurrentLevelPoints(chapterID) and bpp.getCurrentLevelPoints(chapterID) != bpp.getMaxLevelPoints(chapterID)
        if bpp.pointsAux or levelProgressPresents:
            self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem(*self.__formatBattlePassProgress(bpp, bpp.getCurrentLevel(chapterID), chapterID)))

    @classmethod
    def __formatBattlePassProgress(cls, progress, level, chapter):
        return ('', {'awards': cls.__makeProgressAwards(progress, chapter, level),
          'questInfo': cls.__makeProgressQuestInfo(progress, chapter, level),
          'questType': EVENT_TYPE.BATTLE_QUEST,
          'progressList': cls.__makeProgressList(progress, chapter, level),
          'questState': {'statusState': cls.__getMissionState(progress.isDone(chapterID=chapter))},
          'linkBtnTooltip': '' if progress.isApplied else backport.text(R.strings.battle_pass.progression.error()),
          'linkBtnEnabled': progress.isApplied})

    @classmethod
    def __formatBattlePassPoints(cls, progress):
        return ('', {'awards': [],
          'questInfo': cls.__makePointsInfo(progress),
          'questType': EVENT_TYPE.BATTLE_QUEST,
          'progressList': cls.__makePointsList(progress),
          'questState': {'statusState': MISSIONS_STATES.IN_PROGRESS},
          'linkBtnTooltip': '' if progress.isApplied else backport.text(R.strings.battle_pass.progression.error()),
          'linkBtnEnabled': progress.isApplied})

    @staticmethod
    def __makeProgressAwards(progress, chapter, level):
        nothing = []
        if level >= progress.getCurrentLevel(chapter):
            return nothing
        awards = progress.getLevelAwards(chapter, level + 1)
        if not awards:
            return nothing
        awardsList = QuestsBonusComposer(BattlePassTextBonusesPacker()).getPreformattedBonuses(awards)

        def makeUnavailableBlockData():
            return formatters.packTextBlock(text_styles.alert(backport.text(R.strings.quests.bonuses.notAvailable())))

        if awardsList:
            return [ award.getDict() for award in awardsList ]
        return [makeUnavailableBlockData().getDict()]

    @classmethod
    def __makeProgressQuestInfo(cls, progress, chapterID, level):
        isFreePoints = progress.pointsAux and not progress.isLevelMax(chapterID) or progress.isLevelMax(chapterID) and level == progress.getCurrentLevel(chapterID)
        isProgressDone = level < progress.getCurrentLevel(chapterID)
        if isFreePoints:
            title = backport.text(_POST_BATTLE_RES.title.free())
        elif not isPostProgressionChapter(chapterID):
            title = backport.text(_POST_BATTLE_RES.title(), level=level + 1, chapter=cls.__getChapterName(chapterID))
        else:
            level %= len(cls.__battlePass.getLevelsConfig(chapterID))
            title = backport.text(_POST_BATTLE_RES.title.postProgression(), level=level + 1)
        return {'status': cls.__getMissionState(isDone=isProgressDone),
         'questID': BattlePassConsts.FAKE_QUEST_ID,
         'rendererType': QUESTS_ALIASES.RENDERER_TYPE_QUEST,
         'eventType': EVENT_TYPE.BATTLE_QUEST,
         'maxProgrVal': progress.getMaxLevelPoints(chapterID),
         'tooltip': TOOLTIPS.QUESTS_RENDERER_LABEL,
         'description': title,
         'currentProgrVal': progress.getCurrentLevelPoints(chapterID),
         'tasksCount': -1,
         'progrBarType': cls.__getProgressBarType(not progress.isDone(chapterID)),
         'linkTooltip': TOOLTIPS.QUESTS_LINKBTN_BATTLEPASS if chapterID and not cls.__battlePass.isChapterCompleted(chapterID) else TOOLTIPS.QUESTS_LINKBTN_BATTLEPASS_SELECT}

    @classmethod
    def __makePointsInfo(cls, progress):
        chapterID = progress.previousChapterID
        return {'status': '',
         'questID': BattlePassConsts.FAKE_QUEST_ID,
         'eventType': EVENT_TYPE.BATTLE_QUEST,
         'description': backport.text(_POST_BATTLE_RES.progress.points()),
         'progrBarType': formatters.PROGRESS_BAR_TYPE.NONE,
         'tasksCount': -1,
         'linkTooltip': TOOLTIPS.QUESTS_LINKBTN_BATTLEPASS if chapterID and not cls.__battlePass.isChapterCompleted(chapterID) else TOOLTIPS.QUESTS_LINKBTN_BATTLEPASS_SELECT}

    @classmethod
    def __makeProgressList(cls, progress, chapter, level):
        isCurrentChapterLevel = level == progress.getCurrentLevel(chapter)
        isMaxChapterLevel = progress.isLevelMax(chapter)
        isFreePoints = progress.pointsAux and not isMaxChapterLevel or isMaxChapterLevel and isCurrentChapterLevel
        progressLevel = {'description': cls._getDescription(progress),
         'maxProgrVal': progress.getMaxLevelPoints(chapter),
         'progressDiff': '+ {}'.format(progress.getPointsDiff(chapter) if not isFreePoints else progress.pointsAux),
         'progressDiffTooltip': cls._getProgressDiffTooltip(progress, chapter),
         'currentProgrVal': progress.getCurrentLevelPoints(chapter),
         'progrBarType': cls.__getProgressBarType(not progress.pointsAux)}
        return [progressLevel] if not progress.isDone(chapter) or progress.pointsAux and not isMaxChapterLevel or isCurrentChapterLevel else []

    @classmethod
    def __makePointsList(cls, progress):
        progressList = []
        if progress.bpTopPoints > 0:
            description = backport.text(_POST_BATTLE_RES.progress.points.battle())
            tooltip = backport.text(_POST_BATTLE_RES.progress.battle.tooltip())
            points = progress.bpTopPoints
            progressList.append(cls.__getPointsInfo(description, tooltip, points))
        if progress.questPoints > 0:
            description = backport.text(_POST_BATTLE_RES.progress.points.quest())
            tooltip = backport.text(_POST_BATTLE_RES.progress.quests.tooltip())
            points = progress.questPoints
            progressList.append(cls.__getPointsInfo(description, tooltip, points))
        if progress.bonusCapPoints > 0:
            description = backport.text(_POST_BATTLE_RES.progress.points.bonus())
            tooltip = backport.text(_POST_BATTLE_RES.progress.bonus.tooltip())
            points = progress.bonusCapPoints
            progressList.append(cls.__getPointsInfo(description, tooltip, points))
        return progressList

    @staticmethod
    def __getPointsInfo(description, tooltip, points):
        pointsInfo = {'description': description,
         'maxProgrVal': 0,
         'progressDiff': '+ {}'.format(points),
         'progressDiffTooltip': tooltip,
         'currentProgrVal': 0,
         'progrBarType': formatters.PROGRESS_BAR_TYPE.NONE}
        return pointsInfo

    @classmethod
    def __getChapterName(cls, chapterID):
        return backport.text(R.strings.battle_pass.chapter.fullName.num(chapterID)()) if chapterID else ''

    @staticmethod
    def _getDescription(progress):
        if progress.pointsAux:
            text = backport.text(_POST_BATTLE_RES.progress.pointsAux())
        else:
            text = backport.text(_POST_BATTLE_RES.progress())
        return text

    @staticmethod
    def _getProgressDiffTooltip(progress, chapterID):
        if progress.pointsAux:
            text = backport.text(_POST_BATTLE_RES.progress.pointsAux.tooltip(), points=progress.pointsAux)
        else:
            text = backport.text(_POST_BATTLE_RES.progress.tooltip(), points=progress.getPointsDiff(chapterID))
        return text

    @staticmethod
    def __getMissionState(isDone):
        return MISSIONS_STATES.COMPLETED if isDone else MISSIONS_STATES.IN_PROGRESS

    @staticmethod
    def __getProgressBarType(needShow):
        return formatters.PROGRESS_BAR_TYPE.SIMPLE if needShow else formatters.PROGRESS_BAR_TYPE.NONE


class QuestsProgressBlock(base.StatsBlock):
    __eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ()

    def getVO(self):
        vo = super(QuestsProgressBlock, self).getVO()
        return vo

    def setRecord(self, result, reusable):
        commonQuests = []
        c11nQuests = []
        personalMissions = {}
        allCommonQuests = self.__eventsCache.getQuests()
        allCommonQuests.update(self.__eventsCache.getHiddenQuests(lambda q: q.isShowedPostBattle()))
        questsProgress = reusable.personal.getQuestsProgress()
        questTokensConvertion = deepcopy(reusable.personal.getQuestTokensConvertion())
        questTokensCount = reusable.personal.getQuestTokensCount()
        battleMattersProgressData = battleMattersProgressFilter(reusable, allCommonQuests)
        if battleMattersProgressData:
            for e, pCur, pPrev, reset, complete in battleMattersProgressData:
                info = getEventPostBattleInfo(e, allCommonQuests, pCur, pPrev, reset, complete, questTokensConvertion=questTokensConvertion, questTokensCount=questTokensCount)
                if info is not None:
                    self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', info))

        if questsProgress:
            for qID, qProgress in questsProgress.iteritems():
                pGroupBy, pPrev, pCur = qProgress
                isCompleted = isQuestCompleted(pGroupBy, pPrev, pCur)
                if isC11nQuest(qID):
                    quest = allCommonQuests.get(qID)
                    if quest is not None:
                        c11nQuests.append((quest,
                         {pGroupBy: pCur},
                         {pGroupBy: pPrev},
                         isCompleted))
                if qID in allCommonQuests:
                    data = packQuestProgressData(qID, allCommonQuests, qProgress, isCompleted)
                    if data:
                        commonQuests.append(data)
                if personal_missions.g_cache.isPersonalMission(qID):
                    pqID = personal_missions.g_cache.getPersonalMissionIDByUniqueID(qID)
                    questsCache = self.__eventsCache.getPersonalMissions()
                    quest = questsCache.getAllQuests(personal_missions.PM_BRANCH.ALL)[pqID]
                    progress = personalMissions.setdefault(quest, {})
                    progress.update({qID: isCompleted})

        pm2Progress = reusable.personal.getPM2Progress()
        if pm2Progress:
            quests = self.__eventsCache.getPersonalMissions().getAllQuests()
            for qID, data in pm2Progress.iteritems():
                quest = quests[qID]
                if quest in personalMissions:
                    personalMissions[quest].update(data)
                progress = personalMissions.setdefault(quest, {})
                progress.update(data)

        for quest, data in sorted(personalMissions.items(), key=operator.itemgetter(0), cmp=self.__sortPersonalMissions):
            if data.get(quest.getAddQuestID(), False):
                complete = PMComplete(True, True)
            elif data.get(quest.getMainQuestID(), False):
                complete = PMComplete(True, False)
            else:
                complete = PMComplete(False, False)
            info = getEventPostBattleInfo(quest, None, None, None, False, complete, progressData=data, questTokensConvertion=questTokensConvertion, questTokensCount=questTokensCount)
            if info is not None:
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', info))

        for customizationProgress in getProgressiveCustomizationProgress(reusable):
            self.addComponent(self.getNextComponentIndex(), ProgressiveCustomizationVO('', customizationProgress))

        questsByStyle = {}
        for e, pCur, pPrev, complete in c11nQuests:
            progressData = getDataByC11nQuest(e)
            styleID = progressData.styleID
            if styleID <= 0:
                continue
            quests = questsByStyle.setdefault(styleID, list())
            quests.append((e,
             pCur,
             pPrev,
             complete))

        for styleID, quests in questsByStyle.items():
            info = get2dProgressionStylePostBattleInfo(styleID, quests)
            if info is not None:
                self.addComponent(self.getNextComponentIndex(), QuestProgressiveCustomizationVO('', info))

        for e, pCur, pPrev, reset, complete in sorted(commonQuests, cmp=self.__sortCommonQuestsFunc):
            info = getEventPostBattleInfo(e, allCommonQuests, pCur, pPrev, reset, complete, questTokensConvertion=questTokensConvertion, questTokensCount=questTokensCount)
            if info is not None:
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', info))

        return

    @staticmethod
    def __sortPersonalMissions(a, b):
        aFullCompleted, bFullCompleted = a.isFullCompleted(), b.isFullCompleted()
        if aFullCompleted != bFullCompleted:
            return bFullCompleted - aFullCompleted
        aCompleted, bCompleted = a.isCompleted(), b.isCompleted()
        return bCompleted - aCompleted if aCompleted != bCompleted else b.getCampaignID() - a.getCampaignID()

    @staticmethod
    def __sortCommonQuestsFunc(aData, bData):
        aQuest, aCurProg, aPrevProg, _, _ = aData
        bQuest, bCurProg, bPrevProg, _, _ = bData
        res = cmp(aQuest.isCompleted(aCurProg), bQuest.isCompleted(bCurProg))
        if res:
            return -res
        if aQuest.isCompleted() and bQuest.isCompleted(bCurProg):
            res = aQuest.getBonusCount(aCurProg) - aPrevProg.get('bonusCount', 0) - (bQuest.getBonusCount(bCurProg) - bPrevProg.get('bonusCount', 0))
            if not res:
                return res
        return cmp(aQuest.getID(), bQuest.getID())


class DogTagsProgressBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        dogTagsProgress = getDogTagsProgress(reusable)
        if dogTagsProgress is None:
            return
        else:
            unlockedDogTags, upgradedDogTags = dogTagsProgress
            for unlockedDogTag in unlockedDogTags:
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', self._formatDogTag(unlockedDogTag)))

            for upgradedDogTag in upgradedDogTags:
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', self._formatDogTag(upgradedDogTag)))

            return

    @classmethod
    def _formatDogTag(cls, dogTagProgress):
        return {'title': cls.__getInfoTitle(dogTagProgress),
         'description': cls.__getInfoDescription(dogTagProgress),
         'dogTagType': dogTagProgress.dogTagType,
         'componentId': dogTagProgress.componentId,
         'imageSrc': dogTagComposer.getComponentImage(dogTagProgress.componentId, dogTagProgress.compGrade),
         'unlockType': dogTagProgress.unlockType}

    @staticmethod
    def __getInfoTitle(dogTagProgress):
        componentId, dogTagType = dogTagProgress.componentId, dogTagProgress.dogTagType
        compTitle = dogTagComposer.getComponentTitle(componentId)
        viewType = dogTagProgress.unlockType
        strSource = R.strings.dogtags.postbattle.dyn(dogTagType).dyn(viewType).title()
        return backport.text(strSource).format(title=compTitle, level=dogTagProgress.compGrade + 1)

    @staticmethod
    def __getInfoDescription(dogTagProgress):
        viewType = dogTagProgress.unlockType
        strSource = R.strings.dogtags.postbattle.dyn(dogTagProgress.dogTagType).dyn(viewType).description()
        return backport.text(strSource)


class ProgressiveRewardVO(base.StatsItem):
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ()

    def _convert(self, record, reusable):
        progressiveReward = reusable.personal.getProgressiveReward()
        if progressiveReward is None:
            return
        else:
            progressiveConfig = self.lobbyContext.getServerSettings().getProgressiveRewardConfig()
            maxSteps = progressiveConfig.maxLevel
            hasCompleted, currentStep, probability = progressiveReward
            if currentStep >= maxSteps:
                _logger.warning('Current step more than max step in progressive reward')
                return
            if hasCompleted:
                currentStep = currentStep - 1 if currentStep else maxSteps - 1
            descText = text_styles.standard(backport.text(R.strings.battle_results.progressiveReward.descr()))
            return getProgressiveRewardVO(currentStep=currentStep, probability=probability, maxSteps=maxSteps, showBg=True, align=prConst.WIDGET_LAYOUT_H, isHighTitle=True, hasCompleted=hasCompleted, descText=descText)


class ProgressiveCustomizationVO(base.DirectStatsItem):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    def getVO(self):
        questInfo = self._value.get('questInfo', {})
        questID = questInfo.get('questID', None)
        if questInfo and questID is not None:
            _, vehicleIntCD = parseEventID(questID)
            vehicle = self._itemsCache.items.getItemByCD(vehicleIntCD)
            linkBtnEnabled, linkBtnTooltip = getC11nProgressionLinkBtnParams(vehicle)
            self._value['linkBtnEnabled'] = linkBtnEnabled
            self._value['linkBtnTooltip'] = backport.text(linkBtnTooltip)
        return self._value


class QuestProgressiveCustomizationVO(base.DirectStatsItem):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    def getVO(self):
        questInfo = self._value.get('questInfo', {})
        questID = questInfo.get('questID', None)
        if questInfo and questID is not None:
            linkBtnEnabled, linkBtnTooltip = getC11n2dProgressionLinkBtnParams()
            self._value['linkBtnEnabled'] = linkBtnEnabled
            self._value['linkBtnTooltip'] = backport.text(linkBtnTooltip)
        return self._value


class PrestigeProgressVO(base.StatsItem):

    def _convert(self, result, reusable):
        prestigeProgress = getPrestigeProgress(reusable)
        return self.__createPrestigeVO(prestigeProgress) if prestigeProgress else None

    @staticmethod
    def __createPrestigeVO(prestigeData):
        return {'vehCD': prestigeData.vehCD,
         'gradeType': prestigeData.currentGradeType.value,
         'grade': str(prestigeData.currentGrade),
         'lvl': str(prestigeData.newLvl),
         'currentXP': prestigeData.currentXP,
         'nextLvlXP': prestigeData.currentNextLvlXP,
         'gainedXP': '+ {}'.format(backport.getIntegralFormat(prestigeData.gainedXP)),
         'isLvlUp': prestigeData.oldLvl < prestigeData.newLvl}
