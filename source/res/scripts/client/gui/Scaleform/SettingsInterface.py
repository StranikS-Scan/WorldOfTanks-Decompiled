# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/SettingsInterface.py
# Compiled at: 2019-03-14 20:33:41
import BigWorld, SoundGroups, ResMgr
import Keys, sys
from gui.GraphicsPresets import GraphicsPresets
from gui.GraphicsResolutions import g_graficsResolutions
from gui.Scaleform.utils.gui_items import listToDict
from gui.Scaleform.utils.key_mapping import getScaleformKey, getBigworldKey, getBigworldNameFromKey
from messenger import g_settings as messenger_settings
from windows import UIInterface
from debug_utils import LOG_DEBUG, LOG_NOTE, LOG_CURRENT_EXCEPTION
from account_helpers.AccountSettings import AccountSettings
from constants import IS_DEVELOPMENT
from post_processing import g_postProcessing
from functools import partial
import CommandMapping
import Settings
from adisp import process
from gui.Scaleform import VoiceChatInterface
from gui.Scaleform.Waiting import Waiting
from Vibroeffects import VibroManager
from LogitechMonitor import LogitechMonitor
from gui.Scaleform import FEATURES

class SettingsInterface(UIInterface):
    KEYBOARD_MAPPING_COMMANDS = {'movement': {'forward': 'CMD_MOVE_FORWARD',
                  'backward': 'CMD_MOVE_BACKWARD',
                  'left': 'CMD_ROTATE_LEFT',
                  'right': 'CMD_ROTATE_RIGHT',
                  'auto_rotation': 'CMD_CM_VEHICLE_SWITCH_AUTOROTATION'},
     'cruis_control': {'forward': 'CMD_INCREMENT_CRUISE_MODE',
                       'backward': 'CMD_DECREMENT_CRUISE_MODE',
                       'stop_fire': 'CMD_STOP_UNTIL_FIRE'},
     'firing': {'fire': 'CMD_CM_SHOOT',
                'lock_target': 'CMD_CM_LOCK_TARGET',
                'lock_target_off': 'CMD_CM_LOCK_TARGET_OFF',
                'alternate_mode': 'CMD_CM_ALTERNATE_MODE'},
     'equipment': {'item01': 'CMD_AMMO_CHOICE_1',
                   'item02': 'CMD_AMMO_CHOICE_2',
                   'item03': 'CMD_AMMO_CHOICE_3',
                   'item04': 'CMD_AMMO_CHOICE_4',
                   'item05': 'CMD_AMMO_CHOICE_5',
                   'item06': 'CMD_AMMO_CHOICE_6',
                   'item07': 'CMD_AMMO_CHOICE_7',
                   'item08': 'CMD_AMMO_CHOICE_8'},
     'shortcuts': {'my_target': 'CMD_CHAT_SHORTCUT_ATTACK_MY_TARGET',
                   'attack': 'CMD_CHAT_SHORTCUT_ATTACK',
                   'to_base': 'CMD_CHAT_SHORTCUT_BACKTOBASE',
                   'follow_me': 'CMD_CHAT_SHORTCUT_FOLLOWME',
                   'positive': 'CMD_CHAT_SHORTCUT_POSITIVE',
                   'negative': 'CMD_CHAT_SHORTCUT_NEGATIVE',
                   'help_me': 'CMD_CHAT_SHORTCUT_HELPME'},
     'camera': {'camera_up': 'CMD_CM_CAMERA_ROTATE_UP',
                'camera_down': 'CMD_CM_CAMERA_ROTATE_DOWN',
                'camera_left': 'CMD_CM_CAMERA_ROTATE_LEFT',
                'camera_right': 'CMD_CM_CAMERA_ROTATE_RIGHT'},
     'voicechat': {'pushToTalk': 'CMD_VOICECHAT_MUTE'},
     'logitech_keyboard': {'switch_view': 'CMD_LOGITECH_SWITCH_VIEW'},
     'minimap': {'sizeUp': 'CMD_MINIMAP_SIZE_UP',
                 'sizeDown': 'CMD_MINIMAP_SIZE_DOWN',
                 'visible': 'CMD_MINIMAP_VISIBLE'}}
    KEYBOARD_MAPPING_BLOCKS = {'movement': ('forward', 'backward', 'left', 'right', 'auto_rotation'),
     'cruis_control': ('forward', 'backward', 'stop_fire'),
     'firing': ('fire', 'lock_target', 'lock_target_off', 'alternate_mode'),
     'equipment': ('item01', 'item02', 'item03', 'item04', 'item05', 'item06', 'item07', 'item08'),
     'shortcuts': ('my_target', 'attack', 'to_base', 'follow_me', 'positive', 'negative', 'help_me'),
     'camera': ('camera_up', 'camera_down', 'camera_left', 'camera_right'),
     'voicechat': ('pushToTalk',),
     'logitech_keyboard': ('switch_view',),
     'minimap': ('sizeUp', 'sizeDown', 'visible')}
    KEYBOARD_MAPPING_BLOCKS_ORDER = ('movement', 'cruis_control', 'firing', 'vehicle_other', 'equipment', 'shortcuts', 'camera', 'voicechat', 'minimap', 'logitech_keyboard')
    POPULATE_UI = 'SettingsDialog.PopulateUI'
    APPLY_SETTINGS = 'SettingsDialog.ApplySettings'
    COMMIT_SETTINGS = 'SettingsDialog.CommitSettings'
    DELAY_SETTINGS = 'SettingsDialog.DelaySettings'
    AUTODETECT_QUALITY = 'SettingsDialog.AutodetectQuality'
    CURSOR_VALUES = {'mixing': 3,
     'gunTag': 6,
     'centralTag': 8,
     'net': 3,
     'reloader': 0,
     'condition': 0,
     'cassette': 0}
    MARKER_VALUES = {'Hp': 4,
     'Name': 3}
    MARKER_TYPES = ['Base', 'Alt']
    MOUSE_KEYS = {'ingame': {'arcadeSens': ('arcade', 'sensitivity'),
                'sniperSens': ('sniper', 'sensitivity'),
                'artSens': ('strategic', 'sensitivity'),
                'horInvert': ('arcade', 'horzInvert'),
                'vertInvert': ('arcade', 'vertInvert')},
     'lobby': {'arcadeSens': ('arcadeMode/camera', 'sensitivity', 'float'),
               'sniperSens': ('sniperMode/camera', 'sensitivity', 'float'),
               'artSens': ('strategicMode/camera', 'sensitivity', 'float'),
               'horInvert': ('arcadeMode/camera', 'horzInvert', 'bool'),
               'vertInvert': ('arcadeMode/camera', 'vertInvert', 'bool')},
     'default': {'arcadeSens': 1,
                 'sniperSens': 1,
                 'artSens': 1,
                 'horInvert': False,
                 'vertInvert': False}}

    def __init__(self, enableRedefineKeysMode=True):
        UIInterface.__init__(self)
        if not LogitechMonitor.isPresent() and self.KEYBOARD_MAPPING_BLOCKS.has_key('logitech_keyboard'):
            del self.KEYBOARD_MAPPING_BLOCKS['logitech_keyboard']
        if not FEATURES.MINIMAP_SIZE and self.KEYBOARD_MAPPING_BLOCKS.has_key('minimap'):
            del self.KEYBOARD_MAPPING_BLOCKS['minimap']
        self.__enableRedefineKeysMode = enableRedefineKeysMode
        self.graphicsPresets = GraphicsPresets()
        self.resolutions = g_graficsResolutions
        self.__currentSettings = None
        if not FEATURES.VOICE_CHAT and self.KEYBOARD_MAPPING_COMMANDS.has_key('voicechat'):
            if self.KEYBOARD_MAPPING_COMMANDS.has_key('voicechat'):
                del self.KEYBOARD_MAPPING_COMMANDS['voicechat']
            if self.KEYBOARD_MAPPING_BLOCKS.has_key('voicechat'):
                del self.KEYBOARD_MAPPING_BLOCKS['voicechat']
            self.KEYBOARD_MAPPING_BLOCKS_ORDER = list(self.KEYBOARD_MAPPING_BLOCKS_ORDER)
            del self.KEYBOARD_MAPPING_BLOCKS_ORDER[self.KEYBOARD_MAPPING_BLOCKS_ORDER.index('voicechat')]
            self.KEYBOARD_MAPPING_BLOCKS_ORDER = tuple(self.KEYBOARD_MAPPING_BLOCKS_ORDER)
        return

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.uiHolder.addExternalCallbacks({SettingsInterface.POPULATE_UI: self.onPopulateUI,
         SettingsInterface.APPLY_SETTINGS: self.onApplySettings,
         SettingsInterface.COMMIT_SETTINGS: self.onCommitSettings,
         SettingsInterface.DELAY_SETTINGS: self.onDelaySettings,
         SettingsInterface.AUTODETECT_QUALITY: self.onAutodetectSettings,
         'SettingsDialog.useRedifineKeysMode': self.onUseRedifineKeyMode,
         'SettingsDialog.processVivoxTest': self.onProcessVivoxTest,
         'SettingsDialog.voiceChatEnable': self.onVoiceChatEnable,
         'SettingsDialog.updateCaptureDevices': self.onUpdateCaptureDevices,
         'SettingsDialog.setVivoxMicVolume': self.onSetVivoxMicVolume})
        VibroManager.g_instance.onConnect += self.__vm_onConnect
        VibroManager.g_instance.onDisconnect += self.__vm_onDisconnect
        from game import g_guiResetters
        g_guiResetters.add(self.onRecreateDevice)
        BigWorld.wg_setAdapterOrdinalNotifyCallback(self.onRecreateDevice)

    def dispossessUI(self):
        self.uiHolder.removeExternalCallbacks(SettingsInterface.POPULATE_UI, SettingsInterface.APPLY_SETTINGS, SettingsInterface.COMMIT_SETTINGS, SettingsInterface.DELAY_SETTINGS, SettingsInterface.AUTODETECT_QUALITY, 'SettingsDialog.useRedifineKeysMode', 'SettingsDialog.processVivoxTest', 'SettingsDialog.voiceChatEnable', 'SettingsDialog.updateCaptureDevices', 'SettingsDialog.setVivoxMicVolume')
        VibroManager.g_instance.onConnect -= self.__vm_onConnect
        VibroManager.g_instance.onDisconnect -= self.__vm_onDisconnect
        from game import g_guiResetters
        g_guiResetters.discard(self.onRecreateDevice)
        BigWorld.wg_setAdapterOrdinalNotifyCallback(None)
        UIInterface.dispossessUI(self)
        return

    def __isReplayEnabled(self):
        prefs = Settings.g_instance.userPrefs
        try:
            return prefs['replayPrefs'].readBool('enabled', False)
        except:
            return False

    def __setReplayEnabled(self, isEnabled):
        prefs = Settings.g_instance.userPrefs
        try:
            prefs['replayPrefs'].writeBool('enabled', isEnabled)
            from BattleReplay import g_replayCtrl
            g_replayCtrl.enableAutoRecordingBattles(isEnabled)
        except:
            LOG_CURRENT_EXCEPTION()

    def onSetVivoxMicVolume(self, callbackId, value):
        import Vivox
        if round(SoundGroups.g_instance.getVolume('micVivox') * 100) != value:
            SoundGroups.g_instance.setVolume('micVivox', value / 100)
            Vivox.getResponseHandler().setMicrophoneVolume(int(value))

    def onVoiceChatEnable(self, callbackId, isEnable):
        self.__voiceChatEnable(isEnable)

    def __voiceChatEnable(self, isEnable):
        if isEnable is None:
            return
        else:
            preveVoIP = Settings.g_instance.userPrefs.readBool(Settings.KEY_ENABLE_VOIP)
            import Vivox
            if preveVoIP != isEnable:
                Vivox.getResponseHandler().enable(isEnable)
                Settings.g_instance.userPrefs.writeBool(Settings.KEY_ENABLE_VOIP, bool(isEnable))
                from gui.WindowsManager import g_windowsManager
                if g_windowsManager.battleWindow is not None and not isEnable:
                    g_windowsManager.battleWindow.speakingPlayersReset()
                LOG_NOTE('Change state of voip: %s' % str(isEnable))
            return

    def onUseRedifineKeyMode(self, callbackId, isUse):
        if self.__enableRedefineKeysMode:
            BigWorld.wg_setRedefineKeysMode(isUse)

    def onProcessVivoxTest(self, callbackId, isStart):
        LOG_DEBUG('Vivox test: %s' % str(isStart))
        import Vivox
        rh = Vivox.getResponseHandler()
        rh.enterTestChannel() if isStart else rh.leaveTestChannel()
        self.respond([callbackId, False])

    def __vm_onConnect(self):
        self.call('SettingsDialog.VibroManager.Connect')

    def __vm_onDisconnect(self):
        self.call('SettingsDialog.VibroManager.Disconnect')

    def __getVideoSettings(self):
        settings = {}
        settings['monitor'] = {'current': self.resolutions.monitorIndex,
         'real': self.resolutions.realMonitorIndex,
         'options': self.resolutions.monitorsList}
        settings['fullScreen'] = not self.resolutions.isVideoWindowed
        settings['windowSize'] = {'current': self.resolutions.windowSizeIndex,
         'options': self.resolutions.windowSizesList}
        settings['resolution'] = {'current': self.resolutions.videoModeIndex,
         'options': self.resolutions.videoModesList}
        return [settings]

    def __getSettings(self):
        settings = [self.graphicsPresets.getCurrentSettingsForGUI()]
        import Vivox
        rh = Vivox.getResponseHandler()
        mUserPref = messenger_settings.userPreferences
        vManager = VibroManager.g_instance
        vEffGroups = vManager.getGroupsSettings()
        vEffDefGroup = VibroManager.VibroManager.GroupSettings()
        vEffDefGroup.enabled = False
        vEffDefGroup.gain = 0
        cursorOld = AccountSettings.getSettings('cursor')
        cursors = dict()
        if cursorOld:
            try:
                for key, data in cursorOld:
                    AccountSettings.setSettings('cursor', False)
                    cursors[key] = {'alpha': data[0],
                     'type': data[1]}
                    AccountSettings.setSettings('cursors', cursors)

            except Exception:
                cursors = AccountSettings.getSettings('cursors')

        else:
            cursors = AccountSettings.getSettings('cursors')
        markers = AccountSettings.getSettings('markers')
        currentCaptureDeviceIdx = -1
        try:
            currentCaptureDeviceIdx = rh.captureDevices.index(rh.currentCaptureDevice)
        except:
            pass

        config = {'isApplyHighQualityPossible': BigWorld.isApplyHighQualityPossible(),
         'isMRTSupported': BigWorld.MRTSupported(),
         'aspectRatio': {'current': self.resolutions.aspectRatioIndex,
                         'options': self.resolutions.aspectRatiosList},
         'vertSync': self.resolutions.isVideoVSync,
         'tripleBuffered': self.resolutions.isTripleBuffered,
         'multisampling': {'current': self.resolutions.multisamplingTypeIndex,
                           'options': self.resolutions.multisamplingTypesList},
         'customAA': {'current': self.resolutions.customAAModeIndex,
                      'options': self.resolutions.customAAModesList},
         'gamma': self.resolutions.gamma,
         'masterVolume': round(SoundGroups.g_instance.getMasterVolume() * 100),
         'musicVolume': round(SoundGroups.g_instance.getVolume('music') * 100),
         'voiceVolume': round(SoundGroups.g_instance.getVolume('voice') * 100),
         'vehiclesVolume': round(SoundGroups.g_instance.getVolume('vehicles') * 100),
         'effectsVolume': round(SoundGroups.g_instance.getVolume('effects') * 100),
         'guiVolume': round(SoundGroups.g_instance.getVolume('gui') * 100),
         'ambientVolume': round(SoundGroups.g_instance.getVolume('ambient') * 100),
         'masterVivoxVolume': round(SoundGroups.g_instance.getVolume('masterVivox') * 100),
         'micVivoxVolume': round(SoundGroups.g_instance.getVolume('micVivox') * 100),
         'masterFadeVivoxVolume': round(SoundGroups.g_instance.getVolume('masterFadeVivox') * 100),
         'captureDevice': {'current': currentCaptureDeviceIdx,
                           'options': [ device.decode(sys.getfilesystemencoding()).encode('utf-8') for device in rh.captureDevices ]},
         'voiceChatNotSupported': rh.vivoxDomain == '' or not VoiceChatInterface.g_instance.ready,
         'datetimeIdx': mUserPref['datetimeIdx'],
         'showJoinLeaveMessages': mUserPref['showJoinLeaveMessages'],
         'enableOlFilter': mUserPref['enableOlFilter'],
         'enableSpamFilter': mUserPref['enableSpamFilter'],
         'enableStoreChatMws': mUserPref['enableStoreMws'],
         'enableStoreChatCws': mUserPref['enableStoreCws'],
         'invitesFromFriendsOnly': mUserPref['invitesFromFriendsOnly'],
         'showLangBar': Settings.g_instance.userPrefs.readBool(Settings.KEY_SHOW_LANGUAGE_BAR),
         'enableVoIP': Settings.g_instance.userPrefs.readBool(Settings.KEY_ENABLE_VOIP),
         'enablePostMortemEffect': g_postProcessing.getSetting('mortem_post_effect'),
         'nationalVoices': AccountSettings.getSettings('nationalVoices'),
         'isColorBlind': AccountSettings.getSettings('isColorBlind'),
         'minimapAlpha': AccountSettings.getSettings('minimapAlpha'),
         'vibroIsConnected': vManager.connect(),
         'vibroGain': vManager.getGain() * 100,
         'vibroEngine': vEffGroups.get('engine', vEffDefGroup).gain * 100,
         'vibroAcceleration': vEffGroups.get('acceleration', vEffDefGroup).gain * 100,
         'vibroShots': vEffGroups.get('shots', vEffDefGroup).gain * 100,
         'vibroHits': vEffGroups.get('hits', vEffDefGroup).gain * 100,
         'vibroCollisions': vEffGroups.get('collisions', vEffDefGroup).gain * 100,
         'vibroDamage': vEffGroups.get('damage', vEffDefGroup).gain * 100,
         'vibroGUI': vEffGroups.get('gui', vEffDefGroup).gain * 100,
         'ppShowLevels': AccountSettings.getSettings('players_panel')['showLevels'],
         'ppShowTypes': AccountSettings.getSettings('players_panel')['showTypes'],
         'replayEnabled': self.__isReplayEnabled(),
         'cursors': {'values': cursors,
                     'options': SettingsInterface.CURSOR_VALUES},
         'markers': {'values': markers,
                     'options': SettingsInterface.MARKER_VALUES,
                     'types': SettingsInterface.MARKER_TYPES}}
        settings.append(config)
        cmdMap = CommandMapping.g_instance
        defaults = cmdMap.getDefaults()
        keyboard = []
        for group_name in self.KEYBOARD_MAPPING_BLOCKS_ORDER:
            if group_name in self.KEYBOARD_MAPPING_BLOCKS.keys():
                group = {'id': group_name,
                 'commands': []}
                keyboard.append(group)
                for key_setting in self.KEYBOARD_MAPPING_BLOCKS[group_name]:
                    command = cmdMap.getCommand(self.KEYBOARD_MAPPING_COMMANDS[group_name][key_setting])
                    keyCode = cmdMap.get(self.KEYBOARD_MAPPING_COMMANDS[group_name][key_setting])
                    defaultCode = defaults[command] if defaults.has_key(command) else 0
                    key = {'id': key_setting,
                     'command': command,
                     'key': getScaleformKey(keyCode),
                     'keyDefault': getScaleformKey(defaultCode)}
                    group['commands'].append(key)

        settings.append(keyboard)
        mouse = {}
        player = BigWorld.player()
        if hasattr(player.inputHandler, 'ctrls'):
            for key, path in SettingsInterface.MOUSE_KEYS['ingame'].items():
                mouse[key] = {'defaultValue': SettingsInterface.MOUSE_KEYS['default'][key],
                 'value': player.inputHandler.ctrls[path[0]].camera.getUserConfigValue(path[1])}

        else:
            ds = Settings.g_instance.userPrefs[Settings.KEY_CONTROL_MODE]
            for key, path in SettingsInterface.MOUSE_KEYS['lobby'].items():
                default = SettingsInterface.MOUSE_KEYS['default'][key]
                value = default
                if ds is not None:
                    if path[2] == 'float':
                        value = ds[path[0]].readFloat(path[1], default)
                    elif path[2] == 'bool':
                        value = ds[path[0]].readBool(path[1], default)
                    else:
                        LOG_DEBUG('Unknown mouse settings type %s %s' % (key, path))
                mouse[key] = {'defaultValue': default,
                 'value': value}

        settings.append(mouse)
        return settings

    def onUpdateCaptureDevices(self, callbackId):
        self.__updateCaptureDevices()

    @process
    def __updateCaptureDevices(self):
        Waiting.show('__updateCaptureDevices')
        import Vivox
        devices = yield VoiceChatInterface.g_instance.requestCaptureDevices()
        currentCaptureDeviceIdx = -1
        try:
            currentCaptureDeviceIdx = devices.index(Vivox.getResponseHandler().currentCaptureDevice)
        except:
            pass

        value = [currentCaptureDeviceIdx]
        value.extend([ d.decode(sys.getfilesystemencoding()).encode('utf-8') for d in devices ])
        Waiting.hide('__updateCaptureDevices')
        self.call('SettingsDialog.updateCaptureDevices', value)

    def onRecreateDevice(self):
        if self.__currentSettings and self.__currentSettings != self.__getVideoSettings():
            self.__currentSettings = self.__getVideoSettings()
            self.callNice('SettingsDialog.PopulateVideo', self.__getVideoSettings())

    def onAutodetectSettings(self, callbackID):
        presetIndex = BigWorld.autoDetectGraphicsSettings()
        self.call('SettingsDialog.setPreset', [presetIndex])

    def onPopulateUI(self, *args):
        self.__currentSettings = self.__getVideoSettings()
        VoiceChatInterface.g_instance.processFailedMessage()
        self.callNice('SettingsDialog.PopulateUI', self.__getSettings())
        self.callNice('SettingsDialog.PopulateVideo', self.__getVideoSettings())

    def onApplySettings(self, callbackId, settings):
        monitorIndex, presetIndex, settingsList = settings
        if monitorIndex != self.resolutions.realMonitorIndex:
            self.call('SettingsDialog.ApplySettings', ['restartNeeded'])
            return
        applyPresets = self.graphicsPresets.checkApplyGraphicsPreset(int(presetIndex), settingsList)
        self.call('SettingsDialog.ApplySettings', [applyPresets])

    def onDelaySettings(self, *args):
        self.apply(False, *args)

    def onCommitSettings(self, *args):
        self.apply(True, *args)

    def apply(self, restartApproved, callbackId, settings):
        restartClient = False
        import Vivox
        ppSettings = dict(AccountSettings.getSettings('players_panel'))
        ppSettings['showLevels'] = settings['ppShowLevels']
        ppSettings['showTypes'] = settings['ppShowTypes']
        if settings['monitor'] != self.resolutions.realMonitorIndex:
            restartClient = True
        AccountSettings.setSettings('players_panel', ppSettings)
        self.__setReplayEnabled(settings['replayEnabled'])
        AccountSettings.setSettings('nationalVoices', settings['nationalVoices'])
        AccountSettings.setSettings('isColorBlind', settings['isColorBlind'])
        AccountSettings.setSettings('minimapAlpha', settings['minimapAlpha'])
        AccountSettings.setSettings('cursors', settings['cursor'])
        AccountSettings.setSettings('markers', settings['markers'])
        Settings.g_instance.userPrefs.writeBool(Settings.KEY_SHOW_LANGUAGE_BAR, settings['showLangBar'])
        vManager = VibroManager.g_instance
        vManager.setGain(settings['vibroGain'] / 100.0)
        vEffGroups = vManager.getGroupsSettings()
        for groupName, newValue in [('engine', settings['vibroEngine']),
         ('acceleration', settings['vibroAcceleration']),
         ('shots', settings['vibroShots']),
         ('hits', settings['vibroHits']),
         ('collisions', settings['vibroCollisions']),
         ('damage', settings['vibroDamage']),
         ('gui', settings['vibroGUI'])]:
            if groupName in vEffGroups:
                vEffGroups[groupName].gain = newValue / 100.0
                vEffGroups[groupName].enabled = newValue > 0

        vManager.setGroupsSettings(vEffGroups)
        self.__voiceChatEnable(settings['enableVoIP'])
        g_postProcessing.setSetting('mortem_post_effect', settings['enablePostMortemEffect'])
        self.uiHolder.clearCommands()
        cmdMap = CommandMapping.g_instance
        keyboard = settings['controls']['keyboard']
        for i in xrange(len(self.KEYBOARD_MAPPING_BLOCKS)):
            group_name = keyboard[i]['id']
            for j in xrange(len(self.KEYBOARD_MAPPING_BLOCKS[group_name])):
                key_name = keyboard[i]['commands'][j]['id']
                key = 'KEY_NONE'
                if keyboard[i]['commands'][j]['key'] != 0:
                    key = getBigworldNameFromKey(getBigworldKey(keyboard[i]['commands'][j]['key']))
                cmdMap.remove(self.KEYBOARD_MAPPING_COMMANDS[group_name][key_name])
                cmdMap.add(self.KEYBOARD_MAPPING_COMMANDS[group_name][key_name], key)

        cmdMap.save()
        self.uiHolder.bindCommands()
        player = BigWorld.player()
        mouse = settings['controls']['mouse']
        if hasattr(player.inputHandler, 'ctrls'):
            player.inputHandler.ctrls['arcade'].camera.setUserConfigValue('sensitivity', mouse['arcadeSens']['value'])
            player.inputHandler.ctrls['sniper'].camera.setUserConfigValue('sensitivity', mouse['sniperSens']['value'])
            player.inputHandler.ctrls['strategic'].camera.setUserConfigValue('sensitivity', mouse['artSens']['value'])
            for mode in ('arcade', 'sniper', 'strategic'):
                player.inputHandler.ctrls[mode].camera.setUserConfigValue('horzInvert', bool(mouse['horInvert']['value']))
                player.inputHandler.ctrls[mode].camera.setUserConfigValue('vertInvert', bool(mouse['vertInvert']['value']))

        else:
            ds = Settings.g_instance.userPrefs[Settings.KEY_CONTROL_MODE]
            if ds:
                ds['arcadeMode/camera'].writeFloat('sensitivity', mouse['arcadeSens']['value'])
                ds['sniperMode/camera'].writeFloat('sensitivity', mouse['sniperSens']['value'])
                ds['strategicMode/camera'].writeFloat('sensitivity', mouse['artSens']['value'])
                for mode in ('arcadeMode', 'sniperMode', 'strategicMode'):
                    ds['%s/camera' % mode].writeBool('horzInvert', bool(mouse['horInvert']['value']))
                    ds['%s/camera' % mode].writeBool('vertInvert', bool(mouse['vertInvert']['value']))

        self.resolutions.applyChanges(settings['fullScreen'], settings['vertSync'], settings['tripleBuffered'], settings['windowSize'] if not settings['fullScreen'] else settings['resolution'], settings['aspectRatio'], settings['multisampling'], settings['customAA'], settings['gamma'], settings['monitor'])
        if round(SoundGroups.g_instance.getVolume('masterVivox') * 100) != settings['masterVivoxVolume']:
            Vivox.getResponseHandler().setMasterVolume(settings['masterVivoxVolume'])
        if round(SoundGroups.g_instance.getVolume('micVivox') * 100) != settings['micVivoxVolume']:
            Vivox.getResponseHandler().setMicrophoneVolume(settings['micVivoxVolume'])
        SoundGroups.g_instance.setMasterVolume(float(settings['masterVolume']) / 100)
        SoundGroups.g_instance.setVolume('music', float(settings['musicVolume']) / 100)
        SoundGroups.g_instance.setVolume('voice', float(settings['voiceVolume']) / 100)
        SoundGroups.g_instance.setVolume('vehicles', float(settings['vehiclesVolume']) / 100)
        SoundGroups.g_instance.setVolume('effects', float(settings['effectsVolume']) / 100)
        SoundGroups.g_instance.setVolume('gui', float(settings['guiVolume']) / 100)
        SoundGroups.g_instance.setVolume('ambient', float(settings['ambientVolume']) / 100)
        SoundGroups.g_instance.setVolume('masterVivox', float(settings['masterVivoxVolume']) / 100)
        SoundGroups.g_instance.setVolume('micVivox', float(settings['micVivoxVolume']) / 100)
        SoundGroups.g_instance.setVolume('masterFadeVivox', float(settings['masterFadeVivoxVolume']) / 100)
        if len(Vivox.getResponseHandler().captureDevices):
            device = Vivox.getResponseHandler().captureDevices[0]
            if len(Vivox.getResponseHandler().captureDevices) > settings['captureDevice']:
                device = Vivox.getResponseHandler().captureDevices[settings['captureDevice']]
            Vivox.getResponseHandler().setCaptureDevice(device)
        messenger_settings.applyUserPreferences(datetimeIdx=settings['datetimeIdx'], showJoinLeaveMessages=settings['showJoinLeaveMessages'], enableOlFilter=settings['enableOlFilter'], enableSpamFilter=settings['enableSpamFilter'], enableStoreMws=settings['enableStoreChatMws'], enableStoreCws=settings['enableStoreChatCws'], invitesFromFriendsOnly=settings['invitesFromFriendsOnly'])
        qualitySettings = settings['quality']
        applyPresets = self.graphicsPresets.checkApplyGraphicsPreset(int(settings['graphicsQuality']), qualitySettings)
        if applyPresets:
            self.graphicsPresets.applyGraphicsPresets(int(settings['graphicsQuality']), qualitySettings)
            if applyPresets == 'restartNeeded':
                BigWorld.commitPendingGraphicsSettings()
                restartClient = True
            elif applyPresets == 'hasPendingSettings':
                BigWorld.commitPendingGraphicsSettings()
        g_postProcessing.refresh()
        from AvatarInputHandler.cameras import SniperCamera
        SniperCamera._USE_SWINGING = BigWorld.wg_isSniperModeSwingingEnabled()
        if hasattr(player.inputHandler, 'ctrl'):
            if player.inputHandler.ctrl == player.inputHandler.ctrls['sniper']:
                player.inputHandler.ctrl.recreateCamera()
        if restartClient:
            BigWorld.savePreferences()
            if restartApproved:
                BigWorld.callback(0.3, BigWorld.restartGame)
            else:
                BigWorld.callback(0.0, partial(BigWorld.changeVideoMode, -1, BigWorld.isVideoWindowed()))
