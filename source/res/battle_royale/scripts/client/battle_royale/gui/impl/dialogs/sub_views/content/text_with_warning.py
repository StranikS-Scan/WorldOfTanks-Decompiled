# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/dialogs/sub_views/content/text_with_warning.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.dialogs.dialog_template_utils import toString
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_royale.dialogs.sub_views.text_with_warning_view_model import TextWithWarningViewModel
from gui.impl.pub import ViewImpl
if typing.TYPE_CHECKING:
    from typing import Optional, Union
    from gui.impl.gen_utils import DynAccessor

class TextWithWarning(ViewImpl):
    __slots__ = ()

    def __init__(self, mainText, warningText=None):
        settings = ViewSettings(R.views.dialogs.sub_views.content.TextWithWarning())
        settings.model = TextWithWarningViewModel()
        settings.kwargs = {'mainText': mainText,
         'warningText': warningText}
        super(TextWithWarning, self).__init__(settings)

    def _onLoading(self, mainText, warningText, *args, **kwargs):
        super(TextWithWarning, self)._onLoading(*args, **kwargs)
        viewModel = self.getViewModel()
        viewModel.setMainText(toString(mainText))
        if warningText:
            viewModel.setWarningText(toString(warningText))

    def updateText(self, text):
        self.getViewModel().setText(toString(text))
