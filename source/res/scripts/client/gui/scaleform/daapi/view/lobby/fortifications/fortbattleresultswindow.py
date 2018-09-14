# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortBattleResultsWindow.py
import uuid
import BigWorld
import constants
from adisp import process
from constants import FORT_COMBAT_RESULT
from dossiers2.ui.achievements import ACHIEVEMENT_TYPE
from gui.shared.formatters import text_styles
from gui.Scaleform.genConsts.TEXT_ALIGN import TEXT_ALIGN
from helpers import i18n
from shared_utils import CONST_CONTAINER
from gui import SystemMessages
from gui.shared.ClanCache import g_clanCache
from gui.shared.fortifications.FortBuilding import FortBuilding
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.meta.FortBattleResultsWindowMeta import FortBattleResultsWindowMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from debug_utils import LOG_DEBUG
from dossiers2.custom.records import DB_ID_TO_RECORD
from gui.shared.gui_items.dossier import getAchievementFactory
from dossiers2.ui import achievements
from gui.shared.gui_items.dossier.achievements.MarkOnGunAchievement import MarkOnGunAchievement

class FortBattleResultsWindow(FortBattleResultsWindowMeta):

    class BATTLE_RESULT(CONST_CONTAINER):
        WIN = 'battleWin'
        DEFEAT = 'battleDefeat'
        DRAW = 'battleTie'

        @classmethod
        def getResultByWinStatus(cls, winStatus):
            if cls.isWin(winStatus):
                return cls.WIN
            if cls.isDefeat(winStatus):
                return cls.DEFEAT
            return cls.DRAW

        @classmethod
        def isWin(cls, winStatus):
            return winStatus == 1

        @classmethod
        def isDefeat(cls, winStatus):
            return winStatus == -1

        @classmethod
        def isDraw(cls, winStatus):
            return winStatus == 0

    def __init__(self, ctx):
        super(FortBattleResultsWindow, self).__init__()
        self.__data = ctx
        LOG_DEBUG('Fort battle results received', self.__data)

    def onWindowClose(self):
        self.destroy()

    def getMoreInfo(self, battleID):
        if False:
            LOG_DEBUG('show battle detail info window')
        else:
            self.as_notAvailableInfoS(battleID)
            msg = SYSTEM_MESSAGES.FORTIFICATION_ERRORS_BATTLE_INFO_NOT_AVAILABLE
            SystemMessages.g_instance.pushI18nMessage(msg, type=SystemMessages.SM_TYPE.Warning)

    @classmethod
    def _packAchievement(cls, achieve, isUnique = False):
        icons = achieve.getIcons()
        rank, i18nValue = (None, None)
        if achieve.getType() != ACHIEVEMENT_TYPE.SERIES:
            rank, i18nValue = achieve.getValue(), achieve.getI18nValue()
        specialIcon = icons.get(MarkOnGunAchievement.IT_95X85, None)
        return {'type': achieve.getName(),
         'block': achieve.getBlock(),
         'inactive': False,
         'icon': achieve.getSmallIcon() if specialIcon is None else '',
         'rank': rank,
         'localizedValue': i18nValue,
         'unic': isUnique,
         'rare': False,
         'title': achieve.getUserName(),
         'description': achieve.getUserDescription(),
         'rareIconId': None,
         'isEpic': achieve.hasRibbon(),
         'specialIcon': specialIcon,
         'customData': []}

    def __populatePersonalMedals(self):
        self.__data['dossierType'] = None
        self.__data['dossierCompDescr'] = None
        achievementsData = self.__data.get('popUpRecords', [])
        achievementsLeft = []
        achievementsRight = []
        for achievementId, achieveValue in achievementsData:
            record = DB_ID_TO_RECORD[achievementId]
            factory = getAchievementFactory(record)
            if factory is not None:
                achieve = factory.create(value=achieveValue)
                achieveData = self._packAchievement(achieve, isUnique=True)
                if achieve.getName() in achievements.FORT_BATTLE_ACHIEVES_RIGHT:
                    achievementsRight.append(achieveData)
                else:
                    achievementsLeft.append(achieveData)

        achievementsRight.sort(key=lambda k: k['isEpic'], reverse=True)
        return (achievementsLeft, achievementsRight)

    def __updateData(self):
        _ms = i18n.makeString
        winStatus = self.__data['isWinner']
        isDefence = self.__data['isDefence']
        enemyBuildingCapture = self.__data['enemyBuildingCapture']
        ourClanAbbrev = self.__data['ownClanName']
        enemyClanAbbrev = self.__data['enemyClanName']
        clanResourceDataKey = 'fortResourceLostByClan'
        resourceHeaderLabel = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_DEFRESRECEIVED_HEADER)
        byPlayerText = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_DEFRESRECEIVED_BYPLAYER)
        playerResText = BigWorld.wg_getNiceNumberFormat(self.__data.get('fortResource', 0))
        showByPlayerInfo = True
        if self.BATTLE_RESULT.isWin(winStatus):
            g_fortSoundController.playFortClanWarResult('win')
            resultText = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_WIN_HEADER)
            descriptionStartText = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_WIN_DESCRIPTION_START)
            descriptionEndText = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_WIN_DESCRIPTION_END, clanTag='[%s]' % enemyClanAbbrev, numBuildings=enemyBuildingCapture)
            clanResourceDataKey = 'fortResourceCaptureByClan'
        elif self.BATTLE_RESULT.isDefeat(winStatus):
            g_fortSoundController.playFortClanWarResult('lose')
            resultText = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_DEFEAT_HEADER)
            descriptionStartText = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_DEFEAT_DESCRIPTION_START)
            descriptionEndText = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_DEFEAT_DESCRIPTION_END, clanTag='[%s]' % enemyClanAbbrev, numBuildings=enemyBuildingCapture)
            resourceHeaderLabel = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_DEFRESLOST_HEADER)
            byPlayerText = ''
            playerResText = ''
            showByPlayerInfo = False
        else:
            g_fortSoundController.playFortClanWarResult('draw')
            resultText = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_TIE_HEADER)
            descriptionStartText = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_TIE_DESCRIPTION_START)
            descriptionEndText = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_TIE_DESCRIPTION_END, clanTag='[%s]' % enemyClanAbbrev)
        battles = []
        combatsData = self.__data.get('combats', [])
        if isDefence:
            combatsData = FORT_COMBAT_RESULT.invertCombatList(combatsData)
        for data in combatsData:
            combatResult, startTime, _, isDefendersBuilding, buildingTypeID = data
            building = FortBuilding(typeID=buildingTypeID)
            if combatResult in (constants.FORT_COMBAT_RESULT.WIN, constants.FORT_COMBAT_RESULT.TECH_WIN):
                battleResult = text_styles.success(_ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_TABLE_RESULT_WIN))
            else:
                battleResult = text_styles.error(_ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_TABLE_RESULT_DEFEAT))
            battles.append({'battleID': 0,
             'startTime': BigWorld.wg_getShortTimeFormat(startTime),
             'building': building.userName,
             'clanAbbrev': ourClanAbbrev if isDefence == isDefendersBuilding else enemyClanAbbrev,
             'result': battleResult,
             'description': '',
             'participated': True})

        achievementsLeft, achievementsRight = self.__populatePersonalMedals()
        self.as_setDataS({'windowTitle': _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_WINDOWTITLE),
         'resultText': resultText,
         'descriptionStartText': descriptionStartText,
         'descriptionEndText': descriptionEndText,
         'journalText': _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_JOURNAL),
         'defResReceivedText': resourceHeaderLabel,
         'byClanText': _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_DEFRESRECEIVED_BYCLAN),
         'byPlayerText': byPlayerText,
         'battleResult': self.BATTLE_RESULT.getResultByWinStatus(winStatus),
         'clanResText': BigWorld.wg_getNiceNumberFormat(self.__data.get(clanResourceDataKey, 0)),
         'playerResText': playerResText,
         'showByPlayerInfo': showByPlayerInfo,
         'battles': battles,
         'achievementsLeft': achievementsLeft,
         'achievementsRight': achievementsRight,
         'tableHeader': self._createTableHeader()})

    def _createTableHeader(self):
        return [self._createTableBtnInfo(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_TABLE_STARTTIME, 88), self._createTableBtnInfo(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_TABLE_BUILDING, 320), self._createTableBtnInfo(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_TABLE_RESULT, 180)]

    def _createTableBtnInfo(self, label, buttonWidth):
        return {'label': label,
         'buttonWidth': buttonWidth,
         'sortOrder': 0,
         'textAlign': TEXT_ALIGN.LEFT}

    @process
    def getClanEmblem(self):
        if 'enemyClanDBID' in self.__data:
            clanEmblem = yield g_clanCache.getClanEmblemTextureID(self.__data['enemyClanDBID'], False, str(uuid.uuid4()))
            if not self.isDisposed() and clanEmblem is not None:
                self.as_setClanEmblemS(' <IMG SRC="img://{0}" width="24" height="24" vspace="-10"/>'.format(clanEmblem))
        return

    def _populate(self):
        super(FortBattleResultsWindow, self)._populate()
        self.__updateData()
