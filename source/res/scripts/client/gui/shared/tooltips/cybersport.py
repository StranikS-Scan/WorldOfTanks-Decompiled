# Embedded file name: scripts/client/gui/shared/tooltips/cybersport.py
import BigWorld
from debug_utils import LOG_ERROR
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
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


class CybersportAutosearchToolTipData(CybersportToolTipData):

    def getDisplayableData(self, descr = None):
        if descr is not None:
            selected = [ vo_converters.makeVehicleVO(g_itemsCache.items.getItemByCD(int(item))) for item in descr ]
        else:
            selected = None
        data = vo_converters.getUnitRosterModel(selected, tuple(), False)
        data.update({'toolTipType': 'cyberSportAutoSearchVehicles'})
        return data


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

            playerID = unit._members[index]['playerID']
            vehicle = g_itemsCache.items.getItemByCD(unit._vehicles[playerID]['vehTypeCompDescr'])
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

    def getDisplayableData(self, unitIdx = None):
        if unitIdx is not None:
            unitIdx = int(unitIdx)
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            functional = dispatcher.getUnitFunctional()
            data = vo_converters.getUnitRosterData(functional, unitIdx=unitIdx)
            players = functional.getPlayers(unitIdx)
            unitComment = functional.getCensoredComment(unitIdx=unitIdx)
            commander = None
            for dbId, playerInfo in players.iteritems():
                if playerInfo.isCreator():
                    commander = playerInfo
                    break

            data['unitComment'] = unitComment
            if commander is not None:
                data['commanderName'] = commander.getFullName()
                data['commanderRating'] = BigWorld.wg_getIntegralFormat(commander.rating)
            else:
                data['commanderName'] = ''
                data['commanderRating'] = '0'
            return data
        else:
            super(CybersportUnitToolTipData, self).getDisplayableData(unitIdx)
            return


class CybersportUnitLevelToolTipData(CybersportToolTipData):

    def getDisplayableData(self, level):
        ms = i18n.makeString
        requiredLevel = level
        statusLevel = 'warning'
        description = ms(TOOLTIPS.CYBERSPORT_UNITLEVEL_DESCRIPTION)
        statusMsg = ms(TOOLTIPS.CYBERSPORT_UNITLEVEL_BODY_TOTALLEVEL, sumLevels=level)
        note = ''
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
                    reason = vo_converters.makeInvalidTotalLevelMsg(functional)
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
