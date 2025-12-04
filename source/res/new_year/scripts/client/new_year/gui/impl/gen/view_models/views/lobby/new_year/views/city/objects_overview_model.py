# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/city/objects_overview_model.py
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.ny_hover_marker_model import NyHoverMarkerModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.customization_zone.customization_zone_panel_model import CustomizationZonePanelModel

class ObjectsOverviewModel(ViewModel):
    __slots__ = ('onObjectHover', 'onObjectHoverOut')

    def __init__(self, properties=2, commands=2):
        super(ObjectsOverviewModel, self).__init__(properties=properties, commands=commands)

    @property
    def panel(self):
        return self._getViewModel(0)

    @staticmethod
    def getPanelType():
        return CustomizationZonePanelModel

    @property
    def hoveredObject(self):
        return self._getViewModel(1)

    @staticmethod
    def getHoveredObjectType():
        return NyHoverMarkerModel

    def _initialize(self):
        super(ObjectsOverviewModel, self)._initialize()
        self._addViewModelProperty('panel', CustomizationZonePanelModel())
        self._addViewModelProperty('hoveredObject', NyHoverMarkerModel())
        self.onObjectHover = self._addCommand('onObjectHover')
        self.onObjectHoverOut = self._addCommand('onObjectHoverOut')
