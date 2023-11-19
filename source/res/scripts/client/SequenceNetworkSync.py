# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SequenceNetworkSync.py
import CGF
import logging
import BigWorld
from functools import partial
from Event import Event
from cgf_components_common.scenario.sequence_network_sync import SequenceNetworkSync as Sync
from script_component.DynamicScriptComponent import DynamicScriptComponent
from cgf_script.managers_registrator import onAddedQuery, autoregister, onProcessQuery, onRemovedQuery
from GenericComponents import Sequence
from constants import HAS_DEV_RESOURCES
_logger = logging.getLogger(__name__)

class SequenceNetworkSync(DynamicScriptComponent, Sync):

    def __init__(self):
        super(SequenceNetworkSync, self).__init__()
        self.expired = False
        self.onStateChange = Event()

    @property
    def name(self):
        go = self.entity.entityGameObject
        return go.name if go is not None else 'unknown'

    @property
    def actualTime(self):
        return self.syncTime if self.state == int(Sequence.State.Paused) else BigWorld.serverTime() - self.syncTime - 0.5

    def set_state(self, prev):
        old = str(Sequence.State(prev))
        new = str(Sequence.State(self.state))
        _logger.debug('SequenceNetworkSync [%s] changing state [%s]->[%s]', self.name, old, new)
        self.onStateChange(self)

    if HAS_DEV_RESOURCES:

        def start(self):
            return self.cell.setState(Sequence.State.Running, 0.0)

        def stop(self):
            return self.cell.setState(Sequence.State.Stopped, 0.0)

        def pause(self, time=0.0):
            return self.cell.setState(Sequence.State.Paused, time)

    else:

        def start(self):
            pass

        def stop(self):
            pass

        def pause(self, time=0.0):
            pass


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class SequenceNetworkSyncManager(CGF.ComponentManager):

    @onAddedQuery(SequenceNetworkSync, Sequence)
    def onControllerAdded(self, sync, seq):
        sync.onStateChange += partial(self.onStateChange, seq)
        self.onStateChange(seq, sync)
        seq.syncSubSequences()

    @onRemovedQuery(SequenceNetworkSync)
    def onControllerRemoved(self, sync):
        sync.onStateChange.clear()

    @onProcessQuery(SequenceNetworkSync, Sequence, tickGroup='PreSimulation')
    def onProcess(self, sync, seq):
        if sync.state == int(Sequence.State.Stopped) and seq.state != Sequence.State.Stopped:
            seq.stop()
            return
        if sync.state == int(Sequence.State.Paused) or sync.state == int(Sequence.State.Running):
            self.__updateTime(sync, seq)

    def onStateChange(self, seq, sync):
        if sync.state == int(Sequence.State.Stopped):
            seq.stop()
            return
        if sync.state == int(Sequence.State.Running) or sync.state == int(Sequence.State.Paused):
            self.__updateTime(sync, seq)
            return
        _logger.warning('Unknown SequenceNetworkSync [%s] state', sync.name)

    def __updateTime(self, sync, seq):
        time = sync.actualTime
        if time >= seq.duration:
            time = seq.duration
        if seq.time != time:
            seq.setManualTime(time)
