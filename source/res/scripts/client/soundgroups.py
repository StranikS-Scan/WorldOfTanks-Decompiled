# Embedded file name: scripts/client/SoundGroups.py
import BigWorld
import FMOD
import Event
import Settings
import ResMgr
import constants
from debug_utils import *
from helpers import i18n
import PlayerEvents
import traceback
from ReplayEvents import g_replayEvents
from functools import partial
g_instance = None
DSP_LOWPASS_LOW = 7000
DSP_LOWPASS_HI = 20000
DSP_SEEKSPEED = 200000

class SoundModes():
    __MODES_FOLDER = 'gui/soundModes/'
    __MODES_FILENAME = 'main_sound_modes.xml'
    DEFAULT_MODE_NAME = 'default'
    DEFAULT_NATION = 'default'
    MEDIA_PATH = None

    class SoundModeDesc(object):

        def __init__(self, dataSection):
            self.name = dataSection.readString('name', 'default')
            if FMOD.enabled:
                self.voiceLanguage = dataSection.readString('fmod_language', 'default')
            descriptionLink = dataSection.readString('description', '')
            self.description = i18n.makeString(descriptionLink)
            self.invisible = dataSection.readBool('invisible', False)
            self.banksToBeLoaded = []
            self.__isValid = None
            banksSec = dataSection['banks']
            if banksSec is not None:
                for bank in banksSec.values():
                    bankName = bank.asString
                    manualPath = bank.readString('filePath', '')
                    self.banksToBeLoaded.append((bankName, manualPath))

            return

        def getIsValid(self, soundModes):
            if self.__isValid is None:
                self.__isValid = self.__validate(soundModes)
            return self.__isValid

        def loadBanksManually(self):
            if not FMOD.enabled:
                return True
            for bankName, bankPath in self.banksToBeLoaded:
                if bankPath != '':
                    loadSuccessfully = FMOD.loadSoundBankIntoMemoryFromPath(bankPath)
                    if not loadSuccessfully:
                        return False

            return True

        def unloadBanksManually(self):
            if FMOD.enabled:
                for bankName, bankPath in self.banksToBeLoaded:
                    if bankPath != '':
                        FMOD.unloadSoundBankFromMemory(bankName)

        def __validate(self, soundModes):
            prevMode = soundModes.currentMode
            for soundBankName, soundPath in self.banksToBeLoaded:
                pathToCheck = soundPath if soundPath else '%s/%s.fsb' % (SoundModes.MEDIA_PATH, soundBankName)
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
            if other.name == 'default':
                return 1
            return 1

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
                SoundModes.MEDIA_PATH = engineConfig.readString('soundMgr/mediaPath', 'audio')
            else:
                SoundModes.MEDIA_PATH = 'audio'
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
                            else:
                                self.__modes[mode.name] = mode

                        for preset in nationalPresets:
                            if self.__nationalPresets.has_key(preset.name):
                                LOG_WARNING("%s config tries to redefine nationalPreset '%s', ignored" % (preset.name, preset.name))
                            else:
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

            else:
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
                if FMOD.enabled:
                    FMOD.setLanguage(defaultVoiceLanguage, self.modifiedSoundGroups)
                self.__modes[SoundModes.DEFAULT_MODE_NAME].loadBanksManually()
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
        self.__modes[self.__currentMode].unloadBanksManually()
        self.__currentMode = modeName
        modeDesc = self.__modes[modeName]
        if FMOD.enabled:
            languageSet = FMOD.setLanguage(modeDesc.voiceLanguage, self.modifiedSoundGroups)
        if not languageSet:
            LOG_WARNING('Sound: Internal FMOD error in FMOD::setLanguage')
            return False
        if not self.__modes[self.__currentMode].loadBanksManually():
            LOG_WARNING('Sound: Error while manual banks loading')
            return False
        if FMOD.enabled:
            loadedSoundBanks = FMOD.getSoundBanks()
            for bankName, bankPath in modeDesc.banksToBeLoaded:
                found = False
                for loadedBank in loadedSoundBanks:
                    if bankName == loadedBank:
                        found = True
                        break

                if not found:
                    LOG_WARNING('Sound: Bank %s was not loaded while loading %s sound mode' % (bankName, modeName))
                    return False

        return True

    def setCurrentNation(self, nation):
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
        self.__volumeByCategory = {}
        self.__masterVolume = 1.0
        self.__replace = {}
        self.__isWindowVisible = BigWorld.isWindowVisible()
        self.__handleInside = None
        self.__handleOutside = None
        self.__ceilLess = None
        self.__activeStinger = None
        self.__activeTrack = None
        self.__activeStingerPriority = None
        self.__muffled = False
        self.__muffledByReplay = False
        PlayerEvents.g_playerEvents.onAvatarReady += self.onAvatarReady
        self.__categories = {'voice': ('ingame_voice',),
         'vehicles': ('outside/vehicles', 'vehicles', 'inside/vehicles'),
         'effects': ('hits', 'outside/hits', 'inside/hits', 'weapons', 'inside/weapons', 'outside/weapons', 'environment', 'inside/environment', 'outside/environment', 'battle_gui'),
         'gui': ('gui',),
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
            for categoryName in self.__categories.keys():
                self.__volumeByCategory[categoryName] = defCategoryVolumes.get(categoryName, 1.0)

            self.savePreferences()
        else:
            ds = userPrefs[Settings.KEY_SOUND_PREFERENCES]
            self.__masterVolume = ds.readFloat('masterVolume', defMasterVolume)
            for categoryName in self.__categories.keys():
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
        self.defaultGroupList = []
        settings = ResMgr.openSection('scripts/arena_defs/_default_.xml/preloadSoundGroups')
        if settings is not None:
            self.defaultGroupList = settings.readStrings('groupName')
        if FMOD.enabled:
            for sg in self.defaultGroupList:
                result = FMOD.WG_loadSoundGroup(sg)
                if not result:
                    LOG_NOTE('Loading failed for default sound group ', sg)

            FMOD.WG_unloadAll()
        g_replayEvents.onMuteSound += self.__onReplayMute
        from gui.app_loader import g_appLoader
        g_appLoader.onGUISpaceChanged += self.__onGUISpaceChanged
        return

    def __del__(self):
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

        volume = 0.0 if not enable else self.__volumeByCategory['voice']
        self.setVolume('voice', volume, False)

    def enableAmbientAndMusic(self, enable):
        for categoryName in ('ambient', 'music'):
            enable = enable and not self.__muffledByReplay
            volume = 0.0 if not enable else self.__volumeByCategory[categoryName]
            self.setVolume(categoryName, volume, False)

    def enableVoiceSounds(self, enable):
        for categoryName in ('voice',):
            volume = 0.0 if not enable else self.__volumeByCategory[categoryName]
            self.setVolume(categoryName, volume, False)

    def __onReplayMute(self, mute):
        self.__muffledByReplay = mute
        for categoryName in ('vehicles', 'effects', 'ambient'):
            volume = 0.0 if mute else self.__volumeByCategory[categoryName]
            self.setVolume(categoryName, volume, False)

    def __onGUISpaceChanged(self, spaceID):
        pass

    def setMasterVolume(self, volume):
        self.__masterVolume = volume
        self.__muffledVolume = self.__masterVolume * self.getVolume('masterFadeVivox')
        if FMOD.enabled:
            FMOD.setMasterVolume(self.__muffledVolume if self.__muffled else self.__masterVolume)
        self.savePreferences()
        self.onMusicVolumeChanged('music', self.__masterVolume, self.getVolume('music'))
        self.onMusicVolumeChanged('ambient', self.__masterVolume, self.getVolume('ambient'))

    def getMasterVolume(self):
        return self.__masterVolume

    def setVolume(self, categoryName, volume, updatePrefs = True):
        if FMOD.enabled:
            for category in self.__categories[categoryName]:
                try:
                    BigWorld.wg_setCategoryVolume(category, volume)
                except Exception:
                    LOG_CURRENT_EXCEPTION()

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
        for categoryName in self.__volumeByCategory.keys():
            ds.writeFloat('volume_' + categoryName, self.__volumeByCategory[categoryName])

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
            if FMOD.enabled:
                FMOD.setMasterVolume(0)
            return
        self.setMasterVolume(self.__masterVolume)
        for categoryName in self.__volumeByCategory.keys():
            newVolume = self.__volumeByCategory[categoryName]
            if self.__muffledByReplay and categoryName in ('vehicles', 'effects', 'ambient'):
                newVolume = 0.0
            self.setVolume(categoryName, newVolume, updatePrefs=False)

    def muffleFMODVolume(self):
        if not self.__muffled:
            self.__muffled = True
            self.applyPreferences()

    def restoreFMODVolume(self):
        self.__muffled = False
        self.applyPreferences()

    def __muteByWindowVisibility(self):
        isWindowVisible = BigWorld.isWindowVisible()
        if self.__isWindowVisible != isWindowVisible:
            self.__isWindowVisible = isWindowVisible
            self.applyPreferences()
        self.__muteCallbackID = BigWorld.callback(0.25, self.__muteByWindowVisibility)

    def onAvatarReady(self):
        self.__ceilLess = BigWorld.player().vehicleTypeDescriptor.turret['ceilless']

    def unloadAll(self, path = None):
        if FMOD.enabled:
            FMOD.WG_unloadAll()
        import MusicController
        MusicController.g_musicController.destroy()
        MusicController.g_musicController.init(path)

    def preloadSoundGroups(self, arenaName):
        if not FMOD.enabled:
            return
        else:
            self.groupList = []
            settings = ResMgr.openSection('scripts/arena_defs/' + arenaName + '.xml/preloadSoundGroups')
            if settings is not None:
                self.groupList = settings.readStrings('groupName')
            for sg in self.groupList:
                result = FMOD.WG_loadSoundGroup(sg)
                if not result:
                    LOG_NOTE('Loading failed for arena sound group ', sg)

            return

    def checkAndReplace(self, event):
        if event == '':
            print 'SoundGroups.py: asked to play event with empty name'
            traceback.print_stack()
            return ''
        elif event in self.__replace:
            return self.__replace[event]
        else:
            return event

    def getSound3D(self, node, event):
        if FMOD.enabled:
            return FMOD.getSound3D(self.checkAndReplace(event), node)

    def playSound3D(self, node, event):
        if FMOD.enabled:
            s = FMOD.getSound3D(self.checkAndReplace(event), node)
            if s is not None:
                s.play()
        return

    def getSound2D(self, event):
        if FMOD.enabled:
            return FMOD.getSound(self.checkAndReplace(event))

    def playSound2D(self, event):
        if FMOD.enabled:
            return FMOD.playSound(self.checkAndReplace(event))

    def playSoundPos(self, event, pos):
        if FMOD.enabled:
            raise Exception('Tried to use WWISE function from FMOD release')

    def WWgetSound(self, eventName, objectName, matrix, local = (0.0, 0.0, 0.0)):
        pass

    def WWgetSoundCallback(self, eventName, objectName, matrix, callback):
        pass

    def WWgetSoundPos(self, eventName, objectName, position):
        pass

    def loadRemapping(self, arenaDescr):
        self.__replace = {}
        if not hasattr(arenaDescr, 'soundRemapping'):
            return
        for propertyName, propertySection in arenaDescr.soundRemapping.items():
            s1 = propertySection.readString('old')
            s2 = propertySection.readString('new')
            self.__replace[s1] = s2

    def changePlayMode(self, mode):
        if FMOD.enabled:
            FMOD.setEventsParam('viewPlayMode', mode)
        if FMOD.enabled:
            if self.__handleInside == None:
                self.__handleInside = FMOD.DSPgetHandleByNameAndCategory('FMOD Lowpass Simple', 'inside')
            if self.__handleOutside == None:
                self.__handleOutside = FMOD.DSPgetHandleByNameAndCategory('FMOD Lowpass Simple', 'outside')
            if self.__ceilLess == True:
                FMOD.DSPsetParamEx(self.__handleInside, 0, DSP_LOWPASS_HI, DSP_SEEKSPEED)
                FMOD.DSPsetParamEx(self.__handleOutside, 0, DSP_LOWPASS_HI, DSP_SEEKSPEED)
            elif mode == 1:
                FMOD.DSPsetParamEx(self.__handleInside, 0, DSP_LOWPASS_HI, DSP_SEEKSPEED)
                FMOD.DSPsetParamEx(self.__handleOutside, 0, DSP_LOWPASS_LOW, -DSP_SEEKSPEED)
            else:
                FMOD.DSPsetParamEx(self.__handleInside, 0, DSP_LOWPASS_LOW, -DSP_SEEKSPEED)
                FMOD.DSPsetParamEx(self.__handleOutside, 0, DSP_LOWPASS_HI, DSP_SEEKSPEED)
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

    def __getWWISECategoryName(self, categoryName):
        if categoryName == 'gui':
            return 'voice_gui'
        return categoryName


def reloadSoundBanks():
    import MusicController
    if FMOD.enabled:
        FMOD.reloadSoundbanks()
    MusicController.g_musicController.restart()


def loadPluginDB():
    ENVIRONMENT_EFFECTS_CONFIG_FILE = 'scripts/audioplugins.xml'
    section = ResMgr.openSection(ENVIRONMENT_EFFECTS_CONFIG_FILE)
    pluginDB = []
    for propertyName, propertySection in section.items():
        DBplugin = []
        DBplugin.append(propertySection.readString('name'))
        DBplugin.append(propertySection.readString('category'))
        for propertyName2, propertySection2 in propertySection['parameters'].items():
            DBparam = []
            DBparam.append(propertySection2.readInt('index'))
            DBparam.append(propertySection2.readFloat('value'))
            DBplugin.append(DBparam)

        DBparam = None
        pluginDB.append(DBplugin)

    DBitem = None
    if FMOD.enabled:
        FMOD.DSPloadPluginDB(pluginDB)
    pluginDB = None
    return


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
            if FMOD.enabled:
                DBitem.append(propertySection.readStrings('event'))
            DBitem.append(propertySection.readString('hardPoint'))
            lightSoundDB.append(DBitem)

        if FMOD.enabled:
            FMOD.LSloadEventsDB(lightSoundDB)
        lightSoundDB = None
        return
