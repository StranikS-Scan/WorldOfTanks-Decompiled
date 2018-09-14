# Python bytecode 2.7 (decompiled from Python 2.7)
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
import WWISE
from constants import CONTENT_TYPE
from gui.Scaleform.genConsts.ACOUSTICS import ACOUSTICS
from gui.app_loader.decorators import app_getter
from gui.shared import event_dispatcher
from gui.sounds.sound_constants import SPEAKERS_CONFIG
from helpers import dependency
from helpers import isPlayerAvatar
from helpers.i18n import makeString
import nations
import CommandMapping
from helpers import i18n
from Event import Event
from AvatarInputHandler import _INPUT_HANDLER_CFG, AvatarInputHandler
from AvatarInputHandler.DynamicCameras import ArcadeCamera, SniperCamera, StrategicCamera
from AvatarInputHandler.control_modes import PostMortemControlMode, SniperControlMode
from debug_utils import LOG_NOTE, LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_WARNING
from gui.Scaleform.managers.windows_stored_data import g_windowsStoredData
from post_processing import g_postProcessing
from Vibroeffects import VibroManager
from messenger import g_settings as messenger_settings
from account_helpers.AccountSettings import AccountSettings
from account_helpers.settings_core.settings_constants import SOUND
from shared_utils import CONST_CONTAINER, forEach
from gui import GUI_SETTINGS
from gui.shared.utils import graphics, functions
from gui.shared.utils.graphics import g_monitorSettings
from gui.shared.utils.key_mapping import getScaleformKey, getBigworldKey, getBigworldNameFromKey
from ConnectionManager import connectionManager
from gui.Scaleform.locale.SETTINGS import SETTINGS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import icons
from gui.shared.utils.functions import makeTooltip
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.clans import IClanController
from skeletons.gui.sounds import ISoundsController

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

    def __init__(self, isPreview=False):
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

    def fini(self):
        pass

    def getApplyMethod(self, value):
        return APPLY_METHOD.NORMAL

    def get(self):
        return self._get()

    def getOptions(self):
        return self._getOptions()

    def apply(self, value, applyUnchanged=False):
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
        return self._get() if options is None else self.PackStruct(self._get(), self._getOptions())._asdict()

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
        return filter(lambda item: item in f, settings) if f is not None else settings

    def getApplyMethod(self, diff=None):
        settings = self.__filter(self.indices.keys(), diff.keys())
        methods = [ m for m in self.__forEach(settings, lambda n, p: p.getApplyMethod(diff[n])) ]
        if APPLY_METHOD.RESTART in methods:
            return APPLY_METHOD.RESTART
        return APPLY_METHOD.DELAYED if APPLY_METHOD.DELAYED in methods else APPLY_METHOD.NORMAL

    def getSetting(self, name):
        if name in self.indices:
            return self.settings[self.indices[name]][1]
        LOG_WARNING("Failed to get a value of setting as it's not in indices: ", name)
        return SettingAbstract()

    def get(self, names=None):
        settings = self.__filter(self.indices.keys(), names)
        return dict(self.__forEach(settings, lambda n, p: (n, p.get())))

    def apply(self, values, names=None):
        settings = self.__filter(values.keys(), names)
        return list(self.__forEach(settings, lambda n, p: p.apply(values[n])))

    def preview(self, values, names=None):
        settings = self.__filter(values.keys(), names)
        for _ in self.__forEach(settings, lambda n, p: p.preview(values[n])):
            pass

    def revert(self, names=None):
        settings = self.__filter(self.indices.keys(), names)
        for _ in self.__forEach(settings, lambda n, p: p.revert()):
            pass

    def pack(self, names=None):
        result = {}
        for name, param in self.settings:
            if names is None or name in names:
                result[name] = param.pack()

        return result

    def dump(self, names=None):
        settings = self.__filter(self.indices.keys(), names)
        for _ in self.__forEach(settings, lambda n, p: p.dump()):
            pass

    def init(self, names=None):
        settings = self.__filter(self.indices.keys(), names)
        for _ in self.__forEach(settings, lambda n, p: p.init()):
            pass

    def fini(self):
        for _, param in self.settings:
            param.fini()

        self.settings = ()
        self.indices.clear()

    def refresh(self, names=None):
        settings = self.__filter(self.indices.keys(), names)
        for _ in self.__forEach(settings, lambda n, p: p.refresh()):
            pass

    def isEqual(self, values):
        settings = self.__filter(self.indices.keys(), values.keys())
        equality = self.__forEach(settings, lambda n, p: p.isEqual(values[n]))
        return False not in equality


class ReadOnlySetting(SettingAbstract):

    def __init__(self, readerDelegate, isPreview=False):
        super(ReadOnlySetting, self).__init__(isPreview)
        self.readerDelegate = readerDelegate

    def fini(self):
        super(ReadOnlySetting, self).fini()
        self.readerDelegate = None
        return

    def _get(self):
        return self.readerDelegate()


class SoundSetting(SettingAbstract):
    VOLUME_MULT = 100

    def __init__(self, soundGroup, isPreview=False):
        super(SoundSetting, self).__init__(isPreview)
        self.group = soundGroup

    def __toGuiVolume(self, volume):
        return round(volume * self.VOLUME_MULT)

    def __toSysVolume(self, volume):
        return float(volume) / self.VOLUME_MULT

    def _get(self):
        return self.__toGuiVolume(SoundGroups.g_instance.getMasterVolume()) if self.group == 'master' else self.__toGuiVolume(SoundGroups.g_instance.getVolume(self.group))

    def _set(self, value):
        return SoundGroups.g_instance.setMasterVolume(self.__toSysVolume(value)) if self.group == 'master' else SoundGroups.g_instance.setVolume(self.group, self.__toSysVolume(value))


class SoundEnableSetting(SettingAbstract):
    """
    Enable/disable sound system in general
    """
    soundsCtrl = dependency.descriptor(ISoundsController)

    def getApplyMethod(self, value):
        return APPLY_METHOD.RESTART

    def _get(self):
        return self.soundsCtrl.isEnabled()

    def _set(self, value):
        if bool(value):
            self.soundsCtrl.enable()
        else:
            self.soundsCtrl.disable()


class VOIPMasterSoundSetting(SoundSetting):

    def __init__(self, isPreview=False):
        super(VOIPMasterSoundSetting, self).__init__('masterVivox', isPreview)

    def _set(self, value):
        super(VOIPMasterSoundSetting, self)._set(value)
        VOIP.getVOIPManager().setMasterVolume(value)


class VOIPMicSoundSetting(SoundSetting):

    def __init__(self, isPreview=False):
        super(VOIPMicSoundSetting, self).__init__('micVivox', isPreview)

    def _set(self, value):
        super(VOIPMicSoundSetting, self)._set(value)
        VOIP.getVOIPManager().setMicrophoneVolume(value)


class VibroSetting(SettingAbstract):
    GAIN_MULT = 100
    DEFAULT_GAIN = 0

    def __init__(self, vibroGroup, isPreview=False):
        super(VibroSetting, self).__init__(isPreview)
        self.group = vibroGroup

    def __toGuiVolume(self, volume):
        return round(volume * self.GAIN_MULT)

    def __toSysVolume(self, volume):
        return float(volume) / self.GAIN_MULT

    def _get(self):
        vm = VibroManager.g_instance
        return self.__toGuiVolume(vm.getGain()) if self.group == 'master' else self.__toGuiVolume(vm.getGroupGain(self.group, self.DEFAULT_GAIN))

    def _set(self, value):
        vm = VibroManager.g_instance
        return vm.setGain(self.__toSysVolume(value)) if self.group == 'master' else vm.setGroupGain(self.group, self.__toSysVolume(value))


class RegularSetting(SettingAbstract):

    def __init__(self, settingName, isPreview=False):
        super(RegularSetting, self).__init__(isPreview)
        self.settingName = settingName
        self._default = self.getDefaultValue()


class AccountSetting(SettingAbstract):

    def __init__(self, key, subKey=None):
        self.key = key
        self.subKey = subKey
        super(AccountSetting, self).__init__(False)

    def _getSettings(self):
        return AccountSettings.getSettings(self.key)

    def _get(self):
        return self._getSettings() if self.subKey is None else self._getSettings().get(self.subKey)

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

    def __init__(self, settingName, storage, isPreview=False):
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

    def __init__(self, settingName, key, subKey=None, isPreview=False):
        AccountSetting.__init__(self, key, subKey)
        DumpSetting.__init__(self, settingName, isPreview=isPreview)

    def _get(self):
        if BattleReplay.isPlaying():
            return self.getDumpedValue()
        else:
            return super(AccountDumpSetting, self)._get()

    def _save(self, value):
        if BattleReplay.isPlaying():
            self.setDumpedValue(value)
        return super(AccountDumpSetting, self)._save(value)


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

    def __init__(self, sectionName=None, isPreview=False):
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
        return section.readBool(self.sectionName, default) if section is not None else default

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
        return section.readString(self.sectionName, str(default)) if section is not None else default

    def _writeValue(self, section, value):
        if section is not None:
            return section.writeString(self.sectionName, str(value))
        else:
            LOG_WARNING('Section is not defined', section)
            return False

    def getDefaultValue(self):
        pass


class UserPrefsFloatSetting(UserPrefsSetting):

    def _readValue(self, section):
        default = self.getDefaultValue()
        return section.readFloat(self.sectionName, float(default)) if section is not None else default

    def _writeValue(self, section, value):
        if section is not None:
            return section.writeFloat(self.sectionName, float(value))
        else:
            LOG_WARNING('Section is not defined', section)
            return False

    def getDefaultValue(self):
        pass


class PreferencesSetting(SettingAbstract):

    def __init__(self, isPreview=False):
        super(PreferencesSetting, self).__init__(isPreview)
        BigWorld.wg_setSavePreferencesCallback(self._savePrefsCallback)

    def _savePrefsCallback(self, prefsRoot):
        pass


class PostProcessingSetting(StorageDumpSetting):

    def __init__(self, settingName, settingKey, storage, isPreview=False):
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

    def __init__(self, settingName, key, subKey, storage, isPreview=False):
        self._settingKey = key
        self._settingSubKey = subKey
        super(PlayersPanelSetting, self).__init__(settingName, storage, isPreview)

    def getDefaultValue(self):
        return AccountSettings.getSettingsDefault(self._settingKey).get(self._settingSubKey)


class VOIPSetting(AccountSetting):

    def __init__(self, isPreview=False):
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

    def __init__(self, isPreview=False):
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
        return options.index(deviceName) if deviceName in options else -1


class VOIPSupportSetting(ReadOnlySetting):

    def __init__(self):
        super(VOIPSupportSetting, self).__init__(self.__isSupported)

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def __isVoiceChatReady(self):
        return self.bwProto.voipController.isReady()

    def __isSupported(self):
        return VOIP.getVOIPManager().getVOIPDomain() != '' and self.__isVoiceChatReady()


class MessengerSetting(StorageDumpSetting):

    def getDefaultValue(self):
        data = messenger_settings.userPrefs._asdict()
        return data[self.settingName] if self.settingName in data else None


class MessengerDateTimeSetting(MessengerSetting):

    def __init__(self, bit, storage=None):
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
    clanCtrl = dependency.descriptor(IClanController)

    def _get(self):
        return super(ClansSetting, self)._get() if self.clanCtrl.isEnabled() else None

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

    def __init__(self, isPreview=False):
        super(CustomAASetting, self).__init__(isPreview)
        self.__customAAModes = BigWorld.getSupportedCustomAAModes()

    def __getModeIndex(self, mode):
        return self.__customAAModes.index(mode) if mode in self.__customAAModes else -1

    def __getModeByIndex(self, modeIndex):
        return self.__customAAModes[int(modeIndex)] if len(self.__customAAModes) > modeIndex > -1 else None

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

    def __init__(self, isPreview=False):
        super(MultisamplingSetting, self).__init__(isPreview)
        self.__multisamplingTypes = BigWorld.getSupportedMultisamplingTypes()
        self.__multisamplingTypes.insert(0, 0)

    def __getMSTypeIndex(self, msType):
        return self.__multisamplingTypes.index(msType) if msType in self.__multisamplingTypes else -1

    def __getMSTypeByIndex(self, msTypeIndex):
        return self.__multisamplingTypes[int(msTypeIndex)] if len(self.__multisamplingTypes) > msTypeIndex > -1 else None

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

    def __init__(self, isPreview=False):
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
        return 100 if value > 100 else value


class LensEffectSetting(StorageDumpSetting):

    def getDefaultValue(self):
        return SniperControlMode._LENS_EFFECTS_ENABLED

    def setSystemValue(self, value):
        SniperControlMode.enableLensEffects(value)


class GraphicSetting(SettingAbstract):
    MIN_OPTION_VALUE = 4

    def __init__(self, settingName, isPreview=False):
        super(GraphicSetting, self).__init__(isPreview)
        self.name = settingName
        self._currentValue = graphics.getGraphicsSetting(self.name)

    def _get(self):
        return self._currentValue.value if self._currentValue is not None else None

    def _getOptions(self):
        if self._currentValue is not None:
            if self._currentValue.isArray:
                return self._currentValue.options
            else:
                options = []
                for label, data, advanced, supported in self._currentValue.options:
                    options.append({'label': '#settings:graphicsSettingsOptions/%s' % str(label),
                     'data': data,
                     'advanced': advanced,
                     'supported': supported})

                return sorted(options, key=itemgetter('data'), reverse=True)
        return

    def _set(self, value):
        value = int(value)
        originalValue = value
        while not self._tryToSetValue(value) and value <= self.MIN_OPTION_VALUE:
            value = value + 1

        if originalValue != value:
            LOG_NOTE('Adjusted value has been set: `%s`' % value)

    def _save(self, value):
        super(GraphicSetting, self)._save(value)
        self._currentValue = graphics.getGraphicsSetting(self.name)

    def _tryToSetValue(self, value):
        try:
            BigWorld.setGraphicsSetting(self.name, value)
        except Exception:
            LOG_ERROR('Unable to set value `%s` for option `%s`' % (value, self.name))
            return False

        return True

    def getApplyMethod(self, value):
        return BigWorld.getGraphicsSettingApplyMethod(self.name, value)

    def refresh(self):
        self._currentValue = graphics.getGraphicsSetting(self.name)
        super(GraphicSetting, self).refresh()


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


class MonitorSetting(SettingAbstract):

    def __init__(self, isPreview=False, storage=None):
        super(MonitorSetting, self).__init__(isPreview)
        self._storage = weakref.proxy(storage)

    def _get(self):
        return self._storage.monitor

    def _set(self, value):
        self._storage.monitor = int(value)

    def _getOptions(self):
        return BigWorld.wg_getMonitorNames()

    def pack(self):
        result = super(MonitorSetting, self).pack()
        result.update({'real': g_monitorSettings.activeMonitor})
        return result


class BorderlessSizeSettings(SettingAbstract):

    def _get(self):
        pass

    def _getOptions(self):
        result = []
        for modes in g_monitorSettings.getBorderlessSizes():
            modeLabels = []
            for mode in modes:
                modeLabels.append('%dx%s' % (mode.width, mode.height))

            result.append(modeLabels)

        return result


class WindowSizeSetting(SettingAbstract):

    def __init__(self, isPreview=False, storage=None):
        super(WindowSizeSetting, self).__init__(isPreview)
        self.__lastSelectedWindowSize = None
        self._storage = weakref.proxy(storage)
        return

    def _get(self):
        size = self._storage.windowSize
        return self.__getWindowSizeIndex(*size) if size is not None else None

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

    def __getWindowSizeIndex(self, width, height):
        for index, (w, h) in enumerate(self.__getWindowSizes()):
            if w == width and h == height:
                return index

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


class ResolutionSetting(PreferencesSetting):

    def __init__(self, isPreview=False, storage=None):
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

    def _get(self):
        resolution = self._storage.resolution
        return self.__getResolutionIndex(*resolution) if resolution is not None else None

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

    def __init__(self, isPreview=False, storage=None):
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


class VideoModeSettings(PreferencesSetting):

    def __init__(self, storage):
        super(PreferencesSetting, self).__init__()
        self._storage = weakref.proxy(storage)
        self.__videoMode = self._get()

    def isFullscreen(self):
        return self.__videoMode == BigWorld.WindowModeExclusiveFullscreen

    def isWindowed(self):
        return self.__videoMode == BigWorld.WindowModeWindowed

    def isBorderless(self):
        return self.__videoMode == BigWorld.WindowModeBorderless

    def getInt(self):
        return self.__videoMode

    def _getOptions(self):
        result = []
        for data, label in ((BigWorld.WindowModeWindowed, 'windowed'), (BigWorld.WindowModeExclusiveFullscreen, 'fullscreen'), (BigWorld.WindowModeBorderless, 'borderless')):
            result.append({'data': data,
             'label': '#settings:screenMode/%s' % label})

        return result

    def _get(self):
        return self._storage.windowMode

    def _set(self, value):
        self._storage.windowMode = value

    def _save(self, value):
        self.__videoMode = value

    def _savePrefsCallback(self, prefsRoot):
        if g_monitorSettings.isMonitorChanged:
            prefsRoot['devicePreferences'].writeInt('windowMode', self.__videoMode)


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
            assert mType in cls.TYPES.ALL() and mOption in cls.PARAMS.ALL()
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

    def pack(self):
        return self.__getMarkerSettings(forcePackingHP=True)

    def _get(self):
        return self.__getMarkerSettings(forcePackingHP=False)

    def __getMarkerSettings(self, forcePackingHP=False):
        marker = {}
        for mType in self.OPTIONS.TYPES.ALL():
            for param in self.OPTIONS.PARAMS.ALL():
                on = self.OPTIONS.getOptionName(mType, param)
                default = self._default[on]
                if BattleReplay.isPlaying():
                    value = BattleReplay.g_replayCtrl.getSetting(self.settingName, {}).get(on, default)
                else:
                    value = self._storage.extract(self.settingName, on, self._default[on])
                if param == self.OPTIONS.PARAMS.HP and forcePackingHP:
                    marker[on] = self.PackStruct(value, [ '#settings:marker/hp/type%d' % mid for mid in xrange(4) ])._asdict()
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
        ZOOM_INDICATOR = 'zoomIndicator'

    VIRTUAL_OPTIONS = {OPTIONS.MIXING_TYPE: (OPTIONS.MIXING, 4),
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
            types = [ {'loc': makeString('#settings:aim/%s/type%d' % (name, i)),
             'label': '#settings:aim/%s/type%d' % (name, i),
             'index': i} for i in xrange(int(optsLen)) ]
            types = sorted(types, key=itemgetter('loc'))
            for item in types:
                item.pop('loc', None)

            result[vname] = self.PackStruct(result[vname], types)._asdict()

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
        return self.VEHICLE_MODELS_TYPES.index(self.OPTIONS.ALWAYS)


class CarouselTypeSetting(StorageDumpSetting):

    class OPTIONS(CONST_CONTAINER):
        SINGLE = 'single'
        DOUBLE = 'double'

    CAROUSEL_TYPES = (OPTIONS.SINGLE, OPTIONS.DOUBLE)

    def _getOptions(self):
        settingsKey = '#settings:game/%s/%s'
        return [ {'label': settingsKey % (self.settingName, cType)} for cType in self.CAROUSEL_TYPES ]

    def getDefaultValue(self):
        return self.CAROUSEL_TYPES.index(self.OPTIONS.SINGLE)

    def getRowCount(self):
        return self._get() + 1


class BattleLoadingTipSetting(AccountDumpSetting):

    class OPTIONS(CONST_CONTAINER):
        TEXT = 'textTip'
        VISUAL = 'visualTip'
        MINIMAP = 'minimap'
        TIPS_TYPES = (TEXT, VISUAL, MINIMAP)

    def getSettingID(self, isVisualOnly=False, isFallout=False):
        if isVisualOnly:
            return self.OPTIONS.VISUAL
        settingID = self.OPTIONS.TIPS_TYPES[self._get()]
        if isFallout and settingID == BattleLoadingTipSetting.OPTIONS.VISUAL:
            settingID = BattleLoadingTipSetting.OPTIONS.TEXT
        return settingID

    def _getOptions(self):
        settingsKey = '#settings:game/%s/%s'
        return [ settingsKey % (self.settingName, type) for type in self.OPTIONS.TIPS_TYPES ]


class ShowMarksOnGunSetting(StorageAccountSetting):

    def _get(self):
        return not super(ShowMarksOnGunSetting, self)._get()

    def _set(self, value):
        return super(ShowMarksOnGunSetting, self)._set(not value)

    def getDefaultValue(self):
        return True


class ControlSetting(SettingAbstract):
    ControlPackStruct = namedtuple('ControlPackStruct', 'current default')

    def __init__(self, isPreview=False):
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

    def __init__(self, mode, setting, default, isPreview=False):
        super(MouseSetting, self).__init__(isPreview)
        self.mode = mode
        self.setting = setting
        self.default = default
        self.__aihSection = ResMgr.openSection(_INPUT_HANDLER_CFG)

    def getCamera(self):
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

    def __isControlModeAccessible(self):
        return BigWorld.player() is not None and hasattr(BigWorld.player(), 'inputHandler') and hasattr(BigWorld.player().inputHandler, 'ctrls')

    def _getDefault(self):
        return self.default

    def _get(self):
        camera = self.getCamera()
        return camera.getUserConfigValue(self.setting) if camera is not None else self.default

    def _set(self, value):
        camera = self.getCamera()
        if camera is None:
            LOG_WARNING('Error while applying mouse settings: empty camera', self.mode, self.setting)
            return
        else:
            camera.setUserConfigValue(self.setting, value)
            if not self.__isControlModeAccessible():
                camera.writeUserPreferences()
            return


class MouseSensitivitySetting(MouseSetting):

    def __init__(self, mode):
        super(MouseSensitivitySetting, self).__init__(mode, 'sensitivity', 1.0)


class DynamicFOVMultiplierSetting(MouseSetting):

    def __init__(self, isPreview=False):
        super(DynamicFOVMultiplierSetting, self).__init__('arcade', 'fovMultMinMaxDist', self.getDefaultValue(), isPreview)

    def _set(self, value):
        value = ArcadeCamera.MinMax(min=value, max=1.0)
        super(DynamicFOVMultiplierSetting, self)._set(value)

    def setSystemValue(self, value):
        self._set(value)

    def getDefaultValue(self):
        return ArcadeCamera.MinMax(min=1.0, max=1.0)


class FOVSetting(RegularSetting):

    def __init__(self, settingName, isPreview=False, storage=None):
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

    def __init__(self, isPreview=False):
        super(StaticFOVSetting, self).__init__(Settings.KEY_FOV, isPreview)

    def _get(self):
        return int(super(StaticFOVSetting, self)._get())

    def _save(self, value):
        super(StaticFOVSetting, self)._save(int(value))

    def getDefaultValue(self):
        return round(math.degrees(FovExtended.instance().defaultHorizontalFov))


class DynamicFOVSetting(UserPrefsStringSetting):
    DEFAULT = (80, 100)

    def __init__(self, isPreview=False):
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

    def __init__(self, isPreview=False, storage=None):
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

    def __init__(self, settingName, settingKey, storage, isPreview=False):
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

    def __init__(self, storage, isPreview=False):
        super(BackDraftInversionSetting, self).__init__('backDraftInvert', storage, isPreview)

    def _getDefault(self):
        return self._default

    def setSystemValue(self, value):
        if isPlayerAvatar():
            BigWorld.player().invRotationOnBackMovement = value


class KeyboardSetting(ControlSetting):

    def __init__(self, cmd):
        super(KeyboardSetting, self).__init__()
        self.cmd = cmd

    @app_getter
    def app(self):
        return None

    def _getDefault(self):
        command = CommandMapping.g_instance.getCommand(self.cmd)
        return getScaleformKey(CommandMapping.g_instance.getDefaults().get(command, Keys.KEY_NONE))

    def getDefaultValue(self):
        command = CommandMapping.g_instance.getCommand(self.cmd)
        return CommandMapping.g_instance.getDefaults().get(command, Keys.KEY_NONE)

    def _set(self, value):
        return self.setSystemValue(value)

    def _get(self):
        return getScaleformKey(self.getCurrentMapping())

    def setSystemValue(self, value):
        key = 'KEY_NONE'
        if value is not None:
            key = getBigworldNameFromKey(getBigworldKey(value))
        LOG_DEBUG('Settings key command', self.cmd, value, key)
        if self.cmd == 'CMD_VOICECHAT_MUTE' and self.app.gameInputManager is not None:
            self.app.gameInputManager.updateChatKeyHandlers(value)
        CommandMapping.g_instance.remove(self.cmd)
        CommandMapping.g_instance.add(self.cmd, key)
        return

    def getCurrentMapping(self):
        mapping = CommandMapping.g_instance.get(self.cmd)
        if mapping is None:
            mapping = self.getDefaultValue()
        return mapping


class KeyboardSettings(SettingsContainer):
    KEYS_LAYOUT = (('movement', (('forward', 'CMD_MOVE_FORWARD'),
       ('backward', 'CMD_MOVE_BACKWARD'),
       ('left', 'CMD_ROTATE_LEFT'),
       ('right', 'CMD_ROTATE_RIGHT'),
       ('auto_rotation', 'CMD_CM_VEHICLE_SWITCH_AUTOROTATION'),
       ('block_tracks', 'CMD_BLOCK_TRACKS'))),
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
     ('shortcuts', (('my_target/follow_me', 'CMD_CHAT_SHORTCUT_ATTACK_MY_TARGET'),
       ('attack', 'CMD_CHAT_SHORTCUT_ATTACK'),
       ('to_base/to_back', 'CMD_CHAT_SHORTCUT_BACKTOBASE'),
       ('positive', 'CMD_CHAT_SHORTCUT_POSITIVE'),
       ('negative', 'CMD_CHAT_SHORTCUT_NEGATIVE'),
       ('sos/help_me', 'CMD_CHAT_SHORTCUT_HELPME'),
       ('reload/stop', 'CMD_CHAT_SHORTCUT_RELOAD'))),
     ('camera', (('camera_up', 'CMD_CM_CAMERA_ROTATE_UP'),
       ('camera_down', 'CMD_CM_CAMERA_ROTATE_DOWN'),
       ('camera_left', 'CMD_CM_CAMERA_ROTATE_LEFT'),
       ('camera_right', 'CMD_CM_CAMERA_ROTATE_RIGHT'))),
     ('voicechat', (('pushToTalk', 'CMD_VOICECHAT_MUTE'), ('voicechat_enable', 'CMD_VOICECHAT_ENABLE'))),
     ('logitech_keyboard', (('switch_view', 'CMD_LOGITECH_SWITCH_VIEW'),)),
     ('minimap', (('sizeUp', 'CMD_MINIMAP_SIZE_UP'), ('sizeDown', 'CMD_MINIMAP_SIZE_DOWN'), ('visible', 'CMD_MINIMAP_VISIBLE'))))
    IMPORTANT_BINDS = ('forward', 'backward', 'left', 'right', 'fire', 'item01', 'item02', 'item03', 'item04', 'item05', 'item06', 'item07', 'item08')
    KEYS_TOOLTIPS = {'my_target/follow_me': 'SettingsKeyFollowMe',
     'to_base/to_back': 'SettingsKeyTurnBack',
     'sos/help_me': 'SettingsKeyNeedHelp',
     'reload/stop': 'SettingsKeyReload',
     'auto_rotation': 'SettingKeySwitchMode'}
    __hiddenGroups = {'logitech_keyboard'}

    def __init__(self):
        if not GUI_SETTINGS.minimapSize:
            self.hideGroup('minimap', hide=True)
        if not GUI_SETTINGS.voiceChat:
            self.hideGroup('voicechat', hide=True)
        settings = [('keysLayout', ReadOnlySetting(lambda : self._getLayout())), ('keysTooltips', ReadOnlySetting(lambda : self.KEYS_TOOLTIPS))]
        for group in self._getLayout(True):
            for setting in group['values']:
                settings.append((setting['key'], KeyboardSetting(setting['cmd'])))

        super(KeyboardSettings, self).__init__(tuple(settings))
        self.onKeyBindingsChanged = Event()

    def fini(self):
        self.onKeyBindingsChanged.clear()
        super(KeyboardSettings, self).fini()

    @classmethod
    def _getLayout(cls, isFull=False):
        layout = []
        for groupName, groupValues in cls.KEYS_LAYOUT:
            if not isFull:
                if groupName in cls.__hiddenGroups:
                    continue
            layout.append({'key': groupName,
             'values': [ cls.__mapValues(*x) for x in groupValues ]})

        return layout

    @classmethod
    def getKeyboardImportantBinds(cls):
        return cls.IMPORTANT_BINDS

    @classmethod
    def hideGroup(cls, group, hide):
        if hide:
            LOG_DEBUG('Hide settings group', group)
            cls.__hiddenGroups.add(group)
        else:
            LOG_DEBUG('Reveal settings group', group)
            cls.__hiddenGroups.remove(group)

    @classmethod
    def isGroupHidden(cls, group):
        return group in cls.__hiddenGroups

    def apply(self, values, names=None):
        super(KeyboardSettings, self).apply(values, names)
        CommandMapping.g_instance.onMappingChanged(values)
        CommandMapping.g_instance.save()
        self.onKeyBindingsChanged()

    def getCurrentMapping(self):
        mapping = {}
        for _, setting in self.settings:
            if isinstance(setting, KeyboardSetting):
                mapping[setting.cmd] = setting.getCurrentMapping()

        return mapping

    def getDefaultMapping(self):
        mapping = {}
        for _, setting in self.settings:
            if isinstance(setting, KeyboardSetting):
                mapping[setting.cmd] = setting.getDefaultValue()

        return mapping

    @classmethod
    def __mapValues(cls, key, cmd):
        """
        There are also description for keys available:
        'descr' - is a list of {'header': ..., 'label': ...}
        """
        return {'key': key,
         'cmd': cmd}


class FPSPerfomancerSetting(StorageDumpSetting):

    def getDefaultValue(self):
        return BigWorld.getGraphicsSetting('PS_USE_PERFORMANCER')

    def setSystemValue(self, value):
        try:
            BigWorld.setGraphicsSetting('PS_USE_PERFORMANCER', bool(value))
        except Exception:
            LOG_CURRENT_EXCEPTION()


class _BaseSoundPresetSetting(AccountDumpSetting):

    def __init__(self, actionsMap, settingName, key, subKey=None, isPreview=False):
        """
        :param actionsMap: [tuple]. Each element have to be tuple of two elements: method and arguments for this method
        :param settingName: [str] setting name
        :param key: [str] account setting section name
        :param subKey: [str] account setting subsection name
        :param isPreview: [bool] is preview available. It means that value is changed by player selection, and
            it is saved if player applies changes, otherwise - value is changed and saved only
            if player applies changes.
        """
        super(_BaseSoundPresetSetting, self).__init__(settingName, key, subKey, isPreview=isPreview)
        self.__actionsMap = actionsMap

    def setSystemValue(self, value):
        try:
            func, args = self.__actionsMap[value]
            if args is not None:
                func(args)
            else:
                func()
        except IndexError:
            LOG_ERROR(self, 'Unsupported value: %s' % value)

        return

    def fini(self):
        self.__actionsMap = None
        super(_BaseSoundPresetSetting, self).fini()
        return

    def _set(self, value):
        if value < len(self.__actionsMap):
            super(_BaseSoundPresetSetting, self)._set(value)
            self.setSystemValue(value)

    def _save(self, value):
        if value < len(self.__actionsMap):
            super(_BaseSoundPresetSetting, self)._save(value)


_SPEAKER_PRESET_CONFIG = ((ACOUSTICS.TYPE_ACOUSTIC_20, SPEAKERS_CONFIG.SPEAKER_SETUP_2_0),
 (ACOUSTICS.TYPE_ACOUSTIC_51, SPEAKERS_CONFIG.SPEAKER_SETUP_5_1),
 (ACOUSTICS.TYPE_ACOUSTIC_71, SPEAKERS_CONFIG.SPEAKER_SETUP_7_1),
 (ACOUSTICS.TYPE_AUTO, SPEAKERS_CONFIG.AUTO_DETECTION))

def _makeSoundPresetIDsSeq():
    """Gets all available IDs of preset in service layer
    in order that they are displayed in settings window.
    :return: list containing SPEAKERS_CONFIG.*.
    """
    return map(lambda item: item[1], _SPEAKER_PRESET_CONFIG)


def _makeSoundGuiIDsSeq():
    """Gets all available IDs of preset in GUI
    in order that they are displayed in settings window.
    :return:
    """
    return map(lambda item: item[0], _SPEAKER_PRESET_CONFIG)


def _makeSoundPresetIDToGuiID():
    return dict(map(lambda item: (item[1], item[0]), _SPEAKER_PRESET_CONFIG))


class SoundDevicePresetSetting(_BaseSoundPresetSetting):
    soundsCtrl = dependency.descriptor(ISoundsController)

    def __init__(self, settingName, key, subKey=None, isPreview=False):
        super(SoundDevicePresetSetting, self).__init__(((self.soundsCtrl.system.setSoundSystem, 0), (self.soundsCtrl.system.setSoundSystem, 1), (self.soundsCtrl.system.setSoundSystem, 2)), settingName, key, subKey=subKey, isPreview=isPreview)

    def _getOptions(self):
        options = []
        selectedID = self.soundsCtrl.system.getUserSpeakersPresetID()
        if selectedID == SPEAKERS_CONFIG.AUTO_DETECTION:
            selectedID = self.soundsCtrl.system.getSystemSpeakersPresetID()
        mapping = _makeSoundPresetIDToGuiID()
        if selectedID in mapping:
            acousticType = mapping[selectedID]
        else:
            LOG_ERROR('Selected preset is unresolved', selectedID)
            acousticType = ACOUSTICS.TYPE_ACOUSTICS

        def iterator():
            yield (ACOUSTICS.TYPE_ACOUSTICS, acousticType)
            yield (ACOUSTICS.TYPE_HEADPHONES,) * 2
            yield (ACOUSTICS.TYPE_LAPTOP,) * 2

        for baseID, selectedID in iterator():
            options.append({'id': baseID,
             'label': SETTINGS.sounds_sounddevice(selectedID),
             'image': '../maps/icons/settings/{}.png'.format(baseID),
             'tooltip': SETTINGS.sounds_sounddevice(selectedID),
             'speakerId': selectedID})

        return options


class SoundSpeakersPresetSetting(SettingAbstract):
    soundsCtrl = dependency.descriptor(ISoundsController)

    def getSystemPreset(self):
        selectedID = self.soundsCtrl.system.getSystemSpeakersPresetID()
        mapping = _makeSoundPresetIDToGuiID()
        if selectedID in mapping:
            return mapping[selectedID]
        else:
            LOG_ERROR('Selected preset is unresolved', selectedID)
            return ACOUSTICS.TYPE_ACOUSTIC_20

    def isPresetSupportedByIndex(self, index):
        presetIDs = _makeSoundPresetIDsSeq()
        if index < len(presetIDs):
            if self.soundsCtrl.system.getUserSpeakersPresetID() == SPEAKERS_CONFIG.AUTO_DETECTION:
                return presetIDs[index] <= self.soundsCtrl.system.getSystemSpeakersPresetID()
            else:
                return True
        else:
            return False

    def _get(self):
        presetID = self.soundsCtrl.system.getUserSpeakersPresetID()
        presetIDs = _makeSoundPresetIDsSeq()
        if presetID in presetIDs:
            return presetIDs.index(presetID)
        else:
            LOG_ERROR('Index of selected preset is not found', presetID)
            return None
            return None

    def _set(self, value):
        value = int(value)
        presetIDs = _makeSoundPresetIDsSeq()
        if value < len(presetIDs):
            self.soundsCtrl.system.setUserSpeakersPresetID(presetIDs[value])
        else:
            LOG_ERROR('Index of selected preset is invalid', value)

    def _getOptions(self):
        options = []
        for guiID in _makeSoundGuiIDsSeq():
            label = SETTINGS.sounds_acoustictype(guiID)
            device = SETTINGS.sounds_sounddevice(guiID)
            options.append({'id': guiID,
             'label': label,
             'tooltip': device,
             'isAutodetect': guiID == ACOUSTICS.TYPE_AUTO})

        return options


class SoundQualitySetting(AccountSetting):

    def __init__(self):
        super(SoundQualitySetting, self).__init__(SOUND.LOW_QUALITY)

    @classmethod
    def isAvailable(cls):
        return True

    def _set(self, isEnabled):
        self.setSystemValue(isEnabled)
        super(SoundQualitySetting, self)._set(isEnabled)

    def setSystemValue(self, isEnabled):
        WWISE.WW_setLowQuality(isEnabled)


class BassBoostSetting(AccountSetting):
    """
    Enable/disable bass boost WOTD-64517
    """
    soundsCtrl = dependency.descriptor(ISoundsController)

    def __init__(self):
        super(BassBoostSetting, self).__init__(SOUND.BASS_BOOST)

    def _set(self, isEnabled):
        self.setSystemValue(isEnabled)
        super(BassBoostSetting, self)._set(isEnabled)

    def setSystemValue(self, isEnabled):
        self.soundsCtrl.system.setBassBoost(isEnabled)


class NightModeSetting(AccountSetting):
    soundsCtrl = dependency.descriptor(ISoundsController)

    def __init__(self):
        super(NightModeSetting, self).__init__(SOUND.NIGHT_MODE)

    def setSystemValue(self, isEnabled):
        if isEnabled:
            self.soundsCtrl.system.disableDynamicPreset()
        else:
            self.soundsCtrl.system.enableDynamicPreset()

    def _set(self, isEnabled):
        self.setSystemValue(isEnabled)
        super(NightModeSetting, self)._set(isEnabled)


class DetectionAlertSound(AccountSetting):
    _DetectionAlertPackStruct = namedtuple('_DetectionAlertPackStruct', 'current options extraData')
    _WWISE_EVENTS = ('lightbulb', 'lightbulb_02', 'sixthSense')
    _CUSTOM_EVENT_FILE = 'audioww/sixthSense.mp3'

    def __init__(self):
        super(DetectionAlertSound, self).__init__(SOUND.DETECTION_ALERT_SOUND)
        self.__previewSound = None
        return

    def playPreviewSound(self, eventIdx):
        eventToPlay = self._WWISE_EVENTS[eventIdx]
        if self.__previewSound is not None:
            playingEvent = self.__previewSound.name.split(':')[1]
            if self._WWISE_EVENTS.index(playingEvent) != eventIdx:
                self.clearPreviewSound()
                self.__previewSound = SoundGroups.g_instance.getSound2D(eventToPlay)
                self.__previewSound.play()
            else:
                if playingEvent != 'sixthSense':
                    self.clearPreviewSound()
                    self.__previewSound = SoundGroups.g_instance.getSound2D(eventToPlay)
                self.__previewSound.play()
        else:
            self.__previewSound = SoundGroups.g_instance.getSound2D(eventToPlay)
            self.__previewSound.play()
        return

    def clearPreviewSound(self):
        if self.__previewSound is not None:
            self.__previewSound.stop()
            self.__previewSound = None
        return

    def getEventName(self):
        return self._WWISE_EVENTS[self._get()]

    def pack(self):
        return self._DetectionAlertPackStruct(self._get(), self._getOptions(), self._getExtraData())._asdict()

    def _getOptions(self):
        options = []
        for sample in self._WWISE_EVENTS:
            options.append('#settings:sound/{}/{}'.format(SOUND.DETECTION_ALERT_SOUND, sample))

        return options

    def _getExtraData(self):
        """ Gather information about ability to preview the options.
        """
        extraData = []
        for sample in self._WWISE_EVENTS:
            if sample == 'sixthSense':
                canPreview = bool(ResMgr.isFile(self._CUSTOM_EVENT_FILE))
            else:
                canPreview = True
            extraData.append(canPreview)

        return extraData

    def _get(self):
        return self._WWISE_EVENTS.index(super(DetectionAlertSound, self)._get())

    def _save(self, eventIdx):
        super(DetectionAlertSound, self)._save(self._WWISE_EVENTS[eventIdx])


class AltVoicesSetting(StorageDumpSetting):
    ALT_VOICES_PREVIEW = itertools.cycle(('wwsound_mode_preview01', 'wwsound_mode_preview02', 'wwsound_mode_preview03'))
    DEFAULT_IDX = 0
    PREVIEW_SOUNDS_COUNT = 3

    class SOUND_MODE_TYPE:
        UNKNOWN = 0
        REGULAR = 1
        NATIONAL = 2

    def __init__(self, settingName, storage):
        super(AltVoicesSetting, self).__init__(settingName, storage, True)
        self.__previewSound = None
        self.__lastPreviewedValue = None
        self._handlers = {self.SOUND_MODE_TYPE.UNKNOWN: lambda *args: False,
         self.SOUND_MODE_TYPE.REGULAR: self.__applyRegularMode,
         self.SOUND_MODE_TYPE.NATIONAL: self.__applyNationalMode}
        self.__previewNations = []
        return

    @app_getter
    def app(self):
        return None

    def fini(self):
        super(AltVoicesSetting, self).fini()
        self._handlers.clear()

    def playPreviewSound(self, soundMgr=None):
        if self.isSoundModeValid():
            self.clearPreviewSound()
            sndMgr = soundMgr or self.app.soundManager
            if sndMgr is None:
                LOG_ERROR('GUI sound manager is not found')
                return
            sndPath = sndMgr.sounds.getEffectSound(next(self.ALT_VOICES_PREVIEW))
            if SoundGroups.g_instance.soundModes.currentNationalPreset[1]:
                g = functions.rnd_choice(*nations.AVAILABLE_NAMES)
                self.__previewNations = [next(g), next(g), next(g)]
                self.__previewSound = SoundGroups.g_instance.getSound2D(sndPath)
                if self.__previewSound is not None:
                    self.__previewSound.setCallback(self.playPreview)
                    self.playPreview(self.__previewSound)
                return True
            self.__previewSound = SoundGroups.g_instance.getSound2D(sndPath)
            if self.__previewSound is not None:
                self.__previewSound.play()
            return True
        else:
            return False

    def playPreview(self, sound):
        if len(self.__previewNations) and self.__previewSound == sound:
            nation = self.__previewNations.pop()
            SoundGroups.g_instance.soundModes.setCurrentNation(nation)
            sound.play()

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
        self.clearPreviewSound()

    def revert(self):
        super(AltVoicesSetting, self).revert()
        self.__lastPreviewedValue = self._get()
        self.clearPreviewSound()

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
        return value if value < len(modes) else self.DEFAULT_IDX

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
        return self.SOUND_MODE_TYPE.NATIONAL if soundMode.name in SoundGroups.g_instance.soundModes.nationalPresets else self.SOUND_MODE_TYPE.UNKNOWN

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

    def clearPreviewSound(self):
        if self.__previewSound is not None:
            self.__previewSound.stop()
            self.__previewSound = None
        player = BigWorld.player()
        if hasattr(player, 'vehicle'):
            vehicle = player.vehicle
            if vehicle is not None:
                player.vehicle.refreshNationalVoice()
        else:
            SoundGroups.g_instance.soundModes.setCurrentNation(SoundGroups.g_instance.soundModes.DEFAULT_NATION)
        return


class DynamicCamera(StorageDumpSetting):

    def getDefaultValue(self):
        return AvatarInputHandler.isCameraDynamic()


class SniperModeStabilization(StorageDumpSetting):

    def getDefaultValue(self):
        return AvatarInputHandler.isSniperStabilized()


class WindowsTarget4StoredData(SettingAbstract):

    def __init__(self, targetID, isPreview=False):
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
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, sectionName=None, isPreview=False):
        super(InterfaceScaleSetting, self).__init__(sectionName, isPreview)
        self.__interfaceScale = 0
        connectionManager.onDisconnected += self.onDisconnected
        connectionManager.onConnected += self.onConnected

    def get(self):
        self.__checkAndCorrectScaleValue(self.__interfaceScale)
        return self.__interfaceScale

    def getDefaultValue(self):
        return AccountSettings.getSettingsDefault(self.sectionName)

    def setSystemValue(self, value):
        self.__interfaceScale = value
        scale = self.settingsCore.interfaceScale.getScaleByIndex(value)
        width, height = GUI.screenResolution()[:2]
        event_dispatcher.changeAppResolution(width, height, scale)
        g_monitorSettings.setGlyphCache(scale)

    def onConnected(self):
        self.setSystemValue(super(InterfaceScaleSetting, self).get())

    def onDisconnected(self):
        self.setSystemValue(0)

    def _getOptions(self):
        return [self.__getScales(graphics.getSuitableWindowSizes(), BigWorld.wg_getCurrentResolution(True)), self.__getScales(graphics.getSuitableVideoModes()), self.__getScales(graphics.getSuitableBorderlessSizes())]

    def _set(self, value):
        super(InterfaceScaleSetting, self)._save(value)
        self.setSystemValue(value)

    def __getScales(self, modesVariety, additionalSize=None):
        result = []
        for i in xrange(len(modesVariety)):
            modes = sorted(set([ (mode.width, mode.height) for mode in modesVariety[i] ]))
            if additionalSize is not None:
                modes.append(additionalSize[0:2])
            result.append(map(graphics.getInterfaceScalesList, modes))

        return result

    def __checkAndCorrectScaleValue(self, value):
        scaleLength = len(self.settingsCore.interfaceScale.getScaleOptions())
        if value >= scaleLength:
            self.__interfaceScale = 0
            self._set(self.__interfaceScale)
            self.settingsCore.interfaceScale.scaleChanged()


class GraphicsQualityNote(SettingAbstract):
    note = '{0}{1}  {2}{3}'.format("<font face='$FieldFont' size='13' color='#595950'>", i18n.makeString(SETTINGS.GRAPHICSQUALITYHDSD_SD), icons.info(), '</font>')
    _GRAPHICS_QUALITY_TYPES = {CONTENT_TYPE.SD_TEXTURES: note,
     CONTENT_TYPE.TUTORIAL: note,
     CONTENT_TYPE.SANDBOX: note}

    def _get(self):
        return self._GRAPHICS_QUALITY_TYPES.get(ResMgr.activeContentType(), '')

    def _set(self, value):
        pass


class IncreasedZoomSetting(StorageAccountSetting):
    IncreasedZoomPackStruct = namedtuple('IncreasedZoomPackStruct', 'current options extraData')

    def __init__(self, settingName, storage, isPreview=False):
        super(IncreasedZoomSetting, self).__init__(settingName, storage, isPreview)
        self.__mouseSetting = MouseSetting('sniper', self.settingName, self.getDefaultValue())

    def getExtraData(self):
        zooms = self.__mouseSetting.getCamera().getConfigValue('zooms')[-2:]
        zoomStrs = [ i18n.makeString(SETTINGS.GAME_INCREASEDZOOM_ZOOMSTR, zoom=zoom) for zoom in zooms ]
        zoomStr = i18n.makeString(SETTINGS.GAME_INCREASEDZOOM_DELIMETER).join(zoomStrs)
        return {'checkBoxLabel': i18n.makeString(SETTINGS.GAME_INCREASEDZOOM_BASE, zooms=zoomStr),
         'tooltip': makeTooltip(TOOLTIPS.INCREASEDZOOM_HEADER, i18n.makeString(TOOLTIPS.INCREASEDZOOM_BODY, zooms=zoomStr))}

    def pack(self):
        return self.IncreasedZoomPackStruct(self._get(), self._getOptions(), self.getExtraData())._asdict()

    def setSystemValue(self, value):
        if BattleReplay.isPlaying():
            value = True
        self.__mouseSetting.apply(value)


class MouseAffectedSetting(RegularSetting):

    def __init__(self, settingName, isPreview=False):
        super(MouseAffectedSetting, self).__init__(settingName, isPreview)
        self._mouseSettings = map(lambda camera: MouseSetting(camera, self.settingName, self.getDefaultValue()), self._getCameras())

    def _getCameras(self):
        pass

    def setSystemValue(self, value):
        forEach(lambda mouseSetting: mouseSetting.apply(value), self._mouseSettings)


class SnipereModeByShiftSetting(StorageAccountSetting, MouseAffectedSetting):

    def _getCameras(self):
        pass


class GroupSetting(StorageDumpSetting):

    def __init__(self, settingName, storage, options, settingsKey, isPreview=False):
        super(GroupSetting, self).__init__(settingName, storage, isPreview)
        self._options = options
        self._settingsKey = settingsKey
        self._visibleOrder = self._getVisibleOrder()

    def getDefaultValue(self):
        v = super(GroupSetting, self).getDefaultValue()
        if v in self._visibleOrder:
            return v
        else:
            return self._visibleOrder[0] if self._visibleOrder else None

    def _getOptions(self):
        return [ self._getOptionData(key) for key in self._visibleOrder ]

    def _getVisibleOrder(self):
        return sorted(self._options.iterkeys())

    def _getOptionData(self, key):
        return {'label': self._getOptionLabel(key),
         'data': key}

    def _getOptionLabel(self, key):
        return self._settingsKey % str(self._options[key])


class DamageIndicatorTypeSetting(GroupSetting):
    OPTIONS = {0: 'standard',
     1: 'extended'}

    def __init__(self, settingName, storage, isPreview=False):
        super(DamageIndicatorTypeSetting, self).__init__(settingName, storage, options=self.OPTIONS, settingsKey='#settings:feedback/tab/damageIndicator/type/%s', isPreview=isPreview)

    def getDefaultValue(self):
        pass


class DamageIndicatorPresetsSetting(GroupSetting):
    OPTIONS = {0: 'all',
     1: 'withoutCrit'}

    def __init__(self, settingName, storage, isPreview=False):
        super(DamageIndicatorPresetsSetting, self).__init__(settingName, storage, options=self.OPTIONS, settingsKey='#settings:feedback/tab/damageIndicator/presets/%s', isPreview=isPreview)

    def getDefaultValue(self):
        pass


class DamageLogDetailsSetting(GroupSetting):
    OPTIONS = {0: 'always',
     1: 'byAlt',
     2: 'hide'}

    def __init__(self, settingName, storage, isPreview=False):
        super(DamageLogDetailsSetting, self).__init__(settingName, storage, options=self.OPTIONS, settingsKey='#settings:feedback/tab/damageLogPanel/details/%s', isPreview=isPreview)

    def getDefaultValue(self):
        pass
