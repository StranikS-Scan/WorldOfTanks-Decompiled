# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/crew2_consts.py
from enum import Enum

class GENDER(Enum):
    MALE = 0
    FEMALE = 1


BOOL_TO_GENDER = {False: GENDER.MALE,
 True: GENDER.FEMALE}
TAG_TO_GENDER = {'MALE': GENDER.MALE,
 'FEMALE': GENDER.FEMALE}
GENDER_TO_TAG = {v:k for k, v in TAG_TO_GENDER.iteritems()}
GENDER_TO_OPPOSITE = {GENDER.MALE: GENDER.FEMALE,
 GENDER.FEMALE: GENDER.MALE}
XP_TRASH_LIMIT = 315090
