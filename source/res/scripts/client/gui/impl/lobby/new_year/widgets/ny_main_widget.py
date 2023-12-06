# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/widgets/ny_main_widget.py
from ClientSelectableCameraObject import ClientSelectableCameraObject
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_main_widget_anim_types import NewYearMainWidgetAnimTypes
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_main_widget_model import NewYearMainWidgetModel
from gui.impl.new_year.new_year_helper import IS_ROMAN_NUMBERS_ALLOWED
from gui.impl.new_year.sounds import NewYearSoundsManager
from gui.impl.new_year.sound_rtpc_controller import SoundRTPCController
from gui.impl.pub import ViewImpl
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from gui.impl.lobby.new_year.tooltips.ny_main_widget_tooltip import NyMainWidgetTooltip
from gui.impl.lobby.new_year.tooltips.ny_total_bonus_tooltip import NyTotalBonusTooltip
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import NewYearEvent
from helpers import dependency, getLanguageCode, int2roman
from new_year.ny_bonuses import BonusHelper
from new_year.ny_constants import CustomizationObjects, SyncDataKeys
from new_year.ny_level_helper import NewYearAtmospherePresenter
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.impl import IGuiLoader
from skeletons.new_year import INewYearController
from skeletons.gui.shared import IItemsCache
_EXTENDED_RENDER_PIPELINE = 0

class NyMainWidgetInject(InjectComponentAdaptor):

    def _makeInjectView(self):
        return NyMainWidget()


class NyMainWidget(ViewImpl):
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)
    settingsCore = dependency.descriptor(ISettingsCore)
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.components.ny_main_widget.NewYearMainWidget())
        settings.flags = ViewFlags.VIEW
        settings.model = NewYearMainWidgetModel()
        super(NyMainWidget, self).__init__(settings)
        self._lobbyMode = True
        self.__level = NewYearAtmospherePresenter.getLevel()
        self.__maxLevel = self._itemsCache.items.festivity.getMaxLevel()
        self.__prevAtmPoints = 0
        self.__soundManager = NewYearSoundsManager({})
        self.__soundRTPCController = None
        return

    @property
    def viewModel(self):
        return super(NyMainWidget, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.new_year.tooltips.NyMainWidgetTooltip():
            return NyMainWidgetTooltip()
        else:
            return NyTotalBonusTooltip() if event.contentID == R.views.lobby.new_year.tooltips.NyTotalBonusTooltip() else None

    def _initialize(self):
        super(NyMainWidget, self)._initialize()
        self.viewModel.onClick += self.__onWidgetClick
        self._nyController.onDataUpdated += self.__onDataUpdated
        g_eventBus.addListener(NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchView, EVENT_BUS_SCOPE.LOBBY)
        NewYearNavigation.onObjectStateChanged += self.__onObjectStateChanged
        currentObject = NewYearNavigation.getCurrentObject()
        self._lobbyMode = currentObject is None
        self.__soundRTPCController = SoundRTPCController()
        self.__soundRTPCController.init(currentObject)
        self.__soundRTPCController.setLevelAtmosphere(self._itemsCache.items.festivity.getMaxLevel())
        with self.viewModel.transaction() as model:
            self.__updateData(model)
            self.__updateLevel(model)
            self.__updateActiveState(model)
            model.setIsExtendedAnim(True)
        self.viewModel.setIsInited(True)
        return

    def _finalize(self):
        if self.__soundRTPCController is not None:
            self.__soundRTPCController.fini()
            self.__soundRTPCController = None
        self.__soundManager.clear()
        self.viewModel.onClick -= self.__onWidgetClick
        self._nyController.onDataUpdated -= self.__onDataUpdated
        g_eventBus.removeListener(NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchView, scope=EVENT_BUS_SCOPE.LOBBY)
        NewYearNavigation.onObjectStateChanged -= self.__onObjectStateChanged
        super(NyMainWidget, self)._finalize()
        return

    def getLobbyMode(self, *_):
        return self._lobbyMode

    def __onWidgetClick(self, *_):
        ClientSelectableCameraObject.deselectAll()
        NewYearNavigation.switchTo(CustomizationObjects.FIR, True, withFade=True)

    def __onDataUpdated(self, keys):
        if SyncDataKeys.POINTS in keys:
            with self.viewModel.transaction() as model:
                self.__updateData(model)
                self.__updateLevel(model)

    def __updateLevel(self, model):
        animationType = NewYearMainWidgetAnimTypes.ANIM_TYPE_NONE
        level = NewYearAtmospherePresenter.getLevel()
        if level != self.__level:
            if level > self.__level:
                animationType = NewYearMainWidgetAnimTypes.ANIM_TYPE_UP
            else:
                animationType = NewYearMainWidgetAnimTypes.ANIM_TYPE_DOWN_LONG
            self.__level = level
            self.__onLevelChanged()
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

    def __updateData(self, model):
        model.setLobbyMode(self._lobbyMode)
        model.setUserLanguage(str(getLanguageCode()).upper())
        model.setBonusValue(BonusHelper.getCommonBonusInPercents())
        model.setIsRomanNumbersAllowed(IS_ROMAN_NUMBERS_ALLOWED)
        model.setIsEnabled(NewYearNavigation.getCurrentObject() != CustomizationObjects.FIR)

    @staticmethod
    def __updateActiveState(model):
        currentView = NewYearNavigation.getCurrentViewName()
        model.setIsEnabled(currentView != ViewAliases.GLADE_VIEW or NewYearNavigation.getCurrentObject() != CustomizationObjects.FIR)

    def __onObjectStateChanged(self):
        currentObject = NewYearNavigation.getCurrentObject()
        self._lobbyMode = currentObject is None
        with self.viewModel.transaction() as model:
            self.__updateData(model)
            self.__updateLevel(model)
            self.__updateActiveState(model)
        self.__soundRTPCController.setCurrentLocation(currentObject)
        return

    def __onSwitchView(self, _):
        with self.viewModel.transaction() as tx:
            self.__updateActiveState(tx)
        if not self.viewModel.getIsVisible():
            self.__tryToDestroyWidgetTooltip()

    def __tryToDestroyWidgetTooltip(self):
        tooltipIDs = (R.views.lobby.new_year.tooltips.NyMainWidgetTooltip(), R.views.lobby.new_year.tooltips.NyTotalBonusTooltip())
        for tooltipID in tooltipIDs:
            tooltipView = self.__gui.windowsManager.getViewByLayoutID(tooltipID)
            if tooltipView:
                tooltipView.destroyWindow()

    def __onLevelChanged(self):
        self.__soundRTPCController.setLevelAtmosphere(self._itemsCache.items.festivity.getMaxLevel())
