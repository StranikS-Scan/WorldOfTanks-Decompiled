# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/main_view.py
from frameworks.wulf import ViewFlags, ViewSettings, ViewModel
from gui.impl.pub import ViewImpl

class MainView(ViewImpl):
    __slots__ = ()

    def __init__(self, entryID):
        super(MainView, self).__init__(ViewSettings(entryID, ViewFlags.MAIN_VIEW, ViewModel()))
