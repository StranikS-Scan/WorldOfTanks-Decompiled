# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/power_mode_components.py
import bisect
import CGF
from GenericComponents import Sequence
from constants import IS_CLIENT
from cgf_script.component_meta_class import CGFMetaTypes, ComponentProperty, registerComponent
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery, onProcessQuery
from Vehicular import VehicleAudition
from cgf_common.cgf_helpers import getParentGameObjectByComponent
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
if IS_CLIENT:
    from PowerModeController import PowerModeController
else:

    class PowerModeController(object):
        pass


@registerComponent
class PowerModeRTPCComponent(object):
    category = 'Sound'
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'PowerMode RTPC'
    RTPCName = ComponentProperty(type=CGFMetaTypes.STRING, value='RTPC_ext_abl_power_volume', editorName='RTPC name')

    def __init__(self):
        super(PowerModeRTPCComponent, self).__init__()
        self.powerModeControllerGO = None
        self.vehicleAuditionGO = None
        self.progress = -1.0
        return


@registerComponent
class PowerModeActiveProgressLayers(object):
    category = 'Vehicle Mechanics'
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'Power Mode Active Progress Layers'
    points = ComponentProperty(type=CGFMetaTypes.FLOAT_LIST, editorName='Points', value=(0.0,))
    transitionTime = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Transition time', value=2.0)
    layerNamePattern = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Layer name pattern', value='layer_{}')

    def __init__(self):
        super(PowerModeActiveProgressLayers, self).__init__()
        self.powerModeControllerGO = None
        self.requestedLayerName = ''
        self.progress = -1.0
        return


@autoregister(presentInAllWorlds=True)
class PowerModeMechanicManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, PowerModeActiveProgressLayers, Sequence)
    def onPowerModeActiveProgressLayersAdded(self, gameObject, powerModeLayers, sequence):
        powerModeLayers.powerModeControllerGO = getParentGameObjectByComponent(gameObject, PowerModeController)
        self.__requestActiveProgressLayer(powerModeLayers, sequence, isInstantly=True)

    @onRemovedQuery(PowerModeActiveProgressLayers)
    def onPowerModeActiveProgressLayersRemoved(self, powerModeLayers):
        powerModeLayers.powerModeControllerGO = None
        return

    @onProcessQuery(PowerModeActiveProgressLayers, Sequence, period=0.2)
    def onPowerModeProgressActiveProgressLayersProcess(self, powerModeLayers, sequence):
        self.__requestActiveProgressLayer(powerModeLayers, sequence)

    @onAddedQuery(CGF.GameObject, PowerModeRTPCComponent)
    def onPowerModeRTPCAdded(self, gameObject, powerModeRTPCComponent):
        powerModeRTPCComponent.vehicleAuditionGO = getParentGameObjectByComponent(gameObject, VehicleAudition)
        powerModeRTPCComponent.powerModeControllerGO = getParentGameObjectByComponent(gameObject, PowerModeController)
        self.__setEnginePowerMode(powerModeRTPCComponent)

    @onRemovedQuery(PowerModeRTPCComponent)
    def onPowerModeRTPCRemoved(self, powerModeRTPCComponent):
        powerModeRTPCComponent.powerModeControllerGO = None
        self.__setEnginePowerMode(powerModeRTPCComponent)
        return

    @onProcessQuery(PowerModeRTPCComponent, period=0.2)
    def onPowerModeProgressRTPCProcess(self, powerModeRTPCComponent):
        self.__setEnginePowerMode(powerModeRTPCComponent)

    @classmethod
    def __getPowerModeActiveProgress(cls, powerModeControllerGO):
        powerModeController = powerModeControllerGO.findComponentByType(PowerModeController)
        return powerModeController.getMechanicState().activeProgress if powerModeController is not None else 0.0

    @classmethod
    def __setEnginePowerMode(cls, powerModeRTPCComponent):
        if powerModeRTPCComponent.vehicleAuditionGO is None:
            return
        else:
            audition = powerModeRTPCComponent.vehicleAuditionGO.findComponentByType(VehicleAudition)
            if audition is None:
                return
            soundObj = audition.getSoundObject(TankSoundObjectsIndexes.ENGINE)
            if soundObj is None:
                return
            progress = 0.0
            if powerModeRTPCComponent.powerModeControllerGO is not None:
                progress = cls.__getPowerModeActiveProgress(powerModeRTPCComponent.powerModeControllerGO)
            if powerModeRTPCComponent.progress != progress:
                soundObj.setRTPC(powerModeRTPCComponent.RTPCName, progress)
                powerModeRTPCComponent.progress = progress
            return

    @classmethod
    def __requestActiveProgressLayer(cls, powerModeLayers, sequence, isInstantly=False):
        if powerModeLayers.powerModeControllerGO is None:
            return
        else:
            isInTransition = sequence.activeLayerName == Sequence.TRANSITION_LAYER_NAME
            if isInTransition and not isInstantly:
                return
            progress = cls.__getPowerModeActiveProgress(powerModeLayers.powerModeControllerGO)
            if powerModeLayers.progress == progress:
                return
            point = bisect.bisect_left(powerModeLayers.points, progress)
            layerName = powerModeLayers.layerNamePattern.format(point)
            if powerModeLayers.requestedLayerName == layerName:
                return
            transitionTime = 0.0 if isInstantly else powerModeLayers.transitionTime
            sequence.requestLayerChangeByName(layerName, transitionTime)
            powerModeLayers.requestedLayerName = layerName
            powerModeLayers.progress = progress
            return
