# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/client/battle_modifiers/gui/impl/lobby/tooltips/modifiers_domain_tooltip_view.py
import typing
from battle_modifiers.gui.impl.lobby.feature.helpers import packModifierModel
from battle_modifiers.gui.impl.gen.view_models.views.lobby.tooltips.modifiers_domain_tooltip_view_model import ModifiersDomainTooltipViewModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
if typing.TYPE_CHECKING:
    from battle_modifiers.gui.feature.modifiers_data_provider import ModifiersDataProvider

class ModifiersDomainTooltipView(ViewImpl):
    __slots__ = ('__modifiersDomain',)

    def __init__(self, modifiersDomain):
        settings = ViewSettings(layoutID=R.views.battle_modifiers.lobby.tooltips.ModifiersDomainTooltipView(), model=ModifiersDomainTooltipViewModel())
        super(ModifiersDomainTooltipView, self).__init__(settings)
        self.__modifiersDomain = modifiersDomain

    @property
    def viewModel(self):
        return super(ModifiersDomainTooltipView, self).getViewModel()

    def getModifiersDataProvider(self):
        raise NotImplementedError

    def _onLoading(self, *args, **kwargs):
        super(ModifiersDomainTooltipView, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setModifiersDomain(self.__modifiersDomain)
            self.__invalidateModifiers(model.getModifiers())

    def __invalidateModifiers(self, modifiers):
        modifiers.clear()
        modifiersProvider = self.getModifiersDataProvider()
        rawModifiers = modifiersProvider.getDomainModifiers(self.__modifiersDomain) if modifiersProvider else ()
        for modifier in rawModifiers:
            modifiers.addViewModel(packModifierModel(modifier))

        modifiers.invalidate()
