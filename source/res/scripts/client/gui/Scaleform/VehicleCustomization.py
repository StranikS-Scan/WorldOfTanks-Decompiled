# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/VehicleCustomization.py
# Compiled at: 2018-11-29 14:33:44
from account_helpers.Inventory import _VEHICLE
from adisp import process
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_ERROR, LOG_DEBUG
from items import vehicles
from items.vehicles import VehicleDescr
from gui import SystemMessages
from gui.Scaleform.CommandArgsParser import CommandArgsParser
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.customization import _VEHICLE_CUSTOMIZATIONS
from gui.Scaleform.utils.requesters import StatsRequester
from gui.Scaleform.windows import UIInterface
from gui.Scaleform.utils.HangarSpace import g_hangarSpace
from helpers import i18n
from PlayerEvents import g_playerEvents

class VehicleCustomization(UIInterface):
    __removeFormat = '{0:>s} <font color="#FF0000">{1:>s}</font>.'

    def __init__(self):
        super(VehicleCustomization, self).__init__()
        self.__interfaces = {}
        self.__prevCameraLocation = None
        self.__steps = 0
        self.__messages = []
        self.__credits = 0
        self.__gold = 0
        self.__returnHangar = False
        self.__lockUpdate = False
        self.__onceDataInited = False
        self.__removeItemFormats = {}
        return

    def __del__(self):
        LOG_DEBUG('VehicleCustomization deleted')

    def __onServerResponsesReceived(self):
        self.call('Customization.Vehicle.ServerResponsesReceived')
        self.__lockUpdate = False
        Waiting.hide('customizationApply')
        for type, message in self.__messages:
            SystemMessages.pushMessage(message, type=type)

        self.__messages = []
        if self.__returnHangar:
            self.uiHolder.movie.invoke(('loadHangar',))

    def __setPreviewMode(self):
        space = g_hangarSpace.space
        if space is not None:
            self.__prevCameraLocation = space.getCameraLocation()
            space.locateCameraToPreview()
        else:
            LOG_ERROR("ClientHangarSpace isn't initialized")
        return

    def __resetPreviewMode(self):
        space = g_hangarSpace.space
        if space is not None and self.__prevCameraLocation is not None:
            space.setCameraLocation(**self.__prevCameraLocation)
        return

    @process
    def __requestMoney(self):
        self.__credits = yield StatsRequester().getCredits()
        self.__gold = yield StatsRequester().getGold()

    def __finishInitData(self):
        if not self.__onceDataInited:
            self.__requestMoney()
            self.call('Customization.Vehicle.Init', [len(_VEHICLE_CUSTOMIZATIONS)])
            if g_currentVehicle.isLocked() or g_currentVehicle.isBroken():
                self.__setActionsLocked(True)
            self.__setPreviewMode()
            self.__onceDataInited = True
        Waiting.hide('loadPage')

    def __setActionsLocked(self, locked):
        self.call('Customization.Vehicle.SetActionsLocked', [locked])

    def populateUI(self, proxy):
        super(VehicleCustomization, self).populateUI(proxy)
        self.uiHolder.movie.backgroundAlpha = 0.0
        self.uiHolder.addExternalCallbacks({'Customization.Vehicle.RequestSections': self.onRequestSections,
         'Customization.Vehicle.Apply': self.onApply,
         'Customization.Vehicle.DoApply': self.onConfirmApply,
         'Customization.Vehicle.Drop': self.onDrop,
         'Customization.Vehicle.DoDrop': self.onConfirmDrop})
        g_playerEvents.onClientUpdated += self.__pe_onClientUpdated
        g_playerEvents.onShopResync += self.__pe_onShopResync
        g_currentVehicle.onChanged += self.__cv_onChanged
        vehDescr = None
        vehType = None
        if g_currentVehicle.isPresent():
            vehDescr = g_currentVehicle.vehicle.descriptor
            vehType = vehDescr.type
        self.__steps = len(_VEHICLE_CUSTOMIZATIONS)
        for customization in _VEHICLE_CUSTOMIZATIONS:
            sectionName = customization['sectionName']
            interface = customization['interface'](customization['sectionName'])
            interface.onDataInited += self.__ci_onDataInited
            interface.onCustomizationChangeSuccess += self.__ci_onCustomizationChangeSuccess
            interface.onCustomizationChangeFailed += self.__ci_onCustomizationChangeFailed
            interface.onCustomizationDropSuccess += self.__ci_onCustomizationDropSuccess
            interface.onCustomizationDropFailed += self.__ci_onCustomizationDropFailed
            interface.populateUI(proxy)
            interface.fetchCurrentItem(vehDescr)
            interface.invalidateData(vehType)
            self.__interfaces[sectionName] = interface
            self.__removeItemFormats[sectionName] = self.__removeFormat.format(i18n.makeString('#menu:customization/remove/{0:>s}/side-01'.format(sectionName)), i18n.makeString('#menu:customization/remove/{0:>s}/side-02'.format(sectionName)))

        if not self.__steps:
            self.__finishInitData()
        return

    def dispossessUI(self):
        self.__resetPreviewMode()
        for interface in self.__interfaces.itervalues():
            interface.dispossessUI()
            interface.onDataInited -= self.__ci_onDataInited
            interface.onCustomizationChangeSuccess -= self.__ci_onCustomizationChangeSuccess
            interface.onCustomizationChangeFailed -= self.__ci_onCustomizationChangeFailed
            interface.onCustomizationDropSuccess -= self.__ci_onCustomizationDropSuccess
            interface.onCustomizationDropFailed -= self.__ci_onCustomizationDropFailed

        self.__interfaces.clear()
        self.__onceDataInited = False
        g_playerEvents.onClientUpdated -= self.__pe_onClientUpdated
        g_playerEvents.onShopResync -= self.__pe_onShopResync
        g_currentVehicle.onChanged -= self.__cv_onChanged
        self.uiHolder.removeExternalCallbacks('Customization.Vehicle.RequestSections', 'Customization.Vehicle.Apply', 'Customization.Vehicle.DoApply', 'Customization.Vehicle.Drop', 'Customization.Vehicle.DoDrop')
        self.__removeItemFormats.clear()
        super(VehicleCustomization, self).dispossessUI()

    def onRequestSections(self, *args):
        parser = CommandArgsParser(self.onRequestSections.__name__)
        parser.parse(*args)
        for customization in _VEHICLE_CUSTOMIZATIONS:
            parser.addArg(customization['sectionName'])
            parser.addArg(customization['sectionUserString'])
            parser.addArg(customization['priceUserString'])

        self.respond(parser.args())

    def onApply(self, _, *sections):
        if g_currentVehicle.isLocked():
            SystemMessages.pushI18nMessage('#system_messages:customization/vehicle_locked', type=SystemMessages.SM_TYPE.Error)
            return
        elif g_currentVehicle.isBroken():
            SystemMessages.pushI18nMessage('#system_messages:customization/vehicle_{0:>s}'.format(g_currentVehicle.getState()), type=SystemMessages.SM_TYPE.Error)
            return
        else:
            notSelected = []
            selected = []
            remove = []
            totalGold = 0
            totalCredits = 0
            for section in sections:
                interface = self.__interfaces.get(section)
                if interface is not None:
                    if interface.isNewItemSelected():
                        cost, isGold = interface.getSelectedItemCost()
                        if cost > 0:
                            if isGold:
                                totalGold += cost
                            else:
                                totalCredits += cost
                        selected.append(i18n.makeString('#menu:customization/change/{0:>s}'.format(section)))
                        if interface.isCurrentItemRemove():
                            remove.append(self.__removeItemFormats[section])
                    else:
                        notSelected.append(i18n.makeString('#menu:customization/items/{0:>s}'.format(section)))
                else:
                    LOG_ERROR('Section not found', section)

            if len(notSelected) > 0:
                messageEx = i18n.makeString('#dialogs:customization/selectNewItems/message', ', '.join(notSelected))
                self.call('common.showMessageDialog', ['customization/selectNewItems',
                 True,
                 False,
                 messageEx,
                 None])
                return
            creditsNotEnough = totalCredits > self.__credits
            goldNotEnough = totalGold > self.__gold
            if creditsNotEnough or goldNotEnough:
                if creditsNotEnough and goldNotEnough:
                    key = '#system_messages:customization/credits_and_gold_not_enough'
                elif goldNotEnough:
                    key = '#system_messages:customization/gold_not_enough'
                else:
                    key = '#system_messages:customization/credits_not_enough'
                SystemMessages.pushI18nMessage(key, type=SystemMessages.SM_TYPE.Error)
                return
            messageEx = i18n.makeString('#dialogs:customization/changeConfirmation/message', selected=', '.join(selected), remove='\n'.join(remove))
            args = ['customization/changeConfirmation',
             True,
             True,
             messageEx,
             'Customization.Vehicle.DoApply']
            args.extend(sections)
            self.call('common.showMessageDialog', args)
            return

    def onConfirmApply(self, _, *sections):
        self.__returnHangar = True
        vehInvID = g_currentVehicle.vehicle.inventoryId
        self.__steps = len(sections)
        self.__messages = []
        self.call('Customization.Vehicle.RequestServerChanges')
        if self.__steps > 0:
            Waiting.show('customizationApply')
            self.__lockUpdate = True
        for section in sections:
            interface = self.__interfaces.get(section)
            if interface is not None:
                interface.change(vehInvID)
            else:
                LOG_ERROR('Change operation, section not found', section)
                self.__steps -= 1

        if not self.__steps:
            self.__onServerResponsesReceived()
        return

    def onDrop(self, *args):
        parser = CommandArgsParser(self.onDrop.__name__, 1, [str])
        section = parser.parse(*args)
        if g_currentVehicle.isLocked():
            SystemMessages.pushI18nMessage('#system_messages:customization/vehicle_locked', type=SystemMessages.SM_TYPE.Error)
            return
        elif g_currentVehicle.isBroken():
            SystemMessages.pushI18nMessage('#system_messages:customization/vehicle_{0:>s}'.format(g_currentVehicle.getState()), type=SystemMessages.SM_TYPE.Error)
            return
        else:
            dialog = 'customization/{0:>s}Drop'.format(section)
            self.call('common.showMessageDialog', [dialog,
             True,
             True,
             None,
             'Customization.Vehicle.DoDrop',
             section])
            return

    def onConfirmDrop(self, *args):
        parser = CommandArgsParser(self.onConfirmDrop.__name__, 1, [str])
        section = parser.parse(*args)
        interface = self.__interfaces.get(section)
        if interface is not None:
            self.__returnHangar = False
            self.__lockUpdate = True
            Waiting.show('customizationDrop')
            interface.drop(g_currentVehicle.vehicle.inventoryId)
        else:
            LOG_ERROR('Drop operation, section not found', section)
        return

    def __ci_onDataInited(self, _):
        self.__steps -= 1
        if not self.__steps:
            self.__finishInitData()

    def __ci_onCustomizationChangeFailed(self, message):
        self.__returnHangar = False
        self.__messages.append((SystemMessages.SM_TYPE.Error, message))
        self.__steps -= 1
        if not self.__steps:
            self.__onServerResponsesReceived()

    def __ci_onCustomizationChangeSuccess(self, message, type):
        self.__messages.append((type, message))
        self.__steps -= 1
        if not self.__steps:
            self.__onServerResponsesReceived()

    def __ci_onCustomizationDropFailed(self, message):
        Waiting.hide('customizationDrop')
        self.__lockUpdate = False
        SystemMessages.pushMessage(message, type=SystemMessages.SM_TYPE.Error)

    def __ci_onCustomizationDropSuccess(self, message):
        Waiting.hide('customizationDrop')
        self.__lockUpdate = False
        SystemMessages.pushMessage(message, type=SystemMessages.SM_TYPE.Information)

    def __cv_onChanged(self):
        self.__setActionsLocked(g_currentVehicle.isLocked() or g_currentVehicle.isBroken())

    def __pe_onClientUpdated(self, diff):
        stats = diff.get('stats', {})
        if 'credits' in stats:
            self.__credits = stats['credits']
        if 'gold' in stats:
            self.__gold = stats['gold']
        account = diff.get('account', {})
        if 'attrs' in account:
            self.__prevCameraLocation.update({'yaw': None,
             'pitch': None})
        vehCompDescr = diff.get('inventory', {}).get(_VEHICLE, {}).get('compDescr', {}).get(g_currentVehicle.vehicle.inventoryId)
        if vehCompDescr is not None and not self.__lockUpdate:
            vehDescr = VehicleDescr(compactDescr=vehCompDescr)
            for interface in self.__interfaces.itervalues():
                interface.update(vehDescr)

        return

    def __pe_onShopResync(self):
        if not g_currentVehicle.isPresent():
            return
        Waiting.show('loadPage')
        self.__steps = len(_VEHICLE_CUSTOMIZATIONS)
        vehType = vehicles.g_cache.vehicle(*g_currentVehicle.vehicle.descriptor.type.id)
        self.call('Customization.Vehicle.ResetNewItems')
        for interface in self.__interfaces.itervalues():
            interface.invalidateData(vehType, refresh=True)
