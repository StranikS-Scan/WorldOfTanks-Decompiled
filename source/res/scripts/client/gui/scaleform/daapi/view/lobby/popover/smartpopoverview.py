# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/popover/SmartPopOverView.py
from gui.Scaleform.daapi.view.meta.SmartPopOverViewMeta import SmartPopOverViewMeta
from gui.Scaleform.framework.entities.abstract.AbstractPopOverView import AbstractPopOverView

class SmartPopOverView(SmartPopOverViewMeta, AbstractPopOverView):

    def __init__(self, ctx = None):
        super(SmartPopOverView, self).__init__()

    def _populate(self):
        super(SmartPopOverView, self)._populate()
