# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/LegionariesFilterPopover.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.meta.LegionariesFilterPopoverMeta import LegionariesFilterPopoverMeta
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView
from gui.Scaleform.framework.entities.View import View

class LegionariesFilterPopover(View, LegionariesFilterPopoverMeta, SmartPopOverView):

    def __init__(self, ctx):
        super(LegionariesFilterPopover, self).__init__()

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(LegionariesFilterPopover, self)._populate()
        data = {'winsMin': 0,
         'winsMax': 100,
         'winsCurrent': 50,
         'battlesMin': 0,
         'battlesMax': 100000,
         'battlesCurrent': 100,
         'requirements': '',
         'requirementsMaxChars': 200}
        self.as_setDataS(data)

    def _dispose(self):
        super(LegionariesFilterPopover, self)._dispose()

    def applyFilter(self, wins, battles, requirements):
        LOG_DEBUG('APPLY FILTER: ', wins, battles, requirements)
        self.destroy()
