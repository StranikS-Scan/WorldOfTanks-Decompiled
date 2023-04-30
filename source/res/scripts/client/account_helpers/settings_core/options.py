# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/settings_core/options.py
from enum import Enum
from typing import TYPE_CHECKING
import base64
import cPickle
import random
import sys
import fractions
import itertools
import weakref
from collections import namedtuple
from operator import itemgetter
import logging
from aih_constants import CTRL_MODE_NAME
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
from constants import CONTENT_TYPE, IS_CHINA
from gui.Scaleform.genConsts.ACOUSTICS import ACOUSTICS
from gui.app_loader import app_getter
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import event_dispatcher
from gui.sounds.sound_constants import SPEAKERS_CONFIG
from helpers import dependency
from helpers import isPlayerAvatar
from helpers.i18n import makeString
import nations
import CommandMapping
from helpers import i18n
from Event import Event
from AvatarInputHandler import INPUT_HANDLER_CFG, AvatarInputHandler
from AvatarInputHandler.DynamicCameras import ArcadeCamera, SniperCamera, StrategicCamera, ArtyCamera, DualGunCamera
from AvatarInputHandler.control_modes import PostMortemControlMode, SniperControlMode
from debug_utils import LOG_NOTE, LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_WARNING
from gui.Scaleform.managers.windows_stored_data import g_windowsStoredData
from messenger import g_settings as messenger_settings
from account_helpers.AccountSettings import AccountSettings, SPEAKERS_DEVICE
from account_helpers.settings_core.settings_constants import SOUND, SPGAimEntranceModeOptions
from messenger.storage import storage_getter
from shared_utils import CONST_CONTAINER, forEach
from gui import GUI_SETTINGS
from gui.shared.utils import graphics, functions, getPlayerDatabaseID
from gui.shared.utils.monitor_settings import g_monitorSettings
from gui.shared.utils.key_mapping import getScaleformKey, getBigworldKey, getBigworldNameFromKey
from gui.Scaleform.locale.SETTINGS import SETTINGS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import icons, text_styles
from gui.shared.utils.functions import makeTooltip, clamp
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.sounds import ISoundsController
from gui import makeHtmlString
from skeletons.gui.game_control import ISpecialSoundCtrl, IAnonymizerController, IVehiclePostProgressionController
if TYPE_CHECKING:
    from typing import Tuple as TTuple
_logger = logging.getLogger(__name__)

class APPLY_METHOD(object):
    NORMAL = 'normal'
    DELAYED = 'delayed'
    RESTART = 'restart'
    NEXT_BATTLE = 'next_battle'


def highestPriorityMethod(methods):
    if APPLY_METHOD.RESTART in methods:
        return APPLY_METHOD.RESTART
    if APPLY_METHOD.DELAYED in methods:
        return APPLY_METHOD.DELAYED
    return APPLY_METHOD.NEXT_BATTLE if APPLY_METHOD.NEXT_BATTLE in methods else APPLY_METHOD.NORMAL


SettingsExtraData = namedtuple('SettingsExtraData', 'current options extraData')

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
        if f is not None:
            return [ item for item in settings if item in f ]
        else:
            return settings

    def getApplyMethod(self, diff=None):
        settings = self.__filter(self.indices.keys(), diff.keys())
        methods = [ m for m in self.__forEach(settings, lambda n, p: p.getApplyMethod(diff[n])) ]
        return highestPriorityMethod(methods)

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

    def __init__(self, soundGroup, isPreview=True):
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
        if self.subKey is None:
            value = self._getSettings()
        else:
            value = self._getSettings().get(self.subKey)
        if value is None:
            value = self.getDefaultValue()
        return value

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


class StorageDumpSetting(StorageSetting):

    def setDumpedValue(self, value):
        BattleReplay.g_replayCtrl.setSetting(self.settingName, value)

    def getDumpedValue(self):
        return BattleReplay.g_replayCtrl.getSetting(self.settingName, self.getDefaultValue())

    def getDumpValue(self):
        return self._get()

    def dump(self):
        BattleReplay.g_replayCtrl.setSetting(self.settingName, self.getDumpValue())

    def _get(self):
        return self.getDumpedValue() if BattleReplay.isPlaying() else super(StorageDumpSetting, self)._get()

    def _set(self, value):
        if BattleReplay.isPlaying():
            self.setDumpedValue(value)
        return super(StorageDumpSetting, self)._set(value)


class AccountDumpSetting(AccountSetting):

    def __init__(self, settingName, key, subKey=None):
        super(AccountDumpSetting, self).__init__(key, subKey)
        self.__dumpName = settingName

    def setDumpedValue(self, value):
        BattleReplay.g_replayCtrl.setSetting(self.__dumpName, value)

    def getDumpedValue(self):
        return BattleReplay.g_replayCtrl.getSetting(self.__dumpName, self.getDefaultValue())

    def getDumpValue(self):
        return self._get()

    def dump(self):
        BattleReplay.g_replayCtrl.setSetting(self.__dumpName, self.getDumpValue())

    def _get(self):
        return self.getDumpedValue() if BattleReplay.isPlaying() else super(AccountDumpSetting, self)._get()

    def _save(self, value):
        if BattleReplay.isPlaying():
            self.setDumpedValue(value)
        return super(AccountDumpSetting, self)._save(value)


class StorageAccountSetting(StorageDumpSetting):

    def getDefaultValue(self):
        return AccountSettings.getSettingsDefault(self.settingName)


class SettingFalseByDefault(StorageDumpSetting):

    def getDefaultValue(self):
        return False


class SettingTrueByDefault(StorageDumpSetting):

    def getDefaultValue(self):
        return True


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
            _logger.warning('Section is not defined %s', section)
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
            _logger.warning('Section is not defined %s', section)
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
            _logger.warning('Section is not defined %s', section)
            return False

    def getDefaultValue(self):
        pass


class UserPrefsInt64Setting(UserPrefsSetting):

    def _readValue(self, section):
        default = self.getDefaultValue()
        return section.readInt64(self.sectionName, long(default)) if section is not None else default

    def _writeValue(self, section, value):
        if section is not None:
            return section.writeInt64(self.sectionName, long(value))
        else:
            _logger.warning('Section is not defined %s', section)
            return False

    def getDefaultValue(self):
        pass


class PreferencesSetting(SettingAbstract):

    def __init__(self, isPreview=False):
        super(PreferencesSetting, self).__init__(isPreview)
        BigWorld.wg_subscribeToSavePreferences(self._savePrefsCallback)
        BigWorld.wg_subscribeToReadPreferences(self._readPrefsCallback)

    def _savePrefsCallback(self, prefsRoot):
        pass

    def _readPrefsCallback(self, key, value):
        pass


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


class VOIPChannelSetting(UserPrefsInt64Setting):

    def __init__(self, isPreview=False):
        super(VOIPChannelSetting, self).__init__(SOUND.VOIP_ENABLE_CHANNEL, isPreview)

    def initFromPref(self):
        isEnabled, channelHash = self._get()
        VOIP.getVOIPManager().applyChannelSetting(isEnabled, channelHash)

    def _get(self):
        flags = super(VOIPChannelSetting, self)._get()
        isEnabled = flags & 1 != 0
        channelHash = flags >> 1
        return (isEnabled, channelHash)

    def _set(self, value):
        isEnabled, channelHash = value
        VOIP.getVOIPManager().applyChannelSetting(isEnabled, channelHash)
        LOG_NOTE('Change state of channel voip:', isEnabled, channelHash)

    def _save(self, value):
        isEnabled, channelHash = value
        flags = int(bool(isEnabled)) + (int(channelHash) << 1)
        super(VOIPChannelSetting, self)._save(flags)

    def getDefaultValue(self):
        pass


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
        if vm.getCaptureDevices():
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
    lobbyContext = dependency.descriptor(ILobbyContext)

    def _get(self):
        isEnabled = self.lobbyContext.getServerSettings().clanProfile.isEnabled()
        return super(ClansSetting, self)._get() if isEnabled else None

    def getDefaultValue(self):
        return True


class GameplaySetting(StorageAccountSetting):

    def __init__(self, settingName, gameplayName, storage, delegate=lambda : True):
        super(GameplaySetting, self).__init__(settingName, storage)
        self.gameplayName = gameplayName
        self.bit = ArenaType.getGameplaysMask((gameplayName,))
        self.__callable = delegate

    def _get(self):
        if not self.__callable():
            return None
        else:
            settingValue = super(GameplaySetting, self)._get()
            return settingValue & self.bit > 0

    def _set(self, value):
        if not self.__callable():
            LOG_WARNING('GameplaySetting is disabled', self.gameplayName)
            return
        settingValue = super(GameplaySetting, self)._get()
        settingValue ^= self.bit
        if value:
            settingValue |= self.bit
        return super(GameplaySetting, self)._set(settingValue)

    def getDumpValue(self):
        return super(GameplaySetting, self)._get()


class RandomOnly10ModeSetting(StorageAccountSetting):
    _RandomOnly10ModeSettingStruct = namedtuple('_RandomOnly10ModeSettingStruct', 'current options extraData')
    lobbyContext = dependency.descriptor(ILobbyContext)

    def pack(self):
        return self._RandomOnly10ModeSettingStruct(self._get(), self._getOptions(), self.getExtraData())._asdict()

    def getExtraData(self):
        return {'enabled': self.lobbyContext.getServerSettings().isOnly10ModeEnabled()}


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


class DynamicRendererSetting(SettingAbstract):

    def _get(self):
        return round(BigWorld.getDRRAutoscalerBaseScale(), 2) * 100

    def _set(self, value):
        value = float(value) / 100
        BigWorld.setDRRScale(value)


class _AdjustValueSetting(SettingAbstract):

    @classmethod
    def _adjustValue(cls, value):
        return clamp(value, 0, 100)


class ColorFilterIntensitySetting(_AdjustValueSetting):
    DEFAULT_FILTER_INTENSITY = 0.25

    def _get(self):
        value = round(BigWorld.getColorGradingStrength(), 2) * 100
        return self._adjustValue(value)

    def _set(self, value):
        value = float(self._adjustValue(value)) / 100
        BigWorld.setColorGradingStrength(value)

    @classmethod
    def _adjustValue(cls, value):
        return clamp(value, 25, 100)

    def getDefaultValue(self):
        return self.DEFAULT_FILTER_INTENSITY * 100


class BrightnessCorrectionSetting(_AdjustValueSetting):
    DEFAULT_BRIGHTNESS = 0.5

    def _get(self):
        value = round(BigWorld.getColorBrightness(), 2) * 100
        return self._adjustValue(value)

    def _set(self, value):
        value = float(self._adjustValue(value)) / 100
        BigWorld.setColorBrightness(value)

    def getDefaultValue(self):
        return self.DEFAULT_BRIGHTNESS * 100


class ContrastCorrectionSetting(_AdjustValueSetting):
    DEFAULT_CONTRAST = 0.5

    def _get(self):
        value = round(BigWorld.getColorContrast(), 2) * 100
        return self._adjustValue(value)

    def _set(self, value):
        value = float(self._adjustValue(value)) / 100
        BigWorld.setColorContrast(value)

    def getDefaultValue(self):
        return self.DEFAULT_CONTRAST * 100


class SaturationCorrectionSetting(_AdjustValueSetting):
    DEFAULT_SATURATION = 1

    def _get(self):
        value = round(BigWorld.getColorSaturation(), 2) * 100
        return self._adjustValue(value)

    def _set(self, value):
        value = float(self._adjustValue(value)) / 100
        BigWorld.setColorSaturation(value)

    def getDefaultValue(self):
        return self.DEFAULT_SATURATION * 100


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
            options = []
            for label, data, advanced, supported in self._currentValue.options:
                options.append({'label': '#settings:graphicsSettingsOptions/%s' % str(label),
                 'data': data,
                 'advanced': advanced,
                 'supported': supported})

            options = sorted(options, key=itemgetter('data'), reverse=True)
            return options
        else:
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

        if self.isPreview:
            self._currentValue = graphics.getGraphicsSetting(self.name)
        return True

    def getApplyMethod(self, value):
        return BigWorld.getGraphicsSettingApplyMethod(self.name, int(value))

    def refresh(self):
        self._currentValue = graphics.getGraphicsSetting(self.name)
        super(GraphicSetting, self).refresh()


class IGBHardwareAccelerationSetting(UserPrefsBoolSetting):

    def __init__(self):
        super(IGBHardwareAccelerationSetting, self).__init__(Settings.IGB_HARDWARE_ACCELERATION_ENABLED)

    def getApplyMethod(self, value):
        return APPLY_METHOD.RESTART

    def getDefaultValue(self):
        return Settings.g_instance.engineConfig['webBrowser']['hardwareAcceleration'].asBool


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


class WindowSizeSetting(PreferencesSetting):

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
        super(ResolutionSetting, self).__init__(isPreview)
        self._lastSelectedVideoMode = None
        self._storage = weakref.proxy(storage)
        return

    def _getResolutions(self):
        return self._getSuitableResolutions()[self._storage.monitor]

    def _getSuitableResolutions(self):
        result = []
        for modes in graphics.getSuitableVideoModes():
            resolutions = set()
            for mode in modes:
                resolutions.add((mode.width, mode.height))

            result.append(sorted(tuple(resolutions)))

        return result

    def _getResolutionIndex(self, width, height):
        for idx, (w, h) in enumerate(self._getResolutions()):
            if w == width and h == height:
                return idx

    def _get(self):
        resolution = self._storage.resolution
        return self._getResolutionIndex(*resolution) if resolution is not None else None

    def _findBestAspect(self, aspect, maxInt):
        w = 4
        bestDelta = 100000.0
        bestW = 1
        bestH = 1
        while w < maxInt:
            h = 3
            while h < w:
                delta = abs(float(w) / h - aspect)
                if delta < bestDelta:
                    bestDelta = delta
                    bestW = w
                    bestH = h
                h = h + 1

            w = w + 1

        return (bestW, bestH)

    def _getOptions(self):
        res = []
        for resolutions in self._getSuitableResolutions():
            formatedRes = []
            for width, height in resolutions:
                gcd = fractions.gcd(width, height)
                widthOpt = width / gcd
                heightOpt = height / gcd
                if widthOpt > 32:
                    p = self._findBestAspect(float(widthOpt) / heightOpt, 32)
                    widthOpt = p[0]
                    heightOpt = p[1]
                if widthOpt == 8:
                    widthOpt *= 2
                    heightOpt *= 2
                formatedRes.append('{0}x{1} [{2}:{3}]'.format(width, height, widthOpt, heightOpt))

            res.append(formatedRes)

        return res

    def _set(self, value):
        resolution = self._getResolutions()[int(value)]
        self._storage.resolution = resolution
        self._lastSelectedVideoMode = resolution
        FovExtended.instance().refreshFov()

    def _savePrefsCallback(self, prefsRoot):
        if self._lastSelectedVideoMode is not None and g_monitorSettings.isMonitorChanged:
            devPref = prefsRoot['devicePreferences']
            devPref.writeInt('fullscreenWidth', self._lastSelectedVideoMode[0])
            devPref.writeInt('fullscreenHeight', self._lastSelectedVideoMode[1])
        return


class BorderlessSizeSetting(ResolutionSetting):

    def _getSuitableResolutions(self):
        result = []
        for modes in graphics.getSuitableBorderlessSizes():
            resolutions = set()
            for mode in modes:
                resolutions.add((mode.width, mode.height))

            result.append(sorted(tuple(resolutions)))

        return result

    def _get(self):
        resolution = self._storage.borderlessSize
        return self._getResolutionIndex(*resolution) if resolution is not None else None

    def _set(self, value):
        size = self._getResolutions()[int(value)]
        self._storage.borderlessSize = size
        self._lastSelectedVideoMode = size

    def _savePrefsCallback(self, prefsRoot):
        if self._lastSelectedVideoMode is not None and g_monitorSettings.isMonitorChanged:
            devPref = prefsRoot['devicePreferences']
            devPref.writeInt('borderlessWidth', self._lastSelectedVideoMode[0])
            devPref.writeInt('borderlessHeight', self._lastSelectedVideoMode[1])
        return


class RefreshRateSetting(PreferencesSetting):

    def __init__(self, isPreview=False, storage=None):
        super(RefreshRateSetting, self).__init__(isPreview)
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
    WINDOWED = 0
    FULLSCREEN = 1
    BORDERLESS = 2
    OPTIONS = {WINDOWED: 'windowed',
     FULLSCREEN: 'fullscreen',
     BORDERLESS: 'borderless'}

    def __init__(self, storage):
        super(VideoModeSettings, self).__init__()
        self._storage = weakref.proxy(storage)
        self.__videoMode = self._get()

    def _getOptions(self):
        result = []
        allowScreenModes = ((BigWorld.WindowModeWindowed, self.OPTIONS[self.WINDOWED]), (BigWorld.WindowModeExclusiveFullscreen, self.OPTIONS[self.FULLSCREEN]))
        if graphics.getSuitableVideoModes():
            allowScreenModes += ((BigWorld.WindowModeBorderless, self.OPTIONS[self.BORDERLESS]),)
        for data, label in allowScreenModes:
            result.append({'data': data,
             'label': '#settings:screenMode/%s' % label})

        return result

    def _get(self):
        return self._storage.windowMode

    def _set(self, value):
        self._storage.windowMode = value
        self.__videoMode = value

    def _savePrefsCallback(self, prefsRoot):
        prefsRoot['devicePreferences'].writeInt('windowMode', self.__videoMode)

    def _readPrefsCallback(self, key, value):
        if key == 'windowMode':
            self.__videoMode = value


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
            AIM_MARKER_2D = 'AimMarker2D'

        @classmethod
        def getOptionName(cls, mType, mOption):
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

    def _set(self, value):
        totalValue = None
        if value and BattleReplay.isPlaying():
            totalValue = self._get()
            totalValue.update(value)
        super(VehicleMarkerSetting, self)._set(totalValue or value)
        return

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

    def _set(self, value):
        totalValue = None
        if value and BattleReplay.isPlaying():
            totalValue = self._get()
            totalValue.update(value)
        super(AimSetting, self)._set(totalValue or value)
        return

    def pack(self):
        result = self._get()
        for vname, (name, optsLen) in self.VIRTUAL_OPTIONS.iteritems():
            if vname in result:
                types = [ {'loc': makeString('#settings:aim/%s/type%d' % (name, i)),
                 'label': '#settings:aim/%s/type%d' % (name, i),
                 'index': i} for i in xrange(int(optsLen)) ]
                types = sorted(types, key=itemgetter('loc'))
                for item in types:
                    item.pop('loc', None)

                result[vname] = self.PackStruct(result[vname], types)._asdict()

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


class SPGAimSetting(StorageDumpSetting):

    def getExtraData(self):
        labelR = R.strings.settings.aim.spg.dyn(self.settingName)
        tooltipR = labelR.dyn('tooltip') if labelR else None
        data = {'checkBoxLabel': backport.text(labelR()) if labelR else ''}
        if tooltipR:
            data['tooltip'] = makeTooltip(backport.text(tooltipR.header()), backport.text(tooltipR.body()))
        return data

    def pack(self):
        return {'current': self._get(),
         'options': self._getOptions(),
         'extraData': self.getExtraData()}

    def getDefaultValue(self):
        return AccountSettings.getSettingsDefault('spgAim').get(self.settingName, None)


class _BaseAimContourSetting(StorageDumpSetting):
    _RES_ROOT = None
    _OPTIONS_NUMBER = None

    def getDefaultValue(self):
        return AccountSettings.getSettingsDefault('contour').get(self.settingName, None)

    def setSystemValue(self, value):
        raise NotImplementedError

    def pack(self):
        return {'current': self._get(),
         'options': self._getOptions()}

    def _getOptions(self):
        return [ {'data': value,
         'label': backport.text(self._RES_ROOT.dyn('type{}'.format(value))())} for value in xrange(self._OPTIONS_NUMBER) ]


class ContourSetting(_BaseAimContourSetting):
    _RES_ROOT = R.strings.settings.cursor.contour
    _OPTIONS_NUMBER = 2

    def setSystemValue(self, value):
        BigWorld.enableEdgeDrawerVisual(not value)

    def getExtraData(self):
        return [ {'tooltip': makeTooltip(body=backport.text(self._RES_ROOT.dyn('type{}'.format(value)).tooltip()))} for value in xrange(self._OPTIONS_NUMBER) ]

    def pack(self):
        return {'current': self._get(),
         'options': self._getOptions(),
         'extraData': self.getExtraData()}


class ContourPenetratableZoneSetting(_BaseAimContourSetting):
    _RES_ROOT = R.strings.settings.cursor.contourPenetrableZone
    _OPTIONS_NUMBER = 3

    def setSystemValue(self, value):
        BigWorld.setEdgeDrawerPenetratableZoneOverlay(value)


class ContourImpenetratableZoneSetting(_BaseAimContourSetting):
    _RES_ROOT = R.strings.settings.cursor.contourImpenetrableZone
    _OPTIONS_NUMBER = 3

    def setSystemValue(self, value):
        BigWorld.setEdgeDrawerImpenetratableZoneOverlay(value)


class SPGStrategicCamMode(StorageDumpSetting):

    class OPTIONS(CONST_CONTAINER):
        BASE = 'base'
        ALT = 'alt'

    ARTY_CAM_OPTIONS = [OPTIONS.BASE, OPTIONS.ALT]

    def getDefaultValue(self):
        return self.ARTY_CAM_OPTIONS.index(self.OPTIONS.BASE)

    def getExtraData(self):
        tooltipR = R.strings.settings.aim.spg.spgStrategicCamMode.tooltip
        data = {'label': backport.text(R.strings.settings.aim.spg.spgStrategicCamMode())}
        if tooltipR:
            data['tooltip'] = makeTooltip(backport.text(tooltipR.header()), backport.text(tooltipR.body()))
        return data

    def pack(self):
        return {'current': self._get(),
         'options': self._getOptions(),
         'extraData': self.getExtraData()}

    def _getOptions(self):
        settingsKey = '#settings:aim/spg/{}/{}'
        return [ settingsKey.format(self.settingName, mType) for mType in self.ARTY_CAM_OPTIONS ]


class SPGAimEntranceMode(StorageDumpSetting):

    def getDefaultValue(self):
        return AccountSettings.getSettingsDefault('spgAim').get(self.settingName, SPGAimEntranceModeOptions.SETTINGS_OPTIONS.index(SPGAimEntranceModeOptions.LAST))

    def getExtraData(self):
        return {'label': backport.text(R.strings.settings.aim.spg.aimEntranceMode())}

    def pack(self):
        return {'current': self._get(),
         'options': self._getOptions(),
         'extraData': self.getExtraData()}

    def _getOptions(self):
        settingsKey = '#settings:aim/spg/{}/{}'
        return [ settingsKey.format(self.settingName, mType) for mType in SPGAimEntranceModeOptions.SETTINGS_OPTIONS ]


class MinimapSetting(StorageDumpSetting):

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
        return [ settingsKey % (self.settingName, mType) for mType in self.VEHICLE_MODELS_TYPES ]

    def getDefaultValue(self):
        return self.VEHICLE_MODELS_TYPES.index(self.OPTIONS.ALWAYS)


class MinimapArtyHitSetting(StorageDumpSetting):

    class OPTIONS(CONST_CONTAINER):
        HIDE = 'hide'
        DOT = 'dot'

    ARTY_HIT_OPTIONS = [OPTIONS.HIDE, OPTIONS.DOT]

    def getDefaultValue(self):
        return self.ARTY_HIT_OPTIONS.index(self.OPTIONS.DOT)


class MinimapHPSettings(StorageDumpSetting):

    class Options(Enum):
        NEVER = 0
        ALT = 1
        ALWAYS = 2

    def _getOptions(self):
        settingsKey = '#settings:game/%s/%s'
        return [ settingsKey % (self.settingName, mType.lower()) for mType in self.Options.__members__.keys() ]

    def getDefaultValue(self):
        return self.Options.ALT.value


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


class CustomizationDisplayTypeSetting(StorageDumpSetting):

    class OPTIONS(CONST_CONTAINER):
        HISTORICAL = 'historical'
        NOT_HISTORICAL = 'notHistorical'
        ALL = 'all'

    CONTENT_TYPES = (OPTIONS.HISTORICAL, OPTIONS.NOT_HISTORICAL, OPTIONS.ALL)

    def _getOptions(self):
        settingsKey = '#settings:game/%s/%s'
        return [ {'label': settingsKey % (self.settingName, cType)} for cType in self.CONTENT_TYPES ]

    def getDefaultValue(self):
        return self.CONTENT_TYPES.index(self.OPTIONS.ALL)

    def getRowCount(self):
        return self._get() + 1


class DoubleCarouselTypeSetting(StorageDumpSetting):

    class OPTIONS(CONST_CONTAINER):
        ADAPTIVE = 'adaptive'
        SMALL = 'small'

    DOUBLE_CAROUSEL_TYPES = (OPTIONS.ADAPTIVE, OPTIONS.SMALL)

    def _getOptions(self):
        settingsKey = '#settings:game/%s/%s'
        return [ settingsKey % (self.settingName, cType) for cType in self.DOUBLE_CAROUSEL_TYPES ]

    def getDefaultValue(self):
        return self.DOUBLE_CAROUSEL_TYPES.index(self.OPTIONS.ADAPTIVE)

    def enableSmallCarousel(self):
        return self._get() == self.DOUBLE_CAROUSEL_TYPES.index(self.OPTIONS.SMALL)


class VehicleCarouselStatsSetting(StorageDumpSetting):

    def _get(self):
        return bool(super(VehicleCarouselStatsSetting, self)._get())

    def getDefaultValue(self):
        return True


class BattleLoadingTipSetting(AccountDumpSetting):

    class OPTIONS(CONST_CONTAINER):
        TEXT = 'textTip'
        VISUAL = 'visualTip'
        MINIMAP = 'minimap'
        TIPS_TYPES = (TEXT, VISUAL, MINIMAP)

    def getSettingID(self, isVisualOnly=False):
        return self.OPTIONS.VISUAL if isVisualOnly else self.OPTIONS.TIPS_TYPES[self._get()]

    def _getOptions(self):
        settingsKey = '#settings:game/%s/%s'
        return [ settingsKey % (self.key, tType) for tType in self.OPTIONS.TIPS_TYPES ]


class ShowMarksOnGunSetting(StorageAccountSetting):

    def _get(self):
        return not super(ShowMarksOnGunSetting, self)._get()

    def _set(self, value):
        return super(ShowMarksOnGunSetting, self)._set(not value)

    def getDefaultValue(self):
        return True


class ControlSetting(SettingAbstract):
    ControlPackStruct = namedtuple('ControlPackStruct', 'current default')

    def _getDefault(self):
        return None

    def pack(self):
        return self.ControlPackStruct(self._get(), self._getDefault())._asdict()


class StorageControlSetting(StorageDumpSetting, ControlSetting):
    pass


class MouseSetting(ControlSetting):
    CAMERAS = {CTRL_MODE_NAME.POSTMORTEM: (ArcadeCamera.getCameraAsSettingsHolder, 'postMortemMode/camera'),
     CTRL_MODE_NAME.ARCADE: (ArcadeCamera.getCameraAsSettingsHolder, 'arcadeMode/camera'),
     CTRL_MODE_NAME.SNIPER: (SniperCamera.getCameraAsSettingsHolder, 'sniperMode/camera'),
     CTRL_MODE_NAME.STRATEGIC: (StrategicCamera.getCameraAsSettingsHolder, 'strategicMode/camera'),
     CTRL_MODE_NAME.ARTY: (ArtyCamera.getCameraAsSettingsHolder, 'artyMode/camera'),
     CTRL_MODE_NAME.DUAL_GUN: (DualGunCamera.getCameraAsSettingsHolder, 'dualGunMode/camera')}

    def __init__(self, mode, setting, default, isPreview=False, masterSwitch=''):
        super(MouseSetting, self).__init__(isPreview)
        self.mode = mode
        self.setting = setting
        self.default = default
        self.masterSwitch = masterSwitch
        self.__aihSection = ResMgr.openSection(INPUT_HANDLER_CFG)

    def getCamera(self):
        if self._isControlModeAccessible():
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
        if self._isDisabledByMasterSwitch():
            return None
        else:
            camera = self.getCamera()
            return camera.getUserConfigValue(self.setting) if camera is not None else self.default

    def _set(self, value):
        if self._isDisabledByMasterSwitch():
            LOG_WARNING('Mouse setting is disabled', self.mode, self.setting)
            return
        else:
            camera = self.getCamera()
            if camera is None:
                LOG_WARNING('Error while applying mouse settings: empty camera', self.mode, self.setting)
                return
            camera.setUserConfigValue(self.setting, value)
            if not self._isControlModeAccessible():
                camera.writeUserPreferences()
            return

    def _isControlModeAccessible(self):
        return BigWorld.player() is not None and hasattr(BigWorld.player(), 'inputHandler') and hasattr(BigWorld.player().inputHandler, 'ctrls')

    def _isDisabledByMasterSwitch(self):
        return self.masterSwitch and not GUI_SETTINGS.lookup(self.masterSwitch)


class MouseSensitivitySetting(MouseSetting):

    def __init__(self, mode, masterSwitch=''):
        super(MouseSensitivitySetting, self).__init__(mode, 'sensitivity', 1.0, masterSwitch=masterSwitch)


class DynamicFOVMultiplierSetting(MouseSetting):

    def __init__(self, isPreview=False):
        super(DynamicFOVMultiplierSetting, self).__init__(CTRL_MODE_NAME.ARCADE, 'fovMultMinMaxDist', self.getDefaultValue(), isPreview)

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
        return FovExtended.instance().horizontalFov


class DynamicFOVSetting(UserPrefsStringSetting):
    DEFAULT = (80, 100)

    def __init__(self, isPreview=False):
        super(DynamicFOVSetting, self).__init__(Settings.KEY_DYNAMIC_FOV, isPreview)

    def _get(self):
        try:
            return cPickle.loads(base64.b64decode(super(DynamicFOVSetting, self)._get()))
        except Exception:
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

    def getKeyName(self):
        return getBigworldNameFromKey(self.getCurrentMapping())

    def _set(self, value):
        return self.setSystemValue(value)

    def _get(self):
        return getScaleformKey(self.getCurrentMapping())

    def setSystemValue(self, value):
        key = 'KEY_NONE'
        if value is not None:
            key = getBigworldNameFromKey(getBigworldKey(value))
        if self.cmd == 'CMD_VOICECHAT_MUTE' and self.app is not None and self.app.gameInputManager is not None:
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
       ('chargeFire', 'CMD_CM_CHARGE_SHOT'),
       ('lock_target', 'CMD_CM_LOCK_TARGET'),
       ('lock_target_off', 'CMD_CM_LOCK_TARGET_OFF'),
       ('alternate_mode', 'CMD_CM_ALTERNATE_MODE'),
       ('trajectory_view', 'CMD_CM_TRAJECTORY_VIEW'),
       ('reloadPartialClip', 'CMD_RELOAD_PARTIAL_CLIP'))),
     ('vehicle_other', (('showHUD', 'CMD_TOGGLE_GUI'),
       ('showQuestProgress', 'CMD_QUEST_PROGRESS_SHOW'),
       ('frontlineSelfDestruction', 'CMD_REQUEST_RECOVERY'),
       ('showPersonalReserves', 'CMD_SHOW_PERSONAL_RESERVES'))),
     ('equipment', (('item01', 'CMD_AMMO_CHOICE_1'),
       ('item02', 'CMD_AMMO_CHOICE_2'),
       ('item03', 'CMD_AMMO_CHOICE_3'),
       ('item04', 'CMD_AMMO_CHOICE_4'),
       ('item05', 'CMD_AMMO_CHOICE_5'),
       ('item06', 'CMD_AMMO_CHOICE_6'),
       ('item07', 'CMD_AMMO_CHOICE_7'),
       ('item08', 'CMD_AMMO_CHOICE_8'),
       ('item09', 'CMD_AMMO_CHOICE_9'),
       ('item00', 'CMD_AMMO_CHOICE_0'))),
     ('team_communication', (('highlightLocation', 'CMD_CHAT_SHORTCUT_CONTEXT_COMMAND'),
       ('highlightTarget', 'CMD_CHAT_SHORTCUT_CONTEXT_COMMIT'),
       ('showRadialMenu', 'CMD_RADIAL_MENU_SHOW'),
       ('help', 'CMD_CHAT_SHORTCUT_HELPME'),
       ('reloading', 'CMD_CHAT_SHORTCUT_RELOAD'),
       ('fallBack', 'CMD_CHAT_SHORTCUT_BACKTOBASE'),
       ('affirmative', 'CMD_CHAT_SHORTCUT_AFFIRMATIVE'),
       ('negative', 'CMD_CHAT_SHORTCUT_NEGATIVE'),
       ('thankYou', 'CMD_CHAT_SHORTCUT_THANKYOU'))),
     ('camera', (('camera_up', 'CMD_CM_CAMERA_ROTATE_UP'),
       ('camera_down', 'CMD_CM_CAMERA_ROTATE_DOWN'),
       ('camera_left', 'CMD_CM_CAMERA_ROTATE_LEFT'),
       ('camera_right', 'CMD_CM_CAMERA_ROTATE_RIGHT'))),
     ('voicechat', (('pushToTalk', 'CMD_VOICECHAT_MUTE'), ('voicechat_enable', 'CMD_VOICECHAT_ENABLE'))),
     ('minimap', (('sizeUp', 'CMD_MINIMAP_SIZE_UP'), ('sizeDown', 'CMD_MINIMAP_SIZE_DOWN'), ('visible', 'CMD_MINIMAP_VISIBLE'))))
    IMPORTANT_BINDS = ('forward', 'backward', 'left', 'right', 'fire', 'item01', 'item02', 'item03', 'item04', 'item05', 'item06', 'item07', 'item08', 'item09', 'item00')
    KEYS_TOOLTIPS = {'auto_rotation': 'SettingKeySwitchMode',
     'chargeFire': 'SettingsKeyChargeFire',
     'highlightLocation': 'SettingsKeyHighlightLocation',
     'highlightTarget': 'SettingsKeyHighlightTarget',
     'showRadialMenu': 'SettingsKeyShowRadialMenu'}
    __hiddenGroups = set()

    def __init__(self):
        if not GUI_SETTINGS.minimapSize:
            self.hideGroup('minimap', hide=True)
        if not GUI_SETTINGS.voiceChat:
            self.hideGroup('voicechat', hide=True)
        settings = [('keysLayout', ReadOnlySetting(self._getLayout)), ('keysTooltips', ReadOnlySetting(lambda : self.KEYS_TOOLTIPS))]
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
            if groupName == 'firing' and not GUI_SETTINGS.spgAlternativeAimingCameraEnabled:
                groupValues = list(groupValues)
                del groupValues[4]
            if groupName == 'vehicle_other':
                progressEnabled = True
                if IS_CHINA:
                    progressEnabled = False
                if not progressEnabled:
                    groupValues = list(groupValues)
                    del groupValues[2]
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
            if group in cls.__hiddenGroups:
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
        return {'key': key,
         'cmd': cmd}


class _BaseSoundPresetSetting(AccountDumpSetting):

    def __init__(self, actionsMap, settingName, key, subKey=None):
        super(_BaseSoundPresetSetting, self).__init__(settingName, key, subKey)
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
    return [ item[1] for item in _SPEAKER_PRESET_CONFIG ]


def _makeSoundGuiIDsSeq():
    return [ item[0] for item in _SPEAKER_PRESET_CONFIG ]


def _makeSoundPresetIDToGuiID():
    return dict(((item[1], item[0]) for item in _SPEAKER_PRESET_CONFIG))


class SoundDevicePresetSetting(_BaseSoundPresetSetting):
    soundsCtrl = dependency.descriptor(ISoundsController)

    class SYSTEMS(CONST_CONTAINER):
        SPEAKERS = 0
        HEADPHONES = 1
        LAPTOP = 2

    def __init__(self, settingName, key, subKey=None, isPreview=False):
        super(SoundDevicePresetSetting, self).__init__(((self.__setSound, self.SYSTEMS.SPEAKERS), (self.__setSound, self.SYSTEMS.HEADPHONES), (self.__setSound, self.SYSTEMS.LAPTOP)), settingName, key, subKey=subKey)

    def getSystemState(self):
        selectedID = self.get()
        speakersCountID = SPEAKERS_CONFIG.SPEAKER_SETUP_2_0
        if selectedID == self.SYSTEMS.SPEAKERS:
            speakersCountID = self.soundsCtrl.system.getUserSpeakersPresetID()
        return (speakersCountID in (SPEAKERS_CONFIG.AUTO_DETECTION, self.soundsCtrl.system.getSystemSpeakersPresetID()), speakersCountID)

    def _getOptions(self):
        options = []
        selectedID = self.soundsCtrl.system.getUserSpeakersPresetID()
        if selectedID == SPEAKERS_CONFIG.AUTO_DETECTION:
            selectedID = self.soundsCtrl.system.getSystemSpeakersPresetID()
        else:
            self.soundsCtrl.system.getSystemSpeakersPresetID()
        mapping = _makeSoundPresetIDToGuiID()
        if selectedID in mapping:
            acousticType = mapping[selectedID]
        else:
            LOG_ERROR('Selected preset is unresolved', selectedID)
            acousticType = ACOUSTICS.TYPE_ACOUSTICS
        accousticValid = self.soundsCtrl.system.getUserSpeakersPresetID() in (SPEAKERS_CONFIG.AUTO_DETECTION, self.soundsCtrl.system.getSystemSpeakersPresetID())
        otherValid = self.soundsCtrl.system.getSystemSpeakersPresetID() == SPEAKERS_CONFIG.SPEAKER_SETUP_2_0

        def iterator():
            yield (ACOUSTICS.TYPE_ACOUSTICS, acousticType, accousticValid)
            yield (ACOUSTICS.TYPE_HEADPHONES, ACOUSTICS.TYPE_HEADPHONES, otherValid)
            yield (ACOUSTICS.TYPE_LAPTOP, ACOUSTICS.TYPE_LAPTOP, otherValid)

        for baseID, selectedID, isValid in iterator():
            options.append({'id': baseID,
             'label': SETTINGS.sounds_sounddevice(selectedID),
             'image': '../maps/icons/settings/{}.png'.format(baseID),
             'tooltip': SETTINGS.sounds_sounddevice(selectedID),
             'speakerId': selectedID,
             'showDeviceAlert': not isValid})

        return options

    def _set(self, value):
        super(SoundDevicePresetSetting, self)._set(value)
        AccountSettings.setFilter(SPEAKERS_DEVICE, 0)

    def __setSound(self, value):
        self.soundsCtrl.system.setSoundSystem(value)


class SoundSpeakersPresetSetting(SettingAbstract):
    soundsCtrl = dependency.descriptor(ISoundsController)

    def getSystemPreset(self):
        selectedID = self.soundsCtrl.system.getSystemSpeakersPresetID()
        mapping = _makeSoundPresetIDToGuiID()
        if selectedID in mapping:
            return mapping[selectedID]
        LOG_ERROR('Selected preset is unresolved', selectedID)
        return ACOUSTICS.TYPE_ACOUSTIC_20

    def isPresetSupportedByIndex(self, index):
        presetIDs = _makeSoundPresetIDsSeq()
        if index < len(presetIDs):
            presetID = presetIDs[index]
            return presetID in (SPEAKERS_CONFIG.AUTO_DETECTION, self.soundsCtrl.system.getSystemSpeakersPresetID())
        return False

    def _get(self):
        presetID = self.soundsCtrl.system.getUserSpeakersPresetID()
        presetIDs = _makeSoundPresetIDsSeq()
        if presetID in presetIDs:
            return presetIDs.index(presetID)
        else:
            LOG_ERROR('Index of selected preset is not found', presetID)
            return None

    def _set(self, value):
        value = int(value)
        presetIDs = _makeSoundPresetIDsSeq()
        if value < len(presetIDs):
            self.soundsCtrl.system.setUserSpeakersPresetID(presetIDs[value])
            AccountSettings.setFilter(SPEAKERS_DEVICE, 0)
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


class PreviewSoundSetting(AccountSetting):
    _USER_SOUND = 'userSound'
    _WWISE_EVENTS = (_USER_SOUND,)

    def __init__(self, key):
        super(PreviewSoundSetting, self).__init__(key)
        self.__previewSound = None
        return

    def playPreviewSound(self, eventIdx):
        eventToPlay = self._WWISE_EVENTS[eventIdx]
        if self.__previewSound is not None:
            playingEvent = self.__previewSound.name
            if self._WWISE_EVENTS.index(playingEvent) != eventIdx:
                self.clearPreviewSound()
                self.__previewSound = SoundGroups.g_instance.getSound2D(eventToPlay)
                self.__playSound()
            else:
                if playingEvent != self._USER_SOUND:
                    self.clearPreviewSound()
                    self.__previewSound = SoundGroups.g_instance.getSound2D(eventToPlay)
                self.__playSound()
        else:
            self.__previewSound = SoundGroups.g_instance.getSound2D(eventToPlay)
            self.__playSound()
        return

    def clearPreviewSound(self):
        if self.__previewSound is not None:
            self.__previewSound.stop()
            self.__previewSound = None
        return

    def getEventName(self):
        return self._WWISE_EVENTS[self._get()]

    def pack(self):
        return SettingsExtraData(self._get(), self._getOptions(), self._getExtraData())._asdict()

    def _getOptions(self):
        options = []
        for sample in self._WWISE_EVENTS:
            option = {'label': '#settings:sound/{}/{}'.format(self.key, sample)}
            if sample == self._USER_SOUND:
                option.update(tooltip='#settings:sounds/%s' % self._USER_SOUND)
            options.append(option)

        return options

    def _getExtraData(self):
        extraData = []
        for sample in self._WWISE_EVENTS:
            if sample == self._USER_SOUND:
                canPreview = bool(ResMgr.isFile('audioww/%s.mp3' % self._USER_SOUND))
            else:
                canPreview = True
            extraData.append(canPreview)

        return extraData

    def _get(self):
        return self._WWISE_EVENTS.index(super(PreviewSoundSetting, self)._get())

    def _save(self, eventIdx):
        super(PreviewSoundSetting, self)._save(self._WWISE_EVENTS[eventIdx])

    def __playSound(self):
        if self.__previewSound.name in SoundGroups.CUSTOM_MP3_EVENTS:
            SoundGroups.g_instance.prepareMP3(self.__previewSound.name)
        self.__previewSound.play()


class DetectionAlertSound(PreviewSoundSetting):
    _USER_SOUND = 'sixthSense'
    _WWISE_EVENTS = ('lightbulb', 'lightbulb_02', _USER_SOUND)


class ArtyShotAlertSound(PreviewSoundSetting):
    _USER_SOUND = 'soundExploring'
    _WWISE_EVENTS = ('artillery_lightbulb', _USER_SOUND)


class AltVoicesSetting(StorageDumpSetting):
    ALT_VOICES_PREVIEW = itertools.cycle(('wwsound_mode_preview01', 'wwsound_mode_preview02', 'wwsound_mode_preview03'))
    DEFAULT_IDX = 0
    PREVIEW_SOUNDS_COUNT = 3
    __specialSounds = dependency.descriptor(ISpecialSoundCtrl)

    class SOUND_MODE_TYPE(object):
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
        if self.__previewNations and self.__previewSound == sound:
            nation = self.__previewNations.pop()
            genderSwitch = random.choice(SoundGroups.CREW_GENDER_SWITCHES.GENDER_ALL)
            SoundGroups.g_instance.soundModes.setCurrentNation(nation, genderSwitch)
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
        self.__lastPreviewedValue = None
        self.clearPreviewSound()
        return

    def _getOptions(self):
        options = []
        for sm in self.__getSoundModesList():
            options.append({'label': sm.description,
             'tooltip': '#settings:sounds/altVoice/{}'.format(sm.name)})

        return options

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

    def getSystemModeType(self):
        return self.__getSoundModeType(self.__getSoundModesList()[self._get()])

    def __getSoundModeType(self, soundMode):
        if soundMode.name in SoundGroups.g_instance.soundModes.modes:
            return self.SOUND_MODE_TYPE.REGULAR
        return self.SOUND_MODE_TYPE.NATIONAL if soundMode.name in SoundGroups.g_instance.soundModes.nationalPresets else self.SOUND_MODE_TYPE.UNKNOWN

    def __applyRegularMode(self, mode):
        specialVoice = self.__specialSounds.specialVoice
        if specialVoice is not None and not specialVoice.onlyInNational:
            _logger.debug('Use %s as special voice instead %s', specialVoice.languageMode, mode)
            return True
        else:
            soundModes = SoundGroups.g_instance.soundModes
            soundModes.setCurrentNation(soundModes.DEFAULT_NATION)
            return soundModes.setNationalMappingByMode(mode.name)

    def __applyNationalMode(self, mode):
        specialVoice = self.__specialSounds.specialVoice
        if specialVoice is not None:
            _logger.debug('Use %s as special voice instead %s', specialVoice.languageMode, mode)
            return True
        else:
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
        return [ settingsKey % (self.settingName, rType) for rType in self.REPLAY_TYPES ]

    def setSystemValue(self, value):
        BattleReplay.g_replayCtrl.enableAutoRecordingBattles(value)


class SniperZoomSetting(StorageAccountSetting):
    SNIPER_TYPES = ['remember',
     'double',
     'quadruple',
     'octuple']

    def _getOptions(self):
        settingsKey = '#settings:game/%s/%s'
        return [ settingsKey % (self.settingName, rType) for rType in self.SNIPER_TYPES ]

    def setSystemValue(self, value):
        SniperCamera.SniperCamera.setSniperZoomSettings(value - 1)


class HullLockSetting(StorageAccountSetting):

    def getDefaultValue(self):
        return True


class VehicleHPInPlayersPanelSetting(StorageAccountSetting):

    class Options(Enum):
        NEVER = 0
        ALT = 1
        ALWAYS = 2

    def _getOptions(self):
        settingsKey = '#settings:game/%s/%s'
        return [ settingsKey % (self.settingName, mType.lower()) for mType in self.Options.__members__.keys() ]

    def getDefaultValue(self):
        return self.Options.ALT.value


class HangarCamPeriodSetting(StorageAccountSetting):

    class OPTIONS(CONST_CONTAINER):
        TYPE0 = 'type0'
        TYPE1 = 'type1'
        TYPE2 = 'type2'
        NEVER = 'never'
        HANGAR_CAM_TYPES = (TYPE0,
         TYPE1,
         TYPE2,
         NEVER)

    def getDefaultValue(self):
        options = self.OPTIONS
        return options.HANGAR_CAM_TYPES.index(options.TYPE0)

    def _getOptions(self):
        settingsKey = '#settings:game/%s/%s'
        return [ settingsKey % (self.settingName, t) for t in self.OPTIONS.HANGAR_CAM_TYPES ]


class HangarCamParallaxEnabledSetting(StorageAccountSetting):

    def getDefaultValue(self):
        return True


class InterfaceScaleSetting(UserPrefsFloatSetting):
    settingsCore = dependency.descriptor(ISettingsCore)
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, sectionName=None, isPreview=False):
        super(InterfaceScaleSetting, self).__init__(sectionName, isPreview)
        self.__interfaceScale = self._get()

    def get(self):
        if BattleReplay.isPlaying():
            return self._get()
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

    def _getOptions(self):
        return [self.__getScales(graphics.getSuitableWindowSizes(), BigWorld.wg_getCurrentResolution(BigWorld.WindowModeWindowed)), self.__getScales(graphics.getSuitableVideoModes()), self.__getScales(graphics.getSuitableVideoModes())]

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
        if value < 0 or value >= scaleLength:
            self.__interfaceScale = 0
            self._set(self.__interfaceScale)
            self.settingsCore.interfaceScale.scaleChanged()


class GraphicsQualityNote(SettingAbstract):
    _GRAPHICS_QUALITY_TYPES = {CONTENT_TYPE.SD_TEXTURES, CONTENT_TYPE.TUTORIAL, CONTENT_TYPE.SANDBOX}

    def _get(self):
        return '{0}{1}  {2}{3}'.format("<font face='$FieldFont' size='13' color='#595950'>", i18n.makeString(SETTINGS.GRAPHICSQUALITYHDSD_SD), icons.info(), '</font>') if ResMgr.activeContentType() in self._GRAPHICS_QUALITY_TYPES else ''

    def _set(self, value):
        pass


class GraphicsHigtQualityNote(SettingAbstract):
    _GRAPHICS_QUALITY_TYPES = {CONTENT_TYPE.SD_TEXTURES}

    def _get(self):
        return '{0}{1}  {2}{3}'.format("<font face='$FieldFont' size='13' color='#595950'>", i18n.makeString(SETTINGS.GRAPHICSQUALITYHDSD_SD), icons.alert(), '</font>') if ResMgr.activeContentType() in self._GRAPHICS_QUALITY_TYPES else ''

    def _set(self, value):
        pass


class GraphicsQuality(SettingAbstract):

    def _get(self):
        return ResMgr.activeContentType() == CONTENT_TYPE.SD_TEXTURES

    def _set(self, value):
        pass


class AnonymizerSetting(AccountDumpSetting):
    __ctrl = dependency.descriptor(IAnonymizerController)

    def __init__(self, settingName):
        super(AnonymizerSetting, self).__init__(settingName, settingName, 'anonymized')

    @storage_getter('users')
    def usersStorage(self):
        return None

    def getExtraData(self):
        user = self.usersStorage.getUser(getPlayerDatabaseID())
        isInClan = user.getClanInfo().isInClan() if user is not None else False
        tooltip = R.strings.tooltips.anonymizer
        if self.__ctrl.isRestricted:
            footer = backport.text(tooltip.bodyFooter.restricted())
        elif self.__ctrl.isInBattle:
            footer = backport.text(tooltip.bodyFooter.inBattle())
        else:
            footer = backport.text(tooltip.bodyFooter.default())
        body = '{body}{vspace}{footer}'.format(body=backport.text((tooltip.body.clan if isInClan else tooltip.body.noClan)()), vspace='\n\n' if footer else '', footer=text_styles.neutral(footer))
        header = backport.text(tooltip.header())
        return {'checkBoxLabel': backport.text(R.strings.settings.game.anonymizer()),
         'tooltip': makeTooltip(header, body),
         'visible': self.__ctrl.isEnabled,
         'enabled': not (self.__ctrl.isInBattle or self.__ctrl.isRestricted)}

    def pack(self):
        return {'current': self._get(),
         'options': self._getOptions(),
         'extraData': self.getExtraData()}

    def _get(self):
        return self.__ctrl.isAnonymized

    def _save(self, value):
        self.__ctrl.setAnonymized(value)


class DogtagsSetting(StorageDumpSetting):

    def getDefaultValue(self):
        return True


class ShowDamageIconSetting(StorageAccountSetting):

    def getExtraData(self):
        templateName = 'html_templates:lobby/tooltips/settings_show_damage_icon'
        showDamageIconTooltipContent = (makeHtmlString(templateName, 'ricochet'),
         makeHtmlString(templateName, 'trackDamage'),
         makeHtmlString(templateName, 'criticalDamage'),
         makeHtmlString(templateName, 'blocked'),
         makeHtmlString(templateName, 'spacedArmorBlocked'),
         makeHtmlString(templateName, 'trackBlocked'),
         makeHtmlString(templateName, 'wheelBlocked'),
         makeHtmlString(templateName, 'missArmor'))
        return {'checkBoxLabel': backport.text(R.strings.settings.game.showDamageIcon()),
         'tooltip': makeTooltip(backport.text(R.strings.tooltips.showDamageIcon.header()), '<br/>'.join(showDamageIconTooltipContent))}

    def pack(self):
        res = SettingsExtraData(self._get(), self._getOptions(), self.getExtraData())._asdict()
        return res

    def getDefaultValue(self):
        return True


class MouseAffectedSetting(RegularSetting):

    def __init__(self, settingName, isPreview=False):
        super(MouseAffectedSetting, self).__init__(settingName, isPreview)
        self._mouseSettings = [ MouseSetting(camera, self.settingName, self.getDefaultValue()) for camera in self._getCameras() ]

    def _getCameras(self):
        pass

    def setSystemValue(self, value):
        forEach(lambda mouseSetting: mouseSetting.apply(value), self._mouseSettings)


class IncreasedZoomSetting(StorageAccountSetting, MouseAffectedSetting):

    def getExtraData(self):
        zooms = self._mouseSettings[0].getCamera().getConfigValue('zooms')[-2:]
        zoomStrs = [ i18n.makeString(SETTINGS.GAME_INCREASEDZOOM_ZOOMSTR, zoom=zoom) for zoom in zooms ]
        zoomStr = i18n.makeString(SETTINGS.GAME_INCREASEDZOOM_DELIMETER).join(zoomStrs)
        return {'checkBoxLabel': i18n.makeString(SETTINGS.GAME_INCREASEDZOOM_BASE, zooms=zoomStr),
         'tooltip': makeTooltip(TOOLTIPS.INCREASEDZOOM_HEADER, i18n.makeString(TOOLTIPS.INCREASEDZOOM_BODY, zooms=zoomStr))}

    def pack(self):
        return SettingsExtraData(self._get(), self._getOptions(), self.getExtraData())._asdict()

    def setSystemValue(self, value):
        if BattleReplay.isPlaying():
            value = True
        super(IncreasedZoomSetting, self).setSystemValue(value)

    def _getCameras(self):
        return (CTRL_MODE_NAME.SNIPER, CTRL_MODE_NAME.DUAL_GUN)


class SniperModeByShiftSetting(StorageAccountSetting, MouseAffectedSetting):

    def _getCameras(self):
        return (CTRL_MODE_NAME.ARCADE, CTRL_MODE_NAME.SNIPER, CTRL_MODE_NAME.DUAL_GUN)


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


class DamageLogDetailsSetting(GroupSetting):
    SHOW_ALWAYS = 0
    SHOW_BY_ALT_PRESS = 1
    HIDE = 2
    _OPTIONS = {SHOW_ALWAYS: 'always',
     SHOW_BY_ALT_PRESS: 'byAlt',
     HIDE: 'hide'}

    def __init__(self, settingName, storage, isPreview=False):
        super(DamageLogDetailsSetting, self).__init__(settingName, storage, options=self._OPTIONS, settingsKey='#settings:feedback/tab/damageLogPanel/details/%s', isPreview=isPreview)

    def getDefaultValue(self):
        pass


class DamageLogEventTypesSetting(GroupSetting):
    ALL = 0
    ONLY_POSITIVE = 1
    ONLY_NEGATIVE = 2
    _OPTIONS = {ALL: 'both',
     ONLY_POSITIVE: 'positive',
     ONLY_NEGATIVE: 'negative'}

    def __init__(self, settingName, storage, isPreview=False):
        super(DamageLogEventTypesSetting, self).__init__(settingName, storage, options=self._OPTIONS, settingsKey='#settings:feedback/tab/damageLogPanel/eventTypes/%s', isPreview=isPreview)

    def getDefaultValue(self):
        pass


class DamageLogEventPositionsSetting(GroupSetting):
    ALL_BOTTOM = 0
    NEGATIVE_AT_TOP = 1
    _OPTIONS = {ALL_BOTTOM: 'bottom',
     NEGATIVE_AT_TOP: 'topBottom'}

    def __init__(self, settingName, storage, isPreview=False):
        super(DamageLogEventPositionsSetting, self).__init__(settingName, storage, options=self._OPTIONS, settingsKey='#settings:feedback/tab/damageLogPanel/eventPositions/%s', isPreview=isPreview)

    def getDefaultValue(self):
        pass


class BattleEventsSetting(SettingFalseByDefault):

    def __init__(self, settingName, storage, isPreview=False, delegate=lambda : True):
        self.__callable = delegate
        super(BattleEventsSetting, self).__init__(settingName, storage, isPreview)

    def _get(self):
        return None if not self.__callable() else super(BattleEventsSetting, self)._get()


class BattleBorderMapModeShow(GroupSetting):
    SHOW_BY_ALT_PRESS = 0
    SHOW_ALWAYS = 1
    HIDE = 2
    ALWAYS_HIDE = 3
    OPTIONS = {SHOW_BY_ALT_PRESS: 'alt',
     SHOW_ALWAYS: 'always',
     HIDE: 'hide',
     ALWAYS_HIDE: 'alwaysHide'}

    def __init__(self, settingName, storage, isPreview=False):
        super(BattleBorderMapModeShow, self).__init__(settingName, storage, options=self.OPTIONS, settingsKey='#settings:feedback/tab/borderMap/showMode/%s', isPreview=isPreview)

    def getDefaultValue(self):
        return self.SHOW_BY_ALT_PRESS


class BattleBorderMapType(GroupSetting):
    TYPE_WALL = 0
    TYPE_DOTTED = 1
    TYPE_HIDE = 2
    OPTIONS = {TYPE_WALL: 'wall',
     TYPE_DOTTED: 'dotted',
     TYPE_HIDE: 'hide'}

    def __init__(self, settingName, storage, isPreview=False):
        super(BattleBorderMapType, self).__init__(settingName, storage, options=self.OPTIONS, settingsKey='#settings:feedback/tab/borderMap/typeBorder/%s', isPreview=isPreview)

    def getDefaultValue(self):
        return self.TYPE_WALL


class LoginServerSelectionSetting(PreferencesSetting):

    def __init__(self, key):
        super(LoginServerSelectionSetting, self).__init__()
        self.__key = key
        self.__value = Settings.g_instance.userPrefs.readBool(self.__key, False)

    def _savePrefsCallback(self, _):
        Settings.g_instance.userPrefs.writeBool(self.__key, self.__value)

    def _readPrefsCallback(self, key, value):
        if key == self.__key:
            self.__value = value

    def _set(self, value):
        self.__value = value

    def _get(self):
        return self.__value


class QuestsProgressViewType(GroupSetting):
    TYPE_STANDARD = 0
    TYPE_HIDE = 1
    OPTIONS = {TYPE_STANDARD: 'standard',
     TYPE_HIDE: 'hidden'}

    def __init__(self, settingName, storage, isPreview=False):
        super(QuestsProgressViewType, self).__init__(settingName, storage, options=self.OPTIONS, settingsKey='#settings:feedback/tab/questsProgress/type/%s', isPreview=isPreview)

    def getDefaultValue(self):
        return self.TYPE_STANDARD


class QuestsProgressDisplayType(GroupSetting):
    SHOW_ALL = 0
    PROGRESS_ONLY = 1
    OPTIONS = {SHOW_ALL: 'showAll',
     PROGRESS_ONLY: 'showProgress'}

    def __init__(self, settingName, storage, isPreview=False):
        super(QuestsProgressDisplayType, self).__init__(settingName, storage, options=self.OPTIONS, settingsKey='#settings:feedback/tab/questsProgress/standardConditions/%s', isPreview=isPreview)

    def getDefaultValue(self):
        return self.SHOW_ALL


class SwitchSetupsInLoadingSetting(AccountSetting):
    _PackStructure = namedtuple('SwitchSetupsInLoadingSettingData', 'current options extraData')
    _ENABLED_BY_DEFAULT = ('LOW', 'MIN')
    __postProgressionCtrl = dependency.descriptor(IVehiclePostProgressionController)

    def pack(self):
        return self._PackStructure(self._get(), self._getOptions(), self.getExtraData())._asdict()

    def getExtraData(self):
        return {'enabled': self.__postProgressionCtrl.isSwitchSetupFeatureEnabled()}

    def _get(self):
        settingValue = super(SwitchSetupsInLoadingSetting, self)._get()
        return self.__detectDefaultValue() if settingValue is None else settingValue

    def getDefaultValue(self):
        settingValue = super(SwitchSetupsInLoadingSetting, self).getDefaultValue()
        return self.__detectDefaultValue(False) if settingValue is None else settingValue

    def __detectDefaultValue(self, write=True):
        presetIndx = BigWorld.detectGraphicsPresetFromSystemSettings()
        enabledPresets = [ BigWorld.getSystemPerformancePresetIdFromName(pName) for pName in self._ENABLED_BY_DEFAULT ]
        enabledByDefault = presetIndx in enabledPresets
        if write:
            AccountSettings.setSettings(self.key, enabledByDefault)
        return enabledByDefault
