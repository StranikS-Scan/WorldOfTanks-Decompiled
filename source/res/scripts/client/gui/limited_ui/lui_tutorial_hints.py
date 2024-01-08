# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/limited_ui/lui_tutorial_hints.py
from gui.limited_ui.lui_rules_storage import LuiRules
from helpers import dependency
from skeletons.gui.game_control import ILimitedUIController
_ALIAS_TO_RULE_ID = {'blueprintsButton': LuiRules.BLUEPRINTS_BUTTON,
 'DogTagHangarHint': LuiRules.DOG_TAG_HINT,
 'PersonalReservesHangarHint': LuiRules.PR_HANGAR_HINT,
 'sessionStats': LuiRules.SESSION_STATS,
 'ModernizedSetupTabHint': LuiRules.MODERNIZE_SETUP_HINT,
 'ModeSelectorWidgetsBtnHint': LuiRules.MODE_SELECTOR_WIDGET_BTN_HINT}

class LimitedUIHintChecker(object):

    def check(self, aliasId):
        limitedUIController = dependency.instance(ILimitedUIController)
        ruleID = _ALIAS_TO_RULE_ID.get(aliasId)
        return ruleID is None or limitedUIController.isRuleCompleted(ruleID)
