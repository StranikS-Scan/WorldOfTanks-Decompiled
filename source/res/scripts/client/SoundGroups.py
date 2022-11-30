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
import Windowing
from ReplayEvents import g_replayEvents
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_DEBUG
from helpers import i18n, dependency
from skeletons.gui.app_loader import IAppLoader, GuiGlobalSpaceID
from soft_exception import SoftException
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
MASTER_VOLUME_DEFAULT = 0.5
CUSTOM_MP3_EVENTS = ('sixthSense', 'soundExploring')

class CREW_GENDER_SWITCHES(object):
    GROUP = 'SWITCH_ext_vo_gender'
    MALE = 'SWITCH_ext_vo_gender_male'
    FEMALE = 'SWITCH_ext_vo_gender_female'
    DEFAULT = MALE
    GENDER_ALL = (MALE, FEMALE)


class SoundModes(object):
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
                self.__isValid = True
                for soundBankName, soundPath in self.wwbanksToBeLoaded:
                    pathToCheck = soundPath if soundPath != '' else '%s/%s' % (SoundModes.MEDIA_PATH, soundBankName)
                    if not ResMgr.isFile(pathToCheck):
                        self.__isValid = False

            return self.__isValid

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
            folderSection = ResMgr.openSection(SoundModes.__MODES_FOLDER)
            if folderSection is None:
                LOG_ERROR("Folder for SoundModes: '%s' is not found!" % SoundModes.__MODES_FOLDER)
            else:
                defaultNationalPresets = dict(self.__nationalPresets)
                for modesConfigSection in folderSection.values():
                    if ResMgr.getFilename(modesConfigSection.name) != SoundModes.__MODES_FILENAME:
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
        languageSet = self.__setMode(modeName)
        if not languageSet:
            defaultVoiceLanguage = ''
            if SoundModes.DEFAULT_MODE_NAME in self.__modes:
                defaultVoiceLanguage = self.__modes[SoundModes.DEFAULT_MODE_NAME].voiceLanguage
            WWISE.setLanguage(defaultVoiceLanguage)
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
        WWISE.setLanguage(modeDesc.voiceLanguage)
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
        self.__handleInside = None
        self.__handleOutside = None
        self.__activeStinger = None
        self.__activeTrack = None
        self.__activeStingerPriority = None
        self.__muffled = False
        self.__muffledByReplay = False
        self.__spaceID = GuiGlobalSpaceID.UNDEFINED
        PlayerEvents.g_playerEvents.onAvatarReady += self.onAvatarReady
        self.__categories = {'vehicles': ('outside/vehicles', 'vehicles'),
         'effects': ('hits', 'outside/hits', 'inside/weapons', 'outside/weapons', 'outside/environment', 'battle_gui'),
         'gui': ('gui', 'ingame_voice'),
         'music': ('music',),
         'ambient': ('outside/ambient', 'hangar_v2', 'ambientUR'),
         'masterVivox': (),
         'micVivox': (),
         'masterFadeVivox': ()}
        defCategoryVolumes = {'music': 0.5,
         'masterVivox': 0.7,
         'micVivox': 0.4}
        userPrefs = Settings.g_instance.userPrefs
        soundModeName = SoundModes.DEFAULT_MODE_NAME
        nationalMapping = None
        self.__soundModes = None
        self.__viewPlayModeParam = WWISE.WW_getRTPCValue('RTPC_ext_viewPlayMode')
        if not userPrefs.has_key(Settings.KEY_SOUND_PREFERENCES):
            userPrefs.write(Settings.KEY_SOUND_PREFERENCES, '')
            self.__masterVolume = MASTER_VOLUME_DEFAULT
            for categoryName in self.__categories.iterkeys():
                self.__volumeByCategory[categoryName] = defCategoryVolumes.get(categoryName, 1.0)

            self.savePreferences()
        else:
            ds = userPrefs[Settings.KEY_SOUND_PREFERENCES]
            self.__enableStatus = ds.readInt('enable', SOUND_ENABLE_STATUS_DEFAULT)
            self.__masterVolume = ds.readFloat('masterVolume', MASTER_VOLUME_DEFAULT)
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
        if not self.applyPreferences():
            Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)
        g_replayEvents.onMuteSound += self.__onReplayMute
        return

    def destroy(self):
        self.onVolumeChanged.clear()
        self.onMusicVolumeChanged.clear()
        PlayerEvents.g_playerEvents.onAvatarReady -= self.onAvatarReady
        g_replayEvents.onMuteSound -= self.__onReplayMute
        player = BigWorld.player()
        if player is not None and player.inputHandler is not None:
            player.inputHandler.onCameraChanged -= self.__onCameraChanged
        self.onVolumeChanged.clear()
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        LOG_DEBUG('Destroyed: %s' % self)
        return

    def startListeningGUISpaceChanges(self):
        appLoader = dependency.instance(IAppLoader)
        self.__spaceID = appLoader.getSpaceID()
        appLoader.onGUISpaceEntered += self.__onGUISpaceEntered

    def stopListeningGUISpaceChanges(self):
        appLoader = dependency.instance(IAppLoader)
        appLoader.onGUISpaceEntered -= self.__onGUISpaceEntered

    def enableLobbySounds(self, enable):
        for categoryName in ('ambient', 'gui'):
            volume = 0.0 if not enable else self.__volumeByCategory[categoryName]
            self.setVolume(categoryName, volume, False)

    def enableArenaSounds(self, enable):
        for categoryName in ('vehicles', 'effects', 'ambient'):
            enable = enable and not self.__muffledByReplay
            volume = 0.0 if not enable else self.__volumeByCategory[categoryName]
            self.setVolume(categoryName, volume, False)

    def enableAmbientAndMusic(self, enable):
        for categoryName in ('ambient', 'music'):
            enable = enable and not self.__muffledByReplay
            volume = 0.0 if not enable else self.__volumeByCategory[categoryName]
            self.setVolume(categoryName, volume, False)

    def enableEverythingExceptGui(self, enable):
        for categoryName in ('ambient', 'music', 'music_hangar', 'vehicles', 'effects', 'voice'):
            enable = enable and not self.__muffledByReplay
            volume = 0.0 if not enable else self.__volumeByCategory[categoryName]
            self.setVolume(categoryName, volume, False)

    def enableVoiceSounds(self, enable):
        for categoryName in ('gui',):
            volume = 0.0 if not enable else self.__volumeByCategory[categoryName]
            self.setVolume(categoryName, volume, False)

    def __onReplayMute(self, mute):
        if self.__muffledByReplay is mute:
            return
        self.__muffledByReplay = mute
        for categoryName in ('vehicles', 'effects', 'ambient', 'gui', 'voice'):
            volume = 0.0 if mute else self.__volumeByCategory[categoryName]
            self.setVolume(categoryName, volume, False)

    def __onGUISpaceEntered(self, spaceID):
        if WWISE.enabled:
            if spaceID == GuiGlobalSpaceID.LOGIN:
                WWISE.WG_loadLogin()
                self.enableLobbySounds(True)
        self.__spaceID = spaceID

    def setMasterVolume(self, volume):
        self.__masterVolume = volume
        self.__muffledVolume = self.__masterVolume * self.getVolume('masterFadeVivox')
        masterVolume = self.__muffledVolume if self.__muffled else self.__masterVolume
        self.savePreferences()
        WWISE.WW_setMasterVolume(masterVolume)
        self.onMusicVolumeChanged('music', self.__masterVolume, self.getVolume('music'))
        self.onMusicVolumeChanged('ambient', self.__masterVolume, self.getVolume('ambient'))

    def getMasterVolume(self):
        return self.__masterVolume if BigWorld.isWindowVisible() else 0.0

    def getEnableStatus(self):
        return self.__enableStatus

    def setEnableStatus(self, status):
        if status not in SOUND_ENABLE_STATUS_VALUES:
            raise SoftException('Status {} is out of range(3)'.format(status))
        self.__enableStatus = status
        self.savePreferences()

    def setVolume(self, categoryName, volume, updatePrefs=True):
        WWISE.WW_setRTPCBus('RTPC_ext_menu_volume_{}'.format(categoryName), volume * 100.0)
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
        if not BigWorld.isWindowVisible():
            return False
        self.setMasterVolume(self.__masterVolume)
        for categoryName in self.__volumeByCategory.iterkeys():
            newVolume = self.__volumeByCategory[categoryName]
            if self.__muffledByReplay and categoryName in ('vehicles', 'effects', 'ambient'):
                newVolume = 0.0
            self.setVolume(categoryName, newVolume, updatePrefs=False)

        return True

    def muffleWWISEVolume(self):
        if not self.__muffled:
            self.__muffled = True
            self.applyPreferences()

    def restoreWWISEVolume(self):
        self.__muffled = False
        self.applyPreferences()

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

    def __onWindowAccessibilityChanged(self, isAccessible):
        if isAccessible:
            self.applyPreferences()
            Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)

    def unloadAll(self):
        MusicControllerWWISE.destroy()

    def preloadSoundGroups(self, arenaName):
        MusicControllerWWISE.init(arenaName)

    def getSound3D(self, node, event):
        if DEBUG_TRACE_SOUND is True:
            LOG_DEBUG('SOUND: getSound3D', event, node)
        if DEBUG_TRACE_STACK is True:
            import traceback
            traceback.print_stack()
        return self.WWgetSound(event, event + ' : ' + str(node), node)

    def prepareMP3(self, event):
        if event in CUSTOM_MP3_EVENTS:
            if not ResMgr.isFile('audioww/%s.mp3' % event):
                LOG_ERROR('SOUND: mp3 file is not exist', 'audioww/%s.mp3' % event)
            else:
                WWISE.WW_prepareMP3('%s.mp3' % event)

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
            __ceilLess = vehicleTypeDescriptor.turret.ceilless
        if mode == 0:
            self.__viewPlayModeParam.set(1)
            if __ceilLess is True:
                WWISE.WW_setState('STATE_viewPlayMode', 'STATE_viewplaymode_arcade_ceilless')
            else:
                WWISE.WW_setState('STATE_viewPlayMode', 'STATE_viewPlayMode_arcade')
            WWISE.WWsetCameraShift(None)
        elif mode == 1:
            self.__viewPlayModeParam.set(0)
            if __ceilLess is True:
                WWISE.WW_setState('STATE_viewPlayMode', 'STATE_viewplaymode_sniper_ceilless')
            else:
                WWISE.WW_setState('STATE_viewPlayMode', 'STATE_viewPlayMode_sniper')
            if BigWorld.player().getVehicleAttached() is not None:
                compoundModel = BigWorld.player().getVehicleAttached().appearance.compoundModel
                WWISE.WWsetCameraShift(compoundModel.node(TankPartNames.TURRET))
        elif mode == 2:
            self.__viewPlayModeParam.set(2)
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

    def setState(self, stateName, stateValue):
        WWISE.WW_setState(stateName, stateValue)
