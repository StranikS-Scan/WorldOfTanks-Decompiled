# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/impl/lobby/tooltips/comp7_core_modifiers_tooltip_view.py
from __future__ import absolute_import
from battle_modifiers.gui.impl.lobby.feature.helpers import packModifierModel
from battle_modifiers.gui.impl.lobby.tooltips.modifiers_domain_tooltip_view import ModifiersDomainTooltipView
from comp7_core.gui.impl.gen.view_models.views.lobby.tooltips.modifiers_tooltip.modifiers_tooltip_model import ModifiersTooltipModel
from comp7_core.gui.impl.gen.view_models.views.lobby.tooltips.modifiers_tooltip.sub_mode_modifiers import SubModeModifiers
from comp7_core.gui.impl.lobby.comp7_core_helpers.comp7_core_modifiers_data_provider import Comp7CoreSubModifiers, Comp7CoreModifiersDataProvider
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7CoreModifiersTooltipView(ModifiersDomainTooltipView):
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __slots__ = ('__subModesProvider',)

    def __init__(self, modifiersDomain):
        super(Comp7CoreModifiersTooltipView, self).__init__(modifiersDomain, R.views.comp7_core.mono.lobby.tooltips.modifiers_domain_tooltip(), ModifiersTooltipModel())
        self.__subModesProvider = Comp7CoreSubModifiers([ (subMode, modificators.get('battleModifiersDescr', ())) for subMode, modificators in self.__comp7Controller.subModes.items() ])

    def getModifiersDataProvider(self):
        return Comp7CoreModifiersDataProvider(self._modifiersDomain, self.__comp7Controller.battleModifiers)

    def _invalidateSubModes(self, model):
        subModesModifiersVL = model.getSubModesModifiers()
        subModesModifiersVL.clear()
        for provider in self.__subModesProvider.providers:
            subModeModifiersVM = SubModeModifiers()
            modifiersVL = subModeModifiersVM.getModifiers()
            modeName = provider.getDomains()[0]
            subModeModifiersVM.setModeName(modeName)
            rawModifiers = provider.getDomainModifiers(modeName)
            for modifier in rawModifiers:
                modifiersVL.addViewModel(packModifierModel(modifier))

            subModesModifiersVL.addViewModel(subModeModifiersVM)

        subModesModifiersVL.invalidate()
