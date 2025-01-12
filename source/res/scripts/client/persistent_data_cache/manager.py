# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/persistent_data_cache/manager.py
import BigWorld
import wg_async
from helpers import ExitCode
from persistent_data_cache_common.manager import ForceCreatingPDCManager

class ClientForceCreatingPDCManager(ForceCreatingPDCManager):
    __slots__ = ()

    @wg_async.wg_async
    def _start(self):
        super(ClientForceCreatingPDCManager, self)._start()
        saved = yield wg_async.wg_await(self.save())
        if not saved:
            self._logger.error("Couldn't create cache!")
        BigWorld.quitWithExitCode(ExitCode.SUCCESS if saved else ExitCode.FAILED)
