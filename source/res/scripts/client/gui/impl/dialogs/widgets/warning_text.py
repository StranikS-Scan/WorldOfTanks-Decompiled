# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/widgets/warning_text.py
from frameworks.wulf import ViewSettings
from gui.impl.dialogs.dialog_template_utils import toString
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.sub_views.simple_text_view_model import SimpleTextViewModel
from gui.impl.pub import ViewImpl

class WarningText(ViewImpl):
    __slots__ = ('__text',)
    LAYOUT_DYN_ACCESSOR = R.views.dialogs.widgets.WarningText

    def __init__(self, text, layoutID=None):
        settings = ViewSettings(layoutID or self.LAYOUT_DYN_ACCESSOR())
        settings.model = SimpleTextViewModel()
        super(WarningText, self).__init__(settings)
        self.__text = text

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WarningText, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    def __updateViewModel(self):
        with self.viewModel.transaction() as vm:
            vm.setText(toString(self.__text))
