# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/death_cam/death_cam_hud_view.py
import logging
from gui.impl.battle.death_cam.death_cam_ui_view import DeathCamUIView
from gui.impl.battle.death_cam.marker_view import DeathCamMarkerView
from gui.impl.gen import R
from typing import List, Union
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.battle.death_cam.death_cam_hud_view_model import DeathCamHudViewModel
from gui.impl.pub import ViewImpl
_logger = logging.getLogger(__name__)

class DeathCamHudView(ViewImpl):
    __slots__ = ('__subviews',)

    def __init__(self):
        viewSettings = ViewSettings(layoutID=R.views.battle.death_cam.DeathCamHudView(), flags=ViewFlags.VIEW, model=DeathCamHudViewModel())
        super(DeathCamHudView, self).__init__(viewSettings)
        self.__subviews = []

    @property
    def viewModel(self):
        return super(DeathCamHudView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DeathCamHudView, self)._onLoading(*args, **kwargs)
        self.__subviews.append(DeathCamUIView(self.viewModel.deathCamHUD, self))
        self.__subviews.append(DeathCamMarkerView(self.viewModel.marker, self))
        for subview in self.__subviews:
            subview.initialize()

    def _finalize(self):
        for subview in self.__subviews:
            subview.finalize()
            subview.clear()

        self.__subviews = None
        super(DeathCamHudView, self)._finalize()
        return
