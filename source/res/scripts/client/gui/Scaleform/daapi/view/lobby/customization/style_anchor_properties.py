# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/style_anchor_properties.py
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.customization.anchor_properties import AnchorDataVO
from gui.Scaleform.daapi.view.lobby.customization.shared import SEASONS_ORDER, SEASON_TYPE_TO_NAME
from gui.Scaleform.daapi.view.meta.CustomizationStyleAnchorPropertiesMeta import CustomizationStyleAnchorPropertiesMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.formatters import text_styles
from gui.shared.gui_items.processors.vehicle import VehicleAutoStyleEquipProcessor
from gui.shared.utils import decorators
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache

class StyleDataVO(AnchorDataVO):
    __slots__ = ('seasonalItemData', 'itemText', 'itemCount', 'showProlongationCB', 'autoProlongationCBLabel', 'autoProlongationCBSelected', 'is3DStyle')

    def __init__(self, name, desc, isEmpty, itemRendererVO, seasonalItemData, itemText, itemCount, showProlongationCB, autoProlongationCBLabel, autoProlongationCBSelected, is3DStyle):
        super(StyleDataVO, self).__init__(name, desc, isEmpty, itemRendererVO)
        self.seasonalItemData = seasonalItemData
        self.itemText = itemText
        self.itemCount = itemCount
        self.showProlongationCB = showProlongationCB
        self.autoProlongationCBLabel = autoProlongationCBLabel
        self.autoProlongationCBSelected = autoProlongationCBSelected
        self.is3DStyle = is3DStyle

    def asDict(self):
        dataDict = super(StyleDataVO, self).asDict()
        dataDict['seasonalItemData'] = self.seasonalItemData
        dataDict['itemText'] = self.itemText
        dataDict['itemCount'] = self.itemCount
        dataDict['showProlongationCB'] = self.showProlongationCB
        dataDict['autoProlongationCBLabel'] = self.autoProlongationCBLabel
        dataDict['autoProlongationCBSelected'] = self.autoProlongationCBSelected
        dataDict['is3DStyle'] = self.is3DStyle
        return dataDict


class StyleAnchorProperties(CustomizationStyleAnchorPropertiesMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)

    def showRemoveConfirmation(self):
        self.service.onRemoveItems(self._item.intCD)

    def autoProlongationSwitch(self, isSelected):
        self.__setAutoRent(isSelected)

    def _getData(self):
        seasonItemData = []
        allUnique = set()
        is3DStyle = False
        if self._item:
            for season in SEASONS_ORDER:
                seasonName = SEASON_TYPE_TO_NAME.get(season)
                seasonUnique = set()
                outfit = self._item.getOutfit(season)
                items = []
                for item in outfit.items():
                    if item.intCD not in seasonUnique:
                        items.append({'image': item.icon,
                         'hasBonus': item.bonus is not None,
                         'isWide': item.isWide(),
                         'intCD': item.intCD})
                    allUnique.add(item.intCD)
                    seasonUnique.add(item.intCD)

                seasonItemData.append({'season': text_styles.main(VEHICLE_CUSTOMIZATION.getSeasonName(seasonName)),
                 'itemRendererVOs': items})

            is3DStyle = bool(self._item.modelsSet)
        itemText = _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_STYLE_ITEMS)
        name = self._name
        desc = self._desc
        itemData = self._getItemData()
        if itemData is None:
            desc = text_styles.neutral(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_EMPTYSTYLE_HINT)
            itemData = {'intCD': 0,
             'icon': RES_ICONS.MAPS_ICONS_LIBRARY_TANKITEM_BUY_TANK_POPOVER_SMALL}
        showProlongationCB = False
        autoProlongationCBLabel = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_STYLE_AUTOPROLONGATIONLABEL
        if self._item is not None and self._item.isRentable:
            showProlongationCB = True
        return StyleDataVO(name, desc, self._isEmpty, itemData, seasonItemData, itemText, len(allUnique), showProlongationCB, autoProlongationCBLabel, g_currentVehicle.item.isAutoRentStyle, is3DStyle).asDict()

    @decorators.process('loadStats')
    def __setAutoRent(self, autoRent):
        yield VehicleAutoStyleEquipProcessor(g_currentVehicle.item, autoRent).request()
