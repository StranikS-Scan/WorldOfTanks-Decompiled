# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/m_settings.py
from collections import namedtuple, defaultdict
import Event
from debug_utils import LOG_ERROR
from helpers import dependency
from helpers.html.templates import XMLCollection
from messenger import doc_loaders
from messenger.doc_loaders.html_templates import MessageTemplates
from messenger.m_constants import BATTLE_CHANNEL
from skeletons.account_helpers.settings_core import ISettingsCore

def _getAccountRepository():
    import Account
    return Account.g_accountRepository


class _ColorScheme(defaultdict):

    def __init__(self, names, default_factory=None, **kwargs):
        self.__colorsNames = names
        self.__current = names[0]
        super(_ColorScheme, self).__init__(default_factory, **kwargs)

    def __missing__(self, key):
        self[key] = value = dict(((k, 0) for k in self.__colorsNames))
        return value

    def getColorsNames(self):
        return self.__colorsNames

    def getDefColorName(self):
        return self.__colorsNames[0]

    def getColor(self, key):
        return self[key][self.__current]

    def getColors(self, key):
        return map(lambda name: self[key][name], self.__colorsNames)

    def setCurrent(self, name):
        result = False
        if name in self.__colorsNames and self.__current != name:
            self.__current = name
            result = True
        return result

    def getHexStr(self, key):
        return '{0:06X}'.format(self[key][self.__current])

    def iterColors(self):
        for key, colors in self.iteritems():
            yield (key, colors[self.__current])

    def iterHexs(self):
        for key, colors in self.iteritems():
            yield (key, '{0:06X}'.format(colors[self.__current]))


_ServiceChannelSettings = namedtuple('_ServiceChannelSettings', ('highPriorityMsgLifeTime', 'highPriorityMsgAlphaSpeed', 'mediumPriorityMsgLifeTime', 'mediumPriorityMsgAlphaSpeed', 'stackLength', 'padding'))

class _LobbySettings(object):
    __slots__ = ('serviceChannel', 'messageRawFormat', 'badWordFormat', '__messageFormats')

    def __init__(self):
        super(_LobbySettings, self).__init__()
        self.serviceChannel = _ServiceChannelSettings(5.0, 0, 5, 0, 5, 0)
        self.messageRawFormat = u'{0:>s} {1:>s} {2:>s}'
        self.badWordFormat = u'{0:>s}'
        self.__messageFormats = {}

    def getMessageFormat(self, key):
        try:
            return self.__messageFormats[key]
        except KeyError:
            LOG_ERROR('Message formatter not found', key)
            return self.messageRawFormat

    def onSettingsLoaded(self, root):
        for key in ('groups', 'rosters'):
            colorScheme = root.getColorScheme(key)
            for name, userColor in colorScheme.iterHexs():
                if name == 'breaker':
                    timeColor = colorScheme.getHexStr('other')
                else:
                    timeColor = userColor
                self.__messageFormats[name] = self.messageRawFormat % {'user': userColor,
                 'time': timeColor}


_BattleMessageLifeCycle = namedtuple('_MessageInBattle', ('lifeTime', 'alphaSpeed'))

class _BattleSettings(object):
    __slots__ = ('messageLifeCycle', 'messageFormat', 'targetFormat', 'inactiveStateAlpha', 'hintText', 'toolTipText', 'numberOfMessagesInHistory', 'receivers', 'alphaForLastMessages', 'chatIsLockedToolTipText', 'recoveredLatestMessages', 'lifeTimeRecoveredMessages', 'lastReceiver', 'toolTipTextWithMuteInfo')

    def __init__(self):
        super(_BattleSettings, self).__init__()
        self.messageLifeCycle = _BattleMessageLifeCycle(5, 0)
        self.messageFormat = u'%(playerName)s : %(messageText)s'
        self.targetFormat = '%(target)s'
        self.inactiveStateAlpha = 100
        self.hintText = ''
        self.toolTipText = ''
        self.chatIsLockedToolTipText = ''
        self.toolTipTextWithMuteInfo = ''
        self.numberOfMessagesInHistory = 6
        self.receivers = {}
        self.alphaForLastMessages = 20
        self.recoveredLatestMessages = 5
        self.lifeTimeRecoveredMessages = 1
        self.lastReceiver = BATTLE_CHANNEL.TEAM.name


_UserPrefs = namedtuple('_UserPrefs', ('version', 'datetimeIdx', 'enableOlFilter', 'enableSpamFilter', 'invitesFromFriendsOnly', 'storeReceiverInBattle', 'disableBattleChat', 'chatContactsListOnly', 'receiveFriendshipRequest', 'receiveInvitesInBattle'))

def _makeDefUserPrefs():
    return _UserPrefs(version=1, datetimeIdx=2, enableOlFilter=True, enableSpamFilter=False, invitesFromFriendsOnly=False, storeReceiverInBattle=False, disableBattleChat=False, chatContactsListOnly=False, receiveFriendshipRequest=True, receiveInvitesInBattle=True)


class MessengerSettings(object):
    __slots__ = ('__colorsSchemes', '__messageFormatters', '__eManager', '__isUserPrefsInited', 'lobby', 'battle', 'userPrefs', 'htmlTemplates', 'msgTemplates', 'server', 'onUserPreferencesUpdated', 'onColorsSchemesUpdated')
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__colorsSchemes = {}
        self.lobby = _LobbySettings()
        self.battle = _BattleSettings()
        self.userPrefs = _makeDefUserPrefs()
        self.__isUserPrefsInited = False
        self.htmlTemplates = XMLCollection('', '')
        self.msgTemplates = MessageTemplates('', '')
        self.__messageFormatters = {}
        self.server = None
        self.__eManager = Event.EventManager()
        self.onUserPreferencesUpdated = Event.Event(self.__eManager)
        self.onColorsSchemesUpdated = Event.Event(self.__eManager)
        return

    def init(self):
        self.__colorsSchemes.update({'groups': _ColorScheme(['default']),
         'rosters': _ColorScheme(['online', 'offline']),
         'contacts': _ColorScheme(['online', 'offline']),
         'battle/player': _ColorScheme(['default', 'colorBlind']),
         'battle/message': _ColorScheme(['default', 'colorBlind']),
         'battle/receiver': _ColorScheme(['default', 'colorBlind'])})
        from messenger.proto import ServerSettings
        self.server = ServerSettings()
        doc_loaders.load(self)
        self.lobby.onSettingsLoaded(self)
        self.settingsCore.onSettingsChanged += self.__accs_onSettingsChanged

    def fini(self):
        self.settingsCore.onSettingsChanged -= self.__accs_onSettingsChanged
        self.__eManager.clear()
        self.__colorsSchemes.clear()
        self.__messageFormatters.clear()

    def update(self):
        repository = _getAccountRepository()
        if repository:
            settings = repository.serverSettings
        else:
            settings = {}
        self.server.update(settings)
        if self.settingsCore.getSetting('isColorBlind'):
            csName = 'colorBlind'
        else:
            csName = 'default'
        for colorScheme in self.__colorsSchemes.itervalues():
            colorScheme.setCurrent(csName)

    def getColorScheme(self, key):
        try:
            return self.__colorsSchemes[key]
        except KeyError:
            LOG_ERROR('Color scheme not found', key)
            return None

        return None

    def resetUserPreferences(self):
        self.userPrefs = _makeDefUserPrefs()
        self.__isUserPrefsInited = False

    def saveUserPreferences(self, data):
        if doc_loaders.user_prefs.flush(self, data) or not self.__isUserPrefsInited:
            self.__isUserPrefsInited = True
            self.onUserPreferencesUpdated()

    def resetBattleReceiverIfNeed(self):
        if not self.userPrefs.storeReceiverInBattle:
            self.battle.lastReceiver = BATTLE_CHANNEL.TEAM.name

    def __accs_onSettingsChanged(self, diff):
        if 'isColorBlind' in diff:
            result = False
            for colorScheme in self.__colorsSchemes.itervalues():
                csName = 'colorBlind' if diff['isColorBlind'] else 'default'
                if colorScheme.setCurrent(csName):
                    result = True

            if result:
                self.onColorsSchemesUpdated()
