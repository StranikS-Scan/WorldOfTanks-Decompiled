# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/demount_kit_info_window.py
from gui.Scaleform.daapi.view.meta.DemountKitInfoMeta import DemountKitInfoMeta
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache

class DemountKitInfoWindow(DemountKitInfoMeta):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, ctx=None):
        super(DemountKitInfoWindow, self).__init__()
        self.demountKitID = ctx.get('demountKitID')

    def onCancelClick(self):
        self.destroy()

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(DemountKitInfoWindow, self)._populate()
        demountKit = self.goodiesCache.getDemountKit(self.demountKitID)
        self.as_setDemountKitInfoS({'windowTitle': demountKit.userName,
         'name': demountKit.userName,
         'icon': demountKit.iconInfo,
         'description': demountKit.longDescription})
