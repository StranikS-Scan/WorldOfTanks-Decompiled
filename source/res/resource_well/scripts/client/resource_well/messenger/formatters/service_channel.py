# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/messenger/formatters/service_channel.py
from adisp import adisp_async, adisp_process
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from helpers import dependency, time_utils
from messenger import g_settings
from messenger.formatters import TimeFormatter
from messenger.formatters.service_channel import WaitItemsSyncFormatter
from messenger.formatters.service_channel_helpers import MessageData
from resource_well.gui.feature.constants import PurchaseMode
from resource_well.notification.decorators import ResourceWellLockButtonDecorator
from skeletons.gui.resource_well import IResourceWellController

class ResourceWellRewardFormatter(WaitItemsSyncFormatter):
    __TEMPLATE = 'ResourceWellRewardReceivedMessage'
    __R_MESSAGES = R.strings.messenger.serviceChannelMessages.resourceWell.reward
    __resourceWell = dependency.descriptor(IResourceWellController)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            rewardID = message.data.get('rewardID')
            if rewardID is None:
                callback([MessageData(None, None)])
            callback([self.__getMainMessage(rewardID, message), self.__getAdditionalMessage(rewardID, message)])
        else:
            callback([MessageData(None, None)])
        return

    def __getMainMessage(self, rewardID, message):
        serialNumber = message.data.get('serialNumber')
        vehicleName = self.__resourceWell.getRewardVehicle(rewardID).shortUserName
        additionalText = ''
        if serialNumber:
            text = backport.text(self.__R_MESSAGES.serialVehicle.text(), vehicle=text_styles.crystal(vehicleName))
            additionalText = backport.text(R.strings.messenger.serviceChannelMessages.resourceWell.breakLine()) + backport.text(self.__R_MESSAGES.serialVehicle.additionalText(), serialNumber=serialNumber)
        else:
            text = backport.text(self.__R_MESSAGES.vehicle.text(), vehicle=text_styles.crystal(vehicleName))
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'title': backport.text(self.__R_MESSAGES.title(), vehicle=vehicleName),
         'text': text,
         'additionalText': additionalText})
        return MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))

    def __getAdditionalMessage(self, rewardID, message):
        rewardConfig = self.__resourceWell.config.getRewardConfig(rewardID)
        if rewardConfig is None:
            return MessageData(None, None)
        else:
            slots = rewardConfig.bonus.get('slots')
            if not slots:
                return MessageData(None, None)
            text = g_settings.htmlTemplates.format('slotsAccruedInvoiceReceived', {'amount': backport.getIntegralFormat(slots)})
            at = TimeFormatter.getLongDatetimeFormat(time_utils.makeLocalServerTime(message.sentTime))
            formatted = g_settings.msgTemplates.format('resourceWellInvoiceReceived', ctx={'at': at,
             'text': text})
            return MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))


class ResourceWellNoVehiclesFormatter(WaitItemsSyncFormatter):
    __TEMPLATE = 'ResourceWellNoVehiclesMessage'
    __BUTTON_TEMPLATE = 'ResourceWellNoVehiclesWithButtonMessage'
    __R_MESSAGES = R.strings.messenger.serviceChannelMessages.resourceWell
    __resourceWell = dependency.descriptor(IResourceWellController)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if not isSynced or not self.__resourceWell.isEnabled():
            callback([MessageData(None, None)])
            return
        else:
            template = self.__TEMPLATE
            isSerial = message.data.get('isSerial')
            rewardID = message.data.get('rewardID')
            soldOutRewardIDs = message.data.get('soldOutRewardIDs', set())
            vehicle = self.__resourceWell.getRewardVehicle(rewardID)
            if vehicle is None:
                callback([MessageData(None, None)])
                return
            availableRewardIDs = set(self.__resourceWell.config.rewards.keys()).difference(soldOutRewardIDs)
            purchaseMode = self.__resourceWell.getPurchaseMode()
            if purchaseMode is PurchaseMode.TWO_PARALLEL_PRODUCTS and availableRewardIDs:
                template = self.__BUTTON_TEMPLATE
                availableVehicle = self.__resourceWell.getRewardVehicle(availableRewardIDs.pop())
                if availableVehicle is None:
                    callback([MessageData(None, None)])
                    return
                text = backport.text(self.__R_MESSAGES.noVehicles.twoParallelProducts.text(), soldOutVehicle=text_styles.crystal(vehicle.shortUserName), availableVehicle=text_styles.crystal(availableVehicle.shortUserName))
            elif purchaseMode is PurchaseMode.SEQUENTIAL_PRODUCT and isSerial:
                template = self.__BUTTON_TEMPLATE
                text = backport.text(self.__R_MESSAGES.noSerialVehicles.text(), vehicle=text_styles.crystal(vehicle.shortUserName))
            elif self.__resourceWell.getBalance():
                text = backport.text(self.__R_MESSAGES.noVehiclesWithReturn.text())
            else:
                text = backport.text(self.__R_MESSAGES.noVehicles.text())
            formatted = g_settings.msgTemplates.format(template, ctx={'title': backport.text(self.__R_MESSAGES.noVehicles.title()),
             'text': text})
            callback([MessageData(formatted, self._getGuiSettings(message, template, decorator=ResourceWellLockButtonDecorator))])
            return
