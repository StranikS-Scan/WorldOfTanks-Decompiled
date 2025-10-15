# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/tooltips/battle_result_stat_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from portal.gui.impl.gen.view_models.views.lobby.tooltips.battle_result_stat_tooltip_model import BattleResultStatTooltipModel

class BattleResultStatTooltip(ViewImpl):
    __slots__ = ('__name',)

    def __init__(self, name):
        settings = ViewSettings(R.views.portal.lobby.tooltips.BattleResultStatTooltip())
        settings.model = BattleResultStatTooltipModel()
        self.__name = name
        super(BattleResultStatTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleResultStatTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattleResultStatTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            titleRes = R.strings.portal_battle_result.result.tooltip.stat.dyn('{}'.format(self.__name)).dyn('title')()
            title = backport.text(titleRes)
            descrRes = R.strings.portal_battle_result.result.tooltip.stat.dyn('{}'.format(self.__name)).dyn('descr')()
            descr = backport.text(descrRes)
            model.setTitle(title)
            model.setDescr(descr)

    def _finalize(self):
        self.__name = None
        super(BattleResultStatTooltip, self)._finalize()
        return
