# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/tooltips/booster_tooltip.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from last_stand.gui.impl.gen.view_models.views.lobby.tooltips.booster_tooltip_model import BoosterTooltipModel
from last_stand.gui.impl.lobby.ls_helpers import getBoosterFactorsParam
from last_stand_common.last_stand_constants import BoostersSettings
from skeletons.gui.server_events import IEventsCache

class BoosterTooltipView(ViewImpl):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, boosterName='', layoutID=R.views.last_stand.mono.lobby.tooltips.booster_tooltip()):
        settings = ViewSettings(layoutID)
        settings.model = BoosterTooltipModel()
        super(BoosterTooltipView, self).__init__(settings)
        self.__boosterName = boosterName

    @property
    def viewModel(self):
        return super(BoosterTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BoosterTooltipView, self)._onLoading()
        params = getBoosterFactorsParam(self.__boosterName)
        with self.viewModel.transaction() as model:
            model.setBooster(self.__boosterName)
            model.setBody(backport.text(R.strings.last_stand_lobby.booster.dyn(self.__boosterName).description(), **params))
            model.setActivated(self.eventsCache.questsProgress.getTokenCount(BoostersSettings.TOKEN_PREFIX + self.__boosterName))
