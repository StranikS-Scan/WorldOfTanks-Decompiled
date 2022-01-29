# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/lunar_ny_constants.py
from enum import IntEnum
from gui.Scaleform.genConsts.NOTIFICATIONS_CONSTANTS import NOTIFICATIONS_CONSTANTS
from gui.shared.gui_items.loot_box import LunarNYLootBoxTypes
from gui.impl.gen.view_models.views.lobby.lunar_ny.charm_model import CharmType

class EnvelopeTypes(IntEnum):
    PREMIUM_PAID = 0
    PAID = 1
    FREE = 2


ALL_ENVELOPE_TYPES = (EnvelopeTypes.PREMIUM_PAID, EnvelopeTypes.PAID, EnvelopeTypes.FREE)
CHARM_TYPE_BY_TYPE_NAME = {'rare': CharmType.RARE,
 'common': CharmType.COMMON}
ENVELOPE_NAME_BY_TYPE = {EnvelopeTypes.PREMIUM_PAID: 'premiumPaid',
 EnvelopeTypes.PAID: 'paid',
 EnvelopeTypes.FREE: 'free'}
ENVELOPE_TYPE_TO_NOTIFICATIONS_CONSTANTS = {EnvelopeTypes.PREMIUM_PAID: NOTIFICATIONS_CONSTANTS.PREMIUM_PAID,
 EnvelopeTypes.PAID: NOTIFICATIONS_CONSTANTS.PAID,
 EnvelopeTypes.FREE: NOTIFICATIONS_CONSTANTS.FREE}
ENVELOPE_ENTITLEMENT_CODE_TO_TYPE = {'giftsystem_3_simpleEnvelope': EnvelopeTypes.PAID,
 'giftsystem_3_specialEnvelope': EnvelopeTypes.PREMIUM_PAID,
 'giftsystem_3_baseEnvelope': EnvelopeTypes.FREE}
ENVELOPE_IN_SECRET_SANTA_ENTITLEMENTS = {EnvelopeTypes.PAID: 'giftsystem_3_participationRightSimpleEnvelope',
 EnvelopeTypes.PREMIUM_PAID: 'giftsystem_3_participationRightSpecialEnvelope',
 EnvelopeTypes.FREE: 'giftsystem_3_participationRightBaseEnvelope'}
ENVELOPE_ENTITLEMENT_COUNTER = 'loot_box_counter'
ENVELOPE_TYPE_TO_ENTITLEMENT_CODE = {eType:code for code, eType in ENVELOPE_ENTITLEMENT_CODE_TO_TYPE.iteritems()}
ENVELOPE_TYPE_TO_LOOT_BOXES = {EnvelopeTypes.PAID: LunarNYLootBoxTypes.SIMPLE,
 EnvelopeTypes.PREMIUM_PAID: LunarNYLootBoxTypes.SPECIAL,
 EnvelopeTypes.FREE: LunarNYLootBoxTypes.BASE}
LOOT_BOX_TYPE_TO_ENVELOPE_TYPE = {v:k for k, v in ENVELOPE_TYPE_TO_LOOT_BOXES.iteritems()}
MAIN_VIEW_INIT_CONTEXT_ENVELOPE_TYPE = 'initialEnvelopeType'
MAIN_VIEW_INIT_CONTEXT_ENVELOPE_SENDER_ID = 'initialEnvelopeSenderID'
MAIN_VIEW_INIT_CONTEXT_TAB = 'initialTab'
MAIN_VIEW_INIT_CONTEXT_SEND_TO_PLAYER = 'sendEnvelopeToPlayer'
LUNAR_NY_PROGRESSION_QUEST_ID = 'LunarNYEnvelopesProgression:level'
LUNAR_NY_PROGRESSION_QUEST_ID_FORMAT = 'LunarNYEnvelopesProgression:level_{}'
SHOW_TAB_EVENT = 'showTabEvent'
SEND_TO_PLAYER_EVENT = 'sendToPlayerEvent'
SEND_TO_PLAYER_EVENT_IS_ENABLED = 'isEnabled'
