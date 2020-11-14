# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ui_spam/tutorial_conditions.py
from helpers import dependency
from skeletons.gui.game_control import IUISpamController

class UISpamCondition(object):
    _uiSpamController = dependency.descriptor(IUISpamController)

    def check(self, aliasId):
        return not self._uiSpamController.shouldBeHidden(aliasId)
