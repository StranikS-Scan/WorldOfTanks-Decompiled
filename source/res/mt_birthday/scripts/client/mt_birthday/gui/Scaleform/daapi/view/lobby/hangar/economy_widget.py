# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/Scaleform/daapi/view/lobby/hangar/economy_widget.py
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.hangar.hangar_header import EconomyWidgetContent
from helpers import dependency
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController

class BirthdayEconomyWidgetContent(EconomyWidgetContent):
    __birthdayController = dependency.descriptor(ITanksBirthdayController)

    @classmethod
    def isEconomyWidgetVisible(cls):
        return False

    @classmethod
    def backportEconomyWidgetText(cls):
        return backport.text(R.strings.menu.hangar_header.birthday_economics_bonus(), value=cls.__birthdayController.getEconomyBonusValue())
