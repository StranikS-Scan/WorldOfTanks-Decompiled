# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/client_request_lib/data_sources/gateway.py
import zlib
import json
import urllib
from base64 import b64encode
from datetime import datetime, timedelta, time as dt_time
from client_request_lib import exceptions
from client_request_lib.data_sources import base
from debug_utils import LOG_ERROR
EXAMPLES = {}
DEFAULT_SINCE_DELAY = timedelta(days=1)
SUCCESS_STATUSES = [200, 201, 304]
ERROR_MAP = {e.response_code:e for e in exceptions.BaseRequestError.__subclasses__()}

def get_error_from_response(response_code):
    return ERROR_MAP.get(response_code, exceptions.WgcgError)


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


class GatewayDataAccessor(base.BaseDataAccessor):

    def __init__(self, url_fetcher, gateway_host, client_lang=None, user_agent=None):
        self.client_lang = client_lang
        self._session_id = None
        self.url_fetcher = url_fetcher
        self.gateway_host = gateway_host
        self.user_agent = user_agent
        return

    def _apply_converters(self, data, converters):
        if data:
            if not isinstance(data, (tuple, list)):
                data = [data]
            for k, convert in converters.items():
                if '.' in k:
                    prefix, body = k.split('.', 1)
                    for portion in data:
                        if prefix in portion:
                            self._apply_converters(portion[prefix], {body: convert})

                for portion in data:
                    if k in portion:
                        portion[k] = convert(portion[k])

    def _preprocess_callback(self, callback, converters=None):

        def wrapper(something):

            def wrapped(response, func=something):
                try:
                    data = response.body
                    headers = response.headers()
                    try:
                        data = zlib.decompress(data, 16 + zlib.MAX_WBITS)
                    except zlib.error:
                        pass

                    data = json.loads(data)
                except:
                    LOG_ERROR('Can not process request response')
                    data = None
                    headers = None

                if response.responseCode not in SUCCESS_STATUSES:
                    error_data = None
                    if data:
                        error_data = {'description': data.get('description', ''),
                         'title': data.get('title', ''),
                         'notification_type': data.get('notification_type', ''),
                         'extra_data': data.get('extra_data')}
                    return callback(error_data, response.responseCode, response.responseCode, headers)
                else:
                    response_code = exceptions.ResponseCodes.NO_ERRORS
                    if func:
                        data = func(data)
                    if converters:
                        self._apply_converters(data, converters)
                    callback(data, response.responseCode, response_code, headers)
                    return

            return wrapped(something, func=None) if not callable(something) else wrapped

        return wrapper

    def login(self, callback, account_id, spa_token, jwt):
        if jwt:
            auth_type = 'JWT'
            auth_data = spa_token
        else:
            auth_type = 'Basic'
            auth_data = b64encode(':'.join([str(account_id), str(spa_token)]))
        extra_headers = {'AUTHORIZATION': '%s %s' % (auth_type, auth_data)}

        def inner_callback(data, status_code, response_code, headers):
            if status_code in SUCCESS_STATUSES:
                self._session_id = data['session']
            callback(data, status_code, response_code, headers)

        self._request_data(inner_callback, '/login/', headers=extra_headers)

    def logout(self, callback):
        self._request_data(callback, '/logout/')
        self._session_id = None
        return

    def _request_data(self, callback, url, get_data=None, method='GET', post_data=None, headers=None, converters=None):
        get_data = get_data or {}
        get_data = {k:v for k, v in get_data.iteritems() if v is not None}
        url = '/'.join([self.gateway_host.rstrip('/'), url.lstrip('/')])
        if get_data:
            values = []
            for k, val in get_data.iteritems():
                if not isinstance(val, (list, tuple)):
                    val = [val]
                values.append((k, ','.join((str(i) for i in val))))

            urlencoded_string = urllib.urlencode(values)
            url = '{}?{}'.format(url, urlencoded_string)
        default_headers = {'Accept-Encoding': 'compress, gzip'}
        if self.client_lang:
            default_headers['Accept-Language'] = self.client_lang
        default_headers.update(headers or {})
        if self._session_id:
            default_headers['COOKIE'] = 'session=%s' % self._session_id
        if self.user_agent:
            default_headers['User-Agent'] = self.user_agent
        headers = tuple(('{}: {}'.format(k, v) for k, v in default_headers.iteritems() if v))
        args = [headers, 30.0, method]
        if post_data:
            args.append(json.dumps(post_data))
        self.url_fetcher(url, self._preprocess_callback(callback, converters=converters), *args)

    def advent_calendar_fetch_hero_tank_info(self, callback):
        url = '/advc/herotank/'
        return self._request_data(callback, url)

    def craftmachine_modules_info(self, callback):
        url = '/craft/client_settings/'
        return self._request_data(callback, url)

    def get_clans_ratings(self, callback, clan_ids, fields=None):
        get_params = {'clan_ids': clan_ids,
         'fields': fields}
        url = '/ratings/clans/'
        return self._request_data(callback, url, get_data=get_params)

    def get_clans_info(self, callback, clan_ids, fields=None):
        get_params = {'clan_ids': clan_ids,
         'fields': fields}
        url = '/clans/info/'
        return self._request_data(callback, url, get_data=get_params, converters={'created_at': from_iso})

    def get_accounts_names(self, callback, account_ids, fields=None):
        get_params = {'id': account_ids,
         'fields': fields}
        url = '/accounts/names/'
        return self._request_data(callback, url, get_data=get_params, converters={'id': int})

    def get_account_attribute_by_prefix(self, callback, attr_prefix, fields=None):
        get_params = {'attr_prefix': attr_prefix,
         'fields': fields}
        url = '/accounts/attributes/get_by_prefix/'
        return self._request_data(callback, url, get_data=get_params)

    def agate_v4_fetch_product_list_state(self, callback, request_data, fields=None):
        url = '/agate/api/v4/commerce/fetchProductListState/'
        return self._request_data(callback, url, method='POST', post_data=request_data)

    def agate_v5_get_user_subscriptions(self, callback, request_data, fields=None):
        url = '/agate/api/v5/commerce/getUserSubscriptions/'
        return self._request_data(callback, url, method='POST', post_data=request_data)

    def get_clan_members(self, callback, clan_id, fields=None):
        get_params = {'fields': fields}
        url = '/clans/%s/members/' % clan_id
        return self._request_data(callback, url, get_data=get_params, converters={'joined_at': from_iso})

    def get_clan_favorite_attributes(self, callback, clan_id, fields=None):
        get_params = {'clan_id': clan_id}
        url = '/cwh/gm/clans/favorite_attributes'
        return self._request_data(callback, url, get_data=get_params, converters={'favorite_primetime': lambda x: x and datetime.strptime(x, '%H:%M').time(),
         'favorite_arena_6': int,
         'favorite_arena_8': int,
         'favorite_arena_10': int})

    def get_accounts_clans(self, callback, account_ids, fields=None):
        get_params = {'fields': fields,
         'account_ids': account_ids}
        url = '/accounts/clans/'
        return self._request_data(callback, url, get_data=get_params, converters={'in_clan_cooldown_till': from_iso,
         'joined_at': from_iso})

    def get_account_applications_count_since(self, callback, account_id, since=None):
        since = since or datetime.utcnow() - DEFAULT_SINCE_DELAY
        get_params = {'created_after': since.isoformat()}
        url = '/accounts/%s/applications/count/' % account_id
        return self._request_data(callback, url, get_data=get_params)

    def get_clan_invites_count_since(self, callback, clan_id, since=None):
        since = since or datetime.utcnow() - DEFAULT_SINCE_DELAY
        get_params = {'created_after': since.isoformat()}
        url = '/clans/%s/invites/count/' % clan_id
        return self._request_data(callback, url, get_data=get_params)

    def get_alive_status(self, callback):
        url = '/ping/'
        return self._request_data(callback, url)

    def get_account_applications(self, callback, fields=None, statuses=None, get_total_count=False, limit=None, offset=None):
        get_params = {'fields': fields,
         'statuses': statuses}
        if get_total_count:
            get_params['get_total_count'] = 'true'
        if limit is not None:
            get_params['limit'] = limit
        if offset is not None:
            get_params['offset'] = offset
        url = '/my/applications/'
        return self._request_data(callback, url, get_data=get_params, converters={'items.created_at': from_iso,
         'items.updated_at': from_iso})

    def get_clan_applications(self, callback, clan_id, fields=None, statuses=None, get_total_count=False, limit=None, offset=None):
        get_params = {'fields': fields,
         'statuses': statuses}
        if get_total_count:
            get_params['get_total_count'] = 'true'
        if limit is not None:
            get_params['limit'] = limit
        if offset is not None:
            get_params['offset'] = offset
        url = '/clans/%s/applications/' % clan_id
        return self._request_data(callback, url, get_data=get_params, converters={'items.created_at': from_iso,
         'items.updated_at': from_iso})

    def create_applications(self, callback, clan_ids, comment, fields=None):
        url = '/clans/applications/'
        data = {'clan_ids': clan_ids,
         'comment': comment}
        return self._request_data(callback, url, method='POST', post_data=data)

    def accept_application(self, callback, application_id, fields=None):
        url = '/clans/applications/%s/' % application_id
        data = {'status': 'accepted'}
        return self._request_data(callback, url, method='PATCH', post_data=data)

    def decline_application(self, callback, application_id, fields=None):
        url = '/clans/applications/%s/' % application_id
        data = {'status': 'declined'}
        return self._request_data(callback, url, method='PATCH', post_data=data)

    def create_invites(self, callback, clan_id, account_ids, comment, fields=None):
        url = '/clans/%s/invites/' % clan_id
        data = {'account_ids': account_ids,
         'comment': comment}
        return self._request_data(callback, url, method='POST', post_data=data)

    def accept_invite(self, callback, invite_id, fields=None):
        url = '/clans/invites/%s/' % invite_id
        data = {'status': 'accepted'}
        return self._request_data(callback, url, method='PATCH', post_data=data)

    def decline_invite(self, callback, invite_id, fields=None):
        url = '/clans/invites/%s/' % invite_id
        data = {'status': 'declined'}
        return self._request_data(callback, url, method='PATCH', post_data=data)

    def bulk_decline_invites(self, callback, invite_ids, fields=None):
        url = '/clans/decline_invites/'
        data = {'invite_ids': invite_ids}
        return self._request_data(callback, url, method='PATCH', post_data=data)

    def search_clans(self, callback, search, get_total_count=False, fields=None, offset=None, limit=None):
        get_params = {'search': search.encode('utf-8'),
         'fields': fields}
        if get_total_count:
            get_params['get_total_count'] = 'true'
        if limit is not None:
            get_params['limit'] = limit
        if offset is not None:
            get_params['offset'] = offset
        url = '/clans/search/'
        return self._request_data(callback, url, get_data=get_params, converters={'items.created_at': from_iso})

    def get_recommended_clans(self, callback, get_total_count=False, fields=None, offset=None, limit=None):
        get_params = {'fields': fields}
        if get_total_count:
            get_params['get_total_count'] = 'true'
        if limit is not None:
            get_params['limit'] = limit
        if offset is not None:
            get_params['offset'] = offset
        url = '/clans/recommended/'
        return self._request_data(callback, url, get_data=get_params, converters={'items.created_at': from_iso})

    def get_clan_invites(self, callback, clan_id, fields=None, statuses=None, get_total_count=False, limit=None, offset=None):
        get_params = {'fields': fields,
         'statuses': statuses}
        if get_total_count:
            get_params['get_total_count'] = 'true'
        if limit is not None:
            get_params['limit'] = limit
        if offset is not None:
            get_params['offset'] = offset
        url = 'clans/%s/invites/' % clan_id
        return self._request_data(callback, url, get_data=get_params, converters={'items.created_at': from_iso,
         'items.updated_at': from_iso})

    def get_account_invites(self, callback, fields=None, statuses=None, get_total_count=False, limit=None, offset=None):
        statuses = statuses or ['active',
         'declined',
         'accepted',
         'expired',
         'error',
         'deleted']
        get_params = {'fields': fields,
         'statuses': statuses}
        if get_total_count:
            get_params['get_total_count'] = 'true'
        if limit is not None:
            get_params['limit'] = limit
        if offset is not None:
            get_params['offset'] = offset
        url = '/my/invites/'
        return self._request_data(callback, url, get_data=get_params, converters={'items.created_at': from_iso,
         'items.updated_at': from_iso})

    def get_accounts_info(self, callback, account_ids, fields=None):
        get_params = {'account_ids': account_ids,
         'fields': fields}
        url = '/accounts/info/'
        return self._request_data(callback, url, get_data=get_params, converters={'account_id': int})

    def get_clan_provinces(self, callback, clan_id, fields=None):
        get_params = {'clan_id': [clan_id],
         'fields': fields}
        url = '/global_map/wgapi/clan_provinces/'
        return self._request_data(callback, url, get_data=get_params, converters={'prime_time': lambda x: x and datetime.strptime(x, '%H:%M').time(),
         'pillage_end_datetime': from_iso,
         'clan_id': int})

    def get_clan_globalmap_stats(self, callback, clan_id, fields=None):
        url = '/global_map/wgapi/clan_stats/'
        get_params = {'clan_id': clan_id}
        if fields:
            get_params['fields'] = fields
        return self._request_data(callback, url, get_data=get_params, converters={'clan_id': int})

    def get_fronts_info(self, callback, front_names=None, fields=None):
        url = '/global_map/wgapi/new_fronts/'
        get_params = {'fields': fields,
         'front_names': front_names}
        return self._request_data(callback, url, get_data=get_params)

    def get_stronghold_info(self, callback, clan_id=None, fields=None):
        url = '/strongholds/info/'
        get_params = {'clan_id': clan_id}
        if fields:
            get_params['fields'] = fields
        return self._request_data(callback, url, get_data=get_params, converters={'clan_id': int,
         'defence_hour': lambda x: dt_time(x, 0) if x >= 0 else None})

    def get_strongholds_statistics(self, callback, clan_id, fields=None):
        url = '/strongholds/statistics/'
        get_params = {'clan_id': clan_id}
        if fields:
            get_params['fields'] = fields
        return self._request_data(callback, url, get_data=get_params, converters={'vacation_start': timestamp_to_datetime,
         'vacation_finish': timestamp_to_datetime})

    def get_strongholds_state(self, callback, clan_id, fields=None):
        url = '/strongholds/state/'
        get_params = {'clan_id': clan_id}
        return self._request_data(callback, url, get_data=get_params, converters={'clan_id': int,
         'defence_hour': lambda x: dt_time(x, 0) if x >= 0 else None})

    def get_wgsh_unit_info(self, callback, periphery_id, unit_server_id, rev, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        return self._request_data(callback, url, get_data={'rev': rev}, converters={'periphery_id': int,
         'unit_server_id': int})

    def set_vehicle(self, callback, periphery_id, unit_server_id, vehicle_cd, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/vehicles/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'vehicle_cd': vehicle_cd}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='PATCH', post_data=post_data)

    def set_slot_vehicle_type_filter(self, callback, periphery_id, unit_server_id, slot_idx, vehicle_types, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/set_slot_vehicle_filters/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        _data = {'slot_id': slot_idx,
         'vehicle_types': vehicle_types}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='POST', post_data=_data)

    def set_slot_vehicles_filter(self, callback, periphery_id, unit_server_id, slot_idx, vehicles, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/set_slot_vehicle_filters/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        _data = {'slot_id': slot_idx,
         'vehicle_cds': vehicles}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='POST', post_data=_data)

    def get_slot_vehicle_filters(self, callback, periphery_id, unit_server_id, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/get_slot_vehicle_filters/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='GET')

    def stop_players_matching(self, callback, periphery_id, unit_server_id):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/stop_players_matching/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='DELETE')

    def set_readiness(self, callback, periphery_id, unit_server_id, is_ready, reset_vehicle, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/readiness/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        patch_data = {'is_ready': is_ready,
         'reset_vehicle': reset_vehicle}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='PATCH', post_data=patch_data)

    def invite_players(self, callback, periphery_id, unit_server_id, accounts_to_invite, comment, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/invite/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'accounts_to_invite': accounts_to_invite,
         'comment': comment}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='POST', post_data=post_data)

    def assign_player(self, callback, periphery_id, unit_server_id, account_to_assign, slot_id_to_assign, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/assign/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'account_to_assign': account_to_assign,
         'slot_id_to_assign': slot_id_to_assign}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='POST', post_data=post_data)

    def unassign_player(self, callback, periphery_id, unit_server_id, account_to_unassign, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/unassign/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'account_to_unassign': account_to_unassign}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='POST', post_data=post_data)

    def give_leadership(self, callback, periphery_id, unit_server_id, target_account_id, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/give_leadership/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'target_account_id': target_account_id}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='PATCH', post_data=post_data)

    def set_equipment_commander(self, callback, periphery_id, unit_server_id, target_account_id, role, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/equipment_commander/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'equipment_commander_id': target_account_id,
         'role': role}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='POST', post_data=post_data)

    def leave_room(self, callback, periphery_id, unit_server_id, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/leave/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='POST')

    def leave_mode(self, callback, fields=None):
        url = '/wgsh/leave_mode/'
        return self._request_data(callback, url, get_data={}, converters={}, method='DELETE')

    def take_away_leadership(self, callback, periphery_id, unit_server_id, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/take_away_leadership/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='PATCH')

    def kick_player(self, callback, periphery_id, unit_server_id, account_to_kick, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/kick/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'account_to_kick': account_to_kick}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='POST', post_data=post_data)

    def set_open(self, callback, periphery_id, unit_server_id, is_open, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/set_open/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'is_open': is_open}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='PATCH', post_data=post_data)

    def lock_reserve(self, callback, periphery_id, unit_server_id, reserve_id, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/lock_reserve/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'reserve_id': reserve_id}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='POST', post_data=post_data)

    def unlock_reserve(self, callback, periphery_id, unit_server_id, reserve_id, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/unlock_reserve/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'reserve_id': reserve_id}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='POST', post_data=post_data)

    def wgsh_event_settings(self, callback, fields=None):
        url = '/wgshevents/settings'
        return self._request_data(callback, url, get_data={}, method='GET')

    def wgsh_event_clan_info(self, callback, fields=None):
        url = '/wgshevents/clan/info'
        return self._request_data(callback, url, method='GET')

    def wgsh_event_get_frozen_vehicles(self, callback, fields=None):
        url = '/wgshevents/frozen_vehicle'
        return self._request_data(callback, url, method='GET')

    def clan_statistics(self, callback, clan_id, fields=None):
        url = '/wgsh/clans/{clan_id}/'.format(clan_id=clan_id)
        return self._request_data(callback, url, get_data={}, converters={}, method='GET')

    def join_room(self, callback, periphery_id, unit_server_id, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/join/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        return self._request_data(callback, url, get_data={}, method='POST')

    def matchmaking_info(self, callback, periphery_id, unit_server_id, fields=None):
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/matchmaking_info/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        return self._request_data(callback, url, get_data={}, method='GET')

    def user_ranked_position(self, callback, fields=None):
        url = '/ranked/user_position/'
        return self._request_data(callback, url, get_data={}, method='GET')

    def user_ranked_year_position(self, callback):
        url = '/ranked/user_yearly_position/'
        return self._request_data(callback, url, get_data={}, method='GET')

    def account_statistics(self, callback, account_id, fields=None):
        url = '/wgsh/accounts/{account_id}/'.format(account_id=account_id)
        return self._request_data(callback, url, get_data={}, converters={}, method='GET')

    def join_event(self, callback, event_id, fields=None):
        url = '/wgelen/wot/v1/join_event'
        post_data = {'event_id': event_id}
        return self._request_data(callback, url, method='POST', post_data=post_data)

    def leave_event(self, callback, event_id, fields=None):
        url = '/wgelen/wot/v1/leave_event'
        post_data = {'event_id': event_id}
        return self._request_data(callback, url, method='POST', post_data=post_data)

    def get_events_data(self, callback, fields=None):
        url = '/wgelen/wot/v1/get_events_data'
        return self._request_data(callback, url, method='GET')

    def get_hangar_flag(self, callback, fields=None):
        url = '/wgelen/wot/v1/get_hangar_flag'
        return self._request_data(callback, url, method='GET')

    def get_leaderboard(self, callback, event_id, page_number, leaderboard_id, fields=None):
        url = '/wgelen/wot/v1/get_leaderboard'
        get_data = {'event_id': event_id,
         'page_number': page_number,
         'leaderboard_id': leaderboard_id}
        return self._request_data(callback, url, get_data, 'GET')

    def get_my_event_top(self, callback, event_id, fields=None):
        url = '/wgelen/wot/v1/get_my_event_top'
        get_data = {'event_id': event_id}
        return self._request_data(callback, url, get_data, 'GET')

    def get_my_leaderboard_position(self, callback, event_id, leaderboard_id, fields=None):
        url = '/wgelen/wot/v1/get_my_leaderboard_position'
        get_data = {'event_id': event_id,
         'leaderboard_id': leaderboard_id}
        return self._request_data(callback, url, get_data, 'GET')

    def get_player_data(self, callback, fields=None):
        url = '/wgelen/wot/v1/get_player_data'
        return self._request_data(callback, url, method='GET')

    def hof_user_info(self, callback):
        url = '/hof/user/info/'
        return self._request_data(callback, url, method='GET')

    def hof_user_exclude(self, callback):
        url = '/hof/user/exclude/'
        return self._request_data(callback, url, method='POST')

    def hof_user_restore(self, callback):
        url = '/hof/user/restore/'
        return self._request_data(callback, url, method='POST')

    def get_teaser(self, callback, additionalData=None):
        get_params = {'language': self._get_formatted_language_code()}
        if additionalData:
            get_params.update(additionalData)
        url = '/promobe/teaser/'
        return self._request_data(callback, url, get_data=get_params, method='GET')

    def send_teaser(self, callback, promo_id):
        url = '/promobe/teaser/view/'
        params = {'promoscreen_id': promo_id,
         'language': self._get_formatted_language_code()}
        return self._request_data(callback, url, params, method='POST')

    def get_unread_count(self, callback):
        get_params = {'language': self._get_formatted_language_code()}
        url = '/promobe/unread/'
        return self._request_data(callback, url, get_data=get_params, method='GET')

    def client_promo_log(self, callback, data):
        url = '/client_promo_log/'
        return self._request_data(callback, url, data, method='GET')

    def get_mapbox_progression(self, callback):
        url = '/mapbox/progress'
        return self._request_data(callback, url, method='GET')

    def select_mapbox_crewbook(self, callback, itemID):
        url = '/mapbox'
        return self._request_data(callback, url, method='POST', post_data={'itemID': itemID})

    def complete_survey(self, callback, surveyData):
        url = '/mapbox/surveys/complete'
        return self._request_data(callback, url, method='POST', post_data=surveyData)

    def request_authorized_survey_url(self, callback, mapURL):
        return self._request_data(callback, mapURL, method='GET')

    def get_gift_system_state(self, callback, req_event_ids):
        url = '/giftsystem/event/state'
        get_params = {'event_id': req_event_ids}
        return self._request_data(callback, url, get_data=get_params, method='GET')

    def post_gift_system_gift(self, callback, entitlement_code, receiver_id, meta_info):
        url = '/giftsystem/gift'
        post_data = {'entitlement_code': entitlement_code,
         'receiver_id': receiver_id}
        post_data.update(meta_info)
        return self._request_data(callback, url, method='POST', post_data=post_data)

    def get_uilogging_session(self, callback):
        return self._request_data(callback, '/uilogging/session', method='GET')

    def get_inventory_entitlements(self, callback, entitlement_codes):
        url = '/shop/inventory_entitlements/'
        if entitlement_codes:
            urlencoded_string = urllib.urlencode([ ('entitlement_codes', code) for code in entitlement_codes ])
            url = '{}?{}'.format(url, urlencoded_string)
        return self._request_data(callback, url, method='GET')

    def get_inventory_entitlements_v5(self, callback, entitlementsFilter):
        url = '/agate/api/v5/inventory/getInventoryEntitlements/'
        return self._request_data(callback, url, method='POST', post_data=entitlementsFilter)

    def _get_formatted_language_code(self):
        return self.client_lang.replace('_', '-')
