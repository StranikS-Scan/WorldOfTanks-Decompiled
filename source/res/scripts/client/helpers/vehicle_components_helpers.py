# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/vehicle_components_helpers.py


class VehicleComponentDispatcher(object):

    def __init__(self):
        self._registry = {}

    def register(self, name, onAbsent=None, onPresent=None):
        entry = {'absent': onAbsent,
         'present': onPresent}
        self._registry[name] = entry

    def unregister(self):
        self._registry.clear()

    def dispatch(self, vehicle, componentName, *args, **kwargs):
        handlers = self._registry.get(componentName)
        if handlers is None:
            return
        else:
            component = vehicle.dynamicComponents.get(componentName)
            if component is None:
                handlers['absent'](vehicle, *args, **kwargs)
            else:
                handlers['present'](vehicle, component, *args, **kwargs)
            return
