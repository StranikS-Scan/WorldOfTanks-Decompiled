# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_menu_collections_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_menu_collections_tooltip_model import NyMenuCollectionsTooltipModel
from gui.impl.pub import ViewImpl
from new_year.collection_presenters import CurrentNYCollectionPresenter

class NyMenuCollectionsTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID=R.views.lobby.new_year.tooltips.NyMenuCollectionsTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = NyMenuCollectionsTooltipModel()
        super(NyMenuCollectionsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyMenuCollectionsTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(NyMenuCollectionsTooltip, self)._initialize()
        toys = str(CurrentNYCollectionPresenter.getCount())
        allToys = str(CurrentNYCollectionPresenter.getTotalCount())
        self.viewModel.setCurrentToysCount(toys)
        self.viewModel.setAllToysCount(allToys)
