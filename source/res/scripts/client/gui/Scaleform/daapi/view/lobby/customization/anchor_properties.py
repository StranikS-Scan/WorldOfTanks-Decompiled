# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/anchor_properties.py
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from gui.Scaleform.daapi.view.lobby.customization.customization_item_vo import buildCustomizationItemDataVO
from gui.Scaleform.daapi.view.meta.CustomizationAnchorPropertiesMeta import CustomizationAnchorPropertiesMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.daapi.view.lobby.customization.shared import getItemInventoryCount

class ANCHOR_TYPE(object):
    NONE = 0
    STYLE = 1
    PAINT = 2
    CAMO = 3
    DECAL = 4
    EFFECT = 5


class AnchorDataVO(object):
    __slots__ = ('name', 'desc', 'isEmpty', 'itemRendererVO')

    def __init__(self, name, desc, isEmpty, itemRendererVO):
        self.name = name
        self.desc = desc
        self.isEmpty = isEmpty
        self.itemRendererVO = itemRendererVO

    def asDict(self):
        """
        Creates a dictionary with the class' relevant data.
        :return: data object
        """
        return {'name': self.name,
         'desc': self.desc,
         'isEmpty': self.isEmpty,
         'itemRendererVO': self.itemRendererVO}


class AnchorProperties(CustomizationAnchorPropertiesMeta):
    __metaclass__ = ABCMeta
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(AnchorProperties, self).__init__()
        self._c11nView = None
        self._item = None
        self._component = None
        return

    def applyData(self, areaID, slotID, regionID):
        if slotID == GUI_ITEM_TYPE.STYLE:
            self._item = self._c11nView.getModifiedStyle()
        else:
            slot = self._c11nView.getCurrentOutfit().getContainer(areaID).slotFor(slotID)
            self._item = slot.getItem(regionID)
            self._component = slot.getComponent(regionID)
        self._extractDataFromElement()
        self._sendData(self._getData())

    def refreshData(self):
        """
        Collects property data and sends to UI
        """
        self._extractDataFromElement()
        self._sendData(self._getData())

    def _getAnchorType(self):
        return ANCHOR_TYPE.NONE

    @abstractmethod
    def _getData(self):
        return None

    def _populate(self):
        super(AnchorProperties, self)._populate()
        self._c11nView = self.app.containerManager.getContainer(ViewTypes.LOBBY_SUB).getView()

    def _dispose(self):
        self._c11nView = None
        self._item = None
        self._component = None
        super(AnchorProperties, self)._dispose()
        return

    def _extractDataFromElement(self):
        self._isEmpty = not self._item
        if not self._isEmpty:
            self._name = text_styles.highTitle(self._item.userName)
            self._desc = self.__generateDescription()
        else:
            itemTypeName = ''
            if self._getAnchorType:
                if self._getAnchorType() == ANCHOR_TYPE.STYLE:
                    itemTypeName = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_ANCHOR_STYLE
                elif self._getAnchorType() == ANCHOR_TYPE.PAINT:
                    itemTypeName = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_ANCHOR_PAINT
                elif self._getAnchorType() == ANCHOR_TYPE.CAMO:
                    itemTypeName = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_ANCHOR_CAMO
                elif self._getAnchorType() == ANCHOR_TYPE.DECAL:
                    itemTypeName = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_ANCHOR_DECAL
                elif self._getAnchorType() == ANCHOR_TYPE.EFFECT:
                    itemTypeName = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_ANCHOR_EFFECT
            self._name = text_styles.highTitle(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_EMPTYTEXT, elementType=_ms(itemTypeName)))
            self._desc = text_styles.neutral(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_EMPTYSLOT_HINT)

    def _sendData(self, data):
        self.as_setPopoverDataS(data)

    def _getItemData(self):
        """
        generates data for the carousel item renderer
        :return: carousel item renderer VO
        """
        rendererVO = None
        if self._item is not None:
            rendererVO = buildCustomizationItemDataVO(self._item, count=getItemInventoryCount(self._item) if self._item.isRentable else None)
        return rendererVO

    def __generateDescription(self):
        mapValue = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_EMPTYSLOT
        if self._item is not None:
            if self._item.isAllSeason():
                mapValue = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_STYLE_ANY
            elif self._item.isSummer():
                mapValue = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_STYLE_SUMMER
            elif self._item.isWinter():
                mapValue = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_STYLE_WINTER
            elif self._item.isDesert():
                mapValue = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_STYLE_DESERT
        desc = _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_DESCRIPTION_MAP, mapType=text_styles.stats(mapValue))
        if self._item.groupUserName:
            desc = text_styles.concatStylesToSingleLine(desc, _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_INFOTYPE_DESCRIPTION_TYPE, elementType=text_styles.stats(self._item.groupUserName)))
        return text_styles.main(desc)
