# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/new_year_bonus_tooltip.py
import BigWorld
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.new_year.tooltips.new_year_bonus_tooltip_model import NewYearBonusTooltipModel
from gui.impl.pub import ViewImpl, StandardWindow
from helpers import dependency
from items import ny19
from items.components.ny_constants import BonusCollectionIDs
from new_year.ny_constants import COLLECTIONS_SETTINGS_IDS, Collections
from new_year.ny_level_helper import NewYearAtmospherePresenter
from skeletons.new_year import INewYearController

class NewYearBonusTooltip(ViewImpl):
    _nyController = dependency.descriptor(INewYearController)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(NewYearBonusTooltip, self).__init__(R.views.newYearBonusTooltip, ViewFlags.VIEW, NewYearBonusTooltipModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(NewYearBonusTooltip, self).getViewModel()

    def _initialize(self):
        self.viewModel.setCredits(int(self._nyController.getBattleBonus(BonusCollectionIDs.CREDITS)))
        self.viewModel.setXp(int(self._nyController.getBattleBonus(BonusCollectionIDs.XP)))
        self.viewModel.setFree_xp(int(self._nyController.getBattleBonus(BonusCollectionIDs.FREE_XP)))
        self.viewModel.setCrew_xp(int(self._nyController.getBattleBonus(BonusCollectionIDs.CREW_XP)))
        collectionsIDs = COLLECTIONS_SETTINGS_IDS[Collections.NewYear19]
        self.viewModel.setIsFullCollection(self._nyController.isCollectionCompleted(collectionsIDs))
        isMaxLevel = NewYearAtmospherePresenter.getLevel() == ny19.CONSTS.MAX_ATMOSPHERE_LEVEL
        self.viewModel.setIsMaxLevel(isMaxLevel)
        self.viewModel.setDate(BigWorld.wg_getShortDateFormat(self._nyController.getFinishTime()))


class NewYearBonusTooltipWindow(StandardWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(NewYearBonusTooltipWindow, self).__init__(content=NewYearBonusTooltip(), parent=parent)

    def _initialize(self):
        super(NewYearBonusTooltipWindow, self)._initialize()
        self.windowModel.setTitle(R.strings.development.wulf.demoWindow.title)
