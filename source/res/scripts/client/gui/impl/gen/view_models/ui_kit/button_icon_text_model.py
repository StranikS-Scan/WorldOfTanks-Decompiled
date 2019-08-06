# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/button_icon_text_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.ui_kit.button_common_model import ButtonCommonModel

class ButtonIconTextModel(ButtonCommonModel):
    __slots__ = ()

    def getIcon(self):
        return self._getResource(6)

    def setIcon(self, value):
        self._setResource(6, value)

    def _initialize(self):
        super(ButtonIconTextModel, self)._initialize()
        self._addResourceProperty('icon', R.invalid())
