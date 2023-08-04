# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/bonuses/bonuses_helpers.py
import logging
from constants import LOOTBOX_TOKEN_PREFIX
from gui.server_events.bonuses import getMergedBonusesFromDicts
from gui.shared.money import ZERO_MONEY, Currency, Money
from helpers import dependency
from skeletons.gui.system_messages import ISystemMessages
from gui_lootboxes.gui.lb_gui_constants import SCH_CLIENT_MSG_TYPE
TOKEN_COMPENSATION_TEMPLATE = 'lb_comp:{}:{}:{}:{}'
TOKEN_COMPENSATION_PREFIX = 'lb_comp:'
_logger = logging.getLogger(__name__)

def preformatCompensationValue(rewardsList):
    for rewards in rewardsList:
        vehiclesList = rewards.get('vehicles', [])
        compValue = _getCompensationVehicleValue(vehiclesList)
        for tokenID in rewards.get('tokens', {}).keys():
            if tokenID.startswith(TOKEN_COMPENSATION_PREFIX):
                compValue += _getCompensationValueFromToken(tokenID)

        for currency in Currency.ALL:
            if compValue.get(currency, 0) > 0:
                currencyValue = rewards.pop(currency, 0)
                if currency is not None:
                    newCurrencyValue = currencyValue - compValue.get(currency, 0)
                    if newCurrencyValue:
                        rewards[currency] = max(newCurrencyValue, 0)

    return


def _getCompensationVehicleValue(vehiclesList):
    comp = ZERO_MONEY
    for vehiclesDict in vehiclesList:
        for _, vehicleData in vehiclesDict.iteritems():
            if 'rentCompensation' in vehicleData:
                comp += Money.makeFromMoneyTuple(vehicleData['rentCompensation'])
            if 'customCompensation' in vehicleData:
                comp += Money.makeFromMoneyTuple(vehicleData['customCompensation'])

    return comp


def _getCompensationValueFromToken(tokenID):
    currency, value, _, _ = parseCompenstaionToken(tokenID)
    return Money.makeFrom(currency, value)


def prepareOpenResult(result):
    if result and result.success and result.auxData:
        bonus = result.auxData.get('bonus', [])
        preformatCompensationValue(bonus)
        rewards = getMergedBonusesFromDicts(bonus)
        boxesData = {}
        for token in rewards.get('tokens', {}).keys():
            if token.startswith(LOOTBOX_TOKEN_PREFIX):
                _, boxID = token.split(':')
                count = abs(rewards['tokens'][token].get('count', 1))
                boxesData[boxID] = count

        message = {'rewards': rewards,
         'boxesData': boxesData}
        systemMessages = dependency.instance(ISystemMessages)
        systemMessages.proto.serviceChannel.pushClientMessage(message, SCH_CLIENT_MSG_TYPE.LB_OPENED)


def parseCompenstaionToken(tokenID):
    try:
        _, currency, value, item, itemID = tokenID.split(':')
        return (currency,
         int(value),
         item,
         itemID)
    except ValueError as e:
        _logger.error(e)
        return (None, None, None, None)

    return None
