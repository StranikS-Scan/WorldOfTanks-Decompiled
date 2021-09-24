# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_wt_widget_model.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_base_widget_model import ModeSelectorBaseWidgetModel

class ModeSelectorWtWidgetModel(ModeSelectorBaseWidgetModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ModeSelectorWtWidgetModel, self).__init__(properties=properties, commands=commands)

    def getCurrentProgress(self):
        return self._getNumber(1)

    def setCurrentProgress(self, value):
        self._setNumber(1, value)

    def getTotalCount(self):
        return self._getNumber(2)

    def setTotalCount(self, value):
        self._setNumber(2, value)

    def getTicketCount(self):
        return self._getNumber(3)

    def setTicketCount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(ModeSelectorWtWidgetModel, self)._initialize()
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('totalCount', 0)
        self._addNumberProperty('ticketCount', 0)
