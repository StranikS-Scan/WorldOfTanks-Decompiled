# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/eliteWindow/EliteWindow.py
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.meta.EliteWindowMeta import EliteWindowMeta
from gui.shared import events
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class EliteWindow(EliteWindowMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(EliteWindow, self).__init__()
        self.vehInvID = ctx['vehTypeCompDescr']

    def _populate(self):
        super(EliteWindow, self)._populate()
        self.as_setVehicleS(makeVehicleVO(self.itemsCache.items.getItemByCD(self.vehInvID)))

    def onWindowClose(self):
        self.fireEvent(events.CloseWindowEvent(events.CloseWindowEvent.ELITE_WINDOW_CLOSED))
        self.destroy()
