# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/common/comp7_light_common/__init__.py
import constants
import comp7_light_constants
from constants_utils import addArenaGuiTypesFromExtension, addPrebattleTypesFromExtension, addRosterTypes, addInvitationTypes, addClientUnitCmd

def injectConsts(personality):
    addArenaGuiTypesFromExtension(comp7_light_constants.ARENA_GUI_TYPE, personality)
    addPrebattleTypesFromExtension(comp7_light_constants.PREBATTLE_TYPE, personality)
    constants.INBATTLE_CONFIGS.extend(comp7_light_constants.COMP7_LIGHT_INBATTLE_CONFIGS)


def injectSquadConsts(personality):
    comp7_light_constants.UNIT_MGR_FLAGS.inject(personality)
    addRosterTypes(comp7_light_constants.ROSTER_TYPE, personality)
    addInvitationTypes(comp7_light_constants.INVITATION_TYPE, personality)
    addClientUnitCmd(comp7_light_constants.CLIENT_UNIT_CMD, personality)
    constants.INVITATION_TYPE.TYPES_WITH_EXTRA_DATA += (comp7_light_constants.INVITATION_TYPE.COMP7_LIGHT,)
