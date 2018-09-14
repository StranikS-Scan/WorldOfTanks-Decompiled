# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/BaseRallyListView.py
from abc import abstractmethod
from gui import makeHtmlString
from gui.Scaleform.daapi.view.meta.BaseRallyListViewMeta import BaseRallyListViewMeta
from messenger.proto.events import g_messengerEvents

class BaseRallyListView(BaseRallyListViewMeta):

    def __init__(self):
        super(BaseRallyListView, self).__init__()
        self._searchDP = None
        return

    @abstractmethod
    def getPyDataProvider(self):
        return None

    def setData(self, initialData):
        pass

    def canBeClosed(self, callback):
        callback(True)

    def _populate(self):
        super(BaseRallyListView, self)._populate()
        g_messengerEvents.users.onUserActionReceived += self._onUserActionReceived
        self._searchDP = self.getPyDataProvider()
        self._searchDP.setFlashObject(self.as_getSearchDPS())

    def _dispose(self):
        if self._searchDP is not None:
            self._searchDP.fini()
            self._searchDP = None
        g_messengerEvents.users.onUserActionReceived -= self._onUserActionReceived
        super(BaseRallyListView, self)._dispose()
        return

    def getRallyDetails(self, index):
        cfdUnitID, vo = self._searchDP.getRally(index)
        return vo

    def _updateVehiclesLabel(self, minVal, maxVal):
        self.as_setVehiclesTitleS(makeHtmlString('html_templates:lobby/rally/', 'vehiclesLabel', {'minValue': minVal,
         'maxValue': maxVal}))

    def _onUserActionReceived(self, _, user):
        pass
