# Embedded file name: scripts/client/messenger/gui/Scaleform/data/ChannelsDataProvider.py
import BigWorld
from debug_utils import LOG_ERROR
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider
from gui.prb_control.events_dispatcher import TOOLTIP_PRB_DATA
DEFAULT_FIELDS = {'clientID': 0,
 'label': '',
 'canClose': False,
 'isNotified': False,
 'icon': None,
 'order': 0,
 'isInProgress': False,
 'isWindowOpened': False,
 'readyData': None,
 'isWindowFocused': False,
 'tooltipData': None}

class ChannelsDataProvider(DAAPIDataProvider):

    def __init__(self):
        super(ChannelsDataProvider, self).__init__()
        self.__data = {}
        self.__list = []
        self.__isInited = False

    def initGUI(self, flashObj):
        if not self.__isInited:
            self.setFlashObject(flashObj, autoPopulate=False)
            self.create()
            self.__isInited = True

    def finiGUI(self):
        if self.__isInited:
            self.destroy()
            self.__isInited = False

    def clear(self):
        self.__data.clear()
        self.__list = []

    def addItem(self, clientID, data):
        label = data['label']
        tooltipData = data.get('tooltipData', None)
        if tooltipData is None:
            tooltipData = TOOLTIP_PRB_DATA(tooltipId=None, label=label)._asdict()
        item = {'clientID': clientID,
         'label': label,
         'canClose': data.get('canClose', False),
         'isNotified': data.get('isNotified', False),
         'icon': data.get('icon'),
         'order': data.get('order', (0, BigWorld.time())),
         'isInProgress': data.get('isInProgress', False),
         'isWindowOpened': data.get('isWindowOpened', False),
         'readyData': data.get('readyData', None),
         'isWindowFocused': data.get('isWindowFocused', False),
         'tooltipData': tooltipData}
        if clientID in self.__data:
            self.__data[clientID].update(item)
        else:
            self.__data[clientID] = item
        self.buildList()
        self.refresh()
        return

    def removeItem(self, clientID):
        if clientID in self.__data:
            self.__data.pop(clientID).clear()
            self.buildList()
            self.refresh()

    def setItemField(self, clientID, key, value):
        result = False
        if clientID in self.__data:
            item = self.__data[clientID]
            if key in item:
                item[key] = value
                self.buildList()
                self.refresh()
                result = True
            else:
                LOG_ERROR('Key is invalid', key)
        return result

    def clearItemField(self, clientID, key):
        result = False
        if clientID in self.__data and key in DEFAULT_FIELDS:
            item = self.__data[clientID]
            item[key] = DEFAULT_FIELDS[key]
            self.buildList()
            self.refresh()
            result = True
        return result

    def setItemFields(self, clientID, fields):
        result = False
        if clientID in self.__data:
            item = self.__data[clientID]
            item.update(fields)
            self.buildList()
            self.refresh()
            result = True
        return result

    @property
    def collection(self):
        return self.__list

    def buildList(self):
        self.__list = sorted(self.__data.itervalues(), key=lambda item: item['order'])

    def emptyItem(self):
        return DEFAULT_FIELDS

    def refresh(self):
        if self.flashObject:
            super(ChannelsDataProvider, self).refresh()
