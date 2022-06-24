# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/fun_random/tooltips/fun_random_modifiers_domain_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_modifiers.modifier_model import ModifierModel

class FunRandomModifiersDomainTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(FunRandomModifiersDomainTooltipViewModel, self).__init__(properties=properties, commands=commands)

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
        super(FunRandomModifiersDomainTooltipViewModel, self)._initialize()
        self._addStringProperty('modifiersDomain', '')
        self._addArrayProperty('modifiers', Array())
