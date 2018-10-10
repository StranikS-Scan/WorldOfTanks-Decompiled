# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/battle_session/legacy/requester.py
from PlayerEvents import g_playerEvents
from debug_utils import LOG_ERROR
from gui.prb_control import prb_getters
from gui.prb_control.entities.base.requester import IPrbListRequester
from gui.prb_control.items import prb_seqs

class AutoInvitesRequester(IPrbListRequester):

    def __init__(self):
        self.__callback = None
        return

    def start(self, callback):
        if callback is not None and callable(callback):
            self.__callback = callback
        else:
            LOG_ERROR('Callback is None or is not callable')
            return
        g_playerEvents.onPrebattleAutoInvitesChanged += self.__pe_onPrbAutoInvitesChanged
        return

    def stop(self):
        g_playerEvents.onPrebattleAutoInvitesChanged -= self.__pe_onPrbAutoInvitesChanged
        self.__callback = None
        return

    def request(self, ctx=None):
        self.__fetchList()

    def getItem(self, prbID):
        return prb_seqs.AutoInviteItem(prbID, **prb_getters.getPrebattleAutoInvites().get(prbID, {}))

    def __pe_onPrbAutoInvitesChanged(self):
        self.__fetchList()

    def __fetchList(self):
        if self.__callback is not None:
            self.__callback(prb_seqs.AutoInvitesIterator())
        return
