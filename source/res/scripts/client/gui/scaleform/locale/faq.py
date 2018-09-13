# Embedded file name: scripts/client/gui/Scaleform/locale/FAQ.py
from debug_utils import LOG_WARNING

class FAQ(object):
    QUESTION_1 = '#faq:question_1'
    ANSWER_1 = '#faq:answer_1'
    QUESTION_2 = '#faq:question_2'
    ANSWER_2 = '#faq:answer_2'
    QUESTION_3 = '#faq:question_3'
    ANSWER_3 = '#faq:answer_3'
    QUESTION_4 = '#faq:question_4'
    ANSWER_4 = '#faq:answer_4'
    QUESTION_5 = '#faq:question_5'
    ANSWER_5 = '#faq:answer_5'
    QUESTION_6 = '#faq:question_6'
    ANSWER_6 = '#faq:answer_6'
    QUESTION_7 = '#faq:question_7'
    ANSWER_7 = '#faq:answer_7'
    QUESTION_8 = '#faq:question_8'
    ANSWER_8 = '#faq:answer_8'
    QUESTION_9 = '#faq:question_9'
    ANSWER_9 = '#faq:answer_9'
    QUESTION_10 = '#faq:question_10'
    ANSWER_10 = '#faq:answer_10'
    QUESTION_11 = '#faq:question_11'
    ANSWER_11 = '#faq:answer_11'
    QUESTION_12 = '#faq:question_12'
    ANSWER_12 = '#faq:answer_12'
    QUESTION_13 = '#faq:question_13'
    ANSWER_13 = '#faq:answer_13'
    QUESTION_14 = '#faq:question_14'
    ANSWER_14 = '#faq:answer_14'
    QUESTION_15 = '#faq:question_15'
    ANSWER_15 = '#faq:answer_15'
    QUESTION_16 = '#faq:question_16'
    ANSWER_16 = '#faq:answer_16'
    QUESTION_17 = '#faq:question_17'
    ANSWER_17_CONTAINS_LINKS = '#faq:answer_17/contains_links'
    QUESTION_ENUM = (QUESTION_1,
     QUESTION_2,
     QUESTION_3,
     QUESTION_4,
     QUESTION_5,
     QUESTION_6,
     QUESTION_7,
     QUESTION_8,
     QUESTION_9,
     QUESTION_10,
     QUESTION_11,
     QUESTION_12,
     QUESTION_13,
     QUESTION_14,
     QUESTION_15,
     QUESTION_16,
     QUESTION_17)
    ANSWER_ENUM = (ANSWER_1,
     ANSWER_2,
     ANSWER_3,
     ANSWER_4,
     ANSWER_5,
     ANSWER_6,
     ANSWER_7,
     ANSWER_8,
     ANSWER_9,
     ANSWER_10,
     ANSWER_11,
     ANSWER_12,
     ANSWER_13,
     ANSWER_14,
     ANSWER_15,
     ANSWER_16,
     ANSWER_17_CONTAINS_LINKS)

    @staticmethod
    def question(key):
        outcome = '#faq:question_%s' % key
        if outcome not in FAQ.QUESTION_ENUM:
            LOG_WARNING('locale key "' + outcome + '" was not found')
            return None
        else:
            return outcome

    @staticmethod
    def answer(key):
        outcome = '#faq:answer_%s' % key
        if outcome not in FAQ.ANSWER_ENUM:
            LOG_WARNING('locale key "' + outcome + '" was not found')
            return None
        else:
            return outcome
