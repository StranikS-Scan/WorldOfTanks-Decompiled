# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_crew_booster.py
from gui.impl.gen import R
from gui.impl import backport
from gui.shared.money import Money
from gui.shared.formatters import moneyWithIcon
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.hangar.event.event_crew_healing import FakeCrewHealing
from constants import HE19EnergyPurposes

class FakeCrewBooster(FakeCrewHealing):
    _ENERGY_ITEM_PURPOSE = HE19EnergyPurposes.booster.name

    def __init__(self):
        super(FakeCrewBooster, self).__init__()
        self.__needToShow = True

    def _hasUsedEnergy(self):
        return not self._vehiclesController.hasEnergy(self._ENERGY_ITEM_PURPOSE, self._vehCD)

    def _getConfirmData(self):
        currency, amount = self._getEnergyPrice()
        labelExecute = backport.text(R.strings.event.hangar.crew_booster.confirm_buy.labelExecute()) if self._getEnergyFor() else backport.text(R.strings.event.hangar.crew_booster.confirm_buy.labelBuy())
        data = {'messagePreset': 'EventConfirmMessageUI',
         'label': backport.text(R.strings.event.hangar.crew_booster.confirm_buy.label()),
         'message': backport.text(R.strings.event.hangar.crew_booster.confirm_buy.message()),
         'labelExecute': labelExecute,
         'iconPath': backport.image(R.images.gui.maps.icons.event.manageCrew.big.booster()),
         'costValue': amount if not self._getEnergyFor() else 0,
         'currency': currency,
         'storageAmount': self._getEnergyFor()}
        return data

    def _getPannelMeta(self):
        currency, amount = self._getEnergyPrice()
        specialAlias, specialArgs = self._getTooltipInfo(currency, TOOLTIPS_CONSTANTS.EVENT_CREW_BOOSTER_INFO)
        inStorage = ''
        if self._getEnergyFor() > 0:
            inStorage = backport.text(R.strings.event.hangar.crew_booster.panel.inStorage(), value=self._getEnergyFor())
        data = {'description': backport.text(R.strings.event.hangar.crew_booster.panel.header()),
         'cost': moneyWithIcon(Money.makeFrom(currency, amount), currType=currency),
         'tooltip': '',
         'specialArgs': specialArgs,
         'specialAlias': specialAlias,
         'isSpecial': True,
         'buttonEnabled': self._isApplyButtonEnabled(),
         'buttonLabel': backport.text(R.strings.event.hangar.crew_booster.panel.buttonLabel()),
         'icon': backport.image(R.images.gui.maps.icons.event.manageCrew.small.booster()),
         'inStorage': inStorage,
         'isActivated': self._hasUsedEnergy()}
        return data

    def _update(self):
        self._updatePanel()

    def _updatePanel(self):
        if not self._isEnabled():
            self.__needToShow = True
            self.as_setVisibleS(False)
            return
        if not self._checkTimeAndEnergy():
            if not self.__needToShow:
                self.__needToShow = True
                self.as_setVisibleS(False)
                g_currentVehicle.refreshModel()
            return
        if not self._checkVehCanHaveEnergy():
            self.__needToShow = True
            self.as_setVisibleS(False)
            return
        self.as_setDataS(self._getPannelMeta())
        if self.__needToShow:
            self.__needToShow = False
            self.as_setVisibleS(True)
