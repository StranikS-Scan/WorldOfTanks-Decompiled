# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/base_presenter.py
import logging
import typing
from gui.battle_results.stats_ctrl import IBattleResultStatsCtrl, BattleResults
from gui.impl.backport import createContextMenuData
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.reusable import _ReusableInfo
    from gui.battle_results.presenters.packers.interfaces import ITooltipPacker
    BattleResultsModelType = typing.TypeVar('BattleResultsModelType', bound=ViewModel)
    TooltipModelType = typing.TypeVar('TooltipModelType', bound=ViewModel)
_logger = logging.getLogger(__name__)

class BaseStatsPresenter(IBattleResultStatsCtrl):
    __slots__ = ('_battleResults', '_updateCommandsMap')
    _TOOLTIPS_PACKERS = {}
    _CONTEXT_MENU_TYPE = None

    def __init__(self, _):
        self._battleResults = None
        self._updateCommandsMap = {}
        return

    def clear(self):
        self._battleResults = None
        self._updateCommandsMap = {}
        return

    def getVO(self):
        raise SoftException('Unsupported method')

    def getBackportContextMenuData(self, databaseID, vehicleCD):
        return createContextMenuData(self._CONTEXT_MENU_TYPE, self._getContextMenuArgs(databaseID, vehicleCD)) if self._CONTEXT_MENU_TYPE is not None else None

    def setResults(self, results, reusable):
        self._battleResults = BattleResults(results, reusable)

    def packModel(self, model, *args, **kwargs):
        raise NotImplementedError

    def packTooltips(self, tooltipType, model, ctx=None):
        tooltipPacker = self._TOOLTIPS_PACKERS.get(tooltipType)
        if tooltipPacker is None:
            _logger.error('Missing tooltip packer for battle result tooltip "%s"', tooltipType)
            return
        else:
            tooltipPacker.packTooltip(model, self._battleResults, ctx)
            return

    def updateModel(self, updateType, model, ctx=None, isFullUpdate=True):
        processor = self._updateCommandsMap.get(updateType)
        if processor is None:
            _logger.error('Missing processor to update battle results for type "%s"', updateType)
            return
        else:
            processor(model, ctx, isFullUpdate)
            return

    def _getContextMenuArgs(self, databaseID, vehicleCD):
        reusable = self._battleResults.reusable
        playerInfo = reusable.players.getPlayerInfo(databaseID)
        return {'dbID': databaseID,
         'userName': playerInfo.realName,
         'clanAbbrev': playerInfo.clanAbbrev,
         'isAlly': playerInfo.team == reusable.getPersonalTeam(),
         'vehicleCD': vehicleCD,
         'wasInBattle': True,
         'clientArenaIdx': reusable.arenaUniqueID,
         'arenaType': reusable.common.arenaGuiType}
