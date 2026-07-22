# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/client/battle_modifiers/gui/impl/gen/view_models/views/lobby/tooltips/modifiers_domain_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from battle_modifiers.gui.impl.gen.view_models.views.lobby.feature.modifier_model import ModifierModel

class ModifiersDomainTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ModifiersDomainTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getModifiersDomain(self):
        return self._getString(0)

    def setModifiersDomain(self, value):
        self._setString(0, value)

    def getModifiers(self):
        return self._getArray(1)

    def setModifiers(self, value):
        self._setArray(1, value)

    @staticmethod
    def getModifiersType():
        return ModifierModel

    def _initialize(self):
        super(ModifiersDomainTooltipViewModel, self)._initialize()
        self._addStringProperty('modifiersDomain', '')
        self._addArrayProperty('modifiers', Array())
