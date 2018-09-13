# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/eliteWindow/EliteWindow.py
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.meta.EliteWindowMeta import EliteWindowMeta
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.entities.View import View
from gui.shared import g_itemsCache

class EliteWindow(View, EliteWindowMeta, AbstractWindowView):

    def __init__(self, ctx):
        super(EliteWindow, self).__init__()
        self.vehInvID = ctx['vehTypeCompDescr']

    def _populate(self):
        super(AbstractWindowView, self)._populate()
        self.as_setVehicleS(makeVehicleVO(g_itemsCache.items.getItemByCD(self.vehInvID)))

    def onWindowClose(self):
        self.destroy()
