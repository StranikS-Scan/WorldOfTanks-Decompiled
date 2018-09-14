# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HistoricalBattlesListWindowMeta.py
from gui.Scaleform.daapi.view.lobby.prb_windows.PrequeueWindow import PrequeueWindow

class HistoricalBattlesListWindowMeta(PrequeueWindow):

    def onBattleSelected(self, battleID):
        self._printOverrideError('onBattleSelected')

    def onVehicleSelected(self, vehicleID):
        self._printOverrideError('onVehicleSelected')

    def onPriceSelected(self, priceIndex):
        self._printOverrideError('onPriceSelected')

    def showFullDescription(self):
        self._printOverrideError('showFullDescription')

    def as_setCarouselDataS(self, items):
        return self.flashObject.as_setCarouselData(items) if self._isDAAPIInited() else None

    def as_setBattleDataS(self, data):
        return self.flashObject.as_setBattleData(data) if self._isDAAPIInited() else None

    def as_setTeamsDataS(self, teamA, teamB):
        return self.flashObject.as_setTeamsData(teamA, teamB) if self._isDAAPIInited() else None

    def as_setStatusMessageS(self, message):
        return self.flashObject.as_setStatusMessage(message) if self._isDAAPIInited() else None

    def as_selectBattleS(self, battleID):
        return self.flashObject.as_selectBattle(battleID) if self._isDAAPIInited() else None

    def as_selectVehicleS(self, intCD):
        return self.flashObject.as_selectVehicle(intCD) if self._isDAAPIInited() else None

    def as_setPricesS(self, data, selectedIndex):
        return self.flashObject.as_setPrices(data, selectedIndex) if self._isDAAPIInited() else None

    def as_setPriceInfoS(self, message):
        return self.flashObject.as_setPriceInfo(message) if self._isDAAPIInited() else None

    def as_updateFightButtonS(self, enabled, ttHeader, ttBody, showWarn):
        return self.flashObject.as_updateFightButton(enabled, ttHeader, ttBody, showWarn) if self._isDAAPIInited() else None

    def as_setCarouselEnabledS(self, value):
        return self.flashObject.as_setCarouselEnabled(value) if self._isDAAPIInited() else None

    def as_setListEnabledS(self, value):
        return self.flashObject.as_setListEnabled(value) if self._isDAAPIInited() else None

    def as_setPriceDDEnabledS(self, value):
        return self.flashObject.as_setPriceDDEnabled(value) if self._isDAAPIInited() else None

    def as_setCloseBtnEnabledS(self, value):
        return self.flashObject.as_setCloseBtnEnabled(value) if self._isDAAPIInited() else None

    def as_setDateS(self, dateText, ttHeader, ttBody):
        return self.flashObject.as_setDate(dateText, ttHeader, ttBody) if self._isDAAPIInited() else None

    def as_updateTimerS(self, headerTimeText, footerTimeText):
        return self.flashObject.as_updateTimer(headerTimeText, footerTimeText) if self._isDAAPIInited() else None
