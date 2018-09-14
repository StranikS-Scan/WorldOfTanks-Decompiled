# Embedded file name: scripts/client/messenger/gui/Scaleform/__init__.py
MESSENGER_BATTLE_SWF_FILE = 'battle_messenger.swf'
import enumerations
BTMS_COMMANDS = enumerations.Enumeration('Battle messenger commands', [('ChannelsInit', lambda : 'Messenger.Battle.ChannelsInit'),
 ('CheckCooldownPeriod', lambda : 'Messenger.Battle.CheckCooldownPeriod'),
 ('SendMessage', lambda : 'Messenger.Battle.SendMessage'),
 ('ReceiveMessage', lambda : 'Messenger.Battle.RecieveMessage'),
 ('ClearMessages', lambda : 'Messenger.Battle.ClearMessages'),
 ('PopulateUI', lambda : 'Messenger.Battle.PopulateUI'),
 ('RefreshUI', lambda : 'Messenger.Battle.RefreshUI'),
 ('ChangeFocus', lambda : 'Messenger.Battle.ChangeFocus'),
 ('JoinToChannel', lambda : 'Messenger.Battle.JoinToChannel'),
 ('ShowActionFailureMessage', lambda : 'Messenger.Battle.ShowActionFailureMesssage'),
 ('UpdateReceivers', lambda : 'Messenger.Battle.UpdateReceivers'),
 ('UserPreferencesUpdated', lambda : 'Messenger.Battle.UserPreferencesUpdated'),
 ('ReceiverChanged', lambda : 'Messenger.Battle.ReceiverChanged'),
 ('AddToFriends', lambda : 'Battle.UsersRoster.AddToFriends'),
 ('RemoveFromFriends', lambda : 'Battle.UsersRoster.RemoveFromFriends'),
 ('AddToIgnored', lambda : 'Battle.UsersRoster.AddToIgnored'),
 ('RemoveFromIgnored', lambda : 'Battle.UsersRoster.RemoveFromIgnored'),
 ('AddMuted', lambda : 'Battle.UsersRoster.AddMuted'),
 ('RemoveMuted', lambda : 'Battle.UsersRoster.RemoveMuted'),
 ('isHistoryEnabled', lambda : 'Messenger.Battle.isHistoryEnabled'),
 ('upHistory', lambda : 'Messenger.Battle.upHistory'),
 ('downHistory', lambda : 'Messenger.Battle.downHistory'),
 ('EnabledHistoryControls', lambda : 'Messenger.Battle.EnabledHistoryControls'),
 ('GetLatestHistory', lambda : 'Messenger.Battle.GetLatestHistory'),
 ('ShowHistoryMessages', lambda : 'Messenger.Battle.ShowHistoryMessages'),
 ('GetLastMessages', lambda : 'Messenger.Battle.GetLastMessages'),
 ('ShowLatestMessages', lambda : 'Messenger.Battle.ShowLatestMessages')], instance=enumerations.CallabbleEnumItem)

class FILL_COLORS(object):
    BLACK = 'black'
    BROWN = 'brown'
    GREEN = 'green'
    RED = 'red'
