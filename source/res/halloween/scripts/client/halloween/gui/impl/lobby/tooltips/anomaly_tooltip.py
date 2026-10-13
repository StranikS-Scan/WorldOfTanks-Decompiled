# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tooltips/anomaly_tooltip.py
from __future__ import absolute_import
import typing
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from halloween.configs.hw_upgrades_config import getConfig
from halloween.gui.impl.gen.view_models.views.common.anomaly_model import AnomalyType
from halloween.gui.impl.gen.view_models.views.lobby.tooltips.anomaly_tooltip_view_model import AnomalyTooltipViewModel
from halloween.skeletons.halloween_anomalies_controller import IHalloweenAnomaliesController
from helpers import dependency
if typing.TYPE_CHECKING:
    from halloween.gui.game_control.halloween_anomalies_controller import AnomalyData
    from halloween.gui.impl.gen.view_models.views.common.anomaly_model import AnomalyState
_ANOMALY_VEHICLE_KEY = 'vehicleAnomaly'

class AnomalyTooltipView(ViewImpl):
    __slots__ = ('__anomaly', '__state')
    _hwAnomaliesCtrl = dependency.descriptor(IHalloweenAnomaliesController)

    def __init__(self, anomaly, state):
        settings = ViewSettings(R.views.halloween.mono.lobby.tooltips.anomaly_tooltip(), model=AnomalyTooltipViewModel())
        super(AnomalyTooltipView, self).__init__(settings)
        self.__anomaly = anomaly
        self.__state = state

    @property
    def viewModel(self):
        return super(AnomalyTooltipView, self).getViewModel()

    def _onLoading(self):
        with self.viewModel.transaction() as tx:
            anomalyID = self.__anomaly.id
            tx.anomaly.setId(anomalyID)
            tx.anomaly.setType(AnomalyType(self.__anomaly.type))
            tx.anomaly.setState(self.__state)
            locR = R.strings.halloween_buffs.buffs.dyn(anomalyID)
            tx.setDescription(self._getDescription(locR, anomalyID))
            tx.setSpecialInfo(self._getSpecialInfo(locR))

    def _getDescription(self, locR, anomalyName):
        params = getConfig().upgrade[anomalyName].getDefaultConfig().param
        return backport.text(locR.body(), **params)

    def _getSpecialInfo(self, locR):
        specialInfoLocR = locR.dyn(_ANOMALY_VEHICLE_KEY)
        return backport.text(specialInfoLocR()) if specialInfoLocR.isValid() else ''
