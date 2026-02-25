# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/shared/scores.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from cosmic_event_common.cosmic_event_common import ScoreEvents
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.scoring_model import ScoringTypeEnum
if typing.TYPE_CHECKING:
    from typing import List
SCORE_EVENTS_TO_MODEL_ENUM = {ScoreEvents.ARTIFACT_SCAN: ScoringTypeEnum.SCAN,
 ScoreEvents.KILL: ScoringTypeEnum.KILL,
 ScoreEvents.PICKUP: ScoringTypeEnum.PICKUP,
 ScoreEvents.RAMMING: ScoringTypeEnum.RAM,
 ScoreEvents.SHOT: ScoringTypeEnum.SHOT,
 ScoreEvents.ABILITY_HIT: ScoringTypeEnum.ABILITYHIT,
 ScoreEvents.ASSIST: ScoringTypeEnum.ASSIST,
 ScoreEvents.FIRST_BLOOD: ScoringTypeEnum.FIRSTBLOOD,
 ScoreEvents.KILL_STREAK: ScoringTypeEnum.KILLSTREAK,
 ScoreEvents.LOOT_RESEARCHING: ScoringTypeEnum.LOOTRESEARCHING,
 ScoreEvents.LOOT_RESEARCHING_DONE: ScoringTypeEnum.LOOTRESEARCHINGDONE,
 ScoreEvents.LOOT_RESEARCHABLE_PICK_UP: ScoringTypeEnum.LOOTRESEARCHABLEPICKUP}

def sortEvents(eventList):
    sortEventsByName(eventList)
    sortEventsByValue(eventList)


def sortEventsByValue(eventList):
    eventList.sort(key=lambda tup: tup[1], reverse=True)


def sortEventsByName(eventList):
    res = R.strings.cosmicEvent.artefact.actionList
    eventList.sort(key=lambda tup: backport.text(res.dyn(tup[0].value)()))
