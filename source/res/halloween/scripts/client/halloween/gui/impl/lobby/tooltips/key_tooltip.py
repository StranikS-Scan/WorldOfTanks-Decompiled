# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tooltips/key_tooltip.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from halloween.gui.impl.gen.view_models.views.lobby.tooltips.key_tooltip_view_model import KeyTooltipViewModel
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween.skeletons.halloween_controller import IHalloweenController
from helpers import dependency

class KeyTooltipView(ViewImpl):
    __slots__ = ('__isPostBattle', '__ctx')
    _hwArtifactsCtrl = dependency.descriptor(IHalloweenArtefactsController)
    _hwController = dependency.descriptor(IHalloweenController)

    def __init__(self, isPostBattle, ctx=None, layoutID=R.views.halloween.mono.lobby.tooltips.key_tooltip()):
        settings = ViewSettings(layoutID)
        settings.model = KeyTooltipViewModel()
        super(KeyTooltipView, self).__init__(settings)
        self.__isPostBattle = isPostBattle
        self.__ctx = ctx

    @property
    def viewModel(self):
        return super(KeyTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(KeyTooltipView, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setIsPostBatle(self.__isPostBattle)
            model.setKeyCount(self._hwArtifactsCtrl.getArtefactKeyQuantity())
            model.setEndDate(self._hwController.getConfig().get('endDate', 0))
            if self.__isPostBattle:
                model.setEffective(self.__ctx.get('effective', 0))
                model.setBoss(self.__ctx.get('boss', 0))
                model.setDaily(self.__ctx.get('daily', 0))
                model.setSecret(self.__ctx.get('secret', 0))
