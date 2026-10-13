# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/shared/crosshair/state_presenter.py
from __future__ import absolute_import
import typing
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID
from gui.impl.gen.view_models.views.battle.shared.crosshair_state_model import CrosshairStateModel, CrosshairType
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.crosshair_proxy import CrosshairDataProxy
_CROSSHAIR_TYPE_BY_ID = {CROSSHAIR_VIEW_ID.UNDEFINED: CrosshairType.UNDEFINED,
 CROSSHAIR_VIEW_ID.ARCADE: CrosshairType.ARCADE,
 CROSSHAIR_VIEW_ID.SNIPER: CrosshairType.SNIPER,
 CROSSHAIR_VIEW_ID.STRATEGIC: CrosshairType.STRATEGIC,
 CROSSHAIR_VIEW_ID.POSTMORTEM: CrosshairType.POSTMORTEM}

class CrosshairStatePresenter(ViewComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(CrosshairStatePresenter, self).__init__(model=CrosshairStateModel)

    @property
    def viewModel(self):
        return super(CrosshairStatePresenter, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CrosshairStatePresenter, self)._onLoading(*args, **kwargs)
        crosshairCtrl = self.__sessionProvider.shared.crosshair
        if crosshairCtrl is None:
            return
        else:
            with self.viewModel as tx:
                tx.setCrosshairType(self.__getTypeByID(crosshairCtrl.getViewID()))
                tx.setZoomFactor(crosshairCtrl.getZoomFactor())
            return

    def _getEvents(self):
        ctrl = self.__sessionProvider.shared.crosshair
        return () if ctrl is None else ((ctrl.onCrosshairViewChanged, self.__onCrosshairViewChanged), (ctrl.onCrosshairZoomFactorChanged, self.__onCrosshairZoomFactorChanged))

    def __onCrosshairViewChanged(self, viewID):
        self.viewModel.setCrosshairType(self.__getTypeByID(viewID))

    def __onCrosshairZoomFactorChanged(self, zoomFactor):
        self.viewModel.setZoomFactor(zoomFactor)

    @staticmethod
    def __getTypeByID(viewID):
        return _CROSSHAIR_TYPE_BY_ID.get(viewID, CrosshairType.UNDEFINED)
