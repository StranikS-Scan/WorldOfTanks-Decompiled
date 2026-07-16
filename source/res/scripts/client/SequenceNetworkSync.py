# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SequenceNetworkSync.py
from __future__ import absolute_import
import logging
import BigWorld
import CGF
from constants import HAS_DEV_RESOURCES
from cgf_client_common.entity_dyn_components import ReplicableDynamicScriptComponent
from cgf_components.sequence_components import SequencePauseComponent, SequenceSnapshotComponent
from cgf_script.registration import registerReplicableComponent, ComponentProperty
from GenericComponents import Sequence
_logger = logging.getLogger(__name__)
_STATE_STOPPED = Sequence.State.Stopped
_STATE_PAUSED = Sequence.State.Paused
_STATE_RUNNING = Sequence.State.Running
_INT_STATE_STOPPED = int(_STATE_STOPPED)
_INT_STATE_PAUSED = int(_STATE_PAUSED)
_INT_STATE_RUNNING = int(_STATE_RUNNING)

@registerReplicableComponent
class SequenceNetworkSync(ReplicableDynamicScriptComponent):
    editorTitle = 'Sequence Network Sync'
    timeCorrection = ComponentProperty(type=CGF.PropertyType.Float, editorName='Time Correction', value=0.3)

    def __init__(self):
        super(SequenceNetworkSync, self).__init__()
        self.expired = False

    @property
    def name(self):
        go = self.entity.entityGameObject
        return go.name if go is not None else 'unknown'

    @property
    def actualTime(self):
        return self.syncTime if self.state == _INT_STATE_PAUSED else (BigWorld.serverTime() - self.syncTime) * self.speed - self.timeCorrection

    if HAS_DEV_RESOURCES:

        def start(self):
            self.cell.requestState(_STATE_RUNNING)

        def stop(self):
            self.cell.requestState(_STATE_STOPPED)

        def pause(self):
            self.cell.requestState(_STATE_PAUSED)

        def requestTime(self, time):
            self.cell.requestTime(time)

        def requestLayerChange(self, layerIdx, time):
            self.cell.requestLayerChange(layerIdx, time)

        def set_transition(self, prev):
            transition = str(self.transition) if self.transition is not None else 'None'
            _logger.debug('SequenceNetworkSync [%s] new transition [%s]', self.name, transition)
            return

        def set_speed(self, prev):
            old = str(prev)
            new = str(self.speed)
            _logger.debug('SequenceNetworkSync [%s] changing speed [%s]->[%s]', self.name, old, new)

        def set_state(self, prev):
            old = str(Sequence.State(prev))
            new = str(Sequence.State(self.state))
            _logger.debug('SequenceNetworkSync [%s] changing state [%s]->[%s]', self.name, old, new)

        def set_activeLayerIdx(self, prev):
            old = str(prev)
            new = str(self.activeLayerIdx)
            _logger.debug('SequenceNetworkSync [%s] changing active layer [%s]->[%s]', self.name, old, new)

    else:

        def start(self):
            pass

        def stop(self):
            pass

        def pause(self):
            pass

        def requestTime(self, time):
            pass

        def requestLayerChange(self, layerIdx, time):
            pass


class SequenceSnapshot(object):

    def __init__(self, syncTime=0.0, speed=1.0, state=0, activeLayerIdx=0, transition=None):
        self.syncTime = syncTime
        self.speed = speed
        self.state = state
        self.activeLayerIdx = activeLayerIdx
        self.transition = transition


class SequenceNetworkSyncSystem(CGF.System):
    SequenceSyncIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.GameObject, CGF.Ro(SequenceNetworkSync), CGF.Rw(Sequence))
    SequenceActivated = CGF.ActivateReaction(CGF.ReactHas(SequenceNetworkSync), CGF.Rw(Sequence))
    SequenceDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactHas(SequenceNetworkSync), CGF.Rw(Sequence))
    SnapshotActivated = CGF.ActivateReaction(CGF.ReactRo(SequenceSnapshotComponent))
    SnapshotDeactivated = CGF.DeactivateReaction(CGF.ReactRo(SequenceSnapshotComponent))
    PauseActivated = CGF.ActivateReaction(CGF.ReactRo(SequencePauseComponent))
    PauseDeactivated = CGF.DeactivateReaction(CGF.ReactRo(SequencePauseComponent))
    Reactions = CGF.Reactions(SequenceSyncIterate, SequenceActivated, SequenceDeactivated, SnapshotActivated, SnapshotDeactivated, PauseActivated, PauseDeactivated)

    def __init__(self):
        super(SequenceNetworkSyncSystem, self).__init__()
        self.__isSyncPaused = False
        self.__snapshots = {}

    def update(self):
        syncIter, sequenceActivated, sequenceDeactivated, snapshotActivated, snapshotDeactivated, pauseActivated, pauseDeactivated = self.reactions
        snapshots = self.__snapshots
        for go, sequence in sequenceDeactivated:
            snapshots.pop(go.id, None)

        if snapshotDeactivated:
            snapshots.clear()
        if pauseDeactivated and self.__isSyncPaused:
            self.__isSyncPaused = False
        isSyncPaused = self.__isSyncPaused
        if isSyncPaused:
            for sequence in sequenceActivated:
                sequence.pause()

        createSnapshot = bool(snapshotActivated)
        needPause = False
        if pauseActivated and not isSyncPaused:
            self.__isSyncPaused = True
            isSyncPaused = True
            needPause = True
        _syncSequence = self.__syncSequence
        for go, sync, sequence in syncIter:
            if createSnapshot:
                snapshots[go.id] = SequenceSnapshot(sync.syncTime, sync.speed, sync.state, sync.activeLayerIdx, sync.transition)
            if needPause:
                snapshot = snapshots.get(go.id)
                if snapshot is not None:
                    _syncSequence(snapshot, sequence)
            if isSyncPaused:
                break
            _syncSequence(sync, sequence)

        return

    @staticmethod
    def __syncSequence(sync, sequence):
        if not SequenceNetworkSyncSystem.__trySyncTransition(sync, sequence):
            SequenceNetworkSyncSystem.__trySyncActiveLayerIdx(sync, sequence)
        SequenceNetworkSyncSystem.__syncLayer(sync, sequence)

    @staticmethod
    def __trySyncTransition(sync, sequence):
        transition = sync.transition
        if transition is None:
            return False
        else:
            transitionTuple = (transition['layerIdx'], transition['time'])
            if transitionTuple == sequence.transition:
                return False
            sequence.requestLayerChange(transition['layerIdx'], transition['time'])
            sequence.pause()
            return True

    @staticmethod
    def __trySyncActiveLayerIdx(sync, sequence):
        activeLayerIdx = sync.activeLayerIdx
        if activeLayerIdx == sequence.activeLayerIdx:
            return False
        sequence.requestLayerChange(activeLayerIdx, 0.0)
        sequence.pause()
        return True

    @staticmethod
    def __syncLayer(sync, sequence):
        syncState = sync.state
        sequence.speed = sync.speed
        if syncState == _INT_STATE_STOPPED and sequence.state != _STATE_STOPPED:
            sequence.stop()
            return
        if syncState in (_INT_STATE_RUNNING, _INT_STATE_PAUSED):
            SequenceNetworkSyncSystem.__updateTime(sync, sequence)
            return

    @staticmethod
    def __updateTime(sync, sequence):
        time = min(sync.actualTime, sequence.duration)
        if sequence.time != time:
            sequence.requestTime(time)
