# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCTechnicalMaintenance.py
from gui.Scaleform.daapi.view.lobby.hangar.TechnicalMaintenance import TechnicalMaintenance
from gui.Scaleform.daapi.view.meta.BCTechnicalMaintenanceMeta import BCTechnicalMaintenanceMeta
from debug_utils import LOG_DEBUG
from gui.shared.money import Money
from bootcamp.Bootcamp import g_bootcamp
from bootcamp.BootcampLobbyHintsConfig import g_bootcampHintsConfig
from bootcamp.BootcampGarage import g_bootcampGarage

class BCTechnicalMaintenance(BCTechnicalMaintenanceMeta):

    def __init__(self, ctx=None):
        LOG_DEBUG('BCTechnicalMaintenance.__init__')
        super(BCTechnicalMaintenance, self).__init__(ctx, skipConfirm=True)
        self.__isSelected = False
        self.__isLesson = g_bootcamp.getDefaultLobbySettings()['hideHangarOptionalDevices']

    def _populate(self):
        LOG_DEBUG('BCTechnicalMaintenance._populate')
        super(BCTechnicalMaintenance, self)._populate()

    def _dispose(self):
        super(BCTechnicalMaintenance, self)._dispose()
        g_bootcampGarage.runViewAlias('hangar')

    def onDropDownOpen(self, index):
        if not self.__isSelected:
            component = g_bootcampHintsConfig.objects['ServiceSlotRepairOption']
            component['path'] = 'eqItem{0}.select:id=asInt'.format(index + 1)
            LOG_DEBUG('BCTechnicalMaintenance.onDropDownOpen', index)
            g_bootcampGarage.runViewAlias('bootcampTechnicalMaintenance_Popup')

    def onDropDownClose(self, index):
        LOG_DEBUG('BCTechnicalMaintenance.onDropDownClose', index)
        if not self.__isSelected:
            g_bootcampGarage.runViewAlias('bootcampTechnicalMaintenance_Slot')

    def onSlotSelected(self, slotId, index):
        if not self.__isSelected:
            self.__isSelected = True
            g_bootcampGarage.runViewAlias('bootcampTechnicalMaintenance_Done')

    def fillVehicle(self, needRepair, needAmmo, needEquipment, isPopulate, isUnload, isOrderChanged, shells, equipment):
        super(BCTechnicalMaintenance, self).fillVehicle(needRepair, needAmmo, needEquipment, isPopulate, isUnload, isOrderChanged, shells, equipment)
        g_bootcampGarage.runViewAlias('hangar')

    def as_setEquipmentS(self, installed, setup, modules):
        isBlock = True
        for install in installed:
            if install is not None:
                isBlock = False
                break

        for module in modules:
            module['currency'] = 'credits'
            creditsPrice = module['prices'].credits
            module['prices'] = Money(credits=creditsPrice)

        if isBlock and self.__isLesson:
            for module in modules:
                if module['inventoryCount'] == 0:
                    module['enabled'] = False

        super(BCTechnicalMaintenanceMeta, self).as_setEquipmentS(installed, setup, modules)
        return

    def as_setDataS(self, data):
        for shell in data['shells']:
            shell['prices'] = Money(credits=0)

        if self.__isLesson:
            data['autoEquipVisible'] = False
        super(BCTechnicalMaintenanceMeta, self).as_setDataS(data)
