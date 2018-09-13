# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortClanBattleList.py
import BigWorld
from constants import PREBATTLE_TYPE
from gui.Scaleform.daapi.view.lobby.fortifications.components import sorties_dps
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.fort_text import PROMO_TITLE, MAIN_TEXT, STANDARD_TEXT, HIGH_TITLE
from gui.Scaleform.daapi.view.meta.FortClanBattleListMeta import FortClanBattleListMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.prb_control.prb_helpers import UnitListener
from gui.shared.fortifications.fort_helpers import FortListener
from gui.shared.fortifications.settings import CLIENT_FORT_STATE
from helpers import i18n, time_utils

class FortClanBattleList(FortClanBattleListMeta, FortListener, UnitListener, AppRef):

    def _populate(self):
        super(FortClanBattleList, self)._populate()
        self.unitFunctional.setPrbType(PREBATTLE_TYPE.FORT_BATTLE)
        cache = self.fortCtrl.getFortBattlesCache()
        if cache is not None:
            self._searchDP.rebuildList(cache)
        self.startFortListening()
        self.__makeData()
        return

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        self.fortCtrl.removeFortBattlesCache()
        self.stopFortListening()
        super(FortClanBattleList, self)._dispose()

    def getPyDataProvider(self):
        return sorties_dps.ClanBattlesDataProvider()

    def __makeData(self):
        result = {}
        self.__updateNextBattleCount()
        result['actionDescr'] = fort_text.getText(STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_ACTIONDESCR))
        result['titleLbl'] = fort_text.getText(PROMO_TITLE, i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_TITLELBL))
        result['descrLbl'] = fort_text.getText(MAIN_TEXT, i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_DESCRLBL))
        localeBattleCount = i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_CURRENTBTLCOUNT)
        result['battlesCountTitle'] = fort_text.getText(HIGH_TITLE, localeBattleCount)
        self.as_setClanBattleDataS(result)

    def __updateNextBattleCount(self):
        cache = self.fortCtrl.getFortBattlesCache()
        if cache is None:
            return
        else:
            currentBattlesCount = BigWorld.wg_getNiceNumberFormat(len(self._searchDP.collection))
            result = fort_text.getText(HIGH_TITLE, currentBattlesCount)
            self.as_upateClanBattlesCountS(result)
            return

    def onClientStateChanged(self, state):
        self.__updateSearchDP(state)
        if state.getStateID() != CLIENT_FORT_STATE.HAS_FORT:
            self.as_selectByIndexS(-1)
            self._searchDP.setSelectedID(None)
            self.as_setDetailsS(None)
            cache = self.fortCtrl.getFortBattlesCache()
            if cache is not None:
                cache.clearSelectedID()
        self.__updateNextBattleCount()
        return

    def onFortBattleChanged(self, cache, item):
        prevIdx = self._searchDP.getSelectedIdx()
        nextIdx = self._searchDP.updateItem(cache, item)
        if nextIdx is not None and nextIdx != -1 and nextIdx != prevIdx:
            self.as_selectByIndexS(nextIdx)
        elif nextIdx is None or nextIdx == -1:
            self.as_selectByIndexS(-1)
            self._searchDP.setSelectedID(None)
            cache.clearSelectedID()
            self.as_setDetailsS(None)
        self._searchDP.refresh()
        self.__updateNextBattleCount()
        return

    def onFortBattleRemoved(self, cache, battleID):
        dropSelection = self._searchDP.removeItem(cache, battleID)
        if dropSelection:
            self.as_selectByIndexS(-1)
            self._searchDP.setSelectedID(None)
            cache.clearSelectedID()
            self.as_setDetailsS(None)
        self.__updateNextBattleCount()
        return

    def getRallyDetails(self, index):
        vo = self._searchDP.getVO(index)
        if vo is None:
            return
        else:
            cache = self.fortCtrl.getFortBattlesCache()
            if cache is not None and not cache.isRequestInProcess:
                battleID, _ = vo['sortieID']
                if not cache.setSelectedID(battleID):
                    self.as_selectByIndexS(-1)
                    self._searchDP.setSelectedID(None)
                    cache.clearSelectedID()
                    self.as_setDetailsS(None)
                else:
                    self._searchDP.setSelectedID(battleID)
                    self.__makeDetailsData(cache.getSelectedIdx())
            return

    def __makeDetailsData(self, clientIdx):
        result = self._searchDP.getUnitVO(clientIdx)
        cache = self.fortCtrl.getFortBattlesCache()
        if cache is not None:
            item = cache.getItem(cache.getSelectedID())
            isCreated = bool(result)
            isInBattle = False
            isBegin = False
            startTimeLeft = item.getAttackTimeLeft()
            if time_utils.QUARTER_HOUR > startTimeLeft > 0:
                isBegin = True
            elif startTimeLeft == 0:
                isInBattle = True
            isCreationAvailable = not isCreated and isBegin
            result['titleText'] = fort_text.getText(fort_text.PROMO_SUB_TITLE, i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_DETAILS_CREATIONTITLE))
            result['buttonLbl'] = FORTIFICATIONS.SORTIE_LISTVIEW_CREATE
            result['isCreationAvailable'] = not isCreated
            _, clanAbbrev, _ = item.getOpponentClanInfo()
            isDefence = item.isDefence()
            localeStr = FORTIFICATIONS.FORTCLANBATTLELIST_DETAILS_TITLE if isDefence else FORTIFICATIONS.FORTCLANBATTLELIST_DETAILS_ATTACK_TITLE
            result['detailsTitle'] = fort_text.getText(HIGH_TITLE, i18n.makeString(localeStr, clanName='[%s]' % clanAbbrev))
            result['description'] = fort_text.getText(MAIN_TEXT, i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_DETAILS_DESCRIPTION, directionName=i18n.makeString('#fortifications:General/directionName%d' % item.getDirection())))
            result['isEnableBtn'] = isCreationAvailable
            if isCreationAvailable:
                descrText = FORTIFICATIONS.FORTCLANBATTLELIST_DETAILS_CREATIONDESCR
            else:
                descrText = FORTIFICATIONS.FORTCLANBATTLELIST_DETAILS_CREATIONDESCR_DISABLE
            result['descrText'] = fort_text.getText(MAIN_TEXT, i18n.makeString(descrText))
            if isCreated and isInBattle:
                for slot in result['slots']:
                    slot['canBeTaken'] = False

        self._searchDP.refresh()
        self.as_setDetailsS(result)
        return

    def __updateSearchDP(self, state):
        if state.getStateID() != CLIENT_FORT_STATE.HAS_FORT:
            self._searchDP.clear()
            self._searchDP.refresh()
            return
        else:
            cache = self.fortCtrl.getFortBattlesCache()
            if cache is not None:
                self._searchDP.rebuildList(cache)
                self.as_selectByIndexS(self._searchDP.getSelectedIdx())
            return
