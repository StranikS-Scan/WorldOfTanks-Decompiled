# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/client_request_lib/requester.py
from client_request_lib.data_sources.staging import StagingDataAccessor
from client_request_lib.data_sources.fake import FakeDataAccessor
from client_request_lib.data_sources.gateway import GatewayDataAccessor
try:
    import BigWorld
except ImportError:

    class _BW(object):

        def callback(self, delay, callback):
            callback()


    BigWorld = _BW()

class RequestDescriptor(object):

    def __init__(self, accessor_class):
        self.accessor = accessor_class

    def __get__(self, instance, owner):
        return self if instance is None else self.accessor(instance.data_source)


def _in_bigworld(func):
    if callable(func):

        def inner(*args, **kwargs):
            BigWorld.callback(0.0, lambda : func(*args, **kwargs))

        return inner
    return func


def bigworld_callback_wrapper(func):

    def wrapped(*args, **kwargs):
        new_args = [ _in_bigworld(arg) for arg in args ]
        new_kwargs = {k:_in_bigworld(v) for k, v in kwargs.items()}
        return func(*new_args, **new_kwargs)

    return wrapped


def bigworld_wrapped(attr):
    return bigworld_callback_wrapper(attr) if callable(attr) else attr


class BigworldCallbackMutator(type):

    def __new__(cls, name, bases, attr_dict):
        new_attr_dict = {}
        for k, v in attr_dict.iteritems():
            new_attr_dict[k] = bigworld_wrapped(v)

        return type.__new__(cls, name, bases, new_attr_dict)


class BaseAccessor(object):
    __metaclass__ = BigworldCallbackMutator

    def __init__(self, data_source):
        self._data_source = data_source


class AdventCalendarAccessor(BaseAccessor):

    def advent_calendar_fetch_hero_tank_info(self, callback):
        return self._data_source.advent_calendar_fetch_hero_tank_info(callback)


class CrafmachineAccessor(BaseAccessor):

    def craftmachine_modules_info(self, callback):
        return self._data_source.craftmachine_modules_info(callback)


class GmAccessor(BaseAccessor):

    def get_provinces(self, callback, clan_id, fields=None):
        return self._data_source.get_clan_provinces(callback, clan_id, fields=fields)

    def get_statistics(self, callback, clan_id, fields=None):
        return self._data_source.get_clan_globalmap_stats(callback, clan_id, fields=fields)

    def get_fronts_info(self, callback, front_names=None, fields=None):
        return self._data_source.get_fronts_info(callback, front_names=front_names, fields=fields)


class RatingAccessor(BaseAccessor):

    def get_clans_ratings(self, callback, clan_ids, fields=None):
        return self._data_source.get_clans_ratings(callback, clan_ids, fields=fields)


class ExporterAccessor(BaseAccessor):

    def get_accounts_info(self, callback, account_ids, fields=None):
        return self._data_source.get_accounts_info(callback, account_ids, fields=fields)


class SpaAccessor(BaseAccessor):

    def get_accounts_names(self, callback, account_ids, fields=None):
        return self._data_source.get_accounts_names(callback, account_ids, fields=fields)

    def get_account_attribute_by_prefix(self, callback, attr_prefix, fields=None):
        return self._data_source.get_account_attribute_by_prefix(callback, attr_prefix, fields=fields)


class FreyaAccessor(BaseAccessor):

    def freya_v1_fetch_product_list(self, callback, params, fields=None):
        return self._data_source.freya_v1_fetch_product_list(callback, params, fields=fields)


class ClansAccessor(BaseAccessor):

    class INVITE_STATUSES:
        ACCEPTED = 'accepted'
        DECLINED = 'declined'
        DELETED = 'deleted'
        EXPIRED = 'expired'

    class APPLICATION_STATUSES:
        ACCEPTED = 'accepted'
        DECLINED = 'declined'
        DELETED = 'deleted'
        EXPIRED = 'expired'

    def get_clans_info(self, callback, clan_ids, fields=None):
        return self._data_source.get_clans_info(callback, clan_ids, fields=fields)

    def search_clans(self, callback, search, fields=None, offset=0, limit=18, get_total_count=False):
        return self._data_source.search_clans(callback, search, fields=fields, offset=offset, limit=limit, get_total_count=get_total_count)

    def get_recommended_clans(self, callback, fields=None, offset=0, limit=18, get_total_count=False):
        return self._data_source.get_recommended_clans(callback, fields=fields, offset=offset, limit=limit, get_total_count=get_total_count)

    def get_account_applications_count_since(self, callback, account_id, since=None):
        return self._data_source.get_account_applications_count_since(callback, account_id, since=since)

    def get_clan_invites_count_since(self, callback, clan_id, since=None):
        return self._data_source.get_clan_invites_count_since(callback, clan_id, since=since)

    def get_clan_members(self, callback, clan_id, fields=None):
        return self._data_source.get_clan_members(callback, clan_id, fields=fields)

    def get_clan_favorite_attributes(self, callback, clan_id, fields=None):
        return self._data_source.get_clan_favorite_attributes(callback, clan_id, fields=fields)

    def get_accounts_clans(self, callback, account_ids, fields=None):
        return self._data_source.get_accounts_clans(callback, account_ids, fields=fields)

    def get_account_invites(self, callback, fields=None, statuses=None, offset=0, limit=18, get_total_count=False):
        return self._data_source.get_account_invites(callback, fields=fields, statuses=statuses, offset=offset, limit=limit, get_total_count=get_total_count)

    def get_clan_invites(self, callback, clan_id, fields=None, statuses=None, offset=0, limit=18, get_total_count=False):
        return self._data_source.get_clan_invites(callback, clan_id, fields=fields, statuses=statuses, offset=offset, limit=limit, get_total_count=get_total_count)

    def get_account_applications(self, callback, fields=None, statuses=None, offset=0, limit=18, get_total_count=False):
        return self._data_source.get_account_applications(callback, fields=fields, statuses=statuses, offset=offset, limit=limit, get_total_count=get_total_count)

    def get_clan_applications(self, callback, clan_id, fields=None, statuses=None, offset=0, limit=18, get_total_count=False):
        return self._data_source.get_clan_applications(callback, clan_id, fields=fields, statuses=statuses, offset=offset, limit=limit, get_total_count=get_total_count)

    def create_applications(self, callback, clan_ids, comment):
        return self._data_source.create_applications(callback, clan_ids, comment)

    def accept_application(self, callback, application_id):
        return self._data_source.accept_application(callback, application_id)

    def decline_application(self, callback, application_id):
        return self._data_source.decline_application(callback, application_id)

    def create_invites(self, callback, clan_id, account_ids, comment):
        return self._data_source.create_invites(callback, clan_id, account_ids, comment)

    def accept_invite(self, callback, invite_id):
        return self._data_source.accept_invite(callback, invite_id)

    def decline_invite(self, callback, invite_id):
        return self._data_source.decline_invite(callback, invite_id)

    def bulk_decline_invites(self, callback, invite_ids):
        return self._data_source.bulk_decline_invites(callback, invite_ids)


class StrongholdsAccessor(BaseAccessor):

    def get_info(self, callback, clan_id, fields=None):
        return self._data_source.get_stronghold_info(callback, clan_id, fields=fields)

    def get_statistics(self, callback, clan_id, fields=None):
        return self._data_source.get_strongholds_statistics(callback, clan_id, fields=fields)

    def get_state(self, callback, clan_id, fields=None):
        return self._data_source.get_strongholds_state(callback, clan_id, fields=fields)


class WgshAccessor(BaseAccessor):

    def get_wgsh_unit_info(self, callback, periphery_id, unit_server_id, rev, fields=None):
        return self._data_source.get_wgsh_unit_info(callback, periphery_id, unit_server_id, rev, fields=fields)

    def set_vehicle(self, callback, periphery_id, unit_server_id, vehicle_cd, fields=None):
        return self._data_source.set_vehicle(callback, periphery_id, unit_server_id, vehicle_cd, fields=fields)

    def set_readiness(self, callback, periphery_id, unit_server_id, is_ready, reset_vehicle, fields=None):
        return self._data_source.set_readiness(callback, periphery_id, unit_server_id, is_ready, reset_vehicle, fields=fields)

    def invite_players(self, callback, periphery_id, unit_server_id, accounts_to_invite, comment, fields=None):
        return self._data_source.invite_players(callback, periphery_id, unit_server_id, accounts_to_invite, comment, fields=fields)

    def assign_player(self, callback, periphery_id, unit_server_id, account_to_assign, slot_id_to_assign, fields=None):
        return self._data_source.assign_player(callback, periphery_id, unit_server_id, account_to_assign, slot_id_to_assign, fields=fields)

    def unassign_player(self, callback, periphery_id, unit_server_id, account_to_unassign, fields=None):
        return self._data_source.unassign_player(callback, periphery_id, unit_server_id, account_to_unassign, fields=fields)

    def give_leadership(self, callback, periphery_id, unit_server_id, target_account_id, fields=None):
        return self._data_source.give_leadership(callback, periphery_id, unit_server_id, target_account_id, fields=fields)

    def set_equipment_commander(self, callback, periphery_id, unit_server_id, target_account_id, fields=None):
        return self._data_source.set_equipment_commander(callback, periphery_id, unit_server_id, target_account_id, fields=fields)

    def leave_room(self, callback, periphery_id, unit_server_id, fields=None):
        return self._data_source.leave_room(callback, periphery_id, unit_server_id, fields=fields)

    def leave_mode(self, callback, fields=None):
        return self._data_source.leave_mode(callback, fields=fields)

    def take_away_leadership(self, callback, periphery_id, unit_server_id, fields=None):
        return self._data_source.take_away_leadership(callback, periphery_id, unit_server_id, fields=fields)

    def kick_player(self, callback, periphery_id, unit_server_id, account_to_kick, fields=None):
        return self._data_source.kick_player(callback, periphery_id, unit_server_id, account_to_kick, fields=fields)

    def set_open(self, callback, periphery_id, unit_server_id, is_open, fields=None):
        return self._data_source.set_open(callback, periphery_id, unit_server_id, is_open, fields=fields)

    def lock_reserve(self, callback, periphery_id, unit_server_id, reserve_id, fields=None):
        return self._data_source.lock_reserve(callback, periphery_id, unit_server_id, reserve_id, fields=fields)

    def unlock_reserve(self, callback, periphery_id, unit_server_id, reserve_id, fields=None):
        return self._data_source.unlock_reserve(callback, periphery_id, unit_server_id, reserve_id, fields=fields)

    def join_room(self, callback, periphery_id, unit_server_id, fields=None):
        return self._data_source.join_room(callback, periphery_id, unit_server_id, fields=fields)

    def matchmaking_info(self, callback, periphery_id, unit_server_id, fields=None):
        return self._data_source.matchmaking_info(callback, periphery_id, unit_server_id, fields=fields)

    def set_slot_vehicle_type_filter(self, callback, periphery_id, unit_server_id, slot_idx, vehicle_types, fields=None):
        return self._data_source.set_slot_vehicle_type_filter(callback, periphery_id, unit_server_id, slot_idx, vehicle_types, fields=fields)

    def set_slot_vehicles_filter(self, callback, periphery_id, unit_server_id, slot_idx, vehicles, fields=None):
        return self._data_source.set_slot_vehicles_filter(callback, periphery_id, unit_server_id, slot_idx, vehicles, fields=fields)

    def get_slot_vehicle_filters(self, callback, periphery_id, unit_server_id, fields=None):
        return self._data_source.get_slot_vehicle_filters(callback, periphery_id, unit_server_id, fields=fields)

    def stop_players_matching(self, callback, periphery_id, unit_server_id):
        return self._data_source.stop_players_matching(callback, periphery_id, unit_server_id)

    def clan_statistics(self, callback, clan_id, fields=None):
        return self._data_source.clan_statistics(callback, clan_id, fields=fields)

    def account_statistics(self, callback, account_id, fields=None):
        return self._data_source.account_statistics(callback, account_id, fields=fields)


class RblbAccessor(BaseAccessor):

    def user_ranked_position(self, callback, fields=None):
        return self._data_source.user_ranked_position(callback, fields=fields)

    def user_ranked_year_position(self, callback):
        return self._data_source.user_ranked_year_position(callback)


class WGElenAccessor(BaseAccessor):

    def join_event(self, callback, event_id, fields=None):
        return self._data_source.join_event(callback, event_id, fields=fields)

    def leave_event(self, callback, event_id, fields=None):
        return self._data_source.leave_event(callback, event_id, fields=fields)

    def get_events_data(self, callback, fields=None):
        return self._data_source.get_events_data(callback, fields=fields)

    def get_hangar_flag(self, callback, fields=None):
        return self._data_source.get_hangar_flag(callback, fields=fields)

    def get_leaderboard(self, callback, event_id, page_number, leaderboard_id, fields=None):
        return self._data_source.get_leaderboard(callback, event_id, page_number, leaderboard_id, fields=fields)

    def get_my_event_top(self, callback, event_id, fields=None):
        return self._data_source.get_my_event_top(callback, event_id, fields=fields)

    def get_my_leaderboard_position(self, callback, event_id, leaderboard_id, fields=None):
        return self._data_source.get_my_leaderboard_position(callback, event_id, leaderboard_id, fields=fields)

    def get_player_data(self, callback, fields=None):
        return self._data_source.get_player_data(callback, fields=fields)


class WgrmsAccessor(BaseAccessor):

    def hof_user_info(self, callback):
        return self._data_source.hof_user_info(callback)

    def hof_user_exclude(self, callback):
        return self._data_source.hof_user_exclude(callback)

    def hof_user_restore(self, callback):
        return self._data_source.hof_user_restore(callback)


class PromoScreensAccessor(BaseAccessor):

    def get_teaser(self, callback):
        return self._data_source.get_teaser(callback)

    def send_teaser(self, callback, promo_id):
        return self._data_source.send_teaser(callback, promo_id)

    def get_unread_count(self, callback):
        return self._data_source.get_unread_count(callback)

    def client_promo_log(self, callback, data):
        return self._data_source.client_promo_log(callback, data)


class BattlePassAccessor(BaseAccessor):

    def get_video_data(self, callback, season_id, level, has_bp, vote_id):
        return self._data_source.get_video_data(callback, season_id, level, has_bp, vote_id)

    def get_voting_data(self, callback, feature_id, seasons):
        return self._data_source.get_voting_data(callback, feature_id, seasons)


class BobAccessor(BaseAccessor):

    def get_teams(self, callback):
        return self._data_source.get_teams(callback)

    def get_team_skills(self, callback, timestamp):
        return self._data_source.get_team_skills(callback, timestamp)


class Requester(object):
    available_data_sources = {'stagings': StagingDataAccessor,
     'fake': FakeDataAccessor,
     'gateway': GatewayDataAccessor}
    advent_calendar = RequestDescriptor(AdventCalendarAccessor)
    global_map = RequestDescriptor(GmAccessor)
    ratings = RequestDescriptor(RatingAccessor)
    strongholds = RequestDescriptor(StrongholdsAccessor)
    clans = RequestDescriptor(ClansAccessor)
    exporter = RequestDescriptor(ExporterAccessor)
    spa = RequestDescriptor(SpaAccessor)
    wgsh = RequestDescriptor(WgshAccessor)
    rblb = RequestDescriptor(RblbAccessor)
    wgelen = RequestDescriptor(WGElenAccessor)
    wgrms = RequestDescriptor(WgrmsAccessor)
    promo_screens = RequestDescriptor(PromoScreensAccessor)
    freya = RequestDescriptor(FreyaAccessor)
    battle_pass = RequestDescriptor(BattlePassAccessor)
    wgbob = RequestDescriptor(BobAccessor)
    craftmachine = RequestDescriptor(CrafmachineAccessor)

    @classmethod
    def create_requester(cls, url_fetcher, config, client_lang=None, user_agent=None):
        data_accessor = cls.available_data_sources[config.type](url_fetcher, config.url, client_lang=client_lang, user_agent=user_agent)
        return cls(data_accessor)

    def __init__(self, data_source):
        self.data_source = data_source

    @bigworld_wrapped
    def login(self, callback, account_id, token):
        self.data_source.login(callback, account_id, token)

    @bigworld_wrapped
    def logout(self, callback):
        self.data_source.logout(callback)

    @bigworld_wrapped
    def get_alive_status(self, callback):
        self.data_source.get_alive_status(callback)
