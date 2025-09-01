# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/visual_script_client/sound_blocks.py
from visual_script.block import Block
from visual_script.dependency import dependencyImporter
from visual_script.misc import EDITOR_TYPE
from visual_script.slot_types import SLOT_TYPE
from visual_script_client.sound_blocks import SoundMeta
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
SoundGroups = dependencyImporter('SoundGroups')

class PlaySoundOnVehicleSoundObject(Block, SoundMeta):
    _TANK_SOUND_OBJ_NAME_TO_INDEX = {'chassis': TankSoundObjectsIndexes.CHASSIS,
     'engine': TankSoundObjectsIndexes.ENGINE,
     'gun': TankSoundObjectsIndexes.GUN}

    def __init__(self, *args, **kwargs):
        super(PlaySoundOnVehicleSoundObject, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._soundObjId = self._makeDataInputSlot('soundObjID', SLOT_TYPE.STR, EDITOR_TYPE.ENUM_SELECTOR)
        self._soundObjId.setEditorData(self._TANK_SOUND_OBJ_NAME_TO_INDEX.keys())
        self._sndName = self._makeDataInputSlot('soundName', SLOT_TYPE.STR)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        vehicle = self._vehicle.getValue()
        if vehicle and vehicle.appearance and vehicle.appearance.engineAudition:
            soundObjectIndex = self._TANK_SOUND_OBJ_NAME_TO_INDEX.get(self._soundObjId.getValue(), None)
            if soundObjectIndex is None:
                soundObjectIndex = TankSoundObjectsIndexes.CHASSIS
            soundObject = vehicle.appearance.engineAudition.getSoundObject(soundObjectIndex)
            if soundObject:
                soundObject.play(self._sndName.getValue())
        self._out.call()
        return
