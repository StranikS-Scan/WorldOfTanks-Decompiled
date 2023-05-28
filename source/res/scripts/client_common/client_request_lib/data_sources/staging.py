# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/client_request_lib/data_sources/staging.py
from itertools import groupby
import json
from urllib import urlencode
from functools import wraps
from datetime import datetime, time as dt_time
from client_request_lib import exceptions
from client_request_lib.data_sources import base
import functools

def _doResponse(callback, result, status_code, response_code):
    callback(result, status_code, response_code)


EXAMPLES = {}
SUCCESS_STATUSES = [200, 201, 304]

def convert_data(data_mapping, paginated=False):

    def wrapper(func):

        @functools.wraps(func)
        def wrapped(self, callback, *args, **kwargs):

            def new_callback(data, *args, **kwargs):
                for field, converter in data_mapping.items():
                    listed_data = data
                    if paginated:
                        listed_data = data.get('items', [])
                    if not isinstance(listed_data, list):
                        listed_data = [listed_data]
                    for portion in listed_data:
                        if field in portion:
                            portion[field] = converter(portion[field])

                callback(data, *args, **kwargs)

            func(self, new_callback, *args, **kwargs)

        return wrapped

    return wrapper


def from_iso(iso_date):
    if iso_date:
        if '.' in iso_date:
            format = '%Y-%m-%dT%H:%M:%S.%f'
        else:
            format = '%Y-%m-%dT%H:%M:%S'
        return datetime.strptime(iso_date, format)
    return iso_date


def timestamp_to_datetime(timestamp):
    return timestamp and datetime.fromtimestamp(timestamp)


def translate_field_names(response, field_mapping, requested_fields=None):
    if requested_fields:
        field_mapping = {k:v for k, v in field_mapping.iteritems() if k in requested_fields}
    if isinstance(response, list):
        return [ translate_field_names(i, field_mapping) for i in response ]
    backward_mapping = sorted([ (v, k) for k, v in field_mapping.iteritems() ])
    result = {}
    for key, field_iter in groupby(backward_mapping, key=lambda x: x[0].split('.', 1)[0]):
        inner_mapping = {}
        sibling_mapping = {}
        our = ''
        for their, our in field_iter:
            if '.' in their:
                if '.' in our:
                    inner_mapping[our.split('.', 1)[1]] = their.split('.', 1)[1]
                else:
                    sibling_mapping[our] = their.split('.', 1)[1]
            if their in response:
                result[our] = response[their]

        if key in response:
            if sibling_mapping:
                siblings = translate_field_names(response[key], sibling_mapping)
                result.update(siblings)
            if inner_mapping:
                result.update({our.split('.')[0]: translate_field_names(response[key], inner_mapping)})

    return result


def generate_docstring_mapping(field_mapping):
    result = ['\n        .. list-table::\n            :widths: 50 50\n            :header-rows: 1\n\n            * - client_request_lib\n            - Backend\n    ']
    for our, their in field_mapping.iteritems():
        row = '\n            * - ``{our}``\n            - ``{their}``\n        '.format(our=our, their=their)
        result.append(row)

    return ''.join(result)


def mapped_fields(field_mapping, paginated=False, accept_fields_argument=True):

    def wrapper(func):

        @wraps(func)
        def wrapped(self, callback, *args, **kwargs):
            old_fields = None
            if accept_fields_argument:
                if kwargs.get('fields'):
                    old_fields = kwargs['fields']
                    kwargs['fields'] = [ field_mapping[f] for f in kwargs['fields'] ]
                else:
                    old_fields = field_mapping.keys()
                    kwargs['fields'] = field_mapping.values()
                if paginated and kwargs.get('get_total_count'):
                    kwargs['fields'].append('total')

            def wrapped_callback(response, status_code, response_code):
                if status_code in SUCCESS_STATUSES:
                    if paginated:
                        new_response = {'items': [ translate_field_names(i, field_mapping, requested_fields=old_fields) for i in response['items'] ]}
                        if kwargs.get('get_total_count'):
                            new_response['total'] = response['total']
                        response = new_response
                    elif isinstance(response, list):
                        response = [ translate_field_names(i, field_mapping, requested_fields=old_fields) for i in response ]
                    else:
                        response = translate_field_names(response, field_mapping, requested_fields=old_fields)
                callback(response, status_code, response_code)

            func(self, wrapped_callback, *args, **kwargs)
            return

        if wrapped.__doc__ is not None:
            wrapped.__doc__ = '\n\n'.join([wrapped.__doc__, generate_docstring_mapping(field_mapping)])
        return wrapped

    return wrapper


def get_clan_error(data):
    error_map = {'DATA_ERROR': exceptions.BadRequest,
     'SPA_ERROR': exceptions.SpaError,
     'PERMISSION_DENIED': exceptions.PermissionDenied,
     'ACCOUNT_ALREADY_IN_CLAN': exceptions.AccountInClanError,
     'ACCOUNT_NOT_IN_CLAN': exceptions.AccountNotInClanError,
     'STRONGHOLD_NOT_FOUND': exceptions.StrongholdNotFoundError,
     'TOO_MANY_INVITES': exceptions.TooManyInvitesError,
     'WGCCFE_ERROR': exceptions.WgccfeError,
     'ACCOUNT_DOES_NOT_MEET_REQUIREMENTS': exceptions.AccountRequirementsError,
     'APPLICATION_DOES_NOT_EXIST': exceptions.ApplicationDoesNotExistError,
     'CLAN_ALREADY_DISBANDED': exceptions.ClanDisbandedError,
     'INVITE_IS_NOT_ACTIVE': exceptions.InviteIsNotActiveError,
     'CLAN_IS_FULL': exceptions.ClanIsFullError,
     'INVITE_DOES_NOT_EXIST': exceptions.InviteDoesNotExistError,
     'RECRUITING_POLICY_MISMATCH': exceptions.RecruitingPolicyError,
     'ACCOUNT_BANNED': exceptions.AccountBannedError,
     'TOO_MANY_APPLICATIONS': exceptions.TooManyApplicationsError,
     'APPLICATION_IS_NOT_ACTIVE': exceptions.ApplicationIsNotActiveError,
     'WGCCBE_ERROR': exceptions.WgccbeError,
     'CLAN_DOES_NOT_EXIST': exceptions.ClanDoesNotExistError,
     'UNKNOWN_ACCOUNT': exceptions.UnknownAccountError,
     'CLAN_IS_NOT_ACTIVE': exceptions.ClanIsNotActiveError}
    error_key = data and data['title']
    return error_map.get(error_key, exceptions.WgccbeError)


def get_stronghold_error(data):
    error_map = {'VALIDATION_ERROR': exceptions.BadRequest,
     'SPA_ACCOUNT_DOES_NOT_EXIST': exceptions.UnknownAccountError,
     'SPA_ERROR': exceptions.SpaError,
     'CLAN_DOES_NOT_EXIST': exceptions.ClanDoesNotExistError,
     'BE_ERROR': exceptions.WgccbeError,
     'CLAN_IS_DISBANDED': exceptions.ClanDisbandedError,
     'STRONGHOLD_NOT_FOUND': exceptions.StrongholdNotFoundError}
    error_key = data and data['error']
    return error_map.get(error_key, exceptions.WgccfeError)


def get_spa_error(data):
    return exceptions.SpaError


def get_global_map_error(data):
    return exceptions.GlobalMapError


def get_exporter_error(data):
    error = 'Ensure each value is less than or equal to 9223372036854775807.'
    return exceptions.BadRequest if data and error in data.get('account_ids', []) else exceptions.ExporterError


def get_ratings_error(data):
    return exceptions.WgrsError


def get_wgsh_error(data):
    return exceptions.WgshError


ERROR_MAP = {'ratings': get_ratings_error,
 'exporter': get_exporter_error,
 'global_map': get_global_map_error,
 'clans': get_clan_error,
 'spa': get_spa_error,
 'strongholds': get_stronghold_error,
 'wgsh': get_wgsh_error}

def preprocess_callback(callback, service):

    def wrapper(something):

        def wrapped(response, func=something):
            if response.responseCode not in SUCCESS_STATUSES:
                try:
                    data = json.loads(response.body)
                except:
                    data = None

                error = ERROR_MAP[service](data)
                return callback({'description': error.description}, error.status_code, error.response_code)
            else:
                data = json.loads(response.body)
                response_code = exceptions.ResponseCodes.NO_ERRORS
                if func:
                    data = func(data)
                callback(data, response.responseCode, response_code)
                return

        if not callable(something):
            return wrapped(something, func=None)
        else:
            functools.wraps(something)(wrapped)
            return wrapped

    return wrapper


class StagingDataAccessor(base.BaseDataAccessor):
    requests_before_logout = -1

    def __init__(self, url_fetcher, staging_hosts=None, client_lang=None, user_agent=None):
        self.client_lang = client_lang
        self._account = None
        self.url_fetcher = url_fetcher
        self.staging_hosts = staging_hosts or {}
        self.user_agent = user_agent
        return

    def login(self, callback, account_id, spa_token):
        self._account = account_id
        result, status_code = ('ok', 200)
        response_code = exceptions.ResponseCodes.NO_ERRORS
        callback(result, status_code, response_code)

    def logout(self, callback):
        self._account = None
        result, status_code = ('ok', 200)
        response_code = exceptions.ResponseCodes.NO_ERRORS
        callback(result, status_code, response_code)
        return

    def get_alive_status(self, callback):
        result, status_code = {'status': 'I am alive!'}, 200
        response_code = exceptions.ResponseCodes.NO_ERRORS
        callback(result, status_code, response_code)

    def _request_data(self, callback, service, url, method='GET', postData=None):
        service_host = self.staging_hosts[service].strip('/')
        url = '/'.join([service_host] + url.strip('/').split('/'))
        if '?' not in url:
            url = url + '/'
        args = [None, 30.0, method]
        if postData:
            args.append(json.dumps(postData))
        self.url_fetcher(url, callback, *args)
        return

    @mapped_fields({'efficiency': 'efficiency',
     'clan_id': 'clan_id',
     'battles_count_avg': 'battles_count_avg',
     'wins_ratio_avg': 'wins_ratio_avg',
     'xp_avg': 'xp_avg',
     'gm_elo_rating_6': 'gm_elo_rating_6',
     'gm_elo_rating_8': 'gm_elo_rating_8',
     'gm_elo_rating_10': 'gm_elo_rating_10',
     'gm_elo_rating_6_rank': 'gm_elo_rating_6_rank',
     'gm_elo_rating_8_rank': 'gm_elo_rating_8_rank',
     'gm_elo_rating_10_rank': 'gm_elo_rating_10_rank',
     'fb_elo_rating_8': 'fb_elo_rating_8',
     'fb_elo_rating_10': 'fb_elo_rating_10',
     'fb_battles_count_10_28d': 'fb_battles_count_10_28d',
     'fs_battles_count_10_28d': 'fs_battles_count_10_28d',
     'gm_battles_count_28d': 'gm_battles_count_28d',
     'fs_battles_count_28d': 'fs_battles_count_28d',
     'fb_battles_count_28d': 'fb_battles_count_28d'})
    def get_clans_ratings(self, callback, clan_ids, fields=None):
        get_params = {'project': 'api',
         'fields': ','.join(fields),
         'ids': ','.join(map(str, clan_ids))}
        url = 'api/wot/clans/bulks/?%s' % urlencode(get_params)

        @preprocess_callback(callback, 'ratings')
        def inner_callback(data):
            return data['data']

        return self._request_data(inner_callback, 'ratings', url)

    @convert_data({'created_at': from_iso})
    @mapped_fields({'name': 'name',
     'tag': 'tag',
     'motto': 'motto',
     'leader_id': 'leader_id',
     'members_count': 'members_count',
     'created_at': 'created_at',
     'clan_id': 'id',
     'treasury': 'treasury',
     'accepts_join_requests': 'accepts_join_requests'})
    def get_clans_info(self, callback, clan_ids, fields=None):
        get_params = {'ids': ','.join(map(str, clan_ids)),
         'fields': ','.join(fields)}
        url = '/clans/?%s' % urlencode(get_params)

        @preprocess_callback(callback, 'clans')
        def inner_callback(data):
            return data['items']

        return self._request_data(inner_callback, 'clans', url)

    @mapped_fields({'id': 'id',
     'name': 'name'})
    def get_accounts_names(self, callback, account_ids, fields=None):
        get_params = {'id': account_ids}
        url = '/spa/accounts/names/?%s' % urlencode(get_params, doseq=True)

        @preprocess_callback(callback, 'spa')
        def inner_callback(data):
            return [ {'id': k,
             'name': v} for k, v in data.iteritems() ]

        return self._request_data(inner_callback, 'spa', url)

    @convert_data({'joined_at': from_iso})
    @mapped_fields({'account_id': 'id',
     'joined_at': 'joined_at',
     'clan_id': 'clan_id',
     'role_bw_flag': 'role.bw_flag',
     'role_name': 'role.name'})
    def get_clan_members(self, callback, clan_id, fields=None):
        get_params = {'fields': ','.join(fields)}
        url = '/clans/%s/members?%s' % (clan_id, urlencode(get_params))
        return self._request_data(preprocess_callback(callback, 'clans'), 'clans', url)

    @convert_data({'favorite_primetime': lambda x: x and datetime.strptime(x, '%H:%M').time()})
    @mapped_fields({'favorite_arena_6': 'favorite_arena_6',
     'favorite_arena_8': 'favorite_arena_8',
     'favorite_arena_10': 'favorite_arena_10',
     'clan_id': 'clan_id',
     'favorite_primetime': 'favorite_primetime'})
    def get_clan_favorite_attributes(self, callback, clan_id, fields=None):
        get_params = {'clan_id': clan_id}
        url = '/gm/clans/favorite_attributes/?%s' % urlencode(get_params)
        return self._request_data(preprocess_callback(callback, 'clans'), 'clans', url)

    @convert_data({'joined_at': from_iso,
     'in_clan_cooldown_till': from_iso})
    @mapped_fields({'account_id': 'id',
     'joined_at': 'joined_at',
     'clan_id': 'clan_id',
     'role_bw_flag': 'role.bw_flag',
     'role_name': 'role.name',
     'in_clan_cooldown_till': 'in_clan_cooldown_till'})
    def get_accounts_clans(self, callback, account_ids, fields=None):
        get_params = {'fields': ','.join(fields),
         'ids': ','.join(map(str, account_ids))}
        url = '/accounts/?%s' % urlencode(get_params)

        @preprocess_callback(callback, 'clans')
        def inner_callback(data):
            return data['items']

        return self._request_data(inner_callback, 'clans', url)

    @mapped_fields({'total': 'total'}, accept_fields_argument=False)
    def get_account_applications_count_since(self, callback, account_id, since=None):
        get_params = {'fields': 'id',
         'account_id': account_id,
         'created_after': since.isoformat()}
        url = '/applications/?%s' % urlencode(get_params)
        return self._request_data(preprocess_callback(callback, 'clans'), 'clans', url)

    @mapped_fields({'total': 'total'}, accept_fields_argument=False)
    def get_clan_invites_count_since(self, callback, clan_id, since=None):
        get_params = {'fields': 'id',
         'clan_id': clan_id,
         'created_after': since.isoformat()}
        url = '/invites/?%s' % urlencode(get_params)
        return self._request_data(preprocess_callback(callback, 'clans'), 'clans', url)

    @convert_data({'created_at': from_iso,
     'updated_at': from_iso}, paginated=True)
    @mapped_fields({'status': 'status',
     'created_at': 'created_at',
     'updated_at': 'updated_at',
     'sender_id': 'sender_id',
     'id': 'id',
     'account_id': 'account_id',
     'clan_id': 'clan_id',
     'comment': 'data.comment',
     'status_changer_id': 'data.status_changer_id'}, paginated=True)
    def get_account_applications(self, callback, fields=None, statuses=None, get_total_count=False, limit=18, offset=0):
        statuses = statuses or ['active',
         'declined',
         'accepted',
         'expired',
         'error',
         'deleted']
        get_params = {'fields': ','.join(fields),
         'account_id': self._account,
         'statuses': ','.join(statuses),
         'limit': limit,
         'offset': offset}
        url = '/applications/?%s' % urlencode(get_params)
        return self._request_data(preprocess_callback(callback, 'clans'), 'clans', url)

    @convert_data({'created_at': from_iso,
     'updated_at': from_iso}, paginated=True)
    @mapped_fields({'status': 'status',
     'created_at': 'created_at',
     'updated_at': 'updated_at',
     'sender_id': 'sender_id',
     'id': 'id',
     'account_id': 'account_id',
     'clan_id': 'clan_id',
     'comment': 'data.comment',
     'status_changer_id': 'data.status_changer_id'}, paginated=True)
    def get_clan_applications(self, callback, clan_id, fields=None, statuses=None, get_total_count=False, limit=18, offset=0):
        statuses = statuses or ['active',
         'declined',
         'accepted',
         'expired',
         'error',
         'deleted']
        get_params = {'fields': ','.join(fields),
         'clan_id': clan_id,
         'statuses': ','.join(statuses),
         'limit': limit,
         'offset': offset}
        url = '/applications/?%s' % urlencode(get_params)
        return self._request_data(preprocess_callback(callback, 'clans'), 'clans', url)

    @mapped_fields({'clan_id': 'clan_id',
     'id': 'id',
     'account_id': 'account_id'})
    def create_applications(self, callback, clan_ids, comment, fields=None):
        url = '/applications/'
        data = {'account_id': self._account,
         'clan_ids': clan_ids,
         'comment': comment}

        @preprocess_callback(callback, 'clans')
        def inner_callback(data):
            return data.values()

        return self._request_data(inner_callback, 'clans', url, method='POST', postData=data)

    @mapped_fields({'transaction_id': 'transaction_id',
     'id': 'id',
     'account_id': 'account_id',
     'clan_id': 'clan_id'})
    def accept_application(self, callback, application_id, fields=None):
        url = '/applications/%s/' % application_id
        data = {'initiator_id': self._account,
         'status': 'accepted'}

        @preprocess_callback(callback, 'clans')
        def inner_callback(data):
            data = data or {}
            data['account_id'] = data.pop('account_ids')[0]
            data['id'] = application_id
            return data

        return self._request_data(inner_callback, 'clans', url, method='PATCH', postData=data)

    @mapped_fields({'transaction_id': 'transaction_id',
     'id': 'id',
     'account_id': 'account_id',
     'clan_id': 'clan_id'})
    def decline_application(self, callback, application_id, fields=None):
        url = '/applications/%s/' % application_id
        data = {'initiator_id': self._account,
         'status': 'declined'}

        @preprocess_callback(callback, 'clans')
        def inner_callback(data):
            data = data or {}
            data['id'] = application_id
            return data

        return self._request_data(inner_callback, 'clans', url, method='PATCH', postData=data)

    @mapped_fields({'clan_id': 'clan_id',
     'id': 'id',
     'account_id': 'account_id'})
    def create_invites(self, callback, clan_id, account_ids, comment, fields=None):
        url = '/invites/'
        data = {'initiator_id': self._account,
         'clan_id': clan_id,
         'account_ids': account_ids,
         'comment': comment}

        @preprocess_callback(callback, 'clans')
        def inner_callback(data):
            return data.values()

        return self._request_data(inner_callback, 'clans', url, method='POST', postData=data)

    @mapped_fields({'transaction_id': 'transaction_id',
     'id': 'id',
     'account_id': 'account_id',
     'clan_id': 'clan_id'})
    def accept_invite(self, callback, invite_id, fields=None):
        url = '/invites/%s/' % invite_id
        data = {'initiator_id': self._account,
         'status': 'accepted'}

        @preprocess_callback(callback, 'clans')
        def inner_callback(data):
            data = data or {}
            data['account_id'] = data.pop('account_ids')[0]
            data['id'] = invite_id
            return data

        return self._request_data(inner_callback, 'clans', url, method='PATCH', postData=data)

    @mapped_fields({'transaction_id': 'transaction_id',
     'id': 'id',
     'account_id': 'account_id',
     'clan_id': 'clan_id'})
    def decline_invite(self, callback, invite_id, fields=None):
        url = '/invites/%s/' % invite_id
        data = {'initiator_id': self._account,
         'status': 'declined'}

        @preprocess_callback(callback, 'clans')
        def inner_callback(data):
            data = data or {}
            data['id'] = invite_id
            return data

        return self._request_data(inner_callback, 'clans', url, method='PATCH', postData=data)

    @mapped_fields({'id': 'id',
     'clan_id': 'clan_id',
     'account_id': 'account_id'})
    def bulk_decline_invites(self, callback, invite_ids, fields=None):
        url = '/invites/'
        data = {'initiator_id': self._account,
         'status': 'declined',
         'ids': invite_ids}

        @preprocess_callback(callback, 'clans')
        def inner_callback(data):
            data = data and data['items'] or {}
            return data

        return self._request_data(inner_callback, 'clans', url, method='PATCH', postData=data)

    @convert_data({'created_at': from_iso}, paginated=True)
    @mapped_fields({'name': 'name',
     'tag': 'tag',
     'motto': 'motto',
     'leader_id': 'leader_id',
     'members_count': 'members_count',
     'created_at': 'created_at',
     'clan_id': 'id',
     'treasury': 'treasury',
     'accepts_join_requests': 'accepts_join_requests'}, paginated=True)
    def search_clans(self, callback, search, get_total_count=False, fields=None, offset=0, limit=18):
        get_params = {'search': search,
         'game': 'wot',
         'fields': ','.join(fields),
         'limit': limit,
         'offset': offset}
        url = '/clans/search/?%s' % urlencode(get_params)
        return self._request_data(preprocess_callback(callback, 'clans'), 'clans', url)

    @convert_data({'created_at': from_iso}, paginated=True)
    @mapped_fields({'name': 'name',
     'tag': 'tag',
     'motto': 'motto',
     'leader_id': 'leader_id',
     'members_count': 'members_count',
     'created_at': 'created_at',
     'clan_id': 'id',
     'treasury': 'treasury',
     'accepts_join_requests': 'accepts_join_requests'}, paginated=True)
    def get_recommended_clans(self, callback, get_total_count=False, fields=None, offset=0, limit=18):
        get_params = {'game': 'wot',
         'fields': ','.join(fields),
         'limit': limit,
         'offset': offset}
        url = '/clans/?%s' % urlencode(get_params)
        return self._request_data(preprocess_callback(callback, 'clans'), 'clans', url)

    @convert_data({'created_at': from_iso,
     'updated_at': from_iso}, paginated=True)
    @mapped_fields({'status': 'status',
     'created_at': 'created_at',
     'updated_at': 'updated_at',
     'sender_id': 'sender_id',
     'id': 'id',
     'account_id': 'account_id',
     'clan_id': 'clan_id',
     'comment': 'data.comment',
     'status_changer_id': 'data.status_changer_id'}, paginated=True)
    def get_clan_invites(self, callback, clan_id, fields=None, statuses=None, get_total_count=False, limit=18, offset=0):
        statuses = statuses or ['active',
         'declined',
         'accepted',
         'expired',
         'error',
         'deleted']
        get_params = {'fields': ','.join(fields),
         'clan_id': clan_id,
         'statuses': ','.join(statuses),
         'limit': limit,
         'offset': offset}
        url = '/invites/?%s' % urlencode(get_params)
        return self._request_data(preprocess_callback(callback, 'clans'), 'clans', url)

    @convert_data({'created_at': from_iso,
     'updated_at': from_iso}, paginated=True)
    @mapped_fields({'status': 'status',
     'created_at': 'created_at',
     'updated_at': 'updated_at',
     'sender_id': 'sender_id',
     'id': 'id',
     'account_id': 'account_id',
     'clan_id': 'clan_id',
     'comment': 'data.comment',
     'status_changer_id': 'data.status_changer_id'}, paginated=True)
    def get_account_invites(self, callback, fields=None, statuses=None, get_total_count=False, limit=18, offset=0):
        statuses = statuses or ['active',
         'declined',
         'accepted',
         'expired',
         'error',
         'deleted']
        get_params = {'fields': ','.join(fields),
         'account_id': self._account,
         'statuses': ','.join(statuses),
         'limit': limit,
         'offset': offset}
        url = '/invites/?%s' % urlencode(get_params)
        return self._request_data(preprocess_callback(callback, 'clans'), 'clans', url)

    @mapped_fields({'global_rating': 'summary.global_rating',
     'battle_avg_xp': 'summary.battle_avg_xp',
     'battles_count': 'summary.battles_count',
     'battle_avg_performance': 'summary.battle_avg_performance',
     'xp_amount': 'summary.xp_amount',
     'account_id': 'account_id'})
    def get_accounts_info(self, callback, account_ids, fields=None):
        fields = [ i.split('.', 1) for i in fields if i != 'account_id' ]
        grouped = groupby(sorted(fields), key=lambda x: x[0])
        sections = [ '%s[%s]' % (k, ','.join([ j[1] for j in v ])) for k, v in grouped ]
        get_params = {'account_ids': ','.join(map(str, account_ids)),
         'sections': ','.join(sections)}
        url = '/wot/accounts/?%s' % urlencode(get_params)

        @preprocess_callback(callback, 'exporter')
        def inner_callback(data):
            new_data = []
            for account_id, values in data.items():
                values['account_id'] = account_id
                new_data.append(values)

            return new_data

        return self._request_data(inner_callback, 'exporter', url)

    @convert_data({'pillage_end_datetime': from_iso,
     'prime_time': lambda x: x and datetime.strptime(x, '%H:%M').time()})
    @mapped_fields({'front_name': 'frontname',
     'province_id': 'province_id',
     'front_name_localized': 'frontname_localized',
     'province_id_localized': 'province_id_localized',
     'revenue': 'daily_revenue',
     'hq_connected': 'hq_connected',
     'prime_time': 'primetime',
     'game_map': 'game_map',
     'periphery': 'periphery_id',
     'turns_owned': 'turns_owned',
     'pillage_cooldown': 'pillage_cooldown',
     'pillage_end_datetime': 'pillage_end_datetime',
     'arena_id': 'arena_id'})
    def get_clan_provinces(self, callback, clan_id, fields=None):
        get_params = {'clans': ','.join(map(str, [clan_id]))}
        url = '/clans/provinces/?%s' % urlencode(get_params)

        @preprocess_callback(callback, 'global_map')
        def inner_callback(data):
            res = data['clans'] and data['clans'][0]['provinces']
            for i in res:
                i['frontname_localized'] = i['frontname']
                i['province_id_localized'] = i['province_id']

            return res

        return self._request_data(inner_callback, 'global_map', url)

    @mapped_fields({'battles_lost': 'battles_lost',
     'battles_played': 'battles_played',
     'battles_played_on_10_level': 'battles_played_on_10_level',
     'battles_played_on_6_level': 'battles_played_on_6_level',
     'battles_played_on_8_level': 'battles_played_on_8_level',
     'battles_won': 'battles_won',
     'battles_won_on_10_level': 'battles_won_on_10_level',
     'battles_won_on_6_level': 'battles_won_on_6_level',
     'battles_won_on_8_level': 'battles_won_on_8_level',
     'influence_points': 'influence_points',
     'provinces_captured': 'provinces_captured',
     'provinces_count': 'provinces_count'})
    def get_clan_globalmap_stats(self, callback, clan_id, fields=None):
        get_params = {'clans': ','.join(map(str, [clan_id]))}
        url = '/clans/stats?%s' % urlencode(get_params)

        @preprocess_callback(callback, 'global_map')
        def inner_callback(data):
            return data['clans'][0]['stats']

        return self._request_data(inner_callback, 'global_map', url)

    @mapped_fields({'front_name': 'id',
     'front_name_localized': 'id_localized',
     'min_vehicle_level': 'min_vehicle_level',
     'max_vehicle_level': 'max_vehicle_level'})
    def get_fronts_info(self, callback, front_names=None, fields=None):
        url = '/fronts/'

        @preprocess_callback(callback, 'global_map')
        def inner_callback(data):
            res = data['fronts']
            for i in res:
                i['id_localized'] = i['id']

            return res

        return self._request_data(inner_callback, 'global_map', url)

    @convert_data({'defence_hour': lambda x: dt_time(x, 0) if x >= 0 else None})
    @mapped_fields({'buildings.direction': 'buildings.direction',
     'buildings.type': 'buildings.type',
     'buildings.level': 'buildings.level',
     'buildings.position': 'buildings.position',
     'defence_attack_efficiency': 'defence_attack_efficiency',
     'defence_battles_count': 'defence_battles_count',
     'defence_capture_enemy_building_total_count': 'defence_capture_enemy_building_total_count',
     'defence_combat_wins': 'defence_combat_wins',
     'defence_defence_efficiency': 'defence_defence_efficiency',
     'defence_enemy_base_capture_count': 'defence_enemy_base_capture_count',
     'defence_loss_own_building_total_count': 'defence_loss_own_building_total_count',
     'defence_resource_capture_count': 'defence_resource_capture_count',
     'defence_resource_loss_count': 'defence_resource_loss_count',
     'sortie_absolute_battles_count': 'sortie_absolute_battles_count',
     'sortie_battles_count': 'sortie_battles_count',
     'sortie_champion_battles_count': 'sortie_champion_battles_count',
     'sortie_middle_battles_count': 'sortie_middle_battles_count',
     'defence_attack_count': 'defence_attack_count',
     'defence_defence_count': 'defence_defence_count',
     'defence_success_attack_count': 'defence_success_attack_count',
     'defence_success_defence_count': 'defence_success_defence_count',
     'sortie_fort_resource_in_absolute': 'sortie_fort_resource_in_absolute',
     'sortie_fort_resource_in_champion': 'sortie_fort_resource_in_champion',
     'sortie_fort_resource_in_middle': 'sortie_fort_resource_in_middle',
     'sortie_losses': 'sortie_losses',
     'sortie_wins': 'sortie_wins',
     'level': 'level',
     'defence_hour': 'defence_hour',
     'defence_mode_is_activated': 'defence_mode_is_activated',
     'fb_battles_count_10': 'fb_battles_count_10',
     'fb_battles_count_8': 'fb_battles_count_8',
     'total_resource_amount': 'total_resource_amount'})
    def get_stronghold_info(self, callback, clan_id=None, fields=None):
        get_params = urlencode({'performer_id': self._account})
        try:
            clan_id = int(clan_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = 'api/strongholds/%s/' % clan_id
        if self._account:
            url = '?'.join([url, get_params])

        @preprocess_callback(callback, 'strongholds')
        def inner_callback(data):
            return data['stronghold']

        return self._request_data(inner_callback, 'strongholds', url)

    @convert_data({'vacation_finish': timestamp_to_datetime,
     'vacation_start': timestamp_to_datetime})
    @mapped_fields({'buildings.type': 'buildings.type',
     'buildings.hp': 'buildings.hp',
     'buildings.direction': 'buildings.direction',
     'buildings.position': 'buildings.position',
     'buildings.storage': 'buildings.resource_amount',
     'buildings.level': 'buildings.level',
     'buildings_count': 'buildings_count',
     'clan_id': 'clan_id',
     'level': 'level',
     'clan_name': 'clan_name',
     'clan_tag': 'clan_tag',
     'directions': 'directions',
     'directions_count': 'directions_count',
     'off_day': 'off_day',
     'periphery_id': 'periphery_id',
     'vacation_finish': 'vacation_finish',
     'vacation_start': 'vacation_start',
     'sortie_wins_period': 'sortie_wins_period',
     'sortie_battles_wins_percentage_period': 'sortie_battles_wins_percentage_period',
     'sortie_battles_count_period': 'sortie_battles_count_period',
     'defence_battles_count_period': 'defence_battles_count_period'})
    def get_strongholds_statistics(self, callback, clan_id, fields=None):
        get_params = urlencode({'performer_id': self._account})
        try:
            clan_id = int(clan_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/api/strongholds/statistics/%s/' % clan_id
        if self._account:
            url = '?'.join([url, get_params])

        @preprocess_callback(callback, 'strongholds')
        def inner_callback(data):
            return data[0]

        return self._request_data(inner_callback, 'strongholds', url)

    def get_wgsh_unit_info(self, callback, periphery_id, unit_server_id, rev, fields=None):
        try:
            periphery_id = int(periphery_id)
            unit_server_id = int(unit_server_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/unit_api/periphery/{periphery_id}/units/{unit_server_id}/?rev={rev}'.format(periphery_id=periphery_id, unit_server_id=unit_server_id, rev=rev)

        @preprocess_callback(callback, 'wgsh')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgsh', url)

    def set_vehicle(self, callback, periphery_id, unit_server_id, vehicle_cd, fields=None):
        try:
            periphery_id = int(periphery_id)
            unit_server_id = int(unit_server_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/unit_api/periphery/{periphery_id}/units/{unit_server_id}/members/{account_id}/vehicles'.format(periphery_id=periphery_id, unit_server_id=unit_server_id, account_id=self._account)
        patch_data = {'vehicle_cd': vehicle_cd}

        @preprocess_callback(callback, 'wgsh')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgsh', url, method='PATCH', postData=patch_data)

    def set_readiness(self, callback, periphery_id, unit_server_id, is_ready, reset_vehicle, fields=None):
        try:
            periphery_id = int(periphery_id)
            unit_server_id = int(unit_server_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/unit_api/periphery/{periphery_id}/units/{unit_server_id}/members/{account_id}/readiness'.format(periphery_id=periphery_id, unit_server_id=unit_server_id, account_id=self._account)
        patch_data = {'is_ready': is_ready,
         'reset_vehicle': reset_vehicle}

        @preprocess_callback(callback, 'wgsh')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgsh', url, method='PATCH', postData=patch_data)

    def invite_players(self, callback, periphery_id, unit_server_id, accounts_to_invite, comment, fields=None):
        try:
            periphery_id = int(periphery_id)
            unit_server_id = int(unit_server_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/unit_api/periphery/{periphery_id}/units/{unit_server_id}/participants/{account_id}/invite'.format(periphery_id=periphery_id, unit_server_id=unit_server_id, account_id=self._account)
        post_data = {'accounts_to_invite': accounts_to_invite,
         'comment': comment}

        @preprocess_callback(callback, 'wgsh')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgsh', url, method='POST', postData=post_data)

    def assign_player(self, callback, periphery_id, unit_server_id, account_to_assign, fields=None):
        try:
            periphery_id = int(periphery_id)
            unit_server_id = int(unit_server_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/unit_api/periphery/{periphery_id}/units/{unit_server_id}/participants/{account_id}/assign'.format(periphery_id=periphery_id, unit_server_id=unit_server_id, account_id=self._account)
        post_data = {'account_to_assign': account_to_assign}

        @preprocess_callback(callback, 'wgsh')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgsh', url, method='POST', postData=post_data)

    def unassign_player(self, callback, periphery_id, unit_server_id, account_to_unassign, fields=None):
        try:
            periphery_id = int(periphery_id)
            unit_server_id = int(unit_server_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/unit_api/periphery/{periphery_id}/units/{unit_server_id}/participants/{account_id}/unassign'.format(periphery_id=periphery_id, unit_server_id=unit_server_id, account_id=self._account)
        post_data = {'account_to_unassign': account_to_unassign}

        @preprocess_callback(callback, 'wgsh')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgsh', url, method='POST', postData=post_data)

    def give_leadership(self, callback, periphery_id, unit_server_id, target_account_id, fields=None):
        try:
            periphery_id = int(periphery_id)
            unit_server_id = int(unit_server_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/unit_api/periphery/{periphery_id}/units/{unit_server_id}/members/{account_id}/give_leadership'.format(periphery_id=periphery_id, unit_server_id=unit_server_id, account_id=self._account)
        post_data = {'target_account_id': target_account_id}

        @preprocess_callback(callback, 'wgsh')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgsh', url, method='PATCH', postData=post_data)

    def set_equipment_commander(self, callback, periphery_id, unit_server_id, target_account_id, role, fields=None):
        try:
            periphery_id = int(periphery_id)
            unit_server_id = int(unit_server_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/unit_api/periphery/{periphery_id}/units/{unit_server_id}/members/{account_id}/equipment_commander'.format(periphery_id=periphery_id, unit_server_id=unit_server_id, account_id=self._account)
        post_data = {'equipment_commander_id': target_account_id,
         'role': role}

        @preprocess_callback(callback, 'wgsh')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgsh', url, method='PATCH', postData=post_data)

    def leave_room(self, callback, periphery_id, unit_server_id, fields=None):
        try:
            periphery_id = int(periphery_id)
            unit_server_id = int(unit_server_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/unit_api/periphery/{periphery_id}/units/{unit_server_id}/participants/{account_id}/leave'.format(periphery_id=periphery_id, unit_server_id=unit_server_id, account_id=self._account)

        @preprocess_callback(callback, 'wgsh')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgsh', url, method='POST')

    def take_away_leadership(self, callback, periphery_id, unit_server_id, fields=None):
        try:
            periphery_id = int(periphery_id)
            unit_server_id = int(unit_server_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/unit_api/periphery/{periphery}/units/{unit}/participants/{account}/take_away_leadership'.format(periphery=periphery_id, unit=unit_server_id, account=self._account)

        @preprocess_callback(callback, 'wgsh')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgsh', url, method='PATCH')

    def kick_player(self, callback, periphery_id, unit_server_id, account_to_kick, fields=None):
        try:
            periphery_id = int(periphery_id)
            unit_server_id = int(unit_server_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/unit_api/periphery/{periphery_id}/units/{unit_server_id}/members/{account_id}/kick'.format(periphery_id=periphery_id, unit_server_id=unit_server_id, account_id=self._account)
        post_data = {'account_to_kick': account_to_kick}

        @preprocess_callback(callback, 'wgsh')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgsh', url, method='POST', postData=post_data)

    def set_open(self, callback, periphery_id, unit_server_id, is_open, fields=None):
        try:
            periphery_id = int(periphery_id)
            unit_server_id = int(unit_server_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/unit_api/periphery/{periphery_id}/units/{unit_server_id}/participants/{account_id}/set_open'.format(periphery_id=periphery_id, unit_server_id=unit_server_id, account_id=self._account)
        post_data = {'is_open': is_open}

        @preprocess_callback(callback, 'wgsh')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgsh', url, method='PATCH', postData=post_data)

    def lock_reserve(self, callback, periphery_id, unit_server_id, reserve_id, fields=None):
        try:
            periphery_id = int(periphery_id)
            unit_server_id = int(unit_server_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/unit_api/periphery/{periphery_id}/units/{unit_server_id}/members/{account_id}/lock_reserve'.format(periphery_id=periphery_id, unit_server_id=unit_server_id, account_id=self._account)
        post_data = {'reserve_id': reserve_id}

        @preprocess_callback(callback, 'wgsh')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgsh', url, method='POST', postData=post_data)

    def unlock_reserve(self, callback, periphery_id, unit_server_id, reserve_id, fields=None):
        try:
            periphery_id = int(periphery_id)
            unit_server_id = int(unit_server_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/unit_api/periphery/{periphery_id}/units/{unit_server_id}/members/{account_id}/unlock_reserve'.format(periphery_id=periphery_id, unit_server_id=unit_server_id, account_id=self._account)
        post_data = {'reserve_id': reserve_id}

        @preprocess_callback(callback, 'wgsh')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgsh', url, method='POST', postData=post_data)

    def clan_statistics(self, callback, clan_id, fields=None):
        try:
            clan_id = int(clan_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/external_api/v1/clan_card/{clan_id}'.format(clan_id=clan_id)

        @preprocess_callback(callback, 'wgsh')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgsh', url, method='GET')

    def wgsh_event_settings(self, callback, fields=None):
        url = '/settings'

        @preprocess_callback(callback, 'wgshevents')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgshevents', url, method='GET')

    def wgsh_event_clan_info(self, callback, fields=None):

        @preprocess_callback(callback, 'wgshevents')
        def inner_callback(data):
            return data or {}

        url = '/clan/info?%s' % urlencode({'spa_id': self._account})
        return self._request_data(inner_callback, 'wgshevents', url, method='GET')

    def wgsh_event_get_frozen_vehicles(self, callback, fields=None):

        @preprocess_callback(callback, 'wgshevents')
        def inner_callback(data):
            return data or {}

        url = '/frozen_vehicle?%s' % urlencode({'spa_id': self._account})
        return self._request_data(inner_callback, 'wgshevents', url, method='GET')

    def account_statistics(self, callback, account_id, fields=None):
        try:
            account_id = int(account_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/external_api/accounts/{account_id}'.format(account_id=account_id)

        @preprocess_callback(callback, 'wgsh')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgsh', url, method='GET')

    def join_room(self, callback, periphery_id, unit_server_id, fields=None):
        try:
            periphery_id = int(periphery_id)
            unit_server_id = int(unit_server_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        url = '/unit_api/periphery/{periphery_id}/units/{unit_server_id}/members/{account_id}/join'.format(periphery_id=periphery_id, unit_server_id=unit_server_id, account_id=self._account)

        @preprocess_callback(callback, 'wgsh')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'wgsh', url, method='POST')

    def user_ranked_position(self, callback, fields=None):
        url = '/user-position/{account_id}/'.format(account_id=self._account)

        @preprocess_callback(callback, 'rblb')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'rblb', url, method='GET')

    def user_ranked_year_position(self, callback):
        url = '/user-yearly-position/{account_id}/'.format(account_id=self._account)

        @preprocess_callback(callback, 'rblb')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'rblb', url, method='GET')

    @convert_data({'defence_hour': lambda x: dt_time(x, 0) if x >= 0 else None})
    @mapped_fields({'clan_id': 'clan_id',
     'defence_hour': 'defence_hour'})
    def get_strongholds_state(self, callback, clan_id, fields=None):
        get_params = {'clan_id': clan_id}
        try:
            clan_id = int(clan_id)
        except (TypeError, ValueError):
            error = exceptions.BadRequest()
            return callback({'description': error.description}, error.status_code, error.response_code)

        if self._account:
            get_params['performer_id'] = self._account
        url = '/api/strongholds/state/?%s' % urlencode(get_params)

        @preprocess_callback(callback, 'strongholds')
        def inner_callback(data):
            return data and data[0] or {}

        return self._request_data(inner_callback, 'strongholds', url)

    def get_teaser(self, callback, fields=None):
        url = '/teaser/?%s' % urlencode(self._pack_promo_params(fields))

        @preprocess_callback(callback, 'promo')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'promo', url, method='GET')

    def send_teaser(self, callback, promo_id, fields=None):

        @preprocess_callback(callback, 'promo')
        def inner_callback(data):
            return data or {}

        params = {'promoscreen_id': promo_id}
        url = '/teaser/view/'
        return self._request_data(inner_callback, 'promo', url, method='POST', postData=self._pack_promo_params(params))

    def get_unread_count(self, callback, fields=None):
        url = '/unread/?%s' % urlencode(self._pack_promo_params())

        @preprocess_callback(callback, 'promo')
        def inner_callback(data):
            return data or {}

        return self._request_data(inner_callback, 'promo', url, method='GET')

    def client_promo_log(self, callback, data, fields=None):

        @preprocess_callback(callback, 'promo')
        def inner_callback(data):
            return data or {}

        url = '/client_promo_log/?%s' % urlencode(self._pack_promo_params(data))
        return self._request_data(inner_callback, 'promo', url, method='GET')

    def _pack_promo_params(self, params=None):
        if params is None:
            params = {}
        default_params = {'spa_id': self._account}
        default_params.update(params)
        return default_params
