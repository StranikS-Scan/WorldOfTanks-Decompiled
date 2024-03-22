# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/sub_views/icon_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.dialogs.sub_views.simple_text_view_model import SimpleTextViewModel

class IconViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(IconViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def iconLabel(self):
        return self._getViewModel(0)

    @staticmethod
    def getIconLabelType():
        return SimpleTextViewModel

    def getPath(self):
        return self._getResource(1)

    def setPath(self, value):
        self._setResource(1, value)

    def _initialize(self):
        super(IconViewModel, self)._initialize()
        self._addViewModelProperty('iconLabel', SimpleTextViewModel())
        self._addResourceProperty('path', R.invalid())
