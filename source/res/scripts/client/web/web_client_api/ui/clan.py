# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/clan.py
from web.web_client_api import w2c, W2CSchema, Field
from gui.shared.event_dispatcher import showClanProfileWindow, showClanInvitesWindow, showClanSearchWindow, showClanPersonalInvitesWindow

class _OpenClanCardSchema(W2CSchema):
    clan_dbid = Field(required=True, type=(int, long))
    clan_abbrev = Field(required=True, type=basestring)


class ClanWindowWebApiMixin(object):

    @w2c(_OpenClanCardSchema, 'clan_card_window')
    def clanCardWindow(self, cmd):
        showClanProfileWindow(cmd.clan_dbid, cmd.clan_abbrev)

    @w2c(W2CSchema, 'clan_invites_window')
    def handleOpenClanInvites(self, cmd):
        showClanInvitesWindow()

    @w2c(W2CSchema, 'clan_search_window')
    def handleOpenClanSearch(self, cmd):
        showClanSearchWindow()

    @w2c(W2CSchema, 'clan_personal_invites_window')
    def handleOpenPersonalInvites(self, cmd):
        showClanPersonalInvitesWindow()
