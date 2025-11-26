# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/client/battle_modifiers/gui/impl/lobby/hangar/presenters/modifiers_presenter.py
from __future__ import absolute_import
import typing
from battle_modifiers.gui.impl.gen.view_models.views.lobby.hangar.modifiers_hangar_view_model import ModifiersHangarViewModel
from frameworks.wulf.view.array import fillStringsArray
from gui.impl.pub.view_component import ViewComponent
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from battle_modifiers.gui.feature.modifiers_data_provider import ModifiersDataProvider

class ModifiersPresenter(ViewComponent[ModifiersHangarViewModel]):

    def __init__(self):
        super(ModifiersPresenter, self).__init__(model=ModifiersHangarViewModel)

    def getModifiersDataProvider(self):
        raise NotImplementedError

    def _onLoading(self, *args, **kwargs):
        super(ModifiersPresenter, self)._onLoading(*args, **kwargs)
        self._updateData()

    def _updateData(self):
        with self.getViewModel().transaction() as model:
            self.__invalidateModifiersDomains(model.getModifiersDomains())

    def __invalidateModifiersDomains(self, modifiersDomains):
        modifiersProvider = self.getModifiersDataProvider()
        domains = () if modifiersProvider is None else modifiersProvider.getDomains()
        fillStringsArray(domains, modifiersDomains)
        return
