# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/special_sound.py
from collections import namedtuple
import SoundGroups
import nations
from helpers import dependency
from SoundGroups import CREW_GENDER_SWITCHES
from items import tankmen
from items.components.tankmen_components import SPECIAL_VOICE_TAG
from items.components.crewSkins_constants import NO_CREW_SKIN_ID, NO_CREW_SKIN_SOUND_SET
from skeletons.gui.lobby_context import ILobbyContext
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


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _setSpecialVoiceByCommanderSkinID(isFemale, commanderSkinID, lobbyContext=None):
    if commanderSkinID != NO_CREW_SKIN_ID and lobbyContext.getServerSettings().isCrewSkinsEnabled():
        soundSetID = tankmen.g_cache.crewSkins().skins[commanderSkinID].soundSetID
        if soundSetID != NO_CREW_SKIN_SOUND_SET:
            SoundGroups.g_instance.setSwitch(CREW_GENDER_SWITCHES.GROUP, CREW_GENDER_SWITCHES.GENDER_ALL[isFemale])
            SoundGroups.g_instance.soundModes.setMode(soundSetID)
            return True
    return False


def setSpecialVoice(crewGroup, commanderSkinID, vehicleType, isPlayerVehicle):
    groupID, isFemaleCrewCommander, isPremium = tankmen.unpackCrewParams(crewGroup)
    nationID, _ = vehicleType.id
    if _setSpecialVoiceByCommanderSkinID(isFemaleCrewCommander, commanderSkinID):
        return
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
