# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/client_request_lib/exceptions.py


class ResponseCodes(object):
    NO_ERRORS = 0
    UNKNOWN_ERROR = 1
    AUTHENTIFICATION_ERROR = 2
    PERMISSION_DENIED = 3
    BAD_REQUEST = 4
    EXPORTER_ERROR = 5
    GLOBAL_MAP_ERROR = 7
    WGRS_ERROR = 8
    WGCCFE_ERROR = 9
    CLAN_IS_DISBANDED = 10
    STRONGHOLD_NOT_FOUND = 11
    WGCCBE_ERROR = 12
    ACCOUNT_BANNED = 13
    SPA_ERROR = 14
    UNKNOWN_ACCOUNT = 15
    CLAN_DOES_NOT_EXIST = 16
    CLAN_ALREADY_DISBANDED = 17
    CLAN_IS_FULL = 18
    ACCOUNT_ALREADY_IN_CLAN = 19
    RECRUITING_POLICY_MISMATCH = 21
    ACCOUNT_DOES_NOT_MEET_REQUIREMENTS = 22
    TOO_MANY_INVITES = 23
    INVITE_DOES_NOT_EXIST = 24
    INVITE_IS_NOT_ACTIVE = 25
    TOO_MANY_APPLICATIONS = 26
    APPLICATION_DOES_NOT_EXIST = 27
    APPLICATION_IS_NOT_ACTIVE = 28
    ACCOUNT_NOT_IN_CLAN = 29
    CLAN_IS_NOT_ACTIVE = 30
    RATINGS_NOT_FOUND = 31
    WGCG_ERROR = 32
    EXPORTER_DISABLED = 33
    GLOBAL_MAP_DISABLED = 34
    WGRS_DISABLED = 35
    WGCCFE_DISABLED = 36
    SPA_DISABLED = 37
    WGCCBE_DISABLED = 38
    ACCOUNT_IN_TRANSACTION = 39
    CLAN_IN_TRANSACTION = 40
    ACCOUNT_ALREADY_INVITED = 41
    ACCOUNT_ALREADY_APPLIED = 42
    ACCOUNT_IN_COOLDOWN = 43


class BaseRequestError(Exception):

    def __init__(self, *args, **kwargs):
        if 'extra_data' in kwargs:
            self.extra_data = kwargs['extra_data']


class AuthentificationError(BaseRequestError):
    status_code = 401
    response_code = ResponseCodes.AUTHENTIFICATION_ERROR
    description = 'User is not authentificated'


class PermissionDenied(BaseRequestError):
    status_code = 403
    response_code = ResponseCodes.PERMISSION_DENIED
    description = 'Forbidden'


class BadRequest(BaseRequestError):
    status_code = 400
    description = 'Bad request'
    response_code = ResponseCodes.BAD_REQUEST


class ExporterError(BaseRequestError):
    status_code = 500
    description = 'Exporter error was occurred'
    response_code = ResponseCodes.EXPORTER_ERROR


class SpaError(BaseRequestError):
    status_code = 500
    description = 'SPA error was occurred'
    response_code = ResponseCodes.SPA_ERROR


class GlobalMapError(BaseRequestError):
    status_code = 500
    description = 'Global map error was occurred'
    response_code = ResponseCodes.GLOBAL_MAP_ERROR


class WgrsError(BaseRequestError):
    status_code = 500
    description = 'Wgrs error was occurred'
    response_code = ResponseCodes.WGRS_ERROR


class WgccfeError(BaseRequestError):
    description = 'WGCCFE error was occurred'
    status_code = 500
    response_code = ResponseCodes.WGCCFE_ERROR


class ClanDisbandedError(BaseRequestError):
    description = 'Clan is disbanded'
    status_code = 409
    response_code = ResponseCodes.CLAN_IS_DISBANDED


class StrongholdNotFoundError(BaseRequestError):
    description = 'Stronghold is not found'
    status_code = 409
    response_code = ResponseCodes.STRONGHOLD_NOT_FOUND


class WgccbeError(BaseRequestError):
    description = 'WGCCBE error was occurred'
    status_code = 500
    response_code = ResponseCodes.WGCCBE_ERROR


class AccountBannedError(BaseRequestError):
    description = 'Account is banned'
    status_code = 403
    response_code = ResponseCodes.ACCOUNT_BANNED


class UnknownAccountError(BaseRequestError):
    description = 'Account in unknown'
    status_code = 404
    response_code = ResponseCodes.UNKNOWN_ACCOUNT


class RatingsNotFoundError(BaseRequestError):
    description = 'Ratings not found error'
    status_code = 404
    response_code = ResponseCodes.RATINGS_NOT_FOUND


class ClanDoesNotExistError(BaseRequestError):
    description = 'Clan does not exist'
    status_code = 404
    response_code = ResponseCodes.CLAN_DOES_NOT_EXIST


class ClanIsFullError(BaseRequestError):
    description = 'Clan has not free space'
    status_code = 409
    response_code = ResponseCodes.CLAN_IS_FULL


class AccountInClanError(BaseRequestError):
    description = 'Account is in clan already'
    status_code = 409
    response_code = ResponseCodes.ACCOUNT_ALREADY_IN_CLAN


class AccountNotInClanError(BaseRequestError):
    description = 'Account is not in clan'
    status_code = 409
    response_code = ResponseCodes.ACCOUNT_NOT_IN_CLAN


class RecruitingPolicyError(BaseRequestError):
    description = 'Recruiting policy mismatch'
    status_code = 409
    response_code = ResponseCodes.RECRUITING_POLICY_MISMATCH


class AccountRequirementsError(BaseRequestError):
    description = 'Account does not meet requirements'
    status_code = 409
    response_code = ResponseCodes.ACCOUNT_DOES_NOT_MEET_REQUIREMENTS


class TooManyInvitesError(BaseRequestError):
    description = 'Too many invites'
    status_code = 409
    response_code = ResponseCodes.TOO_MANY_INVITES


class InviteDoesNotExistError(BaseRequestError):
    description = 'Invite does not exist'
    status_code = 404
    response_code = ResponseCodes.INVITE_DOES_NOT_EXIST


class InviteIsNotActiveError(BaseRequestError):
    description = 'Invite is not active'
    status_code = 409
    response_code = ResponseCodes.INVITE_IS_NOT_ACTIVE


class TooManyApplicationsError(BaseRequestError):
    description = 'Too Many Applications'
    status_code = 409
    response_code = ResponseCodes.TOO_MANY_APPLICATIONS


class ApplicationDoesNotExistError(BaseRequestError):
    description = 'Application does not exist'
    status_code = 404
    response_code = ResponseCodes.APPLICATION_DOES_NOT_EXIST


class ApplicationIsNotActiveError(BaseRequestError):
    description = 'Application is not active'
    status_code = 409
    response_code = ResponseCodes.APPLICATION_IS_NOT_ACTIVE


class ClanIsNotActiveError(BaseRequestError):
    description = 'Clan is not active'
    status_code = 409
    response_code = ResponseCodes.CLAN_IS_NOT_ACTIVE


class WgcgError(BaseRequestError):
    description = 'WGCG error is occurred'
    status_code = 500
    response_code = ResponseCodes.WGCG_ERROR


class ExporterDisabled(BaseRequestError):
    description = 'Exporter proxying is disabled'
    status_code = 503
    response_code = ResponseCodes.EXPORTER_DISABLED


class GlobalMapDisabled(BaseRequestError):
    description = 'Global map proxying is disabled'
    status_code = 503
    response_code = ResponseCodes.GLOBAL_MAP_DISABLED


class WgrsDisabled(BaseRequestError):
    description = 'WGRS proxying is disabled'
    status_code = 503
    response_code = ResponseCodes.WGRS_DISABLED


class WgccfeDisabled(BaseRequestError):
    description = 'WGCCFE proxying is disabled'
    status_code = 503
    response_code = ResponseCodes.WGCCFE_DISABLED


class SpaDisabled(BaseRequestError):
    description = 'SPA proxying is disabled'
    status_code = 503
    response_code = ResponseCodes.SPA_DISABLED


class WgccbeDisabled(BaseRequestError):
    description = 'WGCCBE proxying is disabled'
    status_code = 503
    response_code = ResponseCodes.WGCCBE_DISABLED


class AccountInTransaction(BaseRequestError):
    description = 'Account in transaction'
    status_code = 409
    response_code = ResponseCodes.ACCOUNT_IN_TRANSACTION


class ClanInTransaction(BaseRequestError):
    description = 'Clan in transaction'
    status_code = 409
    response_code = ResponseCodes.CLAN_IN_TRANSACTION


class AccountAlreadyInvited(BaseRequestError):
    description = 'Account already invited'
    status_code = 409
    response_code = ResponseCodes.ACCOUNT_ALREADY_INVITED


class AccountAlreadyApplied(BaseRequestError):
    description = 'Account already applied'
    status_code = 409
    response_code = ResponseCodes.ACCOUNT_ALREADY_APPLIED


class AccountInCooldown(BaseRequestError):
    description = 'Account in cooldown'
    status_code = 409
    response_code = ResponseCodes.ACCOUNT_IN_COOLDOWN
