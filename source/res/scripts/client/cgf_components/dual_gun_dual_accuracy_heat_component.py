# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/dual_gun_dual_accuracy_heat_component.py
import BigWorld
import typing
import CGF
from GenericComponents import AnimatorComponent
from Sound import Sound3DComponent
from cgf_components.cgf_helpers import getVehicleFromGO
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import autoregister, onAddedQuery
from constants import DUAL_GUN
from debug_utils import LOG_ERROR

@registerComponent
class DualGunDualAccuracyHeatComponent(object):
    category = 'Common'
    editorTitle = 'Dualgun Dual Accuracy Heat Component'
    leftLink = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Left gun animator link', value=AnimatorComponent)
    rightLink = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Right gun animator link', value=AnimatorComponent)
    leftSoundLink = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Left gun sound link', value=Sound3DComponent)
    rightSoundLink = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Right gun sound link', value=Sound3DComponent)
    npcLeftSoundLink = ComponentProperty(type=CGFMetaTypes.LINK, editorName='NPC left gun sound link', value=Sound3DComponent)
    npcRightSoundLink = ComponentProperty(type=CGFMetaTypes.LINK, editorName='NPC right gun sound link', value=Sound3DComponent)

    def __init__(self):
        super(DualGunDualAccuracyHeatComponent, self).__init__()
        self.__vehicleID = None
        self.__gameObject = None
        return

    @property
    def vehicleID(self):
        return self.__vehicleID

    @property
    def gameObject(self):
        return self.__gameObject

    @vehicleID.setter
    def vehicleID(self, vehicleID):
        self.__vehicleID = vehicleID

    @gameObject.setter
    def gameObject(self, gameObject):
        self.__gameObject = gameObject

    def toggleState(self, gun, state):
        animatorLink = self.leftLink if gun == DUAL_GUN.ACTIVE_GUN.LEFT else self.rightLink
        vehicle = BigWorld.player().getVehicleAttached()
        if vehicle is None:
            return
        else:
            isLeft = gun == DUAL_GUN.ACTIVE_GUN.LEFT
            if vehicle.id != self.__vehicleID:
                soundLink = self.npcLeftSoundLink if isLeft else self.npcRightSoundLink
            else:
                soundLink = self.leftSoundLink if isLeft else self.rightSoundLink
            if animatorLink is None or soundLink is None:
                LOG_ERROR('animator/sound component links are not configured', gun, state)
                return
            animator = animatorLink()
            sound3D = soundLink()
            if not state:
                animator.stop()
                sound3D.stop()
                return
            if not animator.isPlaying():
                animator.start()
                sound3D.play()
            return


@autoregister(presentInAllWorlds=True)
class DualGunDualAccuracyHeatManager(CGF.ComponentManager):
    __slots__ = ('__cacheMapping',)

    def __init__(self, *args):
        super(DualGunDualAccuracyHeatManager, self).__init__(*args)
        self.__cacheMapping = {}

    def getAccuracyComponent(self, vehicleID):
        component = self.__cacheMapping.get(vehicleID)
        return None if not component or not component.gameObject or not component.gameObject.isValid() else component

    @onAddedQuery(CGF.GameObject, DualGunDualAccuracyHeatComponent)
    def onAdded(self, gameObject, heatComponent):
        vehicleID = heatComponent.vehicleID or self.__loadVehicleIntoCache(gameObject, heatComponent)
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is None:
            return
        else:
            dualGunDualAccuracy = vehicle.dynamicComponents.get('dualAccuracy')
            if dualGunDualAccuracy is not None:
                dualGunDualAccuracy.onPrefabLoaded()
            return

    def __loadVehicleIntoCache(self, gameObject, heatComponent):
        vehicle = getVehicleFromGO(gameObject, self.spaceID)
        if vehicle is not None:
            heatComponent.vehicleID = vehicle.id
            heatComponent.gameObject = gameObject
            self.__cacheMapping[vehicle.id] = heatComponent
            return vehicle.id
        else:
            return
