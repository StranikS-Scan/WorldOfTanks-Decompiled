# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/fallout/respawn.py
import BigWorld
import nations
from gui import makeHtmlString
from gui.Scaleform.daapi.view.meta.FalloutRespawnViewMeta import FalloutRespawnViewMeta
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import getClassTag, isPremium, isPremiumIGR
from gui.battle_control.controllers.respawn_ctrl import IRespawnView
from gui.shared.formatters.text_styles import standard, main, statInfo, warning
from gui.shared.gui_items.Vehicle import getIconPath
from helpers import dependency
from helpers import i18n, time_utils
from helpers.i18n import makeString
from shared_utils import findFirst
from skeletons.gui.battle_session import IBattleSessionProvider
_FLAG_ICON_TEMPLATE = '../maps/icons/battle/respawn/optimize_flags_160x100/%s.png'
_VEHICLE_TYPE_TEMPLATE = '../maps/icons/vehicleTypes/%s.png'
_VEHICLE_TYPE_ELITE_TEMPLATE = '../maps/icons/vehicleTypes/elite/%s.png'
_VEHICLE_LEVEL_TEMPLATE = '../maps/icons/levels/tank_level_%d.png'
_HTML_TEMPLATE_FALLOUT_INFO_KEY = 'html_templates:battle/falloutSingleInfo'

class FalloutRespawn(FalloutRespawnViewMeta, IRespawnView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(FalloutRespawn, self).__init__()
        self.__selectedVehicleID = None
        self.__disabled = False
        return

    def _populate(self):
        super(FalloutRespawn, self)._populate()

    def _dispose(self):
        super(FalloutRespawn, self)._dispose()

    def onVehicleSelected(self, vehicleID):
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.chooseVehicleForRespawn(int(vehicleID))
        return

    def onPostmortemBtnClick(self):
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.startPostmortem()
        return

    def start(self, vehsList, isLimited):
        mainData = self.__getMainData(isLimited)
        slotsData = self.__getSlotsData(vehsList)
        self.as_initializeComponentS(mainData, slotsData)

    def show(self, selectedID, vehsList, cooldowns):
        self.__selectedVehicleID = selectedID
        self._update(vehsList, cooldowns)

    def hide(self):
        self.__selectedVehicleID = None
        return

    def setSelectedVehicle(self, vehicleID, vehsList, cooldowns):
        self.__selectedVehicleID = vehicleID
        self._update(vehsList, cooldowns)

    def updateTimer(self, timeLeft, vehsList, cooldowns):
        mainTimer = time_utils.getTimeLeftFormat(timeLeft)
        slotsStateData = self.__getSlotsStatesData(vehsList, cooldowns)
        self.as_updateTimerS(mainTimer, slotsStateData)

    def showGasAttackInfo(self, vehsList, cooldowns):
        self.__disabled = True
        self.__selectedVehicleID = None
        slotsStatesData = self.__getSlotsStatesData(vehsList, cooldowns)
        self.as_updateS('', slotsStatesData)
        self.as_showGasAttackModeS()
        return

    def _update(self, vehsList, cooldowns):
        vehicleName = self.__getSelectedVehicle(vehsList)
        slotsStatesData = self.__getSlotsStatesData(vehsList, cooldowns)
        self.as_updateS(vehicleName, slotsStatesData)

    def __getSlotsData(self, vehsList):
        result = []
        for v in vehsList:
            nationID, _ = v.type.id
            result.append({'vehicleID': v.intCD,
             'vehicleName': self.__getVehicleName(v),
             'flagIcon': _FLAG_ICON_TEMPLATE % nations.NAMES[nationID],
             'vehicleIcon': getIconPath(v.type.name),
             'vehicleType': _VEHICLE_TYPE_TEMPLATE % getClassTag(v.type.tags),
             'isElite': False,
             'isPremium': isPremium(v.type.tags),
             'vehicleLevel': _VEHICLE_LEVEL_TEMPLATE % v.type.level})

        return result

    def __getMainData(self, isLimited):
        if isLimited:
            respawnMessage = INGAME_GUI.RESPAWNVIEW_ADDITIONALTIPLIMITED
        else:
            respawnMessage = INGAME_GUI.RESPAWNVIEW_ADDITIONALTIP
        titleMessage = makeHtmlString(_HTML_TEMPLATE_FALLOUT_INFO_KEY, 'titleMessage', {'title': i18n.makeString(INGAME_GUI.RESPAWNVIEW_TITLE),
         'message': standard(i18n.makeString(respawnMessage))})
        return {'titleMsg': titleMessage,
         'helpTextStr': self.__getHelpText(),
         'isPostmortemViewBtnEnabled': False,
         'postmortemBtnLbl': FALLOUT.INFOPANEL_GARAGE_POSTMORTEMBTNLBL}

    def __getSlotsStatesData(self, vehsList, cooldowns):
        result = []
        for v in vehsList:
            compactDescr = v.intCD
            cooldownTime = cooldowns.get(compactDescr, 0)
            cooldownStr = None
            cooldown = cooldownTime - BigWorld.serverTime()
            enabled = cooldown <= 0 and not self.__disabled
            if not enabled:
                if self.__disabled:
                    cooldownStr = i18n.makeString('#ingame_gui:respawnView/disabledLbl')
                elif cooldownTime > self.sessionProvider.shared.arenaPeriod.getEndTime():
                    cooldownStr = i18n.makeString('#ingame_gui:respawnView/destroyedLbl')
                else:
                    cooldownStr = i18n.makeString('#ingame_gui:respawnView/cooldownLbl', time=time_utils.getTimeLeftFormat(cooldown))
            result.append({'vehicleID': compactDescr,
             'selected': compactDescr == self.__selectedVehicleID,
             'enabled': enabled,
             'cooldown': cooldownStr})

        return result

    def __getHelpText(self):
        visitor = self.sessionProvider.arenaVisitor
        isSolo = visitor.isSoloTeam(avatar_getter.getPlayerTeam())
        plusStr = makeString(FALLOUT.INFOPANEL_SINGLEHELPTEXT_PLUS)
        isMultiteam = visitor.gui.isFalloutMultiTeam()
        headerStr = makeHtmlString(_HTML_TEMPLATE_FALLOUT_INFO_KEY, 'header', makeString(FALLOUT.INFOPANEL_SECRETWIN_HEAD))
        additionalBlockTemplate = makeHtmlString(_HTML_TEMPLATE_FALLOUT_INFO_KEY, 'winPoints')
        costKill, costFlags, costDamage = visitor.type.getWinPointsCosts(isSolo=isSolo, forVehicle=True)
        helpStr = ''
        if visitor.hasFlags() and len(costFlags) > 0:
            costFlags = list(costFlags)[0]
            helpStr = self.__getAdditionalBlockStr(additionalBlockTemplate, FALLOUT.INFOPANEL_SINGLEHELPTEXT_WINPOINTS_FLAGCAPTURE, warning(plusStr + str(costFlags)))
            if isMultiteam and isSolo:
                helpStr = self.__getAdditionalBlockStr(additionalBlockTemplate, FALLOUT.INFOPANEL_SINGLEHELPTEXT_WINPOINTS_FLAGDESTROY, warning(plusStr + str(costFlags)))
        helpStr += self.__getAdditionalBlockStr(additionalBlockTemplate, FALLOUT.INFOPANEL_SINGLEHELPTEXT_WINPOINTS_KILL, warning(plusStr + str(costKill)))
        damageDealt, points = costDamage
        points = warning(plusStr + str(points))
        helpStr += additionalBlockTemplate % makeString(FALLOUT.INFOPANEL_SINGLEHELPTEXT_WINPOINTS_DAMAGE, points=points, damageDealt=damageDealt)
        return headerStr + helpStr

    def __getAdditionalBlockStr(self, template, localeKey, params):
        return template % makeString(localeKey, params)

    def __getVehicleByID(self, intCD, vehicles):
        return findFirst(lambda v: v.intCD == intCD, vehicles)

    def __getSelectedVehicle(self, vehsList):
        selectedVehicle = self.__getVehicleByID(self.__selectedVehicleID, vehsList)
        vName = self.__getVehicleName(selectedVehicle)
        return main(i18n.makeString(INGAME_GUI.RESPAWNVIEW_NEXTVEHICLENAME)) + statInfo(vName)

    def __getVehicleName(self, vehicle):
        return makeHtmlString('html_templates:igr/premium-vehicle', 'name', {'vehicle': vehicle.type.shortUserString}) if isPremiumIGR(vehicle.type.tags) else vehicle.type.userString
