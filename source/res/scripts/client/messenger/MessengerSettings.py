# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/MessengerSettings.py
# Compiled at: 2011-11-22 21:14:19
from chat_shared import CHAT_MEMBER_GROUP, USERS_ROSTER_FRIEND, USERS_ROSTER_IGNORED
from debug_utils import LOG_CURRENT_EXCEPTION
import Event
from helpers import i18n
from messenger import BATTLE_DEFAULT_MESSAGE_LIFE_TIME, DEFAULT_MESSAGE_DATETIME_FORMAT_INDEX, LOBBY_MESSAGE_FORMAT, SCH_DEFAULT_POP_UP_MSG_LIFE_TIME, SCH_DEFAULT_POP_UP_MSG_STACK_LENGTH
import Math
import ResMgr
import Settings

class MessengerSettings(object):
    __lobbyMFormats = {}
    __lobbyUserColorScheme = {'himself': (False, True, {'offline': None,
                  'online': ''}),
     'user': (True, True, {'offline': '',
               'online': ''}),
     'friend': (True, True, {'offline': '',
                 'online': ''}),
     'ignored': (True, False, {'offline': '',
                  'online': None})}
    __userRosterKayPairs = {USERS_ROSTER_FRIEND: 'friend',
     USERS_ROSTER_IGNORED: 'ignored'}
    __user = {'datetimeIdx': DEFAULT_MESSAGE_DATETIME_FORMAT_INDEX,
     'showJoinLeaveMessages': False,
     'enableOlFilter': True,
     'enableSpamFilter': False,
     'enableStoreMws': True,
     'enableStoreCws': True,
     'windowsPersistens': {'management': {},
                           'channels': {}},
     'invitesFromFriendsOnly': False}
    __lobby = {'popUpMessageLifeTime': SCH_DEFAULT_POP_UP_MSG_LIFE_TIME,
     'popUpMessageAlphaSpeed': 0,
     'popUpMessageStackLength': SCH_DEFAULT_POP_UP_MSG_STACK_LENGTH,
     'inviteLinkFormat': '%(id)d %(message)s',
     'inviteNoteFormat': '%(note)s',
     'forseDestroyPrebattleChannel': False}
    __battle = {'messageLifeTime': BATTLE_DEFAULT_MESSAGE_LIFE_TIME,
     'messageAlphaSpeed': 0,
     'inactiveStateAlpha': 100}
    __battleMsgColorScheme = {'team': Math.Vector3(0, 255, 0),
     'common': Math.Vector3(255, 255, 255),
     'unknown': Math.Vector3(42, 42, 42)}
    __battlePlayerColorScheme = {'himself': {'default': Math.Vector3(255, 255, 0)},
     'teammate': {'default': Math.Vector3(0, 255, 0)},
     'enemy': {'default': Math.Vector3(255, 0, 0)},
     'unknown': {'default': Math.Vector3(42, 42, 42)},
     'teamkiller': {'default': Math.Vector3(0, 235, 0)},
     'squadman': {'default': Math.Vector3(255, 235, 0)}}
    __debug = {'dumpWaitingToDestroyChannels': False}
    __protocols = {}
    coloringForBadWordFormat = '<font color="#00FFFF">%s</font>'
    __htmlTemplates = {}

    def __init__(self, resourceId):
        self.__resourceId = resourceId
        self.onApplyUserPreferences = Event.Event()

    def getColorSchemeTag(self, roster):
        tag = 'user'
        if bool(roster & USERS_ROSTER_FRIEND):
            tag = self.__userRosterKayPairs[USERS_ROSTER_FRIEND]
        elif bool(roster & USERS_ROSTER_IGNORED):
            tag = self.__userRosterKayPairs[USERS_ROSTER_IGNORED]
        return tag

    @property
    def lobbySettings(self):
        return self.__lobby.copy()

    @property
    def battleSettings(self):
        return self.__battle.copy()

    @property
    def debugSettings(self):
        return self.__debug.copy()

    @property
    def userPreferences(self):
        return self.__user.copy()

    @property
    def supportedProtocols(self):
        return self.__protocols.copy()

    def getLobbyMsgFormat(self, message, user):
        if user.himself:
            key = 'himself'
        elif user.breaker:
            key = 'breaker'
        else:
            groupIdx = message.group
            if CHAT_MEMBER_GROUP.member.index() == groupIdx:
                key = self.getColorSchemeTag(user.roster)
            else:
                key = CHAT_MEMBER_GROUP[groupIdx].name()
        return self.__lobbyMFormats.get(key, LOBBY_MESSAGE_FORMAT)

    def getLobbyUserCS(self, roster, himself=False):
        key = 'himself' if himself else self.getColorSchemeTag(roster)
        scheme = self.__lobbyUserColorScheme[key][2]
        return [scheme['offline'], scheme['online']]

    def getBattlePlayerHexCS(self, isColorBlind=False):
        colorSchemes = {}
        groupKey = 'default'
        if isColorBlind:
            groupKey = 'colorBlind'
        for key, colors in self.__battlePlayerColorScheme.iteritems():
            colorSchemes[key] = '%02X%02X%02X' % colors.get(groupKey if groupKey in colors else 'default').tuple()

        return colorSchemes

    def getBattleMsgHexCS(self):
        colorSchemes = {}
        for key, vector3 in self.__battleMsgColorScheme.iteritems():
            colorSchemes[key] = '%02X%02X%02X' % vector3.tuple()

        return colorSchemes

    def getHtmlTemplate(self, key):
        return self.__htmlTemplates.get(key, key)

    def read(self):
        self.readUserPreference()
        self.readXML()

    def readUserPreference(self):
        userPrefs = Settings.g_instance.userPrefs
        if not userPrefs.has_key(Settings.KEY_MESSENGER_PREFERENCES):
            userPrefs.write(Settings.KEY_MESSENGER_PREFERENCES, '')
            self.saveUserPreferences()
        else:
            ds = userPrefs[Settings.KEY_MESSENGER_PREFERENCES]
            self.__user['datetimeIdx'] = ds.readInt('datetimeIdx', self.__user['datetimeIdx'])
            self.__user['showJoinLeaveMessages'] = ds.readBool('showJoinLeaveMessages', self.__user['showJoinLeaveMessages'])
            self.__user['enableOlFilter'] = ds.readBool('enableOlFilter', self.__user['enableOlFilter'])
            self.__user['enableSpamFilter'] = ds.readBool('enableSpamFilter', self.__user['enableSpamFilter'])
            self.__user['invitesFromFriendsOnly'] = ds.readBool('invitesFromFriendsOnly', self.__user['invitesFromFriendsOnly'])
            self.__user['enableStoreMws'] = ds.readBool('enableStoreMws', self.__user['enableStoreMws'])
            self.__user['enableStoreCws'] = ds.readBool('enableStoreCws', self.__user['enableStoreCws'])
            wSection = ds['windows'] if ds.has_key('windows') else {}
            mSection = wSection['management'] if wSection.has_key('management') else {}
            for windowName, pSection in mSection.items():
                windowName = pSection.readString('name', str()) if pSection.has_key('name') else None
                persistent = pSection.readVector4('persistent', (-1, -1, -1, -1)) if pSection.has_key('persistent') else None
                if len(windowName) > 0 and persistent != Math.Vector4(-1, -1, -1, -1):
                    self.__user['windowsPersistens']['management'][windowName] = persistent

        chSection = wSection['channels'] if wSection.has_key('channels') else {}
        for _, pSection in chSection.items():
            channelId = pSection.readInt64('cid', 0L) if pSection.has_key('cid') else None
            persistent = pSection.readVector4('persistent', (-1, -1, -1, -1)) if pSection.has_key('persistent') else None
            if channelId != 0L and persistent != Math.Vector4(-1, -1, -1, -1):
                self.__user['windowsPersistens']['channels'][channelId] = persistent

        return

    def __readProtocolsXmlSettings(self, protocols):
        for name, section in protocols.items():
            self.__protocols[name] = section.asString

    def __readLobbyXmlSettings(self, lobby):
        colorScheme = lobby['colorScheme']
        if colorScheme:
            messageBodyColor = '%02X%02X%02X' % colorScheme.readVector3('messageBody', Math.Vector3(0, 0, 0)).tuple()
            self.__lobbyMFormats = {}
            gSection = colorScheme['group'] if colorScheme.has_key('group') else {}
            for group, cSection in gSection.items():
                userNameColor = '%02X%02X%02X' % cSection.asVector3.tuple()
                self.__lobbyMFormats[group] = '<font color="#%s">' % userNameColor + '%s</font>&nbsp;' + '<font color="#%s">' % userNameColor + '%s</font>&nbsp;' + '<font color="#%s">' % messageBodyColor + '%s</font>'

            urSection = colorScheme['userRoster'] if colorScheme.has_key('userRoster') else {}
            for userType, (showOffline, showOnline, _) in self.__lobbyUserColorScheme.iteritems():
                uSection = urSection[userType] if urSection.has_key(userType) else {}
                if showOnline:
                    onlineColor = uSection['online'].asVector3.tuple() if uSection.has_key('online') else (0, 0, 0)
                    self.__lobbyUserColorScheme[userType][2]['online'] = (int(onlineColor[0]) << 16) + (int(onlineColor[1]) << 8) + (int(onlineColor[2]) << 0)
                    onlineColor = '%02X%02X%02X' % onlineColor
                    self.__lobbyMFormats[userType] = '<font color="#%s">' % onlineColor + '%s</font>&nbsp;' + '<font color="#%s">' % onlineColor + '%s</font>&nbsp;' + '<font color="#%s">' % messageBodyColor + '%s</font>'
                if showOffline:
                    offlineColor = uSection['offline'].asVector3.tuple() if uSection.has_key('offline') else (0, 0, 0)
                    self.__lobbyUserColorScheme[userType][2]['offline'] = (int(offlineColor[0]) << 16) + (int(offlineColor[1]) << 8) + (int(offlineColor[2]) << 0)

            badWordColor = '%02X%02X%02X' % colorScheme.readVector3('badWord', Math.Vector3(0, 0, 0)).tuple()
            self.coloringForBadWordFormat = '<font color="#' + badWordColor + '">%s</font>'
            breakerColor = '%02X%02X%02X' % colorScheme.readVector3('breaker', Math.Vector3(0, 0, 0)).tuple()
            self.__lobbyMFormats['breaker'] = '<font color="#%s">' % breakerColor + '%s</font>&nbsp;' + '<font color="#%s">' % messageBodyColor + '%s</font>&nbsp;' + '<font color="#%s">' % messageBodyColor + '%s</font>'
        serviceChannel = lobby['serviceChannel']
        if serviceChannel:
            self.__lobby['popUpMessageLifeTime'] = serviceChannel.readFloat('lifeTime', SCH_DEFAULT_POP_UP_MSG_LIFE_TIME)
            self.__lobby['popUpMessageAlphaSpeed'] = serviceChannel.readFloat('alphaSpeed', 0.0)
            self.__lobby['popUpMessageStackLength'] = serviceChannel.readInt('stackLength', SCH_DEFAULT_POP_UP_MSG_STACK_LENGTH)
        invites = lobby['invites']
        if invites:
            self.__lobby['inviteLinkFormat'] = invites.readString('linkFormat', '%(id)d %(message)s')
            self.__lobby['inviteNoteFormat'] = invites.readString('noteFormat', '%(note)s')
        prebattle = lobby['prebattle']
        if prebattle:
            self.__lobby['forseDestroyPrebattleChannel'] = prebattle.readBool('forseDestroyChannel')

    def __readBattlePlayerCSItem(self, csSection):
        result = {'default': Math.Vector3(0, 0, 0)}
        items = csSection.items()
        if len(items):
            result.update(dict(((key, section.asVector3) for key, section in items)))
        else:
            result = {'default': csSection.asVector3}
        return result

    def __readBattleXmlSettings(self, battle):
        self.__battle['messageLifeTime'] = battle.readFloat('lifeTime')
        self.__battle['messageAlphaSpeed'] = battle.readFloat('alphaSpeed')
        self.__battle['inactiveStateAlpha'] = battle.readInt('inactiveStateAlpha', 100)
        colorScheme = battle['colorScheme']
        if colorScheme:
            pColorSection = colorScheme['player']
            if pColorSection is not None:
                for key in self.__battlePlayerColorScheme.keys():
                    csSection = pColorSection[key]
                    if csSection is not None:
                        self.__battlePlayerColorScheme[key] = self.__readBattlePlayerCSItem(csSection)

            msgColorSection = colorScheme['messageBody']
            if msgColorSection:
                for key in self.__battleMsgColorScheme.keys():
                    vector3 = msgColorSection.readVector3(key, (-1, -1, -1))
                    if vector3 != Math.Vector3(-1, -1, -1):
                        self.__battleMsgColorScheme[key] = vector3

        return

    def __readDebugXmlSettings(self, debug):
        self.__debug['dumpWaitingToDestroyChannels'] = debug.readBool('dumpWaitingToDestroyChannels')

    def __readHtmlTemplates(self, htmlSec):
        import re
        srePattern = re.compile('\\_\\(([^)]+)\\)', re.U | re.M)

        def makeString(mutchobj):
            if mutchobj.group(1):
                return i18n.makeString(mutchobj.group(1))

        for key, tSec in htmlSec.items():
            try:
                self.__htmlTemplates[key] = srePattern.sub(makeString, tSec.asString)
            except re.error:
                LOG_CURRENT_EXCEPTION()

    def readXML(self):
        section = ResMgr.openSection(self.__resourceId)
        if section is None:
            return
        else:
            protocols = section['protocols']
            if protocols:
                self.__readProtocolsXmlSettings(protocols)
            lobby = section['lobby']
            if lobby:
                self.__readLobbyXmlSettings(lobby)
            battle = section['battle']
            if battle:
                self.__readBattleXmlSettings(battle)
            debug = section['debug']
            if debug:
                self.__readDebugXmlSettings(debug)
            htmlSec = section['htmlTemplates']
            if htmlSec:
                self.__readHtmlTemplates(htmlSec)
            return

    def saveUserPreferences(self):
        ds = Settings.g_instance.userPrefs[Settings.KEY_MESSENGER_PREFERENCES]
        ds.writeInt('datetimeIdx', self.__user['datetimeIdx'])
        ds.writeBool('showJoinLeaveMessages', self.__user['showJoinLeaveMessages'])
        ds.writeBool('enableOlFilter', self.__user['enableOlFilter'])
        ds.writeBool('enableSpamFilter', self.__user['enableSpamFilter'])
        ds.writeBool('enableStoreMws', self.__user['enableStoreMws'])
        ds.writeBool('enableStoreCws', self.__user['enableStoreCws'])
        ds.writeBool('invitesFromFriendsOnly', self.__user['invitesFromFriendsOnly'])
        if not self.__user['enableStoreMws']:
            self.__user['windowsPersistens']['management'] = {}
        if not self.__user['enableStoreCws']:
            self.__user['windowsPersistens']['channels'] = {}

    def saveWindowPersistens(self):
        ds = Settings.g_instance.userPrefs[Settings.KEY_MESSENGER_PREFERENCES]
        ds.deleteSection('windows')
        wSection = ds.createSection('windows')
        mSection = wSection.createSection('management')
        management = self.__user['windowsPersistens']['management']
        for windowName, persistent in management.iteritems():
            section = mSection.createSection('window')
            section.writeString('name', windowName)
            section.writeVector4('persistent', persistent)

        chSection = wSection.createSection('channels')
        channels = self.__user['windowsPersistens']['channels']
        for channelId, persistent in channels.iteritems():
            section = chSection.createSection('channel')
            section.writeInt64('cid', channelId)
            section.writeVector4('persistent', persistent)

        Settings.g_instance.save()

    def applyWindowPersistens(self, management, channels):
        if self.__user['enableStoreMws']:
            self.__user['windowsPersistens']['management'] = management
        if self.__user['enableStoreCws']:
            self.__user['windowsPersistens']['channels'] = channels
        self.saveWindowPersistens()

    def applyUserPreferences(self, **kwargs):
        self.__user.update(kwargs)
        self.saveUserPreferences()
        self.onApplyUserPreferences()
