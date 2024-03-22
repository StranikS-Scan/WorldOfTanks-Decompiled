# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/death_cam/death_cam_hud_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.battle.death_cam.death_cam_ui_view_model import DeathCamUiViewModel
from gui.impl.gen.view_models.views.battle.death_cam.marker_view_model import MarkerViewModel

class DeathCamHudViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(DeathCamHudViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def deathCamHUD(self):
        return self._getViewModel(0)

    @staticmethod
    def getDeathCamHUDType():
        return DeathCamUiViewModel

    @property
    def marker(self):
        return self._getViewModel(1)

    @staticmethod
    def getMarkerType():
        return MarkerViewModel

    def _initialize(self):
        super(DeathCamHudViewModel, self)._initialize()
        self._addViewModelProperty('deathCamHUD', DeathCamUiViewModel())
        self._addViewModelProperty('marker', MarkerViewModel())
