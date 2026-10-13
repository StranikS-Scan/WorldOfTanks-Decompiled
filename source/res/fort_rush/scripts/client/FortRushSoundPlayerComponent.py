# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/FortRushSoundPlayerComponent.py
from __future__ import absolute_import
from helpers.events_handler import EventsHandler
from typing import Dict, Union, Tuple
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD, FINISH_REASON
from fort_rush.gui.shared.events import CaptureInvaderEvent, CapturePointEvent
from fort_rush.gui.sounds import play2DSound, get2DSound
from fort_rush.gui.sounds.sound_constants import CAPTURE_STATE_START_TO_SOUND, CAPTURE_STATE_STOP_TO_SOUND, CapturePointSounds, RTPC_VALUE_THRESHOLD, SoundStates, WIN_POINTS_CAP_STINGER
from fort_rush_common.fort_rush_constants import CAPTURE_POINT_INVADER_COMPONENT, CAPTURE_POINT_NO_TEAM, CaptureStates
from gui.shared import EVENT_BUS_SCOPE, EventPriority
from script_component.DynamicScriptComponent import DynamicScriptComponent
_NORMALIZED_MAX_VALUE = 1.0

class FortRushSoundPlayerComponent(DynamicScriptComponent, EventsHandler):

    def __init__(self):
        super(FortRushSoundPlayerComponent, self).__init__()
        self._pointStates = {}
        self._pointInvadingTeams = {}
        self._pointOwnerTeams = {}
        self._sound = None
        return

    def _onAvatarReady(self):
        self._subscribe()

    def onDestroy(self):
        self._unsubscribe()
        if self._sound:
            self._sound.stop()
            self._sound = None
        return

    def _getEvents(self):
        return ((self.entity.events.onVehicleHealthChanged, self._onVehicleHealthChanged), (g_playerEvents.onArenaPeriodChange, self._onArenaPeriodChange))

    def _getListeners(self):
        listeners = [(CapturePointEvent.CAPTURABLE_POINT_UPDATE,
          self._onCapturePointUpdate,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.HIGH), (CaptureInvaderEvent.INVADER_ADDED,
          self._onInvaderAdded,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.HIGH), (CaptureInvaderEvent.INVADER_REMOVED,
          self._onInvaderRemoved,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.HIGH)]
        return listeners

    def _onCapturePointUpdate(self, event):
        if not self.entity.isPlayerVehicle:
            return
        else:
            invaderComponent = self.entity.dynamicComponents.get(CAPTURE_POINT_INVADER_COMPONENT)
            isInvadingThisPoint = invaderComponent is not None and invaderComponent.capturablePointName == event.capturablePointName
            isStaleDecreasing = isInvadingThisPoint and event.totalInvaders > 0 and event.state == CaptureStates.DECREASING and event.invadersTeam == self.entity.publicInfo['team']
            newState = CaptureStates.CAPTURING if isStaleDecreasing else event.state
            isNeutralizing = event.ownersTeam not in (CAPTURE_POINT_NO_TEAM, event.invadersTeam) if isStaleDecreasing else event.isNeutralizing
            self._pointInvadingTeams[event.capturablePointName] = event.invadersTeam
            self._pointOwnerTeams[event.capturablePointName] = event.ownersTeam
            previousState = self._pointStates.get(event.capturablePointName, CaptureStates.NEUTRAL)
            if isNeutralizing:
                newState = SoundStates.NEUTRALIZING
            self._pointStates[event.capturablePointName] = newState
            if not isInvadingThisPoint:
                return
            if previousState == newState:
                self._setRTPCValue(event, newState)
                return
            if newState == CaptureStates.CAPTURED and previousState == CaptureStates.CONTESTED:
                soundToPlay = CAPTURE_STATE_STOP_TO_SOUND.get(previousState)
            else:
                soundToPlay = CAPTURE_STATE_START_TO_SOUND.get(newState)
            if soundToPlay is None:
                if newState == CaptureStates.DECREASING and self._sound:
                    if event.ownersTeam == CAPTURE_POINT_NO_TEAM:
                        soundToPlay = CAPTURE_STATE_START_TO_SOUND.get(SoundStates.NEUTRALIZING)
                    else:
                        soundToPlay = CAPTURE_STATE_START_TO_SOUND.get(CaptureStates.CAPTURING)
            self._sound = get2DSound(soundToPlay)
            self._setRTPCValue(event, newState)
            self._sound.play()
            return

    def _setRTPCValue(self, event, resolvedState):
        if resolvedState in (CaptureStates.CAPTURING, CaptureStates.DECREASING, SoundStates.NEUTRALIZING) and self._sound:
            if resolvedState != CaptureStates.DECREASING:
                progress = event.captureProgressPercent * RTPC_VALUE_THRESHOLD
                rtpcValue = progress if resolvedState == SoundStates.NEUTRALIZING else RTPC_VALUE_THRESHOLD + progress
            else:
                progress = (_NORMALIZED_MAX_VALUE - event.captureProgressPercent) * RTPC_VALUE_THRESHOLD
                rtpcValue = progress if event.ownersTeam == CAPTURE_POINT_NO_TEAM else RTPC_VALUE_THRESHOLD + progress
            self._sound.setRTPC(CapturePointSounds.RTPC, rtpcValue)

    def _onInvaderAdded(self, event):
        if event.vehicleID != self.entity.id:
            return
        state = self._pointStates.get(event.baseName, CaptureStates.NEUTRAL)
        if state in (CaptureStates.NEUTRAL, CaptureStates.CAPTURED):
            return
        if state == CaptureStates.DECREASING:
            self._handleDecreasingStateAsInvader(CAPTURE_STATE_START_TO_SOUND, event.baseName)
            return
        invadingTeam = self._pointInvadingTeams.get(event.baseName, CAPTURE_POINT_NO_TEAM)
        if invadingTeam != self.entity.publicInfo['team']:
            return
        self._playCollectionSound(CAPTURE_STATE_START_TO_SOUND, state)

    def _onInvaderRemoved(self, event):
        if event.vehicleID != self.entity.id:
            return
        state = self._pointStates.get(event.baseName, CaptureStates.NEUTRAL)
        if state == CaptureStates.DECREASING:
            self._handleDecreasingStateAsInvader(CAPTURE_STATE_STOP_TO_SOUND, event.baseName)
            return
        self._playCollectionSound(CAPTURE_STATE_STOP_TO_SOUND, state)

    def _playCollectionSound(self, collection, state):
        soundToPlay = collection.get(state)
        if soundToPlay is None:
            return
        else:
            self._sound = get2DSound(soundToPlay)
            self._sound.play()
            return

    def _handleDecreasingStateAsInvader(self, collection, baseName):
        ownerTeam = self._pointOwnerTeams.get(baseName, CAPTURE_POINT_NO_TEAM)
        if ownerTeam == self.entity.publicInfo['team']:
            self._playCollectionSound(collection, CaptureStates.CAPTURING)
        else:
            self._playCollectionSound(collection, SoundStates.NEUTRALIZING)

    def _onVehicleHealthChanged(self, vehicleID, newHealth, oldHealth):
        if not self.entity.isPlayerVehicle or vehicleID != self.entity.id or newHealth <= oldHealth:
            return
        play2DSound(CapturePointSounds.HEAL)

    def _onArenaPeriodChange(self, period, _, __, periodAdditionalInfo):
        if period != ARENA_PERIOD.AFTERBATTLE:
            return
        _, finishReason = periodAdditionalInfo
        if finishReason != FINISH_REASON.WIN_POINTS_CAP:
            return
        play2DSound(WIN_POINTS_CAP_STINGER)
