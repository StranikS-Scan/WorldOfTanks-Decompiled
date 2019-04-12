# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/text_button_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.ui_kit.button_common_model import ButtonCommonModel

class TextButtonModel(ButtonCommonModel):
    __slots__ = ()

    def getLabelAdditional(self):
        return self._getResource(5)

    def setLabelAdditional(self, value):
        self._setResource(5, value)

    def getLabelAdditionalString(self):
        return self._getString(6)

    def setLabelAdditionalString(self, value):
        self._setString(6, value)

    def getImage(self):
        return self._getResource(7)

    def setImage(self, value):
        self._setResource(7, value)

    def _initialize(self):
        super(TextButtonModel, self)._initialize()
        self._addResourceProperty('labelAdditional', R.invalid())
        self._addStringProperty('labelAdditionalString', '')
        self._addResourceProperty('image', R.invalid())
