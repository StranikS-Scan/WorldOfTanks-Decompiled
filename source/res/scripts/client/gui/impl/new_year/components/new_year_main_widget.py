# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/components/new_year_main_widget.py
from account_helpers.settings_core.settings_constants import GRAPHICS
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_main_widget_anim_types import NewYearMainWidgetAnimTypes
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_main_widget_model import NewYearMainWidgetModel
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates
from gui.impl.new_year.sound_rtpc_controller import SoundRTPCController
from gui.impl.pub import ViewImpl
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.tooltips.new_year_widget_tooltip import NewYearWidgetTooltip
from gui.shared import g_eventBus
from gui.shared.events import GameEvent
from helpers import dependency, getLanguageCode, int2roman
from new_year.ny_constants import CustomizationObjects, SyncDataKeys
from new_year.ny_level_helper import NewYearAtmospherePresenter
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.new_year import ICustomizableObjectsManager, INewYearController
from skeletons.gui.shared import IItemsCache
_EXTENDED_RENDER_PIPELINE = 0

class NewYearMainWidgetInject(InjectComponentAdaptor):

    def _makeInjectView(self):
        return NewYearMainWidget()


class NewYearMainWidget(ViewImpl):
    __slots__ = ('__soundManager', '_lobbyMode', '__level', '__soundRTPCController', '__maxLevel')
    _nyController = dependency.descriptor(INewYearController)
    _COManager = dependency.descriptor(ICustomizableObjectsManager)
    _itemsCache = dependency.descriptor(IItemsCache)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.components.new_year_main_widget.NewYearMainWidget())
        settings.flags = ViewFlags.COMPONENT
        settings.model = NewYearMainWidgetModel()
        super(NewYearMainWidget, self).__init__(settings)
        self.__soundManager = NewYearSoundsManager({NewYearSoundConfigKeys.STATE_VALUE: NewYearSoundStates.HANGAR})
        self._lobbyMode = True
        self.__level = NewYearAtmospherePresenter.getLevel()
        self.__maxLevel = self._itemsCache.items.festivity.getMaxLevel()
        self.__soundRTPCController = None
        return

    @property
    def viewModel(self):
        return super(NewYearMainWidget, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return NewYearWidgetTooltip() if event.contentID == R.views.lobby.new_year.tooltips.new_year_widget_tooltip.NewYearWidgetTooltip() else None

    def _initialize(self):
        super(NewYearMainWidget, self)._initialize()
        self.viewModel.onWidgetClick += self.__onWidgetClick
        self._nyController.onDataUpdated += self.__onDataUpdated
        g_eventBus.addListener(GameEvent.IMAGE_VIEW_DONE, self.__onImageViewDone)
        NewYearNavigation.onObjectStateChanged += self.__onObjectStateChanged
        self.__soundManager.onEnterView()
        self.__soundRTPCController = SoundRTPCController()
        self.__soundRTPCController.init(NewYearNavigation.getCurrentObject())
        self.__soundRTPCController.setLevelAtmosphere(self._itemsCache.items.festivity.getMaxLevel())
        with self.viewModel.transaction() as model:
            self.__updateData(model)
            self.__updateLevel(model)
            model.setIsExtendedAnim(self.settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE) == _EXTENDED_RENDER_PIPELINE)

    def _finalize(self):
        if NewYearNavigation.getCurrentObject():
            self.__soundManager.onExitView()
        self.__soundRTPCController.fini()
        self.__soundRTPCController = None
        self.__soundManager.clear()
        self.viewModel.onWidgetClick -= self.__onWidgetClick
        self._nyController.onDataUpdated -= self.__onDataUpdated
        g_eventBus.removeListener(GameEvent.IMAGE_VIEW_DONE, self.__onImageViewDone)
        NewYearNavigation.onObjectStateChanged -= self.__onObjectStateChanged
        super(NewYearMainWidget, self)._finalize()
        return

    def __onImageViewDone(self, _):
        self.__soundManager.setEnterViewState()

    def __onWidgetClick(self, *args):
        if self._lobbyMode:
            NewYearNavigation.showMainView(CustomizationObjects.FIR)
            self.__soundManager.playEvent(NewYearSoundEvents.ENTER_CUSTOME)

    def __onDataUpdated(self, keys):
        if SyncDataKeys.SLOTS in keys:
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
                animationType = NewYearMainWidgetAnimTypes.ANIM_TYPE_DOWN
            self.__level = level
            self.__onLevelChanged()
        maxLevel = self._itemsCache.items.festivity.getMaxLevel()
        if maxLevel != self.__maxLevel:
            self.__maxLevel = maxLevel
            animationType = NewYearMainWidgetAnimTypes.ANIM_TYPE_UP_LONG
        model.setAnimationType(animationType)
        model.setLevel(self.__level)
        model.setLevelRoman(int2roman(self.__maxLevel))

    def __updateData(self, model):
        model.setLobbyMode(self._lobbyMode)
        model.setUserLanguage(str(getLanguageCode()).upper())

    def __onObjectStateChanged(self):
        currentObject = NewYearNavigation.getCurrentObject()
        self._lobbyMode = currentObject is None
        with self.viewModel.transaction() as model:
            self.__updateData(model)
            self.__updateLevel(model)
        self.__soundRTPCController.setCurrentLocation(currentObject)
        if currentObject is None:
            self.__soundManager.onEnterView()
        return

    def __onLevelChanged(self):
        self.__soundRTPCController.setLevelAtmosphere(self._itemsCache.items.festivity.getMaxLevel())
