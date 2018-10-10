# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/special_sound.py
from collections import namedtuple
import SoundGroups
import nations
from SoundGroups import CREW_GENDER_SWITCHES
from items import tankmen
from items.components.tankmen_components import SPECIAL_VOICE_TAG
_VALKYRIE_SOUND_MODES = {'japan:J29_Nameless': 'valkyrie1',
 'japan:J30_Edelweiss': 'valkyrie2'}
_SpecialVoiceData = namedtuple('_SpecialVoiceData', ['name', 'tag', 'genderSwitch'])
_SPECIAL_VOICES = [_SpecialVoiceData(name='buffon', tag=SPECIAL_VOICE_TAG.BUFFON, genderSwitch=CREW_GENDER_SWITCHES.MALE), _SpecialVoiceData(name='sabaton', tag=SPECIAL_VOICE_TAG.SABATON, genderSwitch=CREW_GENDER_SWITCHES.MALE)]

def _setSpecialVoiceByTankmen(nationID, groupID, isPremium):
    for specialVoice in _SPECIAL_VOICES:
        if tankmen.hasTagInTankmenGroup(nationID, groupID, isPremium, specialVoice.tag):
            SoundGroups.g_instance.setSwitch(CREW_GENDER_SWITCHES.GROUP, specialVoice.genderSwitch)
            SoundGroups.g_instance.soundModes.setMode(specialVoice.name)
            return True

    return False


def setSpecialVoice(crewGroup, vehicleType, isPlayerVehicle):
    groupID, isFemaleCrewCommander, isPremium = tankmen.unpackCrewParams(crewGroup)
    nationID, _ = vehicleType.id
    if _setSpecialVoiceByTankmen(nationID, groupID, isPremium):
        return
    if vehicleType.name in _VALKYRIE_SOUND_MODES and isPlayerVehicle:
        SoundGroups.g_instance.soundModes.setMode(_VALKYRIE_SOUND_MODES[vehicleType.name])
        return
    genderSwitch = CREW_GENDER_SWITCHES.DEFAULT
    if SoundGroups.g_instance.soundModes.currentNationalPreset[1]:
        if isFemaleCrewCommander:
            genderSwitch = CREW_GENDER_SWITCHES.FEMALE
    nation = nations.NAMES[nationID]
    SoundGroups.g_instance.soundModes.setCurrentNation(nation, genderSwitch)
