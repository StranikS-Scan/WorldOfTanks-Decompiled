# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/role_presenter_helper.py
from gui.impl import backport
from gui.impl.gen import R

def getRoleUserName(role):
    return backport.text(R.strings.item_types.tankman.roles.dyn(role)())


def getRoleWithFeminineUserName(role, isFemale):
    loc = R.strings.item_types.tankman.roles.female if isFemale else R.strings.item_types.tankman.roles
    return str(backport.text(loc.dyn(role)()))


def getRolePossessiveCaseUserName(role, isFemale):
    loc = R.strings.item_types.tankman.roles.female.possessiveCase if isFemale else R.strings.item_types.tankman.roles.possessiveCase
    return str(backport.text(loc.dyn(role)()))
