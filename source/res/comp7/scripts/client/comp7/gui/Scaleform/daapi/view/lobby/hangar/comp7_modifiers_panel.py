# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/hangar/comp7_modifiers_panel.py
from comp7.constants import COMP7_SEASON_MODIFIERS_DOMAIN
from comp7.gui.impl.lobby.tooltips.comp7_modifiers_domain_tooltip_view import Comp7ModifiersDomainTooltipView
from frameworks.wulf import ViewFlags, ViewSettings, ViewModel
from helpers import dependency
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from skeletons.gui.game_control import IBattleModifiersController
from skeletons.gui.hangar import IBattleModifiersEntry

class Comp7ModifiersPanel(ViewImpl, IBattleModifiersEntry):
    __battleModifiersController = dependency.descriptor(IBattleModifiersController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.comp7.SeasonModifier())
        settings.flags = flags
        settings.model = ViewModel()
        super(Comp7ModifiersPanel, self).__init__(settings)

    @classmethod
    def getIsActive(cls):
        modifiersDomain = cls.__battleModifiersController.getCurrentDomain()
        return modifiersDomain == IBattleModifiersController.ModifiersDomains.COMP7

    def createToolTipContent(self, event, contentID):
        return Comp7ModifiersDomainTooltipView(COMP7_SEASON_MODIFIERS_DOMAIN)
