# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/battle/grinch_help_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from grinch.gui.impl.gen.view_models.views.battle.grinch_help_view_model import GrinchHelpViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl

class GrinchHelpView(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = GrinchHelpViewModel()
        super(GrinchHelpView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(GrinchHelpView, self).getViewModel()


class GrinchHelpWindow(WindowImpl):
    __slots__ = ()

    def __init__(self):
        super(GrinchHelpWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=GrinchHelpView(R.views.grinch.battle.GrinchHelpView()))
