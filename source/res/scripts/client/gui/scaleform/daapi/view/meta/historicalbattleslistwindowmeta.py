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
        if self._isDAAPIInited():
            return self.flashObject.as_setCarouselData(items)

    def as_setBattleDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setBattleData(data)

    def as_setTeamsDataS(self, teamA, teamB):
        if self._isDAAPIInited():
            return self.flashObject.as_setTeamsData(teamA, teamB)

    def as_setStatusMessageS(self, message):
        if self._isDAAPIInited():
            return self.flashObject.as_setStatusMessage(message)

    def as_selectBattleS(self, battleID):
        if self._isDAAPIInited():
            return self.flashObject.as_selectBattle(battleID)

    def as_selectVehicleS(self, intCD):
        if self._isDAAPIInited():
            return self.flashObject.as_selectVehicle(intCD)

    def as_setPricesS(self, data, selectedIndex):
        if self._isDAAPIInited():
            return self.flashObject.as_setPrices(data, selectedIndex)

    def as_setPriceInfoS(self, message):
        if self._isDAAPIInited():
            return self.flashObject.as_setPriceInfo(message)

    def as_updateFightButtonS(self, enabled, ttHeader, ttBody, showWarn):
        if self._isDAAPIInited():
            return self.flashObject.as_updateFightButton(enabled, ttHeader, ttBody, showWarn)

    def as_setCarouselEnabledS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setCarouselEnabled(value)

    def as_setListEnabledS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setListEnabled(value)

    def as_setPriceDDEnabledS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setPriceDDEnabled(value)

    def as_setCloseBtnEnabledS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setCloseBtnEnabled(value)

    def as_setDateS(self, dateText, ttHeader, ttBody):
        if self._isDAAPIInited():
            return self.flashObject.as_setDate(dateText, ttHeader, ttBody)

    def as_updateTimerS(self, headerTimeText, footerTimeText):
        if self._isDAAPIInited():
            return self.flashObject.as_updateTimer(headerTimeText, footerTimeText)
