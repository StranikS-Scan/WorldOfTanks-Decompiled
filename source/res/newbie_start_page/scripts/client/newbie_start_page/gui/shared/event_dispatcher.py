# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: newbie_start_page/scripts/client/newbie_start_page/gui/shared/event_dispatcher.py
import typing

def showNewbieStartPage(guiCtx):
    from newbie_start_page.gui.impl.lobby.newbie_start_page.newbie_start_page_view import NewbieStartPageViewWindow
    window = NewbieStartPageViewWindow(guiCtx)
    window.load()
