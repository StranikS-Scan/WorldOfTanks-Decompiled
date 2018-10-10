# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/locale/INVITES.py
from debug_utils import LOG_WARNING

class INVITES(object):
    INVITES_TEXT_EPIC = '#invites:invites/text/EPIC'
    ERRORS_UNKNOWNUSER = '#invites:errors/unknownuser'
    ERRORS_USEROFFLINE = '#invites:errors/useroffline'
    ERRORS_SELFINVITE = '#invites:errors/selfinvite'
    ERRORS_INVITENOTSUPPORTED = '#invites:errors/inviteNotSupported'
    ERRORS_CREATIONNOTALLOWED = '#invites:errors/creationNotAllowed'
    ERRORS_RECEIVERIGNORESENDER = '#invites:errors/receiverIgnoreSender'
    ERRORS_VEHICLEBROKENORLOCKED = '#invites:errors/vehicleBrokenOrLocked'
    ERRORS_INVALID = '#invites:errors/invalid'
    INVITES_PREBATTLE_ACCEPTNOTALLOWED_UNDEFINEDPERIPHERY = '#invites:invites/prebattle/acceptNotAllowed/undefinedPeriphery'
    INVITES_PREBATTLE_ACCEPTNOTALLOWED_OTHERPERIPHERY = '#invites:invites/prebattle/acceptNotAllowed/otherPeriphery'
    INVITES_PREBATTLE_ALREADYJOINED_SQUAD = '#invites:invites/prebattle/alreadyJoined/SQUAD'
    INVITES_PREBATTLE_ALREADYJOINED_FALLOUT = '#invites:invites/prebattle/alreadyJoined/FALLOUT'
    INVITES_PREBATTLE_ALREADYJOINED_TRAINING = '#invites:invites/prebattle/alreadyJoined/TRAINING'
    INVITES_PREBATTLE_ALREADYJOINED_CLAN = '#invites:invites/prebattle/alreadyJoined/CLAN'
    INVITES_PREBATTLE_ALREADYJOINED_TOURNAMENT = '#invites:invites/prebattle/alreadyJoined/TOURNAMENT'
    INVITES_PREBATTLE_ALREADYJOINED_UNIT = '#invites:invites/prebattle/alreadyJoined/UNIT'
    INVITES_PREBATTLE_ALREADYJOINED_SORTIE = '#invites:invites/prebattle/alreadyJoined/SORTIE'
    INVITES_TEXT_CREATORNAME = '#invites:invites/text/creatorName'
    INVITES_TEXT_SQUAD = '#invites:invites/text/SQUAD'
    INVITES_TEXT_EVENT = '#invites:invites/text/EVENT'
    INVITES_TEXT_FALLOUT = '#invites:invites/text/FALLOUT'
    INVITES_TEXT_FALLOUT_FALLOUT_CLASSIC = '#invites:invites/text/FALLOUT/FALLOUT_CLASSIC'
    INVITES_TEXT_FALLOUT_FALLOUT_MULTITEAM = '#invites:invites/text/FALLOUT/FALLOUT_MULTITEAM'
    INVITES_TEXT_TRAINING = '#invites:invites/text/TRAINING'
    INVITES_TEXT_UNIT = '#invites:invites/text/UNIT'
    INVITES_TEXT_SORTIE = '#invites:invites/text/SORTIE'
    INVITES_TEXT_FORT_BATTLE = '#invites:invites/text/FORT_BATTLE'
    INVITES_TEXT_EXTERNAL = '#invites:invites/text/EXTERNAL'
    INVITES_TEXT_FORT_OFFENCE = '#invites:invites/text/fort/offence'
    INVITES_TEXT_FORT_DEFENCE = '#invites:invites/text/fort/defence'
    INVITES_TEXT_FORT_DIRECTION = '#invites:invites/text/fort/direction'
    CLAN_APPLICATIONS_TITLE = '#invites:clan/applications/title'
    CLAN_APPLICATIONS_COMMENT = '#invites:clan/applications/comment'
    CLAN_APPLICATIONS_COMMENT_MINIMAP = '#invites:clan/applications/comment/minimap'
    CLAN_APPLICATIONS_BUTTONS_DETAILS = '#invites:clan/applications/buttons/details'
    CLAN_PERSONAL_INVITES_TITLE = '#invites:clan/personal/invites/title'
    CLAN_PERSONAL_INVITES_BUTTONS_DETAILS = '#invites:clan/personal/invites/buttons/details'
    CLAN_APPLICATION_TITLE = '#invites:clan/application/title'
    CLAN_APPLICATION_COMMENT = '#invites:clan/application/comment'
    CLAN_INVITE_TITLE = '#invites:clan/invite/title'
    CLAN_INVITE_COMMENT = '#invites:clan/invite/comment'
    INVITES_COMMENT = '#invites:invites/comment'
    INVITES_STATE_PENDING = '#invites:invites/state/PENDING'
    INVITES_STATE_ACCEPTED = '#invites:invites/state/ACCEPTED'
    INVITES_STATE_DECLINED = '#invites:invites/state/DECLINED'
    INVITES_STATE_REVOKED = '#invites:invites/state/REVOKED'
    INVITES_STATE_EXPIRED = '#invites:invites/state/EXPIRED'
    INVITES_STATE_ERROR = '#invites:invites/state/ERROR'
    INVITES_NOTE_SERVER_CHANGE = '#invites:invites/note/server_change'
    INVITES_NOTE_CHANGE_AND_LEAVE_EVENT = '#invites:invites/note/change_and_leave/EVENT'
    INVITES_NOTE_LEAVE_SQUAD = '#invites:invites/note/leave/SQUAD'
    INVITES_NOTE_LEAVE_FALLOUT = '#invites:invites/note/leave/FALLOUT'
    INVITES_NOTE_CHANGE_AND_LEAVE_SQUAD = '#invites:invites/note/change_and_leave/SQUAD'
    INVITES_NOTE_CHANGE_AND_LEAVE_FALLOUT = '#invites:invites/note/change_and_leave/FALLOUT'
    INVITES_NOTE_LEAVE_TRAINING = '#invites:invites/note/leave/TRAINING'
    INVITES_NOTE_CHANGE_AND_LEAVE_TRAINING = '#invites:invites/note/change_and_leave/TRAINING'
    INVITES_NOTE_LEAVE_UNIT = '#invites:invites/note/leave/UNIT'
    INVITES_NOTE_CHANGE_AND_LEAVE_UNIT = '#invites:invites/note/change_and_leave/UNIT'
    INVITES_NOTE_LEAVE_CLAN = '#invites:invites/note/leave/CLAN'
    INVITES_NOTE_CHANGE_AND_LEAVE_CLAN = '#invites:invites/note/change_and_leave/CLAN'
    INVITES_NOTE_LEAVE_TOURNAMENT = '#invites:invites/note/leave/TOURNAMENT'
    INVITES_NOTE_CHANGE_AND_LEAVE_TOURNAMENT = '#invites:invites/note/change_and_leave/TOURNAMENT'
    INVITES_NOTE_LEAVE_SORTIE = '#invites:invites/note/leave/SORTIE'
    INVITES_NOTE_CHANGE_AND_LEAVE_SORTIE = '#invites:invites/note/change_and_leave/SORTIE'
    INVITES_NOTE_LEAVE_FORT_COMMON = '#invites:invites/note/leave/FORT_COMMON'
    INVITES_NOTE_CHANGE_AND_LEAVE_FORT_COMMON = '#invites:invites/note/change_and_leave/FORT_COMMON'
    INVITES_NOTE_LEAVE_E_SPORT_COMMON = '#invites:invites/note/leave/E_SPORT_COMMON'
    INVITES_NOTE_CHANGE_AND_LEAVE_E_SPORT_COMMON = '#invites:invites/note/change_and_leave/E_SPORT_COMMON'
    INVITES_NOTE_LEAVE_FORT_BATTLE = '#invites:invites/note/leave/FORT_BATTLE'
    INVITES_NOTE_CHANGE_AND_LEAVE_FORT_BATTLE = '#invites:invites/note/change_and_leave/FORT_BATTLE'
    INVITES_NOTE_LEAVE_EXTERNAL = '#invites:invites/note/leave/EXTERNAL'
    INVITES_NOTE_CHANGE_AND_LEAVE_EXTERNAL = '#invites:invites/note/change_and_leave/EXTERNAL'
    INVITES_NOTE_LEAVE_RANDOMS = '#invites:invites/note/leave/RANDOMS'
    INVITES_NOTE_CHANGE_AND_LEAVE_RANDOMS = '#invites:invites/note/change_and_leave/RANDOMS'
    INVITES_NOTE_LEAVE_EVENT = '#invites:invites/note/leave/EVENT'
    INVITES_NOTE_CHANGE_AND_LEAVE_EVENT_BATTLES = '#invites:invites/note/change_and_leave/EVENT_BATTLES'
    INVITES_NOTE_LEAVE_SANDBOX = '#invites:invites/note/leave/SANDBOX'
    INVITES_NOTE_CHANGE_AND_LEAVE_SANDBOX = '#invites:invites/note/change_and_leave/SANDBOX'
    INVITES_NOTE_LEAVE_EPIC = '#invites:invites/note/leave/EPIC'
    INVITES_NOTE_CHANGE_AND_LEAVE_EPIC = '#invites:invites/note/change_and_leave/EPIC'
    INVITES_NOTE_LEAVE_EPIC_TRAINING = '#invites:invites/note/leave/EPIC_TRAINING'
    INVITES_NOTE_CHANGE_AND_LEAVE_EPIC_TRAINING = '#invites:invites/note/change_and_leave/EPIC_TRAINING'
    INVITES_NOTE_LEAVE_RANKED = '#invites:invites/note/leave/RANKED'
    INVITES_NOTE_CHANGE_AND_LEAVE_RANKED = '#invites:invites/note/change_and_leave/RANKED'
    GUI_TITLES_RECEIVEDINVITES = '#invites:gui/titles/receivedInvites'
    GUI_TITLES_INVITE = '#invites:gui/titles/invite'
    GUI_TITLES_BARTER = '#invites:gui/titles/barter'
    GUI_TITLES_CLAN = '#invites:gui/titles/clan'
    GUI_LABELS_RECEIVER = '#invites:gui/labels/receiver'
    GUI_LABELS_INVITETEXT = '#invites:gui/labels/inviteText'
    GUI_LABELS_ADDITIONALTEXT = '#invites:gui/labels/additionalText'
    GUI_BUTTONS_SEND = '#invites:gui/buttons/send'
    GUI_BUTTONS_ACCEPT = '#invites:gui/buttons/accept'
    GUI_BUTTONS_REJECT = '#invites:gui/buttons/reject'
    GUI_BUTTONS_CANCEL = '#invites:gui/buttons/cancel'
    FRIENDSHIP_REQUEST_TEXT = '#invites:friendship/request/text'
    FRIENDSHIP_NOTE_APPROVED = '#invites:friendship/note/approved'
    FRIENDSHIP_NOTE_CANCELED = '#invites:friendship/note/canceled'
    FRIENDSHIP_NOTE_PROCESS = '#invites:friendship/note/process'
    FRIENDSHIP_NOTE_MAXROSTER = '#invites:friendship/note/maxRoster'
    FRIENDSHIP_NOTE_NOTCONNECTED = '#invites:friendship/note/notConnected'
    CLANS_STATE_APP_ACTIVE = '#invites:clans/state/app/active'
    CLANS_STATE_APP_ACCEPTED = '#invites:clans/state/app/accepted'
    CLANS_STATE_APP_DECLINED = '#invites:clans/state/app/declined'
    CLANS_STATE_APP_ERROR_INCLANENTERCOOLDOWN = '#invites:clans/state/app/error/inClanEnterCooldown'
    CLANS_STATE_INVITE_ACTIVE = '#invites:clans/state/invite/active'
    CLANS_STATE_INVITE_ACCEPTED = '#invites:clans/state/invite/accepted'
    CLANS_STATE_INVITE_DECLINED = '#invites:clans/state/invite/declined'
    CLANS_STATE_INVITE_ERROR_INCLANENTERCOOLDOWN = '#invites:clans/state/invite/error/inClanEnterCooldown'
    STRONGHOLD_INVITE_SENDINVITETOUSERNAME = '#invites:stronghold/invite/sendInviteToUsername'
    INVITES_NOTE_LEAVE_ENUM = (INVITES_NOTE_LEAVE_SQUAD,
     INVITES_NOTE_LEAVE_FALLOUT,
     INVITES_NOTE_LEAVE_TRAINING,
     INVITES_NOTE_LEAVE_UNIT,
     INVITES_NOTE_LEAVE_CLAN,
     INVITES_NOTE_LEAVE_TOURNAMENT,
     INVITES_NOTE_LEAVE_SORTIE,
     INVITES_NOTE_LEAVE_FORT_COMMON,
     INVITES_NOTE_LEAVE_E_SPORT_COMMON,
     INVITES_NOTE_LEAVE_FORT_BATTLE,
     INVITES_NOTE_LEAVE_EXTERNAL,
     INVITES_NOTE_LEAVE_RANDOMS,
     INVITES_NOTE_LEAVE_EVENT,
     INVITES_NOTE_LEAVE_SANDBOX,
     INVITES_NOTE_LEAVE_EPIC,
     INVITES_NOTE_LEAVE_EPIC_TRAINING,
     INVITES_NOTE_LEAVE_RANKED)
    INVITES_PREBATTLE_ACCEPTNOTALLOWED_ENUM = (INVITES_PREBATTLE_ACCEPTNOTALLOWED_UNDEFINEDPERIPHERY, INVITES_PREBATTLE_ACCEPTNOTALLOWED_OTHERPERIPHERY)
    INVITES_STATE_ENUM = (INVITES_STATE_PENDING,
     INVITES_STATE_ACCEPTED,
     INVITES_STATE_DECLINED,
     INVITES_STATE_REVOKED,
     INVITES_STATE_EXPIRED,
     INVITES_STATE_ERROR)
    INVITES_NOTE_CHANGE_AND_LEAVE_ENUM = (INVITES_NOTE_CHANGE_AND_LEAVE_EVENT,
     INVITES_NOTE_CHANGE_AND_LEAVE_SQUAD,
     INVITES_NOTE_CHANGE_AND_LEAVE_FALLOUT,
     INVITES_NOTE_CHANGE_AND_LEAVE_TRAINING,
     INVITES_NOTE_CHANGE_AND_LEAVE_UNIT,
     INVITES_NOTE_CHANGE_AND_LEAVE_CLAN,
     INVITES_NOTE_CHANGE_AND_LEAVE_TOURNAMENT,
     INVITES_NOTE_CHANGE_AND_LEAVE_SORTIE,
     INVITES_NOTE_CHANGE_AND_LEAVE_FORT_COMMON,
     INVITES_NOTE_CHANGE_AND_LEAVE_E_SPORT_COMMON,
     INVITES_NOTE_CHANGE_AND_LEAVE_FORT_BATTLE,
     INVITES_NOTE_CHANGE_AND_LEAVE_EXTERNAL,
     INVITES_NOTE_CHANGE_AND_LEAVE_RANDOMS,
     INVITES_NOTE_CHANGE_AND_LEAVE_EVENT_BATTLES,
     INVITES_NOTE_CHANGE_AND_LEAVE_SANDBOX,
     INVITES_NOTE_CHANGE_AND_LEAVE_EPIC,
     INVITES_NOTE_CHANGE_AND_LEAVE_EPIC_TRAINING,
     INVITES_NOTE_CHANGE_AND_LEAVE_RANKED)
    INVITES_PREBATTLE_ALREADYJOINED_ENUM = (INVITES_PREBATTLE_ALREADYJOINED_SQUAD,
     INVITES_PREBATTLE_ALREADYJOINED_FALLOUT,
     INVITES_PREBATTLE_ALREADYJOINED_TRAINING,
     INVITES_PREBATTLE_ALREADYJOINED_CLAN,
     INVITES_PREBATTLE_ALREADYJOINED_TOURNAMENT,
     INVITES_PREBATTLE_ALREADYJOINED_UNIT,
     INVITES_PREBATTLE_ALREADYJOINED_SORTIE)

    @classmethod
    def invites_state(cls, key0):
        outcome = '#invites:invites/state/{}'.format(key0)
        if outcome not in cls.INVITES_STATE_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def invites_note_leave(cls, key0):
        outcome = '#invites:invites/note/leave/{}'.format(key0)
        if outcome not in cls.INVITES_NOTE_LEAVE_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def invites_note_change_and_leave(cls, key0):
        outcome = '#invites:invites/note/change_and_leave/{}'.format(key0)
        if outcome not in cls.INVITES_NOTE_CHANGE_AND_LEAVE_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def invites_prebattle_acceptnotallowed(cls, key0):
        outcome = '#invites:invites/prebattle/acceptNotAllowed/{}'.format(key0)
        if outcome not in cls.INVITES_PREBATTLE_ACCEPTNOTALLOWED_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def invites_prebattle_alreadyjoined(cls, key0):
        outcome = '#invites:invites/prebattle/alreadyJoined/{}'.format(key0)
        if outcome not in cls.INVITES_PREBATTLE_ALREADYJOINED_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome
