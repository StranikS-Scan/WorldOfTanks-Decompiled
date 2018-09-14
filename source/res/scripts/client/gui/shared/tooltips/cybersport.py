# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/cybersport.py
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.daapi.view.lobby.rally.ActionButtonStateVO import ActionButtonStateVO
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.shared.tooltips import ToolTipBaseData, TOOLTIP_TYPE
from helpers import dependency
from helpers import i18n
from skeletons.gui.shared import IItemsCache

class CybersportToolTipData(ToolTipBaseData):
    """Cyber sport class for tool tip context."""
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(CybersportToolTipData, self).__init__(context, TOOLTIP_TYPE.CYBER_SPORT)


class CybersportSelectedVehicleToolTipData(CybersportToolTipData):

    def getDisplayableData(self, intCD):
        if intCD is not None:
            vehicle = self.itemsCache.items.getItemByCD(int(intCD))
            return vo_converters.makeVehicleVO(vehicle)
        else:
            super(CybersportSelectedVehicleToolTipData, self).getDisplayableData(intCD)
            return


class CybersportSlotToolTipData(CybersportToolTipData):

    def getDisplayableData(self, index, unitMgrID=None):
        if unitMgrID is not None:
            unitMgrID = int(unitMgrID)
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            entity = dispatcher.getEntity()
            return vo_converters.getUnitRosterData(entity, unitMgrID, int(index))
        else:
            super(CybersportSlotToolTipData, self).getDisplayableData(index, unitMgrID)
            return


class CybersportSlotSelectedToolTipData(CybersportToolTipData):

    def getDisplayableData(self, index, unitMgrID=None):
        if unitMgrID is not None:
            unitMgrID = int(unitMgrID)
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            entity = dispatcher.getEntity()
            _, unit = entity.getUnit(unitMgrID)
            accountDBID = unit.getMembers()[index]['accountDBID']
            vehicles = unit.getVehicles()[accountDBID]
            if vehicles:
                vehicle = self.itemsCache.items.getItemByCD(vehicles[0].vehTypeCompDescr)
                return vo_converters.makeVehicleVO(vehicle, entity.getRosterSettings().getLevelsRange())
        return super(CybersportSlotSelectedToolTipData, self).getDisplayableData(index, unitMgrID)


class SquadSlotSelectedToolTipData(CybersportToolTipData):

    def getDisplayableData(self, index, unitMgrID=None):
        if unitMgrID is not None:
            unitMgrID = int(unitMgrID)
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            entity = dispatcher.getEntity()
            _, unit = entity.getUnit(unitMgrID)
            accountDBID = unit.getMembers()[index]['accountDBID']
            vehicles = unit.getVehicles()[accountDBID]
            if vehicles:
                vehicle = self.itemsCache.items.getItemByCD(vehicles[0].vehTypeCompDescr)
                return vo_converters.makeVehicleVO(vehicle)
        super(SquadSlotSelectedToolTipData, self).getDisplayableData()
        return


class CybersportUnitToolTipData(CybersportToolTipData):

    def getDisplayableData(self, data=None):
        return {'unitComment': data.description,
         'commanderName': data.creatorName,
         'commanderRating': data.rating,
         'commanderRatingDesc': TOOLTIPS.CYBERSPORT_COMMANDER_STATS} if data is not None else super(CybersportUnitToolTipData, self).getDisplayableData(data)


class CybersportUnitLevelToolTipData(CybersportToolTipData):

    def getDisplayableData(self, level):
        ms = i18n.makeString
        requiredLevel = level
        statusLevel = 'warning'
        description = ms(TOOLTIPS.CYBERSPORT_UNITLEVEL_DESCRIPTION)
        statusMsg = ms(TOOLTIPS.CYBERSPORT_UNITLEVEL_BODY_TOTALLEVEL, sumLevels=level)
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            entity = dispatcher.getEntity()
            if entity:
                requiredLevel = entity.getRosterSettings().getMinTotalLevel()
                levelsValidation = entity.validateLevels()
                canDoAction, restriction = levelsValidation.isValid, levelsValidation.restriction
                if restriction == UNIT_RESTRICTION.MIN_TOTAL_LEVEL:
                    statusLevel = 'critical'
                    statusMsg = ms(TOOLTIPS.CYBERSPORT_UNITLEVEL_BODY_MINTOTALLEVELERROR, sumLevels=level)
                elif restriction == UNIT_RESTRICTION.MAX_TOTAL_LEVEL:
                    statusLevel = 'critical'
                    statusMsg = ms(TOOLTIPS.CYBERSPORT_UNITLEVEL_BODY_MAXTOTALLEVELERROR, sumLevels=level)
                elif restriction == UNIT_RESTRICTION.INVALID_TOTAL_LEVEL:
                    msg, ctx = ActionButtonStateVO.getInvalidVehicleLevelsMessage(levelsValidation.ctx)
                    reason = i18n.makeString(msg, **ctx)
                    description = makeHtmlString('html_templates:lobby/cyberSport/unit', 'invalidLevelDescription', {'description': description,
                     'reason': reason})
                elif canDoAction and not restriction:
                    statusLevel = 'info'
        result = {'header': ms(TOOLTIPS.CYBERSPORT_UNITLEVEL_TITLE),
         'description': description,
         'level': str(requiredLevel),
         'icon': RES_ICONS.MAPS_ICONS_LIBRARY_OKICON,
         'levelDescription': ms(TOOLTIPS.CYBERSPORT_UNITLEVEL_BODY),
         'statusMsg': statusMsg,
         'statusLevel': statusLevel}
        return result
