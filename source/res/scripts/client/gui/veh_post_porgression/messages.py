# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_post_porgression/messages.py
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.processors import makeSuccess, makeError
from gui.shared.notifications import NotificationPriorityLevel
from gui.veh_post_porgression.formatters.ext_currency import formatExtendedCurrencyValue
from gui.veh_post_porgression.models.ext_money import ExtendedCurrency
from post_progression_common import ACTION_TYPES
_SPENT_MESSAGES = {ExtendedCurrency.VEH_XP: R.strings.system_messages.vehiclePostProgression.experienceSpent(),
 ExtendedCurrency.XP: R.strings.system_messages.vehiclePostProgression.experienceSpent(),
 ExtendedCurrency.FREE_XP: R.strings.system_messages.vehiclePostProgression.freeExperienceSpent(),
 ExtendedCurrency.CREDITS: R.strings.system_messages.vehiclePostProgression.creditsSpent()}

def makeSpentString(price, ignoreCurrencies=()):
    result = []
    for currency, value in price.iteritems():
        if value and currency not in ignoreCurrencies:
            currencyR = _SPENT_MESSAGES.get(currency, R.invalid())
            if currencyR:
                result.append(backport.text(currencyR, value=formatExtendedCurrencyValue(currency, value)))

    return ' '.join(result)


def makeUnlockFeatureMessage(featureName, vehicleUserName):
    msgKey = R.strings.system_messages.vehiclePostProgression.unlockFeature.dyn(featureName)
    return makeSuccess(backport.text(msgKey.body(), vehicle=vehicleUserName), msgType=SM_TYPE.InformationHeader, msgData={'header': backport.text(msgKey.title())}, msgPriority=NotificationPriorityLevel.HIGH) if msgKey else None


def makeModificationErrorMsg():
    msgKey = R.strings.system_messages.vehiclePostProgression.modificationProcessorError
    return makeError(backport.text(msgKey.body()), msgType=SM_TYPE.ErrorHeader, msgData={'header': backport.text(msgKey.title())}, msgPriority=NotificationPriorityLevel.HIGH)


def makeDiscardPairsMsg(vehicle, modifications):
    ctx = {'vehicle': vehicle.userName}
    msgKey = R.strings.system_messages.vehiclePostProgression.discardPairModification
    modificationNames = [ backport.text(mod.getLocNameRes()()) for mod in modifications ]
    if len(modificationNames) > 1:
        msgBody = R.strings.system_messages.vehiclePostProgression.discardPairsModification.body()
        separator = backport.text(R.strings.system_messages.vehiclePostProgression.discardPairsModification.modifications.separator())
        ctx['modifications'] = separator.join(modificationNames)
    else:
        msgBody = msgKey.body()
        ctx['modification'] = modificationNames[0] if modificationNames else ''
    return makeSuccess(backport.text(msgBody, **ctx), msgType=SM_TYPE.InformationHeader, msgData={'header': backport.text(msgKey.title())}, msgPriority=NotificationPriorityLevel.HIGH)


def makeBuyPairMsg(vehicle, stepID, modID):
    msgKey = R.strings.system_messages.vehiclePostProgression.buyPairModification
    mod = vehicle.postProgression.getStep(stepID).action.getModificationByID(modID)
    userMsg = backport.text(msgKey.body(), vehicle=vehicle.userName, modification=backport.text(mod.getLocNameRes()()))
    spentString = makeSpentString(mod.getPrice())
    return makeSuccess(' '.join((userMsg, spentString)), SM_TYPE.BuyPostProgressionModForCredits)


def makePurchaseStepsMsg(vehicle, stepIDs, price):
    ctx = {'vehicle': vehicle.userName}
    featureUnlockMsgs = []
    levels = []
    for stepID in stepIDs:
        step = vehicle.postProgression.getStep(stepID)
        if step.action.actionType != ACTION_TYPES.PAIR_MODIFICATION:
            levels.append(step.getLevel())
        if step.action.actionType == ACTION_TYPES.FEATURE:
            unlockMsg = makeUnlockFeatureMessage(step.action.getTechName(), vehicle.userName)
            if unlockMsg is not None:
                featureUnlockMsgs.append(unlockMsg)

    levels.sort()
    if len(levels) > 1:
        msgKey = R.strings.system_messages.vehiclePostProgression.researchSteps.body
        separator = backport.text(R.strings.system_messages.vehiclePostProgression.researchSteps.levels.separator())
        ctx['levels'] = separator.join((str(level) for level in levels))
    else:
        msgKey = R.strings.system_messages.vehiclePostProgression.researchStep.body
        ctx['level'] = str(levels[0]) if levels else ''
    userMsg = backport.text(msgKey(), **ctx)
    spentString = makeSpentString(price, ignoreCurrencies=(ExtendedCurrency.XP,))
    return makeSuccess(' '.join((userMsg, spentString)), SM_TYPE.ResearchVehiclePostProgressionSteps, featureUnlockMsgs)


def _getSlotCategoryName(slot):
    categoryR = R.strings.tank_setup.categories.dyn(next(iter(slot.categories))) if slot.categories else R.invalid
    return backport.text(categoryR()) if categoryR else ''


def makeSetSlotCategoryMsg(vehicle, slot):
    msgKey = R.strings.system_messages.vehiclePostProgression.setSlotCategory
    return makeSuccess(backport.text(msgKey.body(), vehicle=vehicle.userName, category=_getSlotCategoryName(slot)), msgType=SM_TYPE.InformationHeader, msgData={'header': backport.text(msgKey.title())}, msgPriority=NotificationPriorityLevel.HIGH) if slot is not None else makeSuccess()


def makeChangeSlotCategoryMsg(vehicle, slot, price):
    msgKey = R.strings.system_messages.vehiclePostProgression.changeSlotCategory
    if slot is not None:
        userMsg = backport.text(msgKey.body(), vehicle=vehicle.userName, category=_getSlotCategoryName(slot))
        spentString = makeSpentString(price)
        return makeSuccess(' '.join((userMsg, spentString)), msgType=SM_TYPE.ChangeSlotCategory)
    else:
        return makeSuccess()


def makeVehiclePostProgressionUnlockMsg(vehicle):
    msgKey = R.strings.system_messages.vehiclePostProgression.vehiclesUnlockPostProgression
    return makeSuccess(backport.text(msgKey.single.body(), vehicle=vehicle.userName), msgType=SM_TYPE.InformationHeader, msgPriority=NotificationPriorityLevel.HIGH, msgData={'header': backport.text(msgKey.title())}) if vehicle.postProgression.isUnlocked(vehicle) else makeSuccess()


def showWelcomeUnlockMsg():
    msgKey = R.strings.system_messages.vehiclePostProgression.vehiclesUnlockPostProgression
    SystemMessages.pushMessage(text=backport.text(msgKey.welcomeUnlock.body()), type=SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(msgKey.title())})
