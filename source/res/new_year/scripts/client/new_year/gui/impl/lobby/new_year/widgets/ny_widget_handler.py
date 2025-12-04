# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/widgets/ny_widget_handler.py
from helpers.events_handler import EventsHandler
from new_year_account_settings import getNYSetting, setNYSettings
from new_year.helpers.server_settings import getNewYearGeneralConfig
from new_year.ny_constants import NY_ACTIVE_WIDGET_TRANSITION_SHOWN, PERCENT
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.ny_constants import ViewAliases
from new_year.gui.impl.new_year.new_year_helper import IS_ROMAN_NUMBERS_ALLOWED
from new_year.gui.shared.events import NewYearEvent
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter
from new_year.ny_constants import CustomizationObjects
from new_year.skeletons.new_year import INewYearController, INewYearTamagotchiController
from new_year.gui.impl.gen.view_models.common.ny_event_state_model import EventState
from gui.impl.gen import R
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.new_year_main_widget_anim_types import NewYearMainWidgetAnimTypes
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.new_year_main_widget_model import NewYearMainWidgetModel, State
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from helpers import dependency, getLanguageCode, int2roman
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from skeletons.account_helpers.settings_core import ISettingsCore
from new_year.skeletons.new_year import ITamagotchiDataProvider

class NyWidgetHandler(EventsHandler):
    __slots__ = ('__model', '__level', '__prevAtmPoints', '__maxLevel', '__lobbyMode')
    _itemsCache = dependency.descriptor(IItemsCache)
    __gui = dependency.descriptor(IGuiLoader)
    __nyController = dependency.descriptor(INewYearController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __dataProvider = dependency.descriptor(ITamagotchiDataProvider)
    __tamagotchiController = dependency.descriptor(INewYearTamagotchiController)

    def __init__(self, model):
        self.__model = model
        self.__level = NewYearAtmospherePresenter.getLevel()
        self.__prevAtmPoints = 0
        self.__maxLevel = self._itemsCache.items.festivity.getMaxLevel()
        self.__lobbyMode = True

    def initialize(self):
        self._subscribe()
        g_eventBus.addListener(NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchView, EVENT_BUS_SCOPE.LOBBY)
        currentObject = NewYearNavigation.getCurrentObject()
        self.__lobbyMode = currentObject is None
        with self.__model.transaction() as tx:
            self.__updateData(tx)
            self.__updateLevel(tx)
            self.__updateActiveState(tx)
            tx.setIsExtendedAnim(True)
        self.__updateRaccoonInfo()
        self.__setNeedToShowTransition()
        return

    def finalize(self):
        self._unsubscribe()
        g_eventBus.removeListener(NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchView, scope=EVENT_BUS_SCOPE.LOBBY)

    def update(self):
        with self.__model.transaction() as tx:
            self.__updateData(tx)
            self.__updateLevel(tx)
        self.__updateRaccoonInfo()

    def _getEvents(self):
        return ((NewYearNavigation.onObjectStateChanged, self.__onObjectStateChanged), (self.__nyController.onStateChanged, self.__onObjectStateChanged), (self.__dataProvider.onSimulationEnd, self.__updateRaccoonInfo))

    def __setNeedToShowTransition(self):
        if self.__checkIfNeedToShowWidgetTransition():
            setNYSettings(NY_ACTIVE_WIDGET_TRANSITION_SHOWN, True)

    def __checkIfNeedToShowWidgetTransition(self):
        activeWidgetTransitionShown = getNYSetting(NY_ACTIVE_WIDGET_TRANSITION_SHOWN)
        isFirstEntrance = not self.__nyController.isOnboardingFinished()
        return not activeWidgetTransitionShown and not isFirstEntrance

    def __updateData(self, model):
        model.setLobbyMode(self.__lobbyMode)
        model.setUserLanguage(str(getLanguageCode()).upper())
        model.setBonusValue(self.__getBonusValue())
        model.setMaxBonusValue(int(self.__nyController.getMaxBonusValue() * PERCENT))
        model.setIsRomanNumbersAllowed(IS_ROMAN_NUMBERS_ALLOWED)
        model.setIsEnabled(NewYearNavigation.getCurrentObject() != CustomizationObjects.FIR)
        model.setIsFirstEntrance(not self.__nyController.isOnboardingFinished())
        model.eventState.setValue(EventState.PAUSED if self.__nyController.isSuspended() else EventState.ACTIVE)
        model.setIsActiveWidgetTransitionShown(getNYSetting(NY_ACTIVE_WIDGET_TRANSITION_SHOWN))
        model.setProgress(NewYearAtmospherePresenter.getPercentsLevelProgress())
        model.setPetLevelNeed(getNewYearGeneralConfig().getRaccoonLevelOpen())
        model.setProgressState(self.__nyController.isEnabled())
        model.setIsPetEntrance(not self.__dataProvider.isOnboarding)

    def __updateLevel(self, model):
        animationType = NewYearMainWidgetAnimTypes.ANIM_TYPE_NONE
        level = NewYearAtmospherePresenter.getLevel()
        if level != self.__level:
            if level > self.__level:
                animationType = NewYearMainWidgetAnimTypes.ANIM_TYPE_UP
            else:
                animationType = NewYearMainWidgetAnimTypes.ANIM_TYPE_DOWN_LONG
            self.__level = level
        maxLevel = self._itemsCache.items.festivity.getMaxLevel()
        if maxLevel != self.__maxLevel:
            self.__maxLevel = maxLevel
            animationType = NewYearMainWidgetAnimTypes.ANIM_TYPE_UP_LONG
        currentAtmPoints = self._itemsCache.items.festivity.getAtmPoints()
        if currentAtmPoints <= self.__prevAtmPoints and animationType == NewYearMainWidgetAnimTypes.ANIM_TYPE_NONE:
            animationType = NewYearMainWidgetAnimTypes.ANIM_TYPE_DOWN
        self.__prevAtmPoints = currentAtmPoints
        model.setAnimationType(animationType)
        model.setLevel(self.__level)
        model.setLevelRoman(int2roman(self.__maxLevel))
        currentPoints, nextPoints = NewYearAtmospherePresenter.getLevelProgress()
        model.setCurrentPoints(currentPoints)
        model.setNextPoints(nextPoints)

    def __updateRaccoonInfo(self):
        with self.__model.transaction() as ts:
            if self.__dataProvider.isValidConfig:
                self.__updateRacoon(ts)
            else:
                self.__disablePet(ts)

    def __disablePet(self, model):
        model.setPetState(State.PAUSE if not self.__tamagotchiController.isPetVisible else State.EMPTY)
        petNeed = model.getPetNeed()
        petNeed.clear()
        petNeed.invalidate()

    def __updateRacoon(self, model):
        model.setBonusValue(self.__getBonusValue())
        petState = self.__dataProvider.playerInfo.state
        state = State(petState)
        model.setPetState(state)
        petNeeds = model.getPetNeed()
        petNeeds.clear()
        for item in self.__dataProvider.getNeeds():
            petNeeds.addString(item)

        petNeeds.invalidate()

    def __onObjectStateChanged(self):
        currentObject = NewYearNavigation.getCurrentObject()
        self.__lobbyMode = currentObject is None
        with self.__model.transaction() as tx:
            self.__updateData(tx)
            self.__updateLevel(tx)
            self.__updateActiveState(tx)
        self.__updateRaccoonInfo()
        return

    @staticmethod
    def __updateActiveState(model):
        currentView = NewYearNavigation.getCurrentViewName()
        model.setIsEnabled(currentView != ViewAliases.CITY_VIEW or NewYearNavigation.getCurrentObject() != CustomizationObjects.FIR)

    def __onSwitchView(self, _):
        with self.__model.transaction() as tx:
            self.__updateActiveState(tx)
        if not self.__model.getIsVisible():
            self.__tryToDestroyWidgetTooltip()

    def __tryToDestroyWidgetTooltip(self):
        tooltipIDs = (R.views.new_year.lobby.new_year.tooltips.NyMainWidgetTooltip(), R.views.new_year.lobby.new_year.tooltips.NyTotalBonusTooltip())
        for tooltipID in tooltipIDs:
            tooltipView = self.__gui.windowsManager.getViewByLayoutID(tooltipID)
            if tooltipView:
                tooltipView.destroyWindow()

    def __getBonusValue(self):
        return self.__nyController.getActiveSettingBonusValue() * PERCENT + self.__dataProvider.getDeb()
