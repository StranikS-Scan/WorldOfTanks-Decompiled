# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/battle_loading.py
import BigWorld
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from cgf_components import wt_helpers
from frameworks.wulf import ViewFlags, ViewSettings
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from skeletons.gui.battle_session import IBattleSessionProvider
from white_tiger.gui.Scaleform.daapi.view.meta.WTBattleLoadingMeta import WTBattleLoadingMeta
from white_tiger.gui.impl.gen.view_models.views.battle.wt_battle_loading_model import WtBattleLoadingModel

class WtBattleLoadingView(ViewImpl, IArenaLoadController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.white_tiger.battle.WtBattleLoadingView())
        settings.flags = flags
        settings.model = WtBattleLoadingModel()
        super(WtBattleLoadingView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WtBattleLoadingView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtBattleLoadingView, self)._onLoading()
        self.sessionProvider.addArenaCtrl(self)
        with self.viewModel.transaction() as tx:
            isBoss = wt_helpers.isBoss()
            tx.setIsBoss(isBoss)
            vehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID)
            vehicleName = vehicle.typeDescriptor.name.split(':')[-1].replace('-', '_')
            tx.setVehicleName(vehicleName)

    def _finalize(self):
        self.sessionProvider.removeArenaCtrl(self)
        super(WtBattleLoadingView, self)._finalize()

    def updateSpaceLoadProgress(self, progress):
        with self.viewModel.transaction() as tx:
            tx.setProgress(progress)


class WtBattleLoading(WTBattleLoadingMeta):

    def _makeInjectView(self):
        return WtBattleLoadingView()
