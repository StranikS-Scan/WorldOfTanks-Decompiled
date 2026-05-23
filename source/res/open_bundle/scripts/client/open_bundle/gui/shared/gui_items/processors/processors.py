# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/shared/gui_items/processors/processors.py
from __future__ import absolute_import
import BigWorld
from future.utils import viewvalues
from adisp import adisp_process, adisp_async
from functools import partial
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.gf_notifications.utils import pushGFNotification
from gui.shared.gui_items.processors import Processor, makeError, plugins
from gui.shared.gui_items.processors.plugins import MessageConfirmator
from gui.shared.money import Currency, ZERO_MONEY, Money
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from helpers.time_utils import getServerUTCTime, makeLocalServerTime
from messenger import g_settings
from messenger.formatters import TimeFormatter
from open_bundle.gui.constants import GFNotificationTemplates
from open_bundle.helpers.resources import getTextResource
from open_bundle.messenger.formatters.service_channel import OpenBundleAchievesFormatter
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController
from skeletons.gui.game_control import IAchievements20EarningController
from skeletons.gui.impl import IGuiLoader

class _ProcessNextStepConfirmator(MessageConfirmator):

    def __init__(self, bundleID, stepNumber):
        super(_ProcessNextStepConfirmator, self).__init__(None, True)
        self.__bundleID = bundleID
        self.__stepNumber = stepNumber
        return

    def _gfMakeMeta(self):
        from open_bundle.gui.shared.event_dispatcher import showOpenBundleConfirmDialog
        return partial(showOpenBundleConfirmDialog, self.__bundleID, self.__stepNumber)

    @adisp_async
    @adisp_process
    def _confirm(self, callback):
        yield lambda callback: callback(None)
        if self._activeHandler():
            isOk, data = yield self._gfMakeMeta()
            result = plugins.makeSuccess(**data) if isOk else plugins.makeError(**data)
            callback(result)
            return


class ProcessNextStepProcessor(Processor):
    __giuLoader = dependency.descriptor(IGuiLoader)
    __achievements = dependency.descriptor(IAchievements20EarningController)
    __openBundle = dependency.descriptor(IOpenBundleController)

    def __init__(self, bundleID, stepNumber):
        super(ProcessNextStepProcessor, self).__init__()
        self.__bundleID = bundleID
        self.__stepNumber = stepNumber
        self.addPlugins([_ProcessNextStepConfirmator(self.__bundleID, self.__stepNumber)])

    def _request(self, callback):
        openBundleAccountComponent = getattr(BigWorld.player(), 'OpenBundleAccountComponent', None)
        if openBundleAccountComponent is None:
            callback(makeError('Cannot find the OpenBundleAccountComponent'))
            return
        else:
            self.__achievements.pause()
            openBundleAccountComponent.processNextStep(self.__bundleID, self.__stepNumber, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))
            return

    def _errorHandler(self, code, errStr='', ctx=None):
        self.__achievements.resume()
        SystemMessages.pushMessage(text=backport.text(getTextResource(self.__bundleID, ('serviceChannelMessages', 'openBundleError'))()), type=SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM)
        return super(ProcessNextStepProcessor, self)._errorHandler(code, errStr, ctx)

    def _successHandler(self, code, ctx=None):
        if self.__openBundle.isUnicNotificationCell(self.__bundleID, ctx.get('receivedCell')) and ctx.get('randomBonus') and not self.__preformatCompensationValue(ctx.get('randomBonus')):
            ctx.update({'bundleID': self.__bundleID})
            self.__pushUnicNotification(ctx)
            self.__pushCommonNotification(ctx, cellRewards=False)
        else:
            self.__pushCommonNotification(ctx)
        if self.__giuLoader.windowsManager.getViewByLayoutID(R.views.open_bundle.mono.lobby.main()) is None:
            self.__achievements.resume()
        return super(ProcessNextStepProcessor, self)._successHandler(code, ctx)

    def __pushCommonNotification(self, ctx, cellRewards=True):
        money = Money.makeFromMoneyTuple(ctx.get('price'))
        currency = money.getCurrency()
        fmt = OpenBundleAchievesFormatter.formatData(ctx if cellRewards else {'fixedBonus': ctx.get('fixedBonus')})
        header = backport.text(getTextResource(self.__bundleID, ('serviceChannelMessages', 'simplePurchase'))(), eventName=backport.text(getTextResource(self.__bundleID, ('bundle', 'name'))()))
        if fmt is not None:
            SystemMessages.pushMessage(text=fmt, type=SystemMessages.SM_TYPE.OpenBundleRewards, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': header,
             'time': TimeFormatter.getLongDatetimeFormat(makeLocalServerTime(getServerUTCTime())),
             'spentCurrency': g_settings.htmlTemplates.format('openBundlePriceIn{}'.format(currency[0].upper() + currency[1:]), {'amount': money.get(currency)})})
        return

    def __pushUnicNotification(self, ctx):
        pushGFNotification(GFNotificationTemplates.SPECIAL_REWARDS_NOTIFICATION, ctx)

    def __preformatCompensationValue(self, rewards):
        vehiclesList = rewards.get('vehicles', [])
        compValue = self.__getCompensationValue(vehiclesList)
        for currency in Currency.ALL:
            if compValue.get(currency, 0) > 0:
                currencyValue = rewards.pop(currency, None)
                if currency is not None:
                    newCurrencyValue = currencyValue - compValue.get(currency, 0)
                    if newCurrencyValue:
                        rewards[currency] = newCurrencyValue

        return compValue != ZERO_MONEY

    def __getCompensationValue(self, vehicles):
        comp = ZERO_MONEY
        for vehicleDict in vehicles:
            for vehData in viewvalues(vehicleDict):
                if 'rentCompensation' in vehData:
                    comp += Money.makeFromMoneyTuple(vehData['rentCompensation'])
                if 'customCompensation' in vehData:
                    comp += Money.makeFromMoneyTuple(vehData['customCompensation'])

        return comp
