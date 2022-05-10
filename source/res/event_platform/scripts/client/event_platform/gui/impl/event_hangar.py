# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/client/event_platform/gui/impl/event_hangar.py
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar

class EventHangar(Hangar):

    def onTestBtnClick(self):
        from helpers import dependency
        from skeletons.gui.app_loader import IAppLoader
        from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
        from gui.Scaleform.framework import ScopeTemplates
        from event_platform.gui.impl.lobby.test_view.test_view4 import TestView4
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        containerManager = app.containerManager
        containerManager.load(GuiImplViewLoadParams(TestView4.layoutID, TestView4, ScopeTemplates.DEFAULT_SCOPE))
