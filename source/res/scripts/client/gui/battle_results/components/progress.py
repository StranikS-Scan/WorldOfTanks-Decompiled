# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/progress.py
import logging
from itertools import chain
import typing
import BigWorld
from battle_pass_common import BattlePassConsts
from constants import EVENT_TYPE
from dog_tags_common.components_config import componentConfigAdapter as cca
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import currentHangarIsBattleRoyale
from gui.battle_results.reusable.progress import VehicleProgressHelper
from gui.Scaleform.daapi.view.lobby.customization.progression_helpers import getC11nProgressionLinkBtnParams, getProgressionPostBattleInfo, parseEventID, getC11n2dProgressionLinkBtnParams
from gui.Scaleform.daapi.view.lobby.server_events.awards_formatters import BattlePassTextBonusesPacker
from gui.Scaleform.genConsts.MISSIONS_STATES import MISSIONS_STATES
from gui.Scaleform.genConsts.PROGRESSIVEREWARD_CONSTANTS import PROGRESSIVEREWARD_CONSTANTS as prConst
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.battle_results.components import base
from gui.battle_results.br_constants import ProgressAction
from gui.dog_tag_composer import dogTagComposer
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import getProgressiveRewardVO
from gui.impl.gen import R
from gui.server_events import formatters
from gui.server_events.awards_formatters import QuestsBonusComposer
from gui.shared.formatters import getItemPricesVO, getItemUnlockPricesVO, text_styles
from gui.shared.gui_items import Tankman
from gui.shared.gui_items.Tankman import getCrewSkinIconSmall
from gui.shared.gui_items.Vehicle import getLevelIconPath
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.gui_items.gui_item_economics import ItemPrice
from helpers import dependency
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IEventBattlesController
if typing.TYPE_CHECKING:
    from typing import Dict, Tuple
    from gui.battle_results.reusable import ReusableInfo
    from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import BattlePassProgress
MIN_BATTLES_TO_SHOW_PROGRESS = 5
_POST_BATTLE_RES = R.strings.battle_pass.reward.postBattle
_logger = logging.getLogger(__name__)

def isQuestCompleted(_, pPrev, pCur):
    return pCur.get('bonusCount', 0) - pPrev.get('bonusCount', 0) > 0


def _makeTankmanDescription(roleName, fullName):
    role = text_styles.main(roleName)
    name = text_styles.standard(fullName)
    return backport.text(R.strings.battle_results.common.crewMember.description(), name=name, role=role)


def _makeVehicleDescription(vehicle):
    vehicleType = text_styles.standard(vehicle.typeUserName)
    vehicleName = text_styles.main(vehicle.userName)
    return backport.text(R.strings.battle_results.common.vehicle.details(), vehicle=vehicleName, type=vehicleType)


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def _makeTankmanVO(tman, avgBattles2NewSkill, itemsCache=None, lobbyContext=None):
    prediction = ''
    if avgBattles2NewSkill > 0:
        prediction = backport.text(R.strings.battle_results.common.newSkillPrediction(), battles=backport.getIntegralFormat(avgBattles2NewSkill))
    data = {'title': backport.text(R.strings.battle_results.common.crewMember.newSkill()),
     'prediction': prediction,
     'linkEvent': ProgressAction.NEW_SKILL_UNLOCK_TYPE,
     'linkId': tman.invID}
    if tman.skinID != NO_CREW_SKIN_ID and lobbyContext.getServerSettings().isCrewSkinsEnabled():
        skinItem = itemsCache.items.getCrewSkin(tman.skinID)
        data['tankmenIcon'] = getCrewSkinIconSmall(skinItem.getIconID())
        fullTankmanName = localizedFullName(skinItem)
    else:
        data['tankmenIcon'] = Tankman.getSmallIconPath(tman.nationID, tman.descriptor.iconID)
        fullTankmanName = tman.fullUserName
    data['description'] = _makeTankmanDescription(tman.roleUserName, fullTankmanName)
    return data


def _makeUnlockModuleVO(item, unlockProps):
    return {'title': backport.text(R.strings.battle_results.common.fitting.research()),
     'description': text_styles.main(item.userName),
     'fittingType': item.getGUIEmblemID(),
     'lvlIcon': getLevelIconPath(item.level),
     'price': getItemUnlockPricesVO(unlockProps),
     'linkEvent': ProgressAction.RESEARCH_UNLOCK_TYPE,
     'linkId': unlockProps.parentID}


def _makeUnlockVehicleVO(item, unlockProps, avgBattlesTillUnlock):
    prediction = ''
    if avgBattlesTillUnlock > 0:
        prediction = backport.text(R.strings.battle_results.common.researchPrediction(), battles=avgBattlesTillUnlock)
    return {'title': backport.text(R.strings.battle_results.common.vehicle.research()),
     'description': _makeVehicleDescription(item),
     'vehicleIcon': item.iconSmall,
     'lvlIcon': getLevelIconPath(item.level),
     'prediction': prediction,
     'price': getItemUnlockPricesVO(unlockProps),
     'linkEvent': ProgressAction.RESEARCH_UNLOCK_TYPE,
     'linkId': unlockProps.parentID}


def _makeVehiclePurchaseVO(item, unlockProps, price):
    return {'title': backport.text(R.strings.battle_results.common.vehicle.purchase()),
     'description': _makeVehicleDescription(item),
     'vehicleIcon': item.iconSmall,
     'lvlIcon': getLevelIconPath(item.level),
     'price': getItemPricesVO(ItemPrice(price=price, defPrice=price)),
     'linkEvent': ProgressAction.PURCHASE_UNLOCK_TYPE,
     'linkId': unlockProps.parentID}


def _makeModulePurchaseVO(item, unlockProps, price):
    return {'title': backport.text(R.strings.battle_results.common.fitting.purchase()),
     'description': text_styles.main(item.userName),
     'fittingType': item.itemTypeName,
     'lvlIcon': getLevelIconPath(item.level),
     'price': getItemPricesVO(ItemPrice(price=price, defPrice=price)),
     'linkEvent': ProgressAction.PURCHASE_UNLOCK_TYPE,
     'linkId': unlockProps.parentID}


class VehicleProgressBlock(base.StatsBlock):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    def getVO(self):
        vo = super(VehicleProgressBlock, self).getVO()
        for item in vo:
            isNewEarnedSkill = item.get('linkEvent') == ProgressAction.NEW_SKILL_UNLOCK_TYPE
            isNewFreeSkill = item.get('freeSkillsLinkEvent') == ProgressAction.NEW_FREE_SKILL_UNLOCK_TYPE
            if not isNewEarnedSkill and not isNewFreeSkill:
                continue
            tankman = self._itemsCache.items.getTankman(item['linkId'])
            item['linkBtnEnabled'] = tankman.canLearnSkills()

        return vo

    def setRecord(self, result, reusable):
        xpEarnings = reusable.personal.xpProgress
        for intCD, data in reusable.personal.getVehicleCDsIterator(result):
            xpEarningsForVehicle = xpEarnings.get(intCD, {})
            vehicleBattleXp = xpEarningsForVehicle.get('xp', 0)
            tankmenXps = dict(xpEarningsForVehicle.get('xpByTmen', []))
            pureCreditsReceived = data.get('pureCreditsReceived', 0)
            helper = VehicleProgressHelper(intCD)
            ready2UnlockModulesVOs, ready2UnlockVehiclesVOs = self.__getReady2UnlockItemsVOs(helper, vehicleBattleXp)
            ready2BuyModulesVOs, ready2BuyVehiclesVOs = self.__getReady2BuyItemsVOs(helper, pureCreditsReceived)
            tankmenVOs = self.__getNewSkilledTankmenVOs(helper, tankmenXps)
            progress = list(chain(ready2UnlockModulesVOs, ready2BuyModulesVOs, tankmenVOs, ready2UnlockVehiclesVOs, ready2BuyVehiclesVOs))
            helper.clear()
            for item in progress:
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', item))

    @staticmethod
    def __getReady2UnlockItemsVOs(helper, vehicleBattleXp):
        ready2UnlockVehicles, ready2UnlockModules = helper.getReady2UnlockItems(vehicleBattleXp)
        ready2UnlockVehiclesVOs = []
        for item, unlockProps, _ in ready2UnlockVehicles:
            avgBattles2Unlock = helper.getAvgBattles2Unlock(unlockProps)
            if not helper.isEnoughXPToUnlock(unlockProps):
                0 < avgBattles2Unlock <= MIN_BATTLES_TO_SHOW_PROGRESS and ready2UnlockVehiclesVOs.append(_makeUnlockVehicleVO(item, unlockProps, avgBattles2Unlock))

        ready2UnlockModulesVOs = [ _makeUnlockModuleVO(item, unlockProps) for item, unlockProps, _ in ready2UnlockModules ]
        return (ready2UnlockModulesVOs, ready2UnlockVehiclesVOs)

    @staticmethod
    def __getReady2BuyItemsVOs(helper, pureCreditsReceived):
        ready2BuyVehicles, ready2BuyModules = helper.getReady2BuyItems(pureCreditsReceived)
        ready2BuyVehiclesVOs = [ _makeVehiclePurchaseVO(item, unlockProps, price) for item, unlockProps, price in ready2BuyVehicles ]
        ready2BuyModulesVOs = [ _makeModulePurchaseVO(item, unlockProps, price) for item, unlockProps, price in ready2BuyModules ]
        return (ready2BuyModulesVOs, ready2BuyVehiclesVOs)

    @staticmethod
    def __getNewSkilledTankmenVOs(helper, tankmenXps):
        tankmenVOs = []
        for tman, isCompletedSkill in helper.getNewSkilledTankmen(tankmenXps):
            avgBattles2NewSkill = 0
            if not isCompletedSkill:
                avgBattles2NewSkill = helper.getAvgBattles2NewSkill(tman)
                if avgBattles2NewSkill <= 0 or avgBattles2NewSkill > MIN_BATTLES_TO_SHOW_PROGRESS:
                    continue
            tankmenVOs.append(_makeTankmanVO(tman, avgBattles2NewSkill))

        return tankmenVOs


class BattlePassProgressBlock(base.StatsBlock):
    __battlePass = dependency.descriptor(IBattlePassController)

    def setRecord(self, result, reusable):
        bpp = reusable.battlePassProgress
        if not bpp.hasProgress:
            return
        isNewPoints = bpp.pointsNew > 0 or bpp.questPoints > 0 or bpp.bonusCapPoints > 0 or bpp.bpTopPoints > 0
        isNewLevel = bpp.currLevel > bpp.prevLevel
        if isNewPoints or isNewLevel:
            self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem(*self.__formatBattlePassProgressPoints(bpp, bpp.currLevel)))
        for lvl in xrange(bpp.prevLevel, bpp.currLevel):
            self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem(*self.__formatBattlePassProgress(bpp, lvl)))

        if bpp.pointsAux or bpp.pointsNew and bpp.pointsMax != bpp.pointsNew:
            self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem(*self.__formatBattlePassProgress(bpp, bpp.currLevel)))

    @classmethod
    def __formatBattlePassProgress(cls, progress, level):
        return ('', {'awards': cls.__makeProgressAwards(progress, level),
          'questInfo': cls.__makeProgressQuestInfo(progress, level),
          'questType': EVENT_TYPE.BATTLE_QUEST,
          'progressList': cls.__makeProgressList(progress, level),
          'questState': {'statusState': cls.__getMissionState(progress.isDone)},
          'linkBtnTooltip': '' if progress.isApplied else backport.text(R.strings.battle_pass.progression.error()),
          'linkBtnEnabled': progress.isApplied})

    @classmethod
    def __formatBattlePassProgressPoints(cls, progress, level):
        return ('', {'awards': [],
          'questInfo': cls.__makeProgressPointsInfo(progress),
          'questType': EVENT_TYPE.BATTLE_QUEST,
          'progressList': cls.__makeProgressListPoints(progress),
          'questState': {'statusState': cls.__getMissionState(progress.isDone)},
          'linkBtnTooltip': '' if progress.isApplied else backport.text(R.strings.battle_pass.progression.error()),
          'linkBtnEnabled': progress.isApplied})

    @staticmethod
    def __makeProgressAwards(progress, level):
        nothing = []
        if level >= progress.currLevel:
            return nothing
        awards = progress.getLevelAwards(level + 1)
        if not awards:
            return nothing
        awardsList = QuestsBonusComposer(BattlePassTextBonusesPacker()).getPreformattedBonuses(awards)

        def makeUnavailableBlockData():
            return formatters.packTextBlock(text_styles.alert(backport.text(R.strings.quests.bonuses.notAvailable())))

        if awardsList:
            return [ award.getDict() for award in awardsList ]
        return [makeUnavailableBlockData().getDict()]

    @classmethod
    def __makeProgressQuestInfo(cls, progress, level):
        isFreePoints = progress.pointsAux and not progress.isLevelMax or progress.isLevelMax and level == progress.currLevel
        chapterID = progress.chapterID
        return {'status': cls.__getMissionState(isDone=level < progress.currLevel),
         'questID': BattlePassConsts.FAKE_QUEST_ID,
         'rendererType': QUESTS_ALIASES.RENDERER_TYPE_QUEST,
         'eventType': EVENT_TYPE.BATTLE_QUEST,
         'maxProgrVal': progress.pointsMax,
         'tooltip': TOOLTIPS.QUESTS_RENDERER_LABEL,
         'description': backport.text(_POST_BATTLE_RES.title.free() if isFreePoints else _POST_BATTLE_RES.title(), level=level + 1, chapter=cls.__getChapterName(chapterID)),
         'currentProgrVal': progress.pointsNew,
         'tasksCount': -1,
         'progrBarType': cls.__getProgressBarType(not progress.isDone),
         'linkTooltip': TOOLTIPS.QUESTS_LINKBTN_BATTLEPASS if chapterID and not cls.__battlePass.isChapterCompleted(chapterID) else TOOLTIPS.QUESTS_LINKBTN_BATTLEPASS_SELECT}

    @classmethod
    def __makeProgressPointsInfo(cls, progress):
        chapterID = progress.chapterID
        return {'status': '',
         'questID': BattlePassConsts.FAKE_QUEST_ID,
         'eventType': EVENT_TYPE.BATTLE_QUEST,
         'description': backport.text(_POST_BATTLE_RES.progress.points()),
         'progrBarType': formatters.PROGRESS_BAR_TYPE.NONE,
         'tasksCount': -1,
         'linkTooltip': TOOLTIPS.QUESTS_LINKBTN_BATTLEPASS if chapterID and not cls.__battlePass.isChapterCompleted(chapterID) else TOOLTIPS.QUESTS_LINKBTN_BATTLEPASS_SELECT}

    @classmethod
    def __makeProgressList(cls, progress, level):
        progressLevel = {'description': cls._getDescription(progress),
         'maxProgrVal': progress.pointsMax,
         'progressDiff': '+ {}'.format(progress.pointsAdd),
         'progressDiffTooltip': cls._getProgressDiffTooltip(progress),
         'currentProgrVal': progress.pointsNew,
         'progrBarType': cls.__getProgressBarType(not progress.pointsAux)}
        return [progressLevel] if not progress.isDone or progress.pointsAux and not progress.isLevelMax or level == progress.currLevel else []

    @classmethod
    def __makeProgressListPoints(cls, progress):
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
    def _getProgressDiffTooltip(progress):
        if progress.pointsAux:
            text = backport.text(_POST_BATTLE_RES.progress.pointsAux.tooltip(), points=progress.pointsAux)
        else:
            text = backport.text(_POST_BATTLE_RES.progress.tooltip(), points=progress.pointsAdd)
        return text

    @staticmethod
    def __getMissionState(isDone):
        return MISSIONS_STATES.COMPLETED if isDone else MISSIONS_STATES.IN_PROGRESS

    @staticmethod
    def __getProgressBarType(needShow):
        return formatters.PROGRESS_BAR_TYPE.SIMPLE if needShow else formatters.PROGRESS_BAR_TYPE.NONE


class Comp7BattlePassProgressBlock(BattlePassProgressBlock):

    @staticmethod
    def _getDescription(progress):
        if progress.pointsAux:
            text = backport.text(_POST_BATTLE_RES.progress.pointsAux())
        else:
            text = backport.text(_POST_BATTLE_RES.comp7.progress())
        return text

    @staticmethod
    def _getProgressDiffTooltip(progress):
        return backport.text(_POST_BATTLE_RES.comp7.progress.tooltip(), points=progress.pointsAdd)


class QuestsProgressBlock(base.StatsBlock):
    eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ()

    def setRecord(self, result, reusable):
        personalMissions = reusable.progress.getPlayerPersonalMissionProgress()
        personalMissionInfo = reusable.progress.packPersonalMissions(personalMissions)
        c11nProgress = reusable.progress.getC11nProgress()
        c11nQuestsInfo = reusable.progress.packC11nQuests(c11nProgress)
        questsProgress = reusable.progress.getPlayerQuestProgress()
        battleMattersProgress = reusable.progress.getBattleMattersProgress()
        commonQuestsInfo = reusable.progress.packQuests(questsProgress)
        battleMattersQuestsInfo = reusable.progress.packQuests(battleMattersProgress)
        for info in battleMattersQuestsInfo:
            self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', info))

        for info in personalMissionInfo:
            self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', info))

        for vehicleIntCD, c11nProgression in reusable.personal.getC11nProgress().iteritems():
            for intCD, progressionData in sorted(c11nProgression.iteritems(), key=lambda (_, d): -d.get('level', 0)):
                info = getProgressionPostBattleInfo(intCD, vehicleIntCD, progressionData)
                if info is not None:
                    self.addComponent(self.getNextComponentIndex(), ProgressiveCustomizationVO('', info))

        for info in c11nQuestsInfo:
            self.addComponent(self.getNextComponentIndex(), QuestProgressiveCustomizationVO('', info))

        for info in commonQuestsInfo:
            self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', info))

        return


class DogTagsProgressBlock(base.StatsBlock):
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ()

    def getVO(self):
        vo = super(DogTagsProgressBlock, self).getVO()
        return vo

    @staticmethod
    def createDogTagInfo(componentId, dogTagType):
        compGrade = BigWorld.player().dogTags.getComponentProgress(componentId).grade
        return {'title': DogTagsProgressBlock.__getInfoTitle(componentId, compGrade, dogTagType),
         'description': DogTagsProgressBlock.__getInfoDescription(componentId, dogTagType),
         'dogTagType': dogTagType,
         'componentId': componentId,
         'imageSrc': dogTagComposer.getComponentImage(componentId, compGrade),
         'unlockType': cca.getComponentById(componentId).viewType.value.lower()}

    @staticmethod
    def __getInfoTitle(componentId, grade, dogTagType):
        compTitle = dogTagComposer.getComponentTitle(componentId)
        viewType = cca.getComponentById(componentId).viewType.value.lower()
        strSource = R.strings.dogtags.postbattle.dyn(dogTagType).dyn(viewType).title()
        return backport.text(strSource).format(title=compTitle, level=grade + 1)

    @staticmethod
    def __getInfoDescription(componentId, dogTagType):
        viewType = cca.getComponentById(componentId).viewType.value.lower()
        strSource = R.strings.dogtags.postbattle.dyn(dogTagType).dyn(viewType).description()
        return backport.text(strSource)

    def setRecord(self, result, reusable):
        if not self.lobbyContext.getServerSettings().isDogTagInPostBattleEnabled():
            return
        dogTags = reusable.personal.getDogTagsProgress()
        for compId in dogTags.get('unlockedComps', []):
            info = self.createDogTagInfo(compId, 'unlock')
            self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', info))

        for compId in dogTags.get('upgradedComps', []):
            info = self.createDogTagInfo(compId, 'upgrade')
            self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', info))


class ProgressiveRewardVO(base.StatsItem):
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ()

    def _convert(self, record, reusable):
        progressiveReward = reusable.progress.getProgressiveReward()
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
    __gameEventCtrl = dependency.descriptor(IEventBattlesController)
    __slots__ = ()

    def getVO(self):
        questInfo = self._value.get('questInfo', {})
        questID = questInfo.get('questID', None)
        if questInfo and questID is not None:
            _, vehicleIntCD = parseEventID(questID)
            vehicle = self._itemsCache.items.getItemByCD(vehicleIntCD)
            linkBtnEnabled, linkBtnTooltip = getC11nProgressionLinkBtnParams(vehicle)
            isEventHangar = self.__gameEventCtrl.isEventPrbActive()
            if currentHangarIsBattleRoyale() or isEventHangar:
                linkBtnEnabled = False
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
            if currentHangarIsBattleRoyale():
                linkBtnEnabled = False
            self._value['linkBtnEnabled'] = linkBtnEnabled
            self._value['linkBtnTooltip'] = backport.text(linkBtnTooltip)
        return self._value
