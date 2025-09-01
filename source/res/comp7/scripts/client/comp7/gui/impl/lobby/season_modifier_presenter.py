# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/season_modifier_presenter.py
from __future__ import absolute_import
from comp7.gui.impl.gen.view_models.views.lobby.season_modifier_model import SeasonModifierModel
from comp7.gui.impl.lobby.tooltips.comp7_modifiers_domain_tooltip_view import Comp7ModifiersDomainTooltipView
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from gui.impl.gen import R
from skeletons.gui.game_control import IComp7Controller
from comp7.constants import COMP7_SEASON_MODIFIERS_DOMAIN

class SeasonModifierPresenter(ViewComponent[SeasonModifierModel]):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self):
        super(SeasonModifierPresenter, self).__init__(model=SeasonModifierModel)

    def _onLoading(self, *args, **kwargs):
        super(SeasonModifierPresenter, self)._onLoading(*args, **kwargs)
        self.__updateData()

    @property
    def viewModel(self):
        return super(SeasonModifierPresenter, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return Comp7ModifiersDomainTooltipView(COMP7_SEASON_MODIFIERS_DOMAIN) if contentID == R.views.battle_modifiers.lobby.tooltips.ModifiersDomainTooltipView() else super(SeasonModifierPresenter, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self.__comp7Controller.onBanUpdated, self.__updateData),
         (self.__comp7Controller.onQualificationStateUpdated, self.__updateData),
         (self.__comp7Controller.onStatusUpdated, self.__updateData),
         (self.__comp7Controller.onModeConfigChanged, self.__updateData))

    def __updateData(self, _=None):
        self.viewModel.setEnabled(self.__comp7Controller.isBattleModifiersAvailable())
