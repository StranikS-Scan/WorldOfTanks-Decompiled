# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/lobby/vehicles_carousel/vehicles_carousel.py
from frameworks.wulf import ViewFlags, ViewSettings
from races.gui.impl.gen.view_models.views.lobby.vehicles_carousel.vehicles_carousel_model import VehiclesCarouselModel
from gui.impl.pub import ViewImpl

class VehiclesCarousel(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = VehiclesCarouselModel()
        super(VehiclesCarousel, self).__init__(settings)

    @property
    def viewModel(self):
        return super(VehiclesCarousel, self).getViewModel()
