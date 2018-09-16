# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/football_evt_panel.py
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.meta.FootballEventPanelMeta import FootballEventPanelMeta
from gui.Scaleform.locale.FOOTBALL2018 import FOOTBALL2018
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from helpers.i18n import makeString

class FootballEventPanel(FootballEventPanelMeta):

    def updatePanel(self):
        if g_currentVehicle.isPresent() and g_currentVehicle.isEvent():
            footballVehicleVO = self._makeFootballVehicleVO(g_currentVehicle)
            self.as_setFootballVehiclePanelDataS(True, footballVehicleVO)
        else:
            self.as_setFootballVehiclePanelDataS(False, None)
        return

    def _makeFootballVehicleVO(self, vehicle):
        item = vehicle.item
        typeStr = item.type
        iconStr = ''
        if item.isFootball:
            descStr = ''
            if item.isFootballStriker:
                typeStr = FOOTBALL2018.SPORT_ROLE_STRIKER
                descStr = FOOTBALL2018.SPORT_ROLE_STRIKER_SHORT_DESC
                iconStr = RES_ICONS.MAPS_ICONS_FE18_CREW_ROLE_BALL_STRIKER
            elif item.isFootballMidfielder:
                typeStr = FOOTBALL2018.SPORT_ROLE_MIDFIELDER
                descStr = FOOTBALL2018.SPORT_ROLE_MIDFIELDER_SHORT_DESC
                iconStr = RES_ICONS.MAPS_ICONS_FE18_CREW_ROLE_BALL_MIDFIELDER
            elif item.isFootballDefender:
                typeStr = FOOTBALL2018.SPORT_ROLE_DEFENDER
                descStr = FOOTBALL2018.SPORT_ROLE_DEFENDER_SHORT_DESC
                iconStr = RES_ICONS.MAPS_ICONS_FE18_CREW_ROLE_BALL_DEFENDER
            typeStr = makeString(typeStr)
            descStr = makeString(descStr)
        else:
            descStr = item.getShortDesc()
        footballVehicleVO = {'tankType': typeStr,
         'tankDescription': descStr,
         'typeIcon': iconStr}
        return footballVehicleVO
