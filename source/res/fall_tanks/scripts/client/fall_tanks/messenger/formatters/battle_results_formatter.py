# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/messenger/formatters/battle_results_formatter.py
from helpers.time_utils import ONE_MINUTE
from messenger.formatters.service_channel import BattleResultsFormatter

def formatTimeWithMs(allSeconds, prec=100):
    minutes, seconds = divmod(round(prec * allSeconds), prec * ONE_MINUTE)
    seconds, ms = divmod(seconds, prec)
    return '%02d:%02d.%02d' % (minutes, seconds, ms)


class FallTanksBattleResultsSubFormatter(BattleResultsFormatter):
    _battleResultKeys = {0: 'fallTanksBattleNotFinishedResult',
     1: 'fallTanksBattleFinishedResult'}

    def _getBattleResultsKey(self, battleResults):
        return int(battleResults.get('fallTanksFinishTime', 0) > 0)

    def _prepareFormatData(self, message):
        templateName, ctx = super(FallTanksBattleResultsSubFormatter, self)._prepareFormatData(message)
        battleResults = message.data
        ctx['finishTime'] = formatTimeWithMs(battleResults.get('fallTanksFinishTime', 0))
        ctx['playerPlace'] = battleResults.get('fallTanksPosition', 0)
        return (templateName, ctx)
