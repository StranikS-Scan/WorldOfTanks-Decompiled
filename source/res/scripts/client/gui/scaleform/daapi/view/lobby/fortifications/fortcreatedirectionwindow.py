# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortCreateDirectionWindow.py
from fortified_regions import g_cache as g_fortCache
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortCreateDirectionWindowMeta import FortCreateDirectionWindowMeta
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.ClanCache import g_clanCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import FortEvent
from gui.shared.fortifications.context import DirectionCtx
from helpers import i18n
from shared_utils import findFirst
from gui import makeHtmlString, DialogsInterface, SystemMessages
from adisp import process

class FortCreateDirectionWindow(FortCreateDirectionWindowMeta, FortViewHelper):

    def __init__(self, _ = None):
        super(FortCreateDirectionWindow, self).__init__()

    def _populate(self):
        super(FortCreateDirectionWindow, self)._populate()
        self.startFortListening()
        self.updateData()

    def _dispose(self):
        self.stopFortListening()
        super(FortCreateDirectionWindow, self)._dispose()

    def updateData(self):
        self.updateHeader()
        self.updateList()

    def updateList(self):
        directions = []
        openedDirectionsCount = len(self.fortCtrl.getFort().getOpenedDirections())
        fightsForDirections = self.fortCtrl.getFort().getDirectionsInBattle()
        for direction in range(1, g_fortCache.maxDirections + 1):
            buildings = self.fortCtrl.getFort().getBuildingsByDirections().get(direction)
            isOpened = buildings is not None
            inBattle = direction in fightsForDirections
            canBeClosed = isOpened and not inBattle and findFirst(lambda b: b is not None, buildings) is None
            buildingsData = []
            if isOpened:
                for building in buildings:
                    data = None
                    if building is not None:
                        uid = self.getBuildingUIDbyID(building.typeID)
                        data = {'uid': uid,
                         'progress': self._getProgress(building.typeID, building.level),
                         'toolTipData': [i18n.makeString('#fortifications:Buildings/buildingName/%s' % uid), self.getCommonBuildTooltipData(building)],
                         'iconSource': FortViewHelper.getSmallIconSource(uid, building.level)}
                    buildingsData.append(data)

            directions.append({'uid': direction,
             'fullName': i18n.makeString('#fortifications:General/direction', value=i18n.makeString('#fortifications:General/directionName%d' % direction)),
             'isOpened': isOpened,
             'canBeClosed': canBeClosed,
             'closeButtonVisible': isOpened and openedDirectionsCount > 1,
             'buildings': buildingsData})

        self.as_setDirectionsS(directions)
        return

    def updateHeader(self):
        playersCount = len(g_clanCache.clanMembers)
        openedDirections = len(self.fortCtrl.getFort().getOpenedDirections())
        requiredPlayersCount = self.fortCtrl.getLimits().getDirectionsMembersRequirements().get(openedDirections + 1, 0)
        isAllDirctnsOpened = openedDirections == g_fortCache.maxDirections
        canOpenDirections = False
        ttHeader = ''
        ttDescr = ''
        if isAllDirctnsOpened:
            description = i18n.makeString(FORTIFICATIONS.FORTDIRECTIONSWINDOW_DESCR_COMPLETED)
        elif self._isFortFrozen():
            baseName = makeHtmlString('html_templates:lobby/fortifications', 'baseFrozen', {'baseName': i18n.makeString(FORTIFICATIONS.BUILDINGS_BUILDINGNAME_BASE_BUILDING) + '.'})
            description = i18n.makeString(FORTIFICATIONS.FORTDIRECTIONSWINDOW_DESCR_BASEREPAIRREQUIRE, baseName=baseName)
            ttHeader = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTCREATEDIRWIN_NEWDIRBTN_DISABLEDBYFROZEN_HEADER)
            ttDescr = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTCREATEDIRWIN_NEWDIRBTN_DISABLEDBYFROZEN_BODY)
        else:
            if playersCount >= requiredPlayersCount:
                template = 'valid'
                canOpenDirections = True
                ttHeader = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTCREATEDIRWIN_NEWDIRBTN_ENABLED_HEADER)
                ttDescr = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTCREATEDIRWIN_NEWDIRBTN_ENABLED_BODY)
            else:
                template = 'notValid'
                ttHeader = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTCREATEDIRWIN_NEWDIRBTN_DISABLEDBYPLAYERS_HEADER)
                ttDescr = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTCREATEDIRWIN_NEWDIRBTN_DISABLEDBYPLAYERS_BODY, count=requiredPlayersCount)
            playersLabel = makeHtmlString('html_templates:lobby/fortifications/playersCount', template, {'count': requiredPlayersCount})
            description = i18n.makeString(FORTIFICATIONS.FORTDIRECTIONSWINDOW_DESCR_REQUIREMENTS, count=playersLabel)
        self.as_setDescriptionS(description)
        self.as_setupButtonS(canOpenDirections, not isAllDirctnsOpened, ttHeader, ttDescr)

    def onWindowClose(self):
        self.destroy()

    def onUpdated(self, isFullUpdate):
        self.updateData()

    def onClanMembersListChanged(self):
        self.updateData()

    def openNewDirection(self):
        self.fireEvent(FortEvent(FortEvent.SWITCH_TO_MODE, ctx={'mode': FORTIFICATION_ALIASES.MODE_DIRECTIONS}), scope=EVENT_BUS_SCOPE.LOBBY)
        self.onWindowClose()

    def closeDirection(self, id):
        self.__requestToClose(id)

    @process
    def __requestToClose(self, id):
        confirmed = yield DialogsInterface.showDialog(I18nConfirmDialogMeta('fortificationCloseDirection'))
        dirID = int(id)
        if confirmed:
            result = yield self.fortProvider.sendRequest(DirectionCtx(dirID, isOpen=False, waitingID='fort/direction/close'))
            if result:
                g_fortSoundController.playDeleteDirection()
                directionName = i18n.makeString('#fortifications:General/directionName%d' % dirID)
                SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_DIRECTIONCLOSED, direction=directionName, type=SystemMessages.SM_TYPE.Warning)
