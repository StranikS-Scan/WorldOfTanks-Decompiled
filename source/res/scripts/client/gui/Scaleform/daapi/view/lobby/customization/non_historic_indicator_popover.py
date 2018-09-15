# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/non_historic_indicator_popover.py
from collections import namedtuple
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import packHeaderColumnData
from gui.Scaleform.daapi.view.meta.CustomizationNonHistoricPopoverMeta import CustomizationNonHistoricPopoverMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.formatters import text_styles
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
PopoverHeaders = namedtuple('PopoverHeaders', ('tableHeaders', 'title', 'subText', 'cancelText'))
NonHistoricItems = namedtuple('NonHistoricItems', ('id', 'icon', 'countText'))

class NonHistoricItemsPopover(CustomizationNonHistoricPopoverMeta):
    service = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx=None):
        super(NonHistoricItemsPopover, self).__init__()
        data = ctx['data']
        self._nonHistoricalItems = data.items

    def onWindowClose(self):
        self.destroy()

    def remove(self, intCD):
        """ Remove an instance of the item from select tank.
        """
        self._nonHistoricalItems[:] = [ x for x in self._nonHistoricalItems if x != intCD ]
        self._assignedDP.rebuildList(self._nonHistoricalItems)
        self.service.onRemoveItems(intCD)

    def removeAll(self):
        """
        Remove item from all applicable tanks
        :return:
        """
        self.service.onRemoveItems(*self._nonHistoricalItems)
        self.destroy()

    def _populate(self):
        super(NonHistoricItemsPopover, self)._populate()
        self._assignedDP = NonHistoricItemDataProvider()
        self._assignedDP.setFlashObject(self.as_getDPS())
        self._assignedDP.rebuildList(self._nonHistoricalItems)
        self.__initHeader()

    def _dispose(self):
        self._nonHistoricalItems = []
        super(NonHistoricItemsPopover, self)._dispose()

    def __initHeader(self):
        common = {'btnHeight': 34,
         'enabled': False}
        headers = [packHeaderColumnData('itemName', 160, label=VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NONHISTORIC_TABLEHEADER_ITEM, direction='ascending', **common), packHeaderColumnData('applied', 100, label=VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NONHISTORIC_TABLEHEADER_APPLIED, direction='ascending', **common), packHeaderColumnData('button', 95, label=VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NONHISTORIC_TABLEHEADER_REMOVE, direction='ascending', **common)]
        title = text_styles.highTitle(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NONHISTORIC_TITLE_ITEMS))
        cancelText = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_NONHISTORIC_BUTTONTEXT_REMOVEFROMALL
        self.as_setHeaderDataS(PopoverHeaders(headers, title, '', cancelText)._asdict())


class NonHistoricItemDataProvider(SortableDAAPIDataProvider):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(NonHistoricItemDataProvider, self).__init__()
        self._list = []
        self._nonHistoricalItems = None
        return

    @property
    def collection(self):
        return self._list

    def emptyItem(self):
        return None

    def clear(self):
        self._list = []

    def fini(self):
        self.clear()
        self._dispose()

    def buildList(self, *args):
        self.clear()
        dataCopy = self._nonHistoricalItems[:]
        while dataCopy:
            itemIntCD = dataCopy[0]
            itemCount = dataCopy.count(itemIntCD)
            dataCopy[:] = [ x for x in dataCopy if x != itemIntCD ]
            item = self.itemsCache.items.getItemByCD(itemIntCD)
            self._list.append(self._makeVO(item, itemCount))

    def rebuildList(self, nonHistoricalItems):
        self._nonHistoricalItems = nonHistoricalItems
        self.buildList()
        self.refresh()

    def _makeVO(self, item, numItems):
        imageIcon = ''
        id = 0
        if item is not None:
            imageIcon = item.icon
            id = item.intCD
        return NonHistoricItems(id, imageIcon, 'x' + str(numItems))._asdict()
