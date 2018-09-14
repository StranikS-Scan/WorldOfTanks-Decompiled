# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/client_request_lib/data_sources/gateway.py
"""
Created on Jul 1, 2015

@author: oleg
"""
import json
from urllib import urlencode
from datetime import datetime, timedelta, time as dt_time
from client_request_lib import exceptions
from client_request_lib.data_sources import base
from base64 import b64encode
import urllib
import zlib
from debug_utils import LOG_DEBUG
EXAMPLES = {}
DEFAULT_SINCE_DELAY = timedelta(days=1)
SUCCESS_STATUSES = [200, 201]
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
    """
    obtain data from client gateway
    
    both function with fetchurl signature and gateway configuration
    should be passed during instantination
    
    :Example:
    
    >>> from client_request_lib.data_sources.fetcher import fetchURL
    >>> gateway_accessor = GatewayDataAccessor(
    ...     fetchURL, 'http://wgcg.ru.cwpp.iv/')
    >>> requester = Requester(gateway_accessor)
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
    """

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
                    content_encoding = response.headers().get('Content-Encoding')
                    if content_encoding == 'gzip':
                        data = zlib.decompress(data, 16 + zlib.MAX_WBITS)
                    data = json.loads(data)
                except:
                    data = None

                if response.responseCode not in SUCCESS_STATUSES:
                    error_data = None
                    if data:
                        error_data = {'description': data['description'],
                         'title': data.get('title', ''),
                         'notification_type': data.get('notification_type', ''),
                         'extra_data': data.get('extra_data')}
                    return callback(error_data, response.responseCode, response.responseCode)
                else:
                    response_code = exceptions.ResponseCodes.NO_ERRORS
                    if func:
                        data = func(data)
                    if converters:
                        self._apply_converters(data, converters)
                    callback(data, response.responseCode, response_code)
                    return

            return wrapped(something, func=None) if not callable(something) else wrapped

        return wrapper

    def __init__(self, url_fetcher, gateway_host, client_lang=None, user_agent=None):
        """
        url_fetcher is fetch_url method with following signature
        staging_hosts is dict of staging hosts for example
        
        :param url_fetcher: fetchURL callback with following signature
                fetchURL(url, callback, headers={}, timeout=30, method='GET', post_data='')
        :param gateway_host: gateway host
        :param client_lang: client language
        :param user_agent: user agent to be passed to WGCG
        :type url_fetcher: function
        :type gateway_host: string
        :type client_lang: string
        :type user_agent: string
        
        :Example:
        
        >>> from client_request_lib.data_sources.fetcher import fetchURL
        >>> staging_accessor = GatewayDataAccessor(
        ...     fetchURL, 'http://wgccfe.clan0101.wgnt.iv/clans/'
        ... )
        
        """
        self.client_lang = client_lang
        self._session_id = None
        self.url_fetcher = url_fetcher
        self.gateway_host = gateway_host
        self.user_agent = user_agent
        return

    def login(self, callback, account_id, spa_token):
        auth = b64encode(':'.join([str(account_id), str(spa_token)]))
        extra_headers = {'AUTHORIZATION': 'Basic %s' % auth}

        def inner_callback(data, status_code, response_code):
            if status_code in SUCCESS_STATUSES:
                self._session_id = data['session']
            callback(data, status_code, response_code)

        self._request_data(inner_callback, '/login/', headers=extra_headers)

    def logout(self, callback):
        self._request_data(callback, '/logout/')
        self._session_id = None
        return

    def _request_data(self, callback, url, get_data={}, method='GET', post_data=None, headers=None, converters=None):
        get_data = {k:v for k, v in get_data.iteritems() if v}
        url = '/'.join([self.gateway_host.strip('/'), url.strip('/'), ''])
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
        headers = tuple(('{}: {}'.format(*d) for d in default_headers.iteritems()))
        args = [headers, 30.0, method]
        if post_data:
            args.append(json.dumps(post_data))
        self.url_fetcher(url, self._preprocess_callback(callback, converters=converters), *args)

    def get_clans_ratings(self, callback, clan_ids, fields=None):
        """
        return data from ratings backend using `bulks API method`_
        
                .. _bulks API method: http://rtd.wargaming.net/docs/wgrs-api/en/latest/clans.html#bulks
        """
        get_params = {'clan_ids': clan_ids,
         'fields': fields}
        url = '/ratings/clans/'
        return self._request_data(callback, url, get_data=get_params)

    def get_clans_info(self, callback, clan_ids, fields=None):
        """
        return data from WGCCBE backend using `clans API method`_
        
                .. _clans API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/api-common/clans.html
        """
        get_params = {'clan_ids': clan_ids,
         'fields': fields}
        url = '/clans/info/'
        return self._request_data(callback, url, get_data=get_params, converters={'created_at': from_iso})

    def get_accounts_names(self, callback, account_ids, fields=None):
        """
        return data from SPA backend using `account id/name mappings API method`_
        
                .. _account id/name mappings API method: https://confluence.wargaming.net/display/WEBDEV/%5BWGNSPA%5D+-
                +SPA+HTTP+API+Examples#id-[WGNSPA]-SPAHTTPAPIExamples-Byids
        """
        get_params = {'id': account_ids,
         'fields': fields}
        url = '/accounts/names/'
        return self._request_data(callback, url, get_data=get_params, converters={'id': int})

    def get_clan_members(self, callback, clan_id, fields=None):
        """
        return data from WGCCBE backend using `clan members API method`_
        
                .. _clan members API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/api-common/
                clans_id_members.html
        """
        get_params = {'fields': fields}
        url = '/clans/%s/members/' % clan_id
        return self._request_data(callback, url, get_data=get_params, converters={'joined_at': from_iso})

    def get_clan_favorite_attributes(self, callback, clan_id, fields=None):
        """
        return data from WGCCBE backend using `favorite_attributes API method`_
        
                .. _favorite_attributes API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/
                statistics/favorite_attributes.html
        """
        url = '/clans/%s/favorite_attributes/' % clan_id
        return self._request_data(callback, url, converters={'favorite_primetime': lambda x: x and datetime.strptime(x, '%H:%M').time(),
         'favorite_arena_6': int,
         'favorite_arena_8': int,
         'favorite_arena_10': int})

    def get_accounts_clans(self, callback, account_ids, fields=None):
        """
        return data from WGCCBE backend using `accounts API method`_
        
                .. _accounts API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/api-common/accounts.html
        """
        get_params = {'fields': fields,
         'account_ids': account_ids}
        url = '/accounts/clans/'
        return self._request_data(callback, url, get_data=get_params, converters={'in_clan_cooldown_till': from_iso,
         'joined_at': from_iso})

    def get_account_applications_count_since(self, callback, account_id, since=None):
        """
        return data from WGCCBE backend using `applications API method`_
        
                .. _applications API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/wotx/applications.html
        """
        since = since or datetime.utcnow() - DEFAULT_SINCE_DELAY
        get_params = {'created_after': since.isoformat()}
        url = '/accounts/%s/applications/count/' % account_id
        return self._request_data(callback, url, get_data=get_params)

    def get_clan_invites_count_since(self, callback, clan_id, since=None):
        """
        return data from WGCCBE backend using `invites API method`_
        
                .. _invites API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/wotx/invites.html
        """
        since = since or datetime.utcnow() - DEFAULT_SINCE_DELAY
        get_params = {'created_after': since.isoformat()}
        url = '/clans/%s/invites/count/' % clan_id
        return self._request_data(callback, url, get_data=get_params)

    def get_alive_status(self, callback):
        url = '/ping/'
        return self._request_data(callback, url)

    def get_account_applications(self, callback, fields=None, statuses=None, get_total_count=False, limit=None, offset=None):
        """
        return data from WGCCBE backend using `applications API method`_
        
                .. _applications API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/wotx/applications.html
        """
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
        """
        return data from WGCCBE backend using `applications API method`_
        
                .. _applications API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/wotx/applications.html
        """
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
        """
        create applications for accounts into clan using `create applications API method`_
                .. _create applications API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/wotx/
                applications.html
        """
        url = '/clans/applications/'
        data = {'clan_ids': clan_ids,
         'comment': comment}
        return self._request_data(callback, url, method='POST', post_data=data)

    def accept_application(self, callback, application_id, fields=None):
        """
        accept application for accounts into clan using `accept applications API method`_
                .. _accept applications API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/wotx/
                applications_id.html
        """
        url = '/clans/applications/%s/' % application_id
        data = {'status': 'accepted'}
        return self._request_data(callback, url, method='PATCH', post_data=data)

    def decline_application(self, callback, application_id, fields=None):
        """
        decline application for accounts into clan using `decline applications API method`_
                .. _decline applications API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/wotx/
                applications_id.html
        """
        url = '/clans/applications/%s/' % application_id
        data = {'status': 'declined'}
        return self._request_data(callback, url, method='PATCH', post_data=data)

    def create_invites(self, callback, clan_id, account_ids, comment, fields=None):
        """
        create applications for accounts into clan using `create invites API method`_
                .. _create invites API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/wotx/invites.html
        """
        url = '/clans/%s/invites/' % clan_id
        data = {'account_ids': account_ids,
         'comment': comment}
        return self._request_data(callback, url, method='POST', post_data=data)

    def accept_invite(self, callback, invite_id, fields=None):
        """
        accept application for accounts into clan using `accept invite API method`_
                .. _accept invite API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/wotx/invites_id.html
        """
        url = '/clans/invites/%s/' % invite_id
        data = {'status': 'accepted'}
        return self._request_data(callback, url, method='PATCH', post_data=data)

    def decline_invite(self, callback, invite_id, fields=None):
        """
        decline application for accounts into clan using `decline invites API method`_
                .. _decline invites API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/wotx/invites_id.html
        """
        url = '/clans/invites/%s/' % invite_id
        data = {'status': 'declined'}
        return self._request_data(callback, url, method='PATCH', post_data=data)

    def bulk_decline_invites(self, callback, invite_ids, fields=None):
        """
        decline application for accounts into clan using `decline invites API method`_
                .. _decline invites API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/wgcc/invites.html#patch
        """
        url = '/clans/decline_invites/'
        data = {'invite_ids': invite_ids}
        return self._request_data(callback, url, method='PATCH', post_data=data)

    def search_clans(self, callback, search, get_total_count=False, fields=None, offset=None, limit=None):
        """
        return data from WGCCBE backend using `clans API method`_
        
                .. _clans API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/api-common/clans.html
        """
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
        """
        return data from WGCCBE backend using `clans API method`_
        
                .. _clans API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/api-common/clans.html
        """
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
        """
        return data from WGCCBE backend using `invites API method`_
        
                .. _invites API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/wotx/invites.html
        """
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
        """
        return data from WGCCBE backend using `invites API method`_
        
                .. _invites API method: http://rtd.wargaming.net/docs/wgccbe/en/latest/wotx/invites.html
        """
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
        """
        return data from exporter backend using `accounts detailed information`_
        
                .. _accounts detailed information: http://rtd.wargaming.net/docs/exporter/en/latest/
                api_wot.html#accounts-detailed-information
        """
        get_params = {'account_ids': account_ids,
         'fields': fields}
        url = '/accounts/info/'
        return self._request_data(callback, url, get_data=get_params, converters={'account_id': int})

    def get_clan_provinces(self, callback, clan_id, fields=None):
        """
        return data from WGCW backend using `clans provinces API method`_
        
                .. _clans provinces API method: http://rtd.wargaming.net/docs/wgcw/en/latest/api/
                wgapi.html?highlight=stats#clans-provinces
        """
        get_params = {'clan_id': [clan_id],
         'fields': fields}
        url = '/clans/provinces/'
        return self._request_data(callback, url, get_data=get_params, converters={'prime_time': lambda x: x and datetime.strptime(x, '%H:%M').time(),
         'pillage_end_datetime': from_iso,
         'clan_id': int})

    def get_clan_globalmap_stats(self, callback, clan_id, fields=None):
        """
        return data from WGCW backend using `clans stats API method`_
        
                .. _clans stats API method: http://rtd.wargaming.net/docs/wgcw/en/latest/api/
                wgapi.html?highlight=stats#clans-stats
        """
        url = '/clans/global_map/stats/'
        get_params = {'clan_id': clan_id}
        if fields:
            get_params['fields'] = fields
        return self._request_data(callback, url, get_data=get_params, converters={'clan_id': int})

    def get_fronts_info(self, callback, front_names=None, fields=None):
        """
        return data from WGCW backend using `fronts info API method`_
        
                .. _fronts info API method: http://rtd.wargaming.net/docs/wgcw/en/latest/api/
                wgapi.html?highlight=stats#id1
        """
        url = '/global_map/fronts/'
        get_params = {'fields': fields,
         'front_names': front_names}
        return self._request_data(callback, url, get_data=get_params)

    def get_stronghold_info(self, callback, clan_id, fields=None):
        """
        return data from WGCCFE backend using `stronghold info API method`_
        
                .. _stronghold info API method: http://rtd.wargaming.net/docs/wgccfe/en/latest/rst/
                strongholds.html#strongholds-clan-id
        """
        url = '/strongholds/info/'
        get_params = {'clan_id': clan_id}
        if fields:
            get_params['fields'] = fields
        return self._request_data(callback, url, get_data=get_params, converters={'clan_id': int,
         'defence_hour': lambda x: dt_time(x, 0) if x >= 0 else None})

    def get_strongholds_statistics(self, callback, clan_id, fields=None):
        """
        return data from WGCCFE backend using `stronghold statistics API method`_
        
                .. _stronghold statistics API method: http://rtd.wargaming.net/docs/wgccfe/en/latest/
                rst/strongholds.html#strongholds-statistics-clan-id
        """
        url = '/strongholds/statistics/'
        get_params = {'clan_id': clan_id}
        if fields:
            get_params['fields'] = fields
        return self._request_data(callback, url, get_data=get_params, converters={'vacation_start': timestamp_to_datetime,
         'vacation_finish': timestamp_to_datetime})

    def get_strongholds_state(self, callback, clan_id, fields=None):
        """
        return data from WGCCFE backend using `stronghold state API method`_
        
                .. _stronghold state API method: http://rtd.wargaming.net/docs/wgccfe/en/latest/rst/
                strongholds.html#strongholds-state
        """
        url = '/strongholds/state/'
        get_params = {'clan_id': clan_id}
        return self._request_data(callback, url, get_data=get_params, converters={'clan_id': int,
         'defence_hour': lambda x: dt_time(x, 0) if x >= 0 else None})

    def get_wgsh_unit_info(self, callback, periphery_id, unit_server_id, fields=None):
        """
        return data from WGSH backend with info needed for prebattle window header
        
            .. _prebattle info API method:
            https://stash.wargaming.net/projects/CLANWARS/repos/wgsh/browse/docs/unit_api/api.md
        """
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int})

    def set_vehicle(self, callback, periphery_id, unit_server_id, vehicle_cd, fields=None):
        """
        request WGSH to change player vehicle
        
            .. _prebattle info API method:
            https://stash.wargaming.net/projects/CLANWARS/repos/wgsh/browse/docs/unit_api/api.md
        """
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/vehicles/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'vehicle_cd': vehicle_cd}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='PATCH', post_data=post_data)

    def set_readiness(self, callback, periphery_id, unit_server_id, is_ready, reset_vehicle, fields=None):
        """
        request WGSH to change player readiness
        
            .. _prebattle info API method:
            https://stash.wargaming.net/projects/CLANWARS/repos/wgsh/browse/docs/unit_api/api.md
        """
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/readiness/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        patch_data = {'is_ready': is_ready,
         'reset_vehicle': reset_vehicle}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='PATCH', post_data=patch_data)

    def invite_players(self, callback, periphery_id, unit_server_id, accounts_to_invite, comment, fields=None):
        """
        request WGSH to send invites to players
        
            .. _prebattle info API method:
            https://stash.wargaming.net/projects/CLANWARS/repos/wgsh/browse/docs/unit_api/api.md
        """
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/invite/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'accounts_to_invite': accounts_to_invite,
         'comment': comment}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='POST', post_data=post_data)

    def assign_player(self, callback, periphery_id, unit_server_id, account_to_assign, slot_id_to_assign, fields=None):
        """
        request WGSH to assign given player to battle
        
            .. _prebattle info API method:
            https://stash.wargaming.net/projects/CLANWARS/repos/wgsh/browse/docs/unit_api/api.md
        """
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/assign/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'account_to_assign': account_to_assign,
         'slot_id_to_assign': slot_id_to_assign}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='POST', post_data=post_data)

    def unassign_player(self, callback, periphery_id, unit_server_id, account_to_unassign, fields=None):
        """
        request WGSH to unassign given player from battle
        
            .. _prebattle info API method:
            https://stash.wargaming.net/projects/CLANWARS/repos/wgsh/browse/docs/unit_api/api.md
        """
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/unassign/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'account_to_unassign': account_to_unassign}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='POST', post_data=post_data)

    def give_leadership(self, callback, periphery_id, unit_server_id, target_account_id, fields=None):
        """
        request WGSH to make player a leader
        
            .. _prebattle info API method:
            https://stash.wargaming.net/projects/CLANWARS/repos/wgsh/browse/docs/unit_api/api.md
        """
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/give_leadership/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'target_account_id': target_account_id}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='PATCH', post_data=post_data)

    def leave_room(self, callback, periphery_id, unit_server_id, fields=None):
        """
        request WGSH to leave current user from room
        
            .. _prebattle info API method:
            https://stash.wargaming.net/projects/CLANWARS/repos/wgsh/browse/docs/unit_api/api.md
        """
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/leave/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='POST')

    def take_away_leadership(self, callback, periphery_id, unit_server_id, fields=None):
        """
        request WGSH to take leadership on room if current user have rights
        
            .. _prebattle info API method:
            https://stash.wargaming.net/projects/CLANWARS/repos/wgsh/browse/docs/unit_api/api.md
        """
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/take_away_leadership/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='PATCH')

    def kick_player(self, callback, periphery_id, unit_server_id, account_to_kick, fields=None):
        """
        request WGSH to kick player from unit
        
            .. _prebattle info API method:
            https://stash.wargaming.net/projects/CLANWARS/repos/wgsh/browse/docs/unit_api/api.md
        """
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/kick/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'account_to_kick': account_to_kick}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='POST', post_data=post_data)

    def set_open(self, callback, periphery_id, unit_server_id, is_open, fields=None):
        """
        request WGSH to set unit to open
        
            .. _prebattle info API method:
            https://stash.wargaming.net/projects/CLANWARS/repos/wgsh/browse/docs/unit_api/api.md
        """
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/set_open/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'is_open': is_open}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='PATCH', post_data=post_data)

    def lock_reserve(self, callback, periphery_id, unit_server_id, reserve_id, fields=None):
        """
        request WGSH to lock given reserve
        
            .. _prebattle info API method:
            https://stash.wargaming.net/projects/CLANWARS/repos/wgsh/browse/docs/unit_api/api.md
        """
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/lock_reserve/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'reserve_id': reserve_id}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='POST', post_data=post_data)

    def unlock_reserve(self, callback, periphery_id, unit_server_id, reserve_id, fields=None):
        """
        request WGSH to unlock given reserve
        
            .. _prebattle info API method:
            https://stash.wargaming.net/projects/CLANWARS/repos/wgsh/browse/docs/unit_api/api.md
        """
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/unlock_reserve/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        post_data = {'reserve_id': reserve_id}
        return self._request_data(callback, url, get_data={}, converters={'periphery_id': int,
         'unit_server_id': int}, method='POST', post_data=post_data)

    def clan_statistics(self, callback, clan_id, fields=None):
        """
        request WGSH to get clan statistics
        
            .. _prebattle info API method:
            https://confluence.wargaming.net/display/WEBDEV/WGSH+-+API+for+WoT+client+dialogs
        """
        url = '/wgsh/clans/{clan_id}/'.format(clan_id=clan_id)
        return self._request_data(callback, url, get_data={}, converters={}, method='GET')

    def join_room(self, callback, periphery_id, unit_server_id, fields=None):
        """
        request WGSH to join current user to room
        
            .. _prebattle info API method:
            https://stash.wargaming.net/projects/CLANWARS/repos/wgsh/browse/docs/unit_api/api.md
        """
        url = '/wgsh/periphery/{periphery_id}/units/{unit_server_id}/join/'.format(periphery_id=periphery_id, unit_server_id=unit_server_id)
        return self._request_data(callback, url, get_data={}, method='POST')

    def account_statistics(self, callback, account_id, fields=None):
        """
        request WGSH to get account statistics
        
            .. _prebattle info API method:
            https://confluence.wargaming.net/display/WEBDEV/WGSH+-+API+for+WoT+client+dialogs
        """
        url = '/wgsh/accounts/{account_id}/'.format(account_id=account_id)
        return self._request_data(callback, url, get_data={}, converters={}, method='GET')
