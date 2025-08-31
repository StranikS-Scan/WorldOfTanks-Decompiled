# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/sound_components.py
import logging
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
import SoundGroups
_logger = logging.getLogger(__name__)

@registerComponent
class SoundNotification(object):
    onEnterNotification = ComponentProperty(type=CGFMetaTypes.STRING, editorName='onEnterNotification', value='')
    onExitNotification = ComponentProperty(type=CGFMetaTypes.STRING, editorName='onExitNotification', value='')
    conditions = ComponentProperty(type=CGFMetaTypes.STRING, editorName='conditions', value='')
    isUnique = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='isUnique', value=False)
    onlyForPlayerVehicle = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='onlyForPlayerVehicle', value=False)


@registerComponent
class ConditionalSound2D(object):
    onEnterSound = ComponentProperty(type=CGFMetaTypes.STRING, editorName='onEnterSound', value='')
    onExitSound = ComponentProperty(type=CGFMetaTypes.STRING, editorName='onExitSound', value='')
    conditions = ComponentProperty(type=CGFMetaTypes.STRING, editorName='conditions', value='')


@registerComponent
class ConditionalSound3D(object):
    onEnterSound = ComponentProperty(type=CGFMetaTypes.STRING, editorName='onEnterSound', value='')
    onExitSound = ComponentProperty(type=CGFMetaTypes.STRING, editorName='onExitSound', value='')
    conditions = ComponentProperty(type=CGFMetaTypes.STRING, editorName='conditions', value='')


@registerComponent
class VehicleSound(ConditionalSound3D):
    _SOUND_OBJ_NAMES_TO_INDEXES = {'chassis': TankSoundObjectsIndexes.CHASSIS,
     'engine': TankSoundObjectsIndexes.ENGINE,
     'gun': TankSoundObjectsIndexes.GUN,
     'hit': TankSoundObjectsIndexes.HIT}
    onEnterSoundNPC = ComponentProperty(type=CGFMetaTypes.STRING, editorName='onEnterSoundNPC', value='')
    onExitSoundNPC = ComponentProperty(type=CGFMetaTypes.STRING, editorName='onExitSoundNPC', value='')
    soundObjectName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='soundObjectName', value='')
    useNPCEvents = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='useNPCEvents', value=False)

    def getSoundObjectIndex(self):
        return self._SOUND_OBJ_NAMES_TO_INDEXES.get(self.soundObjectName)


@registerComponent
class VehicleSoundComponent(object):

    def __init__(self, parent):
        super(VehicleSoundComponent, self).__init__()
        self.parent = parent
        self.soundObjects = []
        self.__matrix = parent.matrix
        self.__soundObjectName = self.__getSoundObjectName(parent.isPlayerVehicle, parent.id)
        self.__soundObject = None
        return

    def play(self, event):
        if self.__soundObject:
            self.__soundObject.play(event)
        else:
            self.__soundObject = self.__createSoundObject()
            if self.__soundObject:
                self.__soundObject.play(event)
            else:
                _logger.warning('SoundOjbect is not valid!')

    def setRTPC(self, nameRTPC, value):
        if self.__soundObject:
            self.__soundObject.setRTPC(nameRTPC, value)
        else:
            _logger.warning('SoundOjbect is not valid!')

    def deactivate(self):
        if self.__soundObject:
            self.__soundObject.stopAll()
        while self.soundObjects:
            soundObj = self.soundObjects.pop()
            if soundObj.isPlaying:
                soundObj.stop()
            soundObj.releaseMatrix()

    def destroy(self):
        if self.__soundObject:
            self.__soundObject.stopAll()
        self.__soundObject = None
        self.parent = None
        return

    def __getSoundObjectName(self, isPlayerVehicle, id):
        soundObjectName = 'VehicleSoundComponent_NPC_'
        if isPlayerVehicle:
            soundObjectName = 'VehicleSoundComponent_PC_'
        soundObjectName += str(id)
        return soundObjectName

    def __createSoundObject(self):
        return SoundGroups.g_instance.WWgetSoundObject(self.__soundObjectName, self.__matrix)

    def __destroySound(self, soundObj):
        if soundObj in self.soundObjects:
            self.soundObjects.remove(soundObj)
        soundObj.releaseMatrix()
