# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/maps_training/map_point_description_tooltip.py
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.maps_training.map_point_description_tooltip_model import MapPointDescriptionTooltipModel
from gui.impl.pub import ViewImpl

class MapPointDescriptionTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.maps_training.MapPointDescriptionTooltip(), args=args, kwargs=kwargs, model=MapPointDescriptionTooltipModel())
        super(MapPointDescriptionTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MapPointDescriptionTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(MapPointDescriptionTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setPointName(kwargs['event'].getArgument(MapPointDescriptionTooltipModel.ARG_POINT_NAME, ''))
