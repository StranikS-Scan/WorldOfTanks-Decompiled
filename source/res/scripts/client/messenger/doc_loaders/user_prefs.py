# Embedded file name: scripts/client/messenger/doc_loaders/user_prefs.py
from messenger.doc_loaders import _xml_helpers
import types
_userProps = {'datetimeIdx': ('readInt', 'writeInt', lambda value: value in xrange(0, 4)),
 'enableOlFilter': ('readBool', 'writeBool', lambda value: type(value) is types.BooleanType),
 'enableSpamFilter': ('readBool', 'writeBool', lambda value: type(value) is types.BooleanType),
 'invitesFromFriendsOnly': ('readBool', 'writeBool', lambda value: type(value) is types.BooleanType),
 'storeReceiverInBattle': ('readBool', 'writeBool', lambda value: type(value) is types.BooleanType),
 'disableBattleChat': ('readBool', 'writeBool', lambda value: type(value) is types.BooleanType),
 'receiveFriendshipRequest': ('readBool', 'writeBool', lambda value: type(value) is types.BooleanType)}

def loadDefault(xmlCtx, section, messengerSettings):
    data = {}
    for tagName, subSec in section.items():
        if tagName != 'preference':
            raise _xml_helpers.XMLError(xmlCtx, 'Tag {0:>s} is invalid'.format(tagName))
        ctx = xmlCtx.next(subSec)
        name = _xml_helpers.readNoEmptyStr(ctx, subSec, 'name', 'Preference name is not defined')
        if name not in _userProps:
            raise _xml_helpers.XMLError(ctx, 'Preference {0:>s} is invalid'.format(name))
        reader, _, validator = _userProps[name]
        value = getattr(subSec, reader)('value')
        if validator(value):
            data[name] = value
        else:
            raise _xml_helpers.XMLError(ctx, 'Invalid value of preference {0:>s}'.format(name))

    if len(data):
        messengerSettings.userPrefs = messengerSettings.userPrefs._replace(**data)


def loadFromServer(messengerSettings):
    from account_helpers.settings_core.SettingsCore import g_settingsCore
    data = messengerSettings.userPrefs._asdict()
    for key, (_, _, _) in _userProps.iteritems():
        settingValue = g_settingsCore.serverSettings.getGameSetting(key, None)
        if settingValue is not None:
            data[key] = settingValue

    version = g_settingsCore.serverSettings.getVersion()
    if version is not None:
        data['version'] = version
    messengerSettings.saveUserPreferences(data)
    return


def flush(messengerSettings, data):
    oldData = messengerSettings.userPrefs._asdict()
    newData = {}
    for key, value in data.iteritems():
        if key in oldData and oldData[key] == value:
            continue
        if key in _userProps:
            newData[key] = value

    if len(newData):
        messengerSettings.userPrefs = messengerSettings.userPrefs._replace(**data)
    return len(newData) > 0
