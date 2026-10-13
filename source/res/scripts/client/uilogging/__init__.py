# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/__init__.py
from __future__ import absolute_import

def getUILoggingConfig(manager):
    from uilogging.core.integration import UILoggingListener
    from uilogging.core.logger import UILoggingCore
    from skeletons.ui_logging import IUILoggingCore, IUILoggingListener
    uiLoggingCore = UILoggingCore()
    uiLoggingCore.init()
    manager.addInstance(IUILoggingCore, uiLoggingCore, finalizer='fini')
    listener = UILoggingListener()
    manager.addInstance(IUILoggingListener, listener, finalizer='fini')
