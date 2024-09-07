# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/poll/poll_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.poll.poll_view_model import PollViewModel
from gui.impl.pub import ViewImpl
from gui.shared import events, EVENT_BUS_SCOPE
from gui.wgnc import g_wgncProvider

class PollView(ViewImpl):
    __slots__ = ('__notID', '__target', '__show')

    def __init__(self, layoutID, ctx, flags=ViewFlags.LOBBY_TOP_SUB_VIEW):
        settings = ViewSettings(layoutID)
        settings.flags = flags
        settings.model = PollViewModel()
        super(PollView, self).__init__(settings)
        self.__notID = ctx.get('notID')
        self.__target = ctx.get('target')

    @property
    def viewModel(self):
        return super(PollView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PollView, self)._onLoading(*args, **kwargs)
        item = g_wgncProvider.getNotItemByName(self.__notID, self.__target.value)
        if not item:
            return
        submitButton = item.getSubmitButton()
        cancelButton = item.getCancelButton()
        with self.viewModel.transaction() as tx:
            tx.setViewType(self.__target)
            tx.setTitle(item.getTopic())
            tx.setText(item.getBody())
            if submitButton:
                tx.setSubmitButtonLbl(submitButton.label)
            if cancelButton:
                tx.setCancelButtonLbl(cancelButton.label)

    def _getEvents(self):
        return ((self.viewModel.onGoToPoll, self.__onGoToPoll), (self.viewModel.onWindowClose, self.__onWindowClose))

    def _getListeners(self):
        return ((events.WGNCShowItemEvent.CLOSE_POLL_WINDOW, self.__handlePollWindowClose, EVENT_BUS_SCOPE.LOBBY),)

    def __onGoToPoll(self):
        item = g_wgncProvider.getNotItemByName(self.__notID, self.__target.value)
        if not item:
            self.destroy()
            return
        button = item.getSubmitButton()
        if button:
            g_wgncProvider.doAction(self.__notID, button.action, self.__target.value)
        self.destroy()

    def __onWindowClose(self):
        item = g_wgncProvider.getNotItemByName(self.__notID, self.__target.value)
        if not item:
            self.destroy()
            return
        button = item.getCancelButton()
        if button:
            g_wgncProvider.doAction(self.__notID, button.action, self.__target.value)
        self.destroy()

    def __handlePollWindowClose(self, event):
        if self.__notID == event.getNotID() and self.__target.value == event.getTarget():
            self.destroy()
