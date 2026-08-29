# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/rest_bonus_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tooltips.rest_bonus_tooltip_model import RestBonusTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from helpers import time_utils
from skeletons.gui.game_control import IRestBonusController
from skeletons.gui.shared import IItemsCache

class RestBonusTooltip(ViewImpl):
    __restBonusController = dependency.descriptor(IRestBonusController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.mono.rest_bonus.tooltips.rest_bonus_tooltip())
        settings.model = RestBonusTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(RestBonusTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RestBonusTooltip, self).getViewModel()

    def _onLoading(self, intCD, *args, **kwargs):
        super(RestBonusTooltip, self)._onLoading(*args, **kwargs)
        vehicle = self.__itemsCache.items.getItemByCD(intCD)
        with self.viewModel.transaction() as model:
            model.setMultiplier(self.__restBonusController.getActualXPFactor(vehicle))
            model.setResetTimestamp(time_utils.getTimestampFromUTC(time_utils.getTimeStructInLocal(self.__restBonusController.getDailyResetTime())))
            model.setEndTimestamp(self.__restBonusController.getRestBonusExpiryTime())
