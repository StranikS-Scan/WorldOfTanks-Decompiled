# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/RadialMenu.py
from weakref import proxy
import BigWorld
import Keys
import GUI
from gui.battle_control import g_sessionProvider
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from helpers import isPlayerAvatar
from gui.shared.utils.key_mapping import getScaleformKey, BW_TO_SCALEFORM
from debug_utils import LOG_ERROR
from gui.Scaleform.windows import UIInterface
import CommandMapping
import FMOD

class RadialMenu(UIInterface):
    DEFAULT_CUT = 'default'
    ALLY_CUT = 'ally'
    ENEMY_CUT = 'enemy'
    ENEMY_SPG_CUT = 'enemy_spg'
    if FMOD.enabled:
        SELECT_EFFECT_SND = 'effects.select_radial_button'
    INDEX_REFERENCES = (2, 1, 5, 4, 0, 3)
    ALL_SHORTCUTS = {DEFAULT_CUT: {'labels': ['attack',
                              'backToBase',
                              'positive',
                              'negative',
                              'helpMe',
                              'reloadingGun'],
                   'commands': ['ATTACK',
                                'BACKTOBASE',
                                'POSITIVE',
                                'NEGATIVE',
                                'HELPME',
                                'RELOADINGGUN'],
                   'icons': ['Attack',
                             'Backtobase',
                             'Yes',
                             'No',
                             'Helpme',
                             'Reload']},
     ALLY_CUT: {'labels': ['followMe',
                           'toBack',
                           'positive',
                           'negative',
                           'helpMeEx',
                           'stop'],
                'commands': ['FOLLOWME',
                             'TURNBACK',
                             'POSITIVE',
                             'NEGATIVE',
                             'HELPMEEX',
                             'STOP'],
                'icons': ['Followme',
                          'Turnback',
                          'Yes',
                          'No',
                          'Helpmeex',
                          'Stop']},
     ENEMY_CUT: {'labels': ['supportMeWithFire',
                            'backToBase',
                            'positive',
                            'negative',
                            'helpMe',
                            'reloadingGun'],
                 'commands': ['SUPPORTMEWITHFIRE',
                              'BACKTOBASE',
                              'POSITIVE',
                              'NEGATIVE',
                              'HELPME',
                              'RELOADINGGUN'],
                 'icons': ['Support',
                           'Backtobase',
                           'Yes',
                           'No',
                           'Helpme',
                           'Reload']},
     ENEMY_SPG_CUT: {'labels': ['attackEnemy',
                                'backToBase',
                                'positive',
                                'negative',
                                'helpMe',
                                'reloadingGun'],
                     'commands': ['ATTACKENEMY',
                                  'BACKTOBASE',
                                  'POSITIVE',
                                  'NEGATIVE',
                                  'HELPME',
                                  'RELOADINGGUN'],
                     'icons': ['AttackSPG',
                               'Backtobase',
                               'Yes',
                               'No',
                               'Helpme',
                               'Reload']}}
    DENIED_KEYB_CMDS = ['ATTACK']
    TARGET_ACTIONS = ['FOLLOWME',
     'TURNBACK',
     'HELPMEEX',
     'SUPPORTMEWITHFIRE',
     'ATTACKENEMY',
     'STOP']
    RELOADING_GUN_ACTION = 'RELOADINGGUN'

    def __init__(self, parentUI):
        UIInterface.__init__(self)
        self.proxy = proxy(self)
        self.GUICtrl = None
        self.__parentUI = parentUI
        self.__settings = None
        self.__currentTarget = None
        self.__currentVehicleDesc = None
        self.__showed = False
        return

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.GUICtrl = self.uiHolder.getMember('_level0.radialMenu')
        self.GUICtrl.script = self
        for state in self.ALL_SHORTCUTS:
            self.GUICtrl.setState(state)
            list = self.__getDataForFlash(state)
            self.GUICtrl.buildData(list)

        g_eventBus.addListener(GameEvent.RADIAL_MENU_CMD, self.__handleRadialMenuCmd, scope=EVENT_BUS_SCOPE.BATTLE)

    def setSettings(self, settings):
        self.__settings = settings
        SHCTS_SECTION = 'shortcuts'
        self.KEYB_MAPPINGS = self.__settings.KEYBOARD_MAPPING_BLOCKS[SHCTS_SECTION]
        self.KEYB_CMDS_MAPPINGS = self.__settings.KEYBOARD_MAPPING_COMMANDS[SHCTS_SECTION]

    def __handleRadialMenuCmd(self, event):
        ctx = event.ctx
        key, isDown, offset = ctx['key'], ctx['isDown'], ctx['offset']
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFired(CommandMapping.CMD_RADIAL_MENU_SHOW, key):
            if isDown:
                if self.__currentVehicleDesc is None:
                    self.__currentVehicleDesc = self.__getCurrentVehicleDesc()
                if self.__currentVehicleDesc is not None:
                    self.__currentTarget = BigWorld.target()
                    mouseUsedForShow = getScaleformKey(key) <= BW_TO_SCALEFORM[Keys.KEY_MOUSE7]
                    self.__onMenuShow(offset, mouseUsedForShow)
            else:
                self.__onMenuHide()
        elif isDown:
            if not self.__ingameMenuIsVisible():
                if self.__currentVehicleDesc is None:
                    self.__currentVehicleDesc = self.__getCurrentVehicleDesc()
                if not self.__showed:
                    self.__currentTarget = BigWorld.target()
                for command in self.KEYB_MAPPINGS:
                    shortcut = self.KEYB_CMDS_MAPPINGS[command]
                    if cmdMap.isFired(getattr(CommandMapping, shortcut), key):
                        action = self.__getMappedCommand(command)
                        if action not in self.DENIED_KEYB_CMDS:
                            self.onAction(action)

        return

    def __getDataForFlash(self, crosshairType):
        if crosshairType != '':
            CMD_LOCALE_PFX = '#ingame_help:chatShortcuts/'
            need_shortcuts = self.ALL_SHORTCUTS[crosshairType]
            flashData = []
            for i, shortcut_key in enumerate(self.KEYB_MAPPINGS):
                index = self.INDEX_REFERENCES[i]
                title = need_shortcuts['labels'][index]
                action = need_shortcuts['commands'][index]
                icon = need_shortcuts['icons'][index]
                data = {'title': CMD_LOCALE_PFX + title,
                 'action': action,
                 'icon': icon}
                flashData.append(data)

            return flashData
        LOG_ERROR('Unknown vehicle type under crosshair target')

    def __getKeysList(self, crosshairType):
        if crosshairType != '':
            keys = []
            need_shortcuts = self.ALL_SHORTCUTS[crosshairType]
            for i, shortcut_key in enumerate(self.KEYB_MAPPINGS):
                index = self.INDEX_REFERENCES[i]
                action = need_shortcuts['commands'][index]
                if action not in self.DENIED_KEYB_CMDS:
                    shortcut = self.KEYB_CMDS_MAPPINGS[self.KEYB_MAPPINGS[index]]
                    keyCode = getScaleformKey(CommandMapping.g_instance.get(shortcut))
                    keys.append(keyCode)
                else:
                    keys.append(0)

            return keys
        LOG_ERROR('Unknown vehicle type under crosshair target')

    def __getMappedCommand(self, shortcut):
        crosshairType = self.__getCrosshairType()
        index = self.__settings.KEYBOARD_MAPPING_BLOCKS['shortcuts'].index(shortcut)
        return self.ALL_SHORTCUTS[crosshairType]['commands'][index]

    def __getCrosshairType(self):
        player = BigWorld.player()
        outcome = self.DEFAULT_CUT
        if self.__isTargetCorrect(player):
            if self.__currentTarget.publicInfo.team == player.team:
                outcome = self.ALLY_CUT
            elif 'SPG' in self.__currentVehicleDesc['vehicleType'].type.tags:
                outcome = self.ENEMY_SPG_CUT
            else:
                outcome = self.ENEMY_CUT
        return outcome

    def __isTargetCorrect(self, player):
        import Vehicle
        if self.__currentTarget is not None and isinstance(self.__currentTarget, Vehicle.Vehicle):
            if self.__currentTarget.isAlive():
                if player is not None and isPlayerAvatar():
                    vInfo = g_sessionProvider.getArenaDP().getVehicleInfo(self.__currentTarget.id)
                    return not vInfo.isActionsDisabled()
        return False

    def __getCurrentVehicleDesc(self):
        player = BigWorld.player()
        vehicles = player.arena.vehicles
        for vID, desc in vehicles.items():
            if vID == player.playerVehicleID:
                return desc

    def __getFireKeyCode(self):
        fireKey = self.__settings.KEYBOARD_MAPPING_COMMANDS['firing']['fire']
        return getScaleformKey(fireKey)

    def __playSound(self, soundName):
        print 'radial', soundName
        if self.uiHolder.soundManager is not None:
            self.uiHolder.soundManager.playSound(soundName)
        return

    def onSelectButton(self):
        self.__playSound(self.SELECT_EFFECT_SND)

    def onAction(self, action):
        chatCommands = g_sessionProvider.getChatCommands()
        if action in self.TARGET_ACTIONS:
            chatCommands.sendTargetedCommand(action, self.__currentTarget.id)
        elif action == self.RELOADING_GUN_ACTION:
            chatCommands.sendReloadingCommand()
        else:
            chatCommands.sendCommand(action)

    def __onMenuShow(self, offset, mouseUsedForShow):
        if not self.__ingameMenuIsVisible():
            screenWidth = BigWorld.screenWidth()
            screenHeight = BigWorld.screenHeight()
            guiScreenWidth, guiScreenHeight = GUI.screenResolution()
            ratioWidth = float(guiScreenWidth / screenWidth)
            ratioHeight = float(guiScreenHeight / screenHeight)
            self.call('RadialMenu.setRatio', [ratioWidth, ratioHeight])
            crosshairType = self.__getCrosshairType()
            keys = self.__getKeysList(crosshairType)
            self.GUICtrl.setFireKeyCode(self.__getFireKeyCode())
            self.GUICtrl.setState(crosshairType)
            self.GUICtrl.updateKeys(keys)
            screenWidth, screenHeight = GUI.screenResolution()
            mouseLeft, mouseTop = offset
            x = round(screenWidth / 2.0 * mouseLeft)
            y = -round(screenHeight / 2.0 * mouseTop)
            offset = (x, y)
            self.__showed = True
            self.GUICtrl.show(offset, mouseUsedForShow)

    def __ingameMenuIsVisible(self):
        battle = self.uiHolder.getMember('_level0')
        return battle.ingameMenusWasShowed()

    def __onMenuHide(self):
        self.__showed = False
        if self.GUICtrl is not None:
            self.GUICtrl.hide()
        return

    def forcedHide(self):
        self.__onMenuHide()

    def destroy(self):
        g_eventBus.removeListener(GameEvent.RADIAL_MENU_CMD, self.__handleRadialMenuCmd, scope=EVENT_BUS_SCOPE.BATTLE)
        self.KEYB_MAPPINGS = None
        self.KEYB_CMDS_MAPPINGS = None
        self.__settings = None
        self.GUICtrl.script = None
        self.GUICtrl = None
        return
