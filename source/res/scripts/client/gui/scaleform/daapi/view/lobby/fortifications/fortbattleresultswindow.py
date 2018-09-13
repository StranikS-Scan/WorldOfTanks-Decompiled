# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortBattleResultsWindow.py
import re
import uuid
import BigWorld
import constants
from adisp import process
from constants import FORT_COMBAT_RESULT
from debug_utils import LOG_DEBUG
from helpers import i18n
from gui import SystemMessages
from gui.shared.ClanCache import g_clanCache
from gui.shared.fortifications.FortBuilding import FortBuilding
from gui.shared.utils import CONST_CONTAINER
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.daapi.view.meta.FortBattleResultsWindowMeta import FortBattleResultsWindowMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from debug_utils import LOG_DEBUG

class FortBattleResultsWindow(View, AbstractWindowView, FortBattleResultsWindowMeta, AppRef):

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

    def __updateData(self):
        _ms = i18n.makeString
        winStatus = self.__data['isWinner']
        isDefence = self.__data['isDefence']
        enemyBuildingCapture = self.__data['enemyBuildingCapture']
        ourClanAbbrev, _ = self.__getClanInfo(self.__data['ownClanName'])
        enemyClanAbbrev, _ = self.__getClanInfo(self.__data['enemyClanName'])
        if self.BATTLE_RESULT.isWin(winStatus):
            g_fortSoundController.playFortClanWarResult('win')
            resultText = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_WIN_HEADER)
            descriptionStartText = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_WIN_DESCRIPTION_START)
            descriptionEndText = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_WIN_DESCRIPTION_END, clanTag='[%s]' % enemyClanAbbrev, numBuildings=enemyBuildingCapture)
        elif self.BATTLE_RESULT.isDefeat(winStatus):
            g_fortSoundController.playFortClanWarResult('lose')
            resultText = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_DEFEAT_HEADER)
            descriptionStartText = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_DEFEAT_DESCRIPTION_START)
            descriptionEndText = _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_DEFEAT_DESCRIPTION_END, clanTag='[%s]' % enemyClanAbbrev, numBuildings=enemyBuildingCapture)
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
                battleResult = fort_text.getText(fort_text.SUCCESS_TEXT, _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_TABLE_RESULT_WIN))
            else:
                battleResult = fort_text.getText(fort_text.SUCCESS_TEXT, _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_TABLE_RESULT_DEFEAT))
            battles.append({'battleID': 0,
             'startTime': BigWorld.wg_getShortTimeFormat(startTime),
             'building': building.userName,
             'clanAbbrev': ourClanAbbrev if isDefence == isDefendersBuilding else enemyClanAbbrev,
             'result': battleResult,
             'description': '',
             'participated': True})

        self.as_setDataS({'windowTitle': _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_WINDOWTITLE),
         'resultText': resultText,
         'descriptionStartText': descriptionStartText,
         'descriptionEndText': descriptionEndText,
         'journalText': _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_JOURNAL),
         'defResReceivedText': _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_DEFRESRECEIVED_HEADER),
         'byClanText': _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_DEFRESRECEIVED_BYCLAN),
         'byPlayerText': _ms(FORTIFICATIONS.FORTBATTLERESULTSWINDOW_DEFRESRECEIVED_BYPLAYER),
         'battleResult': self.BATTLE_RESULT.getResultByWinStatus(winStatus),
         'clanResText': BigWorld.wg_getNiceNumberFormat(self.__data.get('fortResourceByClan', 0)),
         'playerResText': BigWorld.wg_getNiceNumberFormat(self.__data.get('fortResource', 0)),
         'battles': battles})

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

    @classmethod
    def __getClanInfo(cls, enemyClanName):
        try:
            result = re.search('\\[(.+)\\]\\ *(.*)', enemyClanName)
            return (result.group(1), result.group(2))
        except:
            return ('', '')
