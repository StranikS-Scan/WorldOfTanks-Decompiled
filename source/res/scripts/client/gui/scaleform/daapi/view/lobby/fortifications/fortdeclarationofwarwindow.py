# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortDeclarationOfWarWindow.py
import BigWorld
from adisp import process
from FortifiedRegionBase import FORT_EVENT_TYPE
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortDeclarationOfWarWindowMeta import FortDeclarationOfWarWindowMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.ClanCache import g_clanCache
from gui.shared.fortifications import getDirectionFromDirPos, getPositionFromDirPos
from fortified_regions import g_cache as g_fortCache
from gui.shared.fortifications.context import AttackCtx
from helpers import time_utils
from helpers.i18n import makeString as _ms

class FortDeclarationOfWarWindow(FortDeclarationOfWarWindowMeta, FortViewHelper):

    def __init__(self, ctx = None):
        super(FortDeclarationOfWarWindow, self).__init__()
        self.__direction = ctx.get('direction')
        self.__selectedDayStart, self.__selectedDayFinish = ctx.get('dateSelected', (None, None))
        self.__defHourStart = ctx.get('defHourStart')
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
        title = _ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_HEADER, date=BigWorld.wg_getShortDateFormat(self.__selectedDayStart), startTime=BigWorld.wg_getShortTimeFormat(self.__defHourStart), endTime=BigWorld.wg_getShortTimeFormat(self.__defHourStart + time_utils.ONE_HOUR), clanName='[%s]' % self.__item.getClanAbbrev())
        description = _ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_DESCRIPTION)
        self.as_setupHeaderS(title, description)

    @process
    def _updateClansInfo(self):
        myEmblem = yield g_clanCache.getClanEmblemID()
        enemyClanDBID = self.__item.getClanDBID()
        textureID = 'clanWar%d' % enemyClanDBID
        enemyEmblem = yield g_clanCache.getClanEmblemTextureID(enemyClanDBID, False, textureID)
        if self.isDisposed():
            return
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
        fort = self.fortCtrl.getFort()
        inProcess, _ = fort.getDefenceHourProcessing()
        isDefenceOn = fort.isDefenceHourEnabled() or inProcess
        enemyBuildings = [None, None]
        for buildingID, buildingData in self.__item.getDictBuildingsBrief().iteritems():
            dirId = getDirectionFromDirPos(buildingData['dirPosByte'])
            if self.__direction == dirId:
                pos = getPositionFromDirPos(buildingData['dirPosByte'])
                level = buildingData['level']
                if 0 <= level < 5:
                    isAvailable = False
                else:
                    isAvailable = self.__isBuildingAvailableForAttack(buildingData['hp'], g_fortCache.buildings[buildingID].levels[level].hp)
                uid = self.getBuildingUIDbyID(buildingID)
                enemyBuildings[pos] = {'uid': uid,
                 'progress': self._getProgress(buildingID, level),
                 'buildingLevel': level,
                 'isAvailable': isAvailable,
                 'iconSource': FortViewHelper.getSmallIconSource(uid, level, isDefenceOn)}

        enemyDirection = {'name': _ms('#fortifications:General/directionName%d' % self.__direction),
         'isMine': False,
         'buildings': enemyBuildings}
        for direction in range(1, g_fortCache.maxDirections + 1):
            isOpened = fort.isDirectionOpened(direction)
            isBusy = False
            availableTime = None
            name = _ms('#fortifications:General/directionName%d' % direction)
            ttHeader = _ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_ITEM_NOTOPENED_TOOLTIP_HEADER)
            ttBody = _ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_ITEM_NOTOPENED_TOOLTIP_BODY)
            infoMessage = ''
            allieBuildings = []
            if isOpened:
                for building in fort.getBuildingsByDirections().get(direction, ()):
                    data = None
                    if building is not None:
                        buildingTypeId = building.typeID
                        uid = self.getBuildingUIDbyID(buildingTypeId)
                        level = building.level
                        data = {'uid': uid,
                         'progress': self._getProgress(buildingTypeId, level),
                         'buildingLevel': level,
                         'isAvailable': self.__isBuildingAvailableForAttack(building.hp, building.levelRef.hp),
                         'iconSource': FortViewHelper.getSmallIconSource(uid, level, isDefenceOn)}
                    allieBuildings.append(data)

                eventTypeID = FORT_EVENT_TYPE.DIR_OPEN_ATTACKS_BASE + direction
                availableTime, _, _ = fort.events.get(eventTypeID, (None, None, None))
                if availableTime <= self.__selectedDayStart:
                    availableTime = None
                if availableTime is None:
                    attackerClanName = None
                    todayAttacks = fort.getAttacks(filterFunc=lambda a: self.__selectedDayStart <= a.getStartTime() <= self.__selectedDayFinish and a.isPlanned())
                    roamingDateAttacks = fort.getAttacks(filterFunc=lambda a: a.getStartTime() - time_utils.ONE_DAY < self.__defHourStart < a.getStartTime() + time_utils.ONE_DAY and a.isPlanned())
                    for attack in todayAttacks + roamingDateAttacks:
                        if direction == attack.getDirection():
                            isBusy = True
                            _, defClanAbbrev, _ = attack.getOpponentClanInfo()
                            attackerClanName = '[%s]' % defClanAbbrev

                    if isBusy:
                        ttHeader = _ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_ITEM_BUSY_TOOLTIP_HEADER)
                        ttBody = _ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_ITEM_BUSY_TOOLTIP_BODY, clanName=attackerClanName)
                    else:
                        clanForAttackTag = '[%s]' % self.__item.getClanAbbrev()
                        ttHeader = _ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_ITEM_ATTACK_TOOLTIP_HEADER, direction=name)
                        ttBody = _ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_ITEM_ATTACK_TOOLTIP_BODY, direction=name, clanName=clanForAttackTag)
                else:
                    infoMessage = _ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_DIRECTION_NOTAVAILABLE, date=BigWorld.wg_getShortDateFormat(availableTime))
                    ttHeader = _ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_ITEM_NOTAVAILABLE_TOOLTIP_HEADER)
                    ttBody = _ms(FORTIFICATIONS.FORTDECLARATIONOFWARWINDOW_ITEM_NOTAVAILABLE_TOOLTIP_BODY, date=BigWorld.wg_getShortDateFormat(availableTime))
                if not isBusy and selectedDirection == -1:
                    selectedDirection = direction
            directions.append({'leftDirection': {'name': name,
                               'uid': direction,
                               'isOpened': isOpened,
                               'isBusy': isBusy or availableTime is not None,
                               'buildings': allieBuildings,
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
            result = yield self.fortProvider.sendRequest(AttackCtx(self.__item.getClanDBID(), self.__defHourStart, direction, self.__direction, waitingID='fort/attack'))
            if result:
                g_fortSoundController.playFortClanWarDeclared()
            self.destroy()
        return

    def __isBuildingAvailableForAttack(self, currHP, totalHP):
        return currHP / float(totalHP) > 0.2
