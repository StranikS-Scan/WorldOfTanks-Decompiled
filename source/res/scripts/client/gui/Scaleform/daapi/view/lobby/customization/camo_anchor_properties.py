# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/camo_anchor_properties.py
from collections import namedtuple
from gui.shared.gui_items.customization.c11n_items import camoIconTemplate
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.daapi.view.lobby.customization.anchor_properties import AnchorDataVO
from gui.Scaleform.daapi.view.lobby.customization.shared import CAMO_SCALE_SIZE
from gui.Scaleform.daapi.view.lobby.customization.sound_constants import SOUNDS
from gui.Scaleform.daapi.view.meta.CustomizationCamoAnchorPropertiesMeta import CustomizationCamoAnchorPropertiesMeta
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
CustomizationCamoSwatchVO = namedtuple('CustomizationCamoSwatchVO', 'paletteIcon selected')
_MAX_PALETTES = 3
_PALETTE_TEXTURE = 'gui/maps/vehicles/camouflages/camo_palette_{colornum}.dds'
_DEFAULT_COLORNUM = 1
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
        dataDict = super(CustomizationCamoAnchorVO, self).asDict()
        dataDict.update({'swatchColors': self.swatchColors,
         'scaleText': self.scaleText,
         'swatchScales': self.swatchScales})
        return dataDict


class CamoAnchorProperties(CustomizationCamoAnchorPropertiesMeta):
    service = dependency.descriptor(ICustomizationService)

    def setCamoColor(self, paletteIdx):
        self._c11nView.soundManager.playInstantSound(SOUNDS.SELECT)
        self._component.palette = paletteIdx
        self.service.onOutfitChanged()

    def setCamoScale(self, scale, scaleIndex):
        self._c11nView.soundManager.playInstantSound(SOUNDS.SELECT)
        self._component.patternSize = scale
        self.service.onOutfitChanged()

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
                colornum = max(colornum, sum(((color >> 24) / 255.0 > 0 for color in palette)))

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
