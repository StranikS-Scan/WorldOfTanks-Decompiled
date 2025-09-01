# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/components/component_events/events_interfaces.py


class IComponentEvents(object):
    onComponentEventsDestroy = None

    def destroy(self):
        pass


class IComponentListener(object):

    def subscribeTo(self, events):
        raise NotImplementedError

    def unsubscribeFrom(self, events):
        raise NotImplementedError
