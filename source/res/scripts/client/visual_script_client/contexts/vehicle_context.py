# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/contexts/vehicle_context.py
import weakref
from visual_script.context import VScriptContext, vse_get_property
from visual_script.misc import ASPECT
from visual_script.slot_types import SLOT_TYPE

class VehicleContextClient(VScriptContext):

    def __init__(self, vehicle):
        super(VehicleContextClient, self).__init__(ASPECT.CLIENT)
        self._vehicle = vehicle

    def destroy(self):
        self._vehicle = None
        return

    @vse_get_property(SLOT_TYPE.VEHICLE, display_name='Self', description='Return instance of current vehicle', aspects=[ASPECT.CLIENT])
    def getSelf(self):
        return weakref.proxy(self._vehicle)
