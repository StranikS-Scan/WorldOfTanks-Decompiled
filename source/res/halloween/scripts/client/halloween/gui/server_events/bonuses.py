# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/server_events/bonuses.py
from __future__ import absolute_import
from gui.server_events.bonuses import TokensBonus
from halloween.skeletons.halloween_twitch_con_controller import IHalloweenTwitchConController
from helpers import dependency
from halloween_common.halloween_constants import HWStoryChoiceSettings

@dependency.replace_none_kwargs(ctrl=IHalloweenTwitchConController)
def cerfTokenChecker(tokenID, ctrl=None):
    return tokenID == str(ctrl.getCertificateTokenName())


@dependency.replace_none_kwargs(ctrl=IHalloweenTwitchConController)
def fakeChoiceMedalTokenChecker(tokenID, ctrl=None):
    return tokenID == HWStoryChoiceSettings.FAKE_MEDAL


class CerfTokenBonus(TokensBonus):

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(TokensBonus, self).__init__('cerfToken', value, isCompensation, ctx)

    def isShowInGUI(self):
        return True


class FakeChoiceMedalTokenBonus(TokensBonus):

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(FakeChoiceMedalTokenBonus, self).__init__(HWStoryChoiceSettings.FAKE_MEDAL, value, isCompensation, ctx)

    def isShowInGUI(self):
        return True
