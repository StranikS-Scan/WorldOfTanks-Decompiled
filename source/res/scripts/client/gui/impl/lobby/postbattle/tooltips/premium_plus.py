# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/postbattle/tooltips/premium_plus.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.postbattle.tooltips.premium_plus_model import PremiumPlusModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService

class PremiumPlusTooltip(ViewImpl):
    __slots__ = ()
    __battleResults = dependency.descriptor(IBattleResultsService)

    def __init__(self):
        contentResID = R.views.lobby.postbattle.tooltips.PremiumPlus()
        settings = ViewSettings(contentResID)
        settings.model = PremiumPlusModel()
        super(PremiumPlusTooltip, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(PremiumPlusTooltip, self)._initialize(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setPremiumBenefits(self.__battleResults.presenter.getPremiumBenefits())
