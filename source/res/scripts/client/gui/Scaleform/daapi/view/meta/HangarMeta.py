# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HangarMeta.py
from gui.Scaleform.framework.entities.View import View

class HangarMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    null
    """

    def onEscape(self):
        """
        :return :
        """
        self._printOverrideError('onEscape')

    def showHelpLayout(self):
        """
        :return :
        """
        self._printOverrideError('showHelpLayout')

    def closeHelpLayout(self):
        """
        :return :
        """
        self._printOverrideError('closeHelpLayout')

    def toggleGUIEditor(self):
        """
        :return :
        """
        self._printOverrideError('toggleGUIEditor')

    def as_setCrewEnabledS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setCrewEnabled(value) if self._isDAAPIInited() else None

    def as_setCarouselEnabledS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setCarouselEnabled(value) if self._isDAAPIInited() else None

    def as_setupAmmunitionPanelS(self, maintenanceEnabled, maintenanceTooltip, customizationEnabled, customizationTooltip):
        """
        :param maintenanceEnabled:
        :param maintenanceTooltip:
        :param customizationEnabled:
        :param customizationTooltip:
        :return :
        """
        return self.flashObject.as_setupAmmunitionPanel(maintenanceEnabled, maintenanceTooltip, customizationEnabled, customizationTooltip) if self._isDAAPIInited() else None

    def as_setControlsVisibleS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setControlsVisible(value) if self._isDAAPIInited() else None

    def as_setVisibleS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setVisible(value) if self._isDAAPIInited() else None

    def as_showHelpLayoutS(self):
        """
        :return :
        """
        return self.flashObject.as_showHelpLayout() if self._isDAAPIInited() else None

    def as_closeHelpLayoutS(self):
        """
        :return :
        """
        return self.flashObject.as_closeHelpLayout() if self._isDAAPIInited() else None

    def as_setIsIGRS(self, value, text):
        """
        :param value:
        :param text:
        :return :
        """
        return self.flashObject.as_setIsIGR(value, text) if self._isDAAPIInited() else None

    def as_setServerStatsS(self, stats, tooltipType):
        """
        :param stats:
        :param tooltipType:
        :return :
        """
        return self.flashObject.as_setServerStats(stats, tooltipType) if self._isDAAPIInited() else None

    def as_setServerStatsInfoS(self, tooltipFullData):
        """
        :param tooltipFullData:
        :return :
        """
        return self.flashObject.as_setServerStatsInfo(tooltipFullData) if self._isDAAPIInited() else None

    def as_setVehicleIGRS(self, actionIgrDaysLeft):
        """
        :param actionIgrDaysLeft:
        :return :
        """
        return self.flashObject.as_setVehicleIGR(actionIgrDaysLeft) if self._isDAAPIInited() else None

    def as_showMiniClientInfoS(self, description, hyperlink):
        """
        :param description:
        :param hyperlink:
        :return :
        """
        return self.flashObject.as_showMiniClientInfo(description, hyperlink) if self._isDAAPIInited() else None

    def as_show3DSceneTooltipS(self, id, args):
        """
        :param id:
        :param args:
        :return :
        """
        return self.flashObject.as_show3DSceneTooltip(id, args) if self._isDAAPIInited() else None

    def as_hide3DSceneTooltipS(self):
        """
        :return :
        """
        return self.flashObject.as_hide3DSceneTooltip() if self._isDAAPIInited() else None

    def as_setCarouselS(self, linkage, alias):
        """
        :param linkage:
        :param alias:
        :return :
        """
        return self.flashObject.as_setCarousel(linkage, alias) if self._isDAAPIInited() else None
