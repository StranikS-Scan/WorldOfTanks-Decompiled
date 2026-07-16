# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/power_mode_components.py
from __future__ import absolute_import
import bisect
import CGF
from GenericComponents import Sequence
from constants import IS_CLIENT
from cgf_script.registration import ComponentProperty, registerComponent
from Vehicular import VehicleAudition
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
if IS_CLIENT:
    from PowerModeController import PowerModeController
else:

    class PowerModeController(object):
        pass


@registerComponent
class PowerModeRTPCComponent(object):
    category = 'Sound'
    editorTitle = 'PowerMode RTPC'
    domain = CGF.Domain.Client
    RTPCName = ComponentProperty(type=CGF.PropertyType.String, value='RTPC_ext_abl_power_volume', editorName='RTPC name')

    def __init__(self):
        super(PowerModeRTPCComponent, self).__init__()
        self.powerModeControllerGO = None
        self.vehicleAuditionGO = None
        self.progress = -1.0
        return


@registerComponent
class PowerModeActiveProgressLayers(object):
    category = 'Vehicle Mechanics'
    editorTitle = 'Power Mode Active Progress Layers'
    domain = CGF.Domain.Client
    points = ComponentProperty(type=CGF.PropertyType.FloatList, editorName='Points', value=(0.0,))
    transitionTime = ComponentProperty(type=CGF.PropertyType.Float, editorName='Transition time', value=2.0)
    layerNamePattern = ComponentProperty(type=CGF.PropertyType.String, editorName='Layer name pattern', value='layer_{}')

    def __init__(self):
        super(PowerModeActiveProgressLayers, self).__init__()
        self.powerModeControllerGO = None
        self.requestedLayerName = ''
        self.progress = -1.0
        return


class PowerModeMechanicSystem(CGF.System):
    PowerModeProgressActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(PowerModeActiveProgressLayers), CGF.Rw(Sequence))
    PowerModeProgressDectivated = CGF.DeactivateReaction(CGF.ReactRw(PowerModeActiveProgressLayers))
    PowerModeProgressIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Rw(PowerModeActiveProgressLayers), CGF.Rw(Sequence))
    PowerModeRTPCActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(PowerModeRTPCComponent))
    PowerModeRTPCDeactivated = CGF.DeactivateReaction(CGF.ReactRw(PowerModeRTPCComponent))
    PowerModeRTPCIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Rw(PowerModeRTPCComponent))
    PowerModeControllerAccess = CGF.AccessReaction(CGF.GameObject, CGF.Rw(PowerModeController))
    VehicleAuditionAccess = CGF.AccessReaction(CGF.GameObject, CGF.Rw(VehicleAudition))
    Reactions = CGF.Reactions(PowerModeProgressActivated, PowerModeProgressDectivated, PowerModeProgressIterate, PowerModeRTPCActivated, PowerModeRTPCDeactivated, PowerModeControllerAccess, VehicleAuditionAccess, PowerModeRTPCIterate)

    def commonUpdate(self):
        powerModeAccess = self.reaction(self.PowerModeControllerAccess)
        auditionAccess = self.reaction(self.VehicleAuditionAccess)
        for layers in self.reaction(self.PowerModeProgressDectivated):
            layers.powerModeControllerGO = None

        for rtpc in self.reaction(self.PowerModeRTPCDeactivated):
            rtpc.powerModeControllerGO = None
            self.__setEnginePowerMode(rtpc, powerModeAccess, auditionAccess)

        for go, rtpc in self.reaction(self.PowerModeRTPCActivated):
            rtpc.vehicleAuditionGO, _ = CGF.findParentWithReaction(go, auditionAccess)
            rtpc.powerModeControllerGO, _ = CGF.findParentWithReaction(go, powerModeAccess)
            self.__setEnginePowerMode(rtpc, powerModeAccess, auditionAccess)

        for go, layers, sequence in self.reaction(self.PowerModeProgressActivated):
            layers.powerModeControllerGO, _ = CGF.findParentWithReaction(go, powerModeAccess)
            self.__requestActiveProgressLayer(layers, powerModeAccess, sequence, isInstantly=True)

        return

    def periodUpdate(self):
        powerModeAccess = self.reaction(self.PowerModeControllerAccess)
        auditionAccess = self.reaction(self.VehicleAuditionAccess)
        for layers, sequence in self.reaction(self.PowerModeProgressIterate):
            self.__requestActiveProgressLayer(layers, powerModeAccess, sequence)

        for rtpc in self.reaction(self.PowerModeRTPCIterate):
            self.__setEnginePowerMode(rtpc, powerModeAccess, auditionAccess)

    @classmethod
    def __getPowerModeActiveProgress(cls, powerModeControllerGO, powerModeAccess):
        _, powerModeController = powerModeAccess.find(powerModeControllerGO)
        return powerModeController.getMechanicState().activeProgress if powerModeController is not None else 0.0

    @classmethod
    def __setEnginePowerMode(cls, powerModeRTPCComponent, powerModeAccess, auditionAccess):
        if powerModeRTPCComponent.vehicleAuditionGO is None:
            return
        else:
            _, audition = auditionAccess.find(powerModeRTPCComponent.vehicleAuditionGO)
            if audition is None:
                return
            soundObj = audition.getSoundObject(TankSoundObjectsIndexes.ENGINE)
            if soundObj is None:
                return
            progress = 0.0
            if powerModeRTPCComponent.powerModeControllerGO is not None:
                progress = cls.__getPowerModeActiveProgress(powerModeRTPCComponent.powerModeControllerGO, powerModeAccess)
            if powerModeRTPCComponent.progress != progress:
                soundObj.setRTPC(powerModeRTPCComponent.RTPCName, progress)
                powerModeRTPCComponent.progress = progress
            return

    @classmethod
    def __requestActiveProgressLayer(cls, powerModeLayers, powerModeAccess, sequence, isInstantly=False):
        if powerModeLayers.powerModeControllerGO is None:
            return
        else:
            isInTransition = sequence.activeLayerName == Sequence.TRANSITION_LAYER_NAME
            if isInTransition and not isInstantly:
                return
            progress = cls.__getPowerModeActiveProgress(powerModeLayers.powerModeControllerGO, powerModeAccess)
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
