# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortBattlesListView.py
import BigWorld
from constants import PREBATTLE_TYPE
from gui.Scaleform.genConsts.TEXT_MANAGER_STYLES import TEXT_MANAGER_STYLES
from helpers import i18n, time_utils, int2roman
from gui.prb_control.prb_helpers import UnitListener
from gui.Scaleform.daapi.view.lobby.fortifications.components import sorties_dps
from gui.Scaleform.daapi.view.meta.FortClanBattleListMeta import FortClanBattleListMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.shared.fortifications.fort_helpers import FortListener
from gui.shared.fortifications.fort_seqs import BATTLE_ITEM_TYPE
from gui.shared.fortifications.settings import CLIENT_FORT_STATE, FORT_BATTLE_DIVISIONS

class FortBattlesListView(FortClanBattleListMeta, FortListener, UnitListener, AppRef):

    def __init__(self):
        super(FortBattlesListView, self).__init__()
        self.__callback = None
        return

    def onWindowClose(self):
        self.destroy()

    def getPyDataProvider(self):
        return sorties_dps.FortBattlesDataProvider()

    def onClientStateChanged(self, state):
        self.__updateSearchDP(state)
        if state.getStateID() != CLIENT_FORT_STATE.HAS_FORT:
            self.as_selectByIndexS(-1)
            self._searchDP.setSelectedID(None)
            self.as_setDetailsS(None)
            cache = self.fortCtrl.getFortBattlesCache()
            if cache is not None:
                cache.clearSelectedID()
        self.__refreshCallback()
        self.__updateNextBattleCount()
        return

    def onUnitFunctionalInited(self):
        self.unitFunctional.setPrbType(PREBATTLE_TYPE.FORT_BATTLE)

    def onFortBattleChanged(self, cache, item, battleItem):
        prevIdx = self._searchDP.getSelectedIdx()
        nextIdx = self._searchDP.updateItem(cache, item, battleItem)
        if nextIdx is not None and nextIdx != -1 and nextIdx != prevIdx:
            self.as_selectByIndexS(nextIdx)
        elif nextIdx is None or nextIdx == -1:
            self.as_selectByIndexS(-1)
            self._searchDP.setSelectedID(None)
            cache.clearSelectedID()
            self.as_setDetailsS(None)
        self._searchDP.refresh()
        self.__refreshCallback()
        self.__updateNextBattleCount()
        return

    def onFortBattleRemoved(self, cache, battleID):
        dropSelection = self._searchDP.removeItem(cache, battleID)
        if dropSelection:
            self.as_selectByIndexS(-1)
            self._searchDP.setSelectedID(None)
            cache.clearSelectedID()
            self.as_setDetailsS(None)
        self.__refreshCallback()
        self.__updateNextBattleCount()
        return

    def onFortBattleUnitReceived(self, clientIdx):
        self._searchDP.refresh()
        cache = self.fortCtrl.getFortBattlesCache()
        if cache is not None and cache.getSelectedIdx() == clientIdx:
            self.__makeDetailsData(clientIdx)
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
                    self._searchDP.refresh()
            return

    def _populate(self):
        super(FortBattlesListView, self)._populate()
        if self.unitFunctional.getPrbType() != PREBATTLE_TYPE.NONE:
            self.unitFunctional.setPrbType(PREBATTLE_TYPE.FORT_BATTLE)
        self.startFortListening()
        cache = self.fortCtrl.getFortBattlesCache()
        if cache:
            self._searchDP.rebuildList(cache)
        self.__refreshCallback()
        self.__makeData()

    def _dispose(self):
        self.__clearCallback()
        self.stopFortListening()
        super(FortBattlesListView, self)._dispose()

    def __clearCallback(self):
        if self.__callback is not None:
            BigWorld.cancelCallback(self.__callback)
            self.__callback = None
        return

    def __processCallback(self):
        cache = self.fortCtrl.getFortBattlesCache()
        if cache:
            self._searchDP.rebuildList(cache)
            self.__refreshCallback()

    def __refreshCallback(self):
        self.__clearCallback()
        cache = self.fortCtrl.getFortBattlesCache()
        if cache:
            delta = 2 * time_utils.ONE_WEEK
            for item, battleItem in cache.getIterator():
                if battleItem is not None:
                    startTimeLeft = battleItem.getRoundStartTimeLeft()
                else:
                    startTimeLeft = item.getStartTimeLeft()
                if startTimeLeft > time_utils.QUARTER_HOUR:
                    nextNotification = startTimeLeft - time_utils.QUARTER_HOUR
                else:
                    nextNotification = startTimeLeft
                if nextNotification:
                    delta = min(nextNotification, delta)

            self.__callback = BigWorld.callback(delta, self.__processCallback)
        return

    def __makeData(self):
        result = {}
        self.__updateNextBattleCount()
        result['actionDescr'] = self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_ACTIONDESCR))
        result['titleLbl'] = self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.PROMO_TITLE, i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_TITLELBL))
        result['descrLbl'] = self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_DESCRLBL))
        localeBattleCount = i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_CURRENTBTLCOUNT)
        result['battlesCountTitle'] = self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.HIGH_TITLE, localeBattleCount)
        self.as_setClanBattleDataS(result)

    def __updateNextBattleCount(self):
        cache = self.fortCtrl.getFortBattlesCache()
        if cache is None:
            return
        else:
            currentBattlesCount = BigWorld.wg_getNiceNumberFormat(len(self._searchDP.collection))
            result = self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.HIGH_TITLE, currentBattlesCount)
            self.as_upateClanBattlesCountS(result)
            return

    def __makeDetailsData(self, clientIdx):
        result = self._searchDP.getUnitVO(clientIdx)
        cache = self.fortCtrl.getFortBattlesCache()
        maxVehicleLevel = FORT_BATTLE_DIVISIONS.ABSOLUTE.maxVehicleLevel
        if cache is not None:
            item, battleItem = cache.getItem(cache.getSelectedID())
            if battleItem is not None:
                maxVehicleLevel = battleItem.additionalData.division
            isCreated = bool(result)
            isInBattle = False
            isBegin = False
            if battleItem:
                startTimeLeft = battleItem.getRoundStartTimeLeft()
            else:
                startTimeLeft = item.getStartTimeLeft()
            if time_utils.QUARTER_HOUR > startTimeLeft > 0 or item.isHot():
                isBegin = True
            elif startTimeLeft == 0 or item.isInProgress():
                isInBattle = True
            isCreationAvailable = not isCreated and isBegin
            result['titleText'] = self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.PROMO_SUB_TITLE, i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_DETAILS_CREATIONTITLE))
            result['buttonLbl'] = FORTIFICATIONS.SORTIE_LISTVIEW_CREATE
            result['isCreationAvailable'] = not isCreated
            _, clanAbbrev, _ = item.getOpponentClanInfo()
            isDefence = item.getType() == BATTLE_ITEM_TYPE.DEFENCE
            localeStr = FORTIFICATIONS.FORTCLANBATTLELIST_DETAILS_TITLE if isDefence else FORTIFICATIONS.FORTCLANBATTLELIST_DETAILS_ATTACK_TITLE
            result['detailsTitle'] = self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.HIGH_TITLE, i18n.makeString(localeStr, clanName='[%s]' % clanAbbrev))
            result['description'] = self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.FORTCLANBATTLELIST_DETAILS_DESCRIPTION, directionName=i18n.makeString('#fortifications:General/directionName%d' % item.getDirection())))
            result['isEnableBtn'] = isCreationAvailable
            if isCreationAvailable:
                descrText = FORTIFICATIONS.FORTCLANBATTLELIST_DETAILS_CREATIONDESCR
            else:
                descrText = FORTIFICATIONS.FORTCLANBATTLELIST_DETAILS_CREATIONDESCR_DISABLE
            result['descrText'] = self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.MAIN_TEXT, i18n.makeString(descrText))
            if isCreated and isInBattle:
                for slot in result['slots']:
                    slot['canBeTaken'] = False

        self.as_setDetailsS(result)
        self._updateVehiclesLabel(int2roman(1), int2roman(maxVehicleLevel))
        return

    def __updateSearchDP(self, state):
        if state.getStateID() != CLIENT_FORT_STATE.HAS_FORT:
            self.__clearCallback()
            self._searchDP.clear()
            self._searchDP.refresh()
            return
        else:
            cache = self.fortCtrl.getFortBattlesCache()
            if cache is not None:
                self.__refreshCallback()
                self._searchDP.rebuildList(cache)
                self.as_selectByIndexS(self._searchDP.getSelectedIdx())
            return
