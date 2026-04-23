# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/battle_results/missions_progress/progress_presenter_helpers.py
from __future__ import absolute_import
from comp7.gui.impl.lobby.battle_results.missions_progress.comp7_weekly_missions_progress import Comp7WeeklyMissionsProgressPresenter
from comp7.gui.impl.lobby.battle_results.missions_progress.progress_filters import comp7WeeklyQuestsProgressFilter, comp7CustomizationQuestsProgressFilter, comp7CommonBattleQuestsProgressFilter, comp7VehicleProgressFilter
from comp7.gui.impl.lobby.battle_results.missions_progress.comp7_customization_progress import Comp7CustomizationProgressPresenter
from gui.impl.lobby.battle_results.missions_progress.new_module_vehicle_progress import NewModuleVehicleProgressPresenter
from gui.shared.system_factory import collectProgressionPresenters
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from gui.impl.lobby.battle_results.missions_progress.common_battle_quests_progress import CommonBattleQuestsProgressPresenter

@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getComp7ProgressionCategoriesPresenters(eventsCache=None):
    presenters = []
    allCommonQuests = eventsCache.getQuests()
    allCommonQuests.update(eventsCache.getHiddenQuests(lambda q: q.isShowedPostBattle()))
    questsLists = collectProgressionPresenters()
    for categoryProgressFilter, presenter in questsLists.values():
        if presenter == CommonBattleQuestsProgressPresenter:
            categoryProgressFilter = comp7CommonBattleQuestsProgressFilter
        if presenter == NewModuleVehicleProgressPresenter:
            categoryProgressFilter = comp7VehicleProgressFilter
        presenters.append((categoryProgressFilter, presenter, allCommonQuests))

    presenters.extend(((comp7WeeklyQuestsProgressFilter, Comp7WeeklyMissionsProgressPresenter, allCommonQuests), (comp7CustomizationQuestsProgressFilter, Comp7CustomizationProgressPresenter, allCommonQuests)))
    return presenters
