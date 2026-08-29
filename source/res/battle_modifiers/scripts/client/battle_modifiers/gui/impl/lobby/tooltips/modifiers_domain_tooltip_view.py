# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/client/battle_modifiers/gui/impl/lobby/tooltips/modifiers_domain_tooltip_view.py
from __future__ import absolute_import
import typing
from battle_modifiers.gui.impl.lobby.feature.helpers import packModifierModel
from battle_modifiers.gui.impl.gen.view_models.views.lobby.tooltips.modifiers_domain_tooltip_view_model import ModifiersDomainTooltipViewModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
if typing.TYPE_CHECKING:
    from battle_modifiers.gui.feature.modifiers_data_provider import ModifiersDataProvider

class ModifiersDomainTooltipView(ViewImpl):
    __slots__ = ('_modifiersDomain',)

    def __init__(self, modifiersDomain, layoutID=R.views.battle_modifiers.lobby.tooltips.ModifiersDomainTooltipView(), model=None, *args):
        if model is None:
            model = ModifiersDomainTooltipViewModel()
        settings = ViewSettings(layoutID=layoutID, model=model, args=args)
        self._modifiersDomain = modifiersDomain
        super(ModifiersDomainTooltipView, self).__init__(settings)
        return

    def _finalize(self):
        self._modifiersDomain = None
        super(ModifiersDomainTooltipView, self)._finalize()
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def getModifiersDataProvider(self):
        raise NotImplementedError

    def _onLoading(self, *args, **kwargs):
        super(ModifiersDomainTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setModifiersDomain(self._modifiersDomain)
            self.__invalidateModifiers(model.getModifiers())
            self._invalidateSubModes(model)

    def __invalidateModifiers(self, modifiers):
        modifiers.clear()
        modifiersProvider = self.getModifiersDataProvider()
        rawModifiers = () if modifiersProvider is None else modifiersProvider.getDomainModifiers(self._modifiersDomain)
        for modifier in rawModifiers:
            modifiers.addViewModel(packModifierModel(modifier))

        modifiers.invalidate()
        return

    def _invalidateSubModes(self, model):
        pass
