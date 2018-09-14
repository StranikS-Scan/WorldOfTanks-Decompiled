# Embedded file name: scripts/client/gui/shared/tooltips/cybersport.py
import BigWorld
from debug_utils import LOG_ERROR
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.daapi.view.lobby.rally.ActionButtonStateVO import ActionButtonStateVO
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.shared import g_itemsCache
from gui.shared.tooltips import ToolTipBaseData, TOOLTIP_TYPE
from helpers import i18n

class CybersportToolTipData(ToolTipBaseData):

    def __init__(self, context):
        super(CybersportToolTipData, self).__init__(context, TOOLTIP_TYPE.CYBER_SPORT)


class CybersportSelectedVehicleToolTipData(CybersportToolTipData):

    def getDisplayableData(self, intCD):
        if intCD is not None:
            vehicle = g_itemsCache.items.getItemByCD(int(intCD))
            return vo_converters.makeVehicleVO(vehicle)
        else:
            super(CybersportSelectedVehicleToolTipData, self).getDisplayableData(intCD)
            return


class CybersportSlotToolTipData(CybersportToolTipData):

    def getDisplayableData(self, index, unitIdx = None):
        if unitIdx is not None:
            unitIdx = int(unitIdx)
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            functional = dispatcher.getUnitFunctional()
            return vo_converters.getUnitRosterData(functional, unitIdx, int(index))
        else:
            super(CybersportSlotToolTipData, self).getDisplayableData(index, unitIdx)
            return


class CybersportSlotSelectedToolTipData(CybersportToolTipData):

    def getDisplayableData(self, index, unitIdx = None):
        if unitIdx is not None:
            unitIdx = int(unitIdx)
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            functional = dispatcher.getUnitFunctional()
            try:
                _, unit = functional.getUnit(unitIdx)
            except ValueError:
                LOG_ERROR('Unit is not exists')
                return {}

            accountDBID = unit._members[index]['accountDBID']
            vehicle = g_itemsCache.items.getItemByCD(unit._vehicles[accountDBID]['vehTypeCompDescr'])
            return vo_converters.makeVehicleVO(vehicle, functional.getRosterSettings().getLevelsRange())
        else:
            super(CybersportSlotSelectedToolTipData, self).getDisplayableData(index, unitIdx)
            return


class SquadSlotSelectedToolTipData(CybersportToolTipData):

    def getDisplayableData(self, playerID):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            functional = dispatcher.getPrbFunctional()
            playerInfo = functional.getPlayerInfo(pID=playerID)
            if playerInfo.isVehicleSpecified():
                return vo_converters.makeVehicleVO(playerInfo.getVehicle())
        super(SquadSlotSelectedToolTipData, self).getDisplayableData()
        return


class CybersportUnitToolTipData(CybersportToolTipData):

    def getDisplayableData(self, data = None):
        if data is not None:
            commanderRatingDesc = TOOLTIPS.CYBERSPORT_CAPTAIN_STATS if data.isStatic else TOOLTIPS.CYBERSPORT_COMMANDER_STATS
            return {'unitComment': data.description,
             'commanderName': data.creatorName,
             'commanderRating': data.rating,
             'commanderRatingDesc': commanderRatingDesc}
        else:
            return super(CybersportUnitToolTipData, self).getDisplayableData(data)


class CybersportUnitLevelToolTipData(CybersportToolTipData):

    def getDisplayableData(self, level):
        ms = i18n.makeString
        requiredLevel = level
        statusLevel = 'warning'
        description = ms(TOOLTIPS.CYBERSPORT_UNITLEVEL_DESCRIPTION)
        statusMsg = ms(TOOLTIPS.CYBERSPORT_UNITLEVEL_BODY_TOTALLEVEL, sumLevels=level)
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            functional = dispatcher.getUnitFunctional()
            if functional:
                requiredLevel = functional.getRosterSettings().getMinTotalLevel()
                canDoAction, restriction = functional.validateLevels()
                if restriction == UNIT_RESTRICTION.MIN_TOTAL_LEVEL:
                    statusLevel = 'critical'
                    statusMsg = ms(TOOLTIPS.CYBERSPORT_UNITLEVEL_BODY_MINTOTALLEVELERROR, sumLevels=level)
                elif restriction == UNIT_RESTRICTION.MAX_TOTAL_LEVEL:
                    statusLevel = 'critical'
                    statusMsg = ms(TOOLTIPS.CYBERSPORT_UNITLEVEL_BODY_MAXTOTALLEVELERROR, sumLevels=level)
                elif restriction == UNIT_RESTRICTION.INVALID_TOTAL_LEVEL:
                    msg, ctx = ActionButtonStateVO.getInvalidVehicleLevelsMessage(functional)
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
