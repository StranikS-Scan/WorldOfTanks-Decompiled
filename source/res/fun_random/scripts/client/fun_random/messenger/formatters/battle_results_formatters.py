# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/messenger/formatters/battle_results_formatters.py
from adisp import adisp_async, adisp_process
from fun_random.gui.shared.fun_system_factory import collectBattleResultsMessageSubFormatter
from messenger.formatters.service_channel import WaitItemsSyncFormatter, BattleResultsFormatter
from messenger.formatters.service_channel_helpers import MessageData

class FunBattleResultsFormatter(WaitItemsSyncFormatter):

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            battleResults = message.data
            arenaGuiType = battleResults.get('guiType')
            subFormatterCls = collectBattleResultsMessageSubFormatter(arenaGuiType)
            if subFormatterCls is not None:
                messages = yield subFormatterCls().format(message)
                callback(messages)
            else:
                callback([MessageData(None, None)])
        else:
            callback([MessageData(None, None)])
        return


class FunRandomBattleResultsSubFormatter(BattleResultsFormatter):
    pass
