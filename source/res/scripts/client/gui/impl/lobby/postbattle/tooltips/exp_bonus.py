# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/postbattle/tooltips/exp_bonus.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.postbattle.exp_bonus_model import ExpBonusModel
from gui.impl.pub import ViewImpl

class ExpBonusTooltip(ViewImpl):
    __slots__ = ('__sourceDataModel',)

    def __init__(self, sourceDataModel):
        contentResID = R.views.white_tiger.lobby.postbattle.tooltips.ExpBonus()
        settings = ViewSettings(contentResID)
        settings.model = ExpBonusModel()
        super(ExpBonusTooltip, self).__init__(settings)
        self.__sourceDataModel = sourceDataModel

    def _finalize(self):
        super(ExpBonusTooltip, self)._finalize()
        self.__sourceDataModel = None
        return

    def _onLoading(self, *args, **kwargs):
        super(ExpBonusTooltip, self)._initialize(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setMaxBonusCount(self.__sourceDataModel.getMaxBonusCount())
            model.setUsedBonusCount(self.__sourceDataModel.getUsedBonusCount())
            model.setRestriction(self.__sourceDataModel.getRestriction())
            model.setBonusMultiplier(self.__sourceDataModel.getBonusMultiplier())
