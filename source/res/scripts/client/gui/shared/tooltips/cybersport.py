# Embedded file name: scripts/client/gui/shared/tooltips/cybersport.py
import BigWorld
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO, getUnitRosterModel, getUnitRosterData
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared import g_itemsCache
from gui.shared.tooltips import ToolTipBaseData, TOOLTIP_TYPE

class CybersportToolTipData(ToolTipBaseData):

    def __init__(self, context):
        super(CybersportToolTipData, self).__init__(context, TOOLTIP_TYPE.CYBER_SPORT)


class CybersportAutosearchToolTipData(CybersportToolTipData):

    def getDisplayableData(self, descr = None):
        if descr is not None:
            selected = [ makeVehicleVO(g_itemsCache.items.getItemByCD(int(item))) for item in descr ]
        else:
            selected = None
        data = getUnitRosterModel(selected, tuple(), False)
        data.update({'toolTipType': 'cyberSportAutoSearchVehicles'})
        return data


class CybersportSlotToolTipData(CybersportToolTipData):

    def getDisplayableData(self, index, unitIdx = None):
        if unitIdx is not None:
            unitIdx = int(unitIdx)
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            functional = dispatcher.getUnitFunctional()
            return getUnitRosterData(functional, unitIdx, int(index))
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
            return makeVehicleVO(vehicle)
        else:
            super(CybersportSlotSelectedToolTipData, self).getDisplayableData(index, unitIdx)
            return


class CybersportUnitToolTipData(CybersportToolTipData):

    def getDisplayableData(self, unitIdx = None):
        if unitIdx is not None:
            unitIdx = int(unitIdx)
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            functional = dispatcher.getUnitFunctional()
            data = getUnitRosterData(functional, unitIdx=unitIdx)
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
