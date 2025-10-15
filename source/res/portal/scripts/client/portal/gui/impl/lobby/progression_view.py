# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/progression_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showHangar
from portal.gui.impl.gen.view_models.views.lobby.portal_progression_model import PortalProgressionModel
from portal.gui.impl.gen.view_models.views.lobby.portal_progression_level_model import PortalProgressionLevelModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from helpers import dependency
from portal.gui.shared.event_dispatcher import showPortalInfoPage
from portal.skeletons.portal_event_controller import IPortalEventController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IHangarFeatureStateController
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from portal.gui.impl.gen.view_models.views.lobby.portal_medal_model import PortalMedalModel
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.backport import TooltipData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from portal.gui.impl.lobby.tooltips.progress_token_tooltip import ProgressTokenTooltip
from PlayerEvents import g_playerEvents
from skeletons.gui.lobby_context import ILobbyContext
from portal.sounds.sound_constants import PORTAL_PROGRESSION_SOUND_SPACE

class ProgressionView(ViewImpl):
    __slots__ = ('__tooltipData',)
    __portalController = dependency.descriptor(IPortalEventController)
    __appLoader = dependency.descriptor(IAppLoader)
    __hangarFeatureStateController = dependency.descriptor(IHangarFeatureStateController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _COMMON_SOUND_SPACE = PORTAL_PROGRESSION_SOUND_SPACE

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = PortalProgressionModel()
        self.__tooltipData = {}
        super(ProgressionView, self).__init__(settings)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            data = self.__tooltipData.get(tooltipId)
            return data

    @property
    def viewModel(self):
        return super(ProgressionView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ProgressionView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.portal.lobby.tooltips.ProgressTokenTooltip():
            stageNumber = event.getArgument('stageNumber', -1)
            finishedLevelsCount = self.__portalController.getFinishedLevelsCount()
            levelInProgress = finishedLevelsCount + 1
            currentPoints = self.__portalController.getCurrentStampsAtLevel(stageNumber)
            nextLevelPoints = self.__portalController.getStampsCountPerLevel()
            isComplete = levelInProgress != stageNumber
            return ProgressTokenTooltip(True, isComplete, currentPoints, nextLevelPoints)
        return super(ProgressionView, self).createToolTipContent(event=event, contentID=contentID)

    def _onLoading(self, *args, **kwargs):
        super(ProgressionView, self)._onLoading()
        self._updateModel()

    def _onLoaded(self, *args, **kwargs):
        self.__hangarFeatureStateController.enter(self.layoutID, doHideHeader=True)

    def _finalize(self):
        self.__hangarFeatureStateController.exit(self.layoutID)
        super(ProgressionView, self)._finalize()

    def _updateModel(self):
        with self.viewModel.transaction() as model:
            self.__fillProgression(model)
            self.__fillMedals(model)

    def __fillProgression(self, model):
        self.__tooltipData = {}
        currentLevel = self.__portalController.getCurrentLevel()
        stampsPerLevel = self.__portalController.getStampsCountPerLevel()
        currentStamps = self.__portalController.getCurrentStampsAtLevel(currentLevel)
        model.setPointsCurrent(currentStamps)
        model.setCurrentStage(currentLevel)
        model.setStampsNeededPerStage(stampsPerLevel)
        progression = self.__getItemsProgression()
        stages = model.getStages()
        stages.clear()
        stages.reserve(len(progression))
        for _, rewards in progression:
            item = PortalProgressionLevelModel()
            rewardsList = item.getRewards()
            rewardsList.clear()
            rewardsList.reserve(len(rewards))
            packBonusModelAndTooltipData(rewards, rewardsList, self.__tooltipData)
            rewardsList.invalidate()
            stages.addViewModel(item)
            item.setPointsNeededPerStage(stampsPerLevel)

        stages.invalidate()

    def __fillMedals(self, model):
        medals, badges = self.__portalController.getMedals(), self.__portalController.getBadges()
        achievements = model.getMedals()
        achievements.clear()
        achievements.reserve(len(medals) + len(badges))
        for medal in medals:
            record = tuple(medal.split(':'))
            index = '0' if self.__tooltipData is None else str(len(self.__tooltipData))
            self.__tooltipData[index] = TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS, specialArgs=(record[0], record[1], 1))
            factory = getAchievementFactory(record, self.__itemsCache.items.getAccountDossier())
            isAchieved = factory.create().isInDossier()
            achievements.addViewModel(self.__createPortalMedal(record[1], index, isAchieved))

        for badge in badges:
            _, badgeID = tuple(badge.split(':'))
            index = '0' if self.__tooltipData is None else str(len(self.__tooltipData))
            self.__tooltipData[index] = TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BADGE, specialArgs=[int(badgeID)])
            isAchieved = self.__itemsCache.items.getBadges().get(int(badgeID)).isAchieved
            achievements.addViewModel(self.__createPortalMedal('badge_' + badgeID, index, isAchieved))

        achievements.invalidate()
        return

    def __createPortalMedal(self, name, tooltipIdx, isReceived):
        medal = PortalMedalModel()
        medal.setName(name)
        medal.setTooltipId(str(tooltipIdx))
        medal.setTooltipContentId(str(self.__tooltipData[tooltipIdx]))
        medal.setIsReceived(isReceived)
        return medal

    def __getItemsProgression(self):
        result = []
        for data in self.__portalController.getConfig()['progression']:
            rewards = self.__portalController.getQuestRewards(data.get('quest', ''))
            result.append((data.get('level', 0), rewards))

        return result

    def __onCloseHandler(self):
        showHangar()
        self.destroyWindow()

    def __onClientUpdated(self, diff, _):
        self._updateModel()

    def __onAboutEventClick(self):
        showPortalInfoPage()

    def _getEvents(self):
        return ((g_playerEvents.onClientUpdated, self.__onClientUpdated),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onClientUpdated),
         (self.viewModel.onAboutEventClick, self.__onAboutEventClick),
         (self.viewModel.onClose, self.__onCloseHandler))
