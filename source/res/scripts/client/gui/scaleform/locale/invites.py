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
    INVITES_TEXT_FORT_OFFENCE = '#invites:invites/text/fort/offence'
    INVITES_TEXT_FORT_DEFENCE = '#invites:invites/text/fort/defence'
    INVITES_TEXT_FORT_DIRECTION = '#invites:invites/text/fort/direction'
    INVITES_COMMENT = '#invites:invites/comment'
    INVITES_STATE_ACTIVE = '#invites:invites/state/ACTIVE'
    INVITES_STATE_ACCEPTED = '#invites:invites/state/ACCEPTED'
    INVITES_STATE_DECLINED = '#invites:invites/state/DECLINED'
    INVITES_STATE_EXPIRED = '#invites:invites/state/EXPIRED'
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
    INVITES_STATE_ENUM = (INVITES_STATE_ACTIVE,
     INVITES_STATE_ACCEPTED,
     INVITES_STATE_DECLINED,
     INVITES_STATE_EXPIRED)
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
     INVITES_TEXT_FORT_OFFENCE,
     INVITES_TEXT_FORT_DEFENCE,
     INVITES_TEXT_FORT_DIRECTION)
    INVITES_NOTE_CHANGE_AND_LEAVE_ENUM = (INVITES_NOTE_CHANGE_AND_LEAVE_COMPANY,
     INVITES_NOTE_CHANGE_AND_LEAVE_SQUAD,
     INVITES_NOTE_CHANGE_AND_LEAVE_TRAINING,
     INVITES_NOTE_CHANGE_AND_LEAVE_UNIT,
     INVITES_NOTE_CHANGE_AND_LEAVE_CLAN,
     INVITES_NOTE_CHANGE_AND_LEAVE_TOURNAMENT,
     INVITES_NOTE_CHANGE_AND_LEAVE_HISTORICAL,
     INVITES_NOTE_CHANGE_AND_LEAVE_SORTIE,
     INVITES_NOTE_CHANGE_AND_LEAVE_FORT_BATTLE)
    INVITES_NOTE_LEAVE_ENUM = (INVITES_NOTE_LEAVE_COMPANY,
     INVITES_NOTE_LEAVE_SQUAD,
     INVITES_NOTE_LEAVE_TRAINING,
     INVITES_NOTE_LEAVE_UNIT,
     INVITES_NOTE_LEAVE_CLAN,
     INVITES_NOTE_LEAVE_TOURNAMENT,
     INVITES_NOTE_LEAVE_HISTORICAL,
     INVITES_NOTE_LEAVE_SORTIE,
     INVITES_NOTE_LEAVE_FORT_BATTLE)

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
