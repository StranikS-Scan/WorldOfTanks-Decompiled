# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/camo_anchor_properties.py
from collections import namedtuple
from gui.shared.gui_items.customization.c11n_items import camoIconTemplate
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.daapi.view.lobby.customization.anchor_properties import ANCHOR_TYPE
from gui.Scaleform.daapi.view.lobby.customization.anchor_properties import AnchorDataVO
from gui.Scaleform.daapi.view.lobby.customization.shared import CAMO_SCALE_SIZE
from gui.Scaleform.daapi.view.meta.CustomizationCamoAnchorPropertiesMeta import CustomizationCamoAnchorPropertiesMeta
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.customization import ICustomizationService
CustomizationCamoSwatchVO = namedtuple('CustomizationCamoSwatchVO', 'paletteIcon selected')
_MAX_PALETTES = 3
_PALETTE_TEXTURE = 'gui/maps/vehicles/camouflages/camo_palette_{colornum}.dds'
_DEFAULT_COLORNUM = 4
_PALETTE_BACKGROUND = 'gui/maps/vehicles/camouflages/camo_palettes_back.dds'
_PALETTE_WIDTH = 78
_PALETTE_HEIGHT = 18

class CustomizationCamoAnchorVO(AnchorDataVO):
    __slots__ = ('swatchColors', 'scaleText', 'swatchScales')

    def __init__(self, name, desc, isEmpty, itemRendererVO, swatchColors, scaleText, swatchScales):
        super(CustomizationCamoAnchorVO, self).__init__(name, desc, isEmpty, itemRendererVO)
        self.swatchColors = swatchColors
        self.scaleText = scaleText
        self.swatchScales = swatchScales

    def asDict(self):
        """
        Creates a dictionary with the class' relevant data.
        :return: data object
        """
        dataDict = super(CustomizationCamoAnchorVO, self).asDict()
        dataDict.update({'swatchColors': self.swatchColors,
         'scaleText': self.scaleText,
         'swatchScales': self.swatchScales})
        return dataDict


class CamoAnchorProperties(CustomizationCamoAnchorPropertiesMeta):
    service = dependency.descriptor(ICustomizationService)

    def setCamoColor(self, paletteIdx):
        """
        sets the current camo's palette to the palette at the provided index
        :param paletteIdx:
        """
        self._component.palette = paletteIdx
        self.service.onOutfitChanged()

    def setCamoScale(self, scale, scaleIndex):
        """
        Set the scale of the camo to the provided scale value
        :param scale: the new value for camo's patternSize. represents amount of tiling to do
        :param scaleIndex: the index of the camo scale slider that was selected
        """
        self._component.patternSize = scale
        self.service.onOutfitChanged()

    def _getAnchorType(self):
        return ANCHOR_TYPE.CAMO

    def _getData(self):
        swatchColors = []
        swatchScales = []
        if self._item:
            for idx in xrange(len(CAMO_SCALE_SIZE)):
                swatchScales.append({'paletteIcon': '',
                 'label': CAMO_SCALE_SIZE[idx],
                 'selected': self._component.patternSize == idx,
                 'value': idx})

            colornum = _DEFAULT_COLORNUM
            for palette in self._item.palettes:
                colornum = sum(((color >> 24) / 255.0 > 0 for color in palette))

            for idx, palette in enumerate(self._item.palettes[:_MAX_PALETTES]):
                texture = _PALETTE_TEXTURE.format(colornum=colornum)
                icon = camoIconTemplate(texture, _PALETTE_WIDTH, _PALETTE_HEIGHT, palette, background=_PALETTE_BACKGROUND)
                swatchColors.append(CustomizationCamoSwatchVO(icon, idx == self._component.palette)._asdict())

        scaleText = VEHICLE_CUSTOMIZATION.CUSTOMIZATION_POPOVER_CAMO_SCALE
        itemData = self._getItemData()
        if itemData is None:
            itemData = {'intCD': 0,
             'icon': RES_ICONS.MAPS_ICONS_LIBRARY_TANKITEM_BUY_TANK_POPOVER_SMALL}
        return CustomizationCamoAnchorVO(self._name, self._desc, self._isEmpty, itemData, swatchColors, scaleText, swatchScales).asDict()
