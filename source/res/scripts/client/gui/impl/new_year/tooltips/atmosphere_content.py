# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/atmosphere_content.py
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.new_year.tooltips.new_year_atmosphere_tooltip_content_model import NewYearAtmosphereTooltipContentModel
from gui.impl.pub import ViewImpl
from helpers import int2roman, dependency
from items import ny19
from new_year.ny_level_helper import NewYearAtmospherePresenter
from skeletons.new_year import INewYearController

class AtmosphereContent(ViewImpl):
    _nyController = dependency.descriptor(INewYearController)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(AtmosphereContent, self).__init__(R.views.newYearAtmosphereTooltipContent, ViewFlags.VIEW, NewYearAtmosphereTooltipContentModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(AtmosphereContent, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        level = NewYearAtmospherePresenter.getLevel()
        with self.getViewModel().transaction() as tx:
            earned = NewYearAtmospherePresenter.getAmount()
            tx.setEarnedAtmosphere(earned)
            boundLevel = level if level != ny19.CONSTS.MAX_ATMOSPHERE_LEVEL else level - 1
            tx.setTotalAtmosphere(ny19.CONSTS.ATMOSPHERE_LIMIT_BY_LEVEL[boundLevel])
            levelNames = tx.getLevelNames()
            levelValues = tx.getLevelValues()
            for idx, value in enumerate(ny19.CONSTS.TOY_ATMOSPHERE_BY_RANK):
                levelNames.addString(int2roman(idx + 1))
                levelValues.addNumber(value)

            if level == ny19.CONSTS.MAX_ATMOSPHERE_LEVEL:
                tx.setIsLastLevel(True)
            else:
                levelInfo = self._nyController.getLevel(NewYearAtmospherePresenter.getLevel() + 1)
                tx.setHasTankwoman(levelInfo.hasTankman())
                tx.setDiscountValue(levelInfo.variadicDiscountValue())
                tx.setTankLevel(int2roman(level + 1))
