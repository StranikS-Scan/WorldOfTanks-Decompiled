# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/special_sound_ctrl.py
from collections import namedtuple
import logging
import ResMgr
import SoundGroups
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.options import AltVoicesSetting
from helpers import dependency
from SoundGroups import CREW_GENDER_SWITCHES
from items.components.tankmen_components import SPECIAL_VOICE_TAG
from items.special_crew import isMihoCrewCompleted
from items.vehicles import VehicleDescr
from constants import ITEM_DEFS_PATH, CURRENT_REALM
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import ISpecialSoundCtrl
from gui.battle_control import avatar_getter
from PlayerEvents import g_playerEvents
from vehicle_outfit.outfit import Outfit
from skeletons.gui.battle_session import IBattleSessionProvider
from crew2 import settings_globals
_logger = logging.getLogger(__name__)
_XML_PATH = ITEM_DEFS_PATH + 'special_voices.xml'
_FULL_CREW_CONDITION = 'isFullCrew'
_VoiceoverParams = namedtuple('_VoiceoverParams', ['languageMode', 'genderSwitch', 'onlyInNational'])
_genderStrToSwitch = {'male': CREW_GENDER_SWITCHES.MALE,
 'female': CREW_GENDER_SWITCHES.FEMALE}
_isFullCrewCheckers = {SPECIAL_VOICE_TAG.MIHO: isMihoCrewCompleted}

class SpecialSoundCtrl(ISpecialSoundCtrl):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__voiceoverByVehicle = {}
        self.__voiceoverByInstructor = {}
        self.__voiceoverAdditionalModes = {}
        self.__arenaMusicByStyle = {}
        self.__currentMode = None
        self.__arenaMusicSetup = None
        return

    @property
    def arenaMusicSetup(self):
        if self.__arenaMusicSetup is not None:
            return self.__arenaMusicSetup
        else:
            arena = avatar_getter.getArena()
            return arena.arenaType.wwmusicSetup if arena is not None else None

    @property
    def specialVoice(self):
        return self.__currentMode

    def init(self):
        self.__readSpecialVoices()
        self.__validateInstructorsSpecialVoiceTags()
        g_playerEvents.onAvatarBecomeNonPlayer += self.__onAvatarBecomeNonPlayer

    def fini(self):
        self.__voiceoverByVehicle = None
        self.__voiceoverByInstructor = None
        self.__voiceoverAdditionalModes = None
        self.__arenaMusicByStyle = None
        self.__arenaMusicSetup = None
        self.__currentMode = None
        g_playerEvents.onAvatarBecomeNonPlayer -= self.__onAvatarBecomeNonPlayer
        return

    def setPlayerVehicle(self, vehiclePublicInfo, isPlayerVehicle):
        self.__setVoiceoverByVehicleOrInstructor(vehiclePublicInfo, isPlayerVehicle)
        self.__setArenaMusicByStyle(vehiclePublicInfo, isPlayerVehicle)

    def getSoundModeBySpecialVoice(self, specialVoiceTag):
        if specialVoiceTag in self.__voiceoverByVehicle:
            return self.__voiceoverByVehicle[specialVoiceTag]
        elif specialVoiceTag in self.__voiceoverByInstructor:
            return self.__voiceoverByInstructor[specialVoiceTag]
        else:
            _logger.error('There no sound mode for: %s', specialVoiceTag)
            return None

    def __setVoiceoverByVehicleOrInstructor(self, vehiclePublicInfo, isPlayerVehicle):
        vehicleType = VehicleDescr(vehiclePublicInfo.compDescr).type
        if self.__setSpecialVoiceByVehicle(vehicleType.name, isPlayerVehicle):
            return
        self.__setSpecialVoiceByInstructor(vehiclePublicInfo.instructorVoice, isPlayerVehicle)

    def __setArenaMusicByStyle(self, vehiclePublicInfo, isPlayerVehicle):
        self.__arenaMusicSetup = None
        arena = avatar_getter.getArena()
        if arena is None:
            return
        else:
            arenaVisitor = self.__sessionProvider.arenaVisitor
            if arenaVisitor.bonus.hasRespawns():
                _logger.debug('Skip special arena sound according to game mode')
                return
            if isPlayerVehicle and vehiclePublicInfo.outfit:
                outfit = Outfit(vehiclePublicInfo.outfit, vehicleCD=vehiclePublicInfo.compDescr)
                if outfit.style and outfit.style.tags:
                    for tag, arenaMusic in self.__arenaMusicByStyle.iteritems():
                        if tag in outfit.style.tags:
                            self.__arenaMusicSetup = arena.arenaType.wwmusicSetup.copy()
                            self.__arenaMusicSetup.update(arenaMusic)
                            return

            return

    def __onAvatarBecomeNonPlayer(self):
        self.__arenaMusicSetup = None
        self.__currentMode = None
        return

    def __readSpecialVoices(self):
        rootSection = ResMgr.openSection(_XML_PATH)
        if rootSection is None:
            _logger.error('Could not open special voices xml: %s', _XML_PATH)
            return
        else:
            voiceoverSection = rootSection['voiceover']
            if voiceoverSection is not None:
                for source, paramSection in voiceoverSection.items():
                    tag = paramSection.readString('tag')
                    languageMode = paramSection['languageMode']
                    mode = languageMode.readString(CURRENT_REALM) or languageMode.asString
                    onlyInNational = paramSection.readBool('onlyInNational')
                    genderStr = paramSection.readString('gender')
                    gender = _genderStrToSwitch.get(genderStr, CREW_GENDER_SWITCHES.DEFAULT)
                    additionalModeSection = paramSection['additionalModes']
                    if additionalModeSection is not None:
                        modes = {}
                        for condition, addMode in additionalModeSection.items():
                            modes[condition] = _VoiceoverParams(addMode.asString, gender, onlyInNational)

                        self.__voiceoverAdditionalModes[tag] = modes
                    if source == 'instructor':
                        self.__voiceoverByInstructor[tag] = _VoiceoverParams(mode, gender, onlyInNational)
                    if source == 'vehicle':
                        self.__voiceoverByVehicle[tag] = _VoiceoverParams(mode, gender, onlyInNational)

            arenaMusicSection = rootSection['arenaMusic']
            if arenaMusicSection is not None:
                for source, paramSection in arenaMusicSection.items():
                    if source != 'style':
                        continue
                    tag = paramSection.readString('tag')
                    arenaMusic = {}
                    musicSetupSection = paramSection['wwmusicSetup']
                    if musicSetupSection is not None:
                        for name, value in musicSetupSection.items():
                            arenaMusic[name] = value.asString

                    self.__arenaMusicByStyle[tag] = arenaMusic

            return

    def __validateInstructorsSpecialVoiceTags(self):
        instructorSettings = settings_globals.g_instructorSettingsProvider.instructors
        instructorVoiceovers = {instr.voiceover for instr in instructorSettings.itervalues()}
        instructorVoiceovers.discard(None)
        for specialVoiceTag in instructorVoiceovers:
            if specialVoiceTag not in self.__voiceoverByInstructor and specialVoiceTag not in self.__voiceoverByVehicle:
                _logger.error('There no sound mode for: %s', specialVoiceTag)

        return

    def __setSpecialVoiceByVehicle(self, vehicleName, isPlayerVehicle):
        if isPlayerVehicle:
            params = self.__voiceoverByVehicle.get(vehicleName)
            if params is not None:
                self.__setSpecialVoice(params)
                return True
        return False

    def __setSpecialVoiceByInstructor(self, instructorVoice, isPlayerVehicle):
        if isPlayerVehicle:
            params = self.__voiceoverByInstructor.get(instructorVoice)
            if params is not None:
                self.__setSpecialVoice(params)
                return True
        return False

    def __setSpecialVoice(self, params):
        setting = self.__settingsCore.options.getSetting(settings_constants.SOUND.ALT_VOICES)
        if params.onlyInNational and setting.getSystemModeType() == AltVoicesSetting.SOUND_MODE_TYPE.REGULAR:
            _logger.debug('%s can be used only in national sound mode', params.languageMode)
            return
        if not SoundGroups.g_instance.soundModes.setMode(params.languageMode):
            _logger.warning('Could not set special voice: %s', params.languageMode)
            return
        self.__currentMode = params
        SoundGroups.g_instance.setSwitch(CREW_GENDER_SWITCHES.GROUP, params.genderSwitch)

    def __getSpecialModeForCrew(self, tag, nationID, isPremium, crewGroups):
        if tag not in self.__voiceoverAdditionalModes:
            return None
        else:
            crewChecker = _isFullCrewCheckers.get(tag)
            return self.__voiceoverAdditionalModes[tag].get(_FULL_CREW_CONDITION) if crewChecker is not None and crewChecker(nationID, isPremium, crewGroups) else None
