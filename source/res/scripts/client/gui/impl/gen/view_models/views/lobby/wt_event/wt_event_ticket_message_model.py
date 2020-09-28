# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_ticket_message_model.py
from frameworks.wulf import ViewModel

class WtEventTicketMessageModel(ViewModel):
    __slots__ = ('onOpenTasks', 'onBuyTicket')

    def __init__(self, properties=0, commands=2):
        super(WtEventTicketMessageModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(WtEventTicketMessageModel, self)._initialize()
        self.onOpenTasks = self._addCommand('onOpenTasks')
        self.onBuyTicket = self._addCommand('onBuyTicket')
