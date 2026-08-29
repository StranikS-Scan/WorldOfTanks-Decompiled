# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/impl/gen/view_models/views/lobby/tooltips/modifiers_tooltip/sub_mode_modifiers.py
from frameworks.wulf import Array, ViewModel
from comp7_core.gui.impl.gen.view_models.views.lobby.tooltips.modifiers_tooltip.modifier_model import ModifierModel

class SubModeModifiers(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SubModeModifiers, self).__init__(properties=properties, commands=commands)

    def getModeName(self):
        return self._getString(0)

    def setModeName(self, value):
        self._setString(0, value)

    def getModifiers(self):
        return self._getArray(1)

    def setModifiers(self, value):
        self._setArray(1, value)

    @staticmethod
    def getModifiersType():
        return ModifierModel

    def _initialize(self):
        super(SubModeModifiers, self)._initialize()
        self._addStringProperty('modeName', '')
        self._addArrayProperty('modifiers', Array())
