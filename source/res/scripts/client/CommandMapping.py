# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CommandMapping.py
import BigWorld
import ResMgr
import Keys
import Event
import Settings
from shared_utils import findFirst
from debug_utils import LOG_DEBUG
g_instance = None
CMD_MOVE_FORWARD = 1
CMD_MOVE_FORWARD_SPEC = 2
CMD_MOVE_BACKWARD = 3
CMD_ROTATE_LEFT = 4
CMD_ROTATE_RIGHT = 5
CMD_INCREMENT_CRUISE_MODE = 6
CMD_DECREMENT_CRUISE_MODE = 7
CMD_STOP_UNTIL_FIRE = 8
CMD_SWITCH_SERVER_MARKER = 9
CMD_AMMO_CHOICE_1 = 10
CMD_AMMO_CHOICE_2 = 11
CMD_AMMO_CHOICE_3 = 12
CMD_AMMO_CHOICE_4 = 13
CMD_AMMO_CHOICE_5 = 14
CMD_AMMO_CHOICE_6 = 15
CMD_AMMO_CHOICE_7 = 16
CMD_AMMO_CHOICE_8 = 17
CMD_AMMO_CHOICE_9 = 18
CMD_AMMO_CHOICE_0 = 19
CMD_CHAT_SHORTCUT_BACKTOBASE = 22
CMD_CHAT_SHORTCUT_NEGATIVE = 25
CMD_CHAT_SHORTCUT_HELPME = 26
CMD_CM_SHOOT = 27
CMD_CM_SWITCH_TRAJECTORY = 28
CMD_CM_FREE_CAMERA = 29
CMD_CM_LOCK_TARGET = 30
CMD_CM_LOCK_TARGET_OFF = 31
CMD_CM_CAMERA_ROTATE_LEFT = 32
CMD_CM_CAMERA_ROTATE_RIGHT = 33
CMD_CM_CAMERA_ROTATE_UP = 34
CMD_CM_CAMERA_ROTATE_DOWN = 35
CMD_CM_VEHICLE_SWITCH_AUTOROTATION = 36
CMD_CM_INCREASE_ZOOM = 37
CMD_CM_DECREASE_ZOOM = 38
CMD_CM_ALTERNATE_MODE = 39
CMD_CM_CAMERA_RESTORE_DEFAULT = 40
CMD_CM_POSTMORTEM_NEXT_VEHICLE = 41
CMD_CM_POSTMORTEM_SELF_VEHICLE = 42
CMD_VEHICLE_MARKERS_SHOW_INFO = 43
CMD_AMMO_PANEL_SELECT = 44
CMD_MINIMAP_HIGHLIGHT_CELL = 45
CMD_MINIMAP_VEHICLE_SPECIFIC = 46
CMD_MINIMAP_SIZE_UP = 47
CMD_MINIMAP_SIZE_DOWN = 48
CMD_MINIMAP_VISIBLE = 49
CMD_VOICECHAT_MUTE = 50
CMD_TOGGLE_GUI = 53
CMD_RELOAD_PARTIAL_CLIP = 54
CMD_RADIAL_MENU_SHOW = 55
CMD_CHAT_SHORTCUT_RELOAD = 56
CMD_VOICECHAT_ENABLE = 57
CMD_BLOCK_TRACKS = 58
CMD_CM_TRAJECTORY_VIEW = 59
EPIC_GLOBAL_MSG_SAVE_TANKS = 60
EPIC_GLOBAL_MSG_TIME = 61
EPIC_GLOBAL_MSG_LEFT_LANE = 62
EPIC_GLOBAL_MSG_CENTER_LANE = 63
EPIC_GLOBAL_MSG_RIGHT_LANE = 64
EPIC_GLOBAL_MSG_FOCUS_HQ = 65
CMD_REQUEST_RECOVERY = 66
CMD_QUEST_PROGRESS_SHOW = 67
CMD_SHOW_HELP = 68
CMD_CM_CHARGE_SHOT = 69
CO_DEPENDENT_KEYS = {'CMD_CM_CHARGE_SHOT': 'CMD_CM_SHOOT'}
CMD_CHAT_SHORTCUT_CONTEXT_COMMAND = 70
CMD_CHAT_SHORTCUT_CONTEXT_COMMIT = 71
CMD_CHAT_SHORTCUT_THANKYOU = 72
CMD_CM_VEHICLE_UPGRADE_PANEL_LEFT = 73
CMD_CM_VEHICLE_UPGRADE_PANEL_RIGHT = 74
CMD_CM_VEHICLE_UPGRADE_PANEL_ALTERNATIVE_LEFT = 75
CMD_CM_VEHICLE_UPGRADE_PANEL_ALTERNATIVE_RIGHT = 76
CMD_UPGRADE_PANEL_SHOW = 77
CMD_CM_VEHICLE_ACTIVATE_RADAR = 78
CMD_CHAT_SHORTCUT_AFFIRMATIVE = 79

class CommandMapping(object):
    __DEFAULT_CONFIG_FILE_NAME = 'scripts/command_mapping.xml'
    __USER_CONFIG_SECTION_NAME = 'commandMapping'
    onMappingChanged = Event.Event()

    def __init__(self):
        self.__mapping = {}
        self.__dictCommand2CommandName = {}
        self.restoreUserConfig()

    def add(self, commandName, fireKeyName, satelliteKeyNames=None, isDefault=False):
        satelliteKeyNames = satelliteKeyNames or []
        try:
            command = int(self.getCommand(commandName))
            fireKey = int(Keys.__dict__.get(fireKeyName))
            satelliteKeys = tuple((int(Keys.__dict__.get(x)) for x in satelliteKeyNames))
            keyInfo = (command, satelliteKeys, isDefault)
        except Exception:
            return False

        if not isDefault:
            if not self.__checkUserKey(fireKey):
                return False
            for key in satelliteKeys:
                if not self.__checkUserKey(key):
                    return False

        if fireKey not in self.__mapping:
            self.__mapping[fireKey] = []
        if keyInfo not in self.__mapping[fireKey]:
            self.__mapping[fireKey].append(keyInfo)
        self.__dictCommand2CommandName[command] = commandName
        return True

    def get(self, commandName):
        try:
            command = int(self.getCommand(commandName))
            for fireKey, listKeyInfo in self.__mapping.iteritems():
                for keyInfo in listKeyInfo:
                    if keyInfo[0] == command and not keyInfo[1]:
                        return fireKey

        except Exception:
            return None

        return None

    def getCommandKeys(self, command):
        for fireKey, listKeyInfo in self.__mapping.iteritems():
            for keyInfo in listKeyInfo:
                if keyInfo[0] == command:
                    return (fireKey, keyInfo[1])

        return None

    def remove(self, commandName, fireKeyName=None, satelliteKeyNames=None, isDefault=None):
        try:
            delCommand = int(self.getCommand(commandName))
            delFireKey = None if fireKeyName is None else int(Keys.__dict__.get(fireKeyName))
            if satelliteKeyNames is None:
                delSatelliteKeys = None
            else:
                delSatelliteKeys = tuple((int(Keys.__dict__.get(x)) for x in satelliteKeyNames))
            delIsDefault = isDefault
        except Exception:
            return False

        delListFireKey = []
        for fireKey in self.__mapping:
            if delFireKey is not None:
                if fireKey != delFireKey:
                    continue
            delListKeyInfo = []
            for keyInfo in self.__mapping[fireKey]:
                if keyInfo[0] != delCommand:
                    continue
                if delSatelliteKeys is not None:
                    if keyInfo[1] != delSatelliteKeys:
                        continue
                if delIsDefault is not None:
                    if keyInfo[2] != delIsDefault:
                        continue
                delListKeyInfo.append(keyInfo)

            for keyInfo in delListKeyInfo:
                self.__mapping[fireKey].remove(keyInfo)

            if not self.__mapping[fireKey]:
                delListFireKey.append(fireKey)

        for fireKey in delListFireKey:
            del self.__mapping[fireKey]

        return True

    def clear(self):
        self.__mapping = {}

    def restoreDefault(self):
        self.clear()
        self.__loadDefault()
        self.__loadDevelopment()

    def restoreUserConfig(self):
        self.clear()
        self.__loadDefault()
        self.__loadUserConfig()
        self.__loadDevelopment()

    def isActive(self, command):
        for fireKey, listKeyInfo in self.__mapping.iteritems():
            if not BigWorld.isKeyDown(fireKey):
                continue
            for keyInfo in listKeyInfo:
                if keyInfo[0] != command:
                    continue
                bContinue = False
                satelliteKeys = keyInfo[1]
                for key in satelliteKeys:
                    if not BigWorld.isKeyDown(key):
                        bContinue = True
                        break

                if bContinue:
                    continue
                return True

        return False

    def isActiveList(self, listCommands, bAndNor=False):
        if bAndNor:
            for command in listCommands:
                if not self.isActive(command):
                    return False

        else:
            for command in listCommands:
                if self.isActive(command):
                    return True

        return bool(bAndNor)

    def isFired(self, command, key):
        listKeyInfo = self.__mapping.get(key)
        if listKeyInfo is None or key == Keys.KEY_NONE:
            return False
        else:
            for keyInfo in listKeyInfo:
                if keyInfo[0] != command:
                    continue
                bContinue = False
                satelliteKeys = keyInfo[1]
                for satelliteKey in satelliteKeys:
                    if not BigWorld.isKeyDown(satelliteKey):
                        bContinue = True
                        break

                if bContinue:
                    continue
                return True

            return False

    def isFiredList(self, listCommands, key, bAndNor=False):
        if bAndNor:
            for command in listCommands:
                if not self.isFired(command, key):
                    return False

        else:
            for command in listCommands:
                if self.isFired(command, key):
                    return True

        return bool(bAndNor)

    def getName(self, command):
        return self.__dictCommand2CommandName[command] if command in self.__dictCommand2CommandName else None

    def getCommand(self, name):
        return globals().get(name)

    def save(self):
        tmpList = []
        for fireKey, listKeyInfo in self.__mapping.iteritems():
            for command, satelliteKeys, isDefault in listKeyInfo:
                if isDefault:
                    continue
                if satelliteKeys:
                    continue
                commandName = self.getName(command)
                listSatelliteKeyNames = []
                for key in satelliteKeys:
                    listSatelliteKeyNames.append('KEY_' + BigWorld.keyToString(key))

                strSatelliteKeyNames = ''
                for keyName in listSatelliteKeyNames:
                    strSatelliteKeyNames += keyName + ' '

                strSatelliteKeyNames = strSatelliteKeyNames.strip()
                fireKeyName = 'KEY_' + BigWorld.keyToString(fireKey)
                tmpList.append((commandName, fireKeyName, strSatelliteKeyNames))

        if tmpList:
            section = Settings.g_instance.userPrefs
            section.deleteSection(CommandMapping.__USER_CONFIG_SECTION_NAME)
            section = section.createSection(CommandMapping.__USER_CONFIG_SECTION_NAME)
            for commandName, fireKeyName, strSatelliteKeynames in tmpList:
                subsec = section.createSection(commandName)
                subsec.writeString('fireKey', fireKeyName)
                subsec.writeString('satelliteKeys', strSatelliteKeyNames)

            Settings.g_instance.save()

    def __checkUserKey(self, key):
        return True

    def __loadFromSection(self, section, bDelOldCmds=True, asDefault=False):
        needsResave = False
        tempList = []
        for commandName in section.keys():
            subsec = section[commandName]
            fireKeyName = subsec.readString('fireKey')
            satelliteKeyNames = []
            if subsec.has_key('satelliteKeys'):
                satelliteKeyNames = subsec.readString('satelliteKeys').split()
            if bDelOldCmds:
                self.remove(commandName)
            if commandName.find('_SHORTCAT_') != -1:
                commandName = commandName.replace('_SHORTCAT_', '_SHORTCUT_')
                needsResave = True
            tempList.append((commandName, fireKeyName, satelliteKeyNames))

        if asDefault is False:
            for commandNameTarget, commandNameSrc in CO_DEPENDENT_KEYS.iteritems():
                if findFirst(lambda a: a[0] == commandNameTarget, tempList, None) is None:
                    src = findFirst(lambda a: a[0] == commandNameSrc, tempList, None)
                    if src is not None:
                        self.remove(commandNameTarget)
                        tempList.append((commandNameTarget, src[1], src[2]))

        for commandName, fireKeyName, satelliteKeyNames in tempList:
            if not self.add(commandName, fireKeyName, satelliteKeyNames, asDefault):
                LOG_DEBUG('<__loadFromSection>: ' + ('default' if asDefault else 'user') + ' command ' + str(commandName) + ' was not loaded')

        if needsResave:
            self.save()
        return

    def getDefaults(self):
        section = ResMgr.openSection(CommandMapping.__DEFAULT_CONFIG_FILE_NAME)
        result = {}
        for commandName in section.keys():
            subsec = section[commandName]
            fireKeyName = subsec.readString('fireKey')
            satelliteKeyNames = []
            if subsec.has_key('satelliteKeys'):
                satelliteKeyNames = subsec.readString('satelliteKeys').split()
            if not satelliteKeyNames:
                result[self.getCommand(commandName)] = int(Keys.__dict__.get(fireKeyName, 0))

        ResMgr.purge(CommandMapping.__DEFAULT_CONFIG_FILE_NAME, True)
        return result

    def __loadDefault(self):
        section = ResMgr.openSection(CommandMapping.__DEFAULT_CONFIG_FILE_NAME)
        self.__loadFromSection(section, bDelOldCmds=True, asDefault=True)
        ResMgr.purge(CommandMapping.__DEFAULT_CONFIG_FILE_NAME, True)

    def __loadUserConfig(self):
        section = Settings.g_instance.userPrefs
        if not section.has_key(CommandMapping.__USER_CONFIG_SECTION_NAME):
            return
        section = section[CommandMapping.__USER_CONFIG_SECTION_NAME]
        self.__loadFromSection(section, bDelOldCmds=True, asDefault=False)

    def __loadDevelopment(self):
        pass
