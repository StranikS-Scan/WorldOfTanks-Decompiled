# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dog_tags/dog_tags_view.py
import logging
from collections import defaultdict
from operator import attrgetter
import typing
import BigWorld
import WWISE
from BWUtil import AsyncReturn
from constants import DOG_TAGS_CONFIG
from dog_tags_common.components_config import componentConfigAdapter
from dog_tags_common.config.common import ComponentViewType, ComponentPurpose
from frameworks.wulf import ViewFlags, ViewSettings
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.dog_tags.dedication_tooltip_model import DedicationTooltipModel
from gui.impl.gen.view_models.views.lobby.dog_tags.dog_tags_view_model import DogTagsViewModel
from gui.impl.gen.view_models.views.lobby.dog_tags.three_months_tooltip_model import ThreeMonthsTooltipModel
from gui.impl.gen.view_models.views.lobby.dog_tags.triumph_tooltip_model import TriumphTooltipModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.dog_tags.animated_dog_tag_composer import AnimatedDogTagComposer
from gui.impl.lobby.dog_tags.dog_tag_composer import DogTagComposerLobby
from gui.impl.lobby.dog_tags.ranked_efficiency_tooltip import RankedEfficiencyTooltip
from gui.impl.pub import ViewImpl
from gui.server_events import settings as userSettings
from gui.shared import events
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.close_confiramtor_helper import CloseConfirmatorsHelper
from gui.shared.event_dispatcher import showBrowserOverlayView, showDogTagCustomizationConfirmDialog
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from helpers.time_utils import getCurrentLocalServerTimestamp, getTimeStructInLocal
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.web import IWebController
from uilogging.dog_tags.logger import DogTagsViewLogger
from uilogging.dog_tags.logging_constants import DogTagsViewKeys
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from typing import Dict, Callable, Optional, Union
    from frameworks.wulf import View, ViewEvent
    from account_helpers.dog_tags import DogTags as DogTagsAccountHelper
_logger = logging.getLogger(__name__)
DEFAULT_DOG_TAGS_TAB = ComponentViewType.ENGRAVING.getTabIdx()
DOG_TAG_INFO_PAGE_KEY = 'infoPage'

class DogTagsView(ViewImpl):
    __slots__ = ('_dogTagsHelper', '_composer', '_tooltipModelFactories', '_animatedComposer', '__closeConfirmatorHelper', '__selectedEngraving', '__selectedBackground', '__uiLogging')
    _webCtrl = dependency.descriptor(IWebController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, layoutID=R.views.lobby.dog_tags.DogTagsView(), *args, **kwargs):
        settingFlags = ViewFlags.LOBBY_TOP_SUB_VIEW if kwargs.get('makeTopView', False) else ViewFlags.LOBBY_SUB_VIEW
        settings = ViewSettings(layoutID)
        settings.args = args
        settings.kwargs = kwargs
        settings.flags = settingFlags
        settings.model = DogTagsViewModel()
        self._dogTagsHelper = BigWorld.player().dogTags
        self._composer = DogTagComposerLobby(self._dogTagsHelper)
        self._animatedComposer = AnimatedDogTagComposer(self._dogTagsHelper)
        self.__closeConfirmatorHelper = CloseConfirmatorsHelper()
        self.__selectedEngraving = None
        self.__selectedBackground = None
        self._tooltipModelFactories = {R.views.lobby.dog_tags.DedicationTooltip(): DedicationTooltip,
         R.views.lobby.dog_tags.TriumphTooltip(): TriumphTooltip,
         R.views.lobby.dog_tags.ThreeMonthsTooltip(): ThreeMonthsTooltip,
         R.views.lobby.dog_tags.RankedEfficiencyTooltip(): RankedEfficiencyTooltip}
        self.__uiLogging = DogTagsViewLogger(DogTagsViewKeys.ACCOUNT_DASHBOARD)
        super(DogTagsView, self).__init__(settings)
        return

    def highlightComponent(self, highlightedComponentId):
        tabIdx = self.__getComponentTabIdx(highlightedComponentId)
        if tabIdx is not None:
            self.__switchTab(tabIdx)
        return

    def createToolTipContent(self, event, contentID):
        compIdArgName = 'componentId'
        if not event.hasArgument(compIdArgName):
            _logger.error('DogTags view tried to create tooltip without specifying component ID')
            return None
        elif contentID not in self._tooltipModelFactories:
            _logger.error('DogTags view tried creating invalid tooltip with contentID %d', contentID)
            return None
        else:
            return self._tooltipModelFactories[contentID](event.getArgument(compIdArgName))

    @property
    def viewModel(self):
        return super(DogTagsView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.viewModel.onExit += self.__onExit
        self.viewModel.onEquip += self.__onEquip
        self.viewModel.onTabSelect += self.__onTabSelected
        self.viewModel.onInfoButtonClick += self.__onInfoButtonClicked
        self.viewModel.onPlayVideo += self.__onPlayVideo
        self.viewModel.onUpdateSelectedDT += self.__onUpdateSelectedDT
        self._dogTagsHelper.onDogTagDataChanged += self.__onDogTagDataChanged
        self.viewModel.onOnboardingCloseClick += self.__onOnboardingCloseClick
        self.viewModel.onNewComponentHover += self.__onNewComponentHover
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__closeConfirmatorHelper.start(self.__onExit)

    def _finalize(self):
        super(DogTagsView, self)._finalize()
        self.viewModel.onExit -= self.__onExit
        self.viewModel.onEquip -= self.__onEquip
        self.viewModel.onTabSelect -= self.__onTabSelected
        self.viewModel.onInfoButtonClick -= self.__onInfoButtonClicked
        self.viewModel.onPlayVideo -= self.__onPlayVideo
        self.viewModel.onUpdateSelectedDT -= self.__onUpdateSelectedDT
        self._dogTagsHelper.onDogTagDataChanged -= self.__onDogTagDataChanged
        self.viewModel.onOnboardingCloseClick -= self.__onOnboardingCloseClick
        self.viewModel.onNewComponentHover -= self.__onNewComponentHover
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self._soundsOnExit()
        self.__closeConfirmatorHelper.stop()

    def _onLoading(self, highlightedComponentId=-1, makeTopView=False):
        _logger.debug('DogTags::_onLoading')
        self.__update(highlightedComponentId)
        self.viewModel.setIsTopView(makeTopView)
        if not userSettings.getDogTagsSettings().customizableDogTagsVisited:
            with userSettings.dogTagsSettings() as dt:
                dt.setCustomizableDogTagsVisited(True)

    @staticmethod
    def _soundsOnExit():
        switchHangarOverlaySoundFilter(on=False)
        WWISE.WW_eventGlobal(backport.sound(R.sounds.dt_flame_stop()))

    def _markComponentAsViewed(self, compId):
        with self.viewModel.transaction() as tx:
            with userSettings.dogTagsSettings() as dt:
                dt.markComponentAsSeen(compId)
            self._composer.updateComponentModel(tx, compId)
            self.__updateNotificationCounters(tx)
        g_eventBus.handleEvent(events.DogTagsEvent(events.DogTagsEvent.COUNTERS_UPDATED), EVENT_BUS_SCOPE.LOBBY)

    def __isAnimatedDogTagEquipped(self):
        return self._composer.isDogTagEquipped(self._animatedComposer.getSelectedDogTag(self._webCtrl.getAccountProfile()))

    def __update(self, highlightedComponentId=-1):
        _logger.debug('DogTags::__update')
        clanProfile = self._webCtrl.getAccountProfile()
        dogTag = self._composer.getSelectedDogTag(clanProfile)
        engraving, background = self.__getCurrentDogTag()
        with self.viewModel.transaction() as tx:
            self.__selectedBackground = background
            self.__selectedEngraving = engraving
            self._composer.fillModel(tx.equippedDogTag, dogTag)
            self._composer.fillGrid(tx)
            selectedTabIdx = DogTagsView.__getSelectedTabIdx(highlightedComponentId)
            tx.setTab(selectedTabIdx)
            tx.setOnboardingEnabled(userSettings.getDogTagsSettings().onboardingEnabled)
            _logger.debug('DogTags::selectedTabIdx=%d', selectedTabIdx)
            self.__updateNotificationCounters(tx)
            self.viewModel.setIsAnimatedDogTagSelected(self.__isAnimatedDogTagEquipped())

    @staticmethod
    def __getSelectedTabIdx(highlightedComponentId):
        lastVisitedDogTagsTabIdx = userSettings.getDogTagsSettings().lastVisitedDogTagsTabIdx
        selectedTabIdx = DEFAULT_DOG_TAGS_TAB
        if lastVisitedDogTagsTabIdx is not None:
            selectedTabIdx = lastVisitedDogTagsTabIdx
        highlightedComponentTabIdx = DogTagsView.__getComponentTabIdx(highlightedComponentId)
        if highlightedComponentTabIdx is not None:
            selectedTabIdx = highlightedComponentTabIdx
        return selectedTabIdx

    @staticmethod
    def __getComponentTabIdx(compId):
        if compId == -1:
            return None
        else:
            highComp = componentConfigAdapter.getComponentById(compId)
            return None if highComp is None else highComp.viewType.getTabIdx()

    @args2params(int)
    def __onTabSelected(self, newTab):
        self.__switchTab(newTab)

    def __switchTab(self, newTab):
        self.viewModel.setTab(newTab)
        with userSettings.dogTagsSettings() as dt:
            dt.setLastVisitedDogTagsTab(newTab)
        _logger.debug('DogTags::storing selectedTabIdx=%d', newTab)

    def __onInfoButtonClicked(self):
        url = GUI_SETTINGS.dogTagsInfoPage
        _logger.info('Opening info page: %s', url)
        showBrowserOverlayView(url, VIEW_ALIAS.BROWSER_OVERLAY)

    def __updateNotificationCounters(self, model):
        unseenComps = self._dogTagsHelper.getUnseenComps()
        counters = {viewType:defaultdict(int) for viewType in ComponentViewType}
        for compId in unseenComps:
            comp = componentConfigAdapter.getComponentById(compId)
            counters[comp.viewType][comp.purpose] += 1

        model.setNewBackgroundComponentCount(sum(counters[ComponentViewType.BACKGROUND].values()))
        model.setNewEngravingComponentCount(sum(counters[ComponentViewType.ENGRAVING].values()))
        model.setNewEngravingDedicationCount(counters[ComponentViewType.ENGRAVING][ComponentPurpose.DEDICATION])
        model.setNewEngravingTriumphCount(counters[ComponentViewType.ENGRAVING][ComponentPurpose.TRIUMPH])
        model.setNewEngravingSkillCount(counters[ComponentViewType.ENGRAVING][ComponentPurpose.SKILL])

    def __onEquip(self):
        with userSettings.dogTagsSettings() as dt:
            dt.setSelectedCustomizable([self.__selectedBackground, self.__selectedEngraving])
        self._dogTagsHelper.updatePlayerDT(self.__selectedBackground, self.__selectedEngraving)

    @args2params(str)
    def __onPlayVideo(self, urlKey):
        url = ''
        if urlKey == 'onboardingVideo1':
            url = GUI_SETTINGS.dogTagsOnboardingVideo1
        elif urlKey == 'onboardingVideo2':
            url = GUI_SETTINGS.dogTagsOnboardingVideo2
        _logger.info('Starting video: %s', url)
        showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT)

    def __onOnboardingCloseClick(self):
        with userSettings.dogTagsSettings() as dt:
            dt.setOnboardingEnabled(False)
            with self.viewModel.transaction() as tx:
                tx.setOnboardingEnabled(dt.onboardingEnabled)

    @args2params(int)
    def __onNewComponentHover(self, compId):
        self._markComponentAsViewed(compId)

    @wg_async
    def __onExit(self):
        canQuit = yield wg_await(self.__canQuit())
        if not canQuit:
            raise AsyncReturn(False)
        if self.viewFlags == ViewFlags.LOBBY_TOP_SUB_VIEW:
            self.destroyWindow()
        else:
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)
        raise AsyncReturn(canQuit)

    def __getCurrentDogTag(self):
        clanProfile = self._webCtrl.getAccountProfile()
        dogTag = self._composer.getSelectedDogTag(clanProfile)
        engraving = dogTag.getComponentByType(ComponentViewType.ENGRAVING).compId
        background = dogTag.getComponentByType(ComponentViewType.BACKGROUND).compId
        return (engraving, background)

    def __onDogTagDataChanged(self, diff):
        _logger.debug('DogTags::__onDogTagDataChanged: %s', diff)
        self.__update()

    def __onServerSettingsChange(self, diff):
        if DOG_TAGS_CONFIG in diff:
            if not self.lobbyContext.getServerSettings().isDogTagCustomizationScreenEnabled():
                self.destroyWindow()

    @args2params(int, int)
    def __onUpdateSelectedDT(self, background=None, engraving=None):
        self.__selectedBackground = background
        self.__selectedEngraving = engraving

    @wg_async
    def __canQuit(self):
        engraving, background = self.__getCurrentDogTag()
        if background == self.__selectedBackground and engraving == self.__selectedEngraving:
            raise AsyncReturn(True)
        result = yield wg_await(showDogTagCustomizationConfirmDialog(self.__selectedBackground, self.__selectedEngraving, self.getParentWindow()))
        isOK, data = result.result
        if isOK and data['saveChanges']:
            self.__onEquip()
        raise AsyncReturn(isOK)


class GradesTooltip(ViewImpl):

    def __init__(self, contentId, contentModel, *args, **kwargs):
        settings = ViewSettings(contentId, model=contentModel)
        settings.args = args
        settings.kwargs = kwargs
        super(GradesTooltip, self).__init__(settings, *args, **kwargs)

    def _onLoading(self, engravingId):
        engraving = BigWorld.player().dogTags.getDogTagComponentForAccount(engravingId)
        viewModel = self.getViewModel()
        with viewModel.transaction() as model:
            model.setCurrentGrade(engraving.grade)
            gradesArray = model.getGradeValues()
            for grade in engraving.componentDefinition.grades:
                gradesArray.addReal(grade)

            model.setComponentTitle(DogTagComposerLobby.getComponentTitleRes(engraving.compId))
            model.setProgressNumberType(engraving.componentDefinition.numberType.value)


class DedicationTooltip(GradesTooltip):

    def __init__(self, *args, **kwargs):
        super(DedicationTooltip, self).__init__(R.views.lobby.dog_tags.DedicationTooltip(), DedicationTooltipModel(), *args, **kwargs)


class TriumphTooltip(GradesTooltip):

    def __init__(self, *args, **kwargs):
        super(TriumphTooltip, self).__init__(R.views.lobby.dog_tags.TriumphTooltip(), TriumphTooltipModel(), *args, **kwargs)


class ThreeMonthsTooltip(ViewImpl):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.dog_tags.ThreeMonthsTooltip(), model=ThreeMonthsTooltipModel())
        settings.args = args
        settings.kwargs = kwargs
        super(ThreeMonthsTooltip, self).__init__(settings, *args, **kwargs)

    def _onLoading(self, engravingId):
        viewModel = self.getViewModel()
        dtHelper = BigWorld.player().dogTags
        with viewModel.transaction() as model:
            engravingComponent = dtHelper.getDogTagComponentForAccount(engravingId)
            engravingId = engravingComponent.compId
            skillRecords = sorted(dtHelper.getSkillData(engravingId), key=lambda e: e.date)
            indexMax = -1
            if skillRecords:
                maxValue = max(skillRecords[::-1], key=attrgetter('value'))
                if maxValue.value >= engravingComponent.componentDefinition.grades[0]:
                    indexMax = skillRecords.index(maxValue)
            model.setHighlightedIndex(indexMax)
            monthNames = model.getMonthNames()
            monthlyValues = model.getMonthlyValues()
            for date, value in skillRecords:
                monthRes = self._getMonthRes(date[1])
                monthNames.addResource(monthRes)
                if value is not None:
                    monthlyValues.addReal(value)

            currentMonth = getTimeStructInLocal(getCurrentLocalServerTimestamp()).tm_mon
            model.setCurrentMonth(self._getMonthRes(currentMonth))
            model.setProgressNumberType(engravingComponent.componentDefinition.numberType.value)
        return

    @staticmethod
    def _getMonthRes(monthNum):
        monthRes = R.strings.menu.dateTime.months.full.num(monthNum)()
        return monthRes
