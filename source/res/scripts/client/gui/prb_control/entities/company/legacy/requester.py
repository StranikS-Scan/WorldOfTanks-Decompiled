# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/company/legacy/requester.py
import BigWorld
from PlayerEvents import g_playerEvents
from constants import PREBATTLE_TYPE, PREBATTLE_CACHE_KEY
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.prb_control.entities.base.cooldown import PrbCooldownManager
from gui.prb_control.entities.base.requester import IPrbListRequester
from gui.prb_control.items import prb_seqs
from gui.prb_control.settings import REQUEST_TYPE

class CompanyListRequester(IPrbListRequester):
    """
    Companies list request class
    """

    def __init__(self):
        self.__callback = None
        self.__ctx = None
        self.__cooldown = PrbCooldownManager()
        return

    def start(self, callback):
        if callback is not None and callable(callback):
            self.__callback = callback
        else:
            LOG_ERROR('Callback is None or is not callable')
            return
        g_playerEvents.onPrebattlesListReceived += self.__pe_onPrebattlesListReceived
        return

    def stop(self):
        g_playerEvents.onPrebattlesListReceived -= self.__pe_onPrebattlesListReceived
        self.__callback = None
        if self.__ctx:
            self.__ctx.stopProcessing(False)
            self.__ctx = None
        return

    def request(self, ctx=None):
        if self.__cooldown.validate(REQUEST_TYPE.PREBATTLES_LIST):
            if ctx:
                ctx.stopProcessing(False)
            return
        LOG_DEBUG('Request prebattle', ctx)
        self.__cooldown.process(REQUEST_TYPE.PREBATTLES_LIST)
        self.__ctx = ctx
        if ctx.byDivision():
            BigWorld.player().requestPrebattlesByDivision(ctx.isNotInBattle, ctx.division)
        elif ctx.byName():
            BigWorld.player().requestPrebattlesByName(PREBATTLE_TYPE.COMPANY, ctx.isNotInBattle, ctx.creatorMask)
        else:
            BigWorld.player().requestPrebattles(PREBATTLE_TYPE.COMPANY, PREBATTLE_CACHE_KEY.CREATE_TIME, ctx.isNotInBattle, -50, 0)

    def isInCooldown(self):
        """
        Is this request in cooldown now
        """
        return self.__cooldown.isInProcess(REQUEST_TYPE.PREBATTLES_LIST)

    def getCooldown(self):
        """
        Get cooldown time for companies list request
        """
        return self.__cooldown.getTime(REQUEST_TYPE.PREBATTLES_LIST)

    def fireCooldownEvent(self):
        """
        Fires cooldown event to notify about operation
        """
        self.__cooldown.fireEvent(REQUEST_TYPE.PREBATTLES_LIST, self.__cooldown.getTime(REQUEST_TYPE.PREBATTLES_LIST))

    def __pe_onPrebattlesListReceived(self, prbType, count, prebattles):
        """
        Listener for event of companies list receive
        Args:
            prbType: items prebattle type
            count: items count
            prebattles: items, which are list of (sort key, prebattle ID, prebattle cache data like
                PREBATTLE_CACHE_KEY -> data
        """
        if prbType != PREBATTLE_TYPE.COMPANY:
            return
        else:
            if self.__ctx:
                self.__ctx.stopProcessing(True)
                self.__ctx = None
            self.__callback(prb_seqs.PrbListIterator(reversed(prebattles)))
            return
