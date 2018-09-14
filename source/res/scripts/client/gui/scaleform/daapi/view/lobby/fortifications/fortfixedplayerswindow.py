# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortFixedPlayersWindow.py
import BigWorld
from ClientFortifiedRegion import BUILDING_UPDATE_REASON
from adisp import process
from gui import DialogsInterface, SystemMessages
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.lobby.fortifications import FortifiedWindowScopes
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.daapi.view.meta.FortFixedPlayersWindowMeta import FortFixedPlayersWindowMeta
from gui.Scaleform.genConsts.TEXT_ALIGN import TEXT_ALIGN
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.ClanCache import g_clanCache
from gui.shared.formatters import icons, text_styles
from gui.shared.fortifications.context import AttachCtx
from gui.clans.formatters import getClanRoleString
from helpers import i18n
from shared_utils import findFirst

class FortFixedPlayersWindow(FortFixedPlayersWindowMeta, FortViewHelper):

    def __init__(self, ctx = None):
        super(FortFixedPlayersWindow, self).__init__()
        self.__buildingUId = ctx.get('data', None)
        self.__buildingId = self.getBuildingIDbyUID(self.__buildingUId)
        self.__fixedPlayers = None
        self.__oldBuilding = None
        self.__isAssigned = None
        self.__currentPlayerName = BigWorld.player().name
        self.__limitFixedPlayers = None
        return

    def _populate(self):
        super(FortFixedPlayersWindow, self)._populate()
        self.startFortListening()
        self.__makeData()

    def updateWindow(self, ctx):
        self.__buildingUId = ctx.get('data', None)
        self.__buildingId = self.getBuildingIDbyUID(self.__buildingUId)
        self.__makeData()
        return

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        self.stopFortListening()
        self.__buildingId = None
        self.__buildingUId = None
        self.__fixedPlayers = None
        self.__oldBuilding = None
        self.__isAssigned = None
        self.__currentPlayerName = None
        self.__limitFixedPlayers = None
        super(FortFixedPlayersWindow, self)._dispose()
        return

    def assignToBuilding(self):
        self.__showDialog()

    @process
    def __showDialog(self):
        isOk = yield DialogsInterface.showDialog(I18nConfirmDialogMeta('fortificationFixedPlayers', messageCtx={'oldBuilding': i18n.makeString(FORTIFICATIONS.buildings_buildingname(self.__oldBuilding)),
         'newBuilding': i18n.makeString(FORTIFICATIONS.buildings_buildingname(self.__buildingUId))}, scope=FortifiedWindowScopes.ASSIGN_BUILD_DLG_SCOPE))
        if isOk:
            result = yield self.fortProvider.sendRequest(AttachCtx(self.__buildingId, waitingID='fort/building/attach'))
            if result:
                g_fortSoundController.playAttachedToBuilding()
                building = self.fortCtrl.getFort().getBuilding(self.__buildingId)
                SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_FIXEDPLAYERTOBUILDING, buildingName=building.userName, type=SystemMessages.SM_TYPE.Warning)

    def __makeData(self):
        result = {}
        building = self.fortCtrl.getFort().getBuilding(self.__buildingId)
        self.__fixedPlayers = building.attachedPlayers
        self.__oldBuilding = self.getBuildingUIDbyID(self.fortCtrl.getFort().getAssignedBuildingID(BigWorld.player().databaseID))
        self.__isAssigned = self.__buildingUId == self.__oldBuilding
        self.__limitFixedPlayers = building.typeRef.attachedPlayersLimit
        isVisible = True
        isEnabled = True
        btnTooltipData = TOOLTIPS.FORTIFICATION_FIXEDPLAYERS_ASSIGNBTNENABLED
        if self.__isAssigned:
            isVisible = False
            result['playerIsAssigned'] = text_styles.neutral(i18n.makeString(FORTIFICATIONS.FIXEDPLAYERS_HEADER_ISASSIGNED))
        if isVisible and len(self.__fixedPlayers) == self.__limitFixedPlayers:
            isEnabled = False
            btnTooltipData = TOOLTIPS.FORTIFICATION_FIXEDPLAYERS_ASSIGNBTNDISABLED
        result['windowTitle'] = i18n.makeString(FORTIFICATIONS.FIXEDPLAYERS_WINDOWTITLE, buildingName=i18n.makeString(FORTIFICATIONS.buildings_buildingname(self.__buildingUId)))
        result['buildingId'] = self.__buildingId
        result['buttonLbl'] = i18n.makeString(FORTIFICATIONS.FIXEDPLAYERS_HEADER_BTNLBL)
        result['isEnableBtn'] = isEnabled
        result['isVisibleBtn'] = isVisible
        generalToolTip = TOOLTIPS.FORTIFICATION_FIXEDPLAYERS_GENERALTOOLTIP
        if len(self.__fixedPlayers) == self.__limitFixedPlayers:
            generalToolTip = TOOLTIPS.FORTIFICATION_FIXEDPLAYERS_GENERALTOOLTIPMAXLIMIT
        result['generalTooltipData'] = generalToolTip
        result['btnTooltipData'] = btnTooltipData
        result['countLabel'] = self.__playersLabel()
        result['rosters'] = self.__makeRosters()
        result['tableHeader'] = self._createTableHeader()
        self.as_setDataS(result)

    def _createTableHeader(self):
        return [self._createTableBtnInfo(FORTIFICATIONS.CLANLISTWINDOW_TABLE_MEMBERNAME, 'userName', 140, 0, TOOLTIPS.FORTIFICATION_FIXEDPLAYERS_NIC, TEXT_ALIGN.LEFT, 'string'),
         self._createTableBtnInfo(FORTIFICATIONS.CLANLISTWINDOW_TABLE_ROLE, 'playerRoleID', 199, 1, TOOLTIPS.FORTIFICATION_FIXEDPLAYERS_FORTROLE, TEXT_ALIGN.LEFT),
         self._createTableBtnInfo(i18n.makeString(FORTIFICATIONS.FIXEDPLAYERS_LISTHEADER_FIELDWEEK, icon=icons.nut()), 'intWeekMining', 103, 2, TOOLTIPS.FORTIFICATION_FIXEDPLAYERS_WEEK, TEXT_ALIGN.RIGHT),
         self._createTableBtnInfo(i18n.makeString(FORTIFICATIONS.FIXEDPLAYERS_LISTHEADER_FIELDALLTIME, icon=icons.nut()), 'intTotalMining', 103, 2, TOOLTIPS.FORTIFICATION_FIXEDPLAYERS_ALLTIME, TEXT_ALIGN.RIGHT)]

    def _createTableBtnInfo(self, label, id, buttonWidth, sortOrder, toolTip, textAlign, sortType = 'numeric'):
        return {'label': label,
         'id': id,
         'buttonWidth': buttonWidth,
         'sortOrder': sortOrder,
         'toolTip': toolTip,
         'textAlign': textAlign,
         'sortType': sortType,
         'defaultSortDirection': 'ascending'}

    def __playersLabel(self):
        concat = ' / {0}'.format(self.__limitFixedPlayers)
        playerCount = len(self.__fixedPlayers)
        formatter = text_styles.neutral
        if playerCount == 0:
            formatter = text_styles.standard
        return ''.join((formatter(str(playerCount)), text_styles.standard(concat)))

    def __makeRosters(self):
        result = []
        for dbID in self.__fixedPlayers:
            player = findFirst(lambda m: m.getID() == dbID, g_clanCache.clanMembers)
            if player is not None:
                intTotalMining, intWeekMining = self.fortCtrl.getFort().getPlayerContributions(dbID)
                role = text_styles.standard(i18n.makeString(getClanRoleString(player.getClanRole())))
                roleID = self.CLAN_MEMBER_ROLES.index(player.getClanRole())
                vo = vo_converters.makeSimpleClanListRenderVO(player, intTotalMining, intWeekMining, role, roleID)
                result.append(vo)

        return result

    def onUpdated(self, isFullUpdate):
        self.__makeData()

    def onClanMembersListChanged(self):
        self.__makeData()

    def onBuildingChanged(self, buildingTypeID, reason, ctx = None):
        if self.__buildingId == buildingTypeID and reason == BUILDING_UPDATE_REASON.DELETED:
            self.destroy()
