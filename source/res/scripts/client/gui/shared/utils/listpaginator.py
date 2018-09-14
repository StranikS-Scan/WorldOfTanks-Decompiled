# Embedded file name: scripts/client/gui/shared/utils/ListPaginator.py
import weakref
import Event

def _getInitialOffset(count):
    return -count / 2


class ListPaginator(object):

    def __init__(self, requester, offset = 0, count = 20):
        super(ListPaginator, self).__init__()
        self._eManager = Event.EventManager()
        self.onListUpdated = Event.Event(self._eManager)
        self._offset = offset or _getInitialOffset(count)
        self._prevOffset = self._offset
        self._count = count
        self._selectedID = None
        self._requester = weakref.proxy(requester)
        return

    def init(self):
        pass

    def fini(self):
        self._eManager.clear()

    def right(self):
        self._selectedID = None
        self._prevOffset = self._offset
        self._offset += self._count
        self._request()
        return

    def left(self):
        self._selectedID = None
        self._prevOffset = self._offset
        self._offset -= self._count
        self._request()
        return

    def reset(self):
        self._selectedID = None
        self._offset = _getInitialOffset(self._count)
        self._prevOffset = self._offset
        self._request()
        return

    def revertOffset(self):
        self._offset = self._prevOffset

    def refresh(self):
        self._request()

    def setSelectedID(self, selectedID):
        self._selectedID = selectedID

    def getSelectedID(self):
        return self._selectedID

    def _request(self):
        raise NotImplementedError
