# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/status_notifications/panel.py
import logging
import BigWorld
from helpers import dependency
import BattleReplay
from ReplayEvents import g_replayEvents
from gui.Scaleform.daapi.view.battle.shared.status_notifications import components
from gui.Scaleform.daapi.view.battle.shared.status_notifications import replay_components
from gui.Scaleform.daapi.view.meta.StatusNotificationsPanelMeta import StatusNotificationsPanelMeta
from gui.battle_control import event_dispatcher as gui_event_dispatcher
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID
from gui.shared.items_parameters import isAutoReloadGun
from gui.shared.utils.MethodsRules import MethodsRules
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class StatusNotificationTimerPanel(StatusNotificationsPanelMeta, MethodsRules):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _DEFAULT_Y_SHIFT = 114
    _VERTICAL_SHIFT_WITH_AUTOLOADER_IN_SNIPER_MODE = _DEFAULT_Y_SHIFT + 42

    def __init__(self):
        super(StatusNotificationTimerPanel, self).__init__()
        self._viewID = None
        self.__container = None
        self.__vehicleID = None
        return

    def _populate(self):
        super(StatusNotificationTimerPanel, self)._populate()
        containerClass = self._getComponentClass()
        snItems = self._generateItems()
        self.__container = containerClass(snItems, self.__onCollectionUpdated)
        self._addListeners()
        self.as_setInitDataS({'settings': self._generateNotificationTimerSettings()})

    def _addListeners(self):
        g_replayEvents.onPause += self.__onReplayPaused
        crosshairCtrl = self._sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
            self._viewID = crosshairCtrl.getViewID()
        ctrl = self._sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling += self._onVehicleControlling
            vehicle = ctrl.getControllingVehicle()
            if vehicle is not None:
                self._onVehicleControlling(vehicle)
        return

    def _removeListeners(self):
        g_replayEvents.onPause -= self.__onReplayPaused
        crosshairCtrl = self._sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
        ctrl = self._sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling -= self._onVehicleControlling
        return

    def _dispose(self):
        self.clear()
        self.__container.destroy()
        self.__container = None
        if BattleReplay.isPlaying():
            self.__onCollectionUpdated([])
        self._removeListeners()
        super(StatusNotificationTimerPanel, self)._dispose()
        return

    def _getComponentClass(self):
        return replay_components.ReplayStatusNotificationContainer if self._sessionProvider.isReplayPlaying else components.StatusNotificationContainer

    def _generateItems(self):
        return []

    def _generateNotificationTimerSettings(self):
        return []

    def _calcVerticalOffset(self, vehicle):
        verticalOffset = self._DEFAULT_Y_SHIFT
        vTypeDescr = vehicle.typeDescriptor
        hasAutoloaderInterface = vTypeDescr.isDualgunVehicle or isAutoReloadGun(vTypeDescr.gun)
        if self._viewID is CROSSHAIR_VIEW_ID.SNIPER and hasAutoloaderInterface:
            verticalOffset = self._VERTICAL_SHIFT_WITH_AUTOLOADER_IN_SNIPER_MODE
        return verticalOffset

    def _addNotificationTimerSetting(self, data, typeId, iconName, linkage, color='', noiseVisible=False, text='', countdownVisible=True, iconOffsetY=0, iconSmallName='', isReversedTimerDirection=False, canBlink=False, descriptionFontSize=14, descriptionOffsetY=0):
        data.append({'typeId': typeId,
         'iconName': iconName,
         'iconSmallName': iconSmallName,
         'linkage': linkage,
         'color': color,
         'noiseVisible': noiseVisible,
         'text': text,
         'countdownVisible': countdownVisible,
         'iconOffsetY': iconOffsetY,
         'isReversedTimerDirection': isReversedTimerDirection,
         'canBlink': canBlink,
         'descriptionFontSize': descriptionFontSize,
         'descriptionOffsetY': descriptionOffsetY})

    def _updatePanelPosition(self):
        vehicle = BigWorld.entity(self.__vehicleID) if self.__vehicleID is not None else None
        if vehicle is None or vehicle.typeDescriptor is None:
            self.__setVerticalOffset(self._DEFAULT_Y_SHIFT)
            return
        else:
            verticalOffset = self._calcVerticalOffset(vehicle=vehicle)
            self.__setVerticalOffset(verticalOffset)
            return

    def __onReplayPaused(self, isPaused):
        self.as_setSpeedS(BattleReplay.g_replayCtrl.playbackSpeed)

    def __onCollectionUpdated(self, vOs):
        self.__logDataCollection(vOs)
        self.as_setDataS(vOs)
        gui_event_dispatcher.destroyTimersPanelShown(shown=len(vOs) > 0)

    @MethodsRules.delayable()
    def _onVehicleControlling(self, vehicle):
        self._sessionProvider.updateVehicleEffects(vehicle)
        self.__vehicleID = vehicle.id
        self._updatePanelPosition()

    @MethodsRules.delayable('_onVehicleControlling')
    def __onCrosshairViewChanged(self, viewID):
        self._viewID = viewID
        self._updatePanelPosition()

    def __setVerticalOffset(self, verticalOffset):
        self.as_setVerticalOffsetS(verticalOffset)

    @classmethod
    def __logDataCollection(cls, vOs):
        lgr = _logger.debug
        lgr('Status Notifications data:')
        if not vOs:
            lgr('\n   []')
        else:
            for i, vO in enumerate(vOs):
                lgr('\n   %s: %r', i, vO)
