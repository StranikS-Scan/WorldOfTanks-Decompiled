# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/wgcg/data_wrappers/server_replays.py
from typing import NamedTuple, List, Optional
from shared_utils import CONST_CONTAINER

class DataNames(CONST_CONTAINER):
    TOP_REPLAYS = 'TOP_REPLAYS'
    BEST_REPLAYS = 'BEST_REPLAYS'
    MY_REPLAYS = 'MY_REPLAYS'
    REPLAY_LINK = 'REPLAY_LINK'
    FIND_REPLAY = 'FIND_REPLAY'
    ONE_REPLAY = 'ONE_REPLAY'


class StatParams(CONST_CONTAINER):
    DAMAGE_DEALT = 'damage_dealt'
    DAMAGE_ASSISTED = 'damage_assisted'
    DAMAGE_BLOCKED = 'damage_blocked'
    KILLS = 'kills_made'
    EXP = 'exp'
    MARK_OF_MASTERY = 'mastery_mark'
    LIKE_COUNT = 'likes_received'


ShortReplay = NamedTuple('ShortReplay', [('rank', int),
 ('replay_id', int),
 ('arena_id', int),
 ('vehicle_entity_id', int),
 ('map', str),
 ('battle_type', int),
 ('battle_start', int),
 ('vehicle_cd', int),
 ('spa_id', int),
 ('nickname', str),
 ('clan_tag', str),
 ('clan_color', Optional[int]),
 ('exp', int),
 ('damage_dealt', int),
 ('damage_assisted', int),
 ('damage_blocked', int),
 ('kills_made', int),
 ('mastery_mark', int),
 ('achievements_received', int),
 ('achievements', List[str])])
PageReplays = NamedTuple('PageReplays', [('rankings', List[ShortReplay]),
 ('total_entries', int),
 ('limit', int),
 ('offset', int)])
TopReplays = NamedTuple('TopReplays', [('exp', ShortReplay),
 ('damage_dealt', ShortReplay),
 ('damage_assisted', ShortReplay),
 ('damage_blocked', ShortReplay),
 ('kills_made', ShortReplay),
 ('likes_received', ShortReplay)])
ReplayLink = NamedTuple('ReplayLink', [('replay_link', str), ('expire_time', int)])
