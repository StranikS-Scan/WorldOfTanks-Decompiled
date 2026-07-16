# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/temperature_gun_rtpc_component.py
from __future__ import absolute_import
import CGF
import SoundGroups
import typing
from constants import IS_CLIENT
from cgf_script.registration import ComponentProperty, registerComponent
if IS_CLIENT:
    from TemperatureGunController import TemperatureGunController
else:

    class TemperatureGunController(object):
        pass


@registerComponent
class TemperatureGunRTPCComponent(object):
    category = 'Vehicle Mechanics'
    editorTitle = 'Temperature Gun RTPC'
    domain = CGF.Domain.Client
    RTPCName = ComponentProperty(type=CGF.PropertyType.String, value='RTPC_ext_gun_temperature_global', editorName='RTPC name')

    def __init__(self):
        super(TemperatureGunRTPCComponent, self).__init__()
        self.temperatureGunControllerGO = None
        self.progress = -1.0
        return


class TemperatureGunMechanicSystem(CGF.System):
    TemperatureGunActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(TemperatureGunRTPCComponent))
    TemperatureGunDeactivated = CGF.DeactivateReaction(CGF.ReactRw(TemperatureGunRTPCComponent))
    TemperatureGunIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Rw(TemperatureGunRTPCComponent))
    TemperatureControllerAccess = CGF.AccessReaction(CGF.GameObject, CGF.Ro(TemperatureGunController))
    Reactions = CGF.Reactions(TemperatureGunActivated, TemperatureGunDeactivated, TemperatureControllerAccess, TemperatureGunIterate)

    def commonUpdate(self):
        controllerAccess = self.reaction(self.TemperatureControllerAccess)
        for rtpc in self.reaction(self.TemperatureGunDeactivated):
            rtpc.temperatureGunControllerGO = None
            self.__setGunTemperature(rtpc, None)

        for go, rtpc in self.reaction(self.TemperatureGunActivated):
            self.__resolveController(rtpc, go, controllerAccess)

        return

    def periodUpdate(self):
        controllerAccess = self.reaction(self.TemperatureControllerAccess)
        for rtpc in self.reaction(self.TemperatureGunIterate):
            _, controller = controllerAccess.find(rtpc.temperatureGunControllerGO)
            if controller is not None:
                self.__setGunTemperature(rtpc, controller)

        return

    def __resolveController(self, rtpc, go, controllerAccess):
        found = CGF.findParentWithReaction(go, controllerAccess)
        if found is None:
            rtpc.temperatureGunControllerGO = None
            self.__setGunTemperature(rtpc, None)
            return
        else:
            rtpc.temperatureGunControllerGO, controller = found
            self.__setGunTemperature(rtpc, controller)
            return

    @classmethod
    def __getTemperatureGunProgress(cls, controller):
        return controller.getMechanicState().temperatureProgress * 100.0 if controller is not None else 0.0

    @classmethod
    def __setGunTemperature(cls, rtpc, controller):
        progress = cls.__getTemperatureGunProgress(controller)
        if rtpc.progress != progress:
            SoundGroups.g_instance.setGlobalRTPC(rtpc.RTPCName, progress)
            rtpc.progress = progress
