# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/battle_results/missions_progress/progress_presenter_helpers.py
from __future__ import absolute_import
from comp7_light.gui.impl.lobby.battle_results.missions_progress.progress_filters import comp7LightProgressionQuestsOnlyFilter
from comp7_light.gui.impl.lobby.battle_results.missions_progress.comp7_light_progression_quests_progress import Comp7LightProgressionQuestsPresenter
from gui.shared.system_factory import collectProgressionPresenters
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getComp7LightProgressionCategoriesPresenters(eventsCache=None):
    presenters = []
    allCommonQuests = eventsCache.getQuests()
    allCommonQuests.update(eventsCache.getHiddenQuests(lambda q: q.isShowedPostBattle()))
    questsLists = collectProgressionPresenters()
    for categoryProgressFilter, presenter in questsLists.values():
        presenters.append((categoryProgressFilter, presenter, allCommonQuests))

    presenters.append((comp7LightProgressionQuestsOnlyFilter, Comp7LightProgressionQuestsPresenter, allCommonQuests))
    return presenters
