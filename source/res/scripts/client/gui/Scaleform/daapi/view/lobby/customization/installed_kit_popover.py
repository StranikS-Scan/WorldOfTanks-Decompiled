# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/installed_kit_popover.py
from collections import namedtuple
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.customization.shared import SEASONS_ORDER, SEASON_TYPE_TO_NAME, TYPES_ORDER
from gui.Scaleform.daapi.view.meta.CustomizationKitPopoverMeta import CustomizationKitPopoverMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.formatters import text_styles
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType
from skeletons.gui.customization import ICustomizationService
_makeItemIconVO = lambda item: _ItemIcon(item.intCD, item.icon, item.isWide(), item.isHistorical())._asdict()
_CustomizationPopoverKitRendererVO = namedtuple('_CustomizationPopoverKitRendererVO', ('name', 'itemIcons'))
_ItemIcon = namedtuple('_ItemIcon', ('id', 'icon', 'isWide', 'isHistoric'))

class InstalledKitPopover(CustomizationKitPopoverMeta):
    service = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx=None):
        super(InstalledKitPopover, self).__init__()

    def onWindowClose(self):
        self.destroy()

    def removeCustomizationKit(self):
        appliedStyle = self.__ctx.getStyleInfo().modified
        self.__ctx.removeStyle(appliedStyle.intCD)

    def _populate(self):
        super(InstalledKitPopover, self)._populate()
        self.__ctx = self.service.getCtx()
        self.__ctx.onCacheResync += self.__update
        self.__ctx.onCustomizationSeasonChanged += self.__update
        self.__ctx.onCustomizationItemInstalled += self.__update
        self.__ctx.onCustomizationItemsRemoved += self.__update
        self.__ctx.onChangesCanceled += self.__update
        self._assignedDP = InstalledItemsPopoverDataProvider(self.__ctx)
        self._assignedDP.setFlashObject(self.as_getDPS())
        self.__update()

    def _dispose(self):
        self.__ctx.onChangesCanceled -= self.__update
        self.__ctx.onCustomizationItemsRemoved -= self.__update
        self.__ctx.onCustomizationItemInstalled -= self.__update
        self.__ctx.onCustomizationSeasonChanged -= self.__update
        self.__ctx.onCacheResync -= self.__update
        self.__ctx = None
        super(InstalledKitPopover, self)._dispose()
        return

    def __setHeader(self):
        seasonLabel = ''
        if self.__ctx.currentSeason == SeasonType.SUMMER:
            seasonLabel = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_MAPTYPE_SUMMER
        elif self.__ctx.currentSeason == SeasonType.DESERT:
            seasonLabel = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_MAPTYPE_DESERT
        elif self.__ctx.currentSeason == SeasonType.WINTER:
            seasonLabel = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_MAPTYPE_WINTER
        isClear = False
        clearMessage = ''
        if self.__ctx.currentOutfit.isEmpty():
            isClear = True
            clearMessage = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_ITEMSPOPOVER_CLEAR_MASSAGE
        self.as_showClearMessageS(isClear, text_styles.main(clearMessage))
        self.as_setHeaderS(text_styles.highTitle(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_KITPOPOVER_TITLE_ITEMS, mapType=_ms(seasonLabel))))

    def __update(self, *args):
        self._assignedDP.rebuildList()
        self.__setHeader()


class InstalledItemsPopoverDataProvider(SortableDAAPIDataProvider):
    service = dependency.descriptor(ICustomizationService)

    def __init__(self, ctx):
        super(InstalledItemsPopoverDataProvider, self).__init__()
        self._list = []
        self.__ctx = ctx

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
        for season in SEASONS_ORDER:
            items = []
            seasonUnique = set()
            appliedStyle = self.__ctx.getStyleInfo().modified
            if appliedStyle:
                outfit = appliedStyle.getOutfit(season)
                for item in outfit.items():
                    if item.intCD not in seasonUnique and not item.isHiddenInUI():
                        seasonUnique.add(item.intCD)
                        items.append(item)

                if items:
                    items.sort(key=lambda i: TYPES_ORDER.index(i.itemTypeID))
                    itemIcons = list(map(_makeItemIconVO, items))
                    seasonName = SEASON_TYPE_TO_NAME.get(season)
                    seasonTitle = makeHtmlString('html_templates:lobby/customization/PopoverSeasonName', seasonName)
                    self._list.append(_CustomizationPopoverKitRendererVO(seasonTitle, itemIcons)._asdict())

    def rebuildList(self):
        self.buildList()
        self.refresh()
