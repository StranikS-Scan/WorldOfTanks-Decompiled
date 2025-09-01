# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SequenceNetworkSync.py
import CGF
import logging
import BigWorld
from cgf_components.sequence_components import SequencePauseComponent, SequenceSnapshotComponent
from cgf_script.managers_registrator import onAddedQuery, autoregister, onProcessQuery, onRemovedQuery
from GenericComponents import Sequence
from constants import HAS_DEV_RESOURCES, IS_EDITOR
from cgf_script.component_meta_class import registerReplicableComponent, ComponentProperty, CGFMetaTypes
_logger = logging.getLogger(__name__)
if IS_EDITOR:

    class DynamicScriptComponent(object):
        pass


else:
    from BigWorld import DynamicScriptComponent
_STATE_STOPPED = Sequence.State.Stopped
_STATE_PAUSED = Sequence.State.Paused
_STATE_RUNNING = Sequence.State.Running
_INT_STATE_STOPPED = int(_STATE_STOPPED)
_INT_STATE_PAUSED = int(_STATE_PAUSED)
_INT_STATE_RUNNING = int(_STATE_RUNNING)

@registerReplicableComponent
class SequenceNetworkSync(DynamicScriptComponent):
    timeCorrection = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Time Correction', value=0.3)

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


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class SequenceNetworkSyncManager(CGF.ComponentManager):
    syncQuery = CGF.QueryConfig(SequenceNetworkSync, Sequence)

    def __init__(self):
        super(SequenceNetworkSyncManager, self).__init__()
        self.__isSyncPaused = False
        self.__snapshots = dict()

    @onAddedQuery(SequenceNetworkSync, Sequence)
    def onSequenceAdded(self, sync, sequence):
        if self.__isSyncPaused:
            sequence.pause()

    @onRemovedQuery(SequenceNetworkSync, Sequence)
    def onSequenceRemoved(self, sync, sequence):
        self.__snapshots.pop(sequence, None)
        return

    @onProcessQuery(SequenceNetworkSync, Sequence, tickGroup='PreSimulation')
    def onProcess(self, sync, sequence):
        if self.__isSyncPaused:
            return
        SequenceNetworkSyncManager.__syncSequence(sync, sequence)

    @onAddedQuery(SequenceSnapshotComponent)
    def onSnapshotRequested(self, _):
        for sync, sequence in self.syncQuery:
            self.__snapshots[sequence] = SequenceSnapshot(sync.syncTime, sync.speed, sync.state, sync.activeLayerIdx, sync.transition)

    @onRemovedQuery(SequenceSnapshotComponent)
    def onSnapshotCleared(self, _):
        self.__snapshots.clear()

    @onAddedQuery(SequencePauseComponent)
    def onPauseRequested(self, _):
        if self.__isSyncPaused:
            return
        self.__isSyncPaused = True
        for _, sequence in self.syncQuery:
            if sequence in self.__snapshots:
                snapshot = self.__snapshots[sequence]
                SequenceNetworkSyncManager.__syncSequence(snapshot, sequence)

    @onRemovedQuery(SequencePauseComponent)
    def onPauseLifted(self, _):
        if not self.__isSyncPaused:
            return
        self.__isSyncPaused = False

    @staticmethod
    def __syncSequence(sync, sequence):
        if not SequenceNetworkSyncManager.__trySyncTransition(sync, sequence):
            SequenceNetworkSyncManager.__trySyncActiveLayerIdx(sync, sequence)
        SequenceNetworkSyncManager.__syncLayer(sync, sequence)

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
        if syncState == _INT_STATE_RUNNING or syncState == _INT_STATE_PAUSED:
            SequenceNetworkSyncManager.__updateTime(sync, sequence)
            return

    @staticmethod
    def __updateTime(sync, sequence):
        time = sync.actualTime
        duration = sequence.duration
        if time >= duration:
            time = duration
        if sequence.time != time:
            sequence.requestTime(time)
