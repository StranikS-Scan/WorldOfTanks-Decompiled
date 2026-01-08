# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/temperature_gun_rtpc_component.py
import CGF
import SoundGroups
from constants import IS_CLIENT
from cgf_script.component_meta_class import CGFMetaTypes, ComponentProperty, registerComponent
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery, onProcessQuery
from cgf_common.cgf_helpers import getParentGameObjectByComponent
if IS_CLIENT:
    from TemperatureGunController import TemperatureGunController
else:

    class TemperatureGunController(object):
        pass


@registerComponent
class TemperatureGunRTPCComponent(object):
    category = 'Vehicle Mechanics'
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'Temperature Gun RTPC'
    RTPCName = ComponentProperty(type=CGFMetaTypes.STRING, value='RTPC_ext_gun_temperature_global', editorName='RTPC name')

    def __init__(self):
        super(TemperatureGunRTPCComponent, self).__init__()
        self.temperatureGunControllerGO = None
        self.progress = -1.0
        return


@autoregister(presentInAllWorlds=True)
class TemperatureGunMechanicManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, TemperatureGunRTPCComponent)
    def onTemperatureGunRTPCAdded(self, gameObject, temperatureGunRTPCComponent):
        temperatureGunRTPCComponent.temperatureGunControllerGO = getParentGameObjectByComponent(gameObject, TemperatureGunController)
        self.__setGunTemperature(temperatureGunRTPCComponent)

    @onRemovedQuery(TemperatureGunRTPCComponent)
    def onTemperatureGunRTPCRemoved(self, temperatureGunRTPCComponent):
        temperatureGunRTPCComponent.temperatureGunControllerGO = None
        self.__setGunTemperature(temperatureGunRTPCComponent)
        return

    @onProcessQuery(TemperatureGunRTPCComponent, period=0.2)
    def onTemperatureGunProgressRTPCProcess(self, temperatureGunRTPCComponent):
        self.__setGunTemperature(temperatureGunRTPCComponent)

    @classmethod
    def __getTemperatureGunProgress(cls, temperatureGunControllerGO):
        temperController = temperatureGunControllerGO.findComponentByType(TemperatureGunController)
        return temperController.getMechanicState().temperatureProgress * 100.0 if temperController is not None else 0.0

    @classmethod
    def __setGunTemperature(cls, temperatureGunRTPCComponent):
        progress = 0.0
        if temperatureGunRTPCComponent.temperatureGunControllerGO is not None:
            progress = cls.__getTemperatureGunProgress(temperatureGunRTPCComponent.temperatureGunControllerGO)
        if temperatureGunRTPCComponent.progress != progress:
            SoundGroups.g_instance.setGlobalRTPC(temperatureGunRTPCComponent.RTPCName, progress)
            temperatureGunRTPCComponent.progress = progress
        return
