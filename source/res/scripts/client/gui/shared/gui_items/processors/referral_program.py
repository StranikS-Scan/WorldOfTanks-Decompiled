# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/referral_program.py
import BigWorld
import logging
from constants import RP_PGB_POINT
from gui.Scaleform.daapi.view.lobby.referral_program.referral_program_helpers import isReferralProgramEnabled
from gui.shared.gui_items.processors import Processor, plugins, makeI18nError
from gui.shared.gui_items.processors.plugins import SyncValidator
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class CollectRPPgbPointsValidator(SyncValidator):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def _validate(self):
        return plugins.makeSuccess() if self.__isValid() else plugins.makeError()

    def __isValid(self):
        pgbPoints = self.__itemsCache.items.stats.entitlements.get(RP_PGB_POINT, 0)
        pgbDayLimit = self.__itemsCache.items.refProgram.getRPPgbPoints()
        pgbCapacity = self.__lobbyContext.getServerSettings().getRPConfig().pgbCapacity
        isPositiveCount = False if min(pgbPoints, pgbDayLimit, pgbCapacity) == 0 else True
        return isReferralProgramEnabled(lobbyContext=self.__lobbyContext) and isPositiveCount


class CollectRPPgbPointsProcessor(Processor):

    def __init__(self):
        super(CollectRPPgbPointsProcessor, self).__init__()
        self.addPlugin(CollectRPPgbPointsValidator())

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='referralProgram_collectRPPgbPoints/server_error')

    def _request(self, callback):
        _logger.debug('Make server request to collect rp pgb points.')
        BigWorld.player().referralProgram.collectRPPgbPoints(lambda resID, code, errStr: self._response(code, callback, errStr))
