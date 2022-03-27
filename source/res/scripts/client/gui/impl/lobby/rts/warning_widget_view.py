# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/warning_widget_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.rts.warning_widget_view_model import WarningWidgetViewModel
from gui.impl.pub import ViewImpl
from gui.rts_battles.rts_helpers import playedRandomBattleOnTierXVehicle
from helpers import dependency
from skeletons.gui.game_control import IRTSBattlesController
from skeletons.gui.shared import IItemsCache

class WarningWidgetView(ViewImpl):
    __slots__ = ()
    rtsController = dependency.descriptor(IRTSBattlesController)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        model = WarningWidgetViewModel()
        playedEnoughBattlesWithTierX = playedRandomBattleOnTierXVehicle(self.itemsCache, self.rtsController)
        if not playedEnoughBattlesWithTierX:
            minNumOfBattles = self.rtsController.getSettings().getMinNumberOfBattlesPlayedWithTierX()
            model.setMessage(backport.text(R.strings.rts_battles.warningWidget.battlesWarning(), numBattles=minNumOfBattles))
        else:
            model.setMessage(backport.text(R.strings.rts_battles.warningWidget.description()))
        settings = ViewSettings(R.views.lobby.rts.WarningWidgetView(), flags=ViewFlags.COMPONENT, model=model)
        super(WarningWidgetView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WarningWidgetView, self).getViewModel()
