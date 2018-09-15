# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCAppearManager.py
from gui.Scaleform.daapi.view.meta.BCAppearManagerMeta import BCAppearManagerMeta
from debug_utils import LOG_DEBUG
from bootcamp.BootCampEvents import g_bootcampEvents

class BCAppearManager(BCAppearManagerMeta):

    def __init__(self):
        LOG_DEBUG('BCAppearManagerPy.__init__')
        super(BCAppearManager, self).__init__()

    def onComponentTweenComplete(self, componentId):
        LOG_DEBUG('BCAppearManagerPy.onCoomponentTweenComplete', componentId)

    def onComponentPrepareAppear(self, componentId):
        LOG_DEBUG('BCAppearManagerPy.onComponentPrepareAppear', componentId)
        g_bootcampEvents.onComponentAppear(componentId)

    def _dispose(self):
        LOG_DEBUG('BCAppearManagerPy._dispose')
        super(BCAppearManager, self)._dispose()
