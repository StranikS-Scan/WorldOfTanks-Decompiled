# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/points_of_interest/constants.py
from gui.Scaleform.genConsts.POI_CONSTS import POI_CONSTS
from points_of_interest_shared import PoiStatus, PoiType
POI_TYPE_UI_MAPPING = {PoiType.ARTILLERY: POI_CONSTS.POI_TYPE_ARTILLERY,
 PoiType.RECON: POI_CONSTS.POI_TYPE_RECON,
 PoiType.SMOKE: POI_CONSTS.POI_TYPE_SMOKE,
 PoiType.MINEFIELD: POI_CONSTS.POI_TYPE_MINEFIELD}
POI_STATUS_UI_MAPPING = {PoiStatus.ACTIVE: POI_CONSTS.POI_STATUS_ACTIVE,
 PoiStatus.CAPTURING: POI_CONSTS.POI_STATUS_CAPTURING,
 PoiStatus.COOLDOWN: POI_CONSTS.POI_STATUS_COOLDOWN}
