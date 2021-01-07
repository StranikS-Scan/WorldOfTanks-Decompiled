# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dog_tags/dog_tags_view.py
import logging
from collections import defaultdict
from operator import attrgetter
import typing
import BigWorld
from constants import DOG_TAGS_CONFIG
from dog_tags_common.components_config import componentConfigAdapter
from dog_tags_common.config.common import ComponentViewType, ComponentPurpose
from dog_tags_common.dog_tags_storage import ProgressStorage, UnlockedComponentsStorage
from frameworks.wulf import ViewFlags, ViewSettings
from gui import GUI_SETTINGS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.dog_tags.dog_tags_view_model import DogTagsViewModel
from gui.impl.gen.view_models.views.lobby.dog_tags.triumph_tooltip_model import TriumphTooltipModel
from gui.impl.gen.view_models.views.lobby.dog_tags.dedication_tooltip_model import DedicationTooltipModel
from gui.impl.gen.view_models.views.lobby.dog_tags.three_months_tooltip_model import ThreeMonthsTooltipModel
from gui.impl.gen import R
import WWISE
from gui.sounds.filters import switchHangarOverlaySoundFilter
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.dog_tags.dog_tag_composer import DogTagComposerLobby
from gui.impl.pub import ViewImpl
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.server_events import settings as userSettings
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from helpers.time_utils import getCurrentLocalServerTimestamp, getTimeStructInLocal
from shared_utils import CONST_CONTAINER
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from typing import Dict, Callable, Optional, Union
    from account_helpers.dog_tags import DogTags as DogTagsAccountHelper
    from frameworks.wulf import View, ViewEvent, ViewModel
_logger = logging.getLogger(__name__)
DEFAULT_DOG_TAGS_TAB = ComponentViewType.ENGRAVING.getTabIdx()
DOG_TAG_INFO_PAGE_KEY = 'infoPage'

class DogTagsView(ViewImpl):
    __slots__ = ('_dogTagsHelper', '_composer', '_tooltipModelFactories')
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
        self._tooltipModelFactories = {R.views.lobby.dog_tags.DedicationTooltip(): self._gradesTooltipModelFactory(DedicationTooltipModel),
         R.views.lobby.dog_tags.TriumphTooltip(): self._gradesTooltipModelFactory(TriumphTooltipModel),
         R.views.lobby.dog_tags.ThreeMonthsTooltip(): self._threeMonthTooltipModelFactory}
        super(DogTagsView, self).__init__(settings)

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
            model = self._tooltipModelFactories[contentID](event.getArgument(compIdArgName))
            settings = ViewSettings(contentID, model=model)
            return ViewImpl(settings)

    @property
    def viewModel(self):
        return super(DogTagsView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.viewModel.onExit += self.__onExit
        self.viewModel.onEquip += self.__onEquip
        self.viewModel.onTabSelect += self.__onTabSelected
        self.viewModel.onInfoButtonClick += self.__onInfoButtonClicked
        self.viewModel.onPlayVideo += self.__onPlayVideo
        self._dogTagsHelper.onDogTagDataChanged += self.__onDogTagDataChanged
        self.viewModel.onOnboardingCloseClick += self.__onOnboardingCloseClick
        self.viewModel.onNewComponentHover += self.__onNewComponentHover
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def _finalize(self):
        super(DogTagsView, self)._finalize()
        self._soundsOnExit()
        self.viewModel.onExit -= self.__onExit
        self.viewModel.onEquip -= self.__onEquip
        self.viewModel.onTabSelect -= self.__onTabSelected
        self.viewModel.onInfoButtonClick -= self.__onInfoButtonClicked
        self.viewModel.onPlayVideo -= self.__onPlayVideo
        self._dogTagsHelper.onDogTagDataChanged -= self.__onDogTagDataChanged
        self.viewModel.onOnboardingCloseClick -= self.__onOnboardingCloseClick
        self.viewModel.onNewComponentHover -= self.__onNewComponentHover
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def _onLoading(self, highlightedComponentId=-1, makeTopView=False):
        _logger.debug('DogTags::_onLoading')
        self.__update(highlightedComponentId)
        switchHangarOverlaySoundFilter(on=True)
        WWISE.WW_setState(SOUNDS.STATE_PLACE, SOUNDS.STATE_PLACE_DOG_TAGS)
        self.viewModel.setIsTopView(makeTopView)

    @staticmethod
    def _soundsOnExit():
        switchHangarOverlaySoundFilter(on=False)
        WWISE.WW_eventGlobal(backport.sound(R.sounds.dt_customisation_exit()))
        WWISE.WW_eventGlobal(backport.sound(R.sounds.dt_flame_stop()))

    def _markComponentAsViewed(self, compId):
        with self.viewModel.transaction() as tx:
            with userSettings.dogTagsSettings() as dt:
                dt.markComponentAsSeen(compId)
            self._composer.updateComponentModel(tx, compId)
            self.__updateNotificationCounters(tx)
        g_eventBus.handleEvent(events.DogTagsEvent(events.DogTagsEvent.COUNTERS_UPDATED), EVENT_BUS_SCOPE.LOBBY)

    def _gradesTooltipModelFactory(self, modelCtor):

        def _inner(engravingId):
            engraving = self._dogTagsHelper.getDogTagComponentForAccount(engravingId)
            viewModel = modelCtor()
            with viewModel.transaction() as model:
                model.setCurrentGrade(engraving.grade)
                gradesArray = model.getGradeValues()
                for grade in engraving.componentDefinition.grades:
                    gradesArray.addReal(grade)

                model.setComponentTitle(self._composer.getComponentTitleRes(engraving.compId))
                model.setProgressNumberType(engraving.componentDefinition.numberType.value)
            return viewModel

        return _inner

    def _threeMonthTooltipModelFactory(self, engravingId):
        viewModel = ThreeMonthsTooltipModel()
        with viewModel.transaction() as model:
            engravingComponent = self._dogTagsHelper.getDogTagComponentForAccount(engravingId)
            engravingId = engravingComponent.compId
            skillRecords = sorted(self._dogTagsHelper.getSkillData(engravingId), key=lambda e: e.date)
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
        return viewModel

    @staticmethod
    def _getMonthRes(monthNum):
        monthRes = R.strings.menu.dateTime.months.full.num(monthNum)()
        return monthRes

    def __update(self, highlightedComponentId=-1):
        _logger.debug('DogTags::Update')
        clanProfile = self._webCtrl.getAccountProfile()
        dogTag = self._dogTagsHelper.getDisplayableDT(clanProfile)
        with self.viewModel.transaction() as tx:
            self._composer.fillModel(tx.equippedDogTag, dogTag)
            self._composer.fillGrid(tx)
            selectedTabIdx = DogTagsView.__getSelectedTabIdx(highlightedComponentId)
            tx.setTab(selectedTabIdx)
            tx.setOnboardingEnabled(userSettings.getDogTagsSettings().onboardingEnabled)
            _logger.debug('DogTags::selectedTabIdx=%d', selectedTabIdx)
            self.__updateNotificationCounters(tx)

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

    @args2params(int, int)
    def __onEquip(self, background, engraving):
        _logger.debug('DogTags::onEquip(%s, %s)', background, engraving)
        self._dogTagsHelper.updatePlayerDT(background, engraving)
        dogTag = self._dogTagsHelper.getDisplayableDTForComponents([background, engraving], self._webCtrl.getAccountProfile())
        with self.viewModel.transaction() as tx:
            if dogTag:
                self._composer.fillModel(tx.equippedDogTag, dogTag)

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

    def __onExit(self):
        if self.viewFlags == ViewFlags.LOBBY_TOP_SUB_VIEW:
            self.destroyWindow()
        else:
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onDogTagDataChanged(self, diff):
        _logger.debug('DogTags::__onDogTagDataChanged: %s', diff)
        if ProgressStorage.key in diff or UnlockedComponentsStorage.key in diff:
            self.__update()

    def __onServerSettingsChange(self, diff):
        if DOG_TAGS_CONFIG in diff:
            self.__update()


class SOUNDS(CONST_CONTAINER):
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_DOG_TAGS = 'STATE_hangar_place_dog_tags'
