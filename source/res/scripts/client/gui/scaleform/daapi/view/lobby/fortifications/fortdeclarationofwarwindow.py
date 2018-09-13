# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortDeclarationOfWarWindow.py
import BigWorld
from adisp import process
from FortifiedRegionBase import FORT_EVENT_TYPE
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortDeclarationOfWarWindowMeta import FortDeclarationOfWarWindowMeta
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.ClanCache import g_clanCache
from gui.shared.fortifications import getDirectionFromDirPos, getPositionFromDirPos
from fortified_regions import g_cache as g_fortCache
from gui.shared.fortifications.context import AttackCtx
from helpers import i18n
from helpers.i18n import makeString

class FortDeclarationOfWarWindow(AbstractWindowView, View, FortDeclarationOfWarWindowMeta, FortViewHelper):

    def __init__(self, ctx):
        super(FortDeclarationOfWarWindow, self).__init__()
        self.__direction = ctx.get('direction')
        self.__selectedDayStart, self.__selectedDayFinish = ctx.get('dateSelected', (None, None))
        self.__item = ctx.get('item')
        return None

    def _populate(self):
        super(FortDeclarationOfWarWindow, self)._populate()
        self._updateHeader()
        self._updateClansInfo()
        self._updateDirections()

    def _dispose(self):
        super(FortDeclarationOfWarWindow, self)._dispose()

    def _updateHeader(self):
        title = makeString(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_HEADER, date=BigWorld.wg_getShortDateFormat(self.__selectedDayStart), startTime=BigWorld.wg_getShortTimeFormat(self.__selectedDayStart), endTime=BigWorld.wg_getShortTimeFormat(self.__selectedDayFinish), clanName='[%s]' % self.__item.getClanAbbrev())
        description = makeString(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_DESCRIPTION)
        self.as_setupHeaderS(title, description)

    @process
    def _updateClansInfo(self):
        myEmblem = yield g_clanCache.getClanEmblemID()
        enemyClanDBID = self.__item.getClanDBID()
        textureID = 'clanWar%d' % enemyClanDBID
        enemyEmblem = yield g_clanCache.getClanEmblemTextureID(enemyClanDBID, False, textureID)
        myClan = {'id': g_clanCache.clanDBID,
         'name': g_clanCache.clanTag,
         'emblem': myEmblem}
        enemyClan = {'id': enemyClanDBID,
         'name': '[%s]' % self.__item.getClanAbbrev(),
         'emblem': enemyEmblem}
        self.as_setupClansS(myClan, enemyClan)

    def _updateDirections(self):
        directions = []
        selectedDirection = -1
        ms = makeString
        enemyBuildings = [None, None]
        for buildignID, buildingData in self.__item.getDictBuildingsBrief().iteritems():
            dir = getDirectionFromDirPos(buildingData['dirPosByte'])
            if self.__direction == dir:
                pos = getPositionFromDirPos(buildingData['dirPosByte'])
                level = buildingData['level']
                enemyBuildings[pos] = {'uid': self.UI_BUILDINGS_BIND[buildignID],
                 'progress': self._getProgress(buildignID, level),
                 'buildingLevel': level}

        enemyDirection = {'name': i18n.makeString('#fortifications:General/directionName%d' % self.__direction),
         'isMine': False,
         'buildings': enemyBuildings}
        fort = self.fortCtrl.getFort()
        for direction in range(1, g_fortCache.maxDirections + 1):
            isOpened = fort.isDirectionOpened(direction)
            isBusy = False
            availableTime = None
            name = i18n.makeString('#fortifications:General/directionName%d' % direction)
            ttHeader = ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_ITEM_NOTOPENED_TOOLTIP_HEADER)
            ttBody = ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_ITEM_NOTOPENED_TOOLTIP_BODY)
            infoMessage = ''
            dirBuildings = []
            if isOpened:
                for building in fort.getBuildingsByDirections().get(direction, ()):
                    data = None
                    if building is not None:
                        data = {'uid': self.UI_BUILDINGS_BIND[building.typeID],
                         'progress': self._getProgress(building.typeID, building.level),
                         'buildingLevel': building.level}
                    dirBuildings.append(data)

                eventTypeID = FORT_EVENT_TYPE.DIR_OPEN_ATTACKS_BASE + direction
                availableTime, _, _ = fort.events.get(eventTypeID, (None, None, None))
                if availableTime <= self.__selectedDayStart:
                    availableTime = None
                if availableTime is None:
                    attackerClanName = None

                    def filterAttacks(item):
                        if self.__selectedDayStart < item.getStartTime() < self.__selectedDayFinish and not item.isEnded():
                            return True
                        return False

                    for item in fort.getAttacks(filterFunc=filterAttacks):
                        if direction == item.getDirection():
                            isBusy = True
                            _, defClanAbbrev, _ = item.getOpponentClanInfo()
                            attackerClanName = '[%s]' % defClanAbbrev

                    if isBusy:
                        ttHeader = ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_ITEM_BUSY_TOOLTIP_HEADER)
                        ttBody = ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_ITEM_BUSY_TOOLTIP_BODY, clanName=attackerClanName)
                    else:
                        clanForAttackTag = '[%s]' % self.__item.getClanAbbrev()
                        ttHeader = ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_ITEM_ATTACK_TOOLTIP_HEADER, direction=name)
                        ttBody = ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_ITEM_ATTACK_TOOLTIP_BODY, direction=name, clanName=clanForAttackTag)
                else:
                    infoMessage = ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_DIRECTION_NOTAVAILABLE, date=BigWorld.wg_getShortDateFormat(availableTime))
                    ttHeader = ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_ITEM_NOTAVAILABLE_TOOLTIP_HEADER)
                    ttBody = ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_ITEM_NOTAVAILABLE_TOOLTIP_BODY, date=BigWorld.wg_getShortDateFormat(availableTime))
                if not isBusy and selectedDirection == -1:
                    selectedDirection = direction
            directions.append({'leftDirection': {'name': name,
                               'uid': direction,
                               'isOpened': isOpened,
                               'isBusy': isBusy or availableTime is not None,
                               'buildings': dirBuildings,
                               'ttHeader': ttHeader,
                               'ttBody': ttBody,
                               'infoMessage': infoMessage},
             'rightDirection': enemyDirection,
             'connectionIcon': RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_OFFENCE})

        self.as_setDirectionsS(directions)
        self.as_selectDirectionS(selectedDirection)
        return

    def onDirectionSelected(self):
        g_fortSoundController.playMyDirectionSelected()

    def onDirectonChosen(self, direction):
        self.__planAttack(direction)

    def onWindowClose(self):
        self.destroy()

    @process
    def __planAttack(self, direction):
        if self.__item is not None:
            result = yield self.fortProvider.sendRequest(AttackCtx(self.__item.getClanDBID(), self.__selectedDayStart, direction, self.__direction, waitingID='fort/attack'))
            if result:
                g_fortSoundController.playFortClanWarDeclared()
                self.onWindowClose()
        return
