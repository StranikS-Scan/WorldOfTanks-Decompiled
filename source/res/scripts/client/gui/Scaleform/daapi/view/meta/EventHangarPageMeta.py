# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventHangarPageMeta.py
from gui.Scaleform.framework.entities.View import View

class EventHangarPageMeta(View):

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def closeView(self):
        self._printOverrideError('closeView')

    def onEventBannerClick(self):
        self._printOverrideError('onEventBannerClick')

    def onGeneralSelected(self, id):
        self._printOverrideError('onGeneralSelected')

    def onGeneralBuy(self, id):
        self._printOverrideError('onGeneralBuy')

    def onEnergyBuy(self, id):
        self._printOverrideError('onEnergyBuy')

    def onEventStoryBannerClick(self):
        self._printOverrideError('onEventStoryBannerClick')

    def onEventNewsBannerClick(self):
        self._printOverrideError('onEventNewsBannerClick')

    def onGeneralProgressBannerClick(self):
        self._printOverrideError('onGeneralProgressBannerClick')

    def onGeneralSpeedUpClick(self, id):
        self._printOverrideError('onGeneralSpeedUpClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setTimerS(self, timer):
        return self.flashObject.as_setTimer(timer) if self._isDAAPIInited() else None

    def as_setGeneralInfoS(self, data):
        return self.flashObject.as_setGeneralInfo(data) if self._isDAAPIInited() else None

    def as_setNewsCounterS(self, value):
        return self.flashObject.as_setNewsCounter(value) if self._isDAAPIInited() else None

    def as_showVehicleTooltipS(self, data):
        return self.flashObject.as_showVehicleTooltip(data) if self._isDAAPIInited() else None

    def as_hideVehicleTooltipS(self):
        return self.flashObject.as_hideVehicleTooltip() if self._isDAAPIInited() else None
