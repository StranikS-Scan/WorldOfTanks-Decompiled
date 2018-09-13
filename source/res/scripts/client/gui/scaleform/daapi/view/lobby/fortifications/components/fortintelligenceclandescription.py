# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortIntelligenceClanDescription.py
import BigWorld
import time
from constants import FORT_MAX_ELECTED_CLANS, FORT_BUILDING_TYPE
import fortified_regions
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.meta.FortIntelligenceClanDescriptionMeta import FortIntelligenceClanDescriptionMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.events import FortEvent
from gui.shared.fortifications import getDirectionFromDirPos, getPositionFromDirPos
from gui.shared.fortifications.context import FavoriteCtx
from helpers import i18n
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.shared.ClanCache import g_clanCache
from adisp import process
from gui import makeHtmlString
from debug_utils import LOG_DEBUG
from gui.shared import events
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from helpers import time_utils
from gui.shared.utils import functions

class FortIntelligenceClanDescription(FortIntelligenceClanDescriptionMeta, FortViewHelper):

    def __init__(self):
        super(FortIntelligenceClanDescription, self).__init__()
        self.__hasResults = False
        self.__item = None
        self.__selectedDayStart, self.__selectedDayEnd = (0, 0)
        return

    def onFortPublicInfoReceived(self, hasResults):
        self.__hasResults = hasResults
        self.__item = None
        self.__makeData()
        return

    def onFortPublicInfoValidationError(self, _):
        self.__hasResults = False
        self.__item = None
        self.__selectedDayStart, self.__selectedDayEnd = (0, 0)
        self.__makeData()
        return

    def onEnemyClanCardReceived(self, card):
        self.__item = card
        _, timestamp = card.getAvailabilityFromTomorrow()
        self.__selectedDayStart, self.__selectedDayEnd = time_utils.getDayTimeBounds(timestamp)
        self.__makeData()

    def onOpenCalendar(self):
        self.fireEvent(events.ShowViewEvent(FORTIFICATION_ALIASES.FORT_CALENDAR_WINDOW_EVENT, ctx={'dateSelected': self.__selectedDayStart}), EVENT_BUS_SCOPE.LOBBY)

    def onAddRemoveFavorite(self, isAdd):
        clanID = self.__item.getClanDBID()
        self.fireEvent(FortEvent(FortEvent.ON_TOGGLE_BOOKMARK, {'clanID': clanID,
         'isAdd': isAdd}), EVENT_BUS_SCOPE.FORT)
        self.__toggleFavorite()

    def onOpenClanList(self):
        self.fireEvent(events.ShowViewEvent(FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_EVENT), EVENT_BUS_SCOPE.LOBBY)

    def onOpenClanStatistics(self):
        self.fireEvent(events.ShowViewEvent(FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_EVENT), EVENT_BUS_SCOPE.LOBBY)

    def onOpenClanCard(self):
        LOG_DEBUG('onOpenClanCard')

    def onHoverDirection(self):
        g_fortSoundController.playEnemyDirectionHover()

    def onAttackDirection(self, direction):
        g_fortSoundController.playEnemyDirectionSelected()
        selectedDayDate = time_utils.getDateTimeInUTC(self.__selectedDayStart)
        dateSelectedStart = time_utils.getTimestampFromUTC((selectedDayDate.year,
         selectedDayDate.month,
         selectedDayDate.day,
         self.__item.getStartDefHour(),
         0,
         0,
         0))
        self.fireEvent(events.ShowViewEvent(FORTIFICATION_ALIASES.FORT_DECLARATION_OF_WAR_WINDOW_EVENT, ctx={'direction': direction,
         'dateSelected': (dateSelectedStart, dateSelectedStart + time_utils.ONE_HOUR),
         'item': self.__item}), EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(FortIntelligenceClanDescription, self)._populate()
        self.startFortListening()
        self.addListener(events.CalendarEvent.DATE_SELECTED, self.__onCalendarDataSelected, EVENT_BUS_SCOPE.LOBBY)
        self.__makeData()

    def _dispose(self):
        self.__item = None
        self.removeListener(events.CalendarEvent.DATE_SELECTED, self.__onCalendarDataSelected, EVENT_BUS_SCOPE.LOBBY)
        self.stopFortListening()
        super(FortIntelligenceClanDescription, self)._dispose()
        return

    def __onCalendarDataSelected(self, event):
        timestamp = event.getTimestamp()
        if timestamp:
            self.__selectedDayStart, self.__selectedDayEnd = time_utils.getDayTimeBounds(timestamp)
            LOG_DEBUG(time.strftime('Attack time has been changed by user, %d.%m.%Y %H:%M', time_utils.getTimeStructInLocal(timestamp)))
            self.__makeData()

    @process
    def __makeData(self):
        fort = self.fortCtrl.getFort()
        data = {'numOfFavorites': len(fort.favorites),
         'favoritesLimit': FORT_MAX_ELECTED_CLANS,
         'canAttackDirection': self.fortCtrl.getPermissions().canPlanAttack(),
         'canAddToFavorite': self.fortCtrl.getPermissions().canAddToFavorite(),
         'isSelected': self.__item is not None,
         'haveResults': self.__hasResults}
        if self.__item is not None:
            clanID = self.__item.getClanDBID()
            textureID = 'clanDescription%d' % clanID
            clanEmblem = yield g_clanCache.getClanEmblemTextureID(clanID, False, textureID)

            def filterLastWeek(item):
                if self.__selectedDayStart - time_utils.ONE_WEEK < time_utils.makeLocalServerTime(item.getStartTime()) < self.__selectedDayEnd and item.isEnded():
                    return True
                return False

            def filterToday(item):
                if self.__selectedDayStart < time_utils.makeLocalServerTime(item.getStartTime()) < self.__selectedDayEnd and not item.isEnded():
                    return True
                return False

            attacksToday = self.fortCtrl.getFort().getAttacks(clanID, filterToday)
            attacksLastWeek = self.fortCtrl.getFort().getAttacks(clanID, filterLastWeek)
            defencesLastWeek = self.fortCtrl.getFort().getAttacks(clanID, filterLastWeek)
            if attacksToday or attacksLastWeek:
                attackToday = attacksToday[0] if attacksToday else None
                attackLastWeek = attacksLastWeek[-1] if attacksLastWeek else None
                defenceLastWeek = defencesLastWeek[-1] if defencesLastWeek else None
                closestAttack = attackToday or attackLastWeek
                closestAttackTime = closestAttack.getStartTime()
                warStartTime = BigWorld.wg_getShortTimeFormat(closestAttackTime)
                warFinishTime = BigWorld.wg_getShortTimeFormat(closestAttackTime + time_utils.ONE_HOUR)
                warTime = warStartTime + ' - ' + warFinishTime
                warPlannedIcon = makeHtmlString('html_templates:lobby/iconText', 'alert', {})
                warPlannedMsg = makeHtmlString('html_templates:lobby/textStyle', 'alertText', {'message': warTime})
                warPlannedTime = i18n.makeString(warPlannedIcon + ' ' + warPlannedMsg)
                isAlreadyFought = attackLastWeek is not None and (defenceLastWeek is None or defenceLastWeek.getStartTime() > attackLastWeek.getStartTime())
                data.update({'isWarDeclared': attackToday is not None,
                 'isAlreadyFought': isAlreadyFought,
                 'warPlannedDate': BigWorld.wg_getLongDateFormat(closestAttackTime),
                 'warPlannedTime': warPlannedTime,
                 'warNextAvailableDate': BigWorld.wg_getLongDateFormat(closestAttackTime + time_utils.ONE_WEEK),
                 'warPlannedTimeTT': i18n.makeString(TOOLTIPS.FORTIFICATION_FORTINTELLIGENCECLANDESCRIPTION_WARTIME, warTime=warTime)})
            militaryBaseData = self.__item.getDictBuildingsBrief()[FORT_BUILDING_TYPE.MILITARY_BASE]
            baseHP = militaryBaseData['hp']
            baseLevel = militaryBaseData['level']
            baseMaxHP = fortified_regions.g_cache.buildings[FORT_BUILDING_TYPE.MILITARY_BASE].levels[baseLevel].hp
            isFrozen = self._isBuildingFrozen(baseHP, baseMaxHP)
            MIN_VALUE = 0.01
            winPercent = self.__item.getWinPercent() * 100 if self.__item.getWinPercent() is not None else 0
            clanWinsValue = functions.roundToMinOrZero(winPercent, MIN_VALUE)
            clanAvgDefresValue = functions.roundToMinOrZero(self.__item.getResEarnCoeff(), MIN_VALUE)
            data.update({'dateSelected': BigWorld.wg_getLongDateFormat(self.__selectedDayStart),
             'selectedDayTimestamp': self.__selectedDayStart,
             'clanEmblem': clanEmblem,
             'clanTag': '[%s]' % self.__item.getClanAbbrev(),
             'clanName': self.__item.getClanName(),
             'clanInfo': self.__item.getClanMotto(),
             'clanId': clanID,
             'isFavorite': clanID in fort.favorites,
             'isFrozen': isFrozen,
             'clanBattles': {'value': BigWorld.wg_getNiceNumberFormat(self.__item.getArenasCount()) if self.__item.getArenasCount() else '--',
                             'icon': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_BATTLES40X32,
                             'ttHeader': i18n.makeString(TOOLTIPS.FORTIFICATION_FORTINTELLIGENCECLANDESCRIPTION_BATTLES_HEADER),
                             'ttBody': i18n.makeString(TOOLTIPS.FORTIFICATION_FORTINTELLIGENCECLANDESCRIPTION_BATTLES_BODY, wins=BigWorld.wg_getNiceNumberFormat(self.__item.getArenasWins()), defeats=BigWorld.wg_getNiceNumberFormat(self.__item.getArenasCount() - self.__item.getArenasWins()))},
             'clanWins': {'value': '%s%%' % BigWorld.wg_getNiceNumberFormat(clanWinsValue) if clanWinsValue else '--',
                          'icon': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_WINS40X32,
                          'ttHeader': i18n.makeString(TOOLTIPS.FORTIFICATION_FORTINTELLIGENCECLANDESCRIPTION_WINS_HEADER),
                          'ttBody': i18n.makeString(TOOLTIPS.FORTIFICATION_FORTINTELLIGENCECLANDESCRIPTION_WINS_BODY)},
             'clanAvgDefres': {'value': BigWorld.wg_getNiceNumberFormat(clanAvgDefresValue) if clanAvgDefresValue else '--',
                               'icon': RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_DEFRESRATIO40X32,
                               'ttHeader': i18n.makeString(TOOLTIPS.FORTIFICATION_FORTINTELLIGENCECLANDESCRIPTION_AVGDEFRES_HEADER),
                               'ttBody': i18n.makeString(TOOLTIPS.FORTIFICATION_FORTINTELLIGENCECLANDESCRIPTION_AVGDEFRES_BODY)},
             'directions': self.__getDirectionsData()})
        self.as_setDataS(data)
        return

    def __getDirectionsData(self):
        directions = []
        for direction in xrange(1, fortified_regions.g_cache.maxDirections + 1):
            isOpened = bool(self.__item.getDirMask() & 1 << direction)
            name = i18n.makeString('#fortifications:General/directionName%d' % direction)
            data = {'name': name,
             'uid': direction,
             'isOpened': isOpened,
             'ttHeader': i18n.makeString(FORTIFICATIONS.FORTINTELLIGENCE_CLANDESCRIPTION_DIRECTION_TOOLTIP_NOTAVAILABLE_HEADER, direction=name),
             'ttBody': i18n.makeString(FORTIFICATIONS.FORTINTELLIGENCE_CLANDESCRIPTION_DIRECTION_TOOLTIP_NOTOPENED)}
            if isOpened:
                buildings = [None, None]
                for buildingID, buildingData in self.__item.getDictBuildingsBrief().iteritems():
                    dir = getDirectionFromDirPos(buildingData['dirPosByte'])
                    if direction == dir:
                        pos = getPositionFromDirPos(buildingData['dirPosByte'])
                        level = buildingData['level']
                        buildings[pos] = {'uid': self.UI_BUILDINGS_BIND[buildingID],
                         'progress': self._getProgress(buildingID, level),
                         'buildingLevel': level}

                byMyClan = False
                attackerClanDBID = None
                attackerClanName = None
                attackTime = None
                for timestamp, dir, clanDBID, clanAbbrev in self.__item.getListScheduledAttacksAt(self.__selectedDayStart, self.__selectedDayEnd):
                    if direction == dir:
                        attackerClanDBID = clanDBID
                        byMyClan = attackerClanDBID == g_clanCache.clanDBID
                        attackerClanName = '[%s]' % clanAbbrev
                        attackTime = timestamp

                availableTime = self.__item.getDictDirOpenAttacks().get(direction)
                selectedDayDate = time_utils.getDateTimeInUTC(self.__selectedDayStart)
                dateSelectedStart = time_utils.getTimestampFromUTC((selectedDayDate.year,
                 selectedDayDate.month,
                 selectedDayDate.day,
                 self.__item.getStartDefHour(),
                 0,
                 0,
                 0))
                if availableTime <= dateSelectedStart:
                    availableTime = None
                ttHeader, ttBody, infoMessage = self.__getDirectionTooltipData(name, buildings, attackerClanDBID, attackerClanName, attackTime, availableTime)
                data.update({'buildings': buildings,
                 'isAvailable': attackerClanDBID is None and availableTime is None,
                 'infoMessage': infoMessage,
                 'ttHeader': ttHeader,
                 'ttBody': ttBody,
                 'isAttackDeclaredByMyClan': byMyClan,
                 'attackerClanID': attackerClanDBID,
                 'attackerClanName': attackerClanName})
            directions.append(data)

        return directions

    def __getDirectionTooltipData(self, dirName, buildings, attackerClanDBID, attackerClanName, attackTime, availableTime):
        infoMessage = ''
        bodyParts = []
        ms = i18n.makeString
        buildingsMsgs = []
        for building in buildings:
            if building is not None:
                extraInfo = ''
                if building['buildingLevel'] < FORTIFICATION_ALIASES.CLAN_BATTLE_BUILDING_MIN_LEVEL:
                    extraInfo = ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANDESCRIPTION_DIRECTION_TOOLTIP_BUILDINGLOWLEVEL, minLevel=fort_formatters.getTextLevel(FORTIFICATION_ALIASES.CLAN_BATTLE_BUILDING_MIN_LEVEL))
                buildingsMsgs.insert(0, ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANDESCRIPTION_DIRECTION_TOOLTIP_BUILDINGITEM, name=ms(FORTIFICATIONS.buildings_buildingname(building['uid'])), level=ms(FORTIFICATIONS.FORTMAINVIEW_HEADER_LEVELSLBL, buildLevel=str(fort_formatters.getTextLevel(building['buildingLevel']))), extraInfo=extraInfo))

        buildingsNames = '\n'.join(buildingsMsgs)
        if availableTime is not None:
            infoMessage = ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANDESCRIPTION_DIRECTION_NOTAVAILABLE, date=BigWorld.wg_getShortDateFormat(availableTime))
            bodyParts.append(ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANDESCRIPTION_DIRECTION_TOOLTIP_NOTAVAILABLE_INFO, date=BigWorld.wg_getShortDateFormat(availableTime)))
            header = ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANDESCRIPTION_DIRECTION_TOOLTIP_NOTAVAILABLE_HEADER, direction=dirName)
        elif attackerClanDBID is None:
            if buildingsNames:
                bodyParts.append(ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANDESCRIPTION_DIRECTION_TOOLTIP_BUILDINGS, buildings=buildingsNames))
            if self.fortCtrl.getPermissions().canPlanAttack():
                bodyParts.append(ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANDESCRIPTION_DIRECTION_TOOLTIP_ATTACKINFO))
                header = ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANDESCRIPTION_DIRECTION_TOOLTIP_ATTACK, direction=dirName)
            else:
                bodyParts.append(ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANDESCRIPTION_DIRECTION_TOOLTIP_NOTCOMMANDERINFO))
                header = ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANDESCRIPTION_DIRECTION_TOOLTIP_NOTCOMMANDER, direction=dirName)
        else:
            bodyParts.append(ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANDESCRIPTION_DIRECTION_TOOLTIP_BUSY_INFO, date=BigWorld.wg_getShortDateFormat(attackTime), clanName=attackerClanName))
            if buildingsNames:
                bodyParts.append(ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANDESCRIPTION_DIRECTION_TOOLTIP_BUILDINGS, buildings=buildingsNames))
            header = ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANDESCRIPTION_DIRECTION_TOOLTIP_BUSY_HEADER, direction=dirName)
        return (header, '\n'.join(bodyParts), infoMessage)

    @process
    def __toggleFavorite(self):
        if self.__item is not None:
            clanID = self.__item.getClanDBID()
            isAdd = clanID not in self.fortCtrl.getFort().favorites
            yield self.fortProvider.sendRequest(FavoriteCtx(self.__item.getClanDBID(), isAdd=isAdd, waitingID='fort/favorite/' + ('add' if isAdd else 'remove')))
        return
