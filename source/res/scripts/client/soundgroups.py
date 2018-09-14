# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SoundGroups.py
import BigWorld
import WWISE
import Event
import Settings
import ResMgr
import constants
import PlayerEvents
import MusicControllerWWISE
from ReplayEvents import g_replayEvents
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_CURRENT_EXCEPTION, LOG_DEBUG
from helpers import i18n
from constants import ARENA_PERIOD
from vehicle_systems.tankStructure import TankPartNames
ENABLE_LS = True
ENABLE_ENGINE_N_TRACKS = True
DEBUG_TRACE_SOUND = False
DEBUG_TRACE_STACK = False
DEBUG_TRACE_EFFECTLIST = False
g_instance = None
DSP_LOWPASS_LOW = 7000
DSP_LOWPASS_HI = 20000
DSP_SEEKSPEED = 200000
SOUND_ENABLE_STATUS_DEFAULT = 0
SOUND_ENABLE_STATUS_VALUES = range(3)
_arenaPeriodState = {ARENA_PERIOD.WAITING: 'STATE_arenastate_waiting',
 ARENA_PERIOD.PREBATTLE: 'STATE_arenastate_counter',
 ARENA_PERIOD.BATTLE: 'STATE_arenastate_battle'}
_envStateDefs = {'login': ('ue_01_loginscreen_enter', 'ue_01_loginscreen_exit', 0),
 'lobby': ('ue_02_hangar_enter', 'ue_02_hangar_exit', 1),
 'queue': ('ue_03_lobby_enter', 'ue_03_lobby_exit', 0),
 'battleLoading': ('ue_04_loadingscreen_enter', 'ue_04_loadingscreen_exit', 0),
 'battle': ('ue_05_arena_enter', 'ue_05_arena_exit', 0),
 'battleResults': ('ue_06_result_enter', 'ue_06_result_exit', 0)}

class CREW_GENDER_SWITCHES(object):
    GROUP = 'SWITCH_ext_vo_gender'
    MALE = 'SWITCH_ext_vo_gender_male'
    FEMALE = 'SWITCH_ext_vo_gender_female'
    DEFAULT = MALE
    GENDER_ALL = (MALE, FEMALE)


class SoundModes():
    __MODES_FOLDER = 'gui/soundModes/'
    __MODES_FILENAME = 'main_sound_modes.xml'
    DEFAULT_MODE_NAME = 'default'
    DEFAULT_NATION = 'default'
    MEDIA_PATH = None

    class SoundModeDesc(object):

        def __init__(self, dataSection):
            self.name = dataSection.readString('name', 'default')
            self.voiceLanguage = dataSection.readString('wwise_language', '')
            descriptionLink = dataSection.readString('description', '')
            self.description = i18n.makeString(descriptionLink)
            self.invisible = dataSection.readBool('invisible', False)
            self.wwbanksToBeLoaded = []
            self.__isValid = None
            wwbanksSec = dataSection['wwbanks']
            if wwbanksSec is not None:
                for bank in wwbanksSec.values():
                    bankName = bank.asString
                    manualPath = bank.readString('filePath', '')
                    self.wwbanksToBeLoaded.append((bankName, manualPath))

            return

        def getIsValid(self, soundModes):
            if self.__isValid is None:
                self.__isValid = self.__validate(soundModes)
            return self.__isValid

        def __validate(self, soundModes):
            prevMode = soundModes.currentMode
            for soundBankName, soundPath in self.wwbanksToBeLoaded:
                pathToCheck = soundPath if soundPath != '' else '%s/%s' % (SoundModes.MEDIA_PATH, soundBankName)
                if not ResMgr.isFile(pathToCheck):
                    return False

            result = soundModes.setMode(self.name)
            soundModes.setMode(prevMode)
            return result

        def __repr__(self):
            return 'SoundModeDesc<name=%s; lang=%s; visible=%s>' % (self.name, self.voiceLanguage, not self.invisible)

        def __cmp__(self, other):
            if not isinstance(other, SoundModes.SoundModeDesc):
                return -1
            if self.name == 'default':
                return -1
            return 1 if other.name == 'default' else 1

    class NationalPresetDesc(object):

        def __init__(self, dataSection):
            self.name = dataSection.readString('name', 'default')
            descriptionLink = dataSection.readString('description', '')
            self.description = i18n.makeString(descriptionLink)
            self.mapping = {}
            for nationSec in (dataSection['nations'] or {}).values():
                nationName = nationSec.readString('name', 'default')
                soundMode = nationSec.readString('soundMode', 'default')
                self.mapping[nationName] = soundMode

        def __repr__(self):
            return 'NationalPresetDesc<name=%s>' % self.name

    modes = property(lambda self: self.__modes)
    nationalPresets = property(lambda self: self.__nationalPresets)
    currentMode = property(lambda self: self.__currentMode)
    currentNationalPreset = property(lambda self: self.__currentNationalPreset)
    nationToSoundModeMapping = property(lambda self: self.__nationToSoundModeMapping)

    def __init__(self, initialModeName):
        if SoundModes.MEDIA_PATH is None:
            engineConfig = ResMgr.openSection('engine_config.xml')
            if engineConfig is not None:
                SoundModes.MEDIA_PATH = engineConfig.readString('soundMgr/mediaPath', 'audioww')
            else:
                SoundModes.MEDIA_PATH = 'audioww'
        self.__modes = {}
        self.__currentMode = SoundModes.DEFAULT_MODE_NAME
        self.__nationalPresets = {}
        self.__nationToSoundModeMapping = {'default': SoundModes.DEFAULT_MODE_NAME}
        self.__currentNationalPreset = (SoundModes.DEFAULT_MODE_NAME, False)
        self.modifiedSoundGroups = []
        modesSettingsSection = ResMgr.openSection(SoundModes.__MODES_FOLDER + SoundModes.__MODES_FILENAME)
        if modesSettingsSection is None:
            LOG_ERROR('%s is not found' % SoundModes.__MODES_FILENAME)
            return
        else:
            soundModes, nationalPresets = self.__readSoundModesConfig(modesSettingsSection, self.__nationalPresets)
            self.__modes = dict(((soundMode.name, soundMode) for soundMode in soundModes))
            self.__nationalPresets = dict(((preset.name, preset) for preset in nationalPresets))
            if SoundModes.DEFAULT_MODE_NAME not in self.__modes:
                LOG_ERROR('Default sound mode is not found!')
            modifiedSoundGroupsSection = modesSettingsSection['modified_sound_groups']
            if modifiedSoundGroupsSection is not None:
                self.modifiedSoundGroups = modifiedSoundGroupsSection.readStrings('sound_group')
            folderSection = ResMgr.openSection(SoundModes.__MODES_FOLDER)
            if folderSection is None:
                LOG_ERROR("Folder for SoundModes: '%s' is not found!" % SoundModes.__MODES_FOLDER)
            else:
                defaultNationalPresets = dict(self.__nationalPresets)
                for modesConfigSection in folderSection.values():
                    if modesConfigSection.name != SoundModes.__MODES_FILENAME:
                        soundModes, nationalPresets = self.__readSoundModesConfig(modesConfigSection, defaultNationalPresets)
                        for mode in soundModes:
                            if self.__modes.has_key(mode.name):
                                LOG_WARNING("%s config tries to redefine soundMode '%s', ignored" % (modesConfigSection.name, mode.name))
                            self.__modes[mode.name] = mode

                        for preset in nationalPresets:
                            if self.__nationalPresets.has_key(preset.name):
                                LOG_WARNING("%s config tries to redefine nationalPreset '%s', ignored" % (preset.name, preset.name))
                            self.__nationalPresets[preset.name] = preset

            self.setMode(initialModeName)
            return

    def __readSoundModesConfig(self, rootSection, mainNationalPresets):
        soundModes = []
        modesSection = rootSection['modes']
        if modesSection is not None:
            for modeSec in modesSection.values():
                if modeSec.name == 'mode':
                    soundModes.append(SoundModes.SoundModeDesc(modeSec))

        nationalPresetsSection = rootSection['nationalPresets']
        nationalPresets = self.__readNationalPresets(nationalPresetsSection or {})
        overridesSection = rootSection['nationalPresetsOverrides']
        overrides = self.__readNationalPresets(overridesSection or {})
        for overridePreset in overrides:
            nationalPresetToOverride = mainNationalPresets.get(overridePreset.name)
            if nationalPresetToOverride is not None:
                for nationName, soundMode in overridePreset.mapping.iteritems():
                    nationalPresetToOverride.mapping[nationName] = soundMode

            LOG_WARNING("Failed to override nationalPreset '%s'" % overridePreset.name)

        return (soundModes, nationalPresets)

    def __readNationalPresets(self, rootSection):
        for nationalPresetSec in rootSection.values():
            if nationalPresetSec.name == 'preset':
                yield SoundModes.NationalPresetDesc(nationalPresetSec)

    def setMode(self, modeName):
        languageSet = False
        try:
            languageSet = self.__setMode(modeName)
        except:
            LOG_CURRENT_EXCEPTION()

        if not languageSet:
            defaultVoiceLanguage = ''
            if SoundModes.DEFAULT_MODE_NAME in self.__modes:
                defaultVoiceLanguage = self.__modes[SoundModes.DEFAULT_MODE_NAME].voiceLanguage
            try:
                WWISE.setLanguage(defaultVoiceLanguage)
            except:
                LOG_CURRENT_EXCEPTION()

            self.__currentMode = SoundModes.DEFAULT_MODE_NAME
        return languageSet

    def __setMode(self, modeName):
        if modeName not in self.__modes:
            LOG_DEBUG('Sound mode %s does not exist' % modeName)
            return False
        if self.__currentMode == modeName:
            return True
        self.__currentMode = modeName
        modeDesc = self.__modes[modeName]
        languageSet = WWISE.setLanguage(modeDesc.voiceLanguage)
        if not languageSet:
            LOG_WARNING('Sound: Internal WWISE error in WWISE::setLanguage')
            return False
        return True

    def setCurrentNation(self, nation, genderSwitch=CREW_GENDER_SWITCHES.DEFAULT):
        if g_instance is not None:
            g_instance.setSwitch(CREW_GENDER_SWITCHES.GROUP, genderSwitch)
        arena = getattr(BigWorld.player(), 'arena', None)
        inTutorial = arena is not None and arena.guiType is constants.ARENA_GUI_TYPE.TUTORIAL
        if inTutorial:
            self.setMode(SoundModes.DEFAULT_MODE_NAME)
            return
        else:
            nationToQueue = nation
            if nation not in self.__nationToSoundModeMapping:
                nationToQueue = SoundModes.DEFAULT_NATION
            soundMode = self.__nationToSoundModeMapping.get(nationToQueue)
            success = soundMode is not None and self.setMode(soundMode)
            if not success:
                self.setNationalMappingByMode(SoundModes.DEFAULT_MODE_NAME)
            return success

    def setNationalMapping(self, nationToSoundModeMapping):
        for soundModeName in nationToSoundModeMapping.itervalues():
            soundModeDesc = self.__modes.get(soundModeName)
            if soundModeDesc is None:
                LOG_WARNING("SoundMode '%s' is not found" % soundModeName)
                return False
            if not soundModeDesc.getIsValid(self):
                LOG_WARNING("SoundMode '%s' has invalid banks" % soundModeName)
                return False

        self.__nationToSoundModeMapping = nationToSoundModeMapping
        self.__currentNationalPreset = None
        return True

    def setNationalMappingByMode(self, soundMode):
        if soundMode not in self.__modes:
            return False
        success = self.setNationalMapping({'default': soundMode})
        if not success:
            return False
        self.__currentNationalPreset = (soundMode, False)
        return True

    def setNationalMappingByPreset(self, presetName):
        preset = self.__nationalPresets.get(presetName)
        if preset is None:
            return False
        else:
            success = self.setNationalMapping(preset.mapping)
            if not success:
                return False
            self.__currentNationalPreset = (presetName, True)
            return True


class SoundGroups(object):
    soundModes = property(lambda self: self.__soundModes)
    onVolumeChanged = Event.Event()
    onMusicVolumeChanged = Event.Event()

    def __init__(self):
        self.__enableStatus = SOUND_ENABLE_STATUS_DEFAULT
        self.__volumeByCategory = {}
        self.__masterVolume = 1.0
        self.__isWindowVisible = BigWorld.isWindowVisible()
        self.__handleInside = None
        self.__handleOutside = None
        self.__activeStinger = None
        self.__activeTrack = None
        self.__activeStingerPriority = None
        self.__muffled = False
        self.__muffledByReplay = False
        self.__states = []
        from gui.app_loader import g_appLoader
        self.__spaceID = g_appLoader.getSpaceID()
        PlayerEvents.g_playerEvents.onAvatarReady += self.onAvatarReady
        self.__categories = {'vehicles': ('outside/vehicles', 'vehicles'),
         'effects': ('hits', 'outside/hits', 'inside/weapons', 'outside/weapons', 'outside/environment', 'battle_gui'),
         'gui': ('gui', 'ingame_voice'),
         'music': ('music',),
         'ambient': ('outside/ambient', 'hangar_v2', 'ambientUR'),
         'masterVivox': (),
         'micVivox': (),
         'masterFadeVivox': ()}
        defMasterVolume = 0.5
        defCategoryVolumes = {'music': 0.5,
         'masterVivox': 0.7,
         'micVivox': 0.4}
        userPrefs = Settings.g_instance.userPrefs
        soundModeName = SoundModes.DEFAULT_MODE_NAME
        nationalMapping = None
        self.__soundModes = None
        if not userPrefs.has_key(Settings.KEY_SOUND_PREFERENCES):
            userPrefs.write(Settings.KEY_SOUND_PREFERENCES, '')
            self.__masterVolume = defMasterVolume
            for categoryName in self.__categories.iterkeys():
                self.__volumeByCategory[categoryName] = defCategoryVolumes.get(categoryName, 1.0)

            self.savePreferences()
        else:
            ds = userPrefs[Settings.KEY_SOUND_PREFERENCES]
            self.__enableStatus = ds.readInt('enable', SOUND_ENABLE_STATUS_DEFAULT)
            self.__masterVolume = ds.readFloat('masterVolume', defMasterVolume)
            self.__volumeByCategory['music_hangar'] = ds.readFloat('volume_music_hangar', 1.0)
            self.__volumeByCategory['voice'] = ds.readFloat('volume_voice', 1.0)
            self.__volumeByCategory['ev_ambient'] = ds.readFloat('volume_ev_ambient', 0.8)
            self.__volumeByCategory['ev_effects'] = ds.readFloat('volume_ev_effects', 0.8)
            self.__volumeByCategory['ev_gui'] = ds.readFloat('volume_ev_gui', 0.8)
            self.__volumeByCategory['ev_music'] = ds.readFloat('volume_ev_music', 0.8)
            self.__volumeByCategory['ev_vehicles'] = ds.readFloat('volume_ev_vehicles', 0.8)
            self.__volumeByCategory['ev_voice'] = ds.readFloat('volume_ev_voice', 0.8)
            for categoryName in self.__categories.iterkeys():
                volume = ds.readFloat('volume_' + categoryName, defCategoryVolumes.get(categoryName, 1.0))
                self.__volumeByCategory[categoryName] = volume

            soundModeSec = ds['soundMode']
            if soundModeSec is not None:
                soundModeName = soundModeSec.asString
                if soundModeName == '':
                    soundModeName = SoundModes.DEFAULT_MODE_NAME
                    if ds['soundMode'].has_key('nationalPreset'):
                        nationalMapping = ds.readString('soundMode/nationalPreset', '')
                    else:
                        nationsSec = soundModeSec['nations']
                        if nationsSec is not None:
                            nationalMapping = {}
                            for nation, sec in nationsSec.items():
                                nationalMapping[nation] = sec.asString

        self.__soundModes = SoundModes(SoundModes.DEFAULT_MODE_NAME)
        if isinstance(nationalMapping, str):
            self.__soundModes.setNationalMappingByPreset(nationalMapping)
        elif isinstance(nationalMapping, dict):
            self.__soundModes.setNationalMapping(nationalMapping)
        else:
            self.__soundModes.setNationalMappingByMode(soundModeName)
        self.applyPreferences()
        self.__muteCallbackID = BigWorld.callback(0.25, self.__muteByWindowVisibility)
        g_replayEvents.onMuteSound += self.__onReplayMute
        g_appLoader.onGUISpaceEntered += self.__onGUISpaceEntered
        return

    def __del__(self):
        LOG_DEBUG('Deleted: %s' % self)

    def destroy(self):
        self.onVolumeChanged.clear()
        self.onMusicVolumeChanged.clear()
        PlayerEvents.g_playerEvents.onAvatarReady -= self.onAvatarReady
        g_replayEvents.onMuteSound -= self.__onReplayMute
        from gui.app_loader import g_appLoader
        g_appLoader.onGUISpaceEntered -= self.__onGUISpaceEntered
        player = BigWorld.player()
        if player is not None and player.inputHandler is not None:
            player.inputHandler.onCameraChanged -= self.__onCameraChanged
        self.onVolumeChanged.clear()
        if self.__muteCallbackID is not None:
            BigWorld.cancelCallback(self.__muteCallbackID)
            self.__muteCallbackID = None
        return

    def enableLobbySounds(self, enable):
        for categoryName in ('ambient', 'gui'):
            volume = 0.0 if not enable else self.__volumeByCategory[categoryName]
            self.setVolume(categoryName, volume, False)

    def enableArenaSounds(self, enable):
        for categoryName in ('vehicles', 'effects', 'ambient'):
            enable = enable and not self.__muffledByReplay
            volume = 0.0 if not enable else self.__volumeByCategory[categoryName]
            self.setVolume(categoryName, volume, False)

        volume = 0.0 if not enable else self.__volumeByCategory['gui']
        self.setVolume('gui', volume, False)

    def enableAmbientAndMusic(self, enable):
        for categoryName in ('ambient', 'music'):
            enable = enable and not self.__muffledByReplay
            volume = 0.0 if not enable else self.__volumeByCategory[categoryName]
            self.setVolume(categoryName, volume, False)

    def enableVoiceSounds(self, enable):
        for categoryName in ('gui',):
            volume = 0.0 if not enable else self.__volumeByCategory[categoryName]
            self.setVolume(categoryName, volume, False)

    def __onReplayMute(self, mute):
        self.__muffledByReplay = mute
        for categoryName in ('vehicles', 'effects', 'ambient', 'gui'):
            volume = 0.0 if mute else self.__volumeByCategory[categoryName]
            self.setVolume(categoryName, volume, False)

    def __onGUISpaceEntered(self, spaceID):
        from gui.app_loader.settings import GUI_GLOBAL_SPACE_ID
        if WWISE.enabled:
            if spaceID == GUI_GLOBAL_SPACE_ID.LOGIN:
                WWISE.WG_loadLogin()
        if spaceID == GUI_GLOBAL_SPACE_ID.BATTLE:
            BigWorld.player().arena.onPeriodChange += self.__arenaPeriodChanged
        elif self.__spaceID == GUI_GLOBAL_SPACE_ID.BATTLE:
            BigWorld.player().arena.onPeriodChange -= self.__arenaPeriodChanged
        self.__spaceID = spaceID

    def __arenaPeriodChanged(self, *args):
        period = BigWorld.player().arena.period
        state = _arenaPeriodState.get(period, None)
        if state is not None:
            WWISE.WW_setState('STATE_arenastate', state)
        return

    def onEnvStart(self, environment):
        state = _envStateDefs.get(environment, None)
        if state is not None:
            if len(self.__states) > 0:
                prev = self.__states[-1]
                prevState = _envStateDefs[prev]
                if not prevState[2]:
                    LOG_DEBUG('Set UE state: %s' % prevState[1])
                    WWISE.WW_eventGlobalSync(prevState[1])
            LOG_DEBUG('Set UE state: %s' % state[0])
            WWISE.WW_eventGlobalSync(state[0])
            self.__states.append(environment)
        return

    def onEnvStop(self, environment):
        for i in xrange(len(self.__states) - 1, -1, -1):
            if environment == self.__states[i]:
                if i == len(self.__states) - 1:
                    prevState = _envStateDefs[environment]
                    LOG_DEBUG('Set UE state: %s' % prevState[1])
                    WWISE.WW_eventGlobalSync(prevState[1])
                del self.__states[i]
                if len(self.__states) > 0:
                    prev = self.__states[-1]
                    prevState = _envStateDefs[prev]
                    if not prevState[2]:
                        LOG_DEBUG('Set UE state: %s' % prevState[0])
                        WWISE.WW_eventGlobalSync(prevState[0])

    def setMasterVolume(self, volume):
        self.__masterVolume = volume
        self.__muffledVolume = self.__masterVolume * self.getVolume('masterFadeVivox')
        masterVolume = self.__muffledVolume if self.__muffled else self.__masterVolume
        self.savePreferences()
        WWISE.WW_setMasterVolume(masterVolume)
        self.onMusicVolumeChanged('music', self.__masterVolume, self.getVolume('music'))
        self.onMusicVolumeChanged('ambient', self.__masterVolume, self.getVolume('ambient'))

    def getMasterVolume(self):
        return self.__masterVolume

    def getEnableStatus(self):
        return self.__enableStatus

    def setEnableStatus(self, status):
        assert status in SOUND_ENABLE_STATUS_VALUES
        self.__enableStatus = status
        self.savePreferences()

    def setVolume(self, categoryName, volume, updatePrefs=True):
        WWISE.WW_setRTCPGlobal('RTPC_ext_menu_volume_{}'.format(categoryName), volume * 100.0)
        if updatePrefs:
            self.__volumeByCategory[categoryName] = volume
            self.savePreferences()
        if categoryName == 'music' or categoryName == 'ambient':
            self.onMusicVolumeChanged(categoryName, self.__masterVolume, self.getVolume(categoryName))
        self.onVolumeChanged(categoryName, volume)

    def getVolume(self, categoryName):
        return self.__volumeByCategory[categoryName]

    def savePreferences(self):
        ds = Settings.g_instance.userPrefs[Settings.KEY_SOUND_PREFERENCES]
        ds.writeFloat('masterVolume', self.__masterVolume)
        for categoryName in self.__volumeByCategory.iterkeys():
            ds.writeFloat('volume_' + categoryName, self.__volumeByCategory[categoryName])

        ds.writeInt('enable', self.__enableStatus)
        soundModeName = SoundModes.DEFAULT_MODE_NAME if self.__soundModes is None else self.__soundModes.currentMode
        ds.deleteSection('soundMode')
        if self.__soundModes is None:
            ds.writeString('soundMode', soundModeName)
        else:
            curPresetIsNationalPreset = self.__soundModes.currentNationalPreset
            soundModeSection = ds.createSection('soundMode')
            if curPresetIsNationalPreset is None:
                nationsSection = soundModeSection.createSection('nations')
                mapping = self.__soundModes.nationToSoundModeMapping
                for nation, mode in mapping.iteritems():
                    nationsSection.writeString(nation, mode)

            elif curPresetIsNationalPreset[1]:
                soundModeSection.writeString('nationalPreset', curPresetIsNationalPreset[0])
            else:
                ds.writeString('soundMode', curPresetIsNationalPreset[0])
        return

    def applyPreferences(self):
        if not self.__isWindowVisible:
            WWISE.WW_setMasterVolume(0.0)
            return
        self.setMasterVolume(self.__masterVolume)
        for categoryName in self.__volumeByCategory.iterkeys():
            newVolume = self.__volumeByCategory[categoryName]
            if self.__muffledByReplay and categoryName in ('vehicles', 'effects', 'ambient'):
                newVolume = 0.0
            self.setVolume(categoryName, newVolume, updatePrefs=False)

    def muffleWWISEVolume(self):
        if not self.__muffled:
            self.__muffled = True
            self.applyPreferences()

    def restoreWWISEVolume(self):
        self.__muffled = False
        self.applyPreferences()

    def __muteByWindowVisibility(self):
        isWindowVisible = BigWorld.isWindowVisible()
        if self.__isWindowVisible != isWindowVisible:
            self.__isWindowVisible = isWindowVisible
            self.applyPreferences()
        self.__muteCallbackID = BigWorld.callback(0.25, self.__muteByWindowVisibility)

    def onAvatarReady(self):
        BigWorld.player().inputHandler.onCameraChanged += self.__onCameraChanged
        PlayerEvents.g_playerEvents.onAvatarReady -= self.onAvatarReady
        self.changePlayMode(0)

    def __onCameraChanged(self, cameraName, currentVehicleId=None):
        if cameraName != 'postmortem':
            return
        else:
            playerVehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
            if playerVehicle is not None and playerVehicle.isAlive():
                return
            if currentVehicleId is None:
                return
            self.changePlayMode(0)
            return

    def unloadAll(self):
        MusicControllerWWISE.destroy()

    def preloadSoundGroups(self, arenaName):
        from Account import PlayerAccount
        isHangar = isinstance(BigWorld.player(), PlayerAccount)
        if isHangar:
            WWISE.WG_loadHangar()
        else:
            WWISE.WG_unloadHangar()
        MusicControllerWWISE.init(arenaName)

    def getSound3D(self, node, event):
        if DEBUG_TRACE_SOUND is True:
            LOG_DEBUG('SOUND: getSound3D', event, node)
        if DEBUG_TRACE_STACK is True:
            import traceback
            traceback.print_stack()
        return self.WWgetSound(event, event + ' : ' + str(node), node)

    def playSound3D(self, node, event):
        if DEBUG_TRACE_SOUND is True:
            LOG_DEBUG('SOUND: playSound3D', event, node)
        if DEBUG_TRACE_STACK is True:
            import traceback
            traceback.print_stack()
        s = self.WWgetSound(event, event + ' : ' + str(node), node)
        if s is not None:
            s.play()
        return

    def getSound2D(self, event):
        if DEBUG_TRACE_SOUND is True:
            LOG_DEBUG('SOUND: getSound2D', event)
        if DEBUG_TRACE_STACK is True:
            import traceback
            traceback.print_stack()
        return self.WWgetSound(event, None, None)

    def playSound2D(self, event):
        if DEBUG_TRACE_SOUND is True:
            LOG_DEBUG('SOUND: playSound2D', event)
        if DEBUG_TRACE_STACK is True:
            import traceback
            traceback.print_stack()
        return WWISE.WW_eventGlobal(event)

    def playSoundPos(self, event, pos):
        if DEBUG_TRACE_SOUND is True:
            LOG_DEBUG('SOUND: playSoundPos', event, pos)
        if DEBUG_TRACE_STACK is True:
            import traceback
            traceback.print_stack()
        return WWISE.WW_eventGlobalPos(event, pos)

    def playCameraOriented(self, event, pos):
        if DEBUG_TRACE_SOUND is True:
            LOG_DEBUG('SOUND: playCameraOriented', event)
        if DEBUG_TRACE_STACK is True:
            import traceback
            traceback.print_stack()
        WWISE.WW_playCameraOriented(event, pos)

    def getCameraOriented(self, event, pos):
        if DEBUG_TRACE_SOUND is True:
            LOG_DEBUG('SOUND: playCameraOriented', event)
        if DEBUG_TRACE_STACK is True:
            import traceback
            traceback.print_stack()
        return WWISE.WW_getCameraOriented(event, pos)

    def WWgetSoundObject(self, objectName, matrix, local=(0.0, 0.0, 0.0), auxSend=False):
        if DEBUG_TRACE_SOUND is True:
            LOG_DEBUG('SOUND: WWgetSoundObject', objectName, matrix, local)
        if DEBUG_TRACE_STACK is True:
            import traceback
            traceback.print_stack()
        return WWISE.WW_getSoundObject(objectName, matrix, local, auxSend)

    def WWgetSound(self, eventName, objectName, matrix, local=(0.0, 0.0, 0.0)):
        if DEBUG_TRACE_SOUND is True:
            LOG_DEBUG('SOUND: WWgetSound', eventName, objectName, matrix, local)
        if DEBUG_TRACE_STACK is True:
            import traceback
            traceback.print_stack()
        return WWISE.WW_getSound(eventName, objectName, matrix, local)

    def WWgetSoundCallback(self, eventName, objectName, matrix, callback):
        if DEBUG_TRACE_SOUND is True:
            LOG_DEBUG('SOUND: WWgetSoundCallback', eventName, objectName, matrix, callback)
        if DEBUG_TRACE_STACK is True:
            import traceback
            traceback.print_stack()
        return WWISE.WW_getSoundCallback(eventName, objectName, matrix, callback)

    def WWgetSoundPos(self, eventName, objectName, position):
        if DEBUG_TRACE_SOUND is True:
            LOG_DEBUG('SOUND: WWgetSoundPos', eventName, objectName, position)
        if DEBUG_TRACE_STACK is True:
            import traceback
            traceback.print_stack()
        return WWISE.WW_getSoundPos(eventName, objectName, position)

    def changePlayMode(self, mode):
        __ceilLess = None
        if BigWorld.player().getVehicleAttached() is not None:
            vehicleTypeDescriptor = BigWorld.player().getVehicleAttached().typeDescriptor
        else:
            vehicleTypeDescriptor = BigWorld.player().vehicleTypeDescriptor
        if vehicleTypeDescriptor is not None:
            __ceilLess = vehicleTypeDescriptor.turret['ceilless']
        if mode == 0:
            WWISE.WW_setRTCPGlobal('RTPC_ext_viewPlayMode', 1)
            if __ceilLess is True:
                WWISE.WW_setState('STATE_viewPlayMode', 'STATE_viewplaymode_arcade_ceilless')
            else:
                WWISE.WW_setState('STATE_viewPlayMode', 'STATE_viewPlayMode_arcade')
            WWISE.WWsetCameraShift(None)
        elif mode == 1:
            WWISE.WW_setRTCPGlobal('RTPC_ext_viewPlayMode', 0)
            if __ceilLess is True:
                WWISE.WW_setState('STATE_viewPlayMode', 'STATE_viewplaymode_sniper_ceilless')
            else:
                WWISE.WW_setState('STATE_viewPlayMode', 'STATE_viewPlayMode_sniper')
            if BigWorld.player().getVehicleAttached() is not None:
                compoundModel = BigWorld.player().getVehicleAttached().appearance.compoundModel
                WWISE.WWsetCameraShift(compoundModel.node(TankPartNames.TURRET))
        elif mode == 2:
            WWISE.WW_setRTCPGlobal('RTPC_ext_viewPlayMode', 2)
            WWISE.WW_setState('STATE_viewPlayMode', 'STATE_viewPlayMode_strategic')
            WWISE.WWsetCameraShift(None)
        return

    def playStinger(self, event, priority):
        if self.__activeStinger is None or self.__activeStinger.isPlaying is False or priority > self.__activeStingerPriority:
            if self.__activeStinger is not None:
                self.__activeStinger.stop()
            self.__activeStinger = self.playSound2D(event)
            self.__activeStingerPriority = priority
        return

    def playTrack(self, event):
        if self.__activeTrack is None or self.__activeTrack.isPlaying is False:
            if self.__activeTrack is not None:
                self.__activeTrack.stop()
            self.__activeTrack = self.playSound2D(event)
        return

    def setSwitch(self, group, switch):
        WWISE.WW_setSwitch(group, switch)


def reloadSoundBanks():
    pass


def loadLightSoundsDB():
    ENVIRONMENT_EFFECTS_CONFIG_FILE = 'scripts/environment_effects.xml'
    section = ResMgr.openSection(ENVIRONMENT_EFFECTS_CONFIG_FILE)
    if section is None:
        return
    else:
        lightSoundDB = []
        if section['lightSounds'] is None:
            return
        for propertyName, propertySection in section['lightSounds'].items():
            DBitem = []
            DBitem.append(propertySection.readString('modelName'))
            DBitem.append(propertySection.readVector3('offset'))
            DBitem.append(propertySection.readStrings('wwsound'))
            DBitem.append(propertySection.readString('hardPoint'))
            lightSoundDB.append(DBitem)

        WWISE.LSloadEventsDB(lightSoundDB)
        return


def LSstartAll():
    if WWISE.enabled and ENABLE_LS:
        WWISE.LSstartAll()
