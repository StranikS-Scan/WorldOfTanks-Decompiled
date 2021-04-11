# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/account_completion.py
import async
from BWUtil import AsyncReturn
from constants import EMAIL_CONFIRMATION_TOKEN_NAME
from gui.platform.wgnp.controller import isEmailConfirmationNeeded, isEmailAddingNeeded
from helpers import dependency
from skeletons.gui.login_manager import ILoginManager
from skeletons.gui.platform.wgnp_controller import IWGNPRequestController
from skeletons.gui.shared import IItemsCache

def isEnabled():
    loginManager = dependency.instance(ILoginManager)
    return loginManager.isWgcSteam


@async.async
def _isNeedToUpdateEmail(checkResponseFunc, showWaiting=False):
    wgnpCtrl = dependency.instance(IWGNPRequestController)
    isRequired = False
    if isEnabled():
        response = yield async.await(wgnpCtrl.getEmailStatus(showWaiting=showWaiting))
        if response.isSuccess():
            isRequired = checkResponseFunc(response)
    raise AsyncReturn(isRequired)


@async.async
def isEmailAddingRequired(showWaiting=False):
    isRequired = yield async.await(_isNeedToUpdateEmail(isEmailAddingNeeded, showWaiting=showWaiting))
    raise AsyncReturn(isRequired)


@async.async
def isEmailConfirmationRequired(showWaiting=False):
    isRequired = yield async.await(_isNeedToUpdateEmail(isEmailConfirmationNeeded, showWaiting=showWaiting))
    raise AsyncReturn(isRequired)


def hasEmailConfirmationToken():
    itemsCache = dependency.instance(IItemsCache)
    return itemsCache.items.tokens.isTokenAvailable(EMAIL_CONFIRMATION_TOKEN_NAME)
