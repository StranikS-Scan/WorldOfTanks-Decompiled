# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/common/errors.py
from gui.impl.backport import text as loc
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.common.field_email_model import FieldEmailModel
from gui.impl.gen.view_models.views.lobby.account_completion.common.field_name_model import FieldNameModel
from gui.impl.gen.view_models.views.lobby.account_completion.common.field_password_model import FieldPasswordModel
_res = R.strings.dialogs.accountCompletion

def emailIsTooShort():
    return loc(_res.emailIsTooShort(), amount=FieldEmailModel.EMAIL_LEN_MIN)


def emailIsTooLong():
    return loc(_res.emailIsTooLong(), amount=FieldEmailModel.EMAIL_LEN_MAX)


def passwordIsTooShort():
    return loc(_res.passwordIsTooShort(), amount=FieldPasswordModel.PASSWORD_LEN_MIN)


def passwordIsTooLong():
    return loc(_res.passwordIsTooLong(), amount=FieldPasswordModel.PASSWORD_LEN_MAX)


def emailIsInvalid():
    return loc(_res.errorIsWrong())


def emailRestrictedByCountry():
    return loc(_res.emailRestrictedByCountry())


def emailAlreadyTaken():
    return loc(_res.emailAlreadyTaken())


def passwordIsInvalid():
    return loc(_res.badPassword())


def spaPasswordIsWeak():
    return loc(_res.spa.passwordIsWeak())


def serverUnavailableTimed():
    return loc(_res.warningServerUnavailableTimed())


def keyErrorResID():
    return _res.activate.keyError()


def tooManyIncorrectTriesResID():
    return _res.activate.tooManyIncorrectTries()


def nameIsTooShort():
    return loc(_res.renamingOverlay.nameTooShort(), amount=FieldNameModel.NAME_LEN_MIN)


def nameIsTooLong():
    return loc(_res.renamingOverlay.nameToolong(), amount=FieldNameModel.NAME_LEN_MAX)


def nameInvalid():
    return loc(_res.renamingOverlay.nameInvalid())
