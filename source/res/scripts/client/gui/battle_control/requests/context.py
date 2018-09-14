# Embedded file name: scripts/client/gui/battle_control/requests/context.py
from constants import REQUEST_COOLDOWN
from external_strings_utils import truncate_utf8
from gui.prb_control import settings as prb_settings
from gui.battle_control.requests.settings import AVATAR_REQUEST_TYPE
from gui.shared.utils.decorators import ReprInjector
from gui.shared.utils.requesters import RequestCtx

@ReprInjector.withParent(('getDatabaseIDs', 'ids'), ('getComment', 'comment'))

class SendInvitesCtx(RequestCtx):

    def __init__(self, databaseIDs, comment = '', waitingID = ''):
        super(SendInvitesCtx, self).__init__(waitingID=waitingID)
        self.__databaseIDs = databaseIDs[:300]
        if comment:
            self.__comment = truncate_utf8(comment, prb_settings.INVITE_COMMENT_MAX_LENGTH)
        else:
            self.__comment = ''

    def __repr__(self):
        return 'SendInvitesCtx(databaseIDs = {0!r:s}, comment = {1:>s})'.format(self.__databaseIDs, self.__comment)

    def getDatabaseIDs(self):
        return self.__databaseIDs[:]

    def getComment(self):
        return self.__comment

    def getRequestType(self):
        return AVATAR_REQUEST_TYPE.SEND_INVITES

    def getCooldown(self):
        return REQUEST_COOLDOWN.SEND_INVITATION_COOLDOWN
