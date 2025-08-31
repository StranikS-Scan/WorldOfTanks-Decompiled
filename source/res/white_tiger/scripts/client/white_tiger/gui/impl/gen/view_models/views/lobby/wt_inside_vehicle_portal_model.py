# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_inside_vehicle_portal_model.py
from white_tiger.gui.impl.gen.view_models.views.lobby.main_vehicle_prize import MainVehiclePrize
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_portal_model import WtEventPortalModel

class WtInsideVehiclePortalModel(WtEventPortalModel):
    __slots__ = ('onPreviewTankClick',)

    def __init__(self, properties=29, commands=6):
        super(WtInsideVehiclePortalModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainVehiclePrize(self):
        return self._getViewModel(28)

    @staticmethod
    def getMainVehiclePrizeType():
        return MainVehiclePrize

    def _initialize(self):
        super(WtInsideVehiclePortalModel, self)._initialize()
        self._addViewModelProperty('mainVehiclePrize', MainVehiclePrize())
        self.onPreviewTankClick = self._addCommand('onPreviewTankClick')
