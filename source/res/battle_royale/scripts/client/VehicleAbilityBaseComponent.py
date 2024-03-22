# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleAbilityBaseComponent.py
import BigWorld
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from Event import EventsSubscriber

class VehicleAbilityBaseComponent(BigWorld.DynamicScriptComponent):

    def __init__(self, timerViewID=None, markerID=None):
        super(VehicleAbilityBaseComponent, self).__init__()
        self._guiSessionProvider = self.entity.guiSessionProvider
        self._guiFeedback = self.entity.guiSessionProvider.shared.feedback
        self._finishTime = self.finishTime
        self._timerViewID = timerViewID
        self._markerID = markerID
        self._es = EventsSubscriber()
        self.__postponedCalls = []
        self.__isSwitching = False
        self._avatar = BigWorld.player()
        self._subscribeOnEvents()
        self._updateVisuals()

    def set_finishTime(self, _=None):
        self._finishTime = self.finishTime
        self._updateVisuals()

    def onDestroy(self):
        self._destroy()

    def onLeaveWorld(self, *args):
        self._destroy()

    def getInfo(self):
        return {}

    def _onAvatarReady(self):
        pass

    def _subscribeOnEvents(self):
        self._es.subscribeToEvent(self._guiSessionProvider.onUpdateObservedVehicleData, self._onUpdateObservedVehicleData)
        self._es.subscribeToEvent(self.entity.onAppearanceReady, self._onAppearanceReady)
        if self._avatar is not None and self._avatar.inputHandler is not None:
            self._es.subscribeToEvent(self._avatar.inputHandler.onCameraChanged, self.__onCameraChanged)
            self._es.subscribeToEvent(self._avatar.onSwitchingViewPoint, self.__onSwitchingViewPoint)
        return

    def _unSubscribeFromAllEvents(self):
        self._es.unsubscribeFromAllEvents()

    def _destroy(self):
        self._unSubscribeFromAllEvents()
        self.__isSwitching = False
        self._updateVisuals(isShow=False)
        self.__postponedCalls = []
        self._avatar = None
        return

    def _updateVisuals(self, isShow=True):
        self._updateTimer(self._getTimerData(isShow))
        self._updateMarker(self._getMarkerData(isShow), isHide=not isShow)

    def _updateTimer(self, data):
        if self._timerViewID is None:
            return
        else:
            if self.__isSwitching:
                self.__pushToPostponeCall(self._updateTimer, (data,))
            elif self._canUpdateTimer():
                self._guiSessionProvider.invalidateVehicleState(self._timerViewID, data)
                self._updateMarker(self._getMarkerData(isShow=False), isHide=True)
            return

    def _canUpdateTimer(self):
        modeName = self._avatar.inputHandler.ctrlModeName
        return True if self.__entityIDMatches() and modeName != 'video' else False

    def _updateMarker(self, data, isHide=False):
        if self._markerID is None:
            return
        else:
            if self.__isSwitching:
                self.__pushToPostponeCall(self._updateMarker, (data, isHide))
            else:
                modeName = self._avatar.inputHandler.ctrlModeName
                if not self.__entityIDMatches() or isHide or modeName == 'video':
                    self._guiFeedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.VEHICLE_CUSTOM_MARKER, self.entity.id, data)
            return

    def _getTimerData(self, isShow=True):
        data = {'duration': self._getDuration() if isShow else 0.0,
         'endTime': self._finishTime}
        return data

    def _getMarkerData(self, isShow=True):
        data = {'isShown': isShow,
         'isSourceVehicle': True,
         'duration': self._getDuration() if isShow else 0.0,
         'animated': True,
         'markerID': self._markerID}
        return data

    def _getDuration(self):
        return self._finishTime - BigWorld.serverTime() if self._finishTime else 0.0

    def _onUpdateObservedVehicleData(self, vehicleID, *args):
        if self.__isSwitching:
            self.__isSwitching = False
            self.__postponeCallProcessing()
        self._updateVisuals()

    def _onAppearanceReady(self):
        vehicle = self.entity
        appearance = vehicle.appearance
        if appearance is None or not appearance.isConstructed:
            return
        elif vehicle.health <= 0:
            return
        else:
            self._updateVisuals()
            return

    def __entityIDMatches(self):
        return self.entity.id == self._avatar.inputHandler.ctrl.curVehicleID or self._avatar.isObserverFPV and self.entity.id == self._avatar.observedVehicleID

    def __onSwitchingViewPoint(self):
        self.__isSwitching = True

    def __onCameraChanged(self, cameraName, currentVehicleId=None):
        if cameraName == 'video':
            self._updateMarker(self._getMarkerData())

    def __pushToPostponeCall(self, func, args):
        self.__postponedCalls.append((func, args))

    def __postponeCallProcessing(self):
        for f_data in self.__postponedCalls:
            f, args = f_data
            f(*args)

        self.__postponedCalls = []
