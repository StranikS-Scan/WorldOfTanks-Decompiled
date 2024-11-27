# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/widgets/ny_widget_handler.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_ACTIVE_WIDGET_TRANSITION_SHOWN
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.ny_constants import ViewAliases
from new_year.gui.impl.new_year.new_year_helper import IS_ROMAN_NUMBERS_ALLOWED
from new_year.gui.shared.events import NewYearEvent
from new_year.gui.shared.ny_bonuses import BonusHelper
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter
from new_year.ny_constants import CustomizationObjects
from new_year.skeletons.new_year import INewYearController
from new_year.gui.impl.gen.view_models.common.ny_event_state_model import EventState
from Event import Event
from gui.impl.gen import R
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.new_year_main_widget_anim_types import NewYearMainWidgetAnimTypes
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from helpers import dependency, getLanguageCode, int2roman
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from skeletons.account_helpers.settings_core import ISettingsCore
if typing.TYPE_CHECKING:
    from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.new_year_main_widget_model import NewYearMainWidgetModel

class NyWidgetHandler(object):
    _itemsCache = dependency.descriptor(IItemsCache)
    __gui = dependency.descriptor(IGuiLoader)
    __nyController = dependency.descriptor(INewYearController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, model):
        self.__model = model
        self.__level = NewYearAtmospherePresenter.getLevel()
        self.__prevAtmPoints = 0
        self.__maxLevel = self._itemsCache.items.festivity.getMaxLevel()
        self.lobbyMode = True
        self.onLevelChanged = Event()

    def initialize(self):
        NewYearNavigation.onObjectStateChanged += self.__onObjectStateChanged
        self.__nyController.onStateChanged += self.__onObjectStateChanged
        g_eventBus.addListener(NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchView, EVENT_BUS_SCOPE.LOBBY)
        currentObject = NewYearNavigation.getCurrentObject()
        self.lobbyMode = currentObject is None
        with self.__model.transaction() as tx:
            self.__updateData(tx)
            self.__updateLevel(tx)
            self.__updateActiveState(tx)
            tx.setIsExtendedAnim(True)
        return

    def setNeedToShowTransition(self):
        if self.__checkIfNeedToShowWidgetTransition():
            AccountSettings.setNewYear(NY_ACTIVE_WIDGET_TRANSITION_SHOWN, True)

    def __checkIfNeedToShowWidgetTransition(self):
        activeWidgetTransitionShown = AccountSettings.getNewYear(NY_ACTIVE_WIDGET_TRANSITION_SHOWN)
        isFirstEntrance = not self.__nyController.isOnboardingFinished()
        return not activeWidgetTransitionShown and not isFirstEntrance

    def finalize(self):
        NewYearNavigation.onObjectStateChanged -= self.__onObjectStateChanged
        self.__nyController.onStateChanged -= self.__onObjectStateChanged
        g_eventBus.removeListener(NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchView, scope=EVENT_BUS_SCOPE.LOBBY)

    def update(self):
        with self.__model.transaction() as tx:
            self.__updateData(tx)
            self.__updateLevel(tx)

    def __updateData(self, model):
        model.setLobbyMode(self.lobbyMode)
        model.setUserLanguage(str(getLanguageCode()).upper())
        model.setBonusValue(BonusHelper.getCommonBonusInPercents())
        model.setIsRomanNumbersAllowed(IS_ROMAN_NUMBERS_ALLOWED)
        model.setIsEnabled(NewYearNavigation.getCurrentObject() != CustomizationObjects.FIR)
        model.setIsFirstEntrance(not self.__nyController.isOnboardingFinished())
        model.eventState.setValue(EventState.PAUSED if self.__nyController.isSuspended() else EventState.ACTIVE)
        model.setIsActiveWidgetTransitionShown(AccountSettings.getNewYear(NY_ACTIVE_WIDGET_TRANSITION_SHOWN))

    def __updateLevel(self, model):
        animationType = NewYearMainWidgetAnimTypes.ANIM_TYPE_NONE
        level = NewYearAtmospherePresenter.getLevel()
        if level != self.__level:
            if level > self.__level:
                animationType = NewYearMainWidgetAnimTypes.ANIM_TYPE_UP
            else:
                animationType = NewYearMainWidgetAnimTypes.ANIM_TYPE_DOWN_LONG
            self.__level = level
            self.onLevelChanged()
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

    def __onObjectStateChanged(self):
        currentObject = NewYearNavigation.getCurrentObject()
        self.lobbyMode = currentObject is None
        with self.__model.transaction() as tx:
            self.__updateData(tx)
            self.__updateLevel(tx)
            self.__updateActiveState(tx)
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
