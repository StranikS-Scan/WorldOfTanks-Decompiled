# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/components/new_year_entry_widget.py
from frameworks.wulf import ViewFlags
from gui.Scaleform.framework.entities.ub_component_adaptor import UnboundComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.new_year.components.new_year_entry_widget_model import NewYearEntryWidgetModel
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates, NewYearSoundVars
from gui.impl.pub import ViewImpl
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.tooltips.new_year_bonus_tooltip import NewYearBonusTooltip
from gui.shared import g_eventBus
from gui.shared.events import GameEvent
from CurrentVehicle import g_currentVehicle
from helpers import dependency
from new_year.ny_constants import CustomizationObjects, SyncDataKeys
from items.components.ny_constants import ToySettings
from new_year.ny_level_helper import NewYearAtmospherePresenter
from skeletons.new_year import ICustomizableObjectsManager, INewYearController

class NewYearEntryWidgetInject(UnboundComponentAdaptor):

    def _makeUnboundView(self):
        return NewYearEntryWidget()


class NewYearEntryWidget(ViewImpl):
    __slots__ = ('__soundManager',)
    _nyController = dependency.descriptor(INewYearController)
    _COManager = dependency.descriptor(ICustomizableObjectsManager)

    def __init__(self):
        super(NewYearEntryWidget, self).__init__(R.views.newYearEntryWidget, ViewFlags.COMPONENT, NewYearEntryWidgetModel)
        self.__soundManager = NewYearSoundsManager({NewYearSoundConfigKeys.ENTRANCE_EVENT: NewYearSoundEvents.MAIN,
         NewYearSoundConfigKeys.EXIT_EVENT: NewYearSoundEvents.MAIN_EXIT,
         NewYearSoundConfigKeys.STATE_VALUE: NewYearSoundStates.HANGAR})

    @property
    def viewModel(self):
        return super(NewYearEntryWidget, self).getViewModel()

    def _initialize(self):
        super(NewYearEntryWidget, self)._initialize()
        self.viewModel.onWidgetClick += self.__onWidgetClick
        g_currentVehicle.onChanged += self.__updateTankName
        self._nyController.onDataUpdated += self.__onDataUpdated
        g_eventBus.addListener(GameEvent.IMAGE_VIEW_DONE, self.__onImageViewDone)
        self.__updateData()
        self.__soundManager.onEnterView()
        self.__soundManager.setRTPC(NewYearSoundVars.RTPC_LEVEL_ATMOSPHERE, NewYearAtmospherePresenter.getLevel())
        hangedToys = self._nyController.getToysInSlots()
        maxStyle = max(ToySettings.NEW, key=lambda setting: len([ t for t in hangedToys if t is not None and t.setting == setting ]))
        self.__soundManager.setStylesState(maxStyle)

    def _finalize(self):
        if NewYearNavigation.getCurrentObject():
            self.__soundManager.onExitView()
        self.__soundManager.clear()
        self.viewModel.onWidgetClick -= self.__onWidgetClick
        g_currentVehicle.onChanged -= self.__updateTankName
        self._nyController.onDataUpdated -= self.__onDataUpdated
        g_eventBus.removeListener(GameEvent.IMAGE_VIEW_DONE, self.__onImageViewDone)
        super(NewYearEntryWidget, self)._finalize()

    def __onImageViewDone(self, _):
        self.__soundManager.setEnterViewState()

    def __onWidgetClick(self, *args):
        NewYearNavigation.switchByObjectName(CustomizationObjects.FIR)
        self.__soundManager.playEvent(NewYearSoundEvents.ENTER_CUSTOME)

    def __onDataUpdated(self, keys):
        if SyncDataKeys.SLOTS in keys:
            self.__updateData()

    def __updateData(self):
        with self.viewModel.transaction() as tx:
            defaultIcon, smallIcon = self.__getLevelIcons()
            tx.setLevelIconDefaultSrc(defaultIcon)
            tx.setLevelIconSmallSrc(smallIcon)
            self.__updateTankName()

    def __updateTankName(self):
        self.viewModel.setTankName(g_currentVehicle.item.shortUserName)

    def __getLevelIcons(self):
        lvl = NewYearAtmospherePresenter.getLevel()
        return (R.images.gui.maps.icons.new_year.widget.levels.c_96x96.dyn('level{}'.format(lvl)), R.images.gui.maps.icons.new_year.widget.levels.c_80x80.dyn('level{}'.format(lvl)))

    def createToolTipContent(self, event, contentID):
        return NewYearBonusTooltip() if event.contentID == R.views.newYearBonusTooltip else None
