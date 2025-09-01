# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/season_modifier_presenter.py
from __future__ import absolute_import
from comp7_light.gui.impl.gen.view_models.views.lobby.season_modifier_model import SeasonModifierModel
from comp7_light.gui.impl.lobby.tooltips.comp7_light_modifiers_domain_tooltip_view import Comp7LightModifiersDomainTooltipView, COMP7_LIGHT_SEASON_MODIFIERS_DOMAIN
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from gui.impl.gen import R
from skeletons.gui.game_control import IComp7LightController

class SeasonModifierPresenter(ViewComponent[SeasonModifierModel]):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def __init__(self):
        super(SeasonModifierPresenter, self).__init__(model=SeasonModifierModel)

    def _onLoading(self, *args, **kwargs):
        super(SeasonModifierPresenter, self)._onLoading(*args, **kwargs)
        self.__updateData()

    @property
    def viewModel(self):
        return super(SeasonModifierPresenter, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return Comp7LightModifiersDomainTooltipView(COMP7_LIGHT_SEASON_MODIFIERS_DOMAIN) if contentID == R.views.battle_modifiers.lobby.tooltips.ModifiersDomainTooltipView() else super(SeasonModifierPresenter, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self.__comp7LightController.onStatusUpdated, self.__updateData), (self.__comp7LightController.onModeConfigChanged, self.__updateData))

    def __updateData(self, _=None):
        self.viewModel.setEnabled(self.__comp7LightController.isBattleModifiersAvailable())
