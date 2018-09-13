# Embedded file name: scripts/client/messenger/formatters/users_messages.py
from gui import GUI_SETTINGS
from helpers import i18n
from messenger.m_constants import USER_ROSTER_ACTION, MESSENGER_I18N_FILE
_userTransferUserMsgKeys = {USER_ROSTER_ACTION.AddToFriend: '#%s:client/information/addToFriends/message' % MESSENGER_I18N_FILE,
 USER_ROSTER_ACTION.AddToIgnored: '#%s:client/information/addToIgnored/message' % MESSENGER_I18N_FILE,
 USER_ROSTER_ACTION.SetMuted: '#%s:client/information/setMuted/message' % MESSENGER_I18N_FILE,
 USER_ROSTER_ACTION.UnsetMuted: '#%s:client/information/unsetMuted/message' % MESSENGER_I18N_FILE,
 USER_ROSTER_ACTION.RemoveFromFriend: '#%s:client/information/removeFromFriends/message' % MESSENGER_I18N_FILE,
 USER_ROSTER_ACTION.RemoveFromIgnored: '#%s:client/information/removeFromIgnored/message' % MESSENGER_I18N_FILE}

def getUserRosterChangedMessage(actionIndex, user):
    if not GUI_SETTINGS.voiceChat and actionIndex in [USER_ROSTER_ACTION.SetMuted, USER_ROSTER_ACTION.UnsetMuted]:
        return
    else:
        if actionIndex in _userTransferUserMsgKeys:
            message = i18n.makeString(_userTransferUserMsgKeys[actionIndex], user.getName())
        else:
            message = None
        return message


def getBroadcastIsInCoolDownMessage(coolDown):
    return i18n.makeString('#%s:client/error/broadcastInCooldown' % MESSENGER_I18N_FILE, coolDown)
