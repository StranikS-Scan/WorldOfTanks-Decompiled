# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/contexts/ability_context.py
from vehicle_context import VehicleContextClient
from visual_script.context import vse_event_out, vse_set_property
from visual_script.misc import ASPECT
from visual_script.slot_types import SLOT_TYPE

class AbilityContextClient(VehicleContextClient):

    def __init__(self, vehicle):
        super(AbilityContextClient, self).__init__(vehicle)
        self.canActivate = True
        self.errorKey = None
        return

    @vse_set_property(SLOT_TYPE.BOOL, display_name='CanActivate', description='', aspects=[ASPECT.CLIENT])
    def setCanActivate(self, canActivate):
        self.canActivate = canActivate
        if canActivate:
            self.errorKey = None
        return

    @vse_set_property(SLOT_TYPE.STR, display_name='ErrorKey', description='', aspects=[ASPECT.CLIENT])
    def setErrorKey(self, errorKey):
        self.errorKey = errorKey if errorKey else None
        return

    @vse_event_out(display_name='OnCanActive', description='Calls to check whether ability can be activated', aspects=[ASPECT.CLIENT])
    def canActive(self):
        pass

    @vse_event_out(display_name='OnReady', description='Calls when ability ready', aspects=[ASPECT.CLIENT])
    def ready(self):
        pass

    @vse_event_out(display_name='OnActivated', description='Calls when ability activated', aspects=[ASPECT.CLIENT])
    def active(self):
        pass

    @vse_event_out(display_name='OnCooldown', description='Calls when ability becomes cooldown', aspects=[ASPECT.CLIENT])
    def cooldown(self):
        pass

    @vse_event_out(display_name='OnExhausted', description='Calls when ability becomes exhausted', aspects=[ASPECT.CLIENT])
    def exhausted(self):
        pass

    @vse_event_out(display_name='OnPrepared', description='Calls when ability becomes preparing', aspects=[ASPECT.CLIENT])
    def preparing(self):
        pass

    @vse_event_out(display_name='OnCleanup', description='Calls when ability becomes cleanup', aspects=[ASPECT.CLIENT])
    def cleanup(self):
        pass

    @vse_event_out(display_name='OnUnavailable', description='Calls when ability unavailable', aspects=[ASPECT.CLIENT])
    def unavailable(self):
        pass

    @vse_event_out(display_name='OnDeploying', description='Calls when ability becomes deploying', aspects=[ASPECT.CLIENT])
    def deploying(self):
        pass

    def notrunning(self):
        pass
