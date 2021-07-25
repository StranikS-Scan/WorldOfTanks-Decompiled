# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/sub_views/common/simple_text.py
from collections import namedtuple
import typing
from frameworks.wulf import ViewSettings
from gui.impl.dialogs.dialog_template_utils import toString
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.sub_views.image_substitution_view_model import ImageSubstitutionViewModel
from gui.impl.gen.view_models.views.dialogs.sub_views.simple_text_view_model import SimpleTextViewModel
from gui.impl.pub import ViewImpl
if typing.TYPE_CHECKING:
    from typing import Optional, List, Union
    from gui.impl.gen_utils import DynAccessor
ImageSubstitution = namedtuple('ImageSubstitution', 'resourceID placeholder marginTop marginRight marginBottom marginLeft')
ImageSubstitution.__new__.__defaults__ = (-1, None, 0, 0, 0, 0)

class SimpleText(ViewImpl):
    __slots__ = ()
    _LAYOUT_DYN_ACCESSOR = R.views.dialogs.sub_views.common.SimpleText

    def __init__(self, text, imageSubstitutions=None, layoutID=None):
        settings = ViewSettings(layoutID or self._LAYOUT_DYN_ACCESSOR())
        settings.model = SimpleTextViewModel()
        settings.kwargs = {'text': text,
         'imageSubstitutions': imageSubstitutions}
        super(SimpleText, self).__init__(settings)

    def _onLoading(self, text, imageSubstitutions, *args, **kwargs):
        super(SimpleText, self)._onLoading(*args, **kwargs)
        viewModel = self.getViewModel()
        viewModel.setText(toString(text))
        if imageSubstitutions:
            substitutionList = viewModel.getImageSubstitutions()
            for subs in imageSubstitutions:
                imageSubstitutionVM = ImageSubstitutionViewModel()
                imageSubstitutionVM.setPath(subs.resourceID)
                imageSubstitutionVM.setPlaceholder(subs.placeholder)
                imageSubstitutionVM.setMarginTop(subs.marginTop)
                imageSubstitutionVM.setMarginRight(subs.marginRight)
                imageSubstitutionVM.setMarginBottom(subs.marginBottom)
                imageSubstitutionVM.setMarginLeft(subs.marginLeft)
                substitutionList.addViewModel(imageSubstitutionVM)

    def updateText(self, text):
        self.getViewModel().setText(toString(text))
