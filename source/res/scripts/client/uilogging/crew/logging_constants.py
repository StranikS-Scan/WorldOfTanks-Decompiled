# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/crew/logging_constants.py
from enum import Enum
from gui.impl.gen import R
FEATURE = 'crew'
MIN_VIEW_TIME = 2.0

class CrewLogActions(Enum):
    OPEN = 'open'
    CLOSE = 'close'
    CLICK = 'click'
    VIEWED = 'viewed'


class CrewViewKeys(Enum):
    HANGAR = 'hangar'
    PERSONAL_FILE = 'personal_file_view'
    PERSONAL_DATA = 'personal_data_view'
    SERVICE_RECORD = 'service_record_view'
    BARRACKS = 'barracks_view'
    MEMBER_CHANGE = 'member_change_view'
    QUICK_TRAINING = 'quick_training_view'
    TANK_CHANGE = 'tank_change_view'
    WELCOME = 'welcome_view'


class CrewDialogKeys(Enum):
    TANK_CHANGE = 'tank_change_dialog'
    DISMISS_TANKMAN = 'dismiss_tankman_dialog'
    DOCUMENT_CHANGE = 'document_change_dialog'
    RECRUIT = 'recruit_dialog'
    RESTORE_TANKMAN = 'restore_tankman_dialog'
    SKIN_APPLY = 'skin_apply_dialog'
    CONFIRM_SKILLS_LEARN = 'confirm_skills_learn_dialog'
    FREE_SKILL_CONFIRMATION = 'free_skill_confirmation_dialog'
    RETRAIN_SINGLE = 'retrain_single_dialog'


class CrewWidgetKeys(Enum):
    CREW_OPERATIONS_BUTTON = 'crew_widget_crew_operations_button'
    QUIK_TRAINING_BUTTON = 'crew_widget_quik_training_button'
    ACCELERATE_BUTTON = 'crew_widget_accelerate_button'
    TANKMAN_SLOT = 'crew_widget_tankman_slot'
    CHANGE_TANKMAN_BUTTON = 'crew_widget_change_tankman_button'
    SLOT_CONTEXT_MENU = 'crew_widget_slot_context_menu'
    TANKMAN_TOOLTIP = 'crew_widget_tankman_tooltip'
    CHANGE_BUTTON_TOOLTIP = 'crew_widget_change_button_tooltip'


class CrewTankmanContextMenuKeys(Enum):
    PERSONAL_FILE = 'tankman_cm_personal_file_button'
    CHANGE_MEMBER = 'tankman_cm_change_member_button'
    SEND_TO_BARRACKS = 'tankman_cm_send_to_barracks_button'
    DISMISS = 'tankman_cm_dismiss_button'
    QUICK_TRAINING = 'tankman_cm_quick_training_button'
    TANK_CHANGE = 'tankman_cm_tank_change_button'
    RETRAIN = 'tankman_cm_retrain_button'


class CrewPersonalFileKeys(Enum):
    TAB_PERSONAL_FILE = 'personal_file_view_tab_personal_file'
    TAB_PERSONAL_DATA = 'personal_file_view_tab_personal_data'
    TAB_SERVICE_RECORD = 'personal_file_view_tab_service_record'
    TANKMAN_TOOLTIP = 'personal_file_view_tankman_tooltip'
    VOICEOVER_BUTTON = 'personal_file_view_voiceover_button'
    CHANGE_SPECIALIZATION_BUTTON = 'personal_file_view_change_specialization_button'
    RETRAIN_BUTTON = 'personal_file_view_retrain_button'
    PREMIUM_TOOLTIP = 'personal_file_view_premium_tooltip'
    MATRIX_SKILL_TOOLTIP = 'personal_file_view_matrix_skill_tooltip'
    MATRIX_SKILL = 'personal_file_view_matrix_skill'
    MATRIX_INCREASE_BUTTON = 'personal_file_view_matrix_increase_button'
    MATRIX_RESET_BUTTON = 'personal_file_view_matrix_reset_button'


class CrewMemberChangeKeys(Enum):
    CARD = 'member_change_view_card'
    CARD_VOICEOVER_BUTTON = 'member_change_view_card_voiceover_button'
    TANKMAN_CARD_TOOLTIP = 'member_change_view_tankman_card_tooltip'
    DISMISSED_TOGGLE_TOOLTIP = 'member_change_view_dismissed_toggle_tooltip'


class CrewTankChangeKeys(Enum):
    CARD = 'tank_change_view_card'


class CrewQuickTrainingKeys(Enum):
    FREE_XP_CARD = 'quick_training_view_free_xp_card'
    CREW_BOOK_CARD = 'quick_training_view_crew_book_card'
    BUY_CREW_BOOK_BUTTON = 'quick_training_view_buy_crew_book_button'
    SUBMIT_BUTTON = 'quick_training_view_submit_button'
    CANCEL_BUTTON = 'quick_training_view_cancel_button'
    ESC_BUTTON = 'quick_training_view_esc_button'


class CrewPersonalDataKeys(Enum):
    DOCUMENT_CARD = 'personal_data_view_document_card'
    SKIN_CARD = 'personal_data_view_skin_card'


class CrewBarracksKeys(Enum):
    CARD = 'barracks_view_card'
    CARD_DISMISS_BUTTON = 'barracks_view_card_dismiss_button'
    CARD_VOICEOVER_BUTTON = 'barracks_view_card_voiceover_button'
    CARD_CONTEXT_MENU = 'barracks_view_card_context_menu'


class CrewDocumentChangeDialogKeys(Enum):
    FIRSTNAME_SELECT = 'document_change_dialog_firstname_select'
    FIRSTNAME = 'document_change_dialog_firstname'
    LASTNAME_SELECT = 'document_change_dialog_lastname_select'
    LASTNAME = 'document_change_dialog_lastname'


class CrewNavigationButtons(Enum):
    ESC = 'esc'
    CLOSE = 'close'
    TO_PERSONAL_FILE = 'to_personal_file'
    TO_GARAGE = 'to_garage'
    TO_BARRACKS = 'to_barracks'
    SUBMIT = 'submit'
    AFFIRMATIVE = 'affirmative'
    CANCEL = 'cancel'


class CrewMemberAdditionalInfo(Enum):
    RECRUIT = '0'
    TANKMAN = '1'


class TooltipAdditionalInfo(Enum):
    MAIN = '0'
    ALT = '1'


LAYOUT_ID_TO_ITEM = {R.views.lobby.crew.personal_case.PersonalFileView(): CrewViewKeys.PERSONAL_FILE,
 R.views.lobby.crew.personal_case.PersonalDataView(): CrewViewKeys.PERSONAL_DATA,
 R.views.lobby.crew.personal_case.ServiceRecordView(): CrewViewKeys.SERVICE_RECORD,
 R.views.lobby.crew.BarracksView(): CrewViewKeys.BARRACKS,
 R.views.lobby.crew.HangarCrewWidget(): CrewViewKeys.HANGAR,
 R.views.lobby.crew.MemberChangeView(): CrewViewKeys.MEMBER_CHANGE,
 R.views.lobby.crew.TankChangeView(): CrewViewKeys.TANK_CHANGE,
 R.views.lobby.crew.QuickTrainingView(): CrewViewKeys.QUICK_TRAINING}
TABS_LOGGING_KEYS = {R.views.lobby.crew.personal_case.PersonalFileView(): CrewPersonalFileKeys.TAB_PERSONAL_FILE,
 R.views.lobby.crew.personal_case.PersonalDataView(): CrewPersonalFileKeys.TAB_PERSONAL_DATA,
 R.views.lobby.crew.personal_case.ServiceRecordView(): CrewPersonalFileKeys.TAB_SERVICE_RECORD}
