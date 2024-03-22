# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/quest_booster_tooltip.py
from frameworks.wulf import ViewSettings
from gui.goodies.goodie_items import Booster, getFullNameForBoosterIcon
from gui.impl.common.personal_reserves.personal_reserves_shared_model_utils import fillBoosterModelWithData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.personal_reserves.booster_model import BoosterModel
from gui.impl.lobby.personal_reserves.personal_reserves_utils import getBoostersInGroup
from gui.impl.pub import ViewImpl
from helpers import dependency
from helpers.time_utils import ONE_DAY
from skeletons.gui.goodies import IGoodiesCache

class QuestBoosterTooltip(ViewImpl):
    __slots__ = ('boosterID',)
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, boosterID):
        settings = ViewSettings(R.views.lobby.personal_reserves.QuestBoosterTooltip())
        settings.model = BoosterModel()
        super(QuestBoosterTooltip, self).__init__(settings)
        self.boosterID = boosterID

    @property
    def viewModel(self):
        return super(QuestBoosterTooltip, self).getViewModel()

    def _onLoading(self):
        super(QuestBoosterTooltip, self)._onLoading()
        booster = self.goodiesCache.getBooster(self.boosterID)
        boosters = getBoostersInGroup(booster, self.goodiesCache)
        with self.viewModel.transaction() as model:
            fillBoosterModelWithData(model, booster)
            model.setWillExpireAfter(int((booster.expireAfter or 0) / ONE_DAY))
            model.setInDepotExpirableAmount(sum((inDepotBooster.count for inDepotBooster in boosters)))
            model.setIconId(getFullNameForBoosterIcon(booster.boosterType, isPremium=booster.getIsPremium(), isExpirable=bool(booster.expireAfter or 0)))
