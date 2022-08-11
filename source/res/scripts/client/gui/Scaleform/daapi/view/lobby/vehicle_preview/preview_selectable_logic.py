# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/preview_selectable_logic.py
from ClientSelectableRankedObject import ClientSelectableRankedObject
from ClientSelectableWotAnniversaryObject import ClientSelectableWotAnniversaryObject
from hangar_selectable_objects import HangarSelectableLogic

class PreviewSelectableLogic(HangarSelectableLogic):

    def _filterEntity(self, entity):
        isFiltered = super(PreviewSelectableLogic, self)._filterEntity(entity)
        isFiltered = isFiltered and not isinstance(entity, (ClientSelectableRankedObject, ClientSelectableWotAnniversaryObject))
        return isFiltered
