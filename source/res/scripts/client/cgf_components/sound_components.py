# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/sound_components.py
from cgf_script.component_meta_class import CGFComponent, ComponentProperty, CGFMetaTypes
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
import SoundGroups

class SoundNotification(CGFComponent):
    onEnterNotification = ComponentProperty(type=CGFMetaTypes.STRING, editorName='onEnterNotification', value='')
    onExitNotification = ComponentProperty(type=CGFMetaTypes.STRING, editorName='onExitNotification', value='')
    conditions = ComponentProperty(type=CGFMetaTypes.STRING, editorName='conditions', value='')
    isUnique = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='isUnique', value=False)


class Sound2D(CGFComponent):
    onEnterSound = ComponentProperty(type=CGFMetaTypes.STRING, editorName='onEnterSound', value='')
    onExitSound = ComponentProperty(type=CGFMetaTypes.STRING, editorName='onExitSound', value='')
    conditions = ComponentProperty(type=CGFMetaTypes.STRING, editorName='conditions', value='')


class Sound3D(CGFComponent):
    onEnterSound = ComponentProperty(type=CGFMetaTypes.STRING, editorName='onEnterSound', value='')
    onExitSound = ComponentProperty(type=CGFMetaTypes.STRING, editorName='onExitSound', value='')
    conditions = ComponentProperty(type=CGFMetaTypes.STRING, editorName='conditions', value='')


class VehicleSound(Sound3D):
    _SOUND_OBJ_NAMES_TO_INDEXES = {'chassis': TankSoundObjectsIndexes.CHASSIS,
     'engine': TankSoundObjectsIndexes.ENGINE,
     'gun': TankSoundObjectsIndexes.GUN,
     'hit': TankSoundObjectsIndexes.HIT}
    soundObjectName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='soundObjectName', value='')

    def getSoundObjectIndex(self):
        return self._SOUND_OBJ_NAMES_TO_INDEXES.get(self.soundObjectName)


class VehicleSoundComponent(CGFComponent):

    def __init__(self, parent):
        super(VehicleSoundComponent, self).__init__()
        self.parent = parent
        self.soundObjects = []

    def play(self, event):
        soundObj = SoundGroups.g_instance.getSound3D(self.parent.compoundModel.root, event)
        soundObj.setCallback(lambda s: self.__destroySound(soundObj))
        soundObj.play()
        self.soundObjects.append(soundObj)

    def deactivate(self):
        while self.soundObjects:
            soundObj = self.soundObjects.pop()
            if soundObj.isPlaying:
                soundObj.stop()
            soundObj.releaseMatrix()

    def destroy(self):
        self.parent = None
        return

    def __destroySound(self, soundObj):
        if soundObj in self.soundObjects:
            self.soundObjects.remove(soundObj)
        soundObj.releaseMatrix()
