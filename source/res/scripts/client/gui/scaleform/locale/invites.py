# Embedded file name: scripts/client/gui/Scaleform/locale/INVITES.py
from debug_utils import LOG_WARNING

class INVITES(object):
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
    INVITES_PREBATTLE_ALREADYJOINED_COMPANY = '#invites:invites/prebattle/alreadyJoined/COMPANY'
    INVITES_PREBATTLE_ALREADYJOINED_TRAINING = '#invites:invites/prebattle/alreadyJoined/TRAINING'
    INVITES_PREBATTLE_ALREADYJOINED_CLAN = '#invites:invites/prebattle/alreadyJoined/CLAN'
    INVITES_PREBATTLE_ALREADYJOINED_TOURNAMENT = '#invites:invites/prebattle/alreadyJoined/TOURNAMENT'
    INVITES_PREBATTLE_ALREADYJOINED_UNIT = '#invites:invites/prebattle/alreadyJoined/UNIT'
    INVITES_PREBATTLE_ALREADYJOINED_SORTIE = '#invites:invites/prebattle/alreadyJoined/SORTIE'
    INVITES_TEXT_CREATORNAME = '#invites:invites/text/creatorName'
    INVITES_TEXT_SQUAD = '#invites:invites/text/SQUAD'
    INVITES_TEXT_COMPANY = '#invites:invites/text/COMPANY'
    INVITES_TEXT_TRAINING = '#invites:invites/text/TRAINING'
    INVITES_TEXT_UNIT = '#invites:invites/text/UNIT'
    INVITES_TEXT_SORTIE = '#invites:invites/text/SORTIE'
    INVITES_TEXT_FORT_BATTLE = '#invites:invites/text/FORT_BATTLE'
    INVITES_TEXT_CLUBS = '#invites:invites/text/CLUBS'
    INVITES_TEXT_FORT_OFFENCE = '#invites:invites/text/fort/offence'
    INVITES_TEXT_FORT_DEFENCE = '#invites:invites/text/fort/defence'
    INVITES_TEXT_FORT_DIRECTION = '#invites:invites/text/fort/direction'
    INVITES_TEXT_CLUB = '#invites:invites/text/club'
    INVITES_COMMENT_CLUB = '#invites:invites/comment/club'
    INVITES_COMMENT_CLUB_DETAILS = '#invites:invites/comment/club/details'
    CLUB_APPLICATIONS_TITLE = '#invites:club/applications/title'
    CLUB_APPLICATIONS_COMMENT = '#invites:club/applications/comment'
    CLUB_APPLICATIONS_BUTTONS_DETAILS = '#invites:club/applications/buttons/details'
    INVITES_COMMENT = '#invites:invites/comment'
    INVITES_STATE_PENDING = '#invites:invites/state/PENDING'
    INVITES_STATE_ACCEPTED = '#invites:invites/state/ACCEPTED'
    INVITES_STATE_DECLINED = '#invites:invites/state/DECLINED'
    INVITES_STATE_REVOKED = '#invites:invites/state/REVOKED'
    INVITES_STATE_EXPIRED = '#invites:invites/state/EXPIRED'
    INVITES_STATE_ERROR = '#invites:invites/state/ERROR'
    INVITES_NOTE_SERVER_CHANGE = '#invites:invites/note/server_change'
    INVITES_NOTE_LEAVE_COMPANY = '#invites:invites/note/leave/COMPANY'
    INVITES_NOTE_CHANGE_AND_LEAVE_COMPANY = '#invites:invites/note/change_and_leave/COMPANY'
    INVITES_NOTE_LEAVE_SQUAD = '#invites:invites/note/leave/SQUAD'
    INVITES_NOTE_CHANGE_AND_LEAVE_SQUAD = '#invites:invites/note/change_and_leave/SQUAD'
    INVITES_NOTE_LEAVE_TRAINING = '#invites:invites/note/leave/TRAINING'
    INVITES_NOTE_CHANGE_AND_LEAVE_TRAINING = '#invites:invites/note/change_and_leave/TRAINING'
    INVITES_NOTE_LEAVE_UNIT = '#invites:invites/note/leave/UNIT'
    INVITES_NOTE_CHANGE_AND_LEAVE_UNIT = '#invites:invites/note/change_and_leave/UNIT'
    INVITES_NOTE_LEAVE_CLAN = '#invites:invites/note/leave/CLAN'
    INVITES_NOTE_CHANGE_AND_LEAVE_CLAN = '#invites:invites/note/change_and_leave/CLAN'
    INVITES_NOTE_LEAVE_TOURNAMENT = '#invites:invites/note/leave/TOURNAMENT'
    INVITES_NOTE_CHANGE_AND_LEAVE_TOURNAMENT = '#invites:invites/note/change_and_leave/TOURNAMENT'
    INVITES_NOTE_LEAVE_HISTORICAL = '#invites:invites/note/leave/HISTORICAL'
    INVITES_NOTE_CHANGE_AND_LEAVE_HISTORICAL = '#invites:invites/note/change_and_leave/HISTORICAL'
    INVITES_NOTE_LEAVE_SORTIE = '#invites:invites/note/leave/SORTIE'
    INVITES_NOTE_CHANGE_AND_LEAVE_SORTIE = '#invites:invites/note/change_and_leave/SORTIE'
    INVITES_NOTE_LEAVE_FORT_BATTLE = '#invites:invites/note/leave/FORT_BATTLE'
    INVITES_NOTE_CHANGE_AND_LEAVE_FORT_BATTLE = '#invites:invites/note/change_and_leave/FORT_BATTLE'
    INVITES_NOTE_LEAVE_CLUBS = '#invites:invites/note/leave/CLUBS'
    INVITES_NOTE_CHANGE_AND_LEAVE_CLUBS = '#invites:invites/note/change_and_leave/CLUBS'
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
    CLUBS_STATE_ACTIVE = '#invites:clubs/state/ACTIVE'
    CLUBS_STATE_ACCEPTED = '#invites:clubs/state/ACCEPTED'
    CLUBS_STATE_DECLINED = '#invites:clubs/state/DECLINED'
    CLUBS_STATE_CANCELLED = '#invites:clubs/state/CANCELLED'
    INVITES_STATE_ENUM = (INVITES_STATE_PENDING,
     INVITES_STATE_ACCEPTED,
     INVITES_STATE_DECLINED,
     INVITES_STATE_REVOKED,
     INVITES_STATE_EXPIRED,
     INVITES_STATE_ERROR)
    INVITES_PREBATTLE_ALREADYJOINED_ENUM = (INVITES_PREBATTLE_ALREADYJOINED_SQUAD,
     INVITES_PREBATTLE_ALREADYJOINED_COMPANY,
     INVITES_PREBATTLE_ALREADYJOINED_TRAINING,
     INVITES_PREBATTLE_ALREADYJOINED_CLAN,
     INVITES_PREBATTLE_ALREADYJOINED_TOURNAMENT,
     INVITES_PREBATTLE_ALREADYJOINED_UNIT,
     INVITES_PREBATTLE_ALREADYJOINED_SORTIE)
    INVITES_PREBATTLE_ACCEPTNOTALLOWED_ENUM = (INVITES_PREBATTLE_ACCEPTNOTALLOWED_UNDEFINEDPERIPHERY, INVITES_PREBATTLE_ACCEPTNOTALLOWED_OTHERPERIPHERY)
    INVITES_TEXT_ENUM = (INVITES_TEXT_CREATORNAME,
     INVITES_TEXT_SQUAD,
     INVITES_TEXT_COMPANY,
     INVITES_TEXT_TRAINING,
     INVITES_TEXT_UNIT,
     INVITES_TEXT_SORTIE,
     INVITES_TEXT_FORT_BATTLE,
     INVITES_TEXT_CLUBS,
     INVITES_TEXT_FORT_OFFENCE,
     INVITES_TEXT_FORT_DEFENCE,
     INVITES_TEXT_FORT_DIRECTION,
     INVITES_TEXT_CLUB)
    INVITES_NOTE_CHANGE_AND_LEAVE_ENUM = (INVITES_NOTE_CHANGE_AND_LEAVE_COMPANY,
     INVITES_NOTE_CHANGE_AND_LEAVE_SQUAD,
     INVITES_NOTE_CHANGE_AND_LEAVE_TRAINING,
     INVITES_NOTE_CHANGE_AND_LEAVE_UNIT,
     INVITES_NOTE_CHANGE_AND_LEAVE_CLAN,
     INVITES_NOTE_CHANGE_AND_LEAVE_TOURNAMENT,
     INVITES_NOTE_CHANGE_AND_LEAVE_HISTORICAL,
     INVITES_NOTE_CHANGE_AND_LEAVE_SORTIE,
     INVITES_NOTE_CHANGE_AND_LEAVE_FORT_BATTLE,
     INVITES_NOTE_CHANGE_AND_LEAVE_CLUBS)
    INVITES_NOTE_LEAVE_ENUM = (INVITES_NOTE_LEAVE_COMPANY,
     INVITES_NOTE_LEAVE_SQUAD,
     INVITES_NOTE_LEAVE_TRAINING,
     INVITES_NOTE_LEAVE_UNIT,
     INVITES_NOTE_LEAVE_CLAN,
     INVITES_NOTE_LEAVE_TOURNAMENT,
     INVITES_NOTE_LEAVE_HISTORICAL,
     INVITES_NOTE_LEAVE_SORTIE,
     INVITES_NOTE_LEAVE_FORT_BATTLE,
     INVITES_NOTE_LEAVE_CLUBS)

    @staticmethod
    def invites_state(key):
        outcome = '#invites:invites/state/%s' % key
        if outcome not in INVITES.INVITES_STATE_ENUM:
            LOG_WARNING('locale key "' + outcome + '" was not found')
            return None
        else:
            return outcome

    @staticmethod
    def invites_prebattle_alreadyjoined(key):
        outcome = '#invites:invites/prebattle/alreadyJoined/%s' % key
        if outcome not in INVITES.INVITES_PREBATTLE_ALREADYJOINED_ENUM:
            LOG_WARNING('locale key "' + outcome + '" was not found')
            return None
        else:
            return outcome

    @staticmethod
    def invites_prebattle_acceptnotallowed(key):
        outcome = '#invites:invites/prebattle/acceptNotAllowed/%s' % key
        if outcome not in INVITES.INVITES_PREBATTLE_ACCEPTNOTALLOWED_ENUM:
            LOG_WARNING('locale key "' + outcome + '" was not found')
            return None
        else:
            return outcome

    @staticmethod
    def invites_text(key):
        outcome = '#invites:invites/text/%s' % key
        if outcome not in INVITES.INVITES_TEXT_ENUM:
            LOG_WARNING('locale key "' + outcome + '" was not found')
            return None
        else:
            return outcome

    @staticmethod
    def invites_note_change_and_leave(key):
        outcome = '#invites:invites/note/change_and_leave/%s' % key
        if outcome not in INVITES.INVITES_NOTE_CHANGE_AND_LEAVE_ENUM:
            LOG_WARNING('locale key "' + outcome + '" was not found')
            return None
        else:
            return outcome

    @staticmethod
    def invites_note_leave(key):
        outcome = '#invites:invites/note/leave/%s' % key
        if outcome not in INVITES.INVITES_NOTE_LEAVE_ENUM:
            LOG_WARNING('locale key "' + outcome + '" was not found')
            return None
        else:
            return outcome
