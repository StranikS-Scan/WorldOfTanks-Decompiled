# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/Scaleform/quests/settings.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import GroupedViewSettings, ScopeTemplates
from tutorial.gui.Scaleform.quests import pop_ups

class TUTORIAL_VIEW_ALIAS(object):
    TUTORIAL_QUEST_AWARD_WINDOW = 'tQuestAwardWindow'


QUESTS_VIEW_SETTINGS = (GroupedViewSettings(TUTORIAL_VIEW_ALIAS.TUTORIAL_QUEST_AWARD_WINDOW, pop_ups.TutorialQuestAwardWindow, 'awardWindow.swf', WindowLayer.WINDOW, 'tQuestAwardGroup', None, ScopeTemplates.DEFAULT_SCOPE),)
WINDOW_ALIAS_MAP = {'awardWindow': TUTORIAL_VIEW_ALIAS.TUTORIAL_QUEST_AWARD_WINDOW}
