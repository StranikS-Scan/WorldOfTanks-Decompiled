# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/popovers/style_popover.py
import typing
from CurrentVehicle import g_currentVehicle
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.customization.shared import TYPES_ORDER
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.meta.CustomizationKitPopoverMeta import CustomizationKitPopoverMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.customization.shared import SEASON_TYPE_TO_NAME, SEASONS_ORDER
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.customization import ICustomizationService

class StylePopover(CustomizationKitPopoverMeta):
    __service = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx=None):
        super(StylePopover, self).__init__(ctx)
        self.__ctx = None
        self.__style = None
        return

    def onWindowClose(self):
        self.destroy()

    def removeCustomizationKit(self):
        if self.__style is not None:
            self.__ctx.mode.removeStyle(self.__style.intCD)
            self.__style = None
        return

    def updateAutoProlongation(self):
        self.__ctx.mode.changeAutoRent()

    def _populate(self):
        super(StylePopover, self)._populate()
        self.__ctx = self.__service.getCtx()
        self.__ctx.events.onCacheResync += self.__update
        self.__ctx.events.onSeasonChanged += self.__update
        self.__ctx.events.onItemInstalled += self.__update
        self.__ctx.events.onItemsRemoved += self.__update
        self.__ctx.events.onChangesCanceled += self.__update
        self._assignedDP = StylePopoverDataProvider()
        self._assignedDP.setFlashObject(self.as_getDPS())
        self.__update()

    def _dispose(self):
        if self.__ctx.events is not None:
            self.__ctx.events.onChangesCanceled -= self.__update
            self.__ctx.events.onItemsRemoved -= self.__update
            self.__ctx.events.onItemInstalled -= self.__update
            self.__ctx.events.onSeasonChanged -= self.__update
            self.__ctx.events.onCacheResync -= self.__update
        self.__style = None
        self.__ctx = None
        super(StylePopover, self)._dispose()
        return

    def __setHeader(self):
        if self.__style is None:
            header = backport.text(R.strings.vehicle_customization.customization.kitPopover.title.items())
        else:
            header = R.strings.tooltips.vehiclePreview.boxTooltip.style.header
            header = backport.text(header(), value=self.__style.userName)
        self.as_setHeaderS(text_styles.highTitle(header))
        return

    def __setRent(self):
        if self.__style is not None and self.__style.isRentable:
            autoprolongationSelected = self.__ctx.mode.isAutoRentEnabled()
            autoprolongationEnabled = True
        else:
            autoprolongationSelected = False
            autoprolongationEnabled = False
        self.as_setAutoProlongationCheckboxSelectedS(autoprolongationSelected)
        self.as_setAutoProlongationCheckboxEnabledS(autoprolongationEnabled)
        return

    def __setClearMessage(self):
        if self.__style is None:
            isClear = True
            clearMessage = R.strings.vehicle_customization.customization.itemsPopover.message.clear
            clearMessage = backport.text(clearMessage())
        else:
            isClear = False
            clearMessage = ''
        self.as_showClearMessageS(isClear, text_styles.main(clearMessage))
        return

    def __update(self, *_):
        self.__style = self.__ctx.mode.modifiedStyle
        if self.__style is not None and self.__style.isEditable:
            self.destroy()
        self._assignedDP.rebuildList()
        self.__setHeader()
        self.__setRent()
        self.__setClearMessage()
        return


class StylePopoverDataProvider(SortableDAAPIDataProvider):
    __service = dependency.descriptor(ICustomizationService)

    def __init__(self):
        super(StylePopoverDataProvider, self).__init__()
        self._list = []
        self.__ctx = self.__service.getCtx()

    @property
    def collection(self):
        return self._list

    def emptyItem(self):
        return None

    def clear(self):
        self._list = []

    def fini(self):
        self.__ctx = None
        self.clear()
        self._dispose()
        return

    def buildList(self):
        self.clear()
        style = self.__ctx.mode.modifiedStyle
        if style is None:
            return
        else:
            vehicleDescriptor = g_currentVehicle.item.descriptor
            for season in SEASONS_ORDER:
                seasonName = SEASON_TYPE_TO_NAME[season]
                seasonTitle = makeHtmlString('html_templates:lobby/customization/StylePopoverSeasonName', seasonName, ctx={'align': 'LEFT'})
                itemsData = self.__getSeasonItemsData(style, season, vehicleDescriptor)
                seasonGroupVO = {'name': seasonTitle,
                 'itemIcons': itemsData}
                self._list.append(seasonGroupVO)

            return

    def rebuildList(self):
        self.buildList()
        self.refresh()

    def __getSeasonItemsData(self, style, season, vehicleDescriptor):
        items = set()
        nationalEmblemItem = self.__service.getItemByID(GUI_ITEM_TYPE.EMBLEM, vehicleDescriptor.type.defaultPlayerEmblemID)
        outfit = style.getOutfit(season, vehicleCD=vehicleDescriptor.makeCompactDescr())
        for intCD in outfit.items():
            item = self.__service.getItemByCD(intCD)
            if item.isHiddenInUI():
                continue
            items.add(item)

        onlyNationalEmblems = len(items) == 1 and nationalEmblemItem in items
        if items and not onlyNationalEmblems:
            sortedItems = sorted(items, key=self.__orderKey)
            itemsData = list(map(self.__makeItemDataVO, sortedItems))
        else:
            itemsData = [self.__makeItemDataVO(style)]
        return itemsData

    @staticmethod
    def __makeItemDataVO(item):
        itemDataVO = {'id': item.intCD,
         'icon': item.icon,
         'isWide': item.isWide(),
         'customizationDisplayType': item.customizationDisplayType()}
        return itemDataVO

    @staticmethod
    def __orderKey(item):
        return TYPES_ORDER.index(item.itemTypeID)
