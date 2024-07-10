# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/interfaces.py
import typing
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel, Array
    from gui.battle_results.stats_ctrl import BattleResults
    from gui.battle_results.reusable.shared import VehicleSummarizeInfo
    from gui.impl.gen.view_models.views.lobby.battle_results.financial_details_model import FinancialDetailsModel
    from gui.impl.gen.view_models.views.lobby.battle_results.simple_stats_parameter_model import SimpleStatsParameterModel
    BattleResultsComponentModelType = typing.TypeVar('BattleResultsComponentModelType', bound=ViewModel)
    TooltipModelType = typing.TypeVar('TooltipModelType', bound=ViewModel)

class IBattleResultsPacker(object):

    @classmethod
    def packModel(cls, model, battleResults):
        raise NotImplementedError

    @classmethod
    def updateModel(cls, model, battleResults, ctx=None, isFullUpdate=True):
        pass


class ICurrencyPacker(object):

    @classmethod
    def packModel(cls, model, currencyType, battleResults):
        pass


class IStatisticsPacker(object):

    @classmethod
    def packModel(cls, model, info, battleResult):
        pass


class ITooltipPacker(object):

    @classmethod
    def packTooltip(cls, model, battleResults, ctx=None):
        raise NotImplementedError
