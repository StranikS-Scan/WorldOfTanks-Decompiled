# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCTechnicalMaintenance.py
from gui.Scaleform.daapi.view.lobby.hangar.TechnicalMaintenance import TechnicalMaintenance
from gui.shared.money import Money
from bootcamp.BootcampLobbyHintsConfig import g_bootcampHintsConfig
from bootcamp.BootcampGarage import g_bootcampGarage
from bootcamp.BootCampEvents import g_bootcampEvents
from helpers import dependency
from skeletons.gui.game_control import IBootcampController

class BCTechnicalMaintenance(TechnicalMaintenance):
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def __init__(self, ctx=None):
        super(BCTechnicalMaintenance, self).__init__(ctx, skipConfirm=True)
        self.__isSelected = False
        self.__isLesson = self.bootcampCtrl.getDefaultLobbySettings()['hideHangarOptionalDevices']

    def onDropDownOpen(self, index):
        if not self.__isSelected:
            component = g_bootcampHintsConfig.objects['ServiceSlotRepairOption']
            component['path'] = 'eqItem{0}.select:id=asInt'.format(index + 1)
            g_bootcampGarage.runViewAlias('technicalMaintenance_Popup')

    def onDropDownClose(self, _):
        if not self.__isSelected:
            g_bootcampGarage.runViewAlias('technicalMaintenance_Slot')

    def onSlotSelected(self, _, __):
        if not self.__isSelected:
            self.__isSelected = True
            g_bootcampGarage.runViewAlias('technicalMaintenance_Done')

    def fillVehicle(self, needRepair, needAmmo, needEquipment, isPopulate, isUnload, isOrderChanged, shells, equipment):
        super(BCTechnicalMaintenance, self).fillVehicle(needRepair, needAmmo, needEquipment, isPopulate, isUnload, isOrderChanged, shells, equipment)
        g_bootcampGarage.runViewAlias('hangar')

    def as_setDataS(self, data):
        for shell in data['shells']:
            shell['prices'] = Money(credits=0).toMoneyTuple()

        if self.__isLesson:
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

        if isBlock and self.__isLesson:
            for module in modules:
                if module['inventoryCount'] == 0:
                    module['disabled'] = True

        self.as_setEquipmentS(installed, setup, modules)
        return

    def _populate(self):
        super(BCTechnicalMaintenance, self)._populate()
        observer = self.app.bootcampManager.getObserver('BCTechnicalMaintenanceObserver')
        if observer is not None:
            observer.onDropDownOpenEvent += self.onDropDownOpen
            observer.onDropDownCloseEvent += self.onDropDownClose
            observer.onSlotSelectedEvent += self.onSlotSelected
        g_bootcampEvents.onRequestCloseTechnicalMaintenance += self.destroy
        return

    def _dispose(self):
        observer = self.app.bootcampManager.getObserver('BCTechnicalMaintenanceObserver')
        if observer is not None:
            observer.onDropDownOpenEvent -= self.onDropDownOpen
            observer.onDropDownCloseEvent -= self.onDropDownClose
            observer.onSlotSelectedEvent -= self.onSlotSelected
        g_bootcampEvents.onRequestCloseTechnicalMaintenance -= self.destroy
        g_bootcampGarage.onViewClosed(self.settings.alias)
        g_bootcampGarage.onViewClosed('technicalMaintenance_Popup')
        g_bootcampGarage.onViewClosed('technicalMaintenance_Slot')
        g_bootcampGarage.onViewClosed('technicalMaintenance_Done')
        super(BCTechnicalMaintenance, self)._dispose()
        g_bootcampGarage.runViewAlias('hangar')
        return
