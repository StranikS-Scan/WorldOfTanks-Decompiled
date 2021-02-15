# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_notifier/battle_notifier_view.py
import logging
from collections import deque
import ArenaType
from constants import ARENA_BONUS_TYPE
from items.vehicles import getVehicleType, getVehicleClassFromVehicleType
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.battle_notifier.battle_notifier_view_model import BattleNotifierViewModel, ResultEnum
from gui.impl.pub import ViewImpl
from gui.shared.money import Currency
_logger = logging.getLogger(__name__)

class BattleNotifierView(ViewImpl):
    __slots__ = ('__resultsQueue', '__uiReadyForData', '__arenaLoaded')

    def __init__(self):
        settings = ViewSettings(R.views.battle.battle_notifier.BattleNotifierView(), ViewFlags.COMPONENT, BattleNotifierViewModel())
        super(BattleNotifierView, self).__init__(settings)
        self.__resultsQueue = deque()
        self.__uiReadyForData = True
        self.__arenaLoaded = False

    @property
    def viewModel(self):
        return super(BattleNotifierView, self).getViewModel()

    def arenaLoadCompleted(self):
        self.__arenaLoaded = True
        self._sendNotificationData()

    def addBattleResults(self, message):
        results = _collectResults(message)
        if results is None:
            return
        else:
            self.__resultsQueue.append(results)
            self._sendNotificationData()
            return

    def _initialize(self, *args, **kwargs):
        self.viewModel.onResultShown += self.__onResultShown

    def _finalize(self):
        self.viewModel.onResultShown -= self.__onResultShown

    def _sendNotificationData(self):
        if self.__arenaLoaded and self.__uiReadyForData:
            self._fillComponentModel()

    def _fillComponentModel(self):
        if self.__resultsQueue:
            battleResult = self.__resultsQueue.popleft()
            with self.viewModel.transaction() as tr:
                tr.setBattleResult(battleResult['result'])
                tr.setBattleStartTime(battleResult['time'])
                tr.setMapName(battleResult['arenaName'])
                tr.setVehicleName(battleResult['vehicleName'])
                tr.setVehicleTier(battleResult['vehicleTier'])
                tr.setVehicleClass(battleResult['vehicleClass'])
                tr.setCreditsAmount(battleResult[Currency.CREDITS])
                tr.setExperienceAmount(battleResult['xp'])
                tr.setCrystalAmount(battleResult[Currency.CRYSTAL])
            self.__uiReadyForData = False

    def __onResultShown(self):
        self.__uiReadyForData = True
        self._sendNotificationData()


def _randomBattleResults(message):
    battleResults = message.data
    arenaTypeID = battleResults.get('arenaTypeID', 0)
    if arenaTypeID > 0 and arenaTypeID in ArenaType.g_cache:
        arenaType = ArenaType.g_cache[arenaTypeID]
    else:
        arenaType = None
    arenaCreateTime = battleResults.get('arenaCreateTime', None)
    if arenaCreateTime and arenaType:
        results = {'time': arenaCreateTime,
         'vehicleTier': 'N/A',
         'vehicleClass': 'N/A',
         'vehicleName': 'N/A',
         'result': ResultEnum(battleResults.get('isWinner', 0)),
         'arenaName': arenaType.name,
         'xp': 0,
         Currency.CREDITS: 0,
         Currency.CRYSTAL: 0}
        intCD = battleResults.get('playerVehicles', {}).keys()[0]
        vehicleType = getVehicleType(intCD)
        results['vehicleName'] = vehicleType.shortUserString
        results['vehicleClass'] = getVehicleClassFromVehicleType(vehicleType)
        results['vehicleTier'] = vehicleType.level
        xp = battleResults.get('xp')
        if xp:
            results['xp'] = int(xp)
        accCredits = battleResults.get(Currency.CREDITS) - battleResults.get('creditsToDraw', 0)
        if accCredits:
            results[Currency.CREDITS] = int(accCredits)
        crystal = battleResults.get(Currency.CRYSTAL)
        if crystal:
            results[Currency.CRYSTAL] = int(crystal)
        return results
    else:
        _logger.warning('Could not format message, no arena createTime or arenaType found in message.')
        return
        return


_formatters = {ARENA_BONUS_TYPE.REGULAR: _randomBattleResults,
 ARENA_BONUS_TYPE.EPIC_RANDOM: _randomBattleResults}

def _collectResults(message):
    arenaBonusType = message.data.get('bonusType', None)
    if arenaBonusType is None:
        _logger.warning('[BattleNotifier] no "bonusType" item found in battle results. Cannot parse results.')
        return
    else:
        formatter = _formatters.get(arenaBonusType, None)
        if formatter is None:
            _logger.debug('[BattleNotifier] The arena bonus type, %s, is not yet supported. Chat message: %s', arenaBonusType, message)
            return
        return formatter(message)
