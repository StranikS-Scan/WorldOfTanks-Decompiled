# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/veh_post_progression/veh_post_progression_view_adaptor.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.veh_post_progression.vehicle_post_progression_component import VehiclePostProgressionComponentView

class VehiclePostProgressionViewAdaptor(InjectComponentAdaptor):
    __slots__ = ('__ctx',)

    def __init__(self, ctx):
        super(VehiclePostProgressionViewAdaptor, self).__init__()
        self.__ctx = ctx

    def _makeInjectView(self):
        return VehiclePostProgressionComponentView(**self.__ctx)
