# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/windows/window_view.py
import typing
from frameworks.wulf import View
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.development.ui.gen.view_models.demo_window.window_model import WindowModel

class WindowView(View):
    __slots__ = ()

    def __init__(self, layoutID=R.views.demoWindow, viewModelClazz=WindowModel):
        super(WindowView, self).__init__(layoutID, ViewFlags.WINDOW_DECORATOR, viewModelClazz)

    @property
    def viewModel(self):
        return super(WindowView, self).getViewModel()
