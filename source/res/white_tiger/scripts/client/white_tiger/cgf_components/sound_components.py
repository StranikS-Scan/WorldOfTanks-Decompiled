# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/cgf_components/sound_components.py
from __future__ import absolute_import
import logging
import CGF
from cgf_script.registration import ComponentProperty, registerComponent
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
import SoundGroups
_logger = logging.getLogger(__name__)

@registerComponent
class WTSoundNotification(object):
    onEnterNotification = ComponentProperty(type=CGF.PropertyType.String, editorName='onEnterNotification', value='')
    onExitNotification = ComponentProperty(type=CGF.PropertyType.String, editorName='onExitNotification', value='')
    conditions = ComponentProperty(type=CGF.PropertyType.String, editorName='conditions', value='')
    isUnique = ComponentProperty(type=CGF.PropertyType.Bool, editorName='isUnique', value=False)
    onlyForPlayerVehicle = ComponentProperty(type=CGF.PropertyType.Bool, editorName='onlyForPlayerVehicle', value=False)


@registerComponent
class WTConditionalSound2D(object):
    onEnterSound = ComponentProperty(type=CGF.PropertyType.String, editorName='onEnterSound', value='')
    onExitSound = ComponentProperty(type=CGF.PropertyType.String, editorName='onExitSound', value='')
    conditions = ComponentProperty(type=CGF.PropertyType.String, editorName='conditions', value='')


@registerComponent
class WTConditionalSound3D(object):
    onEnterSound = ComponentProperty(type=CGF.PropertyType.String, editorName='onEnterSound', value='')
    onExitSound = ComponentProperty(type=CGF.PropertyType.String, editorName='onExitSound', value='')
    conditions = ComponentProperty(type=CGF.PropertyType.String, editorName='conditions', value='')


@registerComponent
class WTVehicleSound(WTConditionalSound3D):
    _SOUND_OBJ_NAMES_TO_INDEXES = {'chassis': TankSoundObjectsIndexes.CHASSIS,
     'engine': TankSoundObjectsIndexes.ENGINE,
     'gun': TankSoundObjectsIndexes.GUN,
     'hit': TankSoundObjectsIndexes.HIT}
    onEnterSoundNPC = ComponentProperty(type=CGF.PropertyType.String, editorName='onEnterSoundNPC', value='')
    onExitSoundNPC = ComponentProperty(type=CGF.PropertyType.String, editorName='onExitSoundNPC', value='')
    soundObjectName = ComponentProperty(type=CGF.PropertyType.String, editorName='soundObjectName', value='')
    useNPCEvents = ComponentProperty(type=CGF.PropertyType.Bool, editorName='useNPCEvents', value=False)

    def getSoundObjectIndex(self):
        return self._SOUND_OBJ_NAMES_TO_INDEXES.get(self.soundObjectName)

    def __init__(self):
        self.vehicle = None
        return


@registerComponent
class WTVehicleSoundComponent(object):

    def __init__(self, parent):
        super(WTVehicleSoundComponent, self).__init__()
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
