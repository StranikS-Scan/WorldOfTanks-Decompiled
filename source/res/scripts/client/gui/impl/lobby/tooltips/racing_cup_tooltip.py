# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/racing_cup_tooltip.py
from arena_achievements import RACING_ACHIEVEMENT_POINTS, RACING_ACHIEVEMENT_CONDITIONS
from frameworks.wulf import ViewFlags, View
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.tooltips.racing_cup_tooltip_model import RacingCupTooltipModel
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class RacingCupTooltip(View):
    __slots__ = ()
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, cupType, *args, **kwargs):
        super(RacingCupTooltip, self).__init__(R.views.lobby.tooltips.racing_cup_tooltip.RacingCupTooltip(), ViewFlags.COMPONENT, RacingCupTooltipModel, cupType, *args, **kwargs)

    @property
    def viewModel(self):
        return super(RacingCupTooltip, self).getViewModel()

    def _initialize(self, cupType, *args, **kwargs):
        with self.viewModel.transaction() as model:
            model.setCupType(cupType)
            cupCount = self._itemsCache.items.getAccountDossier().getRecordValue('racing2019Achievements', cupType)
            model.setCountCups(cupCount)
            model.setPricePoints(RACING_ACHIEVEMENT_POINTS.get(cupType, 0))
            model.setCupCondition(backport.getIntegralFormat(RACING_ACHIEVEMENT_CONDITIONS.get(cupType, {}).get('minDamageDealt', 0)))
