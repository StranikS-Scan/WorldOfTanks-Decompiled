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
    """
    Provide access to data accessor passed as argument while instance creation
    
    :Example:
    
    >>> class SomeClass(object):
    ...     some = RequestDescriptor(SomeAccessor)
    
    
    .. note:: `SomeAccessor` in this example should accept data_source as arg
    
    """

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


class GmAccessor(BaseAccessor):
    """
    Global map accessor
    
    Access global map data from `data_source` instance
    
    :Example:
    
    >>> class SomeClass(object):
    ...     global_map = RequestDescriptor(GmAccessor)
    ...
    >>> requester=SomeClass(DataAccessor())
    >>> requester.global_map.get_provinces(str, 12312)
    
    """

    def get_provinces(self, callback, clan_id, fields=None):
        """
        request provinces information and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.global_map.get_provinces(printer, 12312)
        (
            [
                {
                    'front_name': 'some_front',
                    'game_map': 'some_map',
                    'hq_connected': True,
                    'periphery': 333,
                    'prime_time': '',
                    'province_id': 'some_province',
                    'revenue': 324,
                    'turns_owned': 12
                }
            ],
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param clan_id: identifier of the clan whose provinces are requested
        :param fields: field set to obtain (optional param)
        :type callback: function
        :type clan_id: integer
        :type fields: list of strings
        """
        return self._data_source.get_clan_provinces(callback, clan_id, fields=fields)

    def get_statistics(self, callback, clan_id, fields=None):
        """
        request statistic information and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.global_map.get_statistics(printer, 12312)
        (
            {
                'battles_lost': 12,
                'battles_played': 332,
                'battles_played_on_10_level': 43,
                'battles_played_on_6_level': 21,
                'battles_played_on_8_level': 32,
                'battles_won': 232,
                'battles_won_on_10_level': 23,
                'battles_won_on_6_level': 12,
                'battles_won_on_8_level': 21,
                'influence_points': 121,
                'provinces_captured': 23
            },
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param clan_id: identifier of the clan whose global map statistic
                        are requested
        :param fields: field set to obtain (optional param)
        :type callback: function
        :type clan_id: integer
        :type fields: list of strings
        """
        return self._data_source.get_clan_globalmap_stats(callback, clan_id, fields=fields)

    def get_fronts_info(self, callback, front_names=None, fields=None):
        """
        request fronts information and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.global_map.get_fronts_info(printer)
        (
            [
                {
                    'front_name': 'front_name',
                    'max_vehicle_level': 4,
                    'min_vehicle_level': 2
                }
            ],
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param fields: field set to obtain (optional param)
        :type callback: function
        :type fields: list of strings
        """
        return self._data_source.get_fronts_info(callback, front_names=front_names, fields=fields)


class RatingAccessor(BaseAccessor):
    """
    Rating accessor
    
    Access rating data from `data_source` instance
    
    :Example:
    
    >>> class SomeClass(object):
    ...     iratings = RequestDescriptor(RatingAccessor)
    ...
    >>> requester=SomeClass(DataAccessor())
    >>> requester.ratings.get_ratings(str, [12312, 3243])
    """

    def get_clans_ratings(self, callback, clan_ids, fields=None):
        """
        request clans ratings information and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.ratings.get_clans_ratings(printer, [123,])
        (
            [
                {
                    'battles_count_avg': 42.2,
                    'clan_id': 123,
                    'efficiency': 34,
                    'fb_battles_count_10_28d': 21,
                    'fb_elo_rating_10': 231,
                    'fb_elo_rating_8': 213,
                    'fs_battles_count_10_28d': 12,
                    'gm_battles_count_28d': 15,
                    'gm_elo_rating_10': 342,
                    'gm_elo_rating_10_rank': 21,
                    'gm_elo_rating_6': 341,
                    'gm_elo_rating_6_rank': 11,
                    'gm_elo_rating_8': 421,
                    'gm_elo_rating_8_rank': 13,
                    'wins_ratio_avg': 43.3
                }
            ],
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param clan_ids: list of clans identifier which ratings are requested
        :param fields: field set to obtain (optional param)
        :type callback: function
        :type clan_ids: list of integer
        :type fields: list of strings
        """
        return self._data_source.get_clans_ratings(callback, clan_ids, fields=fields)


class ExporterAccessor(BaseAccessor):
    """
    Exporter accessor
    
    Access exporter data from `data_source` instance
    
    :Example:
    
    >>> class SomeClass(object):
    ...     exporter = RequestDescriptor(ExporterAccessor)
    ...
    >>> requester=SomeClass(DataAccessor())
    >>> requester.exporter.get_accounts_info(str, [12312, 123])
    """

    def get_accounts_info(self, callback, account_ids, fields=None):
        """
        request accounts information and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.exporter.get_accounts_info(printer, [123,])
        (
            [
                {
                    'account_id': 232,
                    'battle_avg_performance': 32.3,
                    'battle_avg_xp': 234.5,
                    'battles_count': 34,
                    'global_rating': 123.2,
                    'xp_amount': 324
                }
            ],
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param account_ids: list of account identifiers which info
                            is requested
        :param fields: field set to obtain (optional param)
        :type callback: function
        :type account_ids: list of integer
        :type fields: list of strings
        """
        return self._data_source.get_accounts_info(callback, account_ids, fields=fields)


class SpaAccessor(BaseAccessor):
    """
    SPA accessor
    
    Access spa data from `data_source` instance
    
    :Example:
    
    >>> class SomeClass(object):
    ...     spa = RequestDescriptor(SpaAccessor)
    ...
    >>> requester=SomeClass(DataAccessor())
    >>> requester.spa.get_accounts_names(str, [12312, 213])
    """

    def get_accounts_names(self, callback, account_ids, fields=None):
        """
        request accounts names and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.spa.get_accounts_names(printer, [123,])
        (
            [{'id': 123, 'name': 'name'}],
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param account_ids: list of account identifiers which names
                            are requested
        :param fields: field set to obtain (optional param)
        :type callback: function
        :type account_ids: list of integer
        :type fields: list of strings
        """
        return self._data_source.get_accounts_names(callback, account_ids, fields=fields)


class ClansAccessor(BaseAccessor):
    """
    Clan info accessor
    
    Access clans info data from `data_source` instance
    
    :Example:
    
    >>> class SomeClass(object):
    ...     clans = RequestDescriptor(ClansAccessor)
    ...
    >>> requester=SomeClass(DataAccessor())
    >>> requester.clans.get_clans_info(str, [12312, 344])
    """

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
        """
        request clans info and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.get_clans_info(printer, [123,])
        (
            [
                {
                    'accepts_join_requests': True,
                    'clan_id': 13,
                    'created_at': datetime.datetime(2015, 8, 16, 13, 41, 31, 865000),
                    'leader_id': 666,
                    'members_count': 13,
                    'motto': 'yyyy',
                    'name': 'xxx',
                    'tag': 'ff',
                    'treasury': 2423
                }
            ],
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param clan_ids: list of clans identifiers which info is requested
        :param fields: field set to obtain (optional param)
        :type callback: function
        :type clan_ids: list of integer
        :type fields: list of strings
        """
        return self._data_source.get_clans_info(callback, clan_ids, fields=fields)

    def search_clans(self, callback, search, fields=None, offset=0, limit=18, get_total_count=False):
        """
        request clans by substring in name or tag and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.search_clans(printer, 'foo', get_total_count=True)
        (
            {
                'items': [
                    {
                        'accepts_join_requests': True,
                        'clan_id': 13,
                        'created_at': datetime.datetime(2015, 8, 16, 13, 41, 31, 865000),
                        'leader_id': 666,
                        'members_count': 13,
                        'motto': 'yyyy',
                        'name': 'xxx',
                        'tag': 'foo',
                    },
                ],
                'total': 1
            },
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param search: substring predicate used to get clans list which
                        name or tag has search substring
        :param fields: field set to obtain (optional param)
        :param offset: offset of clans portion
        :param limit: maximum size of a portion
        :param get_total_count: whether total count is included in response
        :type callback: function
        :type search: string
        :type fields: list of strings
        :type offset: integer
        :type limit: integer
        :type get_total_count: boolean
        """
        return self._data_source.search_clans(callback, search, fields=fields, offset=offset, limit=limit, get_total_count=get_total_count)

    def get_recommended_clans(self, callback, fields=None, offset=0, limit=18, get_total_count=False):
        """
        request recommended clans and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.get_recommended_clans(printer, get_total_count=True)
        (
            {
                'items': [
                    {
                        'accepts_join_requests': True,
                        'clan_id': 13,
                        'created_at': datetime.datetime(2015, 8, 16, 13, 41, 31, 865000),
                        'leader_id': 666,
                        'members_count': 13,
                        'motto': 'yyyy',
                        'name': 'xxx',
                        'tag': 'foo',
                    },
                ],
                'total': 1
            },
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param fields: field set to obtain (optional param)
        :param offset: offset of clans portion
        :param limit: maximum size of a portion
        :param get_total_count: whether total count is included in response
        :type callback: function
        :type fields: list of strings
        :type offset: integer
        :type limit: integer
        :type get_total_count: boolean
        """
        return self._data_source.get_recommended_clans(callback, fields=fields, offset=offset, limit=limit, get_total_count=get_total_count)

    def get_account_applications_count_since(self, callback, account_id, since=None):
        """
        request account applications count and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.get_account_applications_count_since(printer, 123)
        (
            {'total': 17},
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param account_id: account identifier which applications
                            count is requested
        :param since: start of period apllication created since
                    which is counted
        :type callback: function
        :type clan_ids: list of integer
        :type since: datetime
        """
        return self._data_source.get_account_applications_count_since(callback, account_id, since=since)

    def get_clan_invites_count_since(self, callback, clan_id, since=None):
        """
        request clan invitations count and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.get_clan_invites_count_since(printer, 123)
        (
            {'total': 17},
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param clan_id: list of clan identifier which invites count
                        is requested
        :param since: start of period invites created since this
                    time is requested
        :type callback: function
        :type clan_ids: list of integer
        :type since: datetime
        """
        return self._data_source.get_clan_invites_count_since(callback, clan_id, since=since)

    def get_clan_members(self, callback, clan_id, fields=None):
        """
        request clan members and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.get_clan_members(printer, 123)
        (
            [
                {
                    'account_id': 2324,
                    'clan_id': 111,
                    'joined_at': datetime.datetime(2015, 8, 16, 13, 41, 31, 866000),
                    'role': 1
                }
            ],
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param clan_id: clan identifier which members is requested
        :param fields: field set to obtain (optional param)
        :type callback: function
        :type clan_id: integer
        :type fields: list of strings
        """
        return self._data_source.get_clan_members(callback, clan_id, fields=fields)

    def get_clan_favorite_attributes(self, callback, clan_id, fields=None):
        """
        request favorite_arena and favorite_primetime and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.get_clan_favorite_attributes(printer, 123)
        (
            [
                {
                    "favorite_arena": "6",
                    "clan_id": 123,
                    "favorite_primetime": "19:00"
                }
            ],
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param clan_id: clan identifier which favorite attributes are requested
        :param fields: field set to obtain (optional param)
        :type callback: function
        :type clan_id: integer
        :type fields: list of strings
        """
        return self._data_source.get_clan_favorite_attributes(callback, clan_id, fields=fields)

    def get_accounts_clans(self, callback, account_ids, fields=None):
        """
        request accounts clans and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.get_accounts_clans(printer, [123,])
        (
            [
                {
                    'account_id': 234,
                    'clan_id': 343,
                    'in_clan_cooldown_till': datetime.datetime(2015, 8, 16, 13, 41, 31, 866000),
                    'joined_at': datetime.datetime(2015, 8, 16, 13, 41, 31, 866000),
                    'roles_bw_flags': 13,
                    'roles_names': 'commander'
                }
            ],
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param account_ids: accounts identifiers which clans are requested
        :param fields: field set to obtain (optional param)
        :type callback: function
        :type account_ids: list of integer
        :type fields: list of strings
        """
        return self._data_source.get_accounts_clans(callback, account_ids, fields=fields)

    def get_account_invites(self, callback, fields=None, statuses=None, offset=0, limit=18, get_total_count=False):
        """
        request account invites and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.get_account_invites(printer, 123, get_total_count=True)
        (
            {
                'items': [
                    {
                        'account_id': 123,
                        'clan_id': 7623,
                        'comment': 'Welcome!',
                        'created_at': datetime.datetime(2015, 8, 16, 13, 41, 31, 866000),
                        'id': 2,
                        'sender_id': 26,
                        'status': 'active',
                        'updated_at': datetime.datetime(2015, 8, 16, 13, 41, 31, 866000)
                    }
                ],
                'total': 1
            },
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param fields: field set to obtain (optional param)
        :param statuses: invites statuses to request
        :param offset: offset of invites portion
        :param limit: maximum size of invites portion
        :param get_total_count: wheter total count of invites is needed
        :type callback: function
        :type fields: list of strings
        :type statuses: list of strings
        :type offset: integer
        :type limit: integer
        :type get_total_count: boolean
        """
        return self._data_source.get_account_invites(callback, fields=fields, statuses=statuses, offset=offset, limit=limit, get_total_count=get_total_count)

    def get_clan_invites(self, callback, clan_id, fields=None, statuses=None, offset=0, limit=18, get_total_count=False):
        """
        request clan invites and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.get_clan_invites(printer, 123, get_total_count=True)
        (
            {
                'items': [
                    {
                        'account_id': 5014,
                        'clan_id': 123,
                        'comment': 'Welcome!',
                        'created_at': datetime.datetime(2015, 8, 16, 13, 41, 31, 866000),
                        'id': 2,
                        'sender_id': 26,
                        'status': 'active',
                        'updated_at': datetime.datetime(2015, 8, 16, 13, 41, 31, 866000)
                    }
                ],
                'total': 1
            },
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param clan_id: clan identifier which invites are requested
        :param fields: field set to obtain (optional param)
        :param statuses: invites statuses to request
        :param offset: offset of invites portion
        :param limit: maximum size of invites portion
        :param get_total_count: wheter total count of invites is needed
        :type callback: function
        :type clan_id: integer
        :type fields: list of strings
        :type statuses: list of strings
        :type offset: integer
        :type limit: integer
        :type get_total_count: boolean
        """
        return self._data_source.get_clan_invites(callback, clan_id, fields=fields, statuses=statuses, offset=offset, limit=limit, get_total_count=get_total_count)

    def get_account_applications(self, callback, fields=None, statuses=None, offset=0, limit=18, get_total_count=False):
        """
        request clan applications and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.get_clan_applications(printer, 123, get_total_count=True)
        (
            {
                'items': [
                    {
                        'account_id': 5014,
                        'clan_id': 7623,
                        'comment': 'Welcome!',
                        'created_at': datetime.datetime(2015, 8, 16, 13, 41, 31, 866000),
                        'id': 2,
                        'sender_id': 26,
                        'status': 'active',
                        'updated_at': datetime.datetime(2015, 8, 16, 13, 41, 31, 866000)
                    }
                ],
                'total': 1
            },
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param fields: field set to obtain (optional param)
        :param statuses: applications statuses to request
        :param offset: offset of applications portion
        :param limit: maximum size of applications portion
        :param get_total_count: wheter total count of invites is needed
        :type callback: function
        :type fields: list of strings
        :type statuses: list of strings
        :type offset: integer
        :type limit: integer
        :type get_total_count: boolean
        """
        return self._data_source.get_account_applications(callback, fields=fields, statuses=statuses, offset=offset, limit=limit, get_total_count=get_total_count)

    def get_clan_applications(self, callback, clan_id, fields=None, statuses=None, offset=0, limit=18, get_total_count=False):
        """
        request clan applications and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.get_clan_applications(printer, 123, get_total_count=True)
        (
            {
                'items': [
                    {
                        'account_id': 5014,
                        'clan_id': 7623,
                        'comment': 'Welcome!',
                        'created_at': datetime.datetime(2015, 8, 16, 13, 41, 31, 866000),
                        'id': 2,
                        'sender_id': 26,
                        'status': 'active',
                        'updated_at': datetime.datetime(2015, 8, 16, 13, 41, 31, 866000)
                    }
                ],
                'total': 1
            },
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param clan_id: clan identifier which applications are requested
        :param fields: field set to obtain (optional param)
        :param statuses: applications statuses to request
        :param offset: offset of applications portion
        :param limit: maximum size of applications portion
        :param get_total_count: wheter total count of invites is needed
        :type callback: function
        :type clan_id: integer
        :type fields: list of strings
        :type statuses: list of strings
        :type offset: integer
        :type limit: integer
        :type get_total_count: boolean
        """
        return self._data_source.get_clan_applications(callback, clan_id, fields=fields, statuses=statuses, offset=offset, limit=limit, get_total_count=get_total_count)

    def create_applications(self, callback, clan_ids, comment):
        """
        create clan applications and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.create_applications(printer, [7534, 7535], 'foo')
        (
            [
                {"clan_id": 7534, "id": 4001, "account_id": 789233456},
                {"clan_id": 7535, "id": 4002, "account_id": 789233456},
            ],
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param clan_ids: clan identifiers to application into
        :type callback: function
        :type clan_ids: list of integer
        """
        return self._data_source.create_applications(callback, clan_ids, comment)

    def accept_application(self, callback, application_id):
        """
        accept clan applications and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.accept_application(printer, 13)
        (
            {"transaction_id": 232},
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param application_id: application identifier
        :type callback: function
        :type application_id: integer
        """
        return self._data_source.accept_application(callback, application_id)

    def decline_application(self, callback, application_id):
        """
        decline clan applications and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.decline_application(printer, 13)
        (
            {"transaction_id": 232},
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param application_id: application identifier
        :type callback: function
        :type application_id: integer
        """
        return self._data_source.decline_application(callback, application_id)

    def create_invites(self, callback, clan_id, account_ids, comment):
        """
        create clan inites and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.create_inites(printer, 123, [7534, 7535], 'foo')
        (
            [
                {"clan_id": 7534, "id": 4001, "account_id": 789233456},
                {"clan_id": 7535, "id": 4002, "account_id": 789233456},
            ],
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param clan_id: clan identifier to join
        :param account_ids: accounts identifiers to invite
        :type callback: function
        :type clan_id: integer
        :type account_ids: list of integer
        """
        return self._data_source.create_invites(callback, clan_id, account_ids, comment)

    def accept_invite(self, callback, invite_id):
        """
        accept clan invite and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.accept_invite(printer, 13)
        (
            {"transaction_id": 232},
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param invite_id: invite identifier
        :type callback: function
        :type application_id: integer
        """
        return self._data_source.accept_invite(callback, invite_id)

    def decline_invite(self, callback, invite_id):
        """
        decline clan invite and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.decline_invite(printer, 13)
        (
            {"transaction_id": 232},
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param invite_id: invite identifier
        :type callback: function
        :type invite_id: integer
        """
        return self._data_source.decline_invite(callback, invite_id)

    def bulk_decline_invites(self, callback, invite_ids):
        """
        decline clan invites and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.clans.bulk_decline_invites(printer, [991, 992, 993])
        (
            [
                {"id": 991, "account_id": 1001, "clan_id": 19},
                {"id": 992, "account_id": 1001, "clan_id": 19}
            ],
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param invite_ids: invites' identifiers
        :type callback: function
        :type invite_ids: list of integers
        """
        return self._data_source.bulk_decline_invites(callback, invite_ids)


class StrongholdsAccessor(BaseAccessor):
    """
    Strongholds accessor
    
    Access strongholds data from `data_source` instance
    
    :Example:
    
    >>> class SomeClass(object):
    ...     strongholds = RequestDescriptor(StrongholdsAccessor)
    ...
    >>> requester=SomeClass(DataAccessor())
    >>> requester.strongholds.get_info(str, 12312)
    """

    def get_info(self, callback, clan_id, fields=None):
        """
        request clan stronghold info and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.strongholds.get_info(printer, 123)
        (
            {
                'buildings': [
                    {
                        'direction': 0,
                        'direction_name': '--',
                        'level': 2,
                        'type': 1
                    },
                    {
                        'direction': 1,
                        'direction_name': 'A',
                        'level': 3,
                        'type': 2
                    }
                ],
                'defence_attack_count': 13,
                'defence_attack_efficiency': 23.2,
                'defence_battles_count': 234,
                'defence_capture_enemy_building_total_count': 55,
                'defence_combat_wins': 21,
                'defence_defence_count': 24,
                'defence_defence_efficiency': 32.2,
                'defence_enemy_base_capture_count': 43,
                'defence_loss_own_building_total_count': 65,
                'defence_resource_capture_count': 322,
                'defence_resource_loss_count': 112,
                'defence_success_attack_count': 122,
                'defence_success_defence_count': 5,
                'level': 2,
                'sortie_absolute_battles_count': 23,
                'sortie_battles_count': 23,
                'sortie_champion_battles_count': 32,
                'sortie_fort_resource_in_absolute': 100,
                'sortie_fort_resource_in_champion': 71,
                'sortie_fort_resource_in_middle': 60,
                'sortie_losses': 19,
                'sortie_middle_battles_count': 12,
                'sortie_wins': 12,
                'total_resource_amount': 321
            },
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param clan_id: clan identifier which stronghold info is requested
        :param fields: field set to obtain (optional param)
        :type callback: function
        :type clan_id: integer
        :type fields: list of strings
        """
        return self._data_source.get_stronghold_info(callback, clan_id, fields=fields)

    def get_statistics(self, callback, clan_id, fields=None):
        """
        request clan stronghold statistics and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.strongholds.get_statistics(printer, 123)
        (
            {
                    'buildings': [
                        {
                            'type': 1,
                            'hp': 32,
                            'storage': 123,
                            'level': 4,
                        }
                    ],
                    'buildings_count': 4,
                    'clan_id': 21,
                    'clan_name': 'some_name',
                    'clan_tag': 'tag',
                    'directions': ['A', 'B'],
                    'directions_count': 3,
                    'level': 2,
                    'off_day': 3,
                    'periphery_id': 333,
                    'vacation_finish': datetime.datetime(2015, 8, 20, 10, 41, 31, 866000),
                    'vacation_start': datetime.datetime(2015, 8, 17, 10, 41, 31, 866000)},
                    'sortie_wins_period': 7,
                    'sortie_battles_wins_percentage_period': 20.0,
            200,
            0
            )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param clan_id: clan identifier which stronghold statistics
                        are requested
        :param fields: field set to obtain (optional param)
        :type callback: function
        :type clan_id: integer
        :type fields: list of strings
        """
        return self._data_source.get_strongholds_statistics(callback, clan_id, fields=fields)

    def get_state(self, callback, clan_id, fields=None):
        """
        request clan stronghold state and call `callback`
        with following information after response is parsed:
        
            - `result` is result data
            - `status_code` is http status code of response (RESTful one)
            - `response_code` is unique response code
        
        :Example:
        
        >>> def printer (*args, **kwargs):
                pprint(args)
        ...
        >>> requester.strongholds.get_state(printer, 123)
        (
            {'clan_id': 234, 'defence_hour': 3}
            200,
            0
        )
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param clan_id: clan identifier which stronghold istate is requested
        :param fields: field set to obtain (optional param)
        :type callback: function
        :type clan_id: integer
        :type fields: list of strings
        """
        return self._data_source.get_strongholds_state(callback, clan_id, fields=fields)


class Requester(object):
    """
    request all clan related information using data accessor provided
    
    :Example:
    
    >>> requester=Requester(DataAccessor())
    >>> requester.strongholds.get_info(str, 12312)
    >>> requester.clans.get_clans_info(str, [12312, 344])
    
    """
    available_data_sources = {'stagings': StagingDataAccessor,
     'fake': FakeDataAccessor,
     'gateway': GatewayDataAccessor}
    global_map = RequestDescriptor(GmAccessor)
    ratings = RequestDescriptor(RatingAccessor)
    strongholds = RequestDescriptor(StrongholdsAccessor)
    clans = RequestDescriptor(ClansAccessor)
    exporter = RequestDescriptor(ExporterAccessor)
    spa = RequestDescriptor(SpaAccessor)

    @classmethod
    def create_requester(cls, url_fetcher, config, client_lang=None):
        """
        create requester from config string.
        config string should have following form
        {"type": <data source type>, "accessor_config": <config data for accessor>}
        
        data source types can be follows:
        - fake
        - stagings
        - gateway
        
        it is not needed to pass accessor config for fake data source
        
        for gateway data source wgcg host is expected as accessor config
        
        for staging data source dict of staging hosts are needed
        
        :Example:
        
        >>> fake_requester = Requester.create_requester(None, "{'type': 'fake'}")
        >>> gateway_requester = Requester.create_requester(
        ...     None, '{"type": "gateway", "accessor_config": "http://wgcg.iv"}'
        ... )
        >>> staging_requester = Requester.create_requester(
        ...     None, '{"type": "stagings", "accessor_config": {"clans": "http://wgccbe.iv"}}'
        ... )
        
        
        """
        assert config.type in cls.available_data_sources, '%s data source is unknown' % config.type
        data_accessor = cls.available_data_sources[config.type](url_fetcher, config.url, client_lang=client_lang)
        return cls(data_accessor)

    def __init__(self, data_source):
        self.data_source = data_source

    @bigworld_wrapped
    def login(self, callback, account_id, token):
        """
        login into clan data gateway
        
        :param callback: callback function which will be called when data
                        would be obtained
        :param account_id: account identifier to login
        :param token: SPA1 token
        :type callback: function
        :type account_id: integer
        :type token: string
        """
        self.data_source.login(callback, account_id, token)

    @bigworld_wrapped
    def logout(self, callback):
        self.data_source.logout(callback)

    @bigworld_wrapped
    def get_alive_status(self, callback):
        self.data_source.get_alive_status(callback)
