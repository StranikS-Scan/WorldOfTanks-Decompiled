# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCTechnicalMaintenance.py
from gui.Scaleform.daapi.view.lobby.hangar.TechnicalMaintenance import TechnicalMaintenance
from gui.shared.money import Money

class BCTechnicalMaintenance(TechnicalMaintenance):

    def __init__(self, ctx=None):
        super(BCTechnicalMaintenance, self).__init__(ctx, skipConfirm=True)

    def as_setDataS(self, data):
        for shell in data['shells']:
            shell['userCount'] = shell['count']
            shell['prices'] = Money(credits=0).toMoneyTuple()

        data['autoEquipVisible'] = False
        super(BCTechnicalMaintenance, self).as_setDataS(data)

    def _setEquipment(self, installed, setup, modules):
        isBlock = True
        for install in installed:
            if install is not None:
                isBlock = False
                break

        for module in modules:
            module['currency'] = 'credits'
            creditsPrice = module['prices'].credits
            module['prices'] = Money(credits=creditsPrice).toMoneyTuple()

        if isBlock:
            for module in modules:
                if module['inventoryCount'] == 0:
                    module['disabled'] = True

        self.as_setEquipmentS(installed, setup, modules)
        return
