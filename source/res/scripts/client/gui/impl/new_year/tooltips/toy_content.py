# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/toy_content.py
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.new_year.tooltips.new_year_toy_tooltip_content_model import NewYearToyTooltipContentModel
from gui.impl.pub import ViewImpl
from helpers import int2roman
from new_year.ny_requester import NewYear19ToyInfo

class ToyContent(ViewImpl):
    __slots__ = ('__toyID',)

    def __init__(self, toyID, *args, **kwargs):
        super(ToyContent, self).__init__(R.views.newYearToyTooltipContent, ViewFlags.VIEW, NewYearToyTooltipContentModel, *args, **kwargs)
        self.__toyID = int(toyID)

    @property
    def viewModel(self):
        return super(ToyContent, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        toy = NewYear19ToyInfo(self.__toyID)
        with self.viewModel.transaction() as tx:
            tx.setRank(int2roman(toy.getRank()))
            tx.setRankNumber(str(toy.getRank()))
            tx.setLocalName(toy.getLocalKey())
            tx.setShardsPrice(toy.getShards())
            tx.setAtmospherePoint(toy.getAtmosphere())
            tx.setSetting(toy.getSetting())
