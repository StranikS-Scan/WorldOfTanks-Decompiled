# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/Scaleform/daapi/view/battle/common.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COMP7_PREBATTLE_CAROUSEL_ROW_VALUE

def getSavedRowCountValue():
    savedRowCount = AccountSettings.getSettings(COMP7_PREBATTLE_CAROUSEL_ROW_VALUE)
    return (savedRowCount, savedRowCount != -1)


def rowValueToRowCount(rowValue):
    return rowValue + 1


def rowCountToRowValue(rowCount):
    return rowCount - 1
