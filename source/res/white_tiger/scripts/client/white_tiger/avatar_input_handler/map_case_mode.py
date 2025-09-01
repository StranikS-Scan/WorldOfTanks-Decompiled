# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/avatar_input_handler/map_case_mode.py
from AvatarInputHandler.MapCaseMode import _AreaStrikeSelector, _VehiclesSelector, _DEFAULT_STRIKE_DIRECTION

class HyperionEquimpentWrapper(object):

    def __init__(self, equipment):
        self._equipment = equipment
        self.areaVisual = self.__getParam(equipment, HyperionStrikeSelector.AREA_VISUAL_PARAM_NAME)
        self.areaRadius = float(self.__getParam(equipment, HyperionStrikeSelector.RADIUS_PARAM_NAME, 0.0))
        self.areaWidth = self.areaLength = 2.0 * self.areaRadius
        self.areaColor = None
        return

    def __getattr__(self, attr):
        return getattr(self._equipment, attr)

    def __getParam(self, equipment, paramName, default=None):
        from visual_script.misc import ASPECT
        config = equipment.visualScript.get(ASPECT.CLIENT, [])
        for data in config:
            params = data.get('params', {})
            if paramName not in params:
                continue
            return params[paramName]

        return None


class HyperionStrikeSelector(_AreaStrikeSelector, _VehiclesSelector):
    RADIUS_PARAM_NAME = 'HYPERION_RADIUS'
    AREA_VISUAL_PARAM_NAME = 'areaVisual'

    def __init__(self, position, equipment, direction=_DEFAULT_STRIKE_DIRECTION):
        wrapper = HyperionEquimpentWrapper(equipment)
        self._radius = wrapper.areaRadius
        _AreaStrikeSelector.__init__(self, position, wrapper)
        _VehiclesSelector.__init__(self, self.__intersected, selectPlayer=True)

    def destroy(self):
        _VehiclesSelector.destroy(self)
        _AreaStrikeSelector.destroy(self)

    def tick(self):
        self.highlightVehicles()

    def __intersected(self, vehicles):
        for v in vehicles:
            if self.area.pointInsideCircle(v.position, self._radius):
                yield v
