# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/events_containers/components/life_cycle/interfaces.py
from __future__ import absolute_import
import typing
from events_containers.common.containers import IClientEventsContainer, IClientEventsContainerListener

class ILifeCycleComponent(object):

    @property
    def lifeCycleEvents(self):
        raise NotImplementedError

    def getComponentParams(self):
        return None


class IComponentLifeCycleEventsLogic(object):
    onComponentParamsCollected = None
    onComponentDestroyed = None

    def processParamsCollected(self):
        raise NotImplementedError


class IComponentLifeCycleEvents(IClientEventsContainer, IComponentLifeCycleEventsLogic):
    pass


class IComponentLifeCycleListenerLogic(object):

    def onComponentParamsCollected(self, params):
        pass

    def onComponentDestroyed(self, component):
        pass


class IComponentLifeCycleListener(IClientEventsContainerListener, IComponentLifeCycleListenerLogic):
    pass
