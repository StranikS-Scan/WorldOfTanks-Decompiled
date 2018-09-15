# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/event_boards_pagination.py
from gui.Scaleform.daapi.view.meta.PaginationMeta import PaginationMeta
import Event

class EventBoardsPagination(PaginationMeta):

    def __init__(self):
        super(EventBoardsPagination, self).__init__()
        self.onStepPage = Event.Event()

    def showPage(self, direction):
        self.onStepPage(direction)

    def updatePage(self, page, pagesAmount):
        self.as_setPageS('{}/{}'.format(page, pagesAmount))
        self.as_setEnabledS(page > 1, page < pagesAmount)
