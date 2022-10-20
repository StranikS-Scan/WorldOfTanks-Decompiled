# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/global_progression_view.py
import re
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getMissionInfoData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.gen import R
from gui.impl import backport
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.server_events.bonuses import DossierBonus
from halloween.gui.game_control.halloween_progress_controller import getProgressInfo
from halloween.gui.impl.lobby.base_event_view import BaseEventView
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.impl.pub.lobby_window import LobbyWindow
from halloween.gui.impl.gen.view_models.views.lobby.common.base_quest_model import QuestStatusEnum, BaseQuestModel, QuestTypeEnum
from halloween.hw_constants import PhaseType, HWBonusesType, HALLOWEEN_QUEST_PASSED_TOKEN_TPL, GLOBAL_PROGRESS_TANKMAN_QUEST, GLOBAL_PROGRESS_HW_XP_QUEST, HWTooltips
from halloween.gui.impl.gen.view_models.views.lobby.common.reward_model import RewardModel
from halloween.gui.impl.gen.view_models.views.lobby.global_progression_view_model import GlobalProgressionViewModel
from halloween.gui.sounds.sound_constants import HW_HANGAR_OVERLAYS
from frameworks.wulf import WindowLayer
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.server_events import IEventsCache

class GlobalProgressionView(BaseEventView):
    layoutID = R.views.halloween.lobby.GlobalProgressionView()
    eventsCache = dependency.descriptor(IEventsCache)
    gui = dependency.descriptor(IGuiLoader)
    _COMMON_SOUND_SPACE = HW_HANGAR_OVERLAYS

    def __init__(self, layoutID=None):
        settings = ViewSettings(layoutID or self.layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, GlobalProgressionViewModel())
        super(GlobalProgressionView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(GlobalProgressionView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            bonusArg = event.getArgument('tooltipId', None)
            bonusType = event.getArgument('name', None)
            if bonusType == HWBonusesType.BADGE:
                return self.__badgeTooltip(bonusArg)
            if bonusType == HWBonusesType.MEDAL:
                return self.__achievementTooltip(bonusType, bonusArg)
        return super(GlobalProgressionView, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        super(GlobalProgressionView, self)._initialize(*args, **kwargs)
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': True,
         'setIdle': True,
         'setParallax': True}), EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': False,
         'setIdle': True,
         'setParallax': True}), EVENT_BUS_SCOPE.LOBBY)
        super(GlobalProgressionView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(GlobalProgressionView, self)._onLoading()

    def _fillViewModel(self):
        super(GlobalProgressionView, self)._fillViewModel()
        self.__update()

    def __update(self):
        with self.viewModel.transaction() as model:
            self.__fillQuests(model)

    def __fillQuests(self, model):
        questModels = model.getQuests()
        questModels.clear()
        for i, cardInfo in enumerate(self.__getInfoCardsData()):
            questModel = BaseQuestModel()
            questStatus = cardInfo['status']
            questModel.setName(str(i))
            questModel.setType(cardInfo['type'])
            questModel.setStatus(questStatus)
            isDisabled = not questStatus == QuestStatusEnum.COMPLETED and not questStatus == QuestStatusEnum.INPROGRESS
            questModel.setIsDisabled(isDisabled)
            questModel.setAmount(cardInfo['totalProgress'])
            currentProgress = cardInfo['currentProgress']
            questModel.setProgress(currentProgress)
            questModel.setDeltaFrom(currentProgress)
            self.__fillBonuses(cardInfo['bonuses'], questModel)
            questModels.addViewModel(questModel)

        questModels.invalidate()

    def __fillBonuses(self, bonuses, questModel):
        rewards = questModel.getRewards()
        rewards.clear()
        for bonus in bonuses:
            reward = RewardModel()
            bType, bID = bonus
            reward.setName(bType)
            reward.setTooltipId(str(bID))
            reward.setIconName(self.__getIcon(bType, bID))
            rewards.addViewModel(reward)

        rewards.invalidate()

    def __getIcon(self, bonusType, bonusID):
        if bonusType == HWBonusesType.BADGE:
            return backport.image(R.images.gui.maps.icons.library.badges.c_80x80.dyn('{}_{}'.format('badge', bonusID))())
        return backport.image(R.images.gui.maps.icons.achievement.c_80x80.dyn(bonusID)()) if bonusType == HWBonusesType.MEDAL else ''

    def __getInfoCardsData(self):
        return [self.__getTankmenProgressInfo(), self.__getMainHWXPProgressInfo()]

    def __getTankmenProgressInfo(self):
        quest = findFirst(lambda q: q.getID() == GLOBAL_PROGRESS_TANKMAN_QUEST, self.eventsCache.getAllQuests().itervalues())
        if not quest:
            return {}
        tankmanPassedTokens = [ tokenID for tokenID in self.eventsCache.questsProgress.getTokenNames() if re.match(HALLOWEEN_QUEST_PASSED_TOKEN_TPL, tokenID) ]
        bonusesType = getMissionInfoData(quest).getSubstituteBonuses()
        data = []
        for bonusType in bonusesType:
            if not isinstance(bonusType, DossierBonus):
                continue
            for item in bonusType.getValue().itervalues():
                data.extend([ key for key in item ])

        return {'type': QuestTypeEnum.TANKMAN,
         'currentProgress': len(tankmanPassedTokens),
         'totalProgress': len(self._hwController.phasesHalloween.getPhasesByType(PhaseType.REGULAR)),
         'status': self.__getQuestStatus(quest),
         'bonuses': data}

    def __getMainHWXPProgressInfo(self):
        quest = findFirst(lambda q: q.getID() == GLOBAL_PROGRESS_HW_XP_QUEST, self.eventsCache.getAllQuests().itervalues())
        if not quest:
            return {}
        bonusesType = getMissionInfoData(quest).getSubstituteBonuses()
        data = []
        for bonusType in bonusesType:
            if not isinstance(bonusType, DossierBonus):
                continue
            for item in bonusType.getValue().itervalues():
                data.extend([ key for key in item ])

        progressInfo = getProgressInfo(quest)
        return {'type': QuestTypeEnum.HWXP,
         'currentProgress': progressInfo['currentProgress'],
         'totalProgress': progressInfo['totalProgress'],
         'status': self.__getQuestStatus(quest),
         'bonuses': data}

    def __getQuestStatus(self, quest):
        if quest.getStartTimeLeft() > 0:
            return QuestStatusEnum.WILLOPEN
        if quest.isCompleted():
            return QuestStatusEnum.COMPLETED
        return QuestStatusEnum.INPROGRESS if quest.isAvailable().isValid else QuestStatusEnum.REWARDNOTTAKEN

    def __badgeTooltip(self, badgeID):
        window = backport.BackportTooltipWindow(backport.createTooltipData(isSpecial=True, specialAlias=HWTooltips.HW_BADGE, specialArgs=[int(badgeID)]), self.getParentWindow())
        window.load()
        return window

    def __achievementTooltip(self, block, name):
        window = backport.BackportTooltipWindow(backport.createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS, specialArgs=[block, name]), self.getParentWindow())
        window.load()
        return window


class GlobalProgressionWindow(LobbyWindow):

    def __init__(self, layoutID):
        super(GlobalProgressionWindow, self).__init__(wndFlags=WindowFlags.WINDOW, content=GlobalProgressionView(layoutID=layoutID))
        self._blur = CachedBlur(enabled=True, ownLayer=WindowLayer.TOP_SUB_VIEW)

    def _finalize(self):
        self._blur.fini()
        super(GlobalProgressionWindow, self)._finalize()
