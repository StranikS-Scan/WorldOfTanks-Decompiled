# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/achievements/summary/summary_view.py
import logging
import typing
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import ACHIEVEMENTS_VISITED
from achievements20.WTRStageChecker import WTRStageChecker
from adisp import adisp_process
from constants import AchievementsLayoutStates, Configs
from dog_tags_common.components_config import componentConfigAdapter
from dog_tags_common.config.common import ComponentViewType
from dog_tags_common.player_dog_tag import PlayerDogTag
from dossiers2.ui.achievements import ACHIEVEMENT_SECTION
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.achievements.achievements_helper import fillAchievementModel, convertDbIdsToAchievements
from gui.clans.clan_cache import ClanInfo
from gui.clans.formatters import getClanRoleString
from gui.dog_tag_composer import DogTagComposerClient
from gui.game_control.wot_plus.service_record_customization import getValidatedServiceRecordRibbon, getValidatedServiceRecordBackground, ServiceRecordProcessor, getServiceRecordRibbonOptions, getServiceRecordBackgroundOptions
from gui.impl import backport
from gui.impl.backport import TooltipData
from gui.impl.dialogs.dialogs import showServiceRecordCustomizationConfirmDialog
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.achievements.achievements_constants import KPITypes
from gui.impl.gen.view_models.views.lobby.achievements.views.summary.background_model import BackgroundModel
from gui.impl.gen.view_models.views.lobby.achievements.views.summary.ribbon_model import RibbonModel
from gui.impl.gen.view_models.views.lobby.achievements.views.summary.statistic_item_model import StatisticItemModel
from gui.impl.gen.view_models.views.lobby.achievements.views.summary.summary_view_model import SummaryViewModel, EditState
from gui.impl.lobby.achievements.profile_utils import getProfileCommonInfo, formatPercent, getFormattedValue, getNormalizedValue, isSummaryEnabled, isWTREnabled, getRating, isEditingEnabled, isLayoutEnabled, getMasteryStatistic
from gui.impl.lobby.achievements.tooltips.battles_kpi_tooltip import BattlesKPITooltip
from gui.impl.lobby.achievements.tooltips.editing_tooltip import EditingTooltip
from gui.impl.lobby.achievements.tooltips.kpi_tooltip import KPITooltip
from gui.impl.lobby.achievements.tooltips.wotpr_main_tooltip import WOTPRMainTooltip
from gui.impl.lobby.achievements.tooltips.wtr_info_tooltip import WTRInfoTooltip
from gui.impl.lobby.achievements.tooltips.wtr_main_tooltip import WTRMainTooltip
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.dog_tags.animated_dog_tag_grade_tooltip import AnimatedDogTagGradeTooltip
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showAchievementEditView, showClanProfileWindow
from gui.shared.gui_items.dossier import dumpDossier
from gui.shared.gui_items.dossier.achievements.abstract import isRareAchievement
from gui.shared.view_helpers.emblems import getClanEmblemURL, EmblemSize
from helpers import dependency, server_settings
from skeletons.gui.game_control import IAchievements20Controller
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from typing import Dict, Tuple, List, Any, Generator
_logger = logging.getLogger(__name__)
_STATISTIC_LIST_ORDER = (KPITypes.DAMAGE,
 KPITypes.EXPERIENCE,
 KPITypes.BATTLES,
 KPITypes.DESTROYED,
 KPITypes.ASSISTANCE,
 KPITypes.BLOCKED)

class SummaryView(SubModelPresenter):
    __slots__ = ('__dossier', '__uniqueAwardsCount', '__prevRatingRank', '__prevRatingSubRank', '__userId')
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __achvmntCtrl = dependency.descriptor(IAchievements20Controller)
    __wotPlusCtrl = dependency.descriptor(IWotPlusController)

    def __init__(self, summaryModel, parentView, userId):
        self.__dossier = None
        self.__uniqueAwardsCount = 0
        self.__prevRatingRank = 0
        self.__prevRatingSubRank = 0
        self.__userId = userId
        super(SummaryView, self).__init__(summaryModel, parentView)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def getParentWindow(self):
        return self.parentView.getParentWindow()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(SummaryView, self).createToolTip(event)

    def getTooltipData(self, event):
        name = event.getArgument('name')
        block = event.getArgument('block')
        compId = event.getArgument('compId')
        if name is not None and block is not None:
            return self.__getAchievementsBackportTooltipData(name, block)
        else:
            return self.__getDogTagBackportTooltipData(int(compId)) if compId is not None else None

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.achievements.tooltips.KPITooltip():
            kpiType = event.getArgument('kpiType')
            if kpiType == KPITypes.BATTLES.value:
                return BattlesKPITooltip(self.__userId)
            return KPITooltip(kpiType, self.__userId)
        if contentID == R.views.lobby.achievements.tooltips.WTRInfoTooltip():
            return WTRInfoTooltip()
        if contentID == R.views.lobby.achievements.tooltips.WTRMainTooltip():
            return WTRMainTooltip(self.__userId)
        if contentID == R.views.lobby.achievements.tooltips.EditingTooltip():
            return EditingTooltip(str(event.getArgument('tooltipType')))
        if contentID == R.views.lobby.achievements.tooltips.WOTPRMainTooltip():
            return WOTPRMainTooltip()
        if contentID == R.views.lobby.dog_tags.AnimatedDogTagGradeTooltip():
            params = {'engravingId': event.getArgument('engravingId'),
             'backgroundId': event.getArgument('backgroundId')}
            return AnimatedDogTagGradeTooltip(params=params)
        return super(SummaryView, self).createToolTipContent(event, contentID)

    def initialize(self, *args, **kwargs):
        super(SummaryView, self).initialize(*args, **kwargs)
        self.__dossier = self.__itemsCache.items.getAccountDossier(self.__userId)
        self.__updateSettings()
        self.__updatePage()
        self.__showNotification()
        if not self.__isOtherPlayer:
            self.__achvmntCtrl.onSummaryPageVisited()

    def finalize(self):
        self.__dossier = None
        super(SummaryView, self).finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onAchievementsSettings, self.__onAchievementsSettings),
         (self.viewModel.otherPlayerInfo.onOpenProfile, self.__openClanStatistic),
         (self.viewModel.onCustomizationConfirmed, self.__onCustomizationConfirmed),
         (self.viewModel.onCustomizationDiscard, self.__onCustomizationDiscard),
         (self.viewModel.onSetBackgroundDraft, self.__onSetBackgroundDraft),
         (self.viewModel.onSetRibbonDraft, self.__onSetRibbonDraft),
         (self.viewModel.onSetIsInCustomizationMode, self.__onSetIsInCustomizationMode),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),
         (g_playerEvents.onDossiersResync, self.__dossierResyncHandler),
         (g_playerEvents.onRenewableSubscriptionStatusChanged, self.__onRenewableSubscriptionStatusChanged))

    def _getListeners(self):
        return ((events.Achievements20Event.LAYOUT_CHANGED, self.__onAchievementLayoutChanged, EVENT_BUS_SCOPE.LOBBY), (events.Achievements20Event.CLOSE_EDIT_VIEW, self.__onEditViewClose, EVENT_BUS_SCOPE.LOBBY))

    def __updatePage(self):
        if isSummaryEnabled():
            self.__updateUserInfo()
            self.__getStatistic()
            self.__getAchievementsStats()
            self.__updateSignificantAchievements()
            self.__getPrevStates()
            self.__updateRating()
            self.__updateCustomizationsVisuals()
            self.__updateCustomizationsOptions()
            if self.__isOtherPlayer:
                self.__updateClanInfo()

    @replaceNoneKwargsModel
    def __updateSettings(self, model=None):
        model.setIsSummaryEnabled(isSummaryEnabled())
        model.setIsWTREnabled(isWTREnabled())
        model.setIsOtherPlayer(self.__isOtherPlayer)

    def __updateUserInfo(self):
        if self.__dossier is not None:
            info = getProfileCommonInfo(self.__dossier.getDossierDescr())
            with self.viewModel.transaction() as model:
                model.setIsOtherPlayer(self.__isOtherPlayer)
                model.setRegistrationDate(str(info['registrationDate']))
                if info['lastBattleDate'] is not None:
                    model.setLastVisitDate(str(info['lastBattleDate']))
                    model.setLastVisitTime(str(info['lastBattleTime']))
        return

    def __getStatistic(self):
        if self.__dossier is not None:
            currentMastery, totalMastery = getMasteryStatistic(self.__dossier)
            mainStats, additionalStats = self.__fillStatistic()
            with self.viewModel.transaction() as model:
                model.setCurrentMastery(currentMastery)
                model.setTotalMastery(totalMastery)
                statistic = model.getStatistic()
                statistic.clear()
                for statisticItem in _STATISTIC_LIST_ORDER:
                    statisticModel = StatisticItemModel()
                    statisticModel.setType(str(statisticItem.value))
                    statisticModel.setMainValue(str(mainStats.get(statisticItem, 0)))
                    statisticModel.setAdditionalValue(str(additionalStats.get(statisticItem, 0)))
                    statistic.addViewModel(statisticModel)

                statistic.invalidate()
        return

    def __fillStatistic(self):
        stats = self.__dossier.getRandomStats()
        mainStats = {KPITypes.BATTLES: getFormattedValue(stats.getBattlesCount()),
         KPITypes.ASSISTANCE: getFormattedValue(stats.getMaxAssisted()),
         KPITypes.DESTROYED: getFormattedValue(stats.getFragsCount()),
         KPITypes.BLOCKED: getFormattedValue(stats.getMaxDamageBlockedByArmor()),
         KPITypes.EXPERIENCE: getFormattedValue(stats.getMaxXp()),
         KPITypes.DAMAGE: getFormattedValue(stats.getMaxDamage())}
        additionalStats = {KPITypes.BATTLES: formatPercent(getNormalizedValue(stats.getWinsEfficiency()) * 100),
         KPITypes.ASSISTANCE: getFormattedValue(stats.getDamageAssistedEfficiency()),
         KPITypes.DESTROYED: stats.getMaxFrags(),
         KPITypes.BLOCKED: getFormattedValue(stats.getAvgDamageBlocked()),
         KPITypes.EXPERIENCE: getFormattedValue(stats.getAvgXP()),
         KPITypes.DAMAGE: getFormattedValue(stats.getAvgDamage())}
        return [mainStats, additionalStats]

    def __getAchievementsStats(self):
        achievements = self.__dossier.getTotalStats().getAchievements(isInDossier=True, showHidden=False)
        achievements20GeneralConfig = self.__lobbyContext.getServerSettings().getAchievements20GeneralConfig()
        self.__uniqueAwardsCount = 0
        total = 0
        for section in achievements:
            for achievement in section:
                self.__uniqueAwardsCount += 1
                if achievement.isDone():
                    total += 1
                if achievement.getValue() > 0:
                    if achievement.getSection() == ACHIEVEMENT_SECTION.CLASS:
                        total += 1
                    else:
                        total += achievement.getValue()

        with self.viewModel.transaction() as model:
            model.setNumberOfUniqueAwards(self.__uniqueAwardsCount)
            model.setTotalAwards(total)
            model.setEditState(self.__getEditState())
            model.setAchievementRibbonLength(achievements20GeneralConfig.getLayoutLength())

    @replaceNoneKwargsModel
    def __updateSignificantAchievements(self, model=None):
        layoutState = self.__itemsCache.items.getLayoutState(self.__userId)
        if layoutState == AchievementsLayoutStates.AUTO:
            significantAchievementsList = self.__getSignificantAchievementsList()
        else:
            layout = self.__itemsCache.items.getLayout(self.__userId)
            significantAchievementsList = convertDbIdsToAchievements(layout, self.__dossier)
        prevAchievemetNameList = self.__achvmntCtrl.getPrevAchievementsList()
        significantAchievements = model.getSignificantAchievements()
        significantAchievements.clear()
        for achievement in significantAchievementsList:
            achievementModel = fillAchievementModel(achievement)
            achievementModel.setIsNew(achievementModel.getName() not in prevAchievemetNameList and not self.__isOtherPlayer)
            significantAchievements.addViewModel(achievementModel)

        significantAchievements.invalidate()
        if not self.__isOtherPlayer:
            self.__setPrevAchievementList()

    def __getSignificantAchievementsList(self):
        achievements20GeneralConfig = self.__lobbyContext.getServerSettings().getAchievements20GeneralConfig()
        layoutLength = achievements20GeneralConfig.getLayoutLength()
        mainlRules = achievements20GeneralConfig.getAutoGeneratingMainRules()
        extraRules = achievements20GeneralConfig.getAutoGeneratingExtraRules()
        significantAchievementsList = self.__dossier.getTotalStats().getSignificantAchievements(mainlRules, extraRules, layoutLength)
        return significantAchievementsList

    def __updateRating(self):
        rating = getNormalizedValue(getRating(userId=self.__userId))
        stats = self.__dossier.getRandomStats()
        achievements20GeneralConfig = self.__lobbyContext.getServerSettings().getAchievements20GeneralConfig()
        requiredCountOfBattles = achievements20GeneralConfig.getRequiredCountOfBattles()
        battlesLeftCount = requiredCountOfBattles - stats.getBattlesCount()
        with self.viewModel.transaction() as model:
            model.setPersonalScore(rating)
            model.setRequiredNumberOfBattles(requiredCountOfBattles)
            model.setBattlesLeftCount(0 if battlesLeftCount < 0 else battlesLeftCount)
            if isWTREnabled():
                checker = WTRStageChecker(achievements20GeneralConfig.getStagesOfWTR())
                groupId, stageId, _ = checker.getStage(rating)
                self.__prevRatingRank = groupId
                self.__prevRatingSubRank = stageId
                model.setCurrentRatingRank(self.__prevRatingRank)
                model.setCurrentRatingSubRank(self.__prevRatingSubRank)
        if not self.__isOtherPlayer:
            self.__setPrevStates()

    @server_settings.serverSettingsChangeListener(Configs.ACHIEVEMENTS20_CONFIG.value)
    def __onServerSettingsChanged(self, diff):
        self.__updateSettings()
        if isSummaryEnabled():
            self.__updatePage()
            with self.viewModel.transaction() as model:
                model.setEditState(self.__getEditState())

    def __onAchievementsSettings(self):
        with self.viewModel.transaction() as model:
            model.setIsSuccessfullyEdited(False)
            model.setIsEditOpened(True)
        showAchievementEditView()

    def __dossierResyncHandler(self, *_):
        self.__dossier = self.__itemsCache.items.getAccountDossier(self.__userId)
        self.__updatePage()

    def __getEditState(self):
        if not isEditingEnabled():
            return EditState.NOT_ENOUGH_ACHIEVEMENTS
        return EditState.DISABLED if not isLayoutEnabled() else EditState.AVAILABLE

    def __getDogTagBackportTooltipData(self, compId):
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.DOG_TAGS_INFO, specialArgs=[compId, self.__userId])

    def __getAchievementsBackportTooltipData(self, name, block):
        achievement = self.__dossier.getTotalStats().getAchievement((block, name))
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.ACHIEVEMENT, specialArgs=(self.__dossier.getDossierType(),
         dumpDossier(self.__dossier),
         block,
         name,
         isRareAchievement(achievement)))

    def __getPrevStates(self):
        with self.viewModel.transaction() as model:
            model.setPrevPersonalScore(self.__achvmntCtrl.getWtrPrevPoints())
            model.setPrevCurrentRatingRank(self.__achvmntCtrl.getWtrPrevRank())
            model.setPrevCurrentRatingSubRank(self.__achvmntCtrl.getWtrPrevSubRank())

    def __setPrevStates(self):
        if isWTREnabled():
            accountWtr = getNormalizedValue(getRating())
            self.__achvmntCtrl.setWtrPrevPoints(accountWtr)
            self.__achvmntCtrl.setWtrPrevRank(self.__prevRatingRank)
            self.__achvmntCtrl.setWtrPrevSubRank(self.__prevRatingSubRank)

    def __setPrevAchievementList(self):
        achievements = self.__dossier.getTotalStats().getAchievements(isInDossier=True, showHidden=False)
        achievementsList = [ achievement.getName() for section in achievements for achievement in section ]
        self.__achvmntCtrl.setPrevAchievementsList(achievementsList)

    def __showNotification(self):
        if not AccountSettings.getNotifications(ACHIEVEMENTS_VISITED):
            AccountSettings.setNotifications(ACHIEVEMENTS_VISITED, True)

    def __updateClanInfo(self):
        clanDBID, clanInfo = self.__itemsCache.items.getClanInfo(self.__userId)
        with self.viewModel.transaction() as model:
            if clanInfo is not None:
                clanInfo = ClanInfo(*clanInfo)
                model.otherPlayerInfo.setIsInClan(True)
                model.otherPlayerInfo.setClanName(clanInfo.getClanName())
                model.otherPlayerInfo.setClanPost(getClanRoleString(clanInfo.getMembersFlags()))
                model.otherPlayerInfo.setClanJoiningTime(backport.getLongDateFormat(clanInfo.getJoiningTime()))
                model.otherPlayerInfo.setClanEmblem(getClanEmblemURL(clanDBID, EmblemSize.SIZE_32))
                model.otherPlayerInfo.setShowClanButton(self.__lobbyContext.getServerSettings().clanProfile.isEnabled())
            self.__fillDogTagModel(model.otherPlayerInfo.dogTagModel)
        return

    def __fillDogTagModel(self, model):
        isDogTagEnabled = self.__lobbyContext.getServerSettings().isDogTagEnabled()
        model.setIsEnabled(isDogTagEnabled)
        if isDogTagEnabled:
            dogTag = PlayerDogTag.fromDict(self.__itemsCache.items.getDogTag(self.__userId))
            engraving = dogTag.getComponentByType(ComponentViewType.ENGRAVING)
            background = dogTag.getComponentByType(ComponentViewType.BACKGROUND)
            engravingImage = DogTagComposerClient.getComponentImage(engraving.compId, engraving.grade)
            bgImage = DogTagComposerClient.getComponentImage(background.compId)
            component = componentConfigAdapter.getComponentById(background.compId)
            model.setEngravingCompId(engraving.compId)
            model.setBackgroundCompId(background.compId)
            model.setEngraving(engravingImage)
            model.setBackground(bgImage)
            model.setPurpose(component.purpose.value.lower())
            animation = background.componentDefinition.animation
            if animation is not None:
                model.setAnimation(animation)
            grades = engraving.componentDefinition.grades
            if engraving and grades and engraving.grade == len(grades) - 1:
                model.setIsHighlighted(True)
        return

    def __openClanStatistic(self):
        if self.__lobbyContext.getServerSettings().clanProfile.isEnabled():
            clanID, clanInfo = self.__itemsCache.items.getClanInfo(self.__userId)
            if clanID != 0:
                clanInfo = ClanInfo(*clanInfo)
                showClanProfileWindow(clanID, clanInfo.getClanAbbrev())

    def __onAchievementLayoutChanged(self, ctx):
        self.__updateSignificantAchievements()
        with self.viewModel.transaction() as model:
            model.setIsSuccessfullyEdited(True)

    def __onEditViewClose(self, ctx):
        with self.viewModel.transaction() as model:
            model.setIsEditOpened(False)

    @property
    def __isOtherPlayer(self):
        return self.__userId is not None

    def __getBackgroundAsset(self, backgroundName):
        asset = R.images.gui.maps.icons.achievements.summary.backgrounds.dyn(backgroundName)
        if not asset.isValid():
            _logger.error('[SummaryView] getServiceRecordBackground asset does not exist')
            return 0
        return asset()

    def __getRibbonAsset(self, ribbonName):
        asset = R.images.gui.maps.icons.achievements.summary.ribbons.dyn(ribbonName)
        if not asset.isValid():
            _logger.error('[SummaryView] getServiceRecordRibbon asset does not exist')
            return 0
        return asset()

    def __getServiceRecordBackgroundOptions(self):
        options = []
        for index, name in getServiceRecordBackgroundOptions():
            image = R.images.gui.maps.icons.achievements.summary.backgrounds.dyn(name)
            if not image.isValid():
                _logger.error('[SummaryView] getServiceRecordBackgroundOptions image does not exist')
                continue
            label = R.strings.achievements_page.summary.achievements.customization.backgrounds.dyn(name)
            if not label.isValid():
                _logger.error('[SummaryView] getServiceRecordBackgroundOptions label does not exist')
                continue
            options.append((index, image(), label()))

        return options

    def __getServiceRecordRibbonOptions(self):
        options = []
        for index, name in getServiceRecordRibbonOptions():
            image = R.images.gui.maps.icons.achievements.summary.ribbons.dyn(name)
            if not image.isValid():
                _logger.error('[SummaryView] getServiceRecordRibbonOptions image does not exist')
                continue
            ribbonIcon = '{}_icon'.format(name)
            icon = R.images.gui.maps.icons.achievements.summary.ribbons.dyn(ribbonIcon)
            if not icon.isValid():
                _logger.error('[SummaryView] getServiceRecordRibbonOptions icon does not exist')
                continue
            options.append((index, image(), icon()))

        return options

    def __updateCustomizationsOptions(self):
        with self.viewModel.transaction() as model:
            isCustomizationEnabled = self.__wotPlusCtrl.getSettingsStorage().isServiceRecordCustomizationAvailable()
            if not isCustomizationEnabled:
                return
            bgOptionsData = self.__getServiceRecordBackgroundOptions()
            bgOptions = model.getBackgroundOptions()
            bgOptions.clear()
            bgOptions.reserve(len(bgOptionsData))
            for index, image, label in bgOptionsData:
                bgModel = BackgroundModel()
                bgModel.setSlug(str(index))
                bgModel.setImage(image)
                bgModel.setLabel(label)
                bgOptions.addViewModel(bgModel)

            bgOptions.invalidate()
            ribbonImage = self.__getServiceRecordRibbonOptions()
            ribbonOptions = model.getRibbonOptions()
            ribbonOptions.clear()
            ribbonOptions.reserve(len(ribbonImage))
            for index, image, icon in ribbonImage:
                ribbonModel = RibbonModel()
                ribbonModel.setSlug(str(index))
                ribbonModel.setImage(image)
                ribbonModel.setIcon(icon)
                ribbonOptions.addViewModel(ribbonModel)

            ribbonOptions.invalidate()

    def __updateCustomizationsVisuals(self):
        with self.viewModel.transaction() as model:
            isCustomizationEnabled = self.__wotPlusCtrl.getSettingsStorage().isServiceRecordCustomizationAvailable()
            isButtonEnabled = not self.__isOtherPlayer and isCustomizationEnabled
            if not isCustomizationEnabled and model.getIsInCustomizationMode():
                model.setIsInCustomizationMode(False)
            model.setIsCustomizationButtonVisible(isButtonEnabled)
            model.setIsCustomizationButtonEnabled(isButtonEnabled)
            if self.__isOtherPlayer:
                customizationData = self.__itemsCache.items.getServiceRecordCustomization(self.__userId)
                backgroundIndex, backgroundName = getValidatedServiceRecordBackground(customizationData.get('background', 0))
                ribbonIndex, ribbonName = getValidatedServiceRecordRibbon(customizationData.get('ribbon', 0))
            else:
                backgroundIndex, backgroundName = self.__wotPlusCtrl.getServiceRecordBackground()
                ribbonIndex, ribbonName = self.__wotPlusCtrl.getServiceRecordRibbon()
            model.background.setSlug(str(backgroundIndex))
            model.background.setImage(self.__getBackgroundAsset(backgroundName))
            model.ribbon.setSlug(str(ribbonIndex))
            model.ribbon.setImage(self.__getRibbonAsset(ribbonName))

    def __onSetBackgroundDraft(self, ctx):
        with self.viewModel.transaction() as model:
            slug = int(ctx.get('backgroundDraftSlug'))
            bgOptionsData = self.__getServiceRecordBackgroundOptions()
            for index, image, label in bgOptionsData:
                if slug == index:
                    model.backgroundDraft.setSlug(str(index))
                    model.backgroundDraft.setImage(image)
                    model.backgroundDraft.setLabel(label)
                    break

    def __onSetRibbonDraft(self, ctx):
        with self.viewModel.transaction() as model:
            slug = int(ctx.get('ribbonDraftSlug'))
            ribbonImages = self.__getServiceRecordRibbonOptions()
            for index, image, icon in ribbonImages:
                if slug == index:
                    model.ribbonDraft.setSlug(str(index))
                    model.ribbonDraft.setImage(image)
                    model.ribbonDraft.setIcon(icon)
                    break

    def __onSetIsInCustomizationMode(self, ctx):
        with self.viewModel.transaction() as model:
            model.setIsInCustomizationMode(ctx.get('isInCustomizationMode'))

    @adisp_process
    def __onCustomizationConfirmed(self, ctx):
        yield ServiceRecordProcessor(int(ctx.get('backgroundSlug')), int(ctx.get('ribbonSlug'))).request()
        self.__onSetIsInCustomizationMode({'isInCustomizationMode': False})

    @wg_async
    def __onCustomizationDiscard(self, ctx):
        result = yield wg_await(showServiceRecordCustomizationConfirmDialog())
        if result is None or result.busy or not result.result:
            self.__onSetIsInCustomizationMode({'isInCustomizationMode': False})
            return
        else:
            self.__onCustomizationConfirmed(ctx)
            return

    def __onRenewableSubscriptionStatusChanged(self):
        self.__updateCustomizationsOptions()
        self.__updateCustomizationsVisuals()
