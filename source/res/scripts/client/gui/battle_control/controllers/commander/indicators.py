# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/indicators.py
import logging
import typing
from gui.battle_control.controllers.commander.markers import DamageDirectionMarker
from gui.battle_control.controllers.hit_direction_ctrl import IHitIndicator, HitType
from gui.battle_control.controllers.hit_direction_ctrl.pulls import RTSHitIndex
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Dict
_logger = logging.getLogger(__name__)

class _RTSDamageIndicator(IHitIndicator):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, duration, beginDuration):
        self.__markers = {}
        self.__duration = duration
        self.__beginDuration = beginDuration

    def getHitType(self):
        return HitType.RTS_HIT

    def destroy(self):
        self._unsubscribe()
        for hitIndex in self.__markers:
            self.__markers[hitIndex].fini()

        self.__markers.clear()

    def getDuration(self):
        return self.__duration

    def getBeginAnimationDuration(self):
        return self.__beginDuration

    def setVisible(self, flag):
        if flag:
            self._subscribe()
        else:
            self._unsubscribe()
        for marker in self.__markers.itervalues():
            marker.setVisible(flag)

    def showHitDirection(self, idx, hitData, timeLeft):
        duration = self.__duration
        if duration < timeLeft:
            return
        elif idx in self.__markers:
            self.__markers[idx].redraw(timeLeft)
            return
        else:
            ownVehicle = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(idx.vID)
            if not ownVehicle:
                _logger.warning('Own vehicle is not available as commander vehicle')
                return
            marker = DamageDirectionMarker(ownVehicle, hitData, timeLeft, duration)
            if marker is not None:
                self.__removeMarker(idx)
                self.__markers[idx] = marker
                cameraPos = self.__sessionProvider.dynamic.rtsCommander.getCameraPosition()
                if cameraPos is not None:
                    self.__updateVehicleCameraOffset(idx, cameraPos)
            return

    def hideHitDirection(self, idx):
        marker = self.__markers.get(idx)
        if marker is not None:
            marker.setVisible(False)
        return

    def _subscribe(self):
        if self.__sessionProvider.dynamic.rtsCommander is None:
            return
        else:
            self.__sessionProvider.dynamic.rtsCommander.onCameraPositionChanged += self.__onCameraPositionChanged
            self.__sessionProvider.dynamic.rtsCommander.onTick += self.__onCommanderTick
            return

    def _unsubscribe(self):
        if self.__sessionProvider.dynamic.rtsCommander is None:
            return
        else:
            self.__sessionProvider.dynamic.rtsCommander.onCameraPositionChanged -= self.__onCameraPositionChanged
            self.__sessionProvider.dynamic.rtsCommander.onTick -= self.__onCommanderTick
            return

    def __onCommanderTick(self):
        for idx in list(self.__markers):
            if self.__markers[idx].update():
                self.__removeMarker(idx)

    def __onCameraPositionChanged(self, cameraPosition):
        cameraPosition = cameraPosition or self.__sessionProvider.dynamic.rtsCommander.getCameraPosition()
        if cameraPosition is None:
            return
        else:
            for idx in self.__markers:
                self.__updateVehicleCameraOffset(idx, cameraPosition)

            return

    def __updateVehicleCameraOffset(self, idx, cameraPos):
        marker = self.__markers.get(idx)
        if marker is None:
            return
        else:
            marker.updateScalingFactor(cameraPos)
            return

    def __removeMarker(self, idx):
        marker = self.__markers.pop(idx, None)
        if marker is not None:
            marker.fini()
        return


def createRTSHitIndicator():
    from gui.Scaleform.daapi.view.battle.shared.indicators import DAMAGE_INDICATOR_ANIMATION_DURATION, BEGIN_ANIMATION_DURATION
    return _RTSDamageIndicator(DAMAGE_INDICATOR_ANIMATION_DURATION, BEGIN_ANIMATION_DURATION)
