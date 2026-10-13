# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/style_guide/style_guide_view_model.py
from frameworks.wulf import ViewModel

class StyleGuideViewModel(ViewModel):
    __slots__ = ('onSaveThemeFile',)

    def __init__(self, properties=0, commands=1):
        super(StyleGuideViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(StyleGuideViewModel, self)._initialize()
        self.onSaveThemeFile = self._addCommand('onSaveThemeFile')
