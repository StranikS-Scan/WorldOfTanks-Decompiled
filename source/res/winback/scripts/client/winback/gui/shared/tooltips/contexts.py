# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/shared/tooltips/contexts.py
from gui.shared.tooltips.contexts import ExtendedAwardContext

class WinbackDiscountContext(ExtendedAwardContext):

    def __init__(self, fieldsToExclude=None):
        super(WinbackDiscountContext, self).__init__(fieldsToExclude=fieldsToExclude, showBuyPrice=True, showUnlockPrice=True, isAwardWindow=False)
        self._blueprintsFragmentsCount = 0
        self._customPrice = None
        self._hideStatus = True
        self._showDiscount = True
        return

    def buildItem(self, intCD, tmanCrewLevel=None, rentExpiryTime=None, rentBattles=None, rentWins=None, rentSeason=None, showCrew=False, showVehicleSlot=False, allModulesAvailable=False, blueprintsFragmentsCount=0, customPrice=None, hideStatus=True, showDiscount=True):
        self._blueprintsFragmentsCount = blueprintsFragmentsCount
        self._customPrice = customPrice
        self._hideStatus = hideStatus
        self._showDiscount = showDiscount
        return super(WinbackDiscountContext, self).buildItem(intCD, tmanCrewLevel, rentExpiryTime, rentBattles, rentWins, rentSeason, showCrew, showVehicleSlot, allModulesAvailable)

    def getParams(self):
        params = super(WinbackDiscountContext, self).getParams()
        params['blueprintFragmentsCount'] = self._blueprintsFragmentsCount
        params['customPrice'] = self._customPrice
        params['hideStatus'] = self._hideStatus
        params['showDiscount'] = self._showDiscount
        return params
