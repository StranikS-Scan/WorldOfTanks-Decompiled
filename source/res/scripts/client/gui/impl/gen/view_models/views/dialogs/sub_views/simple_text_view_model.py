# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/sub_views/simple_text_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.dialogs.sub_views.image_substitution_view_model import ImageSubstitutionViewModel

class SimpleTextViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SimpleTextViewModel, self).__init__(properties=properties, commands=commands)

    def getText(self):
        return self._getString(0)

    def setText(self, value):
        self._setString(0, value)

    def getImageSubstitutions(self):
        return self._getArray(1)

    def setImageSubstitutions(self, value):
        self._setArray(1, value)

    @staticmethod
    def getImageSubstitutionsType():
        return ImageSubstitutionViewModel

    def _initialize(self):
        super(SimpleTextViewModel, self)._initialize()
        self._addStringProperty('text', '')
        self._addArrayProperty('imageSubstitutions', Array())
