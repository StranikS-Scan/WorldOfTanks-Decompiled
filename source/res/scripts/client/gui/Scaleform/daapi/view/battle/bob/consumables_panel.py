# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bob/consumables_panel.py
import logging
from functools import partial
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel, TOOLTIP_FORMAT
from gui.Scaleform.daapi.view.battle.shared.points_of_interest.poi_helpers import getPoiTypeByEquipment
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from gui.impl.gen import R
from gui.shared.tooltips.comp7_tooltips import getPoIEquipmentDescription
from gui.shared.utils.functions import stripColorTagDescrTags
from helpers import dependency
from points_of_interest_shared import PoiType, POI_EQUIPMENT_TAG
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class BobConsumablesPanel(ConsumablesPanel):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _POI_EQUIPMENT_IDX = {PoiType.ARTILLERY: 7,
     PoiType.RECON: 8,
     PoiType.MINEFIELD: 9,
     PoiType.SMOKE: 10}
    _R_POI_EQUIPMENT_ICON = R.images.gui.maps.icons.pointsOfInterest.equipments.c_43x43

    def _getEquipmentIconPath(self, item):
        return self._R_POI_EQUIPMENT_ICON if self.__isPoiEquipment(item) else super(BobConsumablesPanel, self)._getEquipmentIconPath(item)

    def _setKeyHandler(self, item, bwKey, idx):
        if bwKey not in self._keys:
            if item.isEntityRequired():
                handler = partial(self._handleEquipmentExpanded, self._cds[idx])
            else:
                handler = partial(self._handleEquipmentPressed, self._cds[idx])
            self._keys[bwKey] = handler

    def _onEquipmentAdded(self, intCD, item):
        if self.__isPoiEquipment(item):
            self.__addPoiEquipmentSlot(intCD, item)
        else:
            super(BobConsumablesPanel, self)._onEquipmentAdded(intCD, item)

    def _updateEquipmentGlow(self, idx, item):
        if self.__isPoiEquipment(item):
            if item.becomeReady:
                self.as_setGlowS(idx, glowID=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN)
        else:
            super(BobConsumablesPanel, self)._updateEquipmentGlow(idx, item)

    def _buildEquipmentSlotTooltipText(self, item):
        return self.__buildPoIEquipmentTooltipText(item) if self.__isPoiEquipment(item) else super(BobConsumablesPanel, self)._buildEquipmentSlotTooltipText(item)

    def __addPoiEquipmentSlot(self, intCD, item):
        equipment = item.getDescriptor()
        poiType = getPoiTypeByEquipment(equipment)
        idx = self._POI_EQUIPMENT_IDX.get(poiType)
        if idx is not None:
            self._addEquipmentSlot(idx, intCD, item)
        else:
            _logger.error('Unknown PointOfInterest Type: %s', poiType)
        return

    @staticmethod
    def __isPoiEquipment(item):
        return item is not None and POI_EQUIPMENT_TAG in item.getTags()

    @staticmethod
    def __buildPoIEquipmentTooltipText(item):
        equipment = item.getDescriptor()
        description = getPoIEquipmentDescription(equipment)
        tooltip = TOOLTIP_FORMAT.format(equipment.userString, stripColorTagDescrTags(description))
        return tooltip
