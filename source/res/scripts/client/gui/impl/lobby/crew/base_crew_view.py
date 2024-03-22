# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/base_crew_view.py
from typing import TYPE_CHECKING, Optional
from AccountCommands import LOCK_REASON
from PlayerEvents import g_playerEvents
from crew_sounds import CREW_SOUND_SPACE, CREW_SOUND_OVERLAY_SPACE
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.base_crew_view_model import BaseCrewViewModel
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showPersonalCase, showChangeCrewMember
from gui.shared.gui_items.Tankman import NO_TANKMAN, NO_SLOT
from gui.shared.gui_items.Vehicle import NO_VEHICLE_ID
from uilogging.crew.loggers import CrewBringToFrontViewLogger
from uilogging.crew.logging_constants import CrewNavigationButtons, LAYOUT_ID_TO_ITEM
if TYPE_CHECKING:
    from gui.impl.lobby.crew.widget.crew_widget import CrewWidget
IS_FROM_ESCAPE_PARAM = 'isFromEscape'

class BaseCrewSoundView(ViewImpl):
    __slots__ = ()
    _COMMON_SOUND_SPACE = CREW_SOUND_SPACE


class BaseCrewSubView(BaseCrewSoundView):
    __slots__ = ()
    _COMMON_SOUND_SPACE = CREW_SOUND_OVERLAY_SPACE


class BaseCrewView(BaseCrewSoundView, LobbyHeaderVisibility, IGlobalListener):
    __slots__ = ('_isHangar', '_crewWidget', '_currentViewID', '_currentViewKey', '_previousViewID', '_uiLogger')

    def __init__(self, settings, parentViewKey=None):
        self._isHangar = bool(self.gui.windowsManager.findWindows(lambda window: getattr(window.content, 'alias', None) == VIEW_ALIAS.LOBBY_HANGAR))
        self._crewWidget = None
        self._currentViewID = settings.kwargs.get('currentViewID', settings.layoutID)
        self._previousViewID = settings.kwargs.get('previousViewID')
        self._currentViewKey = None
        self._uiLogger = CrewBringToFrontViewLogger(self, settings.layoutID, parentViewKey if parentViewKey else LAYOUT_ID_TO_ITEM.get(settings.kwargs.get('previousViewID')))
        super(BaseCrewView, self).__init__(settings)
        return

    def onBringToFront(self, otherWindow):
        self._uiLogger.onBringToFront(otherWindow)

    @property
    def isPersonalFileOpened(self):
        return self.gui.windowsManager.getViewByLayoutID(R.views.lobby.crew.TankmanContainerView()) is not None

    @property
    def crewWidget(self):
        return self._crewWidget

    def bringToFront(self):
        parentWindow = self.getParentWindow()
        parentLayer = parentWindow.layer
        if not parentWindow.isFocused:
            parentWindow.tryFocus()
        windowsOnCurrentLayer = self.gui.windowsManager.findWindows(lambda w: w.layer == parentLayer and isinstance(w.content, BaseCrewView))
        for window in windowsOnCurrentLayer:
            window.content.onBringToFront(parentWindow)

    @property
    def viewModel(self):
        return super(BaseCrewView, self).getViewModel()

    def widgetAutoSelectSlot(self, **kwargs):
        slotIDX = kwargs.get('slotIDX', NO_SLOT)
        tankman = kwargs.get('tankman')
        tankmanID = tankman.invID if tankman else NO_TANKMAN
        tankmanID, slotIDX = self._findWidgetSlotNextIdx(tankmanID, slotIDX)
        self._crewWidget.updateSlotIdx(slotIDX)
        if slotIDX == NO_SLOT:
            self._onEmptySlotAutoSelect(slotIDX)
            return
        self._onTankmanSlotAutoSelect(tankmanID, slotIDX)

    def _findWidgetSlotNextIdx(self, tankmanID, slotIDX):
        if tankmanID != NO_TANKMAN and slotIDX == NO_SLOT:
            slotIDX, _ = self._currentSlotAndTankman(tankmanID)
        return self._getAutoSelectWidget(tankmanID, slotIDX)

    def _currentSlotAndTankman(self, tankmanID):
        crew = self._getCrewBySlotIDX(NO_SLOT)
        for index, tankman in enumerate(crew):
            if tankman[1] and tankman[1].invID == tankmanID:
                return (index, tankman[1])

        return (NO_SLOT, None)

    def _subscribe(self):
        super(BaseCrewView, self)._subscribe()
        self.startGlobalListening()

    def _unsubscribe(self):
        super(BaseCrewView, self)._unsubscribe()
        self.stopGlobalListening()

    def _finalize(self):
        super(BaseCrewView, self)._finalize()
        self.resumeLobbyHeader(self.uniqueID)
        self._crewWidget = None
        self._uiLogger.finalize()
        return

    def _setWidgets(self, **kwargs):
        self._setCrewWidget(**kwargs)

    def _onLoading(self, *args, **kwargs):
        self._setWidgets(**kwargs)
        self._uiLogger.initialize()
        super(BaseCrewView, self)._onLoading()
        self._updateViewModel()

    def _setCrewWidget(self, **kwargs):
        from gui.impl.lobby.crew.widget.crew_widget import CrewWidget
        tankmanInvID = kwargs.get('tankmanInvID', NO_TANKMAN)
        vehicleInvID = kwargs.get('vehicleInvID', NO_VEHICLE_ID)
        slotIdx = kwargs.get('slotIdx', NO_SLOT)
        previousViewID = kwargs.get('previousViewID', None)
        self._crewWidget = CrewWidget(tankmanInvID, vehicleInvID, slotIdx, self._currentViewID, previousViewID, self._isHangar)
        if slotIdx == NO_SLOT:
            slotIdx, _, __ = self._crewWidget.getWidgetData()
        self.setChildView(CrewWidget.LAYOUT_DYN_ACCESSOR(), self._crewWidget)
        self._crewWidget.updateSlotIdx(slotIdx)
        return

    def _updateViewModel(self):
        with self.viewModel.transaction() as vm:
            self._fillViewModel(vm)

    def _fillViewModel(self, vm):
        vm.setIsButtonBarVisible(self._isHangar)
        self._setBackButtonLabel(vm)

    def _setBackButtonLabel(self, vm):
        vm.setBackButtonLabel(R.strings.crew.common.navigation.toPersonalFile())

    def _onLoaded(self, *args, **kwargs):
        self.suspendLobbyHeader(self.uniqueID)
        super(BaseCrewView, self)._onLoaded(*args, **kwargs)

    def _getEvents(self):
        eventsTuple = super(BaseCrewView, self)._getEvents()
        return eventsTuple + ((self.viewModel.onClose, self._onClose),
         (self.viewModel.onBack, self._onBack),
         (self.viewModel.onHangar, self._onHangar),
         (self.viewModel.onAbout, self._onAbout),
         (self._crewWidget.onSlotClick, self._onWidgetSlotClick),
         (self._crewWidget.onChangeCrewClick, self._onWidgetChangeCrewClick),
         (self._crewWidget.onSlotTrySelect, self.widgetAutoSelectSlot),
         (g_playerEvents.onVehicleLockChanged, self._onVehicleLockChanged))

    def _getCrewTankmanIndex(self, slotIDX, crew):
        for index, slot in enumerate(crew):
            if slot and slot[0] == slotIDX:
                return index

        return NO_SLOT

    def _getCrewBySlotIDX(self, slotIDX):
        _, vehicle, __ = self.crewWidget.getWidgetData()
        if not vehicle:
            return []
        else:
            crew = vehicle.crew
            index = self._getCrewTankmanIndex(slotIDX, crew)
            return crew[index::] + crew[:index:] if index != NO_SLOT else crew

    def _getAutoSelectWidget(self, tankmanID, slotIDX):
        crew = self._getCrewBySlotIDX(slotIDX)
        for index, tankman in crew:
            if tankman and not tankman.isDismissed:
                return (tankman.invID, index)

        _, __, tankman = self._crewWidget.getWidgetData()
        if crew or tankmanID == NO_TANKMAN or tankman and tankman.isDismissed:
            slotIDX = NO_SLOT
        return (tankmanID, slotIDX)

    def _onTankmanSlotAutoSelect(self, tankmanInvID, slotIdx):
        pass

    def _destroySubViews(self):
        windows = self.gui.windowsManager.findWindows(lambda w: w.layer == WindowLayer.TOP_SUB_VIEW)
        for window in windows:
            window.destroy()

    @property
    def _backButtonLogingKey(self):
        return CrewNavigationButtons.TO_PERSONAL_FILE

    def _onWidgetSlotClick(self, tankmanInvID, slotIdx):
        if tankmanInvID == NO_TANKMAN:
            self._onEmptySlotClick(tankmanInvID, slotIdx)
        else:
            self._onTankmanSlotClick(tankmanInvID, slotIdx)

    def _logClose(self, params=None):
        if isinstance(params, dict) and params.get(IS_FROM_ESCAPE_PARAM, False):
            self._uiLogger.logNavigationButtonClick(CrewNavigationButtons.ESC)
        else:
            self._uiLogger.logNavigationButtonClick(CrewNavigationButtons.CLOSE)

    def _onClose(self, params=None):
        self._logClose(params)
        self.destroyWindow()

    def _onBack(self, logClick=True):
        if logClick:
            self._uiLogger.logNavigationButtonClick(self._backButtonLogingKey)
        slotIDX, _, tankman = self._crewWidget.getWidgetData()
        if tankman:
            tankmanID = tankman.invID
        else:
            tankmanID, _ = self._findWidgetSlotNextIdx(NO_TANKMAN, slotIDX)
        if tankmanID == NO_TANKMAN and self.crew:
            tankmanID = next((item[1].invID for item in self.crew if item and item[1]), NO_TANKMAN)
        self.destroyWindow()
        showPersonalCase(tankmanID, previousViewID=self._currentViewID)

    def _onHangar(self):
        self._uiLogger.logNavigationButtonClick(CrewNavigationButtons.TO_GARAGE)
        if self._isHangar:
            self._destroySubViews()
        else:
            event_dispatcher.showHangar()

    @staticmethod
    def _onAbout():
        event_dispatcher.showCrewAboutView()

    def _onTankmanSlotClick(self, tankmanInvID, _):
        showPersonalCase(tankmanInvID, previousViewID=self._currentViewID)

    def _onEmptySlotClick(self, tankmanID, slotIdx):
        pass

    def _onWidgetChangeCrewClick(self, vehicleInvID, slotIdx, currentViewID):
        showChangeCrewMember(slotIdx, vehicleInvID, currentViewID)

    def _onEmptySlotAutoSelect(self, slotIDX):
        self.destroyWindow()

    def onPrbEntitySwitched(self):
        self.destroyWindow()

    def _onVehicleLockChanged(self, vehInvID, lockReason):
        if lockReason[0] in (LOCK_REASON.PREBATTLE, LOCK_REASON.UNIT):
            self._destroySubViews()
