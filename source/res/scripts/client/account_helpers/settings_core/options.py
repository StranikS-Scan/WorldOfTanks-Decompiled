# Embedded file name: scripts/client/account_helpers/settings_core/options.py
import base64
import cPickle
from operator import itemgetter
import sys
import fractions
import itertools
from collections import namedtuple
import math
import weakref
import GUI
from AvatarInputHandler.cameras import FovExtended
import BigWorld
import ResMgr
import Keys
import BattleReplay
import VOIP
import Settings
import SoundGroups
import ArenaType
from constants import CONTENT_TYPE
from gui.GraphicsPresets import GraphicsPresets
from gui.app_loader.decorators import sf_lobby
from helpers import isPlayerAccount, isPlayerAvatar
import nations
import CommandMapping
from helpers import i18n
from AvatarInputHandler import _INPUT_HANDLER_CFG, AvatarInputHandler
from AvatarInputHandler.DynamicCameras import ArcadeCamera, SniperCamera, StrategicCamera
from AvatarInputHandler.control_modes import PostMortemControlMode, SniperControlMode
from debug_utils import LOG_NOTE, LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_WARNING
from gui.Scaleform.managers.windows_stored_data import g_windowsStoredData
from post_processing import g_postProcessing
from MemoryCriticalController import g_critMemHandler
from Vibroeffects import VibroManager
from messenger import g_settings as messenger_settings
from account_helpers.AccountSettings import AccountSettings
from account_helpers.settings_core.SettingsCore import g_settingsCore
from account_helpers.settings_core.settings_constants import GRAPHICS
from shared_utils import CONST_CONTAINER
from gui import GUI_SETTINGS
from gui.clans.clan_controller import g_clanCtrl
from gui.shared.utils import graphics, functions
from gui.shared.utils.graphics import g_monitorSettings
from gui.shared.utils.key_mapping import getScaleformKey, getBigworldKey, getBigworldNameFromKey
from gui.Scaleform import VoiceChatInterface
from gui.Scaleform.LogitechMonitor import LogitechMonitor
from gui.battle_control import g_sessionProvider
from ConnectionManager import connectionManager
from gui.Scaleform.locale.SETTINGS import SETTINGS
from gui.shared.formatters import icons
import FMOD

class APPLY_METHOD:
    NORMAL = 'normal'
    DELAYED = 'delayed'
    RESTART = 'restart'


class ISetting(object):

    def get(self):
        raise NotImplementedError

    def apply(self, value):
        raise NotImplementedError

    def preview(self, value):
        raise NotImplementedError

    def revert(self):
        raise NotImplementedError

    def pack(self):
        raise NotImplementedError

    def getApplyMethod(self, value):
        return APPLY_METHOD.NORMAL

    def isEqual(self, value):
        raise NotImplementedError


class SettingAbstract(ISetting):
    PackStruct = namedtuple('PackStruct', 'current options')

    def __init__(self, isPreview = False):
        super(SettingAbstract, self).__init__()
        self.valueReal = None
        self.isPreview = isPreview
        return

    def _get(self):
        return None

    def _getOptions(self):
        return None

    def _set(self, value):
        pass

    def _save(self, value):
        pass

    def init(self):
        pass

    def getApplyMethod(self, value):
        return APPLY_METHOD.NORMAL

    def get(self):
        return self._get()

    def getOptions(self):
        return self._getOptions()

    def apply(self, value, applyUnchanged = False):
        if applyUnchanged:
            self._set(value)
        elif value != self._get():
            self._set(value)
        self._save(value)
        self.valueReal = None
        return self.getApplyMethod(value)

    def preview(self, value):
        if not self.isPreview:
            return
        else:
            if self.valueReal is None:
                self.valueReal = self._get()
            return self._set(value)

    def revert(self):
        if self.isPreview and self.valueReal is not None:
            self._set(self.valueReal)
            self.valueReal = None
        return

    def pack(self):
        options = self._getOptions()
        if options is None:
            return self._get()
        else:
            return self.PackStruct(self._get(), self._getOptions())._asdict()

    def dump(self):
        pass

    def getDefaultValue(self):
        return None

    def setSystemValue(self, value):
        pass

    def refresh(self):
        self.setSystemValue(self.get())

    def isEqual(self, value):
        return self.get() == value


class SettingsContainer(ISetting):

    def __init__(self, settings):
        super(SettingsContainer, self).__init__()
        self.settings = settings
        self.indices = dict(((n, idx) for idx, (n, s) in enumerate(self.settings)))

    def __forEach(self, names, processor):
        for name, param in self.settings:
            if name in names:
                try:
                    yield processor(name, param)
                except Exception:
                    LOG_CURRENT_EXCEPTION()
                    continue

    def __filter(self, settings, f):
        if f is not None:
            return filter(lambda item: item in f, settings)
        else:
            return settings

    def getApplyMethod(self, diff = None):
        settings = self.__filter(self.indices.keys(), diff.keys())
        methods = [ m for m in self.__forEach(settings, lambda n, p: p.getApplyMethod(diff[n])) ]
        if APPLY_METHOD.RESTART in methods:
            return APPLY_METHOD.RESTART
        if APPLY_METHOD.DELAYED in methods:
            return APPLY_METHOD.DELAYED
        return APPLY_METHOD.NORMAL

    def getSetting(self, name):
        if name in self.indices:
            return self.settings[self.indices[name]][1]
        LOG_WARNING("Failed to get a value of setting as it's not in indices: ", name)
        return SettingAbstract()

    def get(self, names = None):
        settings = self.__filter(self.indices.keys(), names)
        return dict(self.__forEach(settings, lambda n, p: (n, p.get())))

    def apply(self, values, names = None):
        settings = self.__filter(values.keys(), names)
        return list(self.__forEach(settings, lambda n, p: p.apply(values[n])))

    def preview(self, values, names = None):
        settings = self.__filter(values.keys(), names)
        for _ in self.__forEach(settings, lambda n, p: p.preview(values[n])):
            pass

    def revert(self, names = None):
        settings = self.__filter(self.indices.keys(), names)
        for _ in self.__forEach(settings, lambda n, p: p.revert()):
            pass

    def pack(self, names = None):
        settings = self.__filter(self.indices.keys(), names)
        return dict(self.__forEach(settings, lambda n, p: (n, p.pack())))

    def dump(self, names = None):
        settings = self.__filter(self.indices.keys(), names)
        for _ in self.__forEach(settings, lambda n, p: p.dump()):
            pass

    def init(self, names = None):
        settings = self.__filter(self.indices.keys(), names)
        for _ in self.__forEach(settings, lambda n, p: p.init()):
            pass

    def refresh(self, names = None):
        settings = self.__filter(self.indices.keys(), names)
        for _ in self.__forEach(settings, lambda n, p: p.refresh()):
            pass

    def isEqual(self, values):
        settings = self.__filter(self.indices.keys(), values.keys())
        equality = self.__forEach(settings, lambda n, p: p.isEqual(values[n]))
        return False not in equality


class ReadOnlySetting(SettingAbstract):

    def __init__(self, readerDelegate, isPreview = False):
        super(ReadOnlySetting, self).__init__(isPreview)
        self.readerDelegate = readerDelegate

    def _get(self):
        return self.readerDelegate()


class SoundSetting(SettingAbstract):
    VOLUME_MULT = 100

    def __init__(self, soundGroup, isPreview = False):
        super(SoundSetting, self).__init__(isPreview)
        self.group = soundGroup

    def __toGuiVolume(self, volume):
        return round(volume * self.VOLUME_MULT)

    def __toSysVolume(self, volume):
        return float(volume) / self.VOLUME_MULT

    def _get(self):
        if self.group == 'master':
            return self.__toGuiVolume(SoundGroups.g_instance.getMasterVolume())
        return self.__toGuiVolume(SoundGroups.g_instance.getVolume(self.group))

    def _set(self, value):
        if self.group == 'master':
            return SoundGroups.g_instance.setMasterVolume(self.__toSysVolume(value))
        return SoundGroups.g_instance.setVolume(self.group, self.__toSysVolume(value))


class VOIPMasterSoundSetting(SoundSetting):

    def __init__(self, isPreview = False):
        super(VOIPMasterSoundSetting, self).__init__('masterVivox', isPreview)

    def _set(self, value):
        super(VOIPMasterSoundSetting, self)._set(value)
        VOIP.getVOIPManager().setMasterVolume(value)


class VOIPMicSoundSetting(SoundSetting):

    def __init__(self, isPreview = False):
        super(VOIPMicSoundSetting, self).__init__('micVivox', isPreview)

    def _set(self, value):
        super(VOIPMicSoundSetting, self)._set(value)
        VOIP.getVOIPManager().setMicrophoneVolume(value)


class VibroSetting(SettingAbstract):
    GAIN_MULT = 100
    DEFAULT_GAIN = 0

    def __init__(self, vibroGroup, isPreview = False):
        super(VibroSetting, self).__init__(isPreview)
        self.group = vibroGroup

    def __toGuiVolume(self, volume):
        return round(volume * self.GAIN_MULT)

    def __toSysVolume(self, volume):
        return float(volume) / self.GAIN_MULT

    def _get(self):
        vm = VibroManager.g_instance
        if self.group == 'master':
            return self.__toGuiVolume(vm.getGain())
        return self.__toGuiVolume(vm.getGroupGain(self.group, self.DEFAULT_GAIN))

    def _set(self, value):
        vm = VibroManager.g_instance
        if self.group == 'master':
            return vm.setGain(self.__toSysVolume(value))
        return vm.setGroupGain(self.group, self.__toSysVolume(value))


class RegularSetting(SettingAbstract):

    def __init__(self, settingName, isPreview = False):
        super(RegularSetting, self).__init__(isPreview)
        self.settingName = settingName
        self._default = self.getDefaultValue()


class AccountSetting(SettingAbstract):

    def __init__(self, key, subKey = None):
        self.key = key
        self.subKey = subKey
        super(AccountSetting, self).__init__(False)

    def _getSettings(self):
        return AccountSettings.getSettings(self.key)

    def _get(self):
        if self.subKey is None:
            return self._getSettings()
        else:
            return self._getSettings().get(self.subKey)

    def _save(self, value):
        settings = value
        if self.subKey is not None:
            settings = dict(self._getSettings())
            settings[self.subKey] = value
        return AccountSettings.setSettings(self.key, settings)

    def getDefaultValue(self):
        value = AccountSettings.getSettingsDefault(self.key)
        if self.subKey is not None:
            settings = dict(value)
            value = settings.get(self.subKey)
        return value


class StorageSetting(RegularSetting):

    def __init__(self, settingName, storage, isPreview = False):
        super(StorageSetting, self).__init__(settingName, isPreview)
        self._storage = weakref.proxy(storage)

    def _get(self):
        return self._storage.extract(self.settingName, self._default)

    def _set(self, value):
        result = self.setSystemValue(value)
        setting = {'option': self.settingName,
         'value': value}
        self._storage.store(setting)
        return result


class DumpSetting(RegularSetting):

    def getDumpValue(self):
        return self._get()

    def setDumpedValue(self, value):
        BattleReplay.g_replayCtrl.setSetting(self.settingName, value)

    def getDumpedValue(self):
        return BattleReplay.g_replayCtrl.getSetting(self.settingName, self._default)

    def dump(self):
        BattleReplay.g_replayCtrl.setSetting(self.settingName, self.getDumpValue())


class StorageDumpSetting(StorageSetting, DumpSetting):

    def _get(self):
        if BattleReplay.isPlaying():
            return self.getDumpedValue()
        else:
            return super(StorageDumpSetting, self)._get()

    def _set(self, value):
        if BattleReplay.isPlaying():
            self.setDumpedValue(value)
        return super(StorageDumpSetting, self)._set(value)


class AccountDumpSetting(AccountSetting, DumpSetting):

    def __init__(self, settingName, key, subKey = None):
        AccountSetting.__init__(self, key, subKey)
        DumpSetting.__init__(self, settingName)

    def _get(self):
        if BattleReplay.isPlaying():
            return self.getDumpedValue()
        else:
            return super(AccountDumpSetting, self)._get()

    def _set(self, value):
        if BattleReplay.isPlaying():
            self.setDumpedValue(value)
        return super(AccountDumpSetting, self)._set(value)


class StorageAccountSetting(StorageDumpSetting):

    def getDefaultValue(self):
        return AccountSettings.getSettingsDefault(self.settingName)


class TutorialSetting(StorageDumpSetting):

    def getDefaultValue(self):
        return False


class ExcludeInReplayAccountSetting(StorageAccountSetting):

    def getDumpValue(self):
        return None

    def setDumpedValue(self, value):
        pass


class UserPrefsSetting(SettingAbstract):

    def __init__(self, sectionName = None, isPreview = False):
        super(UserPrefsSetting, self).__init__(isPreview)
        self.sectionName = sectionName

    def _readValue(self, section):
        return None

    def _writeValue(self, section, value):
        return None

    def _get(self):
        return self._readValue(Settings.g_instance.userPrefs)

    def _save(self, value):
        return self._writeValue(Settings.g_instance.userPrefs, value)


class UserPrefsBoolSetting(UserPrefsSetting):

    def _readValue(self, section):
        default = self.getDefaultValue()
        if section is not None:
            return section.readBool(self.sectionName, default)
        else:
            return default

    def _writeValue(self, section, value):
        if section is not None:
            return section.writeBool(self.sectionName, value)
        else:
            LOG_WARNING('Section is not defined', section)
            return False

    def getDefaultValue(self):
        return False


class UserPrefsStringSetting(UserPrefsSetting):

    def _readValue(self, section):
        default = self.getDefaultValue()
        if section is not None:
            return section.readString(self.sectionName, str(default))
        else:
            return default

    def _writeValue(self, section, value):
        if section is not None:
            return section.writeString(self.sectionName, str(value))
        else:
            LOG_WARNING('Section is not defined', section)
            return False

    def getDefaultValue(self):
        return ''


class UserPrefsFloatSetting(UserPrefsSetting):

    def _readValue(self, section):
        default = self.getDefaultValue()
        if section is not None:
            return section.readFloat(self.sectionName, float(default))
        else:
            return default

    def _writeValue(self, section, value):
        if section is not None:
            return section.writeFloat(self.sectionName, float(value))
        else:
            LOG_WARNING('Section is not defined', section)
            return False

    def getDefaultValue(self):
        return 0.0


class PreferencesSetting(SettingAbstract):

    def __init__(self, isPreview = False):
        super(PreferencesSetting, self).__init__(isPreview)
        BigWorld.wg_setSavePreferencesCallback(self._savePrefsCallback)

    def _savePrefsCallback(self, prefsRoot):
        pass


class PostProcessingSetting(StorageDumpSetting):

    def __init__(self, settingName, settingKey, storage, isPreview = False):
        self._settingKey = settingKey
        super(PostProcessingSetting, self).__init__(settingName, storage, isPreview)

    def getDefaultValue(self):
        return g_postProcessing.getSetting(self._settingKey)

    def setSystemValue(self, value):
        g_postProcessing.setSetting(self._settingKey, value)
        g_postProcessing.refresh()


class PostMortemDelaySetting(StorageDumpSetting):

    def getDefaultValue(self):
        return PostMortemControlMode.getIsPostmortemDelayEnabled()

    def setSystemValue(self, value):
        PostMortemControlMode.setIsPostmortemDelayEnabled(value)


class PlayersPanelSetting(StorageDumpSetting):

    def __init__(self, settingName, key, subKey, storage, isPreview = False):
        self._settingKey = key
        self._settingSubKey = subKey
        super(PlayersPanelSetting, self).__init__(settingName, storage, isPreview)

    def getDefaultValue(self):
        return AccountSettings.getSettingsDefault(self._settingKey).get(self._settingSubKey)


class VOIPSetting(AccountSetting):

    def __init__(self, isPreview = False):
        super(VOIPSetting, self).__init__('enableVoIP')
        self.isPreview = isPreview

    def initFromPref(self):
        self._set(super(VOIPSetting, self)._get())

    def _get(self):
        return VOIP.getVOIPManager().isEnabled()

    def _set(self, isEnable):
        if isEnable is None:
            return
        else:
            prevVoIP = self._get()
            if prevVoIP != isEnable:
                VOIP.getVOIPManager().enable(isEnable)
                LOG_NOTE('Change state of voip:', isEnable)
            return


class VOIPCaptureDevicesSetting(UserPrefsStringSetting):

    def __init__(self, isPreview = False):
        super(VOIPCaptureDevicesSetting, self).__init__(Settings.KEY_VOIP_DEVICE, isPreview)

    def _get(self):
        vm = VOIP.getVOIPManager()
        currentDeviceName = super(VOIPCaptureDevicesSetting, self)._get()
        deviceIdx = self.__getDeviceIdxByName(currentDeviceName)
        if deviceIdx == -1:
            deviceIdx = self.__getDeviceIdxByName(vm.getCurrentCaptureDevice())
        return deviceIdx

    def _getOptions(self):
        return [ i18n.encodeUtf8(device.decode(sys.getfilesystemencoding())) for device in self._getRawOptions() ]

    def _getRawOptions(self):
        return VOIP.getVOIPManager().getCaptureDevices()

    def _set(self, value):
        vm = VOIP.getVOIPManager()
        if len(vm.getCaptureDevices()):
            device = self.__getDeviceNameByIdx(value)
            vm.setCaptureDevice(device)
            LOG_DEBUG('Selecting new capture device', device)
            super(VOIPCaptureDevicesSetting, self)._set(device)

    def _save(self, value):
        super(VOIPCaptureDevicesSetting, self)._save(self.__getDeviceNameByIdx(value))

    @classmethod
    def __getDeviceNameByIdx(cls, idx):
        vm = VOIP.getVOIPManager()
        device = vm.getCaptureDevices()[0]
        if len(vm.getCaptureDevices()) > idx:
            device = vm.getCaptureDevices()[int(idx)]
        return device

    def __getDeviceIdxByName(self, deviceName):
        options = self._getRawOptions()
        if deviceName in options:
            return options.index(deviceName)
        return -1


class VOIPSupportSetting(ReadOnlySetting):

    def __init__(self):
        super(VOIPSupportSetting, self).__init__(self.__isSupported)

    @sf_lobby
    def app(self):
        return None

    def __isVoiceChatReady(self):
        if g_sessionProvider.getCtx().isInBattle:
            return VoiceChatInterface.g_instance.ready
        else:
            app = self.app
            if app is not None and app.voiceChatManager is not None:
                return app.voiceChatManager.ready
            return False
            return

    def __isSupported(self):
        return VOIP.getVOIPManager().getVOIPDomain() != '' and self.__isVoiceChatReady()


class MessengerSetting(StorageDumpSetting):

    def getDefaultValue(self):
        data = messenger_settings.userPrefs._asdict()
        if self.settingName in data:
            return data[self.settingName]
        else:
            return None


class MessengerDateTimeSetting(MessengerSetting):

    def __init__(self, bit, storage = None):
        super(MessengerDateTimeSetting, self).__init__('datetimeIdx', storage)
        self.bit = bit

    def _get(self):
        settingValue = super(MessengerDateTimeSetting, self)._get()
        if settingValue:
            settingValue = settingValue & self.bit
        return bool(settingValue)

    def _set(self, value):
        settingValue = super(MessengerDateTimeSetting, self)._get()
        settingValue ^= self.bit
        if value:
            settingValue |= self.bit
        super(MessengerDateTimeSetting, self)._set(settingValue)

    def getDumpValue(self):
        return super(MessengerDateTimeSetting, self)._get()


class ClansSetting(MessengerSetting):

    def _get(self):
        if g_clanCtrl.isEnabled():
            return super(ClansSetting, self)._get()
        else:
            return None

    def getDefaultValue(self):
        return True


class GameplaySetting(StorageAccountSetting):

    def __init__(self, settingName, gameplayName, storage):
        super(GameplaySetting, self).__init__(settingName, storage)
        self.gameplayName = gameplayName
        self.bit = ArenaType.getVisibilityMask(ArenaType.getGameplayIDForName(self.gameplayName))

    def _get(self):
        settingValue = super(GameplaySetting, self)._get()
        return settingValue & self.bit > 0

    def _set(self, value):
        settingValue = super(GameplaySetting, self)._get()
        settingValue ^= self.bit
        if value:
            settingValue |= self.bit
        return super(GameplaySetting, self)._set(settingValue)

    def getDumpValue(self):
        return super(GameplaySetting, self)._get()


class GammaSetting(SettingAbstract):

    def _get(self):
        return BigWorld.getGammaCorrection()

    def _set(self, value):
        value = max(value, 0.5)
        value = min(value, 2.0)
        BigWorld.setGammaCorrection(value)


class TripleBufferedSetting(SettingAbstract):

    def _get(self):
        return BigWorld.isTripleBuffered()

    def _set(self, value):
        BigWorld.setTripleBuffering(value)


class VerticalSyncSetting(SettingAbstract):

    def _get(self):
        return BigWorld.isVideoVSync()

    def _set(self, value):
        BigWorld.setVideoVSync(value)


class CustomAASetting(SettingAbstract):

    def __init__(self, isPreview = False):
        super(CustomAASetting, self).__init__(isPreview)
        self.__customAAModes = BigWorld.getSupportedCustomAAModes()

    def __getModeIndex(self, mode):
        if mode in self.__customAAModes:
            return self.__customAAModes.index(mode)
        return -1

    def __getModeByIndex(self, modeIndex):
        if len(self.__customAAModes) > modeIndex > -1:
            return self.__customAAModes[int(modeIndex)]
        else:
            return None

    def _get(self):
        return self.__getModeIndex(BigWorld.getCustomAAMode())

    def _getOptions(self):
        return [ '#settings:customAAMode/mode%s' % i for i in self.__customAAModes ]

    def _set(self, modeIndex):
        mode = self.__getModeByIndex(modeIndex)
        if mode is None:
            LOG_ERROR('There is no gamma mode by given index', modeIndex)
            return
        else:
            BigWorld.setCustomAAMode(mode)
            return


class MultisamplingSetting(SettingAbstract):

    def __init__(self, isPreview = False):
        super(MultisamplingSetting, self).__init__(isPreview)
        self.__multisamplingTypes = BigWorld.getSupportedMultisamplingTypes()
        self.__multisamplingTypes.insert(0, 0)

    def __getMSTypeIndex(self, msType):
        if msType in self.__multisamplingTypes:
            return self.__multisamplingTypes.index(msType)
        return -1

    def __getMSTypeByIndex(self, msTypeIndex):
        if len(self.__multisamplingTypes) > msTypeIndex > -1:
            return self.__multisamplingTypes[int(msTypeIndex)]
        else:
            return None

    def _get(self):
        return self.__getMSTypeIndex(BigWorld.getMultisamplingType())

    def _getOptions(self):
        return [ '#settings:multisamplingType/type%s' % i for i in self.__multisamplingTypes ]

    def _set(self, msTypeIndex):
        msType = self.__getMSTypeByIndex(msTypeIndex)
        if msType is None:
            LOG_ERROR('There is no multisampling type by given index', msTypeIndex)
            return
        else:
            BigWorld.setMultisamplingType(msType)
            return


class AspectRatioSetting(SettingAbstract):
    MAGIC_NUMBER = 3.75

    def __init__(self, isPreview = False):
        super(AspectRatioSetting, self).__init__(isPreview)
        self.__aspectRatios = ((4, 3),
         (5, 4),
         (16, 9),
         (16, 10),
         (19, 10))
        maxWidth, maxHeight = g_monitorSettings.maxParams
        if maxHeight > 0:
            aspectRatio3DVision = float(maxWidth) / float(maxHeight)
            if aspectRatio3DVision > self.MAGIC_NUMBER:
                gcd = fractions.gcd(maxWidth, maxHeight)
                self.__aspectRatios += ((maxWidth / gcd, maxHeight / gcd),)

    def __getAspectRatioIndex(self, aspectRatio):
        for index, size in enumerate(self.__aspectRatios):
            if round(float(size[0]) / size[1], 6) == aspectRatio:
                return index

        return len(self.__aspectRatios)

    def __getAspectRatioByIndex(self, apIndex):
        if len(self.__aspectRatios) > apIndex > -1:
            ars = self.__aspectRatios[int(apIndex)]
            return round(float(ars[0]) / ars[1], 6)
        else:
            return None

    def __getCurrentAspectRatio(self):
        return round(BigWorld.getFullScreenAspectRatio(), 6)

    def _get(self):
        return self.__getAspectRatioIndex(self.__getCurrentAspectRatio())

    def _getOptions(self):
        currentAP = self.__getCurrentAspectRatio()
        options = [ '%d:%d' % m for m in self.__aspectRatios ]
        if self.__getAspectRatioIndex(currentAP) == len(self.__aspectRatios):
            options.append('%s:1*' % BigWorld.wg_getNiceNumberFormat(currentAP))
        return options

    def _set(self, apIndex):
        aspectRatio = self.__getAspectRatioByIndex(apIndex)
        if aspectRatio is None:
            LOG_ERROR('There is no aspect ratio by given index', apIndex)
            return
        else:
            BigWorld.changeFullScreenAspectRatio(aspectRatio)
            FovExtended.instance().refreshFov()
            return


class DynamicRendererSetting(SettingAbstract):

    def _get(self):
        if g_settingsCore.getSetting(GRAPHICS.DRR_AUTOSCALER_ENABLED):
            return round(BigWorld.getDRRAutoscalerBaseScale(), 2) * 100
        return round(BigWorld.getDRRScale(), 2) * 100

    def _set(self, value):
        value = float(value) / 100
        BigWorld.setDRRScale(value)


class ColorFilterIntensitySetting(SettingAbstract):

    def _get(self):
        value = round(BigWorld.getColorGradingStrength(), 2) * 100
        return self._adjustValue(value)

    def _set(self, value):
        value = float(self._adjustValue(value)) / 100
        BigWorld.setColorGradingStrength(value)

    def _adjustValue(self, value):
        if value < 25:
            return 25
        if value > 100:
            return 100
        return value


class LensEffectSetting(StorageDumpSetting):

    def getDefaultValue(self):
        return SniperControlMode._LENS_EFFECTS_ENABLED

    def setSystemValue(self, value):
        SniperControlMode.enableLensEffects(value)


class GraphicSetting(SettingAbstract):
    MIN_OPTION_VALUE = 4

    def __init__(self, settingName, isPreview = False):
        super(GraphicSetting, self).__init__(isPreview)
        self.name = settingName
        self._initialValue = None
        self._inited = False
        return

    def _get(self):
        setting = graphics.getGraphicsSetting(self.name)
        if setting is not None:
            if not self._inited:
                self._initialValue = setting.value
                self._inited = True
            return setting.value
        else:
            return

    def _getOptions(self):
        data = graphics.getGraphicsSetting(self.name)
        if data is not None:
            options = []
            for idx, (label, supported, advanced, _) in enumerate(data.options):
                options.append({'label': '#settings:graphicsSettingsOptions/%s' % str(label),
                 'data': idx,
                 'advanced': advanced,
                 'supported': supported})

            return sorted(options, key=itemgetter('data'), reverse=True)
        else:
            return

    def _set(self, value):
        value = int(value)
        originalValue = value
        while not self._tryToSetValue(value) and value <= self.MIN_OPTION_VALUE:
            value = value + 1

        if originalValue != value:
            LOG_NOTE('Adjusted value has been set: `%s`' % value)

    def _tryToSetValue(self, value):
        try:
            BigWorld.setGraphicsSetting(self.name, value)
        except Exception:
            LOG_ERROR('Unable to set value `%s` for option `%s`' % (value, self.name))
            return False

        return True

    def getApplyMethod(self, value):
        data = graphics.getGraphicsSetting(self.name)
        if data is not None and value != self._get():
            if data.needRestart and self._initialValueChanged(value):
                return APPLY_METHOD.RESTART
            if data.delayed:
                return APPLY_METHOD.DELAYED
        return super(GraphicSetting, self).getApplyMethod(value)

    def _initialValueChanged(self, value):
        if self._initialValue is not None:
            return value != self._initialValue
        else:
            return True


class SniperModeSwingingSetting(GraphicSetting):

    def __init__(self):
        super(SniperModeSwingingSetting, self).__init__('SNIPER_MODE_SWINGING_ENABLED')

    def __recreateCamera(self):
        inputHandler = BigWorld.player().inputHandler
        if hasattr(inputHandler, 'ctrl'):
            if inputHandler.ctrl == inputHandler.ctrls['sniper']:
                inputHandler.ctrl.recreateCamera()

    def _set(self, value):
        super(SniperModeSwingingSetting, self)._set(value)
        self.__recreateCamera()


class TextureQualitySetting(GraphicSetting):

    def __init__(self):
        super(TextureQualitySetting, self).__init__('TEXTURE_QUALITY')

    def _set(self, value):
        super(TextureQualitySetting, self)._set(value)
        if g_critMemHandler.originTexQuality != g_critMemHandler.ORIGIN_DEFAULT:
            g_critMemHandler.originTexQuality = value


class TerrainQualitySetting(GraphicSetting):

    def __init__(self):
        super(TerrainQualitySetting, self).__init__('TERRAIN_QUALITY')

    def _set(self, value):
        super(TerrainQualitySetting, self)._set(value)
        if g_critMemHandler.originTerrainQuality != g_critMemHandler.ORIGIN_DEFAULT:
            g_critMemHandler.originTerrainQuality = value


class FloraQualitySetting(GraphicSetting):

    def __init__(self):
        super(FloraQualitySetting, self).__init__('FLORA_QUALITY')

    def _set(self, value):
        super(FloraQualitySetting, self)._set(value)
        if g_critMemHandler.originFloraQuality != g_critMemHandler.ORIGIN_DEFAULT:
            g_critMemHandler.originFloraQuality = value


class GraphicsPresetSetting(SettingAbstract):
    CUSTOM_PRESET_KEY = 'CUSTOM'
    Preset = namedtuple('Preset', 'index key settings')

    def __init__(self):
        super(GraphicsPresetSetting, self).__init__(False)
        self.__presets = []
        self.__graphicsPresets = GraphicsPresets()
        self.__parsePresets()

    def isCustom(self):
        return self._get() == len(self.__presets) - 1

    def __parsePresets(self):
        idx = 0
        for key, idx in graphics.getGraphicsPresetsIndices().iteritems():
            self.__presets.append(self.Preset(idx, key, dict(graphics.getGraphicsPresets(idx)))._asdict())

        self.__presets.append(self.Preset(idx + 1, self.CUSTOM_PRESET_KEY, {})._asdict())

    def __checkPresetForCurrent(self, presetIdx):
        for name, value in graphics.getGraphicsPresets(presetIdx).iteritems():
            graphicSetting = graphics.getGraphicsSetting(name)
            if graphicSetting is None or value != graphicSetting.value:
                return False

        return True

    def _get(self):
        presetsIndices = graphics.getGraphicsPresetsIndices().values()
        for idx in presetsIndices:
            if self.__checkPresetForCurrent(idx):
                return idx

        return len(presetsIndices)

    def _getOptions(self):
        result = []
        for preset in self.__presets:
            isSupported = True
            for settingName in self.__graphicsPresets.GRAPHICS_QUALITY_SETTINGS:
                if settingName in self.__graphicsPresets.GRAPHICS_QUALITY_SETTINGS_PRESETS_EXCLUDE:
                    continue
                value = preset['settings'].get(settingName)
                if value is not None and not self.__graphicsPresets.settingIsSupported(settingName, value):
                    allowedPresetSettings = GUI_SETTINGS.allowedNotSupportedGraphicSettings.get(preset['key'], [])
                    if settingName not in allowedPresetSettings:
                        isSupported = False
                        break

            if isSupported:
                result.append(preset)

        return sorted(result, key=itemgetter('index'))


class MonitorSetting(SettingAbstract):

    def __init__(self, isPreview = False, storage = None):
        super(MonitorSetting, self).__init__(isPreview)
        self._storage = weakref.proxy(storage)

    def _get(self):
        return self._storage.monitor

    def _set(self, value):
        self._storage.monitor = int(value)

    def _getOptions(self):
        return BigWorld.wg_getMonitorNames()

    def getApplyMethod(self, value):
        if g_monitorSettings.isMonitorChanged and g_monitorSettings.isFullscreen:
            return APPLY_METHOD.RESTART
        return super(MonitorSetting, self).getApplyMethod(value)

    def pack(self):
        result = super(MonitorSetting, self).pack()
        result.update({'real': g_monitorSettings.activeMonitor})
        return result


class WindowSizeSetting(SettingAbstract):

    def __init__(self, isPreview = False, storage = None):
        super(WindowSizeSetting, self).__init__(isPreview)
        self.__lastSelectedWindowSize = None
        self._storage = weakref.proxy(storage)
        return

    def __getWindowSizeIndex(self, width, height):
        for index, (w, h) in enumerate(self.__getWindowSizes()):
            if w == width and h == height:
                return index

        return 0

    def __getWindowSizes(self):
        sizes = self.__getSuitableWindowSizes()[self._storage.monitor]
        current = g_monitorSettings.currentWindowSize
        if current is not None and (current.width, current.height) not in sizes:
            sizes.append((current.width, current.height))
        return sizes

    def __getSuitableWindowSizes(self):
        result = []
        for modes in graphics.getSuitableWindowSizes():
            sizes = set()
            for mode in modes:
                sizes.add((mode.width, mode.height))

            result.append(sorted(tuple(sizes)))

        return result

    def _get(self):
        size = self._storage.windowSize
        if size is not None:
            return self.__getWindowSizeIndex(*size)
        else:
            return

    def _getOptions(self):
        allModes = []
        for monitorModes in self.__getSuitableWindowSizes():
            modes = [ '%dx%d' % (width, height) for width, height in monitorModes ]
            currentSizeWidth, currentSizeHeight = self._storage.windowSize
            current = '%dx%d' % (currentSizeWidth, currentSizeHeight)
            if current not in modes:
                modes.append('%s*' % current)
            allModes.append(modes)

        return allModes

    def _set(self, value):
        windowSize = self.__getWindowSizes()[int(value)]
        self._storage.windowSize = windowSize
        self.__lastSelectedWindowSize = windowSize

    def _savePrefsCallback(self, prefsRoot):
        if self.__lastSelectedWindowSize is not None and g_monitorSettings.isMonitorChanged:
            devPref = prefsRoot['devicePreferences']
            devPref.writeInt('windowedWidth', self.__lastSelectedWindowSize[0])
            devPref.writeInt('windowedWidth', self.__lastSelectedWindowSize[1])
        return


class ResolutionSetting(PreferencesSetting):

    def __init__(self, isPreview = False, storage = None):
        super(PreferencesSetting, self).__init__(isPreview)
        self.__lastSelectedVideoMode = None
        self._storage = weakref.proxy(storage)
        return

    def __getResolutions(self):
        return self.__getSuitableResolutions()[self._storage.monitor]

    def __getSuitableResolutions(self):
        result = []
        for modes in graphics.getSuitableVideoModes():
            resolutions = set()
            for mode in modes:
                resolutions.add((mode.width, mode.height))

            result.append(sorted(tuple(resolutions)))

        return result

    def __getResolutionIndex(self, width, height):
        for idx, (w, h) in enumerate(self.__getResolutions()):
            if w == width and h == height:
                return idx

        return 0

    def _get(self):
        resolution = self._storage.resolution
        if resolution is not None:
            return self.__getResolutionIndex(*resolution)
        else:
            return

    def _getOptions(self):
        return [ [ '%dx%d' % (width, height) for width, height in resolutions ] for resolutions in self.__getSuitableResolutions() ]

    def _set(self, value):
        resolution = self.__getResolutions()[int(value)]
        self._storage.resolution = resolution
        self.__lastSelectedVideoMode = resolution

    def _savePrefsCallback(self, prefsRoot):
        if self.__lastSelectedVideoMode is not None and g_monitorSettings.isMonitorChanged:
            devPref = prefsRoot['devicePreferences']
            devPref.writeInt('fullscreenWidth', self.__lastSelectedVideoMode[0])
            devPref.writeInt('fullscreenHeight', self.__lastSelectedVideoMode[1])
        return


class RefreshRateSetting(PreferencesSetting):

    def __init__(self, isPreview = False, storage = None):
        super(PreferencesSetting, self).__init__(isPreview)
        self._storage = weakref.proxy(storage)

    def _getOptions(self):
        result = []
        for modes in graphics.getSuitableVideoModes():
            resolutions = set()
            for mode in modes:
                resolutions.add((mode.width, mode.height))

            ratesList = []
            for width, height in sorted(tuple(resolutions)):
                rates = set()
                for mode in modes:
                    if mode.width == width and mode.height == height:
                        rates.add(mode.refreshRate)

                ratesList.append(sorted(tuple(rates)))

            result.append(ratesList)

        return result

    def _get(self):
        return self._storage.refreshRate

    def _set(self, value):
        self._storage.refreshRate = int(value)


class FullscreenSetting(PreferencesSetting):

    def __init__(self, storage):
        super(PreferencesSetting, self).__init__()
        self._storage = weakref.proxy(storage)
        self.__isFullscreen = self._get()

    def _get(self):
        return self._storage.fullscreen

    def _set(self, value):
        self._storage.fullscreen = bool(value)

    def _save(self, value):
        self.__isFullscreen = value

    def _savePrefsCallback(self, prefsRoot):
        if g_monitorSettings.isMonitorChanged:
            prefsRoot['devicePreferences'].writeBool('windowed', not self.__isFullscreen)


class VehicleMarkerSetting(StorageAccountSetting):

    class OPTIONS(CONST_CONTAINER):

        class TYPES(CONST_CONTAINER):
            BASE = 'Base'
            ALT = 'Alt'

        class PARAMS(CONST_CONTAINER):
            ICON = 'Icon'
            LEVEL = 'Level'
            HP_INDICATOR = 'HpIndicator'
            DAMAGE = 'Damage'
            HP = 'Hp'
            VEHICLE_NAME = 'VehicleName'
            PLAYER_NAME = 'PlayerName'

        @classmethod
        def getOptionName(cls, mType, mOption):
            raise mType in cls.TYPES.ALL() and mOption in cls.PARAMS.ALL() or AssertionError
            return 'marker%s%s' % (mType, mOption)

        @classmethod
        def ALL(cls):
            for mType in cls.TYPES.ALL():
                for mParam in cls.PARAMS.ALL():
                    yield cls.getOptionName(mType, mParam)

    def __init__(self, settingName, storage):
        self.settingKey = 'markers'
        super(VehicleMarkerSetting, self).__init__(settingName, storage)

    def getDefaultValue(self):
        return AccountSettings.getSettingsDefault(self.settingKey)[self.settingName]

    def _get(self):
        marker = {}
        for mType in self.OPTIONS.TYPES.ALL():
            for param in self.OPTIONS.PARAMS.ALL():
                on = self.OPTIONS.getOptionName(mType, param)
                default = self._default[on]
                if BattleReplay.isPlaying():
                    value = BattleReplay.g_replayCtrl.getSetting(self.settingName, {}).get(on, default)
                else:
                    value = self._storage.extract(self.settingName, on, self._default[on])
                if param == self.OPTIONS.PARAMS.HP and isPlayerAccount():
                    marker[on] = self.PackStruct(value, [ '#settings:marker/hp/type%d' % mid for mid in xrange(4) ])._asdict()
                else:
                    marker[on] = value

        return marker


class AimSetting(StorageAccountSetting):

    class OPTIONS(CONST_CONTAINER):
        NET = 'net'
        NET_TYPE = 'netType'
        CENTRAL_TAG = 'centralTag'
        CENTRAL_TAG_TYPE = 'centralTagType'
        RELOADER = 'reloader'
        RELOADER_TIMER = 'reloaderTimer'
        CONDITION = 'condition'
        MIXING = 'mixing'
        MIXING_TYPE = 'mixingType'
        CASSETTE = 'cassette'
        GUN_TAG = 'gunTag'
        GUN_TAG_TYPE = 'gunTagType'

    VIRTUAL_OPTIONS = {OPTIONS.MIXING_TYPE: (OPTIONS.MIXING, 3),
     OPTIONS.GUN_TAG_TYPE: (OPTIONS.GUN_TAG, 15),
     OPTIONS.CENTRAL_TAG_TYPE: (OPTIONS.CENTRAL_TAG, 14),
     OPTIONS.NET_TYPE: (OPTIONS.NET, 4)}

    def _get(self):
        result = {}
        for option in self.OPTIONS.ALL():
            if option in self.VIRTUAL_OPTIONS:
                default = self._default[self.VIRTUAL_OPTIONS[option][0]]['type']
            else:
                default = self._default[option]['alpha']
            if BattleReplay.isPlaying():
                value = BattleReplay.g_replayCtrl.getSetting(self.settingName, {}).get(option, default)
            else:
                value = self._storage.extract(self.settingName, option, default)
            result[option] = value

        return result

    def pack(self):
        result = self._get()
        for vname, (name, optsLen) in self.VIRTUAL_OPTIONS.iteritems():
            result[vname] = self.PackStruct(result[vname], [ '#settings:%s/%s/type%d' % (self.settingName, name, i) for i in xrange(int(optsLen)) ])._asdict()

        return result

    def toAccountSettings(self):
        result = {}
        value = self._get()
        for option in self.OPTIONS.ALL():
            if option not in self.VIRTUAL_OPTIONS:
                alpha = value[option]
                type = 0
                for k, v in self.VIRTUAL_OPTIONS.items():
                    if v[0] == option:
                        type = value[k]

                result[option] = {'alpha': alpha,
                 'type': type}

        return result

    def fromAccountSettings(self, settings):
        result = {}
        for key, value in settings.items():
            if key not in self.VIRTUAL_OPTIONS:
                result[key] = value['alpha']
                for k, v in self.VIRTUAL_OPTIONS.items():
                    if v[0] == key:
                        result[k] = value['type']

        return result


class MinimapSetting(StorageDumpSetting):

    def _get(self):
        return super(MinimapSetting, self)._get()

    def _set(self, value):
        return super(MinimapSetting, self)._set(value)

    def getDefaultValue(self):
        return True


class MinimapVehModelsSetting(StorageDumpSetting):

    class OPTIONS(CONST_CONTAINER):
        NEVER = 'never'
        ALT = 'alt'
        ALWAYS = 'always'

    VEHICLE_MODELS_TYPES = [OPTIONS.NEVER, OPTIONS.ALT, OPTIONS.ALWAYS]

    def _getOptions(self):
        settingsKey = '#settings:game/%s/%s'
        return [ settingsKey % (self.settingName, type) for type in self.VEHICLE_MODELS_TYPES ]

    def getDefaultValue(self):
        return 0


class ShowMarksOnGunSetting(StorageAccountSetting):

    def _get(self):
        return not super(ShowMarksOnGunSetting, self)._get()

    def _set(self, value):
        return super(ShowMarksOnGunSetting, self)._set(not value)

    def getDefaultValue(self):
        return True


class ControlSetting(SettingAbstract):
    ControlPackStruct = namedtuple('ControlPackStruct', 'current default')

    def __init__(self, isPreview = False):
        super(ControlSetting, self).__init__(isPreview)

    def _getDefault(self):
        return None

    def pack(self):
        return self.ControlPackStruct(self._get(), self._getDefault())._asdict()


class StorageControlSetting(StorageDumpSetting, ControlSetting):
    pass


class MouseSetting(ControlSetting):
    CAMERAS = {'postmortem': (ArcadeCamera.getCameraAsSettingsHolder, 'postMortemMode/camera'),
     'arcade': (ArcadeCamera.getCameraAsSettingsHolder, 'arcadeMode/camera'),
     'sniper': (SniperCamera.getCameraAsSettingsHolder, 'sniperMode/camera'),
     'strategic': (StrategicCamera.getCameraAsSettingsHolder, 'strategicMode/camera')}

    def __init__(self, mode, setting, default, isPreview = False):
        super(MouseSetting, self).__init__(isPreview)
        self.mode = mode
        self.setting = setting
        self.default = default
        self.__aihSection = ResMgr.openSection(_INPUT_HANDLER_CFG)

    def __isControlModeAccessible(self):
        return BigWorld.player() is not None and hasattr(BigWorld.player(), 'inputHandler') and hasattr(BigWorld.player().inputHandler, 'ctrls')

    def __getCamera(self):
        if self.__isControlModeAccessible():
            mode = BigWorld.player().inputHandler.ctrls[self.mode]
            if mode is not None:
                return mode.camera
        cameraInfo = self.CAMERAS.get(self.mode)
        if cameraInfo is not None:
            creator, section = cameraInfo
            return creator(self.__aihSection[section])
        else:
            return

    def _getDefault(self):
        return self.default

    def _get(self):
        camera = self.__getCamera()
        if camera is not None:
            return camera.getUserConfigValue(self.setting)
        else:
            return self.default

    def _set(self, value):
        camera = self.__getCamera()
        if camera is None:
            LOG_WARNING('Error while applying mouse settings: empty camera', self.mode, self.setting)
            return
        else:
            camera.setUserConfigValue(self.setting, value)
            if not self.__isControlModeAccessible():
                camera._writeUserPreferences()
            return


class MouseSensitivitySetting(MouseSetting):

    def __init__(self, mode):
        super(MouseSensitivitySetting, self).__init__(mode, 'sensitivity', 1.0)


class DynamicFOVMultiplierSetting(MouseSetting):

    def __init__(self, isPreview = False):
        super(DynamicFOVMultiplierSetting, self).__init__('arcade', 'fovMultMinMaxDist', self.getDefaultValue(), isPreview)

    def _set(self, value):
        value = ArcadeCamera.MinMax(min=value, max=1.0)
        super(DynamicFOVMultiplierSetting, self)._set(value)

    def setSystemValue(self, value):
        self._set(value)

    def getDefaultValue(self):
        return ArcadeCamera.MinMax(min=1.0, max=1.0)


class FOVSetting(RegularSetting):

    def __init__(self, settingName, isPreview = False, storage = None):
        super(FOVSetting, self).__init__(settingName, isPreview)
        self.__static = StaticFOVSetting(isPreview)
        self.__dynamic = DynamicFOVSetting(isPreview)
        self.__storage = weakref.proxy(storage)
        self.__storage.proxyFOV(self)

    def _get(self):
        return (self.__static.get(),) + tuple(self.__dynamic.get())

    def _set(self, value):
        self.__static.apply(value[0])
        self.__dynamic.apply(value[1:])
        self.__storage.FOV = value

    def init(self):
        if not BigWorld.wg_preferencesExistedAtStartup():
            self.apply((95, 80, 100))

    def isEqual(self, value):
        return self._get() == tuple(value)


class StaticFOVSetting(UserPrefsFloatSetting):

    def __init__(self, isPreview = False):
        super(StaticFOVSetting, self).__init__(Settings.KEY_FOV, isPreview)

    def _get(self):
        return int(super(StaticFOVSetting, self)._get())

    def _save(self, value):
        super(StaticFOVSetting, self)._save(int(value))

    def getDefaultValue(self):
        return round(math.degrees(FovExtended.instance().defaultHorizontalFov))


class DynamicFOVSetting(UserPrefsStringSetting):
    DEFAULT = (80, 100)

    def __init__(self, isPreview = False):
        super(DynamicFOVSetting, self).__init__(Settings.KEY_DYNAMIC_FOV, isPreview)

    def _get(self):
        try:
            return cPickle.loads(base64.b64decode(super(DynamicFOVSetting, self)._get()))
        except:
            LOG_ERROR('Could not load dynamic fov setting')
            return self.DEFAULT

    def _save(self, value):
        super(DynamicFOVSetting, self)._save(base64.b64encode(cPickle.dumps(value)))

    def getDefaultValue(self):
        return base64.b64encode(cPickle.dumps(self.DEFAULT))


class DynamicFOVEnabledSetting(UserPrefsBoolSetting):

    def __init__(self, isPreview = False, storage = None):
        super(DynamicFOVEnabledSetting, self).__init__(Settings.KEY_DYNAMIC_FOV_ENABLED, isPreview)
        self.__storage = weakref.proxy(storage)
        self.__storage.proxyDynamicFOVEnabled(self)

    def _get(self):
        return bool(super(DynamicFOVEnabledSetting, self)._get())

    def _set(self, value):
        self.__storage.dynamicFOVEnabled = bool(value)

    def _save(self, value):
        super(DynamicFOVEnabledSetting, self)._save(bool(value))

    def getDefaultValue(self):
        return False


class MouseInversionSetting(StorageControlSetting):

    def __init__(self, settingName, settingKey, storage, isPreview = False):
        super(MouseInversionSetting, self).__init__(settingName, storage, isPreview)
        self.settings = []
        for mode in MouseSetting.CAMERAS:
            self.settings.append(MouseSetting(mode, settingKey, False, isPreview))

    def getDefaultValue(self):
        return False

    def setSystemValue(self, value):
        for setting in self.settings:
            setting._set(value)


class BackDraftInversionSetting(StorageControlSetting, StorageAccountSetting):

    def __init__(self, storage, isPreview = False):
        super(BackDraftInversionSetting, self).__init__('backDraftInvert', storage, isPreview)

    def _getDefault(self):
        return self._default

    def setSystemValue(self, value):
        if isPlayerAvatar():
            BigWorld.player().invRotationOnBackMovement = value


class KeyboardSetting(StorageControlSetting):

    def __init__(self, cmd, storage):
        super(KeyboardSetting, self).__init__(cmd, storage)

    @sf_lobby
    def app(self):
        return None

    def _getDefault(self):
        command = CommandMapping.g_instance.getCommand(self.settingName)
        return getScaleformKey(CommandMapping.g_instance.getDefaults().get(command, Keys.KEY_NONE))

    def getDefaultValue(self):
        command = CommandMapping.g_instance.getCommand(self.settingName)
        return CommandMapping.g_instance.getDefaults().get(command, Keys.KEY_NONE)

    def _set(self, value):
        result = self.setSystemValue(value)
        if KeyboardSettings.USE_SERVER_LAYOUT:
            value = getBigworldKey(value)
            setting = {'option': self.settingName,
             'value': value}
            self._storage.store(setting)
        return result

    def _get(self):
        if KeyboardSettings.USE_SERVER_LAYOUT:
            value = super(KeyboardSetting, self)._get()
        else:
            value = self.getCurrentMapping()
        return getScaleformKey(value)

    def setSystemValue(self, value):
        key = 'KEY_NONE'
        if value is not None:
            key = getBigworldNameFromKey(getBigworldKey(value))
        LOG_DEBUG('Settings key command', self.settingName, value, key)
        if self.settingName == 'CMD_VOICECHAT_MUTE' and isPlayerAccount():
            self.app.gameInputManager.updateChatKeyHandlers(value)
        CommandMapping.g_instance.remove(self.settingName)
        CommandMapping.g_instance.add(self.settingName, key)
        return

    def getCurrentMapping(self):
        mapping = CommandMapping.g_instance.get(self.settingName)
        if mapping is None:
            mapping = self.getDefaultValue()
        return mapping


class KeyboardSettings(SettingsContainer):
    USE_SERVER_LAYOUT = False
    KEYS_LAYOUT = (('movement', (('forward', 'CMD_MOVE_FORWARD'),
       ('backward', 'CMD_MOVE_BACKWARD'),
       ('left', 'CMD_ROTATE_LEFT'),
       ('right', 'CMD_ROTATE_RIGHT'),
       ('auto_rotation', 'CMD_CM_VEHICLE_SWITCH_AUTOROTATION'))),
     ('cruis_control', (('forward_cruise', 'CMD_INCREMENT_CRUISE_MODE'), ('backward_cruise', 'CMD_DECREMENT_CRUISE_MODE'), ('stop_fire', 'CMD_STOP_UNTIL_FIRE'))),
     ('firing', (('fire', 'CMD_CM_SHOOT'),
       ('lock_target', 'CMD_CM_LOCK_TARGET'),
       ('lock_target_off', 'CMD_CM_LOCK_TARGET_OFF'),
       ('alternate_mode', 'CMD_CM_ALTERNATE_MODE'),
       ('reloadPartialClip', 'CMD_RELOAD_PARTIAL_CLIP'))),
     ('vehicle_other', (('showHUD', 'CMD_TOGGLE_GUI'), ('showRadialMenu', 'CMD_RADIAL_MENU_SHOW'))),
     ('equipment', (('item01', 'CMD_AMMO_CHOICE_1'),
       ('item02', 'CMD_AMMO_CHOICE_2'),
       ('item03', 'CMD_AMMO_CHOICE_3'),
       ('item04', 'CMD_AMMO_CHOICE_4'),
       ('item05', 'CMD_AMMO_CHOICE_5'),
       ('item06', 'CMD_AMMO_CHOICE_6'),
       ('item07', 'CMD_AMMO_CHOICE_7'),
       ('item08', 'CMD_AMMO_CHOICE_8'))),
     ('shortcuts', (('attack', 'CMD_CHAT_SHORTCUT_ATTACK', (('attack', 'attack/ext'), ('my_target', 'my_target/ext'), ('follow_me', 'follow_me/ext'))),
       ('to_base', 'CMD_CHAT_SHORTCUT_BACKTOBASE', (('to_base', None), ('to_back', 'to_back/ext'))),
       ('positive', 'CMD_CHAT_SHORTCUT_POSITIVE'),
       ('negative', 'CMD_CHAT_SHORTCUT_NEGATIVE'),
       ('help_me', 'CMD_CHAT_SHORTCUT_HELPME', (('help_me', None), ('help_me_temp', 'help_me_temp/ext'))),
       ('reload', 'CMD_CHAT_SHORTCUT_RELOAD', (('reload', None), ('stop', 'stop/ext'))))),
     ('camera', (('camera_up', 'CMD_CM_CAMERA_ROTATE_UP'),
       ('camera_down', 'CMD_CM_CAMERA_ROTATE_DOWN'),
       ('camera_left', 'CMD_CM_CAMERA_ROTATE_LEFT'),
       ('camera_right', 'CMD_CM_CAMERA_ROTATE_RIGHT'))),
     ('voicechat', (('pushToTalk', 'CMD_VOICECHAT_MUTE'),)),
     ('logitech_keyboard', (('switch_view', 'CMD_LOGITECH_SWITCH_VIEW'),)),
     ('minimap', (('sizeUp', 'CMD_MINIMAP_SIZE_UP'), ('sizeDown', 'CMD_MINIMAP_SIZE_DOWN'), ('visible', 'CMD_MINIMAP_VISIBLE'))))

    def __init__(self, storage):
        settings = [('keysLayout', ReadOnlySetting(lambda : self._getLayout()))]
        for group in self._getLayout(True):
            for setting in group['values']:
                settings.append((setting['key'], KeyboardSetting(setting['cmd'], storage)))

        super(KeyboardSettings, self).__init__(tuple(settings))

    @classmethod
    def _getLayout(cls, isFull = False):
        layout = []
        for groupName, groupValues in cls.KEYS_LAYOUT:
            if not isFull:
                if groupName == 'minimap' and not GUI_SETTINGS.minimapSize:
                    continue
                if groupName == 'voicechat' and not GUI_SETTINGS.voiceChat:
                    continue
                if groupName == 'logitech_keyboard' and not LogitechMonitor.isPresentColor():
                    continue
            layout.append({'key': groupName,
             'values': [ cls.__mapValues(*x) for x in groupValues ]})

        return layout

    def apply(self, values, names = None):
        super(KeyboardSettings, self).apply(values, names)
        CommandMapping.g_instance.onMappingChanged(values)
        CommandMapping.g_instance.save()

    def refresh(self, names = None):
        self.setSystemValue()

    def setSystemValue(self):
        if not self.USE_SERVER_LAYOUT:
            return
        for _, setting in self.settings:
            if isinstance(setting, KeyboardSetting):
                currentValue = setting.get()
                setting.setSystemValue(currentValue)

    def getCurrentMapping(self):
        mapping = {}
        for _, setting in self.settings:
            if isinstance(setting, KeyboardSetting):
                mapping[setting.settingName] = setting.getCurrentMapping()

        return mapping

    def getDefaultMapping(self):
        mapping = {}
        for _, setting in self.settings:
            if isinstance(setting, KeyboardSetting):
                mapping[setting.settingName] = setting.getDefaultValue()

        return mapping

    @classmethod
    def __mapValues(cls, key, cmd, descr = None):
        result = {'key': key,
         'cmd': cmd}
        if False:
            settingsKey = '#settings:keyboard/keysBlocks/command/%s'
            result['descr'] = map(lambda x: {'header': settingsKey % x[0],
             'label': settingsKey % x[1] if x[1] else None}, descr)
        return result


class FPSPerfomancerSetting(StorageDumpSetting):

    def getDefaultValue(self):
        return BigWorld.getGraphicsSetting('PS_USE_PERFORMANCER')

    def setSystemValue(self, value):
        try:
            BigWorld.setGraphicsSetting('PS_USE_PERFORMANCER', bool(value))
        except Exception:
            LOG_CURRENT_EXCEPTION()


class AltVoicesSetting(StorageDumpSetting):
    if FMOD.enabled:
        ALT_VOICES_PREVIEW = itertools.cycle(('sound_mode_preview01', 'sound_mode_preview02', 'sound_mode_preview03'))
    DEFAULT_IDX = 0
    PREVIEW_SOUNDS_COUNT = 3

    class SOUND_MODE_TYPE:
        UNKNOWN = 0
        REGULAR = 1
        NATIONAL = 2

    def __init__(self, setttingName, storage):
        super(AltVoicesSetting, self).__init__(setttingName, storage, True)
        self.__previewSound = None
        self.__lastPreviewedValue = None
        self._handlers = {self.SOUND_MODE_TYPE.UNKNOWN: lambda *args: False,
         self.SOUND_MODE_TYPE.REGULAR: self.__applyRegularMode,
         self.SOUND_MODE_TYPE.NATIONAL: self.__applyNationalMode}
        return

    @sf_lobby
    def app(self):
        return None

    def playPreviewSound(self, soundMgr = None):
        if self.isSoundModeValid():
            self.__clearPreviewSound()
            sndMgr = soundMgr or self.app.soundManager
            sndPath = sndMgr.sounds.getEffectSound(next(self.ALT_VOICES_PREVIEW))
            if SoundGroups.g_instance.soundModes.currentNationalPreset[1]:
                g = functions.rnd_choice(*nations.AVAILABLE_NAMES)
                SoundGroups.g_instance.soundModes.setCurrentNation(next(g))
            SoundGroups.g_instance.playSound2D(sndPath)
            return True
        return False

    def isOptionEnabled(self):
        return len(self.__getSoundModesList()) > 1

    def isSoundModeValid(self):
        if self.__lastPreviewedValue is None:
            self.__lastPreviewedValue = self._get()
        return self.setSystemValue(self.__lastPreviewedValue)

    def preview(self, value):
        if value == 'default':
            value = self.DEFAULT_IDX
        else:
            value = int(value)
        super(AltVoicesSetting, self).preview(value)
        self.__lastPreviewedValue = value
        self.__clearPreviewSound()

    def revert(self):
        super(AltVoicesSetting, self).revert()
        self.__lastPreviewedValue = self._get()
        self.__clearPreviewSound()

    def _getOptions(self):
        return [ sm.description for sm in self.__getSoundModesList() ]

    def getDefaultValue(self):
        modes = self.__getSoundModesList()
        cur = SoundGroups.g_instance.soundModes.currentNationalPreset
        if cur is not None:
            modeName, isNational = cur
            for idx, sm in enumerate(modes):
                if sm.name == modeName:
                    smType = self.__getSoundModeType(sm)
                    if isNational and smType == self.SOUND_MODE_TYPE.NATIONAL or not isNational and smType == self.SOUND_MODE_TYPE.REGULAR:
                        return idx

        return self.DEFAULT_IDX

    def _set(self, value):
        if value == 'default':
            value = self.DEFAULT_IDX
        else:
            value = int(value)
        return super(AltVoicesSetting, self)._set(value)

    def _get(self):
        value = super(AltVoicesSetting, self)._get()
        modes = self.__getSoundModesList()
        if value < len(modes):
            return value
        return self.DEFAULT_IDX

    def setSystemValue(self, value):
        if not self.isOptionEnabled():
            return True
        modes = self.__getSoundModesList()
        mode = modes[self.DEFAULT_IDX]
        if value < len(modes):
            mode = modes[value]
        return self._handlers[self.__getSoundModeType(mode)](mode)

    def __getSoundModeType(self, soundMode):
        if soundMode.name in SoundGroups.g_instance.soundModes.modes:
            return self.SOUND_MODE_TYPE.REGULAR
        if soundMode.name in SoundGroups.g_instance.soundModes.nationalPresets:
            return self.SOUND_MODE_TYPE.NATIONAL
        return self.SOUND_MODE_TYPE.UNKNOWN

    def __applyRegularMode(self, mode):
        soundModes = SoundGroups.g_instance.soundModes
        soundModes.setCurrentNation(soundModes.DEFAULT_NATION)
        return soundModes.setNationalMappingByMode(mode.name)

    def __applyNationalMode(self, mode):
        return SoundGroups.g_instance.soundModes.setNationalMappingByPreset(mode.name)

    def __getSoundModesList(self):
        result = []
        soundModes = SoundGroups.g_instance.soundModes
        for sm in sorted(soundModes.modes.values()):
            if not sm.invisible and sm.getIsValid(soundModes):
                result.append(sm)

        result.extend(soundModes.nationalPresets.values())
        return result

    def __clearPreviewSound(self):
        if self.__previewSound is not None:
            self.__previewSound.stop()
            self.__previewSound = None
        return


class DynamicCamera(StorageDumpSetting):

    def getDefaultValue(self):
        return AvatarInputHandler.isCameraDynamic()


class SniperModeStabilization(StorageDumpSetting):

    def getDefaultValue(self):
        return AvatarInputHandler.isSniperStabilized()


class WindowsTarget4StoredData(SettingAbstract):

    def __init__(self, targetID, isPreview = False):
        super(WindowsTarget4StoredData, self).__init__(isPreview)
        self._targetID = targetID

    def _get(self):
        return g_windowsStoredData.isTargetEnabled(self._targetID)

    def _set(self, value):
        if value:
            g_windowsStoredData.addTarget(self._targetID)
        else:
            g_windowsStoredData.removeTarget(self._targetID)


class ReplaySetting(StorageAccountSetting):
    REPLAY_TYPES = ['none', 'last', 'all']

    def _getOptions(self):
        settingsKey = '#settings:game/%s/%s'
        return [ settingsKey % (self.settingName, type) for type in self.REPLAY_TYPES ]

    def setSystemValue(self, value):
        BattleReplay.g_replayCtrl.enableAutoRecordingBattles(value)


class InterfaceScaleSetting(UserPrefsFloatSetting):

    def __init__(self, sectionName = None, isPreview = False):
        super(InterfaceScaleSetting, self).__init__(sectionName, isPreview)
        self.__interfaceScale = 0
        connectionManager.onDisconnected += self.onDisconnected
        connectionManager.onConnected += self.onConnected

    @sf_lobby
    def app(self):
        return None

    def get(self):
        self.__checkAndCorrectScaleValue(self.__interfaceScale)
        return self.__interfaceScale

    def getDefaultValue(self):
        return AccountSettings.getSettingsDefault(self.sectionName)

    def setSystemValue(self, value):
        self.__interfaceScale = value
        scale = g_settingsCore.interfaceScale.getScaleByIndex(value)
        app = self.app
        if app is not None:
            params = list(GUI.screenResolution()[:2])
            params.append(scale)
            app.updateStage(*params)
        g_monitorSettings.setGlyphCache(scale)
        return

    def onConnected(self):
        self.setSystemValue(super(InterfaceScaleSetting, self).get())

    def onDisconnected(self):
        self.setSystemValue(0)

    def _getOptions(self):
        return [self.__getScales(graphics.getSuitableWindowSizes(), BigWorld.wg_getCurrentResolution(True)), self.__getScales(graphics.getSuitableVideoModes())]

    def _set(self, value):
        super(InterfaceScaleSetting, self)._save(value)
        self.setSystemValue(value)

    def __getScales(self, modesVariety, additionalSize = None):
        result = []
        for i in xrange(len(modesVariety)):
            modes = sorted(set([ (mode.width, mode.height) for mode in modesVariety[i] ]))
            if additionalSize is not None:
                modes.append(additionalSize[0:2])
            result.append(map(graphics.getInterfaceScalesList, modes))

        return result

    def __checkAndCorrectScaleValue(self, value):
        scaleLength = len(g_settingsCore.interfaceScale.getScaleOptions())
        if value >= scaleLength:
            self.__interfaceScale = scaleLength - 1
            self._set(self.__interfaceScale)
            g_settingsCore.interfaceScale.scaleChanged()


class GraphicsQualityNote(SettingAbstract):
    note = '{0}{1}  {2}{3}'.format("<font face='$FieldFont' size='13' color='#595950'>", i18n.makeString(SETTINGS.GRAPHICSQUALITYHDSD_SD), icons.info(), '</font>')
    _GRAPHICS_QUALITY_TYPES = {CONTENT_TYPE.SD_TEXTURES: note,
     CONTENT_TYPE.TUTORIAL: note,
     CONTENT_TYPE.SANDBOX: note}

    def _get(self):
        return self._GRAPHICS_QUALITY_TYPES.get(ResMgr.activeContentType(), '')

    def _set(self, value):
        pass
