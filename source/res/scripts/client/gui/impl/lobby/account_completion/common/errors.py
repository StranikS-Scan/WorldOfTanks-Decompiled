# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/common/errors.py
from gui.impl.backport import text as loc
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.common.field_email_model import FieldEmailModel
_res = R.strings.dialogs.accountCompletion

def emailIsTooShort():
    return loc(_res.emailIsTooShort(), amount=FieldEmailModel.EMAIL_LEN_MIN)


def emailIsTooLong():
    return loc(_res.emailIsTooLong(), amount=FieldEmailModel.EMAIL_LEN_MAX)


def emailIsInvalid():
    return loc(_res.errorIsWrong())


def emailRestrictedByCountry():
    return loc(_res.emailRestrictedByCountry())


def emailAlreadyTaken():
    return loc(_res.emailAlreadyTaken())


def serverUnavailableTimed():
    return loc(_res.warningServerUnavailableTimed())


def keyErrorResID():
    return _res.activate.keyError()


def tooManyIncorrectTriesResID():
    return _res.activate.tooManyIncorrectTries()
