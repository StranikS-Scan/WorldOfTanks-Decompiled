# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/radial_menu.py
from collections import namedtuple
import BigWorld
import CommandMapping
import GUI
from gui.Scaleform.daapi.view.meta.RadialMenuMeta import RadialMenuMeta
from gui.Scaleform.genConsts.BATTLE_ICONS_CONSTS import BATTLE_ICONS_CONSTS
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.battle_control.arena_info.arena_dp import ArenaDataProvider
from gui.battle_control.controllers.chat_cmd_ctrl import CHAT_COMMANDS, TARGET_TRANSLATION_MAPPING, TARGET_ACTIONS
from gui.battle_control.controllers.chat_cmd_ctrl import KB_MAPPING
from gui.shared.SoundEffectsId import SoundEffectsId
from gui.shared.utils.key_mapping import getScaleformKey
from helpers import dependency
from helpers import isPlayerAvatar
from skeletons.gui.battle_session import IBattleSessionProvider
_CMD_LOCALE_PFX = '#ingame_help:chatShortcuts/'
_SHORTCUTS_IN_GROUP = 6

class SHORTCUT_STATES(object):
    DEFAULT = 'default'
    ALLY = 'ally'
    ENEMY = 'enemy'
    ENEMY_SPG = 'enemy_spg'
    ALL = (DEFAULT,
     ALLY,
     ENEMY,
     ENEMY_SPG)


Shortcut = namedtuple('Shortcut', ('title', 'action', 'icon', 'groups', 'indexInGroup'))
SHORTCUTS = (Shortcut(title=_CMD_LOCALE_PFX + 'attack', action=CHAT_COMMANDS.ATTACK, icon=BATTLE_ICONS_CONSTS.ATTACK, groups=[SHORTCUT_STATES.DEFAULT], indexInGroup=4),
 Shortcut(title=_CMD_LOCALE_PFX + 'backToBase', action=CHAT_COMMANDS.BACKTOBASE, icon=BATTLE_ICONS_CONSTS.BACK_TO_BASE, groups=[SHORTCUT_STATES.DEFAULT, SHORTCUT_STATES.ENEMY, SHORTCUT_STATES.ENEMY_SPG], indexInGroup=1),
 Shortcut(title=_CMD_LOCALE_PFX + 'positive', action=CHAT_COMMANDS.POSITIVE, icon=BATTLE_ICONS_CONSTS.YES, groups=list(SHORTCUT_STATES.ALL), indexInGroup=0),
 Shortcut(title=_CMD_LOCALE_PFX + 'negative', action=CHAT_COMMANDS.NEGATIVE, icon=BATTLE_ICONS_CONSTS.NO, groups=list(SHORTCUT_STATES.ALL), indexInGroup=5),
 Shortcut(title=_CMD_LOCALE_PFX + 'helpMe', action=CHAT_COMMANDS.SOS, icon=BATTLE_ICONS_CONSTS.HELP_ME, groups=[SHORTCUT_STATES.DEFAULT, SHORTCUT_STATES.ENEMY, SHORTCUT_STATES.ENEMY_SPG], indexInGroup=3),
 Shortcut(title=_CMD_LOCALE_PFX + 'reloadingGun', action=CHAT_COMMANDS.RELOADINGGUN, icon=BATTLE_ICONS_CONSTS.RELOAD, groups=[SHORTCUT_STATES.DEFAULT, SHORTCUT_STATES.ENEMY, SHORTCUT_STATES.ENEMY_SPG], indexInGroup=2),
 Shortcut(title=_CMD_LOCALE_PFX + 'followMe', action=CHAT_COMMANDS.FOLLOWME, icon=BATTLE_ICONS_CONSTS.FOLLOW_ME, groups=[SHORTCUT_STATES.ALLY], indexInGroup=4),
 Shortcut(title=_CMD_LOCALE_PFX + 'toBack', action=CHAT_COMMANDS.TURNBACK, icon=BATTLE_ICONS_CONSTS.TURN_BACK, groups=[SHORTCUT_STATES.ALLY], indexInGroup=1),
 Shortcut(title=_CMD_LOCALE_PFX + 'helpMeEx', action=CHAT_COMMANDS.HELPME, icon=BATTLE_ICONS_CONSTS.HELP_ME_EX, groups=[SHORTCUT_STATES.ALLY], indexInGroup=3),
 Shortcut(title=_CMD_LOCALE_PFX + 'stop', action=CHAT_COMMANDS.STOP, icon=BATTLE_ICONS_CONSTS.STOP, groups=[SHORTCUT_STATES.ALLY], indexInGroup=2),
 Shortcut(title=_CMD_LOCALE_PFX + 'supportMeWithFire', action=CHAT_COMMANDS.SUPPORTMEWITHFIRE, icon=BATTLE_ICONS_CONSTS.SUPPORT, groups=[SHORTCUT_STATES.ENEMY], indexInGroup=4),
 Shortcut(title=_CMD_LOCALE_PFX + 'attackEnemy', action=CHAT_COMMANDS.ATTACKENEMY, icon=BATTLE_ICONS_CONSTS.ATTACK_SPG, groups=[SHORTCUT_STATES.ENEMY_SPG], indexInGroup=4))
SHORTCUT_SETS = {state:[None] * _SHORTCUTS_IN_GROUP for state in SHORTCUT_STATES.ALL}
for shortcut in SHORTCUTS:
    for group in shortcut.groups:
        SHORTCUT_SETS[group][shortcut.indexInGroup] = shortcut

def getKeyFromAction(action, cut=SHORTCUT_STATES.DEFAULT):
    """
    Gets the key buy given chat action and shortcut. Target actions
    use their base action.
    Args:
        action: chact action
        cut: chat short cut
    
    Returns:
        chat's Scaleform key
    """
    if action in TARGET_ACTIONS and cut != SHORTCUT_STATES.DEFAULT:
        for targetAction, targeData in TARGET_TRANSLATION_MAPPING.iteritems():
            if cut in targeData and action == targeData[cut]:
                action = targetAction
                break

    if action in KB_MAPPING:
        cmd = KB_MAPPING[action]
    else:
        return 0
    shortcut = CommandMapping.g_instance.getName(cmd)
    return getScaleformKey(CommandMapping.g_instance.get(shortcut))


class RadialMenu(RadialMenuMeta, BattleGUIKeyHandler):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(RadialMenu, self).__init__()
        self.__targetID = None
        self.__vehicleType = None
        return

    def handleEscKey(self, isDown):
        return True

    def onAction(self, action):
        chatCommands = self.sessionProvider.shared.chatCommands
        if chatCommands is not None:
            chatCommands.handleChatCommand(action, self.__targetID)
        return

    def onSelect(self):
        self.__playSound(SoundEffectsId.SELECT_RADIAL_BUTTON)

    def show(self):
        player = BigWorld.player()
        target = BigWorld.target()
        self.__targetID = target.id if target is not None else None
        screenWidth = BigWorld.screenWidth()
        screenHeight = BigWorld.screenHeight()
        guiScreenWidth, guiScreenHeight = GUI.screenResolution()
        ratioWidth = float(guiScreenWidth / screenWidth)
        ratioHeight = float(guiScreenHeight / screenHeight)
        ratio = (ratioWidth, ratioHeight)
        crosshairType = self.__getCrosshairType(player, target)
        ctrl = self.sessionProvider.shared.crosshair
        if ctrl is not None:
            position = ctrl.getScaledPosition()
        else:
            position = (guiScreenWidth >> 1, guiScreenHeight >> 1)
        if self.app is not None:
            self.app.registerGuiKeyHandler(self)
        self.as_showS(crosshairType, position, ratio)
        return

    def hide(self):
        if self.app is not None:
            self.app.unregisterGuiKeyHandler(self)
        self.as_hideS()
        return

    def _populate(self):
        super(RadialMenu, self)._populate()
        CommandMapping.g_instance.onMappingChanged += self.__onMappingChanged
        self.__updateMenu()
        arenaDP = self.sessionProvider.getArenaDP()
        if arenaDP is not None and isinstance(arenaDP, ArenaDataProvider):
            self.__vehicleType = arenaDP.getVehicleInfo().vehicleType.classTag
        return

    def _dispose(self):
        CommandMapping.g_instance.onMappingChanged -= self.__onMappingChanged
        super(RadialMenu, self)._dispose()

    def __onMappingChanged(self, *args):
        self.__updateMenu()

    def __updateMenu(self):
        data = []
        for state in SHORTCUT_STATES.ALL:
            stateData = map(lambda x, s=state: {'title': x.title,
             'action': x.action,
             'icon': x.icon,
             'key': getKeyFromAction(x.action, s)}, SHORTCUT_SETS[state])
            data.append({'state': state,
             'data': stateData})

        self.as_buildDataS(data)

    def __getCrosshairType(self, player, target):
        if not self.__isTargetCorrect(player, target):
            return SHORTCUT_STATES.DEFAULT
        elif target.publicInfo.team == player.team:
            return SHORTCUT_STATES.ALLY
        elif self.__vehicleType == 'SPG':
            return SHORTCUT_STATES.ENEMY_SPG
        else:
            return SHORTCUT_STATES.ENEMY

    def __isTargetCorrect(self, player, target):
        if target is not None and target.isAlive() and player is not None and isPlayerAvatar():
            vInfo = self.sessionProvider.getArenaDP().getVehicleInfo(target.id)
            return not vInfo.isActionsDisabled()
        else:
            return False

    def __playSound(self, soundName):
        if self.app.soundManager is not None:
            self.app.soundManager.playEffectSound(soundName)
        return
