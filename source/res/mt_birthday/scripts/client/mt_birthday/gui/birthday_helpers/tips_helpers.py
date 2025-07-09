# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/birthday_helpers/tips_helpers.py
from helpers import dependency
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController

def isBirthdayActive():
    tanksBirthdayController = dependency.instance(ITanksBirthdayController)
    return tanksBirthdayController.isEnabled()
