# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/client_request_lib/data_sources/fake.py
"""
Created on Jul 1, 2015

@author: oleg
"""
from functools import wraps, partial
from datetime import datetime, timedelta, time as dt_time
import random
from client_request_lib import exceptions
from client_request_lib.data_sources import base
EXAMPLES = {}

def _doResponse(callback, result, status_code, response_code):
    callback(result, status_code, response_code)


def fake_method(example):

    def wrapper(func):

        @wraps(func)
        def wrapped(self, callback, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
                response_code = exceptions.ResponseCodes.NO_ERRORS
                status_code = 200
            except exceptions.BaseRequestError as e:
                result = {'description': e.description}
                status_code = e.status_code
                response_code = e.response_code
            except:
                raise
                result = 'Internal error'
                status_code = 500
                response_code = exceptions.ResponseCodes.UNKNOWN_ERROR

            _doResponse(callback, result, status_code, response_code)

        name = func.__name__
        if 'get_' in name:
            name = name.split('get_', 1)[-1]
        EXAMPLES[name] = example
        return wrapped

    return wrapper


def paginated_method(func):

    @wraps(func)
    def wrapped(*args, **kwargs):
        offset = kwargs.pop('offset') or 0
        limit = kwargs.pop('limit') or 18
        diapasone = slice(offset, offset + limit)
        get_total_count = kwargs.pop('get_total_count', False)
        result = func(*args, **kwargs)
        total = len(result)
        result = {'items': result[diapasone]}
        if get_total_count:
            result['total'] = total
        return result

    return wrapped


class FakeDataAccessor(base.BaseDataAccessor):
    """
    obtain fake data
    
    `FakeDataAccessor` should be used for test purposes when one want emulate
    expected backend response
    
    :Example:
    
    >>> fake_accessor = FakeDataAccessor()
    >>> requester = Requester(fake_accessor)
    >>> requester.login(str, 12312, 'sdfee23e2')
    >>> def printer (*args, **kwargs):
                    pprint(args)
    ...
    >>> requester.clans.get_account_applications_count_since(printer, 123)
    (
            {'total': 17},
            200,
            0
    )
    
    Use `requests_before_logout` to emulate session expiration.
    Session will be considered as expired when `requests_before_logout` is made
    use -1 for endless session (default behavior)
    
    :Example:
    
    >>> fake_accessor = FakeDataAccessor()
    >>> fake_accessor.requests_before_logout = 2
    >>> requester = Requester(fake_accessor)
    >>> requester.login(str, 12312, 'sdfee23e2')
    >>> def printer (*args, **kwargs):
                    print (args)
    ...
    >>> requester.clans.get_account_applications_count_since(printer, 123)
    ({'total': 17}, 200, 0)
    >>> requester.clans.get_account_applications_count_since(printer, 123)
    ({'total': 17}, 200, 0)
    >>> requester.clans.get_account_applications_count_since(printer, 123)
    ('User is not authentificated', 403, 2)
    
    To set expected result for method use `set_data` method
    
    :Example:
    
    >>> fake_accessor = FakeDataAccessor()
    >>> requester = Requester(fake_accessor)
    >>> requester.login(str, 12312, 'sdfee23e2')
    >>> def printer (*args, **kwargs):
                    print (args)
    >>> fake_accessor.set_data('account_applications_count_since', 14, {'total': 11})
    >>> requester.clans.get_account_applications_count_since(printer, 14)
    ({'total': 11}, 200, 0)
    >>> requester.clans.get_account_applications_count_since(printer, 123)
    ({'total': 17}, 200, 0)
    
    To emulate error in response set data to error instance
    
    :Example:
    
    >>> fake_accessor = FakeDataAccessor()
    >>> requester = Requester(fake_accessor)
    >>> requester.login(str, 12312, 'sdfee23e2')
    >>> def printer (*args, **kwargs):
                    print (args)
    >>> fake_accessor.set_data('account_applications_count_since', 14, exceptions.PermissionDenied())
    >>> requester.clans.get_account_applications_count_since(printer, 14)
    ('Forbidden', 403, 3)
    >>> requester.clans.get_account_applications_count_since(printer, 123)
    ({'total': 17}, 200, 0)
    
    """
    requests_before_logout = -1

    def __init__(self, url_fetcher=None, config=None, client_lang=None, user_agent=None):
        super(FakeDataAccessor, self).__init__()
        self.client_lang = client_lang
        self._account = None
        self._storage = {}
        self.account = None
        self.user_agent = user_agent
        return

    def login(self, callback, account_id, spa_token):
        self.account = account_id
        self._account = self.requests_before_logout
        result, status_code = ('ok', 200)
        response_code = exceptions.ResponseCodes.NO_ERRORS
        _doResponse(callback, result, status_code, response_code)

    def get_alive_status(self, callback):
        result, status_code = {'status': 'I am alive!'}, 200
        response_code = exceptions.ResponseCodes.NO_ERRORS
        _doResponse(callback, result, status_code, response_code)

    def logout(self, callback):
        self.account = None
        self._account = None
        result, status_code = ('ok', 200)
        response_code = exceptions.ResponseCodes.NO_ERRORS
        _doResponse(callback, result, status_code, response_code)
        return

    def _filter_data(self, data, fields):
        if isinstance(data, list):
            return [ self._filter_data(i, fields) for i in data ]
        return {k:v for k, v in data.iteritems() if k in fields}

    def _request_data(self, section, entity_id, fields=None):
        if not self._account:
            raise exceptions.AuthentificationError()
        self._account -= 1
        try:
            result = self._storage[section][entity_id]
        except KeyError:
            result = EXAMPLES[section]
            if callable(result):
                result = result(entity_id)
                self._storage.setdefault(section, {})[entity_id] = result

        if isinstance(result, exceptions.BaseRequestError):
            raise result
        if fields:
            result = self._filter_data(result, fields)
        return result

    def _compare_keys(self, example, data):
        if isinstance(example, list):
            for i in data:
                self._compare_keys(example[0], i)

        if isinstance(example, dict):
            if set(example) ^ set(data):
                missed = set(example) - set(data)
                extra = set(data) - set(example)
                message = []
                if missed:
                    message.append('(%s) keys are missed' % ', '.join(missed))
                if extra:
                    message.append('(%s) keys are not needed' % ', '.join(extra))
                raise ValueError(' and '.join(message))

    def set_data(self, section, entity_id, data):
        """
        set fake data for different sections, compare keys while setting
        
        possible sections are following:
        
                - account_applications_count_since
                - account_invites
                - accounts_clans
                - accounts_info
                - accounts_names
                - clan_applications
                - clan_globalmap_stats
                - clan_invites_count_since
                - clan_invites
                - clan_members
                - clan_provinces
                - clans_info
                - clans_ratings
                - fronts_info
                - search_clans
                - stronghold_info
                - strongholds_state
                - strongholds_statistics
        
        """
        assert section in EXAMPLES
        example = EXAMPLES[section]
        if not isinstance(data, exceptions.BaseRequestError):
            self._compare_keys(example, data)
        self._storage.setdefault(section, {})[entity_id] = data

    @fake_method(example=lambda clan_id: {'clan_id': clan_id,
     'xp_avg': random.randrange(1, 1000) / 10.0,
     'efficiency': random.randrange(1, 10000),
     'battles_count_avg': random.randrange(1, 10000),
     'wins_ratio_avg': random.randrange(1, 100),
     'gm_elo_rating_6': random.randrange(1, 1000),
     'gm_elo_rating_8': random.randrange(1, 1000),
     'gm_elo_rating_10': random.randrange(1, 1000),
     'gm_elo_rating_6_rank': random.randrange(1, 1000),
     'gm_elo_rating_8_rank': random.randrange(1, 1000),
     'gm_elo_rating_10_rank': random.randrange(1, 1000),
     'fb_elo_rating_8': random.randrange(1, 1000),
     'fb_elo_rating_10': random.randrange(1, 1000),
     'fb_battles_count_10_28d': random.randrange(1, 100),
     'fs_battles_count_10_28d': random.randrange(1, 100),
     'gm_battles_count_28d': random.randrange(1, 100),
     'fs_battles_count_28d': random.randrange(1, 100),
     'fb_battles_count_28d': random.randrange(1, 100)})
    def get_clans_ratings(self, clan_ids, fields=None):
        """
        return fake data from `clans_ratings` section
        """
        return [ self._request_data('clans_ratings', i, fields=fields) for i in clan_ids ]

    @fake_method(example=lambda clan_id: {'name': 'xxx',
     'tag': 'ff',
     'motto': 'yyyy',
     'leader_id': 666,
     'members_count': 13,
     'clan_id': clan_id,
     'created_at': datetime.now(),
     'accepts_join_requests': True,
     'treasury': 2423})
    def get_clans_info(self, clan_ids, fields=None):
        """
        return fake data from `clans_info` section
        """
        return [ self._request_data('clans_info', clan_id, fields=fields) for clan_id in clan_ids ]

    @fake_method(example=lambda acc_id: {'id': acc_id,
     'name': 'name'})
    def get_accounts_names(self, account_ids, fields=None):
        """
        return fake data from `accounts_names` section
        """
        return [ self._request_data('accounts_names', account_id, fields=fields) for account_id in account_ids ]

    @fake_method(example=lambda clan_id: [ {'account_id': 2324 + i,
     'role_name': 'officer',
     'role_bw_flag': 1 << i,
     'clan_id': clan_id,
     'joined_at': datetime.now()} for i in range(11) ])
    def get_clan_members(self, clan_id, fields=None):
        """
        return fake data from `clan_members` section
        """
        return self._request_data('clan_members', clan_id, fields=fields)

    @fake_method(example={'clan_id': 2790,
     'favorite_arena_6': 1,
     'favorite_arena_8': 3,
     'favorite_arena_10': 65549,
     'favorite_primetime': dt_time(19, 0)})
    def get_clan_favorite_attributes(self, clan_id, fields=None):
        """
        return fake data from `clan_favorite_attributes` section
        """
        return self._request_data('clan_favorite_attributes', clan_id, fields=fields)

    @fake_method(example={'total': 17})
    def get_account_applications_count_since(self, account_id, since=None):
        """
        return fake data from `account_applications_count_since` section
        """
        return self._request_data('account_applications_count_since', account_id)

    @fake_method(example={'total': 14})
    def get_clan_invites_count_since(self, clan_id, since=None):
        """
        return fake data from `clan_invites_count_since` section
        """
        return self._request_data('clan_invites_count_since', clan_id)

    @fake_method(example={'account_id': 234,
     'joined_at': datetime.now(),
     'clan_id': 343,
     'role_bw_flag': 13,
     'role_name': 'commander',
     'in_clan_cooldown_till': datetime.now()})
    def get_accounts_clans(self, account_ids, fields):
        """
        return fake data from `accounts_clans` section
        """
        return [ self._request_data('accounts_clans', i, fields=fields) for i in account_ids ]

    @fake_method(example=lambda (account_id, statuses): [ {'status': random.choice(statuses or ('active', 'declined', 'cancelled', 'accepted', 'expired', 'error', 'deleted')),
     'created_at': datetime.now(),
     'updated_at': datetime.now(),
     'sender_id': random.randrange(1, 10000),
     'id': random.randrange(1, 1000000),
     'account_id': account_id,
     'clan_id': random.randrange(1, 10000),
     'status_changer_id': random.randrange(1, 10000),
     'comment': 'Welcome {}!'.format(random.randrange(1, 10000)) if random.choice((1, 0)) else ''} for i in range(random.randrange(0, 1000)) ])
    @paginated_method
    def get_account_applications(self, fields=None, statuses=None):
        """
        return fake data from `account_applications` section
        """
        return self._request_data('account_applications', (self.account, tuple(statuses or [])), fields=fields)

    @fake_method(example=lambda (clan_id, statuses): [ {'status': random.choice(statuses or ('active', 'declined', 'cancelled', 'accepted', 'expired', 'error', 'deleted')),
     'created_at': datetime.now(),
     'updated_at': datetime.now(),
     'sender_id': random.randrange(1, 10000),
     'id': random.randrange(1, 1000000),
     'account_id': random.randrange(1, 10000),
     'clan_id': clan_id,
     'status_changer_id': random.randrange(1, 10000),
     'comment': 'Welcome {}!'.format(random.randrange(1, 10000)) if random.choice((1, 0)) else ''} for i in range(random.randrange(0, 1000)) ])
    @paginated_method
    def get_clan_applications(self, clan_id, fields=None, statuses=None):
        """
        return fake data from `clan_applications` section
        """
        return self._request_data('clan_applications', (clan_id, tuple(statuses or [])), fields=fields)

    @fake_method(example=lambda search: ([] if len(search) % 2 else [ {'name': 'Clan Name %d' % random.randrange(1, 1000),
     'tag': 'TCLAN',
     'motto': 'Clan Motto',
     'leader_id': random.randrange(1, 10000),
     'clan_id': random.randrange(1, 100),
     'members_count': random.randrange(1, 50),
     'created_at': datetime.now(),
     'accepts_join_requests': random.choice((True, False))} for i in range(random.randrange(1, 36)) ]))
    @paginated_method
    def search_clans(self, search, fields=None):
        """
        return fake data from `clans_info` section
        """
        return self._request_data('search_clans', search)

    @fake_method(example=lambda account: [ {'name': 'Clan Name %d' % random.randrange(1, 1000),
     'tag': 'TCLAN',
     'motto': 'Clan Motto',
     'leader_id': random.randrange(1, 10000),
     'clan_id': random.randrange(1, 100),
     'members_count': random.randrange(1, 50),
     'created_at': datetime.now(),
     'accepts_join_requests': random.choice((True, False))} for i in range(random.randrange(1, 36)) ])
    @paginated_method
    def get_recommended_clans(self, fields=None):
        """
        return fake data from `clans_info` section
        """
        return self._request_data('recommended_clans', self.account)

    @fake_method(example=lambda (clan_id, statuses): [ {'status': random.choice(statuses or ('active', 'declined', 'cancelled', 'accepted', 'expired', 'error', 'deleted')),
     'created_at': datetime.now(),
     'updated_at': datetime.now(),
     'sender_id': random.randrange(1, 10000),
     'id': random.randrange(1, 1000000),
     'account_id': random.randrange(1, 10000),
     'clan_id': clan_id,
     'comment': 'Welcome {}!'.format(random.randrange(1, 10000)) if random.choice((1, 0)) else '',
     'status_changer_id': 2132} for i in range(random.randrange(0, 1000)) ])
    @paginated_method
    def get_clan_invites(self, clan_id, fields=None, statuses=None):
        """
        return fake data from `clan_invites` section
        """
        return self._request_data('clan_invites', (clan_id, tuple(statuses or [])), fields=fields)

    @fake_method(example=lambda (account_id, statuses): [ {'status': random.choice(statuses or ('active', 'declined', 'cancelled', 'accepted', 'expired', 'error', 'deleted')),
     'created_at': datetime.now(),
     'updated_at': datetime.now(),
     'sender_id': random.randrange(1, 10000),
     'id': random.randrange(1, 1000000),
     'account_id': account_id,
     'clan_id': random.randrange(1, 10000),
     'status_changer_id': 2132,
     'comment': 'Welcome {}!'.format(random.randrange(1, 10000)) if random.choice((1, 0)) else ''} for i in range(random.randrange(0, 1000)) ])
    @paginated_method
    def get_account_invites(self, fields=None, statuses=None):
        """
        return fake data from `account_invites` section
        """
        return self._request_data('account_invites', (self.account, tuple(statuses or [])), fields=fields)

    @fake_method(example=lambda account_id: {'global_rating': random.randrange(100, 10000),
     'battle_avg_xp': random.randrange(100, 10000),
     'battles_count': random.randrange(1, 1000),
     'battle_avg_performance': random.uniform(0, 1),
     'xp_amount': random.randrange(100, 1000),
     'account_id': account_id})
    def get_accounts_info(self, account_ids, fields=None):
        """
        return fake data from `accounts_info` section
        """
        return [ self._request_data('accounts_info', acc_id, fields=fields) for acc_id in account_ids ]

    @fake_method(example=[{'front_name': 'some_front',
      'province_id': 'some_province',
      'front_name_localized': 'some_front_localized',
      'province_id_localized': 'some_province_localized',
      'revenue': 324,
      'hq_connected': True,
      'prime_time': dt_time(18, 0, 0),
      'periphery': 333,
      'game_map': 'some_map',
      'pillage_cooldown': 1,
      'pillage_end_datetime': datetime.now() + timedelta(hours=3),
      'turns_owned': 12}, {'front_name': 'some_front2',
      'province_id': 'some_province2',
      'front_name_localized': 'some_front_localized2',
      'province_id_localized': 'some_province_localized2',
      'revenue': 333,
      'hq_connected': True,
      'prime_time': dt_time(19, 0, 0),
      'periphery': 444,
      'game_map': 'some_map2',
      'pillage_cooldown': None,
      'pillage_end_datetime': None,
      'turns_owned': 12,
      'arena_id': 5}])
    def get_clan_provinces(self, clan_id, fields=None):
        """
        return fake data from `clan_provinces` section
        """
        return self._request_data('clan_provinces', clan_id, fields=fields)

    @fake_method(example={'battles_lost': 12,
     'influence_points': 121,
     'provinces_captured': 23,
     'provinces_count': 234,
     'battles_played': 332,
     'battles_won': 232,
     'battles_played_on_6_level': 21,
     'battles_won_on_6_level': 12,
     'battles_played_on_8_level': 32,
     'battles_won_on_8_level': 21,
     'battles_played_on_10_level': 43,
     'battles_won_on_10_level': 23})
    def get_clan_globalmap_stats(self, clan_id, fields=None):
        """
        return fake data from `clan_globalmap_stats` section
        """
        return self._request_data('clan_globalmap_stats', clan_id, fields=fields)

    @fake_method(example=[{'front_name': 'front_name',
      'front_name_localized': 'front_name_localized',
      'min_vehicle_level': 2,
      'max_vehicle_level': 4}])
    def get_fronts_info(self, front_names=None, fields=None):
        """
        return fake data from `fronts_info` section
        """
        return self._request_data('fronts_info', front_names, fields=fields)

    @fake_method(example={'defence_mode_is_activated': True,
     'defence_hour': dt_time(10, 0),
     'sortie_battles_count': 23,
     'sortie_wins': 12,
     'sortie_losses': 19,
     'sortie_fort_resource_in_absolute': 100,
     'sortie_fort_resource_in_champion': 71,
     'sortie_fort_resource_in_middle': 60,
     'defence_battles_count': 234,
     'defence_combat_wins': 21,
     'sortie_middle_battles_count': 12,
     'sortie_champion_battles_count': 32,
     'sortie_absolute_battles_count': 23,
     'defence_enemy_base_capture_count': 43,
     'defence_capture_enemy_building_total_count': 55,
     'defence_loss_own_building_total_count': 65,
     'defence_attack_efficiency': 23.2,
     'defence_success_attack_count': 122,
     'defence_attack_count': 13,
     'defence_defence_efficiency': 32.2,
     'defence_defence_count': 24,
     'defence_success_defence_count': 5,
     'total_resource_amount': 321,
     'defence_resource_loss_count': 112,
     'defence_resource_capture_count': 322,
     'fb_battles_count_8': 23,
     'fb_battles_count_10': 12,
     'level': 2,
     'buildings': [{'type': 1,
                    'direction': 0,
                    'level': 2,
                    'position': 2}, {'type': 2,
                    'direction': 1,
                    'level': 3,
                    'position': 2}]})
    def get_stronghold_info(self, clan_id, fields=None):
        """
        return fake data from `stronghold_info` section
        """
        return self._request_data('stronghold_info', clan_id, fields=fields)

    @fake_method(example={'buildings_count': 4,
     'directions_count': 3,
     'buildings': [{'type': 1,
                    'hp': 32,
                    'storage': 123,
                    'level': 4,
                    'position': 7,
                    'direction': 1}],
     'directions': [1, 2],
     'off_day': 3,
     'vacation_start': datetime.utcnow() + timedelta(days=1),
     'vacation_finish': datetime.utcnow() + timedelta(days=4),
     'periphery_id': 333,
     'clan_tag': 'tag',
     'clan_name': 'some_name',
     'clan_id': 21,
     'level': 2,
     'sortie_wins_period': 7,
     'sortie_battles_wins_percentage_period': 20.0,
     'sortie_battles_count_period': 122,
     'defence_battles_count_period': 21})
    def get_strongholds_statistics(self, clan_id, fields=None):
        """
        return fake data from `strongholds_statistics` section
        """
        return self._request_data('strongholds_statistics', clan_id, fields=fields)

    @fake_method(example={'clan_id': 234,
     'defence_hour': dt_time(10, 0)})
    def get_strongholds_state(self, clan_id, fields=None):
        """
        return fake data from `strongholds_state` section
        """
        return self._request_data('strongholds_state', clan_id, fields=fields)

    @fake_method(example=[{'clan_id': 234,
      'account_id': 3,
      'id': 23}])
    def create_invites(self, clan_id, account_ids, comment, fields=None):
        """
        return fake data from `create_invites` section
        """
        return self._request_data('create_invites', (clan_id, account_ids), fields=fields)

    @fake_method(example=[{'clan_id': 224,
      'account_id': 3,
      'id': 123}])
    def create_applications(self, clan_ids, comment, fields=None):
        """
        return fake data from `create_applications` section
        """
        return self._request_data('create_applications', clan_ids, fields=fields)

    @fake_method(example=lambda obj_id: {'transaction_id': 213,
     'id': obj_id,
     'account_id': 343,
     'clan_id': 17})
    def accept_application(self, application_id, fields=None):
        """
        return fake data from `accept_application` section
        """
        return self._request_data('accept_application', application_id, fields=fields)

    @fake_method(example=lambda obj_id: {'id': obj_id,
     'account_id': 343,
     'clan_id': 17})
    def decline_application(self, application_id, fields=None):
        """
        return fake data from `decline_application` section
        """
        return self._request_data('decline_application', application_id, fields=fields)

    @fake_method(example=lambda obj_id: {'transaction_id': 213,
     'id': obj_id,
     'account_id': 343,
     'clan_id': 17})
    def accept_invite(self, invite_id, fields=None):
        """
        return fake data from `accept_invite` section
        """
        return self._request_data('accept_invite', invite_id, fields=fields)

    @fake_method(example=lambda obj_id: {'id': obj_id,
     'account_id': 343,
     'clan_id': 17})
    def decline_invite(self, invite_id, fields=None):
        """
        return fake data from `decline_invite` section
        """
        return self._request_data('decline_invite', invite_id, fields=fields)

    @fake_method(example=[{'id': 991,
      'account_id': 1001,
      'clan_id': 19}, {'id': 992,
      'account_id': 1001,
      'clan_id': 19}, {'id': 993,
      'account_id': 1001,
      'clan_id': 19}])
    def bulk_decline_invites(self, invite_ids):
        """
        return fake data from `bulk_decline_invites` section
        """
        return self._request_data('bulk_decline_invites', invite_ids)

    @fake_method(example={'permissions': {'manage_reserves': ['commander',
                                         'combat_officer',
                                         'executive_officer',
                                         'personnel_officer']},
     'time_to_ready': 900,
     'max_level': 10,
     'battle_series_duration': 3600,
     'enemy_clan': None,
     'industrial_resource_multiplier': 1,
     'max_players_count': 15,
     'type': 'FORT_BATTLE',
     'max_legionaries_count': 0,
     'available_reserves': {'ARTILLERY_STRIKE': [],
                            'HIGH_CAPACITY_TRANSPORT': [],
                            'REQUISITION': [],
                            'AIRSTRIKE': []},
     'direction': 'A',
     'min_players_count': 1,
     'matchmaker_next_tick': 1475578800,
     'battle_series_status': [{'battle_reward': 0,
                               'gameplay_id': 0,
                               'geometry_id': 6,
                               'first_resp_clan_id': None,
                               'second_resp_clan_id': None,
                               'attacker': None,
                               'clan_owner_id': 14000012972L,
                               'current_battle': False,
                               'map_id': 6}, {'battle_reward': 0,
                               'gameplay_id': 0,
                               'geometry_id': 14,
                               'first_resp_clan_id': None,
                               'second_resp_clan_id': None,
                               'attacker': None,
                               'clan_owner_id': 14000012972L,
                               'current_battle': False,
                               'map_id': 14}, {'battle_reward': 0,
                               'gameplay_id': 0,
                               'geometry_id': 20,
                               'first_resp_clan_id': None,
                               'second_resp_clan_id': None,
                               'attacker': None,
                               'clan_owner_id': 14000012972L,
                               'current_battle': False,
                               'map_id': 20}],
     'battle_duration': 600,
     'requisition_bonus_percent': None,
     'public': False,
     'selected_reserves': [None, None, None],
     'min_level': 1})
    def get_wgsh_unit_info(self, periphery_id, unit_id, fields=None):
        """
        return fake data from `wgsh_unit_info` section
        """
        return self._request_data('wgsh_unit_info', unit_id)

    @fake_method(example={})
    def set_vehicle(self, periphery_id, unit_id, vehicle_cd, fields=None):
        """
        return fake data from `set_vehicle` section
        """
        return self._request_data('set_vehicle', unit_id)

    @fake_method(example={})
    def set_readiness(self, periphery_id, unit_id, is_ready, reset_vehicle, fields=None):
        """
        return fake data from `set_readiness` section
        """
        return self._request_data('set_readiness', unit_id)

    @fake_method(example={})
    def invite_players(self, periphery_id, unit_id, accounts_to_invite, comment, fields=None):
        """
        return fake data from `invite_players` section
        """
        return self._request_data('invite_players', unit_id)

    @fake_method(example={})
    def assign_player(self, periphery_id, unit_id, account_to_assign, fields=None):
        """
        return fake data from `assign_player` section
        """
        return self._request_data('assign_player', unit_id)

    @fake_method(example={})
    def unassign_player(self, periphery_id, unit_id, account_to_assign, fields=None):
        """
        return fake data from `unassign_player` section
        """
        return self._request_data('unassign_player', unit_id)

    @fake_method(example={})
    def give_leadership(self, periphery_id, unit_id, account_to_assign, fields=None):
        """
        return fake data from `give_leadership` section
        """
        return self._request_data('give_leadership', unit_id)

    @fake_method(example={})
    def leave_room(self, periphery_id, unit_id, fields=None):
        """
        return fake data from `leave_room` section
        """
        return self._request_data('leave_room', unit_id)

    @fake_method(example={})
    def take_away_leadership(self, periphery_id, unit_id, fields=None):
        """
        return fake data from `take_away_leadership` section
        """
        return self._request_data('take_away_leadership', unit_id)

    @fake_method(example={})
    def kick_player(self, periphery_id, unit_id, account_to_assign, fields=None):
        """
        return fake data from `kick_player` section
        """
        return self._request_data('kick_player', unit_id)

    @fake_method(example={})
    def set_open(self, periphery_id, unit_id, is_open, fields=None):
        """
        return fake data from `set_open` section
        """
        return self._request_data('set_open', unit_id)

    @fake_method(example={})
    def lock_reserve(self, periphery_id, unit_id, reserve_id, fields=None):
        """
        return fake data from `lock_reserve` section
        """
        return self._request_data('lock_reserve', unit_id)

    @fake_method(example={})
    def unlock_reserve(self, periphery_id, unit_id, reserve_id, fields=None):
        """
        return fake data from `unlock_reserve` section
        """
        return self._request_data('unlock_reserve', unit_id)

    @fake_method(example=lambda clan_id: {'skirmishes_statistics': {'last_28_days_battles_count': 1,
                               'last_28_days_wins_count': 1,
                               'wins_count': 1,
                               'loses_count': 1,
                               'draws_count': 1},
     'battles_statistics': {'last_28_days_battles_count': 1,
                            'last_28_days_wins_count': 1,
                            'wins_count': 1,
                            'loses_count': 1,
                            'draws_count': 1},
     'skirmishes_count_last_28_days': 1,
     'battles_count_last_28_days': 1,
     'clear_wins_count': 1,
     'level_6_statistics': {'wins_count': 1,
                            'battles_count': 1},
     'level_8_statistics': {'wins_count': 1,
                            'battles_count': 1},
     'level_10_statistics': {'wins_count': 1,
                             'battles_count': 1}})
    def clan_statistics(self, clan_id, fields=None):
        """
        return fake data from `clan_statistics` section
        """
        return self._request_data('clan_statistics', clan_id)

    @fake_method(example=lambda account_id: {'skirmishes_statistics': {'wins_count': 1,
                               'loses_count': 1,
                               'draws_count': 1},
     'battles_statistics': {'wins_count': 1,
                            'loses_count': 1,
                            'draws_count': 1},
     'industrial_resource_total': {'random_battles': 1,
                                   'skirmishes': 1,
                                   'battles': 1},
     'industrial_resource_last_28_days': {'random_battles': 1,
                                          'skirmishes': 1,
                                          'battles': 1}})
    def account_statistics(self, account_id, fields=None):
        """
        return fake data from `account_statistics` section
        """
        return self._request_data('account_statistics', account_id)

    @fake_method(example={})
    def join_room(self, periphery_id, unit_id, fields=None):
        """
        return fake data from `join_room` section
        """
        return self._request_data('join_room', unit_id)
