# Embedded file name: scripts/client/gui/Scaleform/locale/SYSTEM_MESSAGES.py
from debug_utils import LOG_WARNING

class SYSTEM_MESSAGES(object):
    REPAIR_SUCCESS = '#system_messages:repair/success'
    REPAIR_CREDIT_ERROR = '#system_messages:repair/credit_error'
    REPAIR_SERVER_ERROR = '#system_messages:repair/server_error'
    CHARGE_CREDIT_ERROR_GOLD = '#system_messages:charge/credit_error_gold'
    CHARGE_CREDIT_ERROR_CREDITS = '#system_messages:charge/credit_error_credits'
    CHARGE_CREDIT_ERROR = '#system_messages:charge/credit_error'
    CHARGE_MONEY_SPENT = '#system_messages:charge/money_spent'
    CHARGE_SUCCESS = '#system_messages:charge/success'
    CHARGE_SERVER_ERROR = '#system_messages:charge/server_error'
    CHARGE_INVENTORY_ERROR = '#system_messages:charge/inventory_error'
    CHARGE_SUCCESS_SAVE = '#system_messages:charge/success_save'
    CHARGE_SERVER_ERROR_SAVE = '#system_messages:charge/server_error_save'
    PREMIUM_CONTINUESUCCESS = '#system_messages:premium/continueSuccess'
    PREMIUM_BUYINGSUCCESS = '#system_messages:premium/buyingSuccess'
    PREMIUM_SERVER_ERROR = '#system_messages:premium/server_error'
    PREMIUM_NOT_ENOUGH_GOLD = '#system_messages:premium/not_enough_gold'
    PREMIUM_WALLET_NOT_AVAILABLE = '#system_messages:premium/wallet_not_available'
    PREMIUM_POST_BATTLE_PREMIUM = '#system_messages:premium/post_battle_premium'
    BOOSTER_ACTIVATIONSUCCESS = '#system_messages:booster/activationSuccess'
    BOOSTER_SERVER_ERROR = '#system_messages:booster/server_error'
    BOOSTER_NO_BOOSTERS = '#system_messages:booster/NO_BOOSTERS'
    BOOSTER_ALREADY_USED = '#system_messages:booster/ALREADY_USED'
    BOOSTER_DISABLED = '#system_messages:booster/DISABLED'
    BOOSTER_EXCEPTION = '#system_messages:booster/EXCEPTION'
    BOOSTER_WRONG_ARGS = '#system_messages:booster/WRONG_ARGS'
    UPGRADETANKMAN_SUCCESS = '#system_messages:upgradeTankman/success'
    UPGRADETANKMAN_SERVER_ERROR = '#system_messages:upgradeTankman/server_error'
    ARENA_START_ERRORS_JOIN_TIME_OUT = '#system_messages:arena_start_errors/join/TIME_OUT'
    ARENA_START_ERRORS_JOIN_NOT_FOUND = '#system_messages:arena_start_errors/join/NOT_FOUND'
    ARENA_START_ERRORS_JOIN_WRONG_PERIPHERY_KNOWN = '#system_messages:arena_start_errors/join/WRONG_PERIPHERY_KNOWN'
    ARENA_START_ERRORS_JOIN_WRONG_PERIPHERY_UNKNOWN = '#system_messages:arena_start_errors/join/WRONG_PERIPHERY_UNKNOWN'
    ARENA_START_ERRORS_JOIN_ACCOUNT_LOCK = '#system_messages:arena_start_errors/join/ACCOUNT_LOCK'
    ARENA_START_ERRORS_JOIN_WRONG_VEHICLE = '#system_messages:arena_start_errors/join/WRONG_VEHICLE'
    ARENA_START_ERRORS_JOIN_TEAM_IS_FULL = '#system_messages:arena_start_errors/join/TEAM_IS_FULL'
    ARENA_START_ERRORS_JOIN_WRONG_ARGS = '#system_messages:arena_start_errors/join/WRONG_ARGS'
    ARENA_START_ERRORS_JOIN_CAPTCHA = '#system_messages:arena_start_errors/join/CAPTCHA'
    ARENA_START_ERRORS_JOIN_WRONG_ARENA_STATE = '#system_messages:arena_start_errors/join/WRONG_ARENA_STATE'
    ARENA_START_ERRORS_JOIN_CANNOT_CREATE = '#system_messages:arena_start_errors/join/CANNOT_CREATE'
    ARENA_START_ERRORS_JOIN_PRIVACY = '#system_messages:arena_start_errors/join/PRIVACY'
    ARENA_START_ERRORS_JOIN_WRONG_ACCOUNT_TYPE = '#system_messages:arena_start_errors/join/WRONG_ACCOUNT_TYPE'
    ARENA_START_ERRORS_JOIN_COOLDOWN = '#system_messages:arena_start_errors/join/COOLDOWN'
    ARENA_START_ERRORS_JOIN_NO_VEHICLE = '#system_messages:arena_start_errors/join/no_vehicle'
    ARENA_START_ERRORS_JOIN_NO_READYVEHICLE = '#system_messages:arena_start_errors/join/no_readyVehicle'
    ARENA_START_ERRORS_JOIN_WRONG_BATTLE_ID = '#system_messages:arena_start_errors/join/WRONG_BATTLE_ID'
    ARENA_START_ERRORS_JOIN_EVENT_DISABLED = '#system_messages:arena_start_errors/join/EVENT_DISABLED'
    PREBATTLE_KICK_TYPE_SQUAD = '#system_messages:prebattle/kick/type/squad'
    PREBATTLE_KICK_TYPE_TEAM = '#system_messages:prebattle/kick/type/team'
    PREBATTLE_KICK_TYPE_UNKNOWN = '#system_messages:prebattle/kick/type/unknown'
    PREBATTLE_KICK_REASON_ARENA_CREATION_FAILURE = '#system_messages:prebattle/kick/reason/ARENA_CREATION_FAILURE'
    PREBATTLE_KICK_REASON_AVATAR_CREATION_FAILURE = '#system_messages:prebattle/kick/reason/AVATAR_CREATION_FAILURE'
    PREBATTLE_KICK_REASON_VEHICLE_CREATION_FAILURE = '#system_messages:prebattle/kick/reason/VEHICLE_CREATION_FAILURE'
    PREBATTLE_KICK_REASON_PREBATTLE_CREATION_FAILURE = '#system_messages:prebattle/kick/reason/PREBATTLE_CREATION_FAILURE'
    PREBATTLE_KICK_REASON_BASEAPP_CRASH = '#system_messages:prebattle/kick/reason/BASEAPP_CRASH'
    PREBATTLE_KICK_REASON_CELLAPP_CRASH = '#system_messages:prebattle/kick/reason/CELLAPP_CRASH'
    PREBATTLE_KICK_REASON_UNKNOWN_FAILURE = '#system_messages:prebattle/kick/reason/UNKNOWN_FAILURE'
    PREBATTLE_KICK_REASON_FINISHED = '#system_messages:prebattle/kick/reason/FINISHED'
    PREBATTLE_KICK_REASON_CREATOR_LEFT = '#system_messages:prebattle/kick/reason/CREATOR_LEFT'
    PREBATTLE_KICK_REASON_PLAYERKICK = '#system_messages:prebattle/kick/reason/PLAYERKICK'
    PREBATTLE_KICK_REASON_TIMEOUT = '#system_messages:prebattle/kick/reason/TIMEOUT'
    SESSION_TRACKER_KICK = '#system_messages:session_tracker_kick'
    PREBATTLE_VEHICLEINVALID_LIMITS_LEVEL = '#system_messages:prebattle/vehicleInvalid/limits/level'
    PREBATTLE_VEHICLEINVALID_LIMITS_CLASSLEVEL = '#system_messages:prebattle/vehicleInvalid/limits/classLevel'
    PREBATTLE_VEHICLEINVALID_LIMITS_VEHICLES = '#system_messages:prebattle/vehicleInvalid/limits/vehicles'
    PREBATTLE_VEHICLEINVALID_LIMITS_COMPONENTS = '#system_messages:prebattle/vehicleInvalid/limits/components'
    PREBATTLE_VEHICLEINVALID_LIMITS_AMMO = '#system_messages:prebattle/vehicleInvalid/limits/ammo'
    PREBATTLE_VEHICLEINVALID_LIMITS_SHELLS = '#system_messages:prebattle/vehicleInvalid/limits/shells'
    PREBATTLE_VEHICLEINVALID_LIMITS_TAGS = '#system_messages:prebattle/vehicleInvalid/limits/tags'
    PREBATTLE_VEHICLEINVALID_LIMITS_NOT_SUPPORTED = '#system_messages:prebattle/vehicleInvalid/limits/not_supported'
    PREBATTLE_VEHICLEINVALID_NO_READYVEHICLE = '#system_messages:prebattle/vehicleInvalid/no_readyVehicle'
    PREBATTLE_VEHICLEINVALID_VEHICLENOTSUPPORTED = '#system_messages:prebattle/vehicleInvalid/vehicleNotSupported'
    PREBATTLE_VEHICLEINVALID_NOTSETREADYSTATUS = '#system_messages:prebattle/vehicleInvalid/notSetReadyStatus'
    PREBATTLE_VEHICLEINVALID_FALLOUTONLY = '#system_messages:prebattle/vehicleInvalid/falloutOnly'
    PREBATTLE_VEHICLEINVALID_LIMITS_NATIONS = '#system_messages:prebattle/vehicleInvalid/limits/nations'
    PREBATTLE_VEHICLEINVALID_LIMITS_CLASSES = '#system_messages:prebattle/vehicleInvalid/limits/classes'
    PREBATTLE_TEAMINVALID_LIMIT_MINCOUNT = '#system_messages:prebattle/teamInvalid/limit/minCount'
    PREBATTLE_TEAMINVALID_LIMIT_TOTALLEVEL = '#system_messages:prebattle/teamInvalid/limit/totalLevel'
    PREBATTLE_TEAMINVALID_LIMITS_VEHICLES = '#system_messages:prebattle/teamInvalid/limits/vehicles'
    PREBATTLE_TEAMINVALID_LIMITS_LEVEL = '#system_messages:prebattle/teamInvalid/limits/level'
    PREBATTLE_TEAMINVALID_OBSERVERS = '#system_messages:prebattle/teamInvalid/observers'
    PREBATTLE_TEAMINVALID_EVENT_BATTLE = '#system_messages:prebattle/teamInvalid/event_battle'
    PREBATTLE_HASLOCKEDSTATE = '#system_messages:prebattle/hasLockedState'
    PREBATTLE_INVITES_SENDINVITE_NAME = '#system_messages:prebattle/invites/sendInvite/name'
    PREBATTLE_INVITES_SENDINVITE = '#system_messages:prebattle/invites/sendInvite'
    ARENA_START_ERRORS_KICK_ARENA_CREATION_FAILURE = '#system_messages:arena_start_errors/kick/ARENA_CREATION_FAILURE'
    ARENA_START_ERRORS_KICK_AVATAR_CREATION_FAILURE = '#system_messages:arena_start_errors/kick/AVATAR_CREATION_FAILURE'
    ARENA_START_ERRORS_KICK_VEHICLE_CREATION_FAILURE = '#system_messages:arena_start_errors/kick/VEHICLE_CREATION_FAILURE'
    ARENA_START_ERRORS_KICK_PREBATTLE_CREATION_FAILURE = '#system_messages:arena_start_errors/kick/PREBATTLE_CREATION_FAILURE'
    ARENA_START_ERRORS_KICK_BASEAPP_CRASH = '#system_messages:arena_start_errors/kick/BASEAPP_CRASH'
    ARENA_START_ERRORS_KICK_CELLAPP_CRASH = '#system_messages:arena_start_errors/kick/CELLAPP_CRASH'
    ARENA_START_ERRORS_KICK_UNKNOWN_FAILURE = '#system_messages:arena_start_errors/kick/UNKNOWN_FAILURE'
    ARENA_START_ERRORS_KICK_FINISHED = '#system_messages:arena_start_errors/kick/FINISHED'
    ARENA_START_ERRORS_KICK_CREATOR_LEFT = '#system_messages:arena_start_errors/kick/CREATOR_LEFT'
    ARENA_START_ERRORS_KICK_PLAYERKICK = '#system_messages:arena_start_errors/kick/PLAYERKICK'
    ARENA_START_ERRORS_KICK_TIMEOUT = '#system_messages:arena_start_errors/kick/TIMEOUT'
    ARENA_START_ERRORS_KICK_TIMEOUT_ = '#system_messages:arena_start_errors/kick/timeout'
    PREBATTLE_START_FAILED_KICKEDFROMQUEUE_SQUAD = '#system_messages:prebattle_start_failed/kickedFromQueue/squad'
    PREBATTLE_START_FAILED_KICKEDFROMQUEUE_COMPANY = '#system_messages:prebattle_start_failed/kickedFromQueue/company'
    PREBATTLE_START_FAILED_KICKEDFROMQUEUE_DEAFULT = '#system_messages:prebattle_start_failed/kickedFromQueue/deafult'
    WRONG_SLOT = '#system_messages:wrong_slot'
    CLIENTINSTALLERROR_WRONG_NATION = '#system_messages:clientInstallError_wrong_nation'
    CLIENTINSTALLERROR_NOT_FOR_THIS_VEHICLE_TYPE = '#system_messages:clientInstallError_not_for_this_vehicle_type'
    CLIENTINSTALLERROR_VEHICLEGUN_NOT_FOR_CURRENT_VEHICLE = '#system_messages:clientInstallError_vehicleGun_not_for_current_vehicle'
    CLIENTINSTALLERROR_WRONG_ITEM_TYPE = '#system_messages:clientInstallError_wrong_item_type'
    CLIENTINSTALLERROR_TOO_HEAVY = '#system_messages:clientInstallError_too_heavy'
    CLIENTREMOVEERROR_WRONG_NATION = '#system_messages:clientRemoveError_wrong_nation'
    CLIENTREMOVEERROR_NOT_IN_LIST = '#system_messages:clientRemoveError_not_in_list'
    CLIENTREMOVEERROR_WRONG_ITEM_TYPE = '#system_messages:clientRemoveError_wrong_item_type'
    CLIENTREMOVEERROR_TOO_HEAVY = '#system_messages:clientRemoveError_too_heavy'
    SERVERINSTALLERROR = '#system_messages:serverInstallError'
    SERVERREMOVEERROR = '#system_messages:serverRemoveError'
    BUY_VEHICLE_SLOT_ERROR = '#system_messages:buy_vehicle_slot_error'
    BUY_VEHICLE_SLOT_ERROR2 = '#system_messages:buy_vehicle_slot_error2'
    BUY_FREE_VEHICLE_LIMIT_ERROR = '#system_messages:buy_free_vehicle_limit_error'
    INSTALL_COMPONENT = '#system_messages:install_component'
    REMOVE_COMPONENT = '#system_messages:remove_component'
    CURRENT_VEHICLE_CHANGED = '#system_messages:current_vehicle_changed'
    INSTALL_VEHICLE_LOCKED = '#system_messages:install_vehicle_locked'
    INSTALL_VEHICLE_BROKEN = '#system_messages:install_vehicle_broken'
    REMOVE_VEHICLE_LOCKED = '#system_messages:remove_vehicle_locked'
    REMOVE_VEHICLE_BROKEN = '#system_messages:remove_vehicle_broken'
    SELL_VEHICLE_LOCKED = '#system_messages:sell_vehicle_locked'
    SELL_VEHICLE_BROKEN = '#system_messages:sell_vehicle_broken'
    WINDOW_BUTTONS_CLOSE = '#system_messages:window/buttons/close'
    CONNECTED = '#system_messages:connected'
    DISCONNECTED = '#system_messages:disconnected'
    ROAMING_NOT_ALLOWED = '#system_messages:roaming_not_allowed'
    SERVER_SHUT_DOWN = '#system_messages:server_shut_down'
    UNLOCKS_VEHICLE_UNLOCK_SUCCESS = '#system_messages:unlocks/vehicle/unlock_success'
    UNLOCKS_ITEM_UNLOCK_SUCCESS = '#system_messages:unlocks/item/unlock_success'
    UNLOCKS_VEHICLE_ALREADY_UNLOCKED = '#system_messages:unlocks/vehicle/already_unlocked'
    UNLOCKS_ITEM_ALREADY_UNLOCKED = '#system_messages:unlocks/item/already_unlocked'
    UNLOCKS_VEHICLE_SERVER_ERROR = '#system_messages:unlocks/vehicle/server_error'
    UNLOCKS_ITEM_SERVER_ERROR = '#system_messages:unlocks/item/server_error'
    UNLOCKS_VEHICLE_IN_PROCESSING = '#system_messages:unlocks/vehicle/in_processing'
    UNLOCKS_ITEM_IN_PROCESSING = '#system_messages:unlocks/item/in_processing'
    UNLOCKS_DRAWFAILED = '#system_messages:unlocks/drawFailed'
    SHOP_VEHICLE_NOT_ENOUGH_MONEY = '#system_messages:shop/vehicle/not_enough_money'
    SHOP_VEHICLE_NOT_ENOUGH_MONEY_FOR_RENT = '#system_messages:shop/vehicle/not_enough_money_for_rent'
    SHOP_VEHICLE_COMMON_RENT_OR_BUY_ERROR = '#system_messages:shop/vehicle/common_rent_or_buy_error'
    SHOP_ITEM_NOT_ENOUGH_MONEY = '#system_messages:shop/item/not_enough_money'
    SHOP_VEHICLE_NOT_FOUND = '#system_messages:shop/vehicle/not_found'
    SHOP_ITEM_NOT_FOUND = '#system_messages:shop/item/not_found'
    SHOP_ITEM_COMMON_RENT_OR_BUY_ERROR = '#system_messages:shop/item/common_rent_or_buy_error'
    SHOP_ITEM_BUY_SUCCESS = '#system_messages:shop/item/buy_success'
    SHOP_ITEM_BUY_SERVER_ERROR = '#system_messages:shop/item/buy_server_error'
    SHOP_ITEM_BUY_AND_EQUIP_IN_PROCESSING = '#system_messages:shop/item/buy_and_equip_in_processing'
    INVENTORY_VEHICLE_NOT_FOUND = '#system_messages:inventory/vehicle/not_found'
    INVENTORY_ITEM_NOT_FOUND = '#system_messages:inventory/item/not_found'
    INVENTORY_VEHICLE_ALREADY_EXISTS = '#system_messages:inventory/vehicle/already_exists'
    INVENTORY_ITEM_ALREADY_EXISTS = '#system_messages:inventory/item/already_exists'
    INVENTORY_ITEM_EQUIP_IN_PROCESSING = '#system_messages:inventory/item/equip_in_processing'
    SQUAD_MEMBERJOINED = '#system_messages:squad/memberJoined'
    SQUAD_MEMBERLEAVE = '#system_messages:squad/memberLeave'
    SQUAD_MEMBERREADY = '#system_messages:squad/memberReady'
    SQUAD_MEMBERNOTREADY = '#system_messages:squad/memberNotReady'
    SQUAD_MEMBEROFFLINE = '#system_messages:squad/memberOffline'
    SQUAD_CREATEERROR = '#system_messages:squad/createError'
    SQUAD_NOTSETREADYSTATUS = '#system_messages:squad/notSetReadyStatus'
    SQUAD_KICKEDFROMQUEUE = '#system_messages:squad/kickedFromQueue'
    COMPANY_MEMBERJOINED = '#system_messages:company/memberJoined'
    COMPANY_MEMBERLEAVE = '#system_messages:company/memberLeave'
    COMPANY_MEMBERREADY = '#system_messages:company/memberReady'
    COMPANY_MEMBERNOTREADY = '#system_messages:company/memberNotReady'
    COMPANY_MEMBEROFFLINE = '#system_messages:company/memberOffline'
    COMPANY_CREATEERROR = '#system_messages:company/createError'
    COMPANY_NOTSETREADYSTATUS = '#system_messages:company/notSetReadyStatus'
    COMPANY_KICKEDFROMQUEUE = '#system_messages:company/kickedFromQueue'
    BATTLESESSION_KICKEDFROMQUEUE = '#system_messages:battleSession/kickedFromQueue'
    MEMBERROSTERCHANGEDMAIN = '#system_messages:memberRosterChangedMain'
    MEMBERROSTERCHANGEDSECOND = '#system_messages:memberRosterChangedSecond'
    BATTLESESSION_MEMBERJOINED = '#system_messages:battleSession/memberJoined'
    BATTLESESSION_MEMBERLEAVE = '#system_messages:battleSession/memberLeave'
    BATTLESESSION_MEMBERREADY = '#system_messages:battleSession/memberReady'
    BATTLESESSION_MEMBERNOTREADY = '#system_messages:battleSession/memberNotReady'
    BATTLESESSION_MEMBEROFFLINE = '#system_messages:battleSession/memberOffline'
    MEMORY_CRITICAL_INSUFFICIENT_MEMORY_PLEASE_REBOOT = '#system_messages:memory_critical/insufficient_memory_please_reboot'
    MEMORY_CRITICAL_TEX_WAS_LOWERED_TO_MEDIUM = '#system_messages:memory_critical/tex_was_lowered_to_medium'
    MEMORY_CRITICAL_TEX_WAS_LOWERED_TO_LOW = '#system_messages:memory_critical/tex_was_lowered_to_low'
    MEMORY_CRITICAL_TEX_WAS_LOWERED_TO_MIN = '#system_messages:memory_critical/tex_was_lowered_to_min'
    TRADINGERROR_TOO_MANY_OUT_OFFERS = '#system_messages:tradingError/TOO_MANY_OUT_OFFERS'
    TRADINGERROR_NOT_ALLOWED = '#system_messages:tradingError/NOT_ALLOWED'
    TRADINGERROR_NO_WARES = '#system_messages:tradingError/NO_WARES'
    TRADINGERROR_DECLINED_BY_DEST = '#system_messages:tradingError/DECLINED_BY_DEST'
    TRADINGERROR_UNEXPECTED_ERROR = '#system_messages:tradingError/UNEXPECTED_ERROR'
    GRAFICSOPTIONSFAIL = '#system_messages:graficsOptionsFail'
    GRAFICSPRESETFAIL = '#system_messages:graficsPresetFail'
    DENUNCIATION_SUCCESS = '#system_messages:denunciation/success'
    CUSTOMIZATION_CREDITS_NOT_ENOUGH = '#system_messages:customization/credits_not_enough'
    CUSTOMIZATION_GOLD_NOT_ENOUGH = '#system_messages:customization/gold_not_enough'
    CUSTOMIZATION_CREDITS_AND_GOLD_NOT_ENOUGH = '#system_messages:customization/credits_and_gold_not_enough'
    CUSTOMIZATION_VEHICLE_LOCKED = '#system_messages:customization/vehicle_locked'
    CUSTOMIZATION_VEHICLE_DAMAGED = '#system_messages:customization/vehicle_damaged'
    CUSTOMIZATION_VEHICLE_DESTROYED = '#system_messages:customization/vehicle_destroyed'
    CUSTOMIZATION_VEHICLE_EXPLODED = '#system_messages:customization/vehicle_exploded'
    CUSTOMIZATION_CAMOUFLAGE_NOT_SELECTED = '#system_messages:customization/camouflage_not_selected'
    CUSTOMIZATION_CAMOUFLAGE_DAYS_NOT_SELECTED = '#system_messages:customization/camouflage_days_not_selected'
    CUSTOMIZATION_CAMOUFLAGE_COST_NOT_FOUND = '#system_messages:customization/camouflage_cost_not_found'
    CUSTOMIZATION_CAMOUFLAGE_NOT_FOUND_TO_DROP = '#system_messages:customization/camouflage_not_found_to_drop'
    CUSTOMIZATION_CAMOUFLAGE_GET_COST_SERVER_ERROR = '#system_messages:customization/camouflage_get_cost_server_error'
    CUSTOMIZATION_CAMOUFLAGE_CHANGE_SERVER_ERROR = '#system_messages:customization/camouflage_change_server_error'
    CUSTOMIZATION_CAMOUFLAGE_DROP_SERVER_ERROR = '#system_messages:customization/camouflage_drop_server_error'
    CUSTOMIZATION_CAMOUFLAGE_CHANGE_SUCCESS_CREDITS = '#system_messages:customization/camouflage_change_success/credits'
    CUSTOMIZATION_CAMOUFLAGE_CHANGE_SUCCESS_GOLD = '#system_messages:customization/camouflage_change_success/gold'
    CUSTOMIZATION_CAMOUFLAGE_CHANGE_SUCCESS_FREE = '#system_messages:customization/camouflage_change_success/free'
    CUSTOMIZATION_CAMOUFLAGE_DROP_SUCCESS = '#system_messages:customization/camouflage_drop_success'
    CUSTOMIZATION_CAMOUFLAGE_STORED_SUCCESS = '#system_messages:customization/camouflage_stored_success'
    CUSTOMIZATION_EMBLEM_NOT_SELECTED = '#system_messages:customization/emblem_not_selected'
    CUSTOMIZATION_EMBLEM_DAYS_NOT_SELECTED = '#system_messages:customization/emblem_days_not_selected'
    CUSTOMIZATION_EMBLEM_COST_NOT_FOUND = '#system_messages:customization/emblem_cost_not_found'
    CUSTOMIZATION_EMBLEM_NOT_FOUND_TO_DROP = '#system_messages:customization/emblem_not_found_to_drop'
    CUSTOMIZATION_EMBLEM_GET_COST_SERVER_ERROR = '#system_messages:customization/emblem_get_cost_server_error'
    CUSTOMIZATION_EMBLEM_CHANGE_SERVER_ERROR = '#system_messages:customization/emblem_change_server_error'
    CUSTOMIZATION_EMBLEM_DROP_SERVER_ERROR = '#system_messages:customization/emblem_drop_server_error'
    CUSTOMIZATION_EMBLEM_CHANGE_SUCCESS_CREDITS = '#system_messages:customization/emblem_change_success/credits'
    CUSTOMIZATION_EMBLEM_CHANGE_SUCCESS_GOLD = '#system_messages:customization/emblem_change_success/gold'
    CUSTOMIZATION_EMBLEM_CHANGE_SUCCESS_FREE = '#system_messages:customization/emblem_change_success/free'
    CUSTOMIZATION_EMBLEM_DROP_SUCCESS = '#system_messages:customization/emblem_drop_success'
    CUSTOMIZATION_EMBLEM_STORED_SUCCESS = '#system_messages:customization/emblem_stored_success'
    CUSTOMIZATION_INSCRIPTION_NOT_SELECTED = '#system_messages:customization/inscription_not_selected'
    CUSTOMIZATION_INSCRIPTION_DAYS_NOT_SELECTED = '#system_messages:customization/inscription_days_not_selected'
    CUSTOMIZATION_INSCRIPTION_COST_NOT_FOUND = '#system_messages:customization/inscription_cost_not_found'
    CUSTOMIZATION_INSCRIPTION_NOT_FOUND_TO_DROP = '#system_messages:customization/inscription_not_found_to_drop'
    CUSTOMIZATION_INSCRIPTION_GET_COST_SERVER_ERROR = '#system_messages:customization/inscription_get_cost_server_error'
    CUSTOMIZATION_INSCRIPTION_CHANGE_SERVER_ERROR = '#system_messages:customization/inscription_change_server_error'
    CUSTOMIZATION_INSCRIPTION_DROP_SERVER_ERROR = '#system_messages:customization/inscription_drop_server_error'
    CUSTOMIZATION_INSCRIPTION_CHANGE_SUCCESS_CREDITS = '#system_messages:customization/inscription_change_success/credits'
    CUSTOMIZATION_INSCRIPTION_CHANGE_SUCCESS_GOLD = '#system_messages:customization/inscription_change_success/gold'
    CUSTOMIZATION_INSCRIPTION_CHANGE_SUCCESS_FREE = '#system_messages:customization/inscription_change_success/free'
    CUSTOMIZATION_INSCRIPTION_DROP_SUCCESS = '#system_messages:customization/inscription_drop_success'
    CUSTOMIZATION_INSCRIPTION_STORED_SUCCESS = '#system_messages:customization/inscription_stored_success'
    CUSTOMIZATION_IGR_TYPE_CHANGED_ERROR = '#system_messages:customization/igr_type_changed_error'
    CUSTOMIZATION_ADDED_CAMOUFLAGES = '#system_messages:customization/added/camouflages'
    CUSTOMIZATION_ADDED_EMBLEMS = '#system_messages:customization/added/emblems'
    CUSTOMIZATION_ADDED_INSCRIPTIONS = '#system_messages:customization/added/inscriptions'
    CUSTOMIZATION_REMOVED_CAMOUFLAGES = '#system_messages:customization/removed/camouflages'
    CUSTOMIZATION_REMOVED_EMBLEMS = '#system_messages:customization/removed/emblems'
    CUSTOMIZATION_REMOVED_INSCRIPTIONS = '#system_messages:customization/removed/inscriptions'
    CUSTOMIZATION_ADDED_CAMOUFLAGESVALUE = '#system_messages:customization/added/camouflagesValue'
    CUSTOMIZATION_ADDED_EMBLEMSVALUE = '#system_messages:customization/added/emblemsValue'
    CUSTOMIZATION_ADDED_INSCRIPTIONSVALUE = '#system_messages:customization/added/inscriptionsValue'
    CHECKOUT_ERROR = '#system_messages:checkout_error'
    ANOTHER_PERIPHERY = '#system_messages:another_periphery'
    SHOP_RESYNC = '#system_messages:shop_resync'
    DOSSIERS_UNAVAILABLE = '#system_messages:dossiers_unavailable'
    ACTIONACHIEVEMENT_TITLE = '#system_messages:actionAchievement/title'
    ACTIONACHIEVEMENTS_TITLE = '#system_messages:actionAchievements/title'
    TRAINING_ERROR_SWAPTEAMS = '#system_messages:training/error/swapTeams'
    TRAINING_ERROR_DOACTION = '#system_messages:training/error/doAction'
    GAMESESSIONCONTROL_KOREA_SESSIONTIME = '#system_messages:gameSessionControl/korea/sessionTime'
    GAMESESSIONCONTROL_KOREA_TIMETILLMIDNIGHT = '#system_messages:gameSessionControl/korea/timeTillMidnight'
    GAMESESSIONCONTROL_KOREA_PLAYTIMELEFT = '#system_messages:gameSessionControl/korea/playTimeLeft'
    GAMESESSIONCONTROL_KOREA_MIDNIGHTNOTIFICATION = '#system_messages:gameSessionControl/korea/midnightNotification'
    GAMESESSIONCONTROL_KOREA_PLAYTIMENOTIFICATION = '#system_messages:gameSessionControl/korea/playTimeNotification'
    GAMESESSIONCONTROL_KOREA_NOTE = '#system_messages:gameSessionControl/korea/note'
    VIDEO_ERROR = '#system_messages:video/error'
    SECURITYMESSAGE_POOR_PASS = '#system_messages:securityMessage/poor_pass'
    SECURITYMESSAGE_NO_QUESTION = '#system_messages:securityMessage/no_question'
    SECURITYMESSAGE_BAD_EMAIL = '#system_messages:securityMessage/bad_email'
    SECURITYMESSAGE_NO_PHONE = '#system_messages:securityMessage/no_phone'
    SECURITYMESSAGE_OLD_PASS = '#system_messages:securityMessage/old_pass'
    SECURITYMESSAGE_CHANGE_SETINGS = '#system_messages:securityMessage/change_setings'
    ACCOUNT_WAS_RESTORED = '#system_messages:account_was_restored'
    LOGIN_TO_OTHER_GAME_WOT = '#system_messages:login_to_other_game_wot'
    LOGIN_TO_OTHER_GAME_WOWP = '#system_messages:login_to_other_game_wowp'
    LOGIN_TO_OTHER_GAME_WOTG = '#system_messages:login_to_other_game_wotg'
    LOGIN_TO_OTHER_GAME_WOWS = '#system_messages:login_to_other_game_wows'
    LOGIN_TO_OTHER_GAME_WOTB = '#system_messages:login_to_other_game_wotb'
    LOGIN_TO_OTHER_GAME_UNKNOWN = '#system_messages:login_to_other_game_unknown'
    LOGIN_TO_OTHER_GAME_WEB = '#system_messages:login_to_other_game_web'
    RECRUIT_WINDOW_SERVER_ERROR = '#system_messages:recruit_window/server_error'
    RECRUIT_WINDOW_SUCCESS = '#system_messages:recruit_window/success'
    RECRUIT_WINDOW_FINANCIAL_SUCCESS = '#system_messages:recruit_window/financial_success'
    RECRUIT_WINDOW_NOT_ENOUGH_CREDITS = '#system_messages:recruit_window/not_enough_credits'
    RECRUIT_WINDOW_NOT_ENOUGH_GOLD = '#system_messages:recruit_window/not_enough_gold'
    RECRUIT_WINDOW_WALLET_NOT_AVAILABLE = '#system_messages:recruit_window/wallet_not_available'
    RECRUIT_WINDOW_FREE_TANKMEN_LIMIT = '#system_messages:recruit_window/free_tankmen_limit'
    RECRUIT_WINDOW_NOT_ENOUGH_SPACE = '#system_messages:recruit_window/not_enough_space'
    EQUIP_TANKMAN_SUCCESS = '#system_messages:equip_tankman/success'
    EQUIP_TANKMAN_SERVER_ERROR = '#system_messages:equip_tankman/server_error'
    EQUIP_TANKMAN_INVALID_VEHICLE = '#system_messages:equip_tankman/invalid_vehicle'
    EQUIP_TANKMAN_VEHICLE_NEED_REPAIR = '#system_messages:equip_tankman/vehicle_need_repair'
    EQUIP_TANKMAN_VEHICLE_LOCKED = '#system_messages:equip_tankman/vehicle_locked'
    REEQUIP_TANKMAN_SUCCESS = '#system_messages:reequip_tankman/success'
    REEQUIP_TANKMAN_SERVER_ERROR = '#system_messages:reequip_tankman/server_error'
    REEQUIP_TANKMAN_INVALID_VEHICLE = '#system_messages:reequip_tankman/invalid_vehicle'
    REEQUIP_TANKMAN_VEHICLE_NEED_REPAIR = '#system_messages:reequip_tankman/vehicle_need_repair'
    REEQUIP_TANKMAN_VEHICLE_LOCKED = '#system_messages:reequip_tankman/vehicle_locked'
    BUY_AND_EQUIP_TANKMAN_SUCCESS = '#system_messages:buy_and_equip_tankman/success'
    BUY_AND_EQUIP_TANKMAN_FINANCIAL_SUCCESS = '#system_messages:buy_and_equip_tankman/financial_success'
    BUY_AND_EQUIP_TANKMAN_SERVER_ERROR = '#system_messages:buy_and_equip_tankman/server_error'
    BUY_AND_EQUIP_TANKMAN_INVALID_VEHICLE = '#system_messages:buy_and_equip_tankman/invalid_vehicle'
    BUY_AND_EQUIP_TANKMAN_VEHICLE_LOCKED = '#system_messages:buy_and_equip_tankman/vehicle_locked'
    BUY_AND_EQUIP_TANKMAN_NOT_ENOUGH_CREDITS = '#system_messages:buy_and_equip_tankman/not_enough_credits'
    BUY_AND_EQUIP_TANKMAN_NOT_ENOUGH_GOLD = '#system_messages:buy_and_equip_tankman/not_enough_gold'
    BUY_AND_EQUIP_TANKMAN_WALLET_NOT_AVAILABLE = '#system_messages:buy_and_equip_tankman/wallet_not_available'
    BUY_AND_EQUIP_TANKMAN_FREE_TANKMEN_LIMIT = '#system_messages:buy_and_equip_tankman/free_tankmen_limit'
    BUY_AND_REEQUIP_TANKMAN_SUCCESS = '#system_messages:buy_and_reequip_tankman/success'
    BUY_AND_REEQUIP_TANKMAN_FINANCIAL_SUCCESS = '#system_messages:buy_and_reequip_tankman/financial_success'
    BUY_AND_REEQUIP_TANKMAN_SERVER_ERROR = '#system_messages:buy_and_reequip_tankman/server_error'
    BUY_AND_REEQUIP_TANKMAN_INVALID_VEHICLE = '#system_messages:buy_and_reequip_tankman/invalid_vehicle'
    BUY_AND_REEQUIP_TANKMAN_VEHICLE_LOCKED = '#system_messages:buy_and_reequip_tankman/vehicle_locked'
    BUY_AND_REEQUIP_TANKMAN_NOT_ENOUGH_CREDITS = '#system_messages:buy_and_reequip_tankman/not_enough_credits'
    BUY_AND_REEQUIP_TANKMAN_NOT_ENOUGH_GOLD = '#system_messages:buy_and_reequip_tankman/not_enough_gold'
    BUY_AND_REEQUIP_TANKMAN_WALLET_NOT_AVAILABLE = '#system_messages:buy_and_reequip_tankman/wallet_not_available'
    BUY_AND_REEQUIP_TANKMAN_FREE_TANKMEN_LIMIT = '#system_messages:buy_and_reequip_tankman/free_tankmen_limit'
    BUY_AND_REEQUIP_TANKMAN_NOT_ENOUGH_SPACE = '#system_messages:buy_and_reequip_tankman/not_enough_space'
    DISMISS_TANKMAN_SUCCESS = '#system_messages:dismiss_tankman/success'
    DISMISS_TANKMAN_SERVER_ERROR = '#system_messages:dismiss_tankman/server_error'
    DISMISS_TANKMAN_INVALID_VEHICLE = '#system_messages:dismiss_tankman/invalid_vehicle'
    DISMISS_TANKMAN_VEHICLE_NEED_REPAIR = '#system_messages:dismiss_tankman/vehicle_need_repair'
    DISMISS_TANKMAN_VEHICLE_LOCKED = '#system_messages:dismiss_tankman/vehicle_locked'
    UNLOAD_TANKMAN_SUCCESS = '#system_messages:unload_tankman/success'
    UNLOAD_TANKMAN_SERVER_ERROR = '#system_messages:unload_tankman/server_error'
    UNLOAD_TANKMAN_NOT_ENOUGH_SPACE = '#system_messages:unload_tankman/not_enough_space'
    UNLOAD_TANKMAN_INVALID_VEHICLE = '#system_messages:unload_tankman/invalid_vehicle'
    UNLOAD_TANKMAN_VEHICLE_NEED_REPAIR = '#system_messages:unload_tankman/vehicle_need_repair'
    UNLOAD_TANKMAN_VEHICLE_LOCKED = '#system_messages:unload_tankman/vehicle_locked'
    UNLOAD_CREW_SUCCESS = '#system_messages:unload_crew/success'
    UNLOAD_CREW_SERVER_ERROR = '#system_messages:unload_crew/server_error'
    UNLOAD_CREW_NOT_ENOUGH_SPACE = '#system_messages:unload_crew/not_enough_space'
    UNLOAD_CREW_INVALID_VEHICLE = '#system_messages:unload_crew/invalid_vehicle'
    UNLOAD_CREW_VEHICLE_NEED_REPAIR = '#system_messages:unload_crew/vehicle_need_repair'
    UNLOAD_CREW_VEHICLE_LOCKED = '#system_messages:unload_crew/vehicle_locked'
    RETURN_CREW_SUCCESS = '#system_messages:return_crew/success'
    RETURN_CREW_SERVER_ERROR = '#system_messages:return_crew/server_error'
    RETURN_CREW_NOT_ENOUGH_SPACE = '#system_messages:return_crew/not_enough_space'
    RETURN_CREW_INVALID_VEHICLE = '#system_messages:return_crew/invalid_vehicle'
    RETURN_CREW_VEHICLE_NEED_REPAIR = '#system_messages:return_crew/vehicle_need_repair'
    RETURN_CREW_VEHICLE_LOCKED = '#system_messages:return_crew/vehicle_locked'
    RETRAINING_TANKMAN_SUCCESS = '#system_messages:retraining_tankman/success'
    RETRAINING_TANKMAN_FINANCIAL_SUCCESS = '#system_messages:retraining_tankman/financial_success'
    RETRAINING_TANKMAN_SERVER_ERROR = '#system_messages:retraining_tankman/server_error'
    RETRAINING_TANKMAN_INVALID_VEHICLE = '#system_messages:retraining_tankman/invalid_vehicle'
    RETRAINING_TANKMAN_VEHICLE_NEED_REPAIR = '#system_messages:retraining_tankman/vehicle_need_repair'
    RETRAINING_TANKMAN_VEHICLE_LOCKED = '#system_messages:retraining_tankman/vehicle_locked'
    RETRAINING_TANKMAN_INVALID_OPERATION = '#system_messages:retraining_tankman/invalid_operation'
    RETRAINING_CREW_SUCCESS = '#system_messages:retraining_crew/success'
    RETRAINING_CREW_FINANCIAL_SUCCESS = '#system_messages:retraining_crew/financial_success'
    RETRAINING_CREW_SERVER_ERROR = '#system_messages:retraining_crew/server_error'
    RETRAINING_CREW_INVALID_VEHICLE = '#system_messages:retraining_crew/invalid_vehicle'
    RETRAINING_CREW_VEHICLE_NEED_REPAIR = '#system_messages:retraining_crew/vehicle_need_repair'
    RETRAINING_CREW_VEHICLE_LOCKED = '#system_messages:retraining_crew/vehicle_locked'
    RETRAINING_CREW_EMPTY_LIST = '#system_messages:retraining_crew/empty_list'
    RETRAINING_CREW_INVALID_OPERATION = '#system_messages:retraining_crew/invalid_operation'
    ADD_TANKMAN_SKILL_SUCCESS = '#system_messages:add_tankman_skill/success'
    ADD_TANKMAN_SKILL_SERVER_ERROR = '#system_messages:add_tankman_skill/server_error'
    ADD_TANKMAN_SKILL_INVALID_VEHICLE = '#system_messages:add_tankman_skill/invalid_vehicle'
    ADD_TANKMAN_SKILL_VEHICLE_NEED_REPAIR = '#system_messages:add_tankman_skill/vehicle_need_repair'
    ADD_TANKMAN_SKILL_VEHICLE_LOCKED = '#system_messages:add_tankman_skill/vehicle_locked'
    DROP_TANKMAN_SKILL_SUCCESS = '#system_messages:drop_tankman_skill/success'
    DROP_TANKMAN_SKILL_SERVER_ERROR = '#system_messages:drop_tankman_skill/server_error'
    DROP_TANKMAN_SKILL_INVALID_VEHICLE = '#system_messages:drop_tankman_skill/invalid_vehicle'
    DROP_TANKMAN_SKILL_VEHICLE_NEED_REPAIR = '#system_messages:drop_tankman_skill/vehicle_need_repair'
    DROP_TANKMAN_SKILL_VEHICLE_LOCKED = '#system_messages:drop_tankman_skill/vehicle_locked'
    CHANGE_TANKMAN_ROLE_SUCCESS = '#system_messages:change_tankman_role/success'
    CHANGE_TANKMAN_ROLE_INSTALLED = '#system_messages:change_tankman_role/installed'
    CHANGE_TANKMAN_ROLE_SLOT_IS_TAKEN = '#system_messages:change_tankman_role/slot_is_taken'
    CHANGE_TANKMAN_ROLE_NO_VEHICLE = '#system_messages:change_tankman_role/no_vehicle'
    CHANGE_TANKMAN_ROLE_SERVER_ERROR = '#system_messages:change_tankman_role/server_error'
    CHANGE_TANKMAN_ROLE_NOT_ENOUGH_GOLD = '#system_messages:change_tankman_role/not_enough_gold'
    CHANGE_TANKMAN_ROLE_NOT_ENOUGH_CREDITS = '#system_messages:change_tankman_role/not_enough_credits'
    CHANGE_TANKMAN_ROLE_WALLET_NOT_AVAILABLE = '#system_messages:change_tankman_role/wallet_not_available'
    CHANGE_TANKMAN_ROLE_INVALID_VEHICLE = '#system_messages:change_tankman_role/invalid_vehicle'
    CHANGE_TANKMAN_ROLE_INVALID_ROLE = '#system_messages:change_tankman_role/invalid_role'
    FREE_XP_TO_TMAN_SKILL_SUCCESS = '#system_messages:free_xp_to_tman_skill/success'
    FREE_XP_TO_TMAN_SKILL_SERVER_ERROR = '#system_messages:free_xp_to_tman_skill/server_error'
    FREE_XP_TO_TMAN_SKILL_ERROR_WRONG_ARGS_TYPE = '#system_messages:free_xp_to_tman_skill/error/WRONG_ARGS_TYPE'
    FREE_XP_TO_TMAN_SKILL_ERROR_NO_TANKMAN_WITH_GIVEN_ID = '#system_messages:free_xp_to_tman_skill/error/No tankman with given id'
    FREE_XP_TO_TMAN_SKILL_ERROR_SHOP_DESYNC = '#system_messages:free_xp_to_tman_skill/error/SHOP_DESYNC'
    FREE_XP_TO_TMAN_SKILL_ERROR_NO_FREE_XP = '#system_messages:free_xp_to_tman_skill/error/NO_FREE_XP'
    FREE_XP_TO_TMAN_SKILL_ERROR_NOT_IMPLEMENTED = '#system_messages:free_xp_to_tman_skill/error/NOT_IMPLEMENTED'
    REPLACE_TANKMAN_SUCCESS = '#system_messages:replace_tankman/success'
    REPLACE_TANKMAN_SERVER_ERROR = '#system_messages:replace_tankman/server_error'
    REPLACE_TANKMAN_INVALID_VEHICLE = '#system_messages:replace_tankman/invalid_vehicle'
    REPLACE_TANKMAN_VEHICLE_NEED_REPAIR = '#system_messages:replace_tankman/vehicle_need_repair'
    REPLACE_TANKMAN_VEHICLE_LOCKED = '#system_messages:replace_tankman/vehicle_locked'
    REPLACE_TANKMAN_NOT_ENOUGH_MONEY = '#system_messages:replace_tankman/not_enough_money'
    VEHICLE_BUY_SUCCESS = '#system_messages:vehicle_buy/success'
    VEHICLE_BUY_SERVER_ERROR = '#system_messages:vehicle_buy/server_error'
    VEHICLE_BUY_INVALID_VEHICLE = '#system_messages:vehicle_buy/invalid_vehicle'
    VEHICLE_BUY_SERVER_ERROR_CENTERDOWN = '#system_messages:vehicle_buy/server_error_centerDown'
    VEHICLE_BUY_NOT_ENOUGH_CREDITS = '#system_messages:vehicle_buy/not_enough_credits'
    VEHICLE_BUY_NOT_ENOUGH_GOLD = '#system_messages:vehicle_buy/not_enough_gold'
    VEHICLE_BUY_WALLET_NOT_AVAILABLE = '#system_messages:vehicle_buy/wallet_not_available'
    VEHICLE_RENT_SUCCESS = '#system_messages:vehicle_rent/success'
    VEHICLE_RENT_SERVER_ERROR = '#system_messages:vehicle_rent/server_error'
    VEHICLE_RENT_INVALID_VEHICLE = '#system_messages:vehicle_rent/invalid_vehicle'
    VEHICLE_RENT_SERVER_ERROR_CENTERDOWN = '#system_messages:vehicle_rent/server_error_centerDown'
    VEHICLE_RENT_NOT_ENOUGH_CREDITS = '#system_messages:vehicle_rent/not_enough_credits'
    VEHICLE_RENT_NOT_ENOUGH_GOLD = '#system_messages:vehicle_rent/not_enough_gold'
    VEHICLE_RENT_WALLET_NOT_AVAILABLE = '#system_messages:vehicle_rent/wallet_not_available'
    VEHICLE_SLOT_BUY_SUCCESS = '#system_messages:vehicle_slot_buy/success'
    VEHICLE_SLOT_BUY_NOT_ENOUGH_GOLD = '#system_messages:vehicle_slot_buy/not_enough_gold'
    VEHICLE_SLOT_BUY_WALLET_NOT_AVAILABLE = '#system_messages:vehicle_slot_buy/wallet_not_available'
    VEHICLE_SLOT_BUY_SERVER_ERROR = '#system_messages:vehicle_slot_buy/server_error'
    VEHICLE_SELL_SUCCESS = '#system_messages:vehicle_sell/success'
    VEHICLE_SELL_SUCCESS_DISMANTLING = '#system_messages:vehicle_sell/success_dismantling'
    VEHICLE_SELL_SERVER_ERROR = '#system_messages:vehicle_sell/server_error'
    VEHICLE_SELL_INVALID_VEHICLE = '#system_messages:vehicle_sell/invalid_vehicle'
    VEHICLE_SELL_VEHICLE_CANNOT_BE_SOLD = '#system_messages:vehicle_sell/vehicle_cannot_be_sold'
    VEHICLE_SELL_VEHICLE_NEED_REPAIR = '#system_messages:vehicle_sell/vehicle_need_repair'
    VEHICLE_SELL_VEHICLE_LOCKED = '#system_messages:vehicle_sell/vehicle_locked'
    VEHICLE_SELL_NOT_ENOUGH_CREDITS = '#system_messages:vehicle_sell/not_enough_credits'
    VEHICLE_SELL_NOT_ENOUGH_GOLD = '#system_messages:vehicle_sell/not_enough_gold'
    VEHICLE_SELL_WALLET_NOT_AVAILABLE = '#system_messages:vehicle_sell/wallet_not_available'
    VEHICLE_SELL_VEHICLE_SELL_LIMIT = '#system_messages:vehicle_sell/vehicle_sell_limit'
    VEHICLE_SELL_NOT_ENOUGH_SPACE = '#system_messages:vehicle_sell/not_enough_space'
    VEHICLE_REMOVE_SUCCESS = '#system_messages:vehicle_remove/success'
    VEHICLE_REMOVE_SUCCESS_DISMANTLING = '#system_messages:vehicle_remove/success_dismantling'
    VEHICLE_REMOVE_SERVER_ERROR = '#system_messages:vehicle_remove/server_error'
    VEHICLE_REMOVE_INVALID_VEHICLE = '#system_messages:vehicle_remove/invalid_vehicle'
    VEHICLE_REMOVE_VEHICLE_CANNOT_BE_SOLD = '#system_messages:vehicle_remove/vehicle_cannot_be_sold'
    VEHICLE_REMOVE_VEHICLE_NEED_REPAIR = '#system_messages:vehicle_remove/vehicle_need_repair'
    VEHICLE_REMOVE_VEHICLE_LOCKED = '#system_messages:vehicle_remove/vehicle_locked'
    VEHICLE_REMOVE_NOT_ENOUGH_CREDITS = '#system_messages:vehicle_remove/not_enough_credits'
    VEHICLE_REMOVE_NOT_ENOUGH_GOLD = '#system_messages:vehicle_remove/not_enough_gold'
    VEHICLE_REMOVE_WALLET_NOT_AVAILABLE = '#system_messages:vehicle_remove/wallet_not_available'
    VEHICLE_REMOVE_VEHICLE_SELL_LIMIT = '#system_messages:vehicle_remove/vehicle_sell_limit'
    VEHICLE_REMOVE_NOT_ENOUGH_SPACE = '#system_messages:vehicle_remove/not_enough_space'
    VEHICLE_TMENXP_ACCELERATOR_SUCCESSFALSE = '#system_messages:vehicle_tmenxp_accelerator/successFalse'
    VEHICLE_TMENXP_ACCELERATOR_SUCCESSTRUE = '#system_messages:vehicle_tmenxp_accelerator/successTrue'
    VEHICLE_TMENXP_ACCELERATOR_INVALID_VEHICLE = '#system_messages:vehicle_tmenxp_accelerator/invalid_vehicle'
    VEHICLE_TMENXP_ACCELERATOR_VEHICLE_NEED_REPAIR = '#system_messages:vehicle_tmenxp_accelerator/vehicle_need_repair'
    VEHICLE_TMENXP_ACCELERATOR_VEHICLE_LOCKED = '#system_messages:vehicle_tmenxp_accelerator/vehicle_locked'
    VEHICLE_TMENXP_ACCELERATOR_SERVER_ERROR = '#system_messages:vehicle_tmenxp_accelerator/server_error'
    VEHICLE_REPAIR_SUCCESS = '#system_messages:vehicle_repair/success'
    VEHICLE_REPAIR_NOT_ENOUGH_CREDITS = '#system_messages:vehicle_repair/not_enough_credits'
    VEHICLE_REPAIR_SERVER_ERROR = '#system_messages:vehicle_repair/server_error'
    BUY_TANKMEN_BERTHS_SUCCESS = '#system_messages:buy_tankmen_berths/success'
    BUY_TANKMEN_BERTHS_SERVER_ERROR = '#system_messages:buy_tankmen_berths/server_error'
    BUY_TANKMEN_BERTHS_NOT_ENOUGH_CREDITS = '#system_messages:buy_tankmen_berths/not_enough_credits'
    BUY_TANKMEN_BERTHS_NOT_ENOUGH_GOLD = '#system_messages:buy_tankmen_berths/not_enough_gold'
    BUY_TANKMEN_BERTHS_WALLET_NOT_AVAILABLE = '#system_messages:buy_tankmen_berths/wallet_not_available'
    SHELL_BUY_SUCCESS = '#system_messages:shell_buy/success'
    SHELL_BUY_INVALID_MODULE = '#system_messages:shell_buy/invalid_module'
    SHELL_BUY_NOT_ENOUGH_CREDITS = '#system_messages:shell_buy/not_enough_credits'
    SHELL_BUY_NOT_ENOUGH_GOLD = '#system_messages:shell_buy/not_enough_gold'
    SHELL_BUY_WALLET_NOT_AVAILABLE = '#system_messages:shell_buy/wallet_not_available'
    SHELL_BUY_SERVER_ERROR = '#system_messages:shell_buy/server_error'
    SHELL_BUY_SERVER_ERROR_CENTERDOWN = '#system_messages:shell_buy/server_error_centerDown'
    MODULE_BUY_SUCCESS = '#system_messages:module_buy/success'
    MODULE_BUY_INVALID_MODULE = '#system_messages:module_buy/invalid_module'
    MODULE_BUY_NOT_ENOUGH_CREDITS = '#system_messages:module_buy/not_enough_credits'
    MODULE_BUY_NOT_ENOUGH_GOLD = '#system_messages:module_buy/not_enough_gold'
    MODULE_BUY_WALLET_NOT_AVAILABLE = '#system_messages:module_buy/wallet_not_available'
    MODULE_BUY_SERVER_ERROR = '#system_messages:module_buy/server_error'
    MODULE_BUY_SERVER_ERROR_CENTERDOWN = '#system_messages:module_buy/server_error_centerDown'
    MODULE_BUY_VEHICLE_NEED_REPAIR = '#system_messages:module_buy/vehicle_need_repair'
    MODULE_BUY_VEHICLE_LOCKED = '#system_messages:module_buy/vehicle_locked'
    MODULE_BUY_INVALID_VEHICLE = '#system_messages:module_buy/invalid_vehicle'
    MODULE_BUY_ERROR_WRONG_NATION = '#system_messages:module_buy/error_wrong_nation'
    MODULE_BUY_ERROR_NOT_FOR_THIS_VEHICLE_TYPE = '#system_messages:module_buy/error_not_for_this_vehicle_type'
    MODULE_BUY_ERROR_NOT_FOR_CURRENT_VEHICLE = '#system_messages:module_buy/error_not_for_current_vehicle'
    MODULE_BUY_ERROR_NO_GUN = '#system_messages:module_buy/error_no_gun'
    MODULE_BUY_ERROR_WRONG_ITEM_TYPE = '#system_messages:module_buy/error_wrong_item_type'
    MODULE_BUY_ERROR_TOO_HEAVY = '#system_messages:module_buy/error_too_heavy'
    MODULE_BUY_ERROR_TOO_HEAVY_CHASSIS = '#system_messages:module_buy/error_too_heavy_chassis'
    MODULE_BUY_ERROR_NEED_TURRET = '#system_messages:module_buy/error_need_turret'
    MODULE_BUY_ERROR_NEED_GUN = '#system_messages:module_buy/error_need_gun'
    MODULE_BUY_ERROR_IS_CURRENT = '#system_messages:module_buy/error_is_current'
    MODULE_BUY_ERROR_NOT_WITH_INSTALLED_EQUIPMENT = '#system_messages:module_buy/error_not_with_installed_equipment'
    ARTEFACT_BUY_SUCCESS = '#system_messages:artefact_buy/success'
    ARTEFACT_BUY_INVALID_MODULE = '#system_messages:artefact_buy/invalid_module'
    ARTEFACT_BUY_NOT_ENOUGH_CREDITS = '#system_messages:artefact_buy/not_enough_credits'
    ARTEFACT_BUY_NOT_ENOUGH_GOLD = '#system_messages:artefact_buy/not_enough_gold'
    ARTEFACT_BUY_WALLET_NOT_AVAILABLE = '#system_messages:artefact_buy/wallet_not_available'
    ARTEFACT_BUY_SERVER_ERROR = '#system_messages:artefact_buy/server_error'
    ARTEFACT_BUY_SERVER_ERROR_CENTERDOWN = '#system_messages:artefact_buy/server_error_centerDown'
    ARTEFACT_BUY_ERROR_TOO_HEAVY = '#system_messages:artefact_buy/error_too_heavy'
    ARTEFACT_BUY_VEHICLE_NEED_REPAIR = '#system_messages:artefact_buy/vehicle_need_repair'
    ARTEFACT_BUY_VEHICLE_LOCKED = '#system_messages:artefact_buy/vehicle_locked'
    ARTEFACT_BUY_INVALID_VEHICLE = '#system_messages:artefact_buy/invalid_vehicle'
    ARTEFACT_BUY_ERROR_NOT_FOR_THIS_VEHICLE_TYPE = '#system_messages:artefact_buy/error_not_for_this_vehicle_type'
    SHELL_SELL_SUCCESS = '#system_messages:shell_sell/success'
    SHELL_SELL_INVALID_MODULE = '#system_messages:shell_sell/invalid_module'
    SHELL_SELL_SERVER_ERROR = '#system_messages:shell_sell/server_error'
    MODULE_SELL_SUCCESS = '#system_messages:module_sell/success'
    MODULE_SELL_INVALID_MODULE = '#system_messages:module_sell/invalid_module'
    MODULE_SELL_SERVER_ERROR = '#system_messages:module_sell/server_error'
    ARTEFACT_SELL_SUCCESS = '#system_messages:artefact_sell/success'
    ARTEFACT_SELL_INVALID_MODULE = '#system_messages:artefact_sell/invalid_module'
    ARTEFACT_SELL_SERVER_ERROR = '#system_messages:artefact_sell/server_error'
    MODULE_APPLY_SUCCESS = '#system_messages:module_apply/success'
    MODULE_APPLY_SUCCESS_GUN_CHANGE = '#system_messages:module_apply/success_gun_change'
    MODULE_APPLY_SERVER_ERROR = '#system_messages:module_apply/server_error'
    MODULE_APPLY_INVALID_VEHICLE = '#system_messages:module_apply/invalid_vehicle'
    MODULE_APPLY_VEHICLE_LOCKED = '#system_messages:module_apply/vehicle_locked'
    MODULE_APPLY_VEHICLE_NEED_REPAIR = '#system_messages:module_apply/vehicle_need_repair'
    MODULE_APPLY_ERROR_WRONG_NATION = '#system_messages:module_apply/error_wrong_nation'
    MODULE_APPLY_ERROR_NOT_FOR_THIS_VEHICLE_TYPE = '#system_messages:module_apply/error_not_for_this_vehicle_type'
    MODULE_APPLY_ERROR_NOT_FOR_CURRENT_VEHICLE = '#system_messages:module_apply/error_not_for_current_vehicle'
    MODULE_APPLY_ERROR_NO_GUN = '#system_messages:module_apply/error_no_gun'
    MODULE_APPLY_ERROR_WRONG_ITEM_TYPE = '#system_messages:module_apply/error_wrong_item_type'
    MODULE_APPLY_ERROR_TOO_HEAVY = '#system_messages:module_apply/error_too_heavy'
    MODULE_APPLY_ERROR_TOO_HEAVY_CHASSIS = '#system_messages:module_apply/error_too_heavy_chassis'
    MODULE_APPLY_ERROR_NEED_TURRET = '#system_messages:module_apply/error_need_turret'
    MODULE_APPLY_ERROR_NEED_GUN = '#system_messages:module_apply/error_need_gun'
    MODULE_APPLY_ERROR_IS_CURRENT = '#system_messages:module_apply/error_is_current'
    MODULE_APPLY_ERROR_NOT_WITH_INSTALLED_EQUIPMENT = '#system_messages:module_apply/error_not_with_installed_equipment'
    MODULE_APPLY_INCOMPATIBLEEQS = '#system_messages:module_apply/incompatibleEqs'
    ARTEFACT_APPLY_SUCCESS = '#system_messages:artefact_apply/success'
    ARTEFACT_APPLY_GOLD_SUCCESS = '#system_messages:artefact_apply/gold_success'
    ARTEFACT_APPLY_GOLD_ERROR_NOT_ENOUGH = '#system_messages:artefact_apply/gold_error_not_enough'
    ARTEFACT_REMOVE_SUCCESS = '#system_messages:artefact_remove/success'
    ARTEFACT_REMOVE_GOLD_SUCCESS = '#system_messages:artefact_remove/gold_success'
    ARTEFACT_REMOVE_GOLD_ERROR_NOT_ENOUGH = '#system_messages:artefact_remove/gold_error_not_enough'
    ARTEFACT_REMOVE_INCOMPATIBLEEQS = '#system_messages:artefact_remove/incompatibleEqs'
    ARTEFACT_DESTROY_SUCCESS = '#system_messages:artefact_destroy/success'
    ARTEFACT_APPLY_SERVER_ERROR = '#system_messages:artefact_apply/server_error'
    ARTEFACT_REMOVE_SERVER_ERROR = '#system_messages:artefact_remove/server_error'
    ARTEFACT_DESTROY_SERVER_ERROR = '#system_messages:artefact_destroy/server_error'
    ARTEFACT_APPLY_INVALID_VEHICLE = '#system_messages:artefact_apply/invalid_vehicle'
    ARTEFACT_APPLY_VEHICLE_LOCKED = '#system_messages:artefact_apply/vehicle_locked'
    ARTEFACT_APPLY_VEHICLE_NEED_REPAIR = '#system_messages:artefact_apply/vehicle_need_repair'
    ARTEFACT_REMOVE_INVALID_VEHICLE = '#system_messages:artefact_remove/invalid_vehicle'
    ARTEFACT_REMOVE_VEHICLE_LOCKED = '#system_messages:artefact_remove/vehicle_locked'
    ARTEFACT_REMOVE_VEHICLE_NEED_REPAIR = '#system_messages:artefact_remove/vehicle_need_repair'
    ARTEFACT_DESTROY_INVALID_VEHICLE = '#system_messages:artefact_destroy/invalid_vehicle'
    ARTEFACT_DESTROY_VEHICLE_LOCKED = '#system_messages:artefact_destroy/vehicle_locked'
    ARTEFACT_DESTROY_VEHICLE_NEED_REPAIR = '#system_messages:artefact_destroy/vehicle_need_repair'
    ARTEFACT_APPLY_ERROR_NOT_FOR_THIS_VEHICLE_TYPE = '#system_messages:artefact_apply/error_not_for_this_vehicle_type'
    ARTEFACT_APPLY_ERROR_TOO_HEAVY = '#system_messages:artefact_apply/error_too_heavy'
    ARTEFACT_REMOVE_ERROR_TOO_HEAVY = '#system_messages:artefact_remove/error_too_heavy'
    LAYOUT_APPLY_SUCCESS_MONEY_SPENT = '#system_messages:layout_apply/success_money_spent'
    LAYOUT_APPLY_SERVER_ERROR = '#system_messages:layout_apply/server_error'
    LAYOUT_APPLY_WRONG_ARGS_TYPE = '#system_messages:layout_apply/WRONG_ARGS_TYPE'
    LAYOUT_APPLY_SHOP_DESYNC = '#system_messages:layout_apply/SHOP_DESYNC'
    LAYOUT_APPLY_WRONG_ARG_VALUE = '#system_messages:layout_apply/WRONG_ARG_VALUE'
    LAYOUT_APPLY_SHELLS_NO_CREDITS = '#system_messages:layout_apply/SHELLS_NO_CREDITS'
    LAYOUT_APPLY_SHELLS_NO_GOLD = '#system_messages:layout_apply/SHELLS_NO_GOLD'
    LAYOUT_APPLY_SHELLS_NO_WALLET_SESSION = '#system_messages:layout_apply/SHELLS_NO_WALLET_SESSION'
    LAYOUT_APPLY_EQS_NO_CREDITS = '#system_messages:layout_apply/EQS_NO_CREDITS'
    LAYOUT_APPLY_EQS_NO_GOLD = '#system_messages:layout_apply/EQS_NO_GOLD'
    LAYOUT_APPLY_EQS_NO_WALLET_SESSION = '#system_messages:layout_apply/EQS_NO_WALLET_SESSION'
    LAYOUT_APPLY_NOT_RESEARCHED_ITEM = '#system_messages:layout_apply/NOT_RESEARCHED_ITEM'
    LAYOUT_APPLY_BUYING_GOLD_EQS_FOR_CREDITS_DISABLED = '#system_messages:layout_apply/BUYING_GOLD_EQS_FOR_CREDITS_DISABLED'
    LAYOUT_APPLY_BUYING_GOLD_SHELLS_FOR_CREDITS_DISABLED = '#system_messages:layout_apply/BUYING_GOLD_SHELLS_FOR_CREDITS_DISABLED'
    LAYOUT_APPLY_NO_VEHICLE_WITH_GIVEN_ID = '#system_messages:layout_apply/No vehicle with given id'
    LAYOUT_APPLY_VEHICLE_IS_LOCKED = '#system_messages:layout_apply/Vehicle is locked'
    LAYOUT_APPLY_CANNOT_EQUIP_SHELLS = '#system_messages:layout_apply/Cannot equip shells'
    LAYOUT_APPLY_CANNOT_EQUIP_SHELLS__MAXAMMO_LIMIT_EXCEEDED_ = '#system_messages:layout_apply/Cannot equip shells (maxAmmo limit exceeded)'
    LAYOUT_APPLY_CANNOT_EQUIP_EQUIPMENT = '#system_messages:layout_apply/Cannot equip equipment'
    LAYOUT_APPLY_COMPONENT_IS_NOT_IN_SHOP = '#system_messages:layout_apply/Component is not in shop'
    LAYOUT_APPLY_WALLET_NOT_AVAILABLE = '#system_messages:layout_apply/wallet_not_available'
    LAYOUT_APPLY_INVALID_VEHICLE = '#system_messages:layout_apply/invalid_vehicle'
    LAYOUT_APPLY_VEHICLE_LOCKED = '#system_messages:layout_apply/vehicle_locked'
    REQUEST_ISINCOOLDOWN = '#system_messages:request/isInCoolDown'
    PREBATTLE_REQUEST_NAME_CHANGE_SETTINGS = '#system_messages:prebattle/request/name/CHANGE_SETTINGS'
    PREBATTLE_REQUEST_NAME_CHANGE_ARENA_VOIP = '#system_messages:prebattle/request/name/CHANGE_ARENA_VOIP'
    PREBATTLE_REQUEST_NAME_CHANGE_USER_STATUS = '#system_messages:prebattle/request/name/CHANGE_USER_STATUS'
    PREBATTLE_REQUEST_NAME_SWAP_TEAMS = '#system_messages:prebattle/request/name/SWAP_TEAMS'
    PREBATTLE_REQUEST_NAME_SET_TEAM_STATE = '#system_messages:prebattle/request/name/SET_TEAM_STATE'
    PREBATTLE_REQUEST_NAME_SET_PLAYER_STATE = '#system_messages:prebattle/request/name/SET_PLAYER_STATE'
    PREBATTLE_REQUEST_NAME_SEND_INVITE = '#system_messages:prebattle/request/name/SEND_INVITE'
    PREBATTLE_REQUEST_NAME_PREBATTLES_LIST = '#system_messages:prebattle/request/name/PREBATTLES_LIST'
    PREBATTLE_REQUEST_NAME_CHANGE_UNIT_STATE = '#system_messages:prebattle/request/name/CHANGE_UNIT_STATE'
    PREBATTLE_REQUEST_NAME_UNITS_LIST = '#system_messages:prebattle/request/name/UNITS_LIST'
    PREBATTLE_REQUEST_NAME_CLOSE_SLOT = '#system_messages:prebattle/request/name/CLOSE_SLOT'
    PREBATTLE_REQUEST_NAME_CHANGE_RATED = '#system_messages:prebattle/request/name/CHANGE_RATED'
    PREBATTLE_REQUEST_NAME_CHANGE_DIVISION = '#system_messages:prebattle/request/name/CHANGE_DIVISION'
    PREBATTLE_REQUEST_NAME_SET_ES_VEHICLE_LIST = '#system_messages:prebattle/request/name/SET_ES_VEHICLE_LIST'
    PREBATTLE_REQUEST_NAME_CHANGE_ES_TYPE = '#system_messages:prebattle/request/name/CHANGE_ES_TYPE'
    FORTIFICATION_REQUEST_NAME_CREATE_FORT = '#system_messages:fortification/request/name/CREATE_FORT'
    FORTIFICATION_REQUEST_NAME_DELETE_FORT = '#system_messages:fortification/request/name/DELETE_FORT'
    FORTIFICATION_REQUEST_NAME_OPEN_DIRECTION = '#system_messages:fortification/request/name/OPEN_DIRECTION'
    FORTIFICATION_REQUEST_NAME_CLOSE_DIRECTION = '#system_messages:fortification/request/name/CLOSE_DIRECTION'
    FORTIFICATION_REQUEST_NAME_ADD_BUILDING = '#system_messages:fortification/request/name/ADD_BUILDING'
    FORTIFICATION_REQUEST_NAME_DELETE_BUILDING = '#system_messages:fortification/request/name/DELETE_BUILDING'
    FORTIFICATION_REQUEST_NAME_TRANSPORTATION = '#system_messages:fortification/request/name/TRANSPORTATION'
    FORTIFICATION_REQUEST_NAME_ADD_ORDER = '#system_messages:fortification/request/name/ADD_ORDER'
    FORTIFICATION_REQUEST_NAME_ACTIVATE_ORDER = '#system_messages:fortification/request/name/ACTIVATE_ORDER'
    FORTIFICATION_REQUEST_NAME_ATTACH = '#system_messages:fortification/request/name/ATTACH'
    FORTIFICATION_REQUEST_NAME_UPGRADE = '#system_messages:fortification/request/name/UPGRADE'
    FORTIFICATION_REQUEST_NAME_CREATE_SORTIE = '#system_messages:fortification/request/name/CREATE_SORTIE'
    FORTIFICATION_REQUEST_NAME_REQUEST_SORTIE_UNIT = '#system_messages:fortification/request/name/REQUEST_SORTIE_UNIT'
    FORTIFICATION_REQUEST_NAME_CHANGE_DEF_HOUR = '#system_messages:fortification/request/name/CHANGE_DEF_HOUR'
    FORTIFICATION_REQUEST_NAME_CHANGE_OFF_DAY = '#system_messages:fortification/request/name/CHANGE_OFF_DAY'
    FORTIFICATION_REQUEST_NAME_CHANGE_PERIPHERY = '#system_messages:fortification/request/name/CHANGE_PERIPHERY'
    FORTIFICATION_REQUEST_NAME_CHANGE_VACATION = '#system_messages:fortification/request/name/CHANGE_VACATION'
    FORTIFICATION_REQUEST_NAME_CHANGE_SETTINGS = '#system_messages:fortification/request/name/CHANGE_SETTINGS'
    FORTIFICATION_REQUEST_NAME_SHUTDOWN_DEF_HOUR = '#system_messages:fortification/request/name/SHUTDOWN_DEF_HOUR'
    FORTIFICATION_REQUEST_NAME_CANCEL_SHUTDOWN_DEF_HOUR = '#system_messages:fortification/request/name/CANCEL_SHUTDOWN_DEF_HOUR'
    FORTIFICATION_REQUEST_NAME_REQUEST_PUBLIC_INFO = '#system_messages:fortification/request/name/REQUEST_PUBLIC_INFO'
    FORTIFICATION_REQUEST_NAME_REQUEST_CLAN_CARD = '#system_messages:fortification/request/name/REQUEST_CLAN_CARD'
    FORTIFICATION_REQUEST_NAME_ADD_FAVORITE = '#system_messages:fortification/request/name/ADD_FAVORITE'
    FORTIFICATION_REQUEST_NAME_REMOVE_FAVORITE = '#system_messages:fortification/request/name/REMOVE_FAVORITE'
    FORTIFICATION_REQUEST_NAME_PLAN_ATTACK = '#system_messages:fortification/request/name/PLAN_ATTACK'
    CLUB_REQUEST_NAME_SUBSCRIBE = '#system_messages:club/request/name/SUBSCRIBE'
    CLUB_REQUEST_NAME_UNSUBSCRIBE = '#system_messages:club/request/name/UNSUBSCRIBE'
    CLUB_REQUEST_NAME_CREATE_CLUB = '#system_messages:club/request/name/CREATE_CLUB'
    CLUB_REQUEST_NAME_GET_MY_CLUBS = '#system_messages:club/request/name/GET_MY_CLUBS'
    CLUB_REQUEST_NAME_GET_MY_CLUBS_HISTORY = '#system_messages:club/request/name/GET_MY_CLUBS_HISTORY'
    CLUB_REQUEST_NAME_DESTROY_CLUB = '#system_messages:club/request/name/DESTROY_CLUB'
    CLUB_REQUEST_NAME_LEAVE_CLUB = '#system_messages:club/request/name/LEAVE_CLUB'
    CLUB_REQUEST_NAME_GET_CLUB = '#system_messages:club/request/name/GET_CLUB'
    CLUB_REQUEST_NAME_OPEN_CLUB = '#system_messages:club/request/name/OPEN_CLUB'
    CLUB_REQUEST_NAME_CLOSE_CLUB = '#system_messages:club/request/name/CLOSE_CLUB'
    CLUB_REQUEST_NAME_GET_CLUBS = '#system_messages:club/request/name/GET_CLUBS'
    CLUB_REQUEST_NAME_CHANGE_CLUB_NAME = '#system_messages:club/request/name/CHANGE_CLUB_NAME'
    CLUB_REQUEST_NAME_CHANGE_CLUB_EMBLEM = '#system_messages:club/request/name/CHANGE_CLUB_EMBLEM'
    CLUB_REQUEST_NAME_SEND_INVITE = '#system_messages:club/request/name/SEND_INVITE'
    CLUB_REQUEST_NAME_REVOKE_INVITE = '#system_messages:club/request/name/REVOKE_INVITE'
    CLUB_REQUEST_NAME_ACCEPT_INVITE = '#system_messages:club/request/name/ACCEPT_INVITE'
    CLUB_REQUEST_NAME_DECLINE_INVITE = '#system_messages:club/request/name/DECLINE_INVITE'
    CLUB_REQUEST_NAME_SEND_APPLICATION = '#system_messages:club/request/name/SEND_APPLICATION'
    CLUB_REQUEST_NAME_REVOKE_APPLICATION = '#system_messages:club/request/name/REVOKE_APPLICATION'
    CLUB_REQUEST_NAME_ACCEPT_APPLICATION = '#system_messages:club/request/name/ACCEPT_APPLICATION'
    CLUB_REQUEST_NAME_DECLINE_APPLICATION = '#system_messages:club/request/name/DECLINE_APPLICATION'
    CLUB_REQUEST_NAME_JOIN_UNIT = '#system_messages:club/request/name/JOIN_UNIT'
    CLUB_REQUEST_NAME_GET_APPLICATIONS = '#system_messages:club/request/name/GET_APPLICATIONS'
    CLUB_REQUEST_NAME_GET_CLUB_APPLICANTS = '#system_messages:club/request/name/GET_CLUB_APPLICANTS'
    CLUB_REQUEST_NAME_GET_INVITES = '#system_messages:club/request/name/GET_INVITES'
    CLUB_REQUEST_NAME_TRANSFER_OWNERSHIP = '#system_messages:club/request/name/TRANSFER_OWNERSHIP'
    CLUB_REQUEST_NAME_ASSIGN_OFFICER = '#system_messages:club/request/name/ASSIGN_OFFICER'
    CLUB_REQUEST_NAME_ASSIGN_PRIVATE = '#system_messages:club/request/name/ASSIGN_PRIVATE'
    CLUB_REQUEST_NAME_KICK_MEMBER = '#system_messages:club/request/name/KICK_MEMBER'
    CLUB_REQUEST_NAME_SET_APPLICANT_REQUIREMENTS = '#system_messages:club/request/name/SET_APPLICANT_REQUIREMENTS'
    CLUBS_REQUEST_SUCCESS_APPLICATION_SENT = '#system_messages:clubs/request/success/application/sent'
    CLUBS_REQUEST_SUCCESS_APPLICATION_REVOKE = '#system_messages:clubs/request/success/application/revoke'
    CLUBS_REQUEST_SUCCESS_APPLICATION_ACCEPT = '#system_messages:clubs/request/success/application/accept'
    CLUBS_REQUEST_SUCCESS_APPLICATION_DECLINE = '#system_messages:clubs/request/success/application/decline'
    CLUBS_REQUEST_SUCCESS_INVITE_SENT = '#system_messages:clubs/request/success/invite/sent'
    CLUBS_REQUEST_SUCCESS_INVITES_SENT = '#system_messages:clubs/request/success/invites/sent'
    CLUBS_REQUEST_SUCCESS_INVITES_SENT_NAMES_SUCCESS = '#system_messages:clubs/request/success/invites/sent/names/success'
    CLUBS_REQUEST_SUCCESS_INVITES_SENT_NAMES_ERROR = '#system_messages:clubs/request/success/invites/sent/names/error'
    CLUBS_REQUEST_SUCCESS_INVITE_REVOKE = '#system_messages:clubs/request/success/invite/revoke'
    CLUBS_REQUEST_SUCCESS_CREATECLUB = '#system_messages:clubs/request/success/createClub'
    CLUBS_REQUEST_SUCCESS_LEAVECLUB = '#system_messages:clubs/request/success/leaveClub'
    CLUBS_REQUEST_SUCCESS_DESTROYCLUB = '#system_messages:clubs/request/success/destroyClub'
    CLUBS_REQUEST_SUCCESS_OPENCLUB = '#system_messages:clubs/request/success/openClub'
    CLUBS_REQUEST_SUCCESS_CLOSECLUB = '#system_messages:clubs/request/success/closeClub'
    CLUBS_REQUEST_SUCCESS_USERS_ASSIGNPRIVATE = '#system_messages:clubs/request/success/users/assignPrivate'
    CLUBS_REQUEST_SUCCESS_USERS_ASSIGNOFFICER = '#system_messages:clubs/request/success/users/assignOfficer'
    CLUBS_REQUEST_SUCCESS_USERS_TRANSFEROWNERSHIP = '#system_messages:clubs/request/success/users/transferOwnership'
    CLUBS_REQUEST_SUCCESS_USERS_KICK = '#system_messages:clubs/request/success/users/kick'
    CLUBS_REQUEST_ERRORS_DEFAULT = '#system_messages:clubs/request/errors/default'
    CLUBS_REQUEST_ERRORS_SOME_ERROR_ON_ESTB_SIDE__SEE_SERVER_LOG_FOR_DETAILS_ = '#system_messages:clubs/request/errors/Some error on estb side. See server log for details.'
    CLUBS_REQUEST_ERRORS_ACCOUNT_ALREADY_OWNS_THE_CLUB_ = '#system_messages:clubs/request/errors/Account already owns the club.'
    CLUBS_REQUEST_ERRORS_ACCOUNT_ALREADY_A_CLUB_MEMBER_ = '#system_messages:clubs/request/errors/Account already a club member.'
    CLUBS_REQUEST_ERRORS_NO_CLUB_FOUND_ = '#system_messages:clubs/request/errors/No club found.'
    CLUBS_REQUEST_ERRORS_ACCOUNT_NOT_A_CLUB_MEMBER_ = '#system_messages:clubs/request/errors/Account not a club member.'
    CLUBS_REQUEST_ERRORS_FORBIDDEN_OPERATION_FOR_NON_EMPTY_CLUB_ = '#system_messages:clubs/request/errors/Forbidden operation for non-empty club.'
    CLUBS_REQUEST_ERRORS_THIS_OPERATION_IS_FORBIDDEN_FOR_CLUB_OWNER_ = '#system_messages:clubs/request/errors/This operation is forbidden for club owner.'
    CLUBS_REQUEST_ERRORS_FORBIDDEN_OPERATION_BECAUSE_APPLICANTS_LIMIT_REACHED_ = '#system_messages:clubs/request/errors/Forbidden operation because applicants limit reached.'
    CLUBS_REQUEST_ERRORS_FORBIDDEN_OPERATION_BECAUSE_MEMBERS_LIMIT_REACHED_ = '#system_messages:clubs/request/errors/Forbidden operation because members limit reached.'
    CLUBS_REQUEST_ERRORS_INVITE_TO_THE_CLUB_ALREADY_SENT_TO_THIS_PLAYER_ = '#system_messages:clubs/request/errors/Invite to the club already sent to this player.'
    CLUBS_REQUEST_ERRORS_INVITE_TO_THE_CLUB_NOT_FOUND_FOR_THIS_PLAYER_ = '#system_messages:clubs/request/errors/Invite to the club not found for this player.'
    CLUBS_REQUEST_ERRORS_ACCOUNT_NOT_A_CLUB_APPLICANT_ = '#system_messages:clubs/request/errors/Account not a club applicant.'
    CLUBS_REQUEST_ERRORS_INCORRECT_PARAMS_PASSED_TO_THE_HANDLER_ = '#system_messages:clubs/request/errors/Incorrect params passed to the handler.'
    CLUBS_REQUEST_ERRORS_HANDLER_RESPONSE_NOT_REGISTERED_ = '#system_messages:clubs/request/errors/Handler response not registered.'
    CLUBS_REQUEST_ERRORS_APPLICATIONS_TO_THE_CLOSED_CLUB_ARE_FORBIDDEN_ = '#system_messages:clubs/request/errors/Applications to the closed club are forbidden.'
    CLUBS_REQUEST_ERRORS_NONE_OF_THE_SUB_REQUESTS_WAS_NOT_COMPLETED_SUCCESSFULLY_ = '#system_messages:clubs/request/errors/None of the sub-requests was not completed successfully.'
    CLUBS_REQUEST_ERRORS_THIS_EMBLEM_NOT_REGISTERED_IN_EMULATOR_ = '#system_messages:clubs/request/errors/This emblem not registered in emulator.'
    CLUBS_REQUEST_ERRORS_COMMAND_FAILED_BY_TIMEOUT_ = '#system_messages:clubs/request/errors/Command failed by timeout.'
    CLUBS_REQUEST_ERRORS_UNKNOWN_OR_UNEXPECTED_ERROR_ = '#system_messages:clubs/request/errors/Unknown or unexpected error.'
    CLUBS_REQUEST_ERRORS_ACCOUNT_NOT_FOUND_FOR_GIVEN_ID_ = '#system_messages:clubs/request/errors/Account not found for given ID.'
    CLUBS_REQUEST_ERRORS_ACCOUNT_FOR_GIVEN_ID_IS_BANNED_ = '#system_messages:clubs/request/errors/Account for given ID is banned.'
    CLUBS_REQUEST_ERRORS_INTERNAL_ERROR_IN_SPA__ = '#system_messages:clubs/request/errors/Internal error in SPA .'
    CLUBS_REQUEST_ERRORS_FORBIDDEN_OPERATION_FOR_THIS_ACCOUNT_ = '#system_messages:clubs/request/errors/Forbidden operation for this account.'
    CLUBS_REQUEST_ERRORS_INACTIVE_CLUB_ = '#system_messages:clubs/request/errors/Inactive club.'
    CLUBS_REQUEST_ERRORS_INACTIVE_APPLICATION_ = '#system_messages:clubs/request/errors/Inactive application.'
    CLUBS_REQUEST_ERRORS_INACTIVE_INVITE_ = '#system_messages:clubs/request/errors/Inactive invite.'
    CLUBS_REQUEST_ERRORS_TOO_MANY_REQUESTS_ARE_IN_THE_PENDING_STATE_ = '#system_messages:clubs/request/errors/Too many requests are in the pending state.'
    CLUBS_REQUEST_ERRORS_TOO_MANY_INVITES_SENT_TO_THAT_PLAYER_ = '#system_messages:clubs/request/errors/Too many invites sent to that player.'
    CLUBS_REQUEST_ERRORS_THIS_CLUB_NAME_IS_ALREADY_TAKEN_ = '#system_messages:clubs/request/errors/This club name is already taken.'
    CLUBS_REQUEST_ERRORS_INCORRECT_CHECKOUT_TOKEN_ = '#system_messages:clubs/request/errors/Incorrect checkout token.'
    CLUBS_REQUEST_ERRORS_CLUB_IS_LOCKED_ = '#system_messages:clubs/request/errors/Club is locked.'
    CLUBS_REQUEST_ERRORS_ATTEMPT_TO_ACCESS_TO_THE_INCORRECT_URL_ = '#system_messages:clubs/request/errors/Attempt to access to the incorrect url.'
    CLUBS_REQUEST_ERRORS_APPLICATION_FROM_THIS_ACCOUNT_ALREADY_EXISTS_ = '#system_messages:clubs/request/errors/Application from this account already exists.'
    CLUBS_REQUEST_ERRORS_WRONG_OBTAINED_WEB_DATA_FORMAT__PLEASE_SEE_SERVER_LOGS_ = '#system_messages:clubs/request/errors/Wrong obtained web data format. Please see server logs.'
    CLUBS_REQUEST_ERRORS_THIS_OPERATION_IS_RESTRICTED_ON_WEB_SIDE_ = '#system_messages:clubs/request/errors/This operation is restricted on web side.'
    CLUBS_REQUEST_ERRORS_WEB_API_IS_NOT_AVAILABLE_AT_THIS_MOMENT_ = '#system_messages:clubs/request/errors/Web API is not available at this moment.'
    CLUBS_REQUEST_ERRORS_THIS_CLUB_IS_NOT_IN_THE_LADDER_ = '#system_messages:clubs/request/errors/This club is not in the ladder.'
    CLUBS_REQUEST_ERRORS_UNITMGR_NOT_AVAILABLE = '#system_messages:clubs/request/errors/UnitMgr not available'
    CLUBS_REQUEST_ERRORS_TEAM_DOES_NOT_EXIST = '#system_messages:clubs/request/errors/TEAM_DOES_NOT_EXIST'
    CLUBS_REQUEST_ERRORS_TEAM_IS_FULL = '#system_messages:clubs/request/errors/TEAM_IS_FULL'
    CLUBS_REQUEST_ERRORS_TEAM_IS_NOT_ACTIVE = '#system_messages:clubs/request/errors/TEAM_IS_NOT_ACTIVE'
    CLUBS_REQUEST_ERRORS_TEAM_ALREADY_EXIST = '#system_messages:clubs/request/errors/TEAM_ALREADY_EXIST'
    CLUBS_REQUEST_ERRORS_TEAM_MEMBERS_COUNT_ERROR = '#system_messages:clubs/request/errors/TEAM_MEMBERS_COUNT_ERROR'
    CLUBS_REQUEST_ERRORS_TEAM_DOES_NOT_HAVE_OWNER = '#system_messages:clubs/request/errors/TEAM_DOES_NOT_HAVE_OWNER'
    CLUBS_REQUEST_ERRORS_TEAM_DOSSIER_WAS_LOCKED = '#system_messages:clubs/request/errors/TEAM_DOSSIER_WAS_LOCKED'
    CLUBS_REQUEST_ERRORS_TEAM_ALREADY_UNLOCKED = '#system_messages:clubs/request/errors/TEAM_ALREADY_UNLOCKED'
    CLUBS_REQUEST_ERRORS_TEAM_LOCK_TOKEN_ERROR = '#system_messages:clubs/request/errors/TEAM_LOCK_TOKEN_ERROR'
    CLUBS_REQUEST_ERRORS_EMBLEM_DOES_NOT_EXIST = '#system_messages:clubs/request/errors/EMBLEM_DOES_NOT_EXIST'
    CLUBS_REQUEST_ERRORS_WGESTB_COOLDOWN = '#system_messages:clubs/request/errors/WGESTB_COOLDOWN'
    CLUBS_REQUEST_ERRORS_CHANGE_TEAM_NAME_COOLDOWN = '#system_messages:clubs/request/errors/CHANGE_TEAM_NAME_COOLDOWN'
    CLUBS_REQUEST_ERRORS_CHANGE_TEAM_TAG_COOLDOWN = '#system_messages:clubs/request/errors/CHANGE_TEAM_TAG_COOLDOWN'
    CLUBS_REQUEST_ERRORS_TEAM_LEAVE_COOLDOWN = '#system_messages:clubs/request/errors/TEAM_LEAVE_COOLDOWN'
    CLUBS_REQUEST_ERRORS_CANCEL_APPLICATION_COOLDOWN = '#system_messages:clubs/request/errors/CANCEL_APPLICATION_COOLDOWN'
    CLUBS_REQUEST_ERRORS_CREATE_TEAM_AFTER_LEAVE_COOLDOWN = '#system_messages:clubs/request/errors/CREATE_TEAM_AFTER_LEAVE_COOLDOWN'
    CLUBS_REQUEST_ERRORS_CREATE_TEAM_AFTER_DEACTIVATION_COOLDOWN = '#system_messages:clubs/request/errors/CREATE_TEAM_AFTER_DEACTIVATION_COOLDOWN'
    CLUBS_REQUEST_ERRORS_JOIN_TEAM_AFTER_DEACTIVATION_COOLDOWN = '#system_messages:clubs/request/errors/JOIN_TEAM_AFTER_DEACTIVATION_COOLDOWN'
    CLUBS_REQUEST_ERRORS_SAME_TEAM_APPLICATION_COOLDOWN = '#system_messages:clubs/request/errors/SAME_TEAM_APPLICATION_COOLDOWN'
    CLUBS_REQUEST_ERRORS_MEMBERSHIP_APPLICATION_NOT_NEEDED = '#system_messages:clubs/request/errors/MEMBERSHIP_APPLICATION_NOT_NEEDED'
    CLUBS_REQUEST_ERRORS_APPLICATION_FOR_USER_EXCEEDED = '#system_messages:clubs/request/errors/APPLICATION_FOR_USER_EXCEEDED'
    CLUBS_REQUEST_ERRORS_ACCOUNT_BANNED = '#system_messages:clubs/request/errors/ACCOUNT_BANNED'
    CLUBS_REQUEST_ERRORS_ACCOUNT_NOT_IN_TEAM = '#system_messages:clubs/request/errors/ACCOUNT_NOT_IN_TEAM'
    CLUBS_REQUEST_ERRORS_ACCOUNT_ALREADY_IN_TEAM = '#system_messages:clubs/request/errors/ACCOUNT_ALREADY_IN_TEAM'
    CLUBS_REQUEST_ERRORS_ACCOUNT_TEAMS_LIMIT_EXCEEDED = '#system_messages:clubs/request/errors/ACCOUNT_TEAMS_LIMIT_EXCEEDED'
    CLUBS_REQUEST_ERRORS_ACCOUNT_IS_TEAM_OWNER = '#system_messages:clubs/request/errors/ACCOUNT_IS_TEAM_OWNER'
    CLUBS_REQUEST_ERRORS_OWNER_TEAMS_LIMIT_EXCEEDED = '#system_messages:clubs/request/errors/OWNER_TEAMS_LIMIT_EXCEEDED'
    CLUBS_REQUEST_ERRORS_INVITE_DOES_NOT_EXIST = '#system_messages:clubs/request/errors/INVITE_DOES_NOT_EXIST'
    CLUBS_REQUEST_ERRORS_INVITE_IS_NOT_ACTIVE = '#system_messages:clubs/request/errors/INVITE_IS_NOT_ACTIVE'
    CLUBS_REQUEST_ERRORS_HAS_NO_CLUB = '#system_messages:clubs/request/errors/HAS_NO_CLUB'
    CLUBS_REQUEST_ERRORS_TOO_MANY_INVITES_PER_CALL = '#system_messages:clubs/request/errors/TOO_MANY_INVITES_PER_CALL'
    CLUBS_REQUEST_ERRORS_TEAM_ACTIVE_PROPOSALS_EXCEEDED = '#system_messages:clubs/request/errors/TEAM_ACTIVE_PROPOSALS_EXCEEDED'
    CLUBS_REQUEST_ERRORS_NOT_ENOUGH_RATED_BATTLES = '#system_messages:clubs/request/errors/NOT_ENOUGH_RATED_BATTLES'
    CLUBS_REQUEST_ERRORS_HAVE_NO_RIGHTS = '#system_messages:clubs/request/errors/HAVE_NO_RIGHTS'
    CLUBS_REQUEST_ERRORS_CLUBS_ARE_DISABLED = '#system_messages:clubs/request/errors/CLUBS ARE DISABLED'
    CLUBS_REQUEST_ERRORS_TIME_OUT = '#system_messages:clubs/request/errors/time out'
    CLUBS_REQUEST_ERRORS_SENDINVITE_IGNORED = '#system_messages:clubs/request/errors/sendInvite/ignored'
    CLUBS_REQUEST_ERRORS_SENDAPP_IGNORED = '#system_messages:clubs/request/errors/sendApp/ignored'
    CLUBS_REQUEST_ERRORS_JOINUNIT_WEBUNAVAILABLE = '#system_messages:clubs/request/errors/joinUnit/webUnavailable'
    CLANS_ISCLANPROFILEDISABLED = '#system_messages:clans/isClanProfileDisabled'
    CLANS_REQUEST_ERRORS_FORBIDDEN_ACCOUNT_TYPE = '#system_messages:clans/request/errors/FORBIDDEN_ACCOUNT_TYPE'
    CLANS_REQUEST_ERRORS_CANT_SEND_INVITES = '#system_messages:clans/request/errors/CANT_SEND_INVITES'
    CLANS_REQUEST_ERRORS_CLAN_CONSCRIPTION_CLOSED = '#system_messages:clans/request/errors/CLAN_CONSCRIPTION_CLOSED'
    CLANS_REQUEST_ERRORS_CLAN_IS_FULL = '#system_messages:clans/request/errors/CLAN_IS_FULL'
    CLANS_REQUEST_ERRORS_DEFAULT = '#system_messages:clans/request/errors/DEFAULT'
    CLANS_REQUEST_ERRORS_USER_IS_NOT_AUTHENTIFICATED = '#system_messages:clans/request/errors/User is not authentificated'
    CLANS_REQUEST_ERRORS_FORBIDDEN = '#system_messages:clans/request/errors/Forbidden'
    CLANS_REQUEST_ERRORS_BAD_REQUEST = '#system_messages:clans/request/errors/Bad request'
    CLANS_REQUEST_ERRORS_EXPORTER_ERROR_WAS_OCCURRED = '#system_messages:clans/request/errors/Exporter error was occurred'
    CLANS_REQUEST_ERRORS_SPA_ERROR_WAS_OCCURRED = '#system_messages:clans/request/errors/SPA error was occurred'
    CLANS_REQUEST_ERRORS_GLOBAL_MAP_ERROR_WAS_OCCURRED = '#system_messages:clans/request/errors/Global map error was occurred'
    CLANS_REQUEST_ERRORS_WGRS_ERROR_WAS_OCCURRED = '#system_messages:clans/request/errors/Wgrs error was occurred'
    CLANS_REQUEST_ERRORS_WGCCFE_ERROR_WAS_OCCURRED = '#system_messages:clans/request/errors/WGCCFE error was occurred'
    CLANS_REQUEST_ERRORS_CLAN_IS_DISBANDED = '#system_messages:clans/request/errors/Clan is disbanded'
    CLANS_REQUEST_ERRORS_STRONGHOLD_IS_NOT_FOUND = '#system_messages:clans/request/errors/Stronghold is not found'
    CLANS_REQUEST_ERRORS_WGCCBE_ERROR_WAS_OCCURRED = '#system_messages:clans/request/errors/WGCCBE error was occurred'
    CLANS_REQUEST_ERRORS_ACCOUNT_IS_BANNED = '#system_messages:clans/request/errors/Account is banned'
    CLANS_REQUEST_ERRORS_ACCOUNT_IN_UNKNOWN = '#system_messages:clans/request/errors/Account in unknown'
    CLANS_REQUEST_ERRORS_CLAN_DOES_NOT_EXIST = '#system_messages:clans/request/errors/Clan does not exist'
    CLANS_REQUEST_ERRORS_CLAN_IS_FULL_ = '#system_messages:clans/request/errors/Clan is full'
    CLANS_REQUEST_ERRORS_ACCOUNT_IS_IN_CLAN_ALREADY = '#system_messages:clans/request/errors/Account is in clan already'
    CLANS_REQUEST_ERRORS_ACCOUNT_IS_NOT_IN_CLAN = '#system_messages:clans/request/errors/Account is not in clan'
    CLANS_REQUEST_ERRORS_RECRUITING_POLICY_MISMATCH = '#system_messages:clans/request/errors/Recruiting policy mismatch'
    CLANS_REQUEST_ERRORS_ACCOUNT_DOES_NOT_MEET_REQUIREMENTS = '#system_messages:clans/request/errors/Account does not meet requirements'
    CLANS_REQUEST_ERRORS_TOO_MANY_INVITES = '#system_messages:clans/request/errors/Too many invites'
    CLANS_REQUEST_ERRORS_INVITE_DOES_NOT_EXIST = '#system_messages:clans/request/errors/Invite does not exist'
    CLANS_REQUEST_ERRORS_INVITE_IS_NOT_ACTIVE = '#system_messages:clans/request/errors/Invite is not active'
    CLANS_REQUEST_ERRORS_TOO_MANY_APPLICATIONS = '#system_messages:clans/request/errors/Too Many Applications'
    CLANS_REQUEST_ERRORS_APPLICATION_DOES_NOT_EXIST = '#system_messages:clans/request/errors/Application does not exist'
    CLANS_REQUEST_ERRORS_APPLICATION_IS_NOT_ACTIVE = '#system_messages:clans/request/errors/Application is not active'
    CLANS_REQUEST_ERRORS_CLAN_IS_NOT_ACTIVE = '#system_messages:clans/request/errors/Clan is not active'
    CLANS_NOTIFICATIONS_FROM = '#system_messages:clans/notifications/from'
    CLANS_NOTIFICATIONS_ACCEPT = '#system_messages:clans/notifications/accept'
    CLANS_NOTIFICATIONS_DECLINE = '#system_messages:clans/notifications/decline'
    CLANS_NOTIFICATIONS_INFO = '#system_messages:clans/notifications/info'
    CLANS_NOTIFICATIONS_INVITE = '#system_messages:clans/notifications/invite'
    CLANS_NOTIFICATIONS_INVITE_ACCEPTED = '#system_messages:clans/notifications/invite/accepted'
    CLANS_NOTIFICATIONS_INVITE_DECLINED = '#system_messages:clans/notifications/invite/declined'
    CLANS_NOTIFICATIONS_INVITE_EXPIRED = '#system_messages:clans/notifications/invite/expired'
    CLANS_NOTIFICATIONS_REQUEST = '#system_messages:clans/notifications/request'
    CLANS_NOTIFICATIONS_REQUEST_ACCEPTED = '#system_messages:clans/notifications/request/accepted'
    CLANS_NOTIFICATIONS_REQUEST_DECLINED = '#system_messages:clans/notifications/request/declined'
    CLANS_NOTIFICATIONS_INVITES = '#system_messages:clans/notifications/invites'
    CLANS_NOTIFICATIONS_INVITES_TURNOFF = '#system_messages:clans/notifications/invites/turnOff'
    CLANS_NOTIFICATIONS_INVITES_WATCHINVITES = '#system_messages:clans/notifications/invites/watchInvites'
    CLANS_NOTIFICATIONS_REQUESTS = '#system_messages:clans/notifications/requests'
    CLANS_NOTIFICATIONS_REQUESTS_WATCHREQUESTS = '#system_messages:clans/notifications/requests/watchRequests'
    CLANS_NOTIFICATIONS_REQUESTSENT = '#system_messages:clans/notifications/requestSent'
    CLANS_NOTIFICATIONS_INVITESENT = '#system_messages:clans/notifications/inviteSent'
    CLANS_NOTIFICATIONS_INVITESSENT = '#system_messages:clans/notifications/invitesSent'
    CLANS_NOTIFICATIONS_INVITESENDERROR = '#system_messages:clans/notifications/inviteSendError'
    CLANS_NOTIFICATIONS_INVITESSENDERROR = '#system_messages:clans/notifications/invitesSendError'
    CLANS_NOTIFICATIONS_PERSONAL_APPACCEPTED = '#system_messages:clans/notifications/personal/appAccepted'
    CLANS_NOTIFICATIONS_PERSONAL_APPDECLINED = '#system_messages:clans/notifications/personal/appDeclined'
    CLANS_NOTIFICATIONS_INVITEACCEPTED = '#system_messages:clans/notifications/inviteAccepted'
    CLANS_NOTIFICATIONS_INVITEDECLINED = '#system_messages:clans/notifications/inviteDeclined'
    EXCHANGE_SUCCESS = '#system_messages:exchange/success'
    EXCHANGE_NOT_ENOUGH_GOLD = '#system_messages:exchange/not_enough_gold'
    EXCHANGE_WALLET_NOT_AVAILABLE = '#system_messages:exchange/wallet_not_available'
    EXCHANGE_SERVER_ERROR = '#system_messages:exchange/server_error'
    EXCHANGEXP_SUCCESS = '#system_messages:exchangeXP/success'
    EXCHANGEXP_NOT_ENOUGH_GOLD = '#system_messages:exchangeXP/not_enough_gold'
    EXCHANGEXP_WALLET_NOT_AVAILABLE = '#system_messages:exchangeXP/wallet_not_available'
    EXCHANGEXP_SERVER_ERROR = '#system_messages:exchangeXP/server_error'
    QUESTS_NOQUESTSWITHGIVENID = '#system_messages:quests/noQuestsWithGivenID'
    WALLET_AVAILABLE = '#system_messages:wallet/available'
    WALLET_AVAILABLE_GOLD = '#system_messages:wallet/available_gold'
    WALLET_AVAILABLE_FREEXP = '#system_messages:wallet/available_freexp'
    WALLET_NOT_AVAILABLE = '#system_messages:wallet/not_available'
    WALLET_NOT_AVAILABLE_GOLD = '#system_messages:wallet/not_available_gold'
    WALLET_NOT_AVAILABLE_FREEXP = '#system_messages:wallet/not_available_freexp'
    POTAPOVQUESTS_SELECT_SUCCESS = '#system_messages:potapovQuests/select/success'
    POTAPOVQUESTS_SELECT_SERVER_ERROR = '#system_messages:potapovQuests/select/server_error'
    POTAPOVQUESTS_SELECT_SERVER_ERROR_WRONG_ARGS_TYPE = '#system_messages:potapovQuests/select/server_error/WRONG_ARGS_TYPE'
    POTAPOVQUESTS_SELECT_SERVER_ERROR_WRONG_ARGS = '#system_messages:potapovQuests/select/server_error/WRONG_ARGS'
    POTAPOVQUESTS_SELECT_SERVER_ERROR_NOT_ENOUGH_SLOTS = '#system_messages:potapovQuests/select/server_error/NOT_ENOUGH_SLOTS'
    POTAPOVQUESTS_SELECT_SERVER_ERROR_NOT_GOTTEN_REWARD = '#system_messages:potapovQuests/select/server_error/NOT_GOTTEN_REWARD'
    POTAPOVQUESTS_SELECT_SERVER_ERROR_NOT_BOUGHT_TILE = '#system_messages:potapovQuests/select/server_error/NOT_BOUGHT_TILE'
    POTAPOVQUESTS_SELECT_SERVER_ERROR_QUEST_ALREADY_COMPLETED = '#system_messages:potapovQuests/select/server_error/QUEST_ALREADY_COMPLETED'
    POTAPOVQUESTS_SELECT_SERVER_ERROR_NOT_UNLOCKED_QUEST = '#system_messages:potapovQuests/select/server_error/NOT_UNLOCKED_QUEST'
    POTAPOVQUESTS_SELECT_SERVER_ERROR_TOO_MANY_QUESTS_IN_CHAIN = '#system_messages:potapovQuests/select/server_error/TOO_MANY_QUESTS_IN_CHAIN'
    POTAPOVQUESTS_SELECT_SERVER_ERROR_LOCKED_BY_VEHICLE_QUEST = '#system_messages:potapovQuests/select/server_error/LOCKED_BY_VEHICLE_QUEST'
    POTAPOVQUESTS_SELECT_SERVER_ERROR_SEASON_LIMIT_THE_SAME_CLASS = '#system_messages:potapovQuests/select/server_error/SEASON_LIMIT_THE_SAME_CLASS'
    POTAPOVQUESTS_REFUSE_SUCCESS = '#system_messages:potapovQuests/refuse/success'
    POTAPOVQUESTS_REFUSE_SERVER_ERROR = '#system_messages:potapovQuests/refuse/server_error'
    POTAPOVQUESTS_REFUSE_SERVER_ERROR_LOCKED_BY_VEHICLE_QUEST = '#system_messages:potapovQuests/refuse/server_error/LOCKED_BY_VEHICLE_QUEST'
    POTAPOVQUESTS_SELECT_SERVER_ERROR_FALLOUT_LOCKED_BY_VEHICLE_QUEST = '#system_messages:potapovQuests/select/server_error/fallout/LOCKED_BY_VEHICLE_QUEST'
    POTAPOVQUESTS_REFUSE_SERVER_ERROR_FALLOUT_LOCKED_BY_VEHICLE_QUEST = '#system_messages:potapovQuests/refuse/server_error/fallout/LOCKED_BY_VEHICLE_QUEST'
    POTAPOVQUESTS_REFUSE_DISABLED = '#system_messages:potapovQuests/refuse/DISABLED'
    POTAPOVQUESTS_REWARD_REGULAR_SUCCESS = '#system_messages:potapovQuests/reward/regular/success'
    POTAPOVQUESTS_REWARD_REGULAR_SERVER_ERROR = '#system_messages:potapovQuests/reward/regular/server_error'
    POTAPOVQUESTS_REWARD_REGULAR_SERVER_ERROR_WRONG_ARGS_TYPE = '#system_messages:potapovQuests/reward/regular/server_error/WRONG_ARGS_TYPE'
    POTAPOVQUESTS_REWARD_REGULAR_SERVER_ERROR_NO_REWARD = '#system_messages:potapovQuests/reward/regular/server_error/NO_REWARD'
    POTAPOVQUESTS_REWARD_REGULAR_SERVER_ERROR_INVALID_STATE = '#system_messages:potapovQuests/reward/regular/server_error/INVALID_STATE'
    POTAPOVQUESTS_REWARD_REGULAR_SERVER_ERROR_DISABLED = '#system_messages:potapovQuests/reward/regular/server_error/DISABLED'
    POTAPOVQUESTS_REWARD_TANKWOMAN_SUCCESS = '#system_messages:potapovQuests/reward/tankwoman/success'
    POTAPOVQUESTS_REWARD_TANKWOMAN_SERVER_ERROR = '#system_messages:potapovQuests/reward/tankwoman/server_error'
    POTAPOVQUESTS_REWARD_TANKWOMAN_SERVER_ERROR_WRONG_ARGS_TYPE = '#system_messages:potapovQuests/reward/tankwoman/server_error/WRONG_ARGS_TYPE'
    POTAPOVQUESTS_REWARD_TANKWOMAN_SERVER_ERROR_NO_REWARD = '#system_messages:potapovQuests/reward/tankwoman/server_error/NO_REWARD'
    POTAPOVQUESTS_REWARD_TANKWOMAN_SERVER_ERROR_INVALID_STATE = '#system_messages:potapovQuests/reward/tankwoman/server_error/INVALID_STATE'
    POTAPOVQUESTS_REWARD_TANKWOMAN_SERVER_ERROR_DISABLED = '#system_messages:potapovQuests/reward/tankwoman/server_error/DISABLED'
    POTAPOVQUESTS_SELECT_DISABLED = '#system_messages:potapovQuests/select/DISABLED'
    UNIT_ERRORS_ALREADY_JOINED_UNIT = '#system_messages:unit/errors/ALREADY_JOINED_UNIT'
    UNIT_ERRORS_CANT_CHANGE_DIVISION = '#system_messages:unit/errors/CANT_CHANGE_DIVISION'
    UNIT_ERRORS_SORTIES_FORBIDDEN = '#system_messages:unit/errors/SORTIES_FORBIDDEN'
    UNIT_ERRORS_UNIT_MGR_ENTITY_CREATION_FAIL = '#system_messages:unit/errors/UNIT_MGR_ENTITY_CREATION_FAIL'
    UNIT_ERRORS_UNIT_ADD_FAIL = '#system_messages:unit/errors/UNIT_ADD_FAIL'
    UNIT_ERRORS_CANT_FIND_UNIT_MGR = '#system_messages:unit/errors/CANT_FIND_UNIT_MGR'
    UNIT_ERRORS_ADD_PLAYER_FAIL = '#system_messages:unit/errors/ADD_PLAYER_FAIL'
    UNIT_ERRORS_NO_AVAILABLE_SLOTS = '#system_messages:unit/errors/NO_AVAILABLE_SLOTS'
    UNIT_ERRORS_NO_UNIT_MGR = '#system_messages:unit/errors/NO_UNIT_MGR'
    UNIT_ERRORS_WRONG_UNIT_REQUISITES = '#system_messages:unit/errors/WRONG_UNIT_REQUISITES'
    UNIT_ERRORS_REMOVE_PLAYER_FAIL = '#system_messages:unit/errors/REMOVE_PLAYER_FAIL'
    UNIT_ERRORS_GET_VEHICLE_FAIL = '#system_messages:unit/errors/GET_VEHICLE_FAIL'
    UNIT_ERRORS_FAIL_UNIT_METHOD = '#system_messages:unit/errors/FAIL_UNIT_METHOD'
    UNIT_ERRORS_BAD_SLOT_IDX = '#system_messages:unit/errors/BAD_SLOT_IDX'
    UNIT_ERRORS_INSUFFICIENT_ROLE = '#system_messages:unit/errors/INSUFFICIENT_ROLE'
    UNIT_ERRORS_NO_UNIT = '#system_messages:unit/errors/NO_UNIT'
    UNIT_ERRORS_JOIN_CTX_LOCK = '#system_messages:unit/errors/JOIN_CTX_LOCK'
    UNIT_ERRORS_CANT_INVITE = '#system_messages:unit/errors/CANT_INVITE'
    UNIT_ERRORS_NOT_READY = '#system_messages:unit/errors/NOT_READY'
    UNIT_ERRORS_NOT_IN_QUEUE = '#system_messages:unit/errors/NOT_IN_QUEUE'
    UNIT_ERRORS_NOT_IDLE = '#system_messages:unit/errors/NOT_IDLE'
    UNIT_ERRORS_NOT_IN_SEARCH = '#system_messages:unit/errors/NOT_IN_SEARCH'
    UNIT_ERRORS_BAD_JOINING_ACC = '#system_messages:unit/errors/BAD_JOINING_ACC'
    UNIT_ERRORS_PLAYER_IGNORED = '#system_messages:unit/errors/PLAYER_IGNORED'
    UNIT_ERRORS_NOT_INVITED = '#system_messages:unit/errors/NOT_INVITED'
    UNIT_ERRORS_GET_READY_VEHICLE_FAIL = '#system_messages:unit/errors/GET_READY_VEHICLE_FAIL'
    UNIT_ERRORS_COOLDOWN = '#system_messages:unit/errors/COOLDOWN'
    UNIT_ERRORS_BAD_POINTS_SUM = '#system_messages:unit/errors/BAD_POINTS_SUM'
    UNIT_ERRORS_BAD_VEHICLE_LEVEL = '#system_messages:unit/errors/BAD_VEHICLE_LEVEL'
    UNIT_WARNINGS_NO_CLAN_MEMBERS = '#system_messages:unit/warnings/NO_CLAN_MEMBERS'
    UNIT_ERRORS_NO_PLAYER = '#system_messages:unit/errors/NO_PLAYER'
    UNIT_ERRORS_SLOT_RESERVED = '#system_messages:unit/errors/SLOT_RESERVED'
    UNIT_ERRORS_SLOT_OCCUPIED = '#system_messages:unit/errors/SLOT_OCCUPIED'
    UNIT_ERRORS_TOO_MANY_CLOSED_SLOTS = '#system_messages:unit/errors/TOO_MANY_CLOSED_SLOTS'
    UNIT_ERRORS_SLOT_NOT_CLOSED = '#system_messages:unit/errors/SLOT_NOT_CLOSED'
    UNIT_WARNINGS_CANT_PICK_LEADER = '#system_messages:unit/warnings/CANT_PICK_LEADER'
    UNIT_ERRORS_RESTRICT_LEGIONARIES = '#system_messages:unit/errors/RESTRICT_LEGIONARIES'
    UNIT_ERRORS_RESTRICT_INVITED = '#system_messages:unit/errors/RESTRICT_INVITED'
    UNIT_ERRORS_VEHICLE_MISMATCH = '#system_messages:unit/errors/VEHICLE_MISMATCH'
    UNIT_ERRORS_NO_VEHICLES = '#system_messages:unit/errors/NO_VEHICLES'
    UNIT_ERRORS_TOO_MANY_LEGIONARIES = '#system_messages:unit/errors/TOO_MANY_LEGIONARIES'
    UNIT_ERRORS_VEHICLE_NOT_CHOSEN = '#system_messages:unit/errors/VEHICLE_NOT_CHOSEN'
    UNIT_ERRORS_ALREADY_IN_SLOT = '#system_messages:unit/errors/ALREADY_IN_SLOT'
    UNIT_WARNINGS_KICKED_CANDIDATE = '#system_messages:unit/warnings/KICKED_CANDIDATE'
    UNIT_WARNINGS_KICKED_PLAYER = '#system_messages:unit/warnings/KICKED_PLAYER'
    UNIT_WARNINGS_UNIT_ASSEMBLER_TIMEOUT = '#system_messages:unit/warnings/UNIT_ASSEMBLER_TIMEOUT'
    UNIT_WARNINGS_KICKED_FROM_UNIT_ASSEMBLER = '#system_messages:unit/warnings/KICKED_FROM_UNIT_ASSEMBLER'
    UNIT_WARNINGS_INVITE_REMOVED = '#system_messages:unit/warnings/INVITE_REMOVED'
    UNIT_WARNINGS_ALREADY_INVITED = '#system_messages:unit/warnings/ALREADY_INVITED'
    UNIT_WARNINGS_WAITING_FOR_JOIN = '#system_messages:unit/warnings/WAITING_FOR_JOIN'
    UNIT_WARNINGS_CLAN_CHANGED = '#system_messages:unit/warnings/CLAN_CHANGED'
    UNIT_WARNINGS_FORT_BATTLE_END = '#system_messages:unit/warnings/FORT_BATTLE_END'
    UNIT_NOTIFICATION_PLAYEROFFLINE = '#system_messages:unit/notification/playerOffline'
    UNIT_NOTIFICATION_PLAYERONLINE = '#system_messages:unit/notification/playerOnline'
    UNIT_NOTIFICATION_PLAYERADDED = '#system_messages:unit/notification/playerAdded'
    UNIT_NOTIFICATION_PLAYERREMOVED = '#system_messages:unit/notification/playerRemoved'
    UNIT_NOTIFICATION_GIVELEADERSHIP = '#system_messages:unit/notification/giveLeadership'
    UNIT_NOTIFICATION_CHANGEDIVISION = '#system_messages:unit/notification/changeDivision'
    UNIT_NOTIFICATION_DIVISIONTYPE_MIDDLE = '#system_messages:unit/notification/divisionType/MIDDLE'
    UNIT_NOTIFICATION_DIVISIONTYPE_CHAMPION = '#system_messages:unit/notification/divisionType/CHAMPION'
    UNIT_NOTIFICATION_DIVISIONTYPE_ABSOLUTE = '#system_messages:unit/notification/divisionType/ABSOLUTE'
    UNITBROWSER_ERRORS_BAD_ACCEPT_CONTEXT = '#system_messages:unitBrowser/errors/BAD_ACCEPT_CONTEXT'
    PERIPHERY_ERRORS_ISNOTAVAILABLE = '#system_messages:periphery/errors/isNotAvailable'
    UNIT_ERRORS_BAD_CLAN = '#system_messages:unit/errors/BAD_CLAN'
    UNIT_ERRORS_BAD_ACCOUNT_TYPE = '#system_messages:unit/errors/BAD_ACCOUNT_TYPE'
    UNIT_ERRORS_HAS_IN_ARENA_MEMBERS = '#system_messages:unit/errors/HAS_IN_ARENA_MEMBERS'
    UNIT_ERRORS_ACCOUNT_RESTORED = '#system_messages:unit/errors/ACCOUNT_RESTORED'
    UNIT_ERRORS_UNIT_RESTORED = '#system_messages:unit/errors/UNIT_RESTORED'
    UNIT_ERRORS_OFFLINE_PLAYER = '#system_messages:unit/errors/OFFLINE_PLAYER'
    UNIT_ERRORS_TIMEOUT = '#system_messages:unit/errors/TIMEOUT'
    UNIT_ERRORS_BAD_ROSTER_PACK = '#system_messages:unit/errors/BAD_ROSTER_PACK'
    UNIT_ERRORS_CLUB_CHECKOUT_FAIL = '#system_messages:unit/errors/CLUB_CHECKOUT_FAIL'
    UNIT_ERRORS_PREV_RATED_BATTLE_IN_PROGRESS = '#system_messages:unit/errors/PREV_RATED_BATTLE_IN_PROGRESS'
    IGR_CUSTOMIZATION_BEGIN = '#system_messages:igr/customization/begin'
    IGR_CUSTOMIZATION_END = '#system_messages:igr/customization/end'
    INFO_NOAVAILABLE = '#system_messages:info/noAvailable'
    DRR_SCALE_STEP_UP = '#system_messages:drr_scale/step_up'
    DRR_SCALE_STEP_DOWN = '#system_messages:drr_scale/step_down'
    FORTIFICATION_FIXEDPLAYERTOBUILDING = '#system_messages:fortification/fixedPlayerToBuilding'
    FORTIFICATION_MODERNIZATIONBUILDING = '#system_messages:fortification/modernizationBuilding'
    FORTIFICATION_BUILDINGPROCESS = '#system_messages:fortification/buildingProcess'
    FORTIFICATION_DEMOUNTBUILDING = '#system_messages:fortification/demountBuilding'
    FORTIFICATION_DIRECTIONOPENED = '#system_messages:fortification/directionOpened'
    FORTIFICATION_DIRECTIONCLOSED = '#system_messages:fortification/directionClosed'
    FORTIFICATION_CREATED = '#system_messages:fortification/created'
    FORTIFICATION_ADDORDER = '#system_messages:fortification/addOrder'
    FORTIFICATION_ACTIVATEORDER = '#system_messages:fortification/activateOrder'
    FORTIFICATION_TRANSPORT = '#system_messages:fortification/transport'
    FORTIFICATION_DEFENCEHOURSET = '#system_messages:fortification/defenceHourSet'
    FORTIFICATION_DEFENCEHOURSET_OFFDAY = '#system_messages:fortification/defenceHourSet/offDay'
    FORTIFICATION_DEFENCEHOURSET_NOOFFDAY = '#system_messages:fortification/defenceHourSet/noOffDay'
    FORTIFICATION_VACATIONSET = '#system_messages:fortification/vacationSet'
    FORTIFICATION_DEFENCEHOURDEACTIVATED = '#system_messages:fortification/defenceHourDeactivated'
    FORTIFICATION_FORTBATTLEFINISHED = '#system_messages:fortification/fortBattleFinished'
    FORTIFICATION_ERRORS_UNKNOWN = '#system_messages:fortification/errors/UNKNOWN'
    FORTIFICATION_ERRORS_NOT_SUPPORTED = '#system_messages:fortification/errors/NOT_SUPPORTED'
    FORTIFICATION_ERRORS_BAD_METHOD = '#system_messages:fortification/errors/BAD_METHOD'
    FORTIFICATION_ERRORS_BAD_SORTIE_TIME = '#system_messages:fortification/errors/BAD_SORTIE_TIME'
    FORTIFICATION_ERRORS_NOT_CREATED = '#system_messages:fortification/errors/NOT_CREATED'
    FORTIFICATION_ERRORS_ALREADY_CREATED = '#system_messages:fortification/errors/ALREADY_CREATED'
    FORTIFICATION_ERRORS_NO_CLAN = '#system_messages:fortification/errors/NO_CLAN'
    FORTIFICATION_ERRORS_DUPLICATE_BUILDING_TYPE = '#system_messages:fortification/errors/DUPLICATE_BUILDING_TYPE'
    FORTIFICATION_ERRORS_WRONG_POS = '#system_messages:fortification/errors/WRONG_POS'
    FORTIFICATION_ERRORS_NO_BUILDING = '#system_messages:fortification/errors/NO_BUILDING'
    FORTIFICATION_ERRORS_NOT_ATTACHED_TO_BUILDING = '#system_messages:fortification/errors/NOT_ATTACHED_TO_BUILDING'
    FORTIFICATION_ERRORS_STORAGE_OVERFLOW = '#system_messages:fortification/errors/STORAGE_OVERFLOW'
    FORTIFICATION_ERRORS_EVENT_COOLDOWN = '#system_messages:fortification/errors/EVENT_COOLDOWN'
    FORTIFICATION_ERRORS_DEFENCE_NOT_POSSIBLE = '#system_messages:fortification/errors/DEFENCE_NOT_POSSIBLE'
    FORTIFICATION_ERRORS_DIR_NOT_OPEN = '#system_messages:fortification/errors/DIR_NOT_OPEN'
    FORTIFICATION_ERRORS_DIR_ALREADY_OPEN = '#system_messages:fortification/errors/DIR_ALREADY_OPEN'
    FORTIFICATION_ERRORS_NOT_ENOUGH_CLAN_MEMBERS = '#system_messages:fortification/errors/NOT_ENOUGH_CLAN_MEMBERS'
    FORTIFICATION_ERRORS_DIR_OCCUPIED = '#system_messages:fortification/errors/DIR_OCCUPIED'
    FORTIFICATION_ERRORS_BAD_DIR = '#system_messages:fortification/errors/BAD_DIR'
    FORTIFICATION_ERRORS_BAD_SORTIE_ID = '#system_messages:fortification/errors/BAD_SORTIE_ID'
    FORTIFICATION_ERRORS_TOO_MANY_PLAYERS_ATTACHED = '#system_messages:fortification/errors/TOO_MANY_PLAYERS_ATTACHED'
    FORTIFICATION_ERRORS_ALREADY_ATTACHED = '#system_messages:fortification/errors/ALREADY_ATTACHED'
    FORTIFICATION_ERRORS_NO_DEST_BUILDING = '#system_messages:fortification/errors/NO_DEST_BUILDING'
    FORTIFICATION_ERRORS_NOT_ENOUGH_RESOURCE = '#system_messages:fortification/errors/NOT_ENOUGH_RESOURCE'
    FORTIFICATION_ERRORS_CANT_UPGRADE = '#system_messages:fortification/errors/CANT_UPGRADE'
    FORTIFICATION_ERRORS_FORT_LEVEL_TOO_LOW = '#system_messages:fortification/errors/FORT_LEVEL_TOO_LOW'
    FORTIFICATION_ERRORS_TRANSPORT_COOLDOWN = '#system_messages:fortification/errors/TRANSPORT_COOLDOWN'
    FORTIFICATION_ERRORS_TRANSPORT_LIMIT_EXCEEDED = '#system_messages:fortification/errors/TRANSPORT_LIMIT_EXCEEDED'
    FORTIFICATION_ERRORS_BAD_VACATION_START = '#system_messages:fortification/errors/BAD_VACATION_START'
    FORTIFICATION_ERRORS_BAD_VACATION_DURATION = '#system_messages:fortification/errors/BAD_VACATION_DURATION'
    FORTIFICATION_ERRORS_NOT_A_CLAN_MEMBER = '#system_messages:fortification/errors/NOT_A_CLAN_MEMBER'
    FORTIFICATION_ERRORS_INSUFFICIENT_CLAN_ROLE = '#system_messages:fortification/errors/INSUFFICIENT_CLAN_ROLE'
    FORTIFICATION_ERRORS_ORDER_ALREADY_IN_PRODUCTION = '#system_messages:fortification/errors/ORDER_ALREADY_IN_PRODUCTION'
    FORTIFICATION_ERRORS_ORDER_ALREADY_ACTIVATED = '#system_messages:fortification/errors/ORDER_ALREADY_ACTIVATED'
    FORTIFICATION_ERRORS_TOO_MANY_ORDERS = '#system_messages:fortification/errors/TOO_MANY_ORDERS'
    FORTIFICATION_ERRORS_BUILDING_NOT_READY = '#system_messages:fortification/errors/BUILDING_NOT_READY'
    FORTIFICATION_ERRORS_WRONG_BUILDING = '#system_messages:fortification/errors/WRONG_BUILDING'
    FORTIFICATION_ERRORS_START_SCENARIO_NOT_DONE = '#system_messages:fortification/errors/START_SCENARIO_NOT_DONE'
    FORTIFICATION_ERRORS_CANT_TRANSPORT = '#system_messages:fortification/errors/CANT_TRANSPORT'
    FORTIFICATION_ERRORS_NO_ORDER = '#system_messages:fortification/errors/NO_ORDER'
    FORTIFICATION_ERRORS_NO_ORDER_DEF = '#system_messages:fortification/errors/NO_ORDER_DEF'
    FORTIFICATION_ERRORS_NO_ORDER_LEVEL = '#system_messages:fortification/errors/NO_ORDER_LEVEL'
    FORTIFICATION_ERRORS_BUILDINGS_STILL_PRESENT = '#system_messages:fortification/errors/BUILDINGS_STILL_PRESENT'
    FORTIFICATION_ERRORS_DIRECTIONS_STILL_OPEN = '#system_messages:fortification/errors/DIRECTIONS_STILL_OPEN'
    FORTIFICATION_ERRORS_TOO_MANY_SORTIES = '#system_messages:fortification/errors/TOO_MANY_SORTIES'
    FORTIFICATION_ERRORS_METHOD_COOLDOWN = '#system_messages:fortification/errors/METHOD_COOLDOWN'
    FORTIFICATION_ERRORS_BAD_RESOURCE_COUNT = '#system_messages:fortification/errors/BAD_RESOURCE_COUNT'
    FORTIFICATION_ERRORS_CENTER_NOT_AVAILABLE = '#system_messages:fortification/errors/CENTER_NOT_AVAILABLE'
    FORTIFICATION_ERRORS_BATTLE_INFO_NOT_AVAILABLE = '#system_messages:fortification/errors/BATTLE_INFO_NOT_AVAILABLE'
    FORTIFICATION_ERRORS_DEF_HOUR_NOT_ACTIVE = '#system_messages:fortification/errors/DEF_HOUR_NOT_ACTIVE'
    FORTIFICATION_ERRORS_NO_DATA_FOR_ACTIVATING_ORDER = '#system_messages:fortification/errors/NO_DATA_FOR_ACTIVATING_ORDER'
    FORTIFICATION_ERRORS_FAILED_TO_BOOK_DIR = '#system_messages:fortification/errors/FAILED_TO_BOOK_DIR'
    FORTIFICATION_ERRORS_DIR_LOCKED = '#system_messages:fortification/errors/DIR_LOCKED'
    FORTIFICATION_ERRORS_BASE_DAMAGED = '#system_messages:fortification/errors/BASE_DAMAGED'
    FORTIFICATION_ERRORS_ORDER_NOT_SUPPORTED = '#system_messages:fortification/errors/ORDER_NOT_SUPPORTED'
    FORTIFICATION_ERRORS_POSITION_OCCUPIED = '#system_messages:fortification/errors/POSITION_OCCUPIED'
    FORTIFICATION_ERRORS_BAD_SORTIE_DIVISION = '#system_messages:fortification/errors/BAD_SORTIE_DIVISION'
    FORTIFICATION_ERRORS_PERIPHERY_NOT_CONNECTED = '#system_messages:fortification/errors/PERIPHERY_NOT_CONNECTED'
    FORTIFICATION_ERRORS_TOO_FEW_OPEN_DIRS = '#system_messages:fortification/errors/TOO_FEW_OPEN_DIRS'
    FORTIFICATION_ERRORS_SHUTDOWN_ALREADY_REQUESTED = '#system_messages:fortification/errors/SHUTDOWN_ALREADY_REQUESTED'
    FORTIFICATION_ERRORS_SHUTDOWN_NOT_REQUESTED = '#system_messages:fortification/errors/SHUTDOWN_NOT_REQUESTED'
    FORTIFICATION_ERRORS_NO_PRODUCTION_ORDER = '#system_messages:fortification/errors/NO_PRODUCTION_ORDER'
    FORTIFICATION_ERRORS_ORDER_ALREADY_SUSPENDED = '#system_messages:fortification/errors/ORDER_ALREADY_SUSPENDED'
    FORTIFICATION_ERRORS_ORDER_NOT_SUSPENDED = '#system_messages:fortification/errors/ORDER_NOT_SUSPENDED'
    FORTIFICATION_ERRORS_GLOBAL_PRODUCTION_SUSPEND = '#system_messages:fortification/errors/GLOBAL_PRODUCTION_SUSPEND'
    FORTIFICATION_ERRORS_BUILDING_DAMAGED = '#system_messages:fortification/errors/BUILDING_DAMAGED'
    FORTIFICATION_ERRORS_BASE_NOT_DAMAGED = '#system_messages:fortification/errors/BASE_NOT_DAMAGED'
    FORTIFICATION_ERRORS_DIRECTION_CONTESTED = '#system_messages:fortification/errors/DIRECTION_CONTESTED'
    FORTIFICATION_ERRORS_BASE_DESTROYED = '#system_messages:fortification/errors/BASE_DESTROYED'
    FORTIFICATION_ERRORS_BAD_ORDERS_COUNT = '#system_messages:fortification/errors/BAD_ORDERS_COUNT'
    FORTIFICATION_ERRORS_BAD_HOUR_VALUE = '#system_messages:fortification/errors/BAD_HOUR_VALUE'
    FORTIFICATION_ERRORS_BAD_DAY_VALUE = '#system_messages:fortification/errors/BAD_DAY_VALUE'
    FORTIFICATION_ERRORS_BATTLE_DOES_NOT_EXIST = '#system_messages:fortification/errors/BATTLE_DOES_NOT_EXIST'
    FORTIFICATION_ERRORS_UNIT_NOT_READY = '#system_messages:fortification/errors/UNIT_NOT_READY'
    FORTIFICATION_ERRORS_BAD_FORT_BATTLE_ID = '#system_messages:fortification/errors/BAD_FORT_BATTLE_ID'
    FORTIFICATION_ERRORS_WRONG_CLAN = '#system_messages:fortification/errors/WRONG_CLAN'
    FORTIFICATION_ERRORS_ATTACK_DIR_BUSY = '#system_messages:fortification/errors/ATTACK_DIR_BUSY'
    FORTIFICATION_ERRORS_DEFENCE_DIR_BUSY = '#system_messages:fortification/errors/DEFENCE_DIR_BUSY'
    FORTIFICATION_ERRORS_NON_ALIGNED_TIMESTAMP = '#system_messages:fortification/errors/NON_ALIGNED_TIMESTAMP'
    FORTIFICATION_ERRORS_CLAN_ON_VACATION = '#system_messages:fortification/errors/CLAN_ON_VACATION'
    FORTIFICATION_ERRORS_CLAN_HAS_OFF_DAY = '#system_messages:fortification/errors/CLAN_HAS_OFF_DAY'
    FORTIFICATION_ERRORS_DIR_NOT_OPEN_FOR_ATTACKS = '#system_messages:fortification/errors/DIR_NOT_OPEN_FOR_ATTACKS'
    FORTIFICATION_ERRORS_ALREADY_PLANNED_ATTACK = '#system_messages:fortification/errors/ALREADY_PLANNED_ATTACK'
    FORTIFICATION_ERRORS_ATTACK_COOLDOWN = '#system_messages:fortification/errors/ATTACK_COOLDOWN'
    FORTIFICATION_ERRORS_ATTACK_PREORDER_FAILED = '#system_messages:fortification/errors/ATTACK_PREORDER_FAILED'
    FORTIFICATION_ERRORS_SCR_DIR_LOCKED = '#system_messages:fortification/errors/SCR_DIR_LOCKED'
    FORTIFICATION_ERRORS_DEST_DIR_LOCKED = '#system_messages:fortification/errors/DEST_DIR_LOCKED'
    FORTIFICATION_ERRORS_NO_SUCH_ATTACK = '#system_messages:fortification/errors/NO_SUCH_ATTACK'
    FORTIFICATION_ERRORS_ATTACK_NOT_PLANNED = '#system_messages:fortification/errors/ATTACK_NOT_PLANNED'
    FORTIFICATION_ERRORS_DEFENCE_NOT_PLANNED = '#system_messages:fortification/errors/DEFENCE_NOT_PLANNED'
    FORTIFICATION_ERRORS_ATTACKS_NOT_LOADED = '#system_messages:fortification/errors/ATTACKS_NOT_LOADED'
    FORTIFICATION_ERRORS_ALREADY_FAVORITE = '#system_messages:fortification/errors/ALREADY_FAVORITE'
    FORTIFICATION_ERRORS_BAD_CLAN_DBID = '#system_messages:fortification/errors/BAD_CLAN_DBID'
    FORTIFICATION_ERRORS_NOT_FAVORITE = '#system_messages:fortification/errors/NOT_FAVORITE'
    FORTIFICATION_ERRORS_BAD_DMG = '#system_messages:fortification/errors/BAD_DMG'
    FORTIFICATION_ERRORS_CANT_CREATE_CLAN = '#system_messages:fortification/errors/CANT_CREATE_CLAN'
    FORTIFICATION_ERRORS_CANT_LOOKUP_CLAN = '#system_messages:fortification/errors/CANT_LOOKUP_CLAN'
    FORTIFICATION_ERRORS_WRONG_PERIPHERY = '#system_messages:fortification/errors/WRONG_PERIPHERY'
    FORTIFICATION_ERRORS_FORT_BATTLES_DISABLED = '#system_messages:fortification/errors/FORT_BATTLES_DISABLED'
    FORTIFICATION_ERRORS_TOO_MANY_DEFENCES = '#system_messages:fortification/errors/TOO_MANY_DEFENCES'
    FORTIFICATION_ERRORS_CURFEW_HOUR = '#system_messages:fortification/errors/CURFEW_HOUR'
    FORTIFICATION_ERRORS_JOIN_CTX_LOCKED = '#system_messages:fortification/errors/JOIN_CTX_LOCKED'
    FORTIFICATION_ERRORS_ATTACK_TOO_LATE = '#system_messages:fortification/errors/ATTACK_TOO_LATE'
    FORTIFICATION_ERRORS_FORBIDDEN_FORT_BATTLE_HOUR = '#system_messages:fortification/errors/FORBIDDEN_FORT_BATTLE_HOUR'
    FORTIFICATION_ERRORS_BAD_SORTIE_PERIPHERY_ID = '#system_messages:fortification/errors/BAD_SORTIE_PERIPHERY_ID'
    BUTTONS_GOTOPOLL = '#system_messages:buttons/goToPoll'
    INVITE_STATUS_WRONG_CLAN = '#system_messages:invite/status/WRONG_CLAN'
    INVITE_STATUS_LEGIONARIES_NOT_ALLOWED = '#system_messages:invite/status/LEGIONARIES_NOT_ALLOWED'
    RALLY_LEAVEDISABLED = '#system_messages:rally/leaveDisabled'
    SQUAD_LEAVEDISABLED = '#system_messages:squad/leaveDisabled'
    BATTLERESULTS_SHARING_SUCCESS = '#system_messages:battleResults/sharing/success'
    BATTLE_REQUEST_SEND_INVITES = '#system_messages:battle/request/SEND_INVITES'
    PREBATTLE_REQUEST_NAME_ENUM = (PREBATTLE_REQUEST_NAME_CHANGE_SETTINGS,
     PREBATTLE_REQUEST_NAME_CHANGE_ARENA_VOIP,
     PREBATTLE_REQUEST_NAME_CHANGE_USER_STATUS,
     PREBATTLE_REQUEST_NAME_SWAP_TEAMS,
     PREBATTLE_REQUEST_NAME_SET_TEAM_STATE,
     PREBATTLE_REQUEST_NAME_SET_PLAYER_STATE,
     PREBATTLE_REQUEST_NAME_SEND_INVITE,
     PREBATTLE_REQUEST_NAME_PREBATTLES_LIST,
     PREBATTLE_REQUEST_NAME_CHANGE_UNIT_STATE,
     PREBATTLE_REQUEST_NAME_UNITS_LIST,
     PREBATTLE_REQUEST_NAME_CLOSE_SLOT,
     PREBATTLE_REQUEST_NAME_CHANGE_RATED,
     PREBATTLE_REQUEST_NAME_CHANGE_DIVISION,
     PREBATTLE_REQUEST_NAME_SET_ES_VEHICLE_LIST,
     PREBATTLE_REQUEST_NAME_CHANGE_ES_TYPE)
    FORTIFICATION_REQUEST_NAME_ENUM = (FORTIFICATION_REQUEST_NAME_CREATE_FORT,
     FORTIFICATION_REQUEST_NAME_DELETE_FORT,
     FORTIFICATION_REQUEST_NAME_OPEN_DIRECTION,
     FORTIFICATION_REQUEST_NAME_CLOSE_DIRECTION,
     FORTIFICATION_REQUEST_NAME_ADD_BUILDING,
     FORTIFICATION_REQUEST_NAME_DELETE_BUILDING,
     FORTIFICATION_REQUEST_NAME_TRANSPORTATION,
     FORTIFICATION_REQUEST_NAME_ADD_ORDER,
     FORTIFICATION_REQUEST_NAME_ACTIVATE_ORDER,
     FORTIFICATION_REQUEST_NAME_ATTACH,
     FORTIFICATION_REQUEST_NAME_UPGRADE,
     FORTIFICATION_REQUEST_NAME_CREATE_SORTIE,
     FORTIFICATION_REQUEST_NAME_REQUEST_SORTIE_UNIT,
     FORTIFICATION_REQUEST_NAME_CHANGE_DEF_HOUR,
     FORTIFICATION_REQUEST_NAME_CHANGE_OFF_DAY,
     FORTIFICATION_REQUEST_NAME_CHANGE_PERIPHERY,
     FORTIFICATION_REQUEST_NAME_CHANGE_VACATION,
     FORTIFICATION_REQUEST_NAME_CHANGE_SETTINGS,
     FORTIFICATION_REQUEST_NAME_SHUTDOWN_DEF_HOUR,
     FORTIFICATION_REQUEST_NAME_CANCEL_SHUTDOWN_DEF_HOUR,
     FORTIFICATION_REQUEST_NAME_REQUEST_PUBLIC_INFO,
     FORTIFICATION_REQUEST_NAME_REQUEST_CLAN_CARD,
     FORTIFICATION_REQUEST_NAME_ADD_FAVORITE,
     FORTIFICATION_REQUEST_NAME_REMOVE_FAVORITE,
     FORTIFICATION_REQUEST_NAME_PLAN_ATTACK)
    UNIT_ERRORS_ENUM = (UNIT_ERRORS_ALREADY_JOINED_UNIT,
     UNIT_ERRORS_CANT_CHANGE_DIVISION,
     UNIT_ERRORS_SORTIES_FORBIDDEN,
     UNIT_ERRORS_UNIT_MGR_ENTITY_CREATION_FAIL,
     UNIT_ERRORS_UNIT_ADD_FAIL,
     UNIT_ERRORS_CANT_FIND_UNIT_MGR,
     UNIT_ERRORS_ADD_PLAYER_FAIL,
     UNIT_ERRORS_NO_AVAILABLE_SLOTS,
     UNIT_ERRORS_NO_UNIT_MGR,
     UNIT_ERRORS_WRONG_UNIT_REQUISITES,
     UNIT_ERRORS_REMOVE_PLAYER_FAIL,
     UNIT_ERRORS_GET_VEHICLE_FAIL,
     UNIT_ERRORS_FAIL_UNIT_METHOD,
     UNIT_ERRORS_BAD_SLOT_IDX,
     UNIT_ERRORS_INSUFFICIENT_ROLE,
     UNIT_ERRORS_NO_UNIT,
     UNIT_ERRORS_JOIN_CTX_LOCK,
     UNIT_ERRORS_CANT_INVITE,
     UNIT_ERRORS_NOT_READY,
     UNIT_ERRORS_NOT_IN_QUEUE,
     UNIT_ERRORS_NOT_IDLE,
     UNIT_ERRORS_NOT_IN_SEARCH,
     UNIT_ERRORS_BAD_JOINING_ACC,
     UNIT_ERRORS_PLAYER_IGNORED,
     UNIT_ERRORS_NOT_INVITED,
     UNIT_ERRORS_GET_READY_VEHICLE_FAIL,
     UNIT_ERRORS_COOLDOWN,
     UNIT_ERRORS_BAD_POINTS_SUM,
     UNIT_ERRORS_BAD_VEHICLE_LEVEL,
     UNIT_ERRORS_NO_PLAYER,
     UNIT_ERRORS_SLOT_RESERVED,
     UNIT_ERRORS_SLOT_OCCUPIED,
     UNIT_ERRORS_TOO_MANY_CLOSED_SLOTS,
     UNIT_ERRORS_SLOT_NOT_CLOSED,
     UNIT_ERRORS_RESTRICT_LEGIONARIES,
     UNIT_ERRORS_RESTRICT_INVITED,
     UNIT_ERRORS_VEHICLE_MISMATCH,
     UNIT_ERRORS_NO_VEHICLES,
     UNIT_ERRORS_TOO_MANY_LEGIONARIES,
     UNIT_ERRORS_VEHICLE_NOT_CHOSEN,
     UNIT_ERRORS_ALREADY_IN_SLOT,
     UNIT_ERRORS_BAD_CLAN,
     UNIT_ERRORS_BAD_ACCOUNT_TYPE,
     UNIT_ERRORS_HAS_IN_ARENA_MEMBERS,
     UNIT_ERRORS_ACCOUNT_RESTORED,
     UNIT_ERRORS_UNIT_RESTORED,
     UNIT_ERRORS_OFFLINE_PLAYER,
     UNIT_ERRORS_TIMEOUT,
     UNIT_ERRORS_BAD_ROSTER_PACK,
     UNIT_ERRORS_CLUB_CHECKOUT_FAIL,
     UNIT_ERRORS_PREV_RATED_BATTLE_IN_PROGRESS)
    FORTIFICATION_ERRORS_ENUM = (FORTIFICATION_ERRORS_UNKNOWN,
     FORTIFICATION_ERRORS_NOT_SUPPORTED,
     FORTIFICATION_ERRORS_BAD_METHOD,
     FORTIFICATION_ERRORS_BAD_SORTIE_TIME,
     FORTIFICATION_ERRORS_NOT_CREATED,
     FORTIFICATION_ERRORS_ALREADY_CREATED,
     FORTIFICATION_ERRORS_NO_CLAN,
     FORTIFICATION_ERRORS_DUPLICATE_BUILDING_TYPE,
     FORTIFICATION_ERRORS_WRONG_POS,
     FORTIFICATION_ERRORS_NO_BUILDING,
     FORTIFICATION_ERRORS_NOT_ATTACHED_TO_BUILDING,
     FORTIFICATION_ERRORS_STORAGE_OVERFLOW,
     FORTIFICATION_ERRORS_EVENT_COOLDOWN,
     FORTIFICATION_ERRORS_DEFENCE_NOT_POSSIBLE,
     FORTIFICATION_ERRORS_DIR_NOT_OPEN,
     FORTIFICATION_ERRORS_DIR_ALREADY_OPEN,
     FORTIFICATION_ERRORS_NOT_ENOUGH_CLAN_MEMBERS,
     FORTIFICATION_ERRORS_DIR_OCCUPIED,
     FORTIFICATION_ERRORS_BAD_DIR,
     FORTIFICATION_ERRORS_BAD_SORTIE_ID,
     FORTIFICATION_ERRORS_TOO_MANY_PLAYERS_ATTACHED,
     FORTIFICATION_ERRORS_ALREADY_ATTACHED,
     FORTIFICATION_ERRORS_NO_DEST_BUILDING,
     FORTIFICATION_ERRORS_NOT_ENOUGH_RESOURCE,
     FORTIFICATION_ERRORS_CANT_UPGRADE,
     FORTIFICATION_ERRORS_FORT_LEVEL_TOO_LOW,
     FORTIFICATION_ERRORS_TRANSPORT_COOLDOWN,
     FORTIFICATION_ERRORS_TRANSPORT_LIMIT_EXCEEDED,
     FORTIFICATION_ERRORS_BAD_VACATION_START,
     FORTIFICATION_ERRORS_BAD_VACATION_DURATION,
     FORTIFICATION_ERRORS_NOT_A_CLAN_MEMBER,
     FORTIFICATION_ERRORS_INSUFFICIENT_CLAN_ROLE,
     FORTIFICATION_ERRORS_ORDER_ALREADY_IN_PRODUCTION,
     FORTIFICATION_ERRORS_ORDER_ALREADY_ACTIVATED,
     FORTIFICATION_ERRORS_TOO_MANY_ORDERS,
     FORTIFICATION_ERRORS_BUILDING_NOT_READY,
     FORTIFICATION_ERRORS_WRONG_BUILDING,
     FORTIFICATION_ERRORS_START_SCENARIO_NOT_DONE,
     FORTIFICATION_ERRORS_CANT_TRANSPORT,
     FORTIFICATION_ERRORS_NO_ORDER,
     FORTIFICATION_ERRORS_NO_ORDER_DEF,
     FORTIFICATION_ERRORS_NO_ORDER_LEVEL,
     FORTIFICATION_ERRORS_BUILDINGS_STILL_PRESENT,
     FORTIFICATION_ERRORS_DIRECTIONS_STILL_OPEN,
     FORTIFICATION_ERRORS_TOO_MANY_SORTIES,
     FORTIFICATION_ERRORS_METHOD_COOLDOWN,
     FORTIFICATION_ERRORS_BAD_RESOURCE_COUNT,
     FORTIFICATION_ERRORS_CENTER_NOT_AVAILABLE,
     FORTIFICATION_ERRORS_BATTLE_INFO_NOT_AVAILABLE,
     FORTIFICATION_ERRORS_DEF_HOUR_NOT_ACTIVE,
     FORTIFICATION_ERRORS_NO_DATA_FOR_ACTIVATING_ORDER,
     FORTIFICATION_ERRORS_FAILED_TO_BOOK_DIR,
     FORTIFICATION_ERRORS_DIR_LOCKED,
     FORTIFICATION_ERRORS_BASE_DAMAGED,
     FORTIFICATION_ERRORS_ORDER_NOT_SUPPORTED,
     FORTIFICATION_ERRORS_POSITION_OCCUPIED,
     FORTIFICATION_ERRORS_BAD_SORTIE_DIVISION,
     FORTIFICATION_ERRORS_PERIPHERY_NOT_CONNECTED,
     FORTIFICATION_ERRORS_TOO_FEW_OPEN_DIRS,
     FORTIFICATION_ERRORS_SHUTDOWN_ALREADY_REQUESTED,
     FORTIFICATION_ERRORS_SHUTDOWN_NOT_REQUESTED,
     FORTIFICATION_ERRORS_NO_PRODUCTION_ORDER,
     FORTIFICATION_ERRORS_ORDER_ALREADY_SUSPENDED,
     FORTIFICATION_ERRORS_ORDER_NOT_SUSPENDED,
     FORTIFICATION_ERRORS_GLOBAL_PRODUCTION_SUSPEND,
     FORTIFICATION_ERRORS_BUILDING_DAMAGED,
     FORTIFICATION_ERRORS_BASE_NOT_DAMAGED,
     FORTIFICATION_ERRORS_DIRECTION_CONTESTED,
     FORTIFICATION_ERRORS_BASE_DESTROYED,
     FORTIFICATION_ERRORS_BAD_ORDERS_COUNT,
     FORTIFICATION_ERRORS_BAD_HOUR_VALUE,
     FORTIFICATION_ERRORS_BAD_DAY_VALUE,
     FORTIFICATION_ERRORS_BATTLE_DOES_NOT_EXIST,
     FORTIFICATION_ERRORS_UNIT_NOT_READY,
     FORTIFICATION_ERRORS_BAD_FORT_BATTLE_ID,
     FORTIFICATION_ERRORS_WRONG_CLAN,
     FORTIFICATION_ERRORS_ATTACK_DIR_BUSY,
     FORTIFICATION_ERRORS_DEFENCE_DIR_BUSY,
     FORTIFICATION_ERRORS_NON_ALIGNED_TIMESTAMP,
     FORTIFICATION_ERRORS_CLAN_ON_VACATION,
     FORTIFICATION_ERRORS_CLAN_HAS_OFF_DAY,
     FORTIFICATION_ERRORS_DIR_NOT_OPEN_FOR_ATTACKS,
     FORTIFICATION_ERRORS_ALREADY_PLANNED_ATTACK,
     FORTIFICATION_ERRORS_ATTACK_COOLDOWN,
     FORTIFICATION_ERRORS_ATTACK_PREORDER_FAILED,
     FORTIFICATION_ERRORS_SCR_DIR_LOCKED,
     FORTIFICATION_ERRORS_DEST_DIR_LOCKED,
     FORTIFICATION_ERRORS_NO_SUCH_ATTACK,
     FORTIFICATION_ERRORS_ATTACK_NOT_PLANNED,
     FORTIFICATION_ERRORS_DEFENCE_NOT_PLANNED,
     FORTIFICATION_ERRORS_ATTACKS_NOT_LOADED,
     FORTIFICATION_ERRORS_ALREADY_FAVORITE,
     FORTIFICATION_ERRORS_BAD_CLAN_DBID,
     FORTIFICATION_ERRORS_NOT_FAVORITE,
     FORTIFICATION_ERRORS_BAD_DMG,
     FORTIFICATION_ERRORS_CANT_CREATE_CLAN,
     FORTIFICATION_ERRORS_CANT_LOOKUP_CLAN,
     FORTIFICATION_ERRORS_WRONG_PERIPHERY,
     FORTIFICATION_ERRORS_FORT_BATTLES_DISABLED,
     FORTIFICATION_ERRORS_TOO_MANY_DEFENCES,
     FORTIFICATION_ERRORS_CURFEW_HOUR,
     FORTIFICATION_ERRORS_JOIN_CTX_LOCKED,
     FORTIFICATION_ERRORS_ATTACK_TOO_LATE,
     FORTIFICATION_ERRORS_FORBIDDEN_FORT_BATTLE_HOUR,
     FORTIFICATION_ERRORS_BAD_SORTIE_PERIPHERY_ID)
    UNIT_NOTIFICATION_DIVISIONTYPE_ENUM = (UNIT_NOTIFICATION_DIVISIONTYPE_MIDDLE, UNIT_NOTIFICATION_DIVISIONTYPE_CHAMPION, UNIT_NOTIFICATION_DIVISIONTYPE_ABSOLUTE)
    UNITBROWSER_ERRORS_ENUM = UNITBROWSER_ERRORS_BAD_ACCEPT_CONTEXT
    UNIT_NOTIFICATION_ENUM = (UNIT_NOTIFICATION_PLAYEROFFLINE,
     UNIT_NOTIFICATION_PLAYERONLINE,
     UNIT_NOTIFICATION_PLAYERADDED,
     UNIT_NOTIFICATION_PLAYERREMOVED,
     UNIT_NOTIFICATION_GIVELEADERSHIP,
     UNIT_NOTIFICATION_CHANGEDIVISION)
    UNIT_WARNINGS_ENUM = (UNIT_WARNINGS_NO_CLAN_MEMBERS,
     UNIT_WARNINGS_CANT_PICK_LEADER,
     UNIT_WARNINGS_KICKED_CANDIDATE,
     UNIT_WARNINGS_KICKED_PLAYER,
     UNIT_WARNINGS_UNIT_ASSEMBLER_TIMEOUT,
     UNIT_WARNINGS_KICKED_FROM_UNIT_ASSEMBLER,
     UNIT_WARNINGS_INVITE_REMOVED,
     UNIT_WARNINGS_ALREADY_INVITED,
     UNIT_WARNINGS_WAITING_FOR_JOIN,
     UNIT_WARNINGS_CLAN_CHANGED,
     UNIT_WARNINGS_FORT_BATTLE_END)
    CUSTOMIZATION_VEHICLE_ENUM = (CUSTOMIZATION_VEHICLE_LOCKED,
     CUSTOMIZATION_VEHICLE_DAMAGED,
     CUSTOMIZATION_VEHICLE_DESTROYED,
     CUSTOMIZATION_VEHICLE_EXPLODED)
    all_ENUM = (REPAIR_SUCCESS,
     REPAIR_CREDIT_ERROR,
     REPAIR_SERVER_ERROR,
     CHARGE_CREDIT_ERROR_GOLD,
     CHARGE_CREDIT_ERROR_CREDITS,
     CHARGE_CREDIT_ERROR,
     CHARGE_MONEY_SPENT,
     CHARGE_SUCCESS,
     CHARGE_SERVER_ERROR,
     CHARGE_INVENTORY_ERROR,
     CHARGE_SUCCESS_SAVE,
     CHARGE_SERVER_ERROR_SAVE,
     PREMIUM_CONTINUESUCCESS,
     PREMIUM_BUYINGSUCCESS,
     PREMIUM_SERVER_ERROR,
     PREMIUM_NOT_ENOUGH_GOLD,
     PREMIUM_WALLET_NOT_AVAILABLE,
     PREMIUM_POST_BATTLE_PREMIUM,
     BOOSTER_ACTIVATIONSUCCESS,
     BOOSTER_SERVER_ERROR,
     BOOSTER_NO_BOOSTERS,
     BOOSTER_ALREADY_USED,
     BOOSTER_DISABLED,
     BOOSTER_EXCEPTION,
     BOOSTER_WRONG_ARGS,
     UPGRADETANKMAN_SUCCESS,
     UPGRADETANKMAN_SERVER_ERROR,
     ARENA_START_ERRORS_JOIN_TIME_OUT,
     ARENA_START_ERRORS_JOIN_NOT_FOUND,
     ARENA_START_ERRORS_JOIN_WRONG_PERIPHERY_KNOWN,
     ARENA_START_ERRORS_JOIN_WRONG_PERIPHERY_UNKNOWN,
     ARENA_START_ERRORS_JOIN_ACCOUNT_LOCK,
     ARENA_START_ERRORS_JOIN_WRONG_VEHICLE,
     ARENA_START_ERRORS_JOIN_TEAM_IS_FULL,
     ARENA_START_ERRORS_JOIN_WRONG_ARGS,
     ARENA_START_ERRORS_JOIN_CAPTCHA,
     ARENA_START_ERRORS_JOIN_WRONG_ARENA_STATE,
     ARENA_START_ERRORS_JOIN_CANNOT_CREATE,
     ARENA_START_ERRORS_JOIN_PRIVACY,
     ARENA_START_ERRORS_JOIN_WRONG_ACCOUNT_TYPE,
     ARENA_START_ERRORS_JOIN_COOLDOWN,
     ARENA_START_ERRORS_JOIN_NO_VEHICLE,
     ARENA_START_ERRORS_JOIN_NO_READYVEHICLE,
     ARENA_START_ERRORS_JOIN_WRONG_BATTLE_ID,
     ARENA_START_ERRORS_JOIN_EVENT_DISABLED,
     PREBATTLE_KICK_TYPE_SQUAD,
     PREBATTLE_KICK_TYPE_TEAM,
     PREBATTLE_KICK_TYPE_UNKNOWN,
     PREBATTLE_KICK_REASON_ARENA_CREATION_FAILURE,
     PREBATTLE_KICK_REASON_AVATAR_CREATION_FAILURE,
     PREBATTLE_KICK_REASON_VEHICLE_CREATION_FAILURE,
     PREBATTLE_KICK_REASON_PREBATTLE_CREATION_FAILURE,
     PREBATTLE_KICK_REASON_BASEAPP_CRASH,
     PREBATTLE_KICK_REASON_CELLAPP_CRASH,
     PREBATTLE_KICK_REASON_UNKNOWN_FAILURE,
     PREBATTLE_KICK_REASON_FINISHED,
     PREBATTLE_KICK_REASON_CREATOR_LEFT,
     PREBATTLE_KICK_REASON_PLAYERKICK,
     PREBATTLE_KICK_REASON_TIMEOUT,
     SESSION_TRACKER_KICK,
     PREBATTLE_VEHICLEINVALID_LIMITS_LEVEL,
     PREBATTLE_VEHICLEINVALID_LIMITS_CLASSLEVEL,
     PREBATTLE_VEHICLEINVALID_LIMITS_VEHICLES,
     PREBATTLE_VEHICLEINVALID_LIMITS_COMPONENTS,
     PREBATTLE_VEHICLEINVALID_LIMITS_AMMO,
     PREBATTLE_VEHICLEINVALID_LIMITS_SHELLS,
     PREBATTLE_VEHICLEINVALID_LIMITS_TAGS,
     PREBATTLE_VEHICLEINVALID_LIMITS_NOT_SUPPORTED,
     PREBATTLE_VEHICLEINVALID_NO_READYVEHICLE,
     PREBATTLE_VEHICLEINVALID_VEHICLENOTSUPPORTED,
     PREBATTLE_VEHICLEINVALID_NOTSETREADYSTATUS,
     PREBATTLE_VEHICLEINVALID_FALLOUTONLY,
     PREBATTLE_VEHICLEINVALID_LIMITS_NATIONS,
     PREBATTLE_VEHICLEINVALID_LIMITS_CLASSES,
     PREBATTLE_TEAMINVALID_LIMIT_MINCOUNT,
     PREBATTLE_TEAMINVALID_LIMIT_TOTALLEVEL,
     PREBATTLE_TEAMINVALID_LIMITS_VEHICLES,
     PREBATTLE_TEAMINVALID_LIMITS_LEVEL,
     PREBATTLE_TEAMINVALID_OBSERVERS,
     PREBATTLE_TEAMINVALID_EVENT_BATTLE,
     PREBATTLE_HASLOCKEDSTATE,
     PREBATTLE_INVITES_SENDINVITE_NAME,
     PREBATTLE_INVITES_SENDINVITE,
     ARENA_START_ERRORS_KICK_ARENA_CREATION_FAILURE,
     ARENA_START_ERRORS_KICK_AVATAR_CREATION_FAILURE,
     ARENA_START_ERRORS_KICK_VEHICLE_CREATION_FAILURE,
     ARENA_START_ERRORS_KICK_PREBATTLE_CREATION_FAILURE,
     ARENA_START_ERRORS_KICK_BASEAPP_CRASH,
     ARENA_START_ERRORS_KICK_CELLAPP_CRASH,
     ARENA_START_ERRORS_KICK_UNKNOWN_FAILURE,
     ARENA_START_ERRORS_KICK_FINISHED,
     ARENA_START_ERRORS_KICK_CREATOR_LEFT,
     ARENA_START_ERRORS_KICK_PLAYERKICK,
     ARENA_START_ERRORS_KICK_TIMEOUT,
     ARENA_START_ERRORS_KICK_TIMEOUT_,
     PREBATTLE_START_FAILED_KICKEDFROMQUEUE_SQUAD,
     PREBATTLE_START_FAILED_KICKEDFROMQUEUE_COMPANY,
     PREBATTLE_START_FAILED_KICKEDFROMQUEUE_DEAFULT,
     WRONG_SLOT,
     CLIENTINSTALLERROR_WRONG_NATION,
     CLIENTINSTALLERROR_NOT_FOR_THIS_VEHICLE_TYPE,
     CLIENTINSTALLERROR_VEHICLEGUN_NOT_FOR_CURRENT_VEHICLE,
     CLIENTINSTALLERROR_WRONG_ITEM_TYPE,
     CLIENTINSTALLERROR_TOO_HEAVY,
     CLIENTREMOVEERROR_WRONG_NATION,
     CLIENTREMOVEERROR_NOT_IN_LIST,
     CLIENTREMOVEERROR_WRONG_ITEM_TYPE,
     CLIENTREMOVEERROR_TOO_HEAVY,
     SERVERINSTALLERROR,
     SERVERREMOVEERROR,
     BUY_VEHICLE_SLOT_ERROR,
     BUY_VEHICLE_SLOT_ERROR2,
     BUY_FREE_VEHICLE_LIMIT_ERROR,
     INSTALL_COMPONENT,
     REMOVE_COMPONENT,
     CURRENT_VEHICLE_CHANGED,
     INSTALL_VEHICLE_LOCKED,
     INSTALL_VEHICLE_BROKEN,
     REMOVE_VEHICLE_LOCKED,
     REMOVE_VEHICLE_BROKEN,
     SELL_VEHICLE_LOCKED,
     SELL_VEHICLE_BROKEN,
     WINDOW_BUTTONS_CLOSE,
     CONNECTED,
     DISCONNECTED,
     ROAMING_NOT_ALLOWED,
     SERVER_SHUT_DOWN,
     UNLOCKS_VEHICLE_UNLOCK_SUCCESS,
     UNLOCKS_ITEM_UNLOCK_SUCCESS,
     UNLOCKS_VEHICLE_ALREADY_UNLOCKED,
     UNLOCKS_ITEM_ALREADY_UNLOCKED,
     UNLOCKS_VEHICLE_SERVER_ERROR,
     UNLOCKS_ITEM_SERVER_ERROR,
     UNLOCKS_VEHICLE_IN_PROCESSING,
     UNLOCKS_ITEM_IN_PROCESSING,
     UNLOCKS_DRAWFAILED,
     SHOP_VEHICLE_NOT_ENOUGH_MONEY,
     SHOP_VEHICLE_NOT_ENOUGH_MONEY_FOR_RENT,
     SHOP_VEHICLE_COMMON_RENT_OR_BUY_ERROR,
     SHOP_ITEM_NOT_ENOUGH_MONEY,
     SHOP_VEHICLE_NOT_FOUND,
     SHOP_ITEM_NOT_FOUND,
     SHOP_ITEM_COMMON_RENT_OR_BUY_ERROR,
     SHOP_ITEM_BUY_SUCCESS,
     SHOP_ITEM_BUY_SERVER_ERROR,
     SHOP_ITEM_BUY_AND_EQUIP_IN_PROCESSING,
     INVENTORY_VEHICLE_NOT_FOUND,
     INVENTORY_ITEM_NOT_FOUND,
     INVENTORY_VEHICLE_ALREADY_EXISTS,
     INVENTORY_ITEM_ALREADY_EXISTS,
     INVENTORY_ITEM_EQUIP_IN_PROCESSING,
     SQUAD_MEMBERJOINED,
     SQUAD_MEMBERLEAVE,
     SQUAD_MEMBERREADY,
     SQUAD_MEMBERNOTREADY,
     SQUAD_MEMBEROFFLINE,
     SQUAD_CREATEERROR,
     SQUAD_NOTSETREADYSTATUS,
     SQUAD_KICKEDFROMQUEUE,
     COMPANY_MEMBERJOINED,
     COMPANY_MEMBERLEAVE,
     COMPANY_MEMBERREADY,
     COMPANY_MEMBERNOTREADY,
     COMPANY_MEMBEROFFLINE,
     COMPANY_CREATEERROR,
     COMPANY_NOTSETREADYSTATUS,
     COMPANY_KICKEDFROMQUEUE,
     BATTLESESSION_KICKEDFROMQUEUE,
     MEMBERROSTERCHANGEDMAIN,
     MEMBERROSTERCHANGEDSECOND,
     BATTLESESSION_MEMBERJOINED,
     BATTLESESSION_MEMBERLEAVE,
     BATTLESESSION_MEMBERREADY,
     BATTLESESSION_MEMBERNOTREADY,
     BATTLESESSION_MEMBEROFFLINE,
     MEMORY_CRITICAL_INSUFFICIENT_MEMORY_PLEASE_REBOOT,
     MEMORY_CRITICAL_TEX_WAS_LOWERED_TO_MEDIUM,
     MEMORY_CRITICAL_TEX_WAS_LOWERED_TO_LOW,
     MEMORY_CRITICAL_TEX_WAS_LOWERED_TO_MIN,
     TRADINGERROR_TOO_MANY_OUT_OFFERS,
     TRADINGERROR_NOT_ALLOWED,
     TRADINGERROR_NO_WARES,
     TRADINGERROR_DECLINED_BY_DEST,
     TRADINGERROR_UNEXPECTED_ERROR,
     GRAFICSOPTIONSFAIL,
     GRAFICSPRESETFAIL,
     DENUNCIATION_SUCCESS,
     CUSTOMIZATION_CREDITS_NOT_ENOUGH,
     CUSTOMIZATION_GOLD_NOT_ENOUGH,
     CUSTOMIZATION_CREDITS_AND_GOLD_NOT_ENOUGH,
     CUSTOMIZATION_CAMOUFLAGE_NOT_SELECTED,
     CUSTOMIZATION_CAMOUFLAGE_DAYS_NOT_SELECTED,
     CUSTOMIZATION_CAMOUFLAGE_COST_NOT_FOUND,
     CUSTOMIZATION_CAMOUFLAGE_NOT_FOUND_TO_DROP,
     CUSTOMIZATION_CAMOUFLAGE_GET_COST_SERVER_ERROR,
     CUSTOMIZATION_CAMOUFLAGE_CHANGE_SERVER_ERROR,
     CUSTOMIZATION_CAMOUFLAGE_DROP_SERVER_ERROR,
     CUSTOMIZATION_CAMOUFLAGE_CHANGE_SUCCESS_CREDITS,
     CUSTOMIZATION_CAMOUFLAGE_CHANGE_SUCCESS_GOLD,
     CUSTOMIZATION_CAMOUFLAGE_CHANGE_SUCCESS_FREE,
     CUSTOMIZATION_CAMOUFLAGE_DROP_SUCCESS,
     CUSTOMIZATION_CAMOUFLAGE_STORED_SUCCESS,
     CUSTOMIZATION_EMBLEM_NOT_SELECTED,
     CUSTOMIZATION_EMBLEM_DAYS_NOT_SELECTED,
     CUSTOMIZATION_EMBLEM_COST_NOT_FOUND,
     CUSTOMIZATION_EMBLEM_NOT_FOUND_TO_DROP,
     CUSTOMIZATION_EMBLEM_GET_COST_SERVER_ERROR,
     CUSTOMIZATION_EMBLEM_CHANGE_SERVER_ERROR,
     CUSTOMIZATION_EMBLEM_DROP_SERVER_ERROR,
     CUSTOMIZATION_EMBLEM_CHANGE_SUCCESS_CREDITS,
     CUSTOMIZATION_EMBLEM_CHANGE_SUCCESS_GOLD,
     CUSTOMIZATION_EMBLEM_CHANGE_SUCCESS_FREE,
     CUSTOMIZATION_EMBLEM_DROP_SUCCESS,
     CUSTOMIZATION_EMBLEM_STORED_SUCCESS,
     CUSTOMIZATION_INSCRIPTION_NOT_SELECTED,
     CUSTOMIZATION_INSCRIPTION_DAYS_NOT_SELECTED,
     CUSTOMIZATION_INSCRIPTION_COST_NOT_FOUND,
     CUSTOMIZATION_INSCRIPTION_NOT_FOUND_TO_DROP,
     CUSTOMIZATION_INSCRIPTION_GET_COST_SERVER_ERROR,
     CUSTOMIZATION_INSCRIPTION_CHANGE_SERVER_ERROR,
     CUSTOMIZATION_INSCRIPTION_DROP_SERVER_ERROR,
     CUSTOMIZATION_INSCRIPTION_CHANGE_SUCCESS_CREDITS,
     CUSTOMIZATION_INSCRIPTION_CHANGE_SUCCESS_GOLD,
     CUSTOMIZATION_INSCRIPTION_CHANGE_SUCCESS_FREE,
     CUSTOMIZATION_INSCRIPTION_DROP_SUCCESS,
     CUSTOMIZATION_INSCRIPTION_STORED_SUCCESS,
     CUSTOMIZATION_IGR_TYPE_CHANGED_ERROR,
     CUSTOMIZATION_ADDED_CAMOUFLAGES,
     CUSTOMIZATION_ADDED_EMBLEMS,
     CUSTOMIZATION_ADDED_INSCRIPTIONS,
     CUSTOMIZATION_REMOVED_CAMOUFLAGES,
     CUSTOMIZATION_REMOVED_EMBLEMS,
     CUSTOMIZATION_REMOVED_INSCRIPTIONS,
     CUSTOMIZATION_ADDED_CAMOUFLAGESVALUE,
     CUSTOMIZATION_ADDED_EMBLEMSVALUE,
     CUSTOMIZATION_ADDED_INSCRIPTIONSVALUE,
     CHECKOUT_ERROR,
     ANOTHER_PERIPHERY,
     SHOP_RESYNC,
     DOSSIERS_UNAVAILABLE,
     ACTIONACHIEVEMENT_TITLE,
     ACTIONACHIEVEMENTS_TITLE,
     TRAINING_ERROR_SWAPTEAMS,
     TRAINING_ERROR_DOACTION,
     GAMESESSIONCONTROL_KOREA_SESSIONTIME,
     GAMESESSIONCONTROL_KOREA_TIMETILLMIDNIGHT,
     GAMESESSIONCONTROL_KOREA_PLAYTIMELEFT,
     GAMESESSIONCONTROL_KOREA_MIDNIGHTNOTIFICATION,
     GAMESESSIONCONTROL_KOREA_PLAYTIMENOTIFICATION,
     GAMESESSIONCONTROL_KOREA_NOTE,
     VIDEO_ERROR,
     SECURITYMESSAGE_POOR_PASS,
     SECURITYMESSAGE_NO_QUESTION,
     SECURITYMESSAGE_BAD_EMAIL,
     SECURITYMESSAGE_NO_PHONE,
     SECURITYMESSAGE_OLD_PASS,
     SECURITYMESSAGE_CHANGE_SETINGS,
     ACCOUNT_WAS_RESTORED,
     LOGIN_TO_OTHER_GAME_WOT,
     LOGIN_TO_OTHER_GAME_WOWP,
     LOGIN_TO_OTHER_GAME_WOTG,
     LOGIN_TO_OTHER_GAME_WOWS,
     LOGIN_TO_OTHER_GAME_WOTB,
     LOGIN_TO_OTHER_GAME_UNKNOWN,
     LOGIN_TO_OTHER_GAME_WEB,
     RECRUIT_WINDOW_SERVER_ERROR,
     RECRUIT_WINDOW_SUCCESS,
     RECRUIT_WINDOW_FINANCIAL_SUCCESS,
     RECRUIT_WINDOW_NOT_ENOUGH_CREDITS,
     RECRUIT_WINDOW_NOT_ENOUGH_GOLD,
     RECRUIT_WINDOW_WALLET_NOT_AVAILABLE,
     RECRUIT_WINDOW_FREE_TANKMEN_LIMIT,
     RECRUIT_WINDOW_NOT_ENOUGH_SPACE,
     EQUIP_TANKMAN_SUCCESS,
     EQUIP_TANKMAN_SERVER_ERROR,
     EQUIP_TANKMAN_INVALID_VEHICLE,
     EQUIP_TANKMAN_VEHICLE_NEED_REPAIR,
     EQUIP_TANKMAN_VEHICLE_LOCKED,
     REEQUIP_TANKMAN_SUCCESS,
     REEQUIP_TANKMAN_SERVER_ERROR,
     REEQUIP_TANKMAN_INVALID_VEHICLE,
     REEQUIP_TANKMAN_VEHICLE_NEED_REPAIR,
     REEQUIP_TANKMAN_VEHICLE_LOCKED,
     BUY_AND_EQUIP_TANKMAN_SUCCESS,
     BUY_AND_EQUIP_TANKMAN_FINANCIAL_SUCCESS,
     BUY_AND_EQUIP_TANKMAN_SERVER_ERROR,
     BUY_AND_EQUIP_TANKMAN_INVALID_VEHICLE,
     BUY_AND_EQUIP_TANKMAN_VEHICLE_LOCKED,
     BUY_AND_EQUIP_TANKMAN_NOT_ENOUGH_CREDITS,
     BUY_AND_EQUIP_TANKMAN_NOT_ENOUGH_GOLD,
     BUY_AND_EQUIP_TANKMAN_WALLET_NOT_AVAILABLE,
     BUY_AND_EQUIP_TANKMAN_FREE_TANKMEN_LIMIT,
     BUY_AND_REEQUIP_TANKMAN_SUCCESS,
     BUY_AND_REEQUIP_TANKMAN_FINANCIAL_SUCCESS,
     BUY_AND_REEQUIP_TANKMAN_SERVER_ERROR,
     BUY_AND_REEQUIP_TANKMAN_INVALID_VEHICLE,
     BUY_AND_REEQUIP_TANKMAN_VEHICLE_LOCKED,
     BUY_AND_REEQUIP_TANKMAN_NOT_ENOUGH_CREDITS,
     BUY_AND_REEQUIP_TANKMAN_NOT_ENOUGH_GOLD,
     BUY_AND_REEQUIP_TANKMAN_WALLET_NOT_AVAILABLE,
     BUY_AND_REEQUIP_TANKMAN_FREE_TANKMEN_LIMIT,
     BUY_AND_REEQUIP_TANKMAN_NOT_ENOUGH_SPACE,
     DISMISS_TANKMAN_SUCCESS,
     DISMISS_TANKMAN_SERVER_ERROR,
     DISMISS_TANKMAN_INVALID_VEHICLE,
     DISMISS_TANKMAN_VEHICLE_NEED_REPAIR,
     DISMISS_TANKMAN_VEHICLE_LOCKED,
     UNLOAD_TANKMAN_SUCCESS,
     UNLOAD_TANKMAN_SERVER_ERROR,
     UNLOAD_TANKMAN_NOT_ENOUGH_SPACE,
     UNLOAD_TANKMAN_INVALID_VEHICLE,
     UNLOAD_TANKMAN_VEHICLE_NEED_REPAIR,
     UNLOAD_TANKMAN_VEHICLE_LOCKED,
     UNLOAD_CREW_SUCCESS,
     UNLOAD_CREW_SERVER_ERROR,
     UNLOAD_CREW_NOT_ENOUGH_SPACE,
     UNLOAD_CREW_INVALID_VEHICLE,
     UNLOAD_CREW_VEHICLE_NEED_REPAIR,
     UNLOAD_CREW_VEHICLE_LOCKED,
     RETURN_CREW_SUCCESS,
     RETURN_CREW_SERVER_ERROR,
     RETURN_CREW_NOT_ENOUGH_SPACE,
     RETURN_CREW_INVALID_VEHICLE,
     RETURN_CREW_VEHICLE_NEED_REPAIR,
     RETURN_CREW_VEHICLE_LOCKED,
     RETRAINING_TANKMAN_SUCCESS,
     RETRAINING_TANKMAN_FINANCIAL_SUCCESS,
     RETRAINING_TANKMAN_SERVER_ERROR,
     RETRAINING_TANKMAN_INVALID_VEHICLE,
     RETRAINING_TANKMAN_VEHICLE_NEED_REPAIR,
     RETRAINING_TANKMAN_VEHICLE_LOCKED,
     RETRAINING_TANKMAN_INVALID_OPERATION,
     RETRAINING_CREW_SUCCESS,
     RETRAINING_CREW_FINANCIAL_SUCCESS,
     RETRAINING_CREW_SERVER_ERROR,
     RETRAINING_CREW_INVALID_VEHICLE,
     RETRAINING_CREW_VEHICLE_NEED_REPAIR,
     RETRAINING_CREW_VEHICLE_LOCKED,
     RETRAINING_CREW_EMPTY_LIST,
     RETRAINING_CREW_INVALID_OPERATION,
     ADD_TANKMAN_SKILL_SUCCESS,
     ADD_TANKMAN_SKILL_SERVER_ERROR,
     ADD_TANKMAN_SKILL_INVALID_VEHICLE,
     ADD_TANKMAN_SKILL_VEHICLE_NEED_REPAIR,
     ADD_TANKMAN_SKILL_VEHICLE_LOCKED,
     DROP_TANKMAN_SKILL_SUCCESS,
     DROP_TANKMAN_SKILL_SERVER_ERROR,
     DROP_TANKMAN_SKILL_INVALID_VEHICLE,
     DROP_TANKMAN_SKILL_VEHICLE_NEED_REPAIR,
     DROP_TANKMAN_SKILL_VEHICLE_LOCKED,
     CHANGE_TANKMAN_ROLE_SUCCESS,
     CHANGE_TANKMAN_ROLE_INSTALLED,
     CHANGE_TANKMAN_ROLE_SLOT_IS_TAKEN,
     CHANGE_TANKMAN_ROLE_NO_VEHICLE,
     CHANGE_TANKMAN_ROLE_SERVER_ERROR,
     CHANGE_TANKMAN_ROLE_NOT_ENOUGH_GOLD,
     CHANGE_TANKMAN_ROLE_NOT_ENOUGH_CREDITS,
     CHANGE_TANKMAN_ROLE_WALLET_NOT_AVAILABLE,
     CHANGE_TANKMAN_ROLE_INVALID_VEHICLE,
     CHANGE_TANKMAN_ROLE_INVALID_ROLE,
     FREE_XP_TO_TMAN_SKILL_SUCCESS,
     FREE_XP_TO_TMAN_SKILL_SERVER_ERROR,
     FREE_XP_TO_TMAN_SKILL_ERROR_WRONG_ARGS_TYPE,
     FREE_XP_TO_TMAN_SKILL_ERROR_NO_TANKMAN_WITH_GIVEN_ID,
     FREE_XP_TO_TMAN_SKILL_ERROR_SHOP_DESYNC,
     FREE_XP_TO_TMAN_SKILL_ERROR_NO_FREE_XP,
     FREE_XP_TO_TMAN_SKILL_ERROR_NOT_IMPLEMENTED,
     REPLACE_TANKMAN_SUCCESS,
     REPLACE_TANKMAN_SERVER_ERROR,
     REPLACE_TANKMAN_INVALID_VEHICLE,
     REPLACE_TANKMAN_VEHICLE_NEED_REPAIR,
     REPLACE_TANKMAN_VEHICLE_LOCKED,
     REPLACE_TANKMAN_NOT_ENOUGH_MONEY,
     VEHICLE_BUY_SUCCESS,
     VEHICLE_BUY_SERVER_ERROR,
     VEHICLE_BUY_INVALID_VEHICLE,
     VEHICLE_BUY_SERVER_ERROR_CENTERDOWN,
     VEHICLE_BUY_NOT_ENOUGH_CREDITS,
     VEHICLE_BUY_NOT_ENOUGH_GOLD,
     VEHICLE_BUY_WALLET_NOT_AVAILABLE,
     VEHICLE_RENT_SUCCESS,
     VEHICLE_RENT_SERVER_ERROR,
     VEHICLE_RENT_INVALID_VEHICLE,
     VEHICLE_RENT_SERVER_ERROR_CENTERDOWN,
     VEHICLE_RENT_NOT_ENOUGH_CREDITS,
     VEHICLE_RENT_NOT_ENOUGH_GOLD,
     VEHICLE_RENT_WALLET_NOT_AVAILABLE,
     VEHICLE_SLOT_BUY_SUCCESS,
     VEHICLE_SLOT_BUY_NOT_ENOUGH_GOLD,
     VEHICLE_SLOT_BUY_WALLET_NOT_AVAILABLE,
     VEHICLE_SLOT_BUY_SERVER_ERROR,
     VEHICLE_SELL_SUCCESS,
     VEHICLE_SELL_SUCCESS_DISMANTLING,
     VEHICLE_SELL_SERVER_ERROR,
     VEHICLE_SELL_INVALID_VEHICLE,
     VEHICLE_SELL_VEHICLE_CANNOT_BE_SOLD,
     VEHICLE_SELL_VEHICLE_NEED_REPAIR,
     VEHICLE_SELL_VEHICLE_LOCKED,
     VEHICLE_SELL_NOT_ENOUGH_CREDITS,
     VEHICLE_SELL_NOT_ENOUGH_GOLD,
     VEHICLE_SELL_WALLET_NOT_AVAILABLE,
     VEHICLE_SELL_VEHICLE_SELL_LIMIT,
     VEHICLE_SELL_NOT_ENOUGH_SPACE,
     VEHICLE_REMOVE_SUCCESS,
     VEHICLE_REMOVE_SUCCESS_DISMANTLING,
     VEHICLE_REMOVE_SERVER_ERROR,
     VEHICLE_REMOVE_INVALID_VEHICLE,
     VEHICLE_REMOVE_VEHICLE_CANNOT_BE_SOLD,
     VEHICLE_REMOVE_VEHICLE_NEED_REPAIR,
     VEHICLE_REMOVE_VEHICLE_LOCKED,
     VEHICLE_REMOVE_NOT_ENOUGH_CREDITS,
     VEHICLE_REMOVE_NOT_ENOUGH_GOLD,
     VEHICLE_REMOVE_WALLET_NOT_AVAILABLE,
     VEHICLE_REMOVE_VEHICLE_SELL_LIMIT,
     VEHICLE_REMOVE_NOT_ENOUGH_SPACE,
     VEHICLE_TMENXP_ACCELERATOR_SUCCESSFALSE,
     VEHICLE_TMENXP_ACCELERATOR_SUCCESSTRUE,
     VEHICLE_TMENXP_ACCELERATOR_INVALID_VEHICLE,
     VEHICLE_TMENXP_ACCELERATOR_VEHICLE_NEED_REPAIR,
     VEHICLE_TMENXP_ACCELERATOR_VEHICLE_LOCKED,
     VEHICLE_TMENXP_ACCELERATOR_SERVER_ERROR,
     VEHICLE_REPAIR_SUCCESS,
     VEHICLE_REPAIR_NOT_ENOUGH_CREDITS,
     VEHICLE_REPAIR_SERVER_ERROR,
     BUY_TANKMEN_BERTHS_SUCCESS,
     BUY_TANKMEN_BERTHS_SERVER_ERROR,
     BUY_TANKMEN_BERTHS_NOT_ENOUGH_CREDITS,
     BUY_TANKMEN_BERTHS_NOT_ENOUGH_GOLD,
     BUY_TANKMEN_BERTHS_WALLET_NOT_AVAILABLE,
     SHELL_BUY_SUCCESS,
     SHELL_BUY_INVALID_MODULE,
     SHELL_BUY_NOT_ENOUGH_CREDITS,
     SHELL_BUY_NOT_ENOUGH_GOLD,
     SHELL_BUY_WALLET_NOT_AVAILABLE,
     SHELL_BUY_SERVER_ERROR,
     SHELL_BUY_SERVER_ERROR_CENTERDOWN,
     MODULE_BUY_SUCCESS,
     MODULE_BUY_INVALID_MODULE,
     MODULE_BUY_NOT_ENOUGH_CREDITS,
     MODULE_BUY_NOT_ENOUGH_GOLD,
     MODULE_BUY_WALLET_NOT_AVAILABLE,
     MODULE_BUY_SERVER_ERROR,
     MODULE_BUY_SERVER_ERROR_CENTERDOWN,
     MODULE_BUY_VEHICLE_NEED_REPAIR,
     MODULE_BUY_VEHICLE_LOCKED,
     MODULE_BUY_INVALID_VEHICLE,
     MODULE_BUY_ERROR_WRONG_NATION,
     MODULE_BUY_ERROR_NOT_FOR_THIS_VEHICLE_TYPE,
     MODULE_BUY_ERROR_NOT_FOR_CURRENT_VEHICLE,
     MODULE_BUY_ERROR_NO_GUN,
     MODULE_BUY_ERROR_WRONG_ITEM_TYPE,
     MODULE_BUY_ERROR_TOO_HEAVY,
     MODULE_BUY_ERROR_TOO_HEAVY_CHASSIS,
     MODULE_BUY_ERROR_NEED_TURRET,
     MODULE_BUY_ERROR_NEED_GUN,
     MODULE_BUY_ERROR_IS_CURRENT,
     MODULE_BUY_ERROR_NOT_WITH_INSTALLED_EQUIPMENT,
     ARTEFACT_BUY_SUCCESS,
     ARTEFACT_BUY_INVALID_MODULE,
     ARTEFACT_BUY_NOT_ENOUGH_CREDITS,
     ARTEFACT_BUY_NOT_ENOUGH_GOLD,
     ARTEFACT_BUY_WALLET_NOT_AVAILABLE,
     ARTEFACT_BUY_SERVER_ERROR,
     ARTEFACT_BUY_SERVER_ERROR_CENTERDOWN,
     ARTEFACT_BUY_ERROR_TOO_HEAVY,
     ARTEFACT_BUY_VEHICLE_NEED_REPAIR,
     ARTEFACT_BUY_VEHICLE_LOCKED,
     ARTEFACT_BUY_INVALID_VEHICLE,
     ARTEFACT_BUY_ERROR_NOT_FOR_THIS_VEHICLE_TYPE,
     SHELL_SELL_SUCCESS,
     SHELL_SELL_INVALID_MODULE,
     SHELL_SELL_SERVER_ERROR,
     MODULE_SELL_SUCCESS,
     MODULE_SELL_INVALID_MODULE,
     MODULE_SELL_SERVER_ERROR,
     ARTEFACT_SELL_SUCCESS,
     ARTEFACT_SELL_INVALID_MODULE,
     ARTEFACT_SELL_SERVER_ERROR,
     MODULE_APPLY_SUCCESS,
     MODULE_APPLY_SUCCESS_GUN_CHANGE,
     MODULE_APPLY_SERVER_ERROR,
     MODULE_APPLY_INVALID_VEHICLE,
     MODULE_APPLY_VEHICLE_LOCKED,
     MODULE_APPLY_VEHICLE_NEED_REPAIR,
     MODULE_APPLY_ERROR_WRONG_NATION,
     MODULE_APPLY_ERROR_NOT_FOR_THIS_VEHICLE_TYPE,
     MODULE_APPLY_ERROR_NOT_FOR_CURRENT_VEHICLE,
     MODULE_APPLY_ERROR_NO_GUN,
     MODULE_APPLY_ERROR_WRONG_ITEM_TYPE,
     MODULE_APPLY_ERROR_TOO_HEAVY,
     MODULE_APPLY_ERROR_TOO_HEAVY_CHASSIS,
     MODULE_APPLY_ERROR_NEED_TURRET,
     MODULE_APPLY_ERROR_NEED_GUN,
     MODULE_APPLY_ERROR_IS_CURRENT,
     MODULE_APPLY_ERROR_NOT_WITH_INSTALLED_EQUIPMENT,
     MODULE_APPLY_INCOMPATIBLEEQS,
     ARTEFACT_APPLY_SUCCESS,
     ARTEFACT_APPLY_GOLD_SUCCESS,
     ARTEFACT_APPLY_GOLD_ERROR_NOT_ENOUGH,
     ARTEFACT_REMOVE_SUCCESS,
     ARTEFACT_REMOVE_GOLD_SUCCESS,
     ARTEFACT_REMOVE_GOLD_ERROR_NOT_ENOUGH,
     ARTEFACT_REMOVE_INCOMPATIBLEEQS,
     ARTEFACT_DESTROY_SUCCESS,
     ARTEFACT_APPLY_SERVER_ERROR,
     ARTEFACT_REMOVE_SERVER_ERROR,
     ARTEFACT_DESTROY_SERVER_ERROR,
     ARTEFACT_APPLY_INVALID_VEHICLE,
     ARTEFACT_APPLY_VEHICLE_LOCKED,
     ARTEFACT_APPLY_VEHICLE_NEED_REPAIR,
     ARTEFACT_REMOVE_INVALID_VEHICLE,
     ARTEFACT_REMOVE_VEHICLE_LOCKED,
     ARTEFACT_REMOVE_VEHICLE_NEED_REPAIR,
     ARTEFACT_DESTROY_INVALID_VEHICLE,
     ARTEFACT_DESTROY_VEHICLE_LOCKED,
     ARTEFACT_DESTROY_VEHICLE_NEED_REPAIR,
     ARTEFACT_APPLY_ERROR_NOT_FOR_THIS_VEHICLE_TYPE,
     ARTEFACT_APPLY_ERROR_TOO_HEAVY,
     ARTEFACT_REMOVE_ERROR_TOO_HEAVY,
     LAYOUT_APPLY_SUCCESS_MONEY_SPENT,
     LAYOUT_APPLY_SERVER_ERROR,
     LAYOUT_APPLY_WRONG_ARGS_TYPE,
     LAYOUT_APPLY_SHOP_DESYNC,
     LAYOUT_APPLY_WRONG_ARG_VALUE,
     LAYOUT_APPLY_SHELLS_NO_CREDITS,
     LAYOUT_APPLY_SHELLS_NO_GOLD,
     LAYOUT_APPLY_SHELLS_NO_WALLET_SESSION,
     LAYOUT_APPLY_EQS_NO_CREDITS,
     LAYOUT_APPLY_EQS_NO_GOLD,
     LAYOUT_APPLY_EQS_NO_WALLET_SESSION,
     LAYOUT_APPLY_NOT_RESEARCHED_ITEM,
     LAYOUT_APPLY_BUYING_GOLD_EQS_FOR_CREDITS_DISABLED,
     LAYOUT_APPLY_BUYING_GOLD_SHELLS_FOR_CREDITS_DISABLED,
     LAYOUT_APPLY_NO_VEHICLE_WITH_GIVEN_ID,
     LAYOUT_APPLY_VEHICLE_IS_LOCKED,
     LAYOUT_APPLY_CANNOT_EQUIP_SHELLS,
     LAYOUT_APPLY_CANNOT_EQUIP_SHELLS__MAXAMMO_LIMIT_EXCEEDED_,
     LAYOUT_APPLY_CANNOT_EQUIP_EQUIPMENT,
     LAYOUT_APPLY_COMPONENT_IS_NOT_IN_SHOP,
     LAYOUT_APPLY_WALLET_NOT_AVAILABLE,
     LAYOUT_APPLY_INVALID_VEHICLE,
     LAYOUT_APPLY_VEHICLE_LOCKED,
     REQUEST_ISINCOOLDOWN,
     PREBATTLE_REQUEST_NAME_CHANGE_SETTINGS,
     PREBATTLE_REQUEST_NAME_CHANGE_ARENA_VOIP,
     PREBATTLE_REQUEST_NAME_CHANGE_USER_STATUS,
     PREBATTLE_REQUEST_NAME_SWAP_TEAMS,
     PREBATTLE_REQUEST_NAME_SET_TEAM_STATE,
     PREBATTLE_REQUEST_NAME_SET_PLAYER_STATE,
     PREBATTLE_REQUEST_NAME_SEND_INVITE,
     PREBATTLE_REQUEST_NAME_PREBATTLES_LIST,
     PREBATTLE_REQUEST_NAME_CHANGE_UNIT_STATE,
     PREBATTLE_REQUEST_NAME_UNITS_LIST,
     PREBATTLE_REQUEST_NAME_CLOSE_SLOT,
     PREBATTLE_REQUEST_NAME_CHANGE_RATED,
     PREBATTLE_REQUEST_NAME_CHANGE_DIVISION,
     PREBATTLE_REQUEST_NAME_SET_ES_VEHICLE_LIST,
     PREBATTLE_REQUEST_NAME_CHANGE_ES_TYPE,
     FORTIFICATION_REQUEST_NAME_CREATE_FORT,
     FORTIFICATION_REQUEST_NAME_DELETE_FORT,
     FORTIFICATION_REQUEST_NAME_OPEN_DIRECTION,
     FORTIFICATION_REQUEST_NAME_CLOSE_DIRECTION,
     FORTIFICATION_REQUEST_NAME_ADD_BUILDING,
     FORTIFICATION_REQUEST_NAME_DELETE_BUILDING,
     FORTIFICATION_REQUEST_NAME_TRANSPORTATION,
     FORTIFICATION_REQUEST_NAME_ADD_ORDER,
     FORTIFICATION_REQUEST_NAME_ACTIVATE_ORDER,
     FORTIFICATION_REQUEST_NAME_ATTACH,
     FORTIFICATION_REQUEST_NAME_UPGRADE,
     FORTIFICATION_REQUEST_NAME_CREATE_SORTIE,
     FORTIFICATION_REQUEST_NAME_REQUEST_SORTIE_UNIT,
     FORTIFICATION_REQUEST_NAME_CHANGE_DEF_HOUR,
     FORTIFICATION_REQUEST_NAME_CHANGE_OFF_DAY,
     FORTIFICATION_REQUEST_NAME_CHANGE_PERIPHERY,
     FORTIFICATION_REQUEST_NAME_CHANGE_VACATION,
     FORTIFICATION_REQUEST_NAME_CHANGE_SETTINGS,
     FORTIFICATION_REQUEST_NAME_SHUTDOWN_DEF_HOUR,
     FORTIFICATION_REQUEST_NAME_CANCEL_SHUTDOWN_DEF_HOUR,
     FORTIFICATION_REQUEST_NAME_REQUEST_PUBLIC_INFO,
     FORTIFICATION_REQUEST_NAME_REQUEST_CLAN_CARD,
     FORTIFICATION_REQUEST_NAME_ADD_FAVORITE,
     FORTIFICATION_REQUEST_NAME_REMOVE_FAVORITE,
     FORTIFICATION_REQUEST_NAME_PLAN_ATTACK,
     CLUB_REQUEST_NAME_SUBSCRIBE,
     CLUB_REQUEST_NAME_UNSUBSCRIBE,
     CLUB_REQUEST_NAME_CREATE_CLUB,
     CLUB_REQUEST_NAME_GET_MY_CLUBS,
     CLUB_REQUEST_NAME_GET_MY_CLUBS_HISTORY,
     CLUB_REQUEST_NAME_DESTROY_CLUB,
     CLUB_REQUEST_NAME_LEAVE_CLUB,
     CLUB_REQUEST_NAME_GET_CLUB,
     CLUB_REQUEST_NAME_OPEN_CLUB,
     CLUB_REQUEST_NAME_CLOSE_CLUB,
     CLUB_REQUEST_NAME_GET_CLUBS,
     CLUB_REQUEST_NAME_CHANGE_CLUB_NAME,
     CLUB_REQUEST_NAME_CHANGE_CLUB_EMBLEM,
     CLUB_REQUEST_NAME_SEND_INVITE,
     CLUB_REQUEST_NAME_REVOKE_INVITE,
     CLUB_REQUEST_NAME_ACCEPT_INVITE,
     CLUB_REQUEST_NAME_DECLINE_INVITE,
     CLUB_REQUEST_NAME_SEND_APPLICATION,
     CLUB_REQUEST_NAME_REVOKE_APPLICATION,
     CLUB_REQUEST_NAME_ACCEPT_APPLICATION,
     CLUB_REQUEST_NAME_DECLINE_APPLICATION,
     CLUB_REQUEST_NAME_JOIN_UNIT,
     CLUB_REQUEST_NAME_GET_APPLICATIONS,
     CLUB_REQUEST_NAME_GET_CLUB_APPLICANTS,
     CLUB_REQUEST_NAME_GET_INVITES,
     CLUB_REQUEST_NAME_TRANSFER_OWNERSHIP,
     CLUB_REQUEST_NAME_ASSIGN_OFFICER,
     CLUB_REQUEST_NAME_ASSIGN_PRIVATE,
     CLUB_REQUEST_NAME_KICK_MEMBER,
     CLUB_REQUEST_NAME_SET_APPLICANT_REQUIREMENTS,
     CLUBS_REQUEST_SUCCESS_APPLICATION_SENT,
     CLUBS_REQUEST_SUCCESS_APPLICATION_REVOKE,
     CLUBS_REQUEST_SUCCESS_APPLICATION_ACCEPT,
     CLUBS_REQUEST_SUCCESS_APPLICATION_DECLINE,
     CLUBS_REQUEST_SUCCESS_INVITE_SENT,
     CLUBS_REQUEST_SUCCESS_INVITES_SENT,
     CLUBS_REQUEST_SUCCESS_INVITES_SENT_NAMES_SUCCESS,
     CLUBS_REQUEST_SUCCESS_INVITES_SENT_NAMES_ERROR,
     CLUBS_REQUEST_SUCCESS_INVITE_REVOKE,
     CLUBS_REQUEST_SUCCESS_CREATECLUB,
     CLUBS_REQUEST_SUCCESS_LEAVECLUB,
     CLUBS_REQUEST_SUCCESS_DESTROYCLUB,
     CLUBS_REQUEST_SUCCESS_OPENCLUB,
     CLUBS_REQUEST_SUCCESS_CLOSECLUB,
     CLUBS_REQUEST_SUCCESS_USERS_ASSIGNPRIVATE,
     CLUBS_REQUEST_SUCCESS_USERS_ASSIGNOFFICER,
     CLUBS_REQUEST_SUCCESS_USERS_TRANSFEROWNERSHIP,
     CLUBS_REQUEST_SUCCESS_USERS_KICK,
     CLUBS_REQUEST_ERRORS_DEFAULT,
     CLUBS_REQUEST_ERRORS_SOME_ERROR_ON_ESTB_SIDE__SEE_SERVER_LOG_FOR_DETAILS_,
     CLUBS_REQUEST_ERRORS_ACCOUNT_ALREADY_OWNS_THE_CLUB_,
     CLUBS_REQUEST_ERRORS_ACCOUNT_ALREADY_A_CLUB_MEMBER_,
     CLUBS_REQUEST_ERRORS_NO_CLUB_FOUND_,
     CLUBS_REQUEST_ERRORS_ACCOUNT_NOT_A_CLUB_MEMBER_,
     CLUBS_REQUEST_ERRORS_FORBIDDEN_OPERATION_FOR_NON_EMPTY_CLUB_,
     CLUBS_REQUEST_ERRORS_THIS_OPERATION_IS_FORBIDDEN_FOR_CLUB_OWNER_,
     CLUBS_REQUEST_ERRORS_FORBIDDEN_OPERATION_BECAUSE_APPLICANTS_LIMIT_REACHED_,
     CLUBS_REQUEST_ERRORS_FORBIDDEN_OPERATION_BECAUSE_MEMBERS_LIMIT_REACHED_,
     CLUBS_REQUEST_ERRORS_INVITE_TO_THE_CLUB_ALREADY_SENT_TO_THIS_PLAYER_,
     CLUBS_REQUEST_ERRORS_INVITE_TO_THE_CLUB_NOT_FOUND_FOR_THIS_PLAYER_,
     CLUBS_REQUEST_ERRORS_ACCOUNT_NOT_A_CLUB_APPLICANT_,
     CLUBS_REQUEST_ERRORS_INCORRECT_PARAMS_PASSED_TO_THE_HANDLER_,
     CLUBS_REQUEST_ERRORS_HANDLER_RESPONSE_NOT_REGISTERED_,
     CLUBS_REQUEST_ERRORS_APPLICATIONS_TO_THE_CLOSED_CLUB_ARE_FORBIDDEN_,
     CLUBS_REQUEST_ERRORS_NONE_OF_THE_SUB_REQUESTS_WAS_NOT_COMPLETED_SUCCESSFULLY_,
     CLUBS_REQUEST_ERRORS_THIS_EMBLEM_NOT_REGISTERED_IN_EMULATOR_,
     CLUBS_REQUEST_ERRORS_COMMAND_FAILED_BY_TIMEOUT_,
     CLUBS_REQUEST_ERRORS_UNKNOWN_OR_UNEXPECTED_ERROR_,
     CLUBS_REQUEST_ERRORS_ACCOUNT_NOT_FOUND_FOR_GIVEN_ID_,
     CLUBS_REQUEST_ERRORS_ACCOUNT_FOR_GIVEN_ID_IS_BANNED_,
     CLUBS_REQUEST_ERRORS_INTERNAL_ERROR_IN_SPA__,
     CLUBS_REQUEST_ERRORS_FORBIDDEN_OPERATION_FOR_THIS_ACCOUNT_,
     CLUBS_REQUEST_ERRORS_INACTIVE_CLUB_,
     CLUBS_REQUEST_ERRORS_INACTIVE_APPLICATION_,
     CLUBS_REQUEST_ERRORS_INACTIVE_INVITE_,
     CLUBS_REQUEST_ERRORS_TOO_MANY_REQUESTS_ARE_IN_THE_PENDING_STATE_,
     CLUBS_REQUEST_ERRORS_TOO_MANY_INVITES_SENT_TO_THAT_PLAYER_,
     CLUBS_REQUEST_ERRORS_THIS_CLUB_NAME_IS_ALREADY_TAKEN_,
     CLUBS_REQUEST_ERRORS_INCORRECT_CHECKOUT_TOKEN_,
     CLUBS_REQUEST_ERRORS_CLUB_IS_LOCKED_,
     CLUBS_REQUEST_ERRORS_ATTEMPT_TO_ACCESS_TO_THE_INCORRECT_URL_,
     CLUBS_REQUEST_ERRORS_APPLICATION_FROM_THIS_ACCOUNT_ALREADY_EXISTS_,
     CLUBS_REQUEST_ERRORS_WRONG_OBTAINED_WEB_DATA_FORMAT__PLEASE_SEE_SERVER_LOGS_,
     CLUBS_REQUEST_ERRORS_THIS_OPERATION_IS_RESTRICTED_ON_WEB_SIDE_,
     CLUBS_REQUEST_ERRORS_WEB_API_IS_NOT_AVAILABLE_AT_THIS_MOMENT_,
     CLUBS_REQUEST_ERRORS_THIS_CLUB_IS_NOT_IN_THE_LADDER_,
     CLUBS_REQUEST_ERRORS_UNITMGR_NOT_AVAILABLE,
     CLUBS_REQUEST_ERRORS_TEAM_DOES_NOT_EXIST,
     CLUBS_REQUEST_ERRORS_TEAM_IS_FULL,
     CLUBS_REQUEST_ERRORS_TEAM_IS_NOT_ACTIVE,
     CLUBS_REQUEST_ERRORS_TEAM_ALREADY_EXIST,
     CLUBS_REQUEST_ERRORS_TEAM_MEMBERS_COUNT_ERROR,
     CLUBS_REQUEST_ERRORS_TEAM_DOES_NOT_HAVE_OWNER,
     CLUBS_REQUEST_ERRORS_TEAM_DOSSIER_WAS_LOCKED,
     CLUBS_REQUEST_ERRORS_TEAM_ALREADY_UNLOCKED,
     CLUBS_REQUEST_ERRORS_TEAM_LOCK_TOKEN_ERROR,
     CLUBS_REQUEST_ERRORS_EMBLEM_DOES_NOT_EXIST,
     CLUBS_REQUEST_ERRORS_WGESTB_COOLDOWN,
     CLUBS_REQUEST_ERRORS_CHANGE_TEAM_NAME_COOLDOWN,
     CLUBS_REQUEST_ERRORS_CHANGE_TEAM_TAG_COOLDOWN,
     CLUBS_REQUEST_ERRORS_TEAM_LEAVE_COOLDOWN,
     CLUBS_REQUEST_ERRORS_CANCEL_APPLICATION_COOLDOWN,
     CLUBS_REQUEST_ERRORS_CREATE_TEAM_AFTER_LEAVE_COOLDOWN,
     CLUBS_REQUEST_ERRORS_CREATE_TEAM_AFTER_DEACTIVATION_COOLDOWN,
     CLUBS_REQUEST_ERRORS_JOIN_TEAM_AFTER_DEACTIVATION_COOLDOWN,
     CLUBS_REQUEST_ERRORS_SAME_TEAM_APPLICATION_COOLDOWN,
     CLUBS_REQUEST_ERRORS_MEMBERSHIP_APPLICATION_NOT_NEEDED,
     CLUBS_REQUEST_ERRORS_APPLICATION_FOR_USER_EXCEEDED,
     CLUBS_REQUEST_ERRORS_ACCOUNT_BANNED,
     CLUBS_REQUEST_ERRORS_ACCOUNT_NOT_IN_TEAM,
     CLUBS_REQUEST_ERRORS_ACCOUNT_ALREADY_IN_TEAM,
     CLUBS_REQUEST_ERRORS_ACCOUNT_TEAMS_LIMIT_EXCEEDED,
     CLUBS_REQUEST_ERRORS_ACCOUNT_IS_TEAM_OWNER,
     CLUBS_REQUEST_ERRORS_OWNER_TEAMS_LIMIT_EXCEEDED,
     CLUBS_REQUEST_ERRORS_INVITE_DOES_NOT_EXIST,
     CLUBS_REQUEST_ERRORS_INVITE_IS_NOT_ACTIVE,
     CLUBS_REQUEST_ERRORS_HAS_NO_CLUB,
     CLUBS_REQUEST_ERRORS_TOO_MANY_INVITES_PER_CALL,
     CLUBS_REQUEST_ERRORS_TEAM_ACTIVE_PROPOSALS_EXCEEDED,
     CLUBS_REQUEST_ERRORS_NOT_ENOUGH_RATED_BATTLES,
     CLUBS_REQUEST_ERRORS_HAVE_NO_RIGHTS,
     CLUBS_REQUEST_ERRORS_CLUBS_ARE_DISABLED,
     CLUBS_REQUEST_ERRORS_TIME_OUT,
     CLUBS_REQUEST_ERRORS_SENDINVITE_IGNORED,
     CLUBS_REQUEST_ERRORS_SENDAPP_IGNORED,
     CLUBS_REQUEST_ERRORS_JOINUNIT_WEBUNAVAILABLE,
     CLANS_ISCLANPROFILEDISABLED,
     CLANS_REQUEST_ERRORS_FORBIDDEN_ACCOUNT_TYPE,
     CLANS_REQUEST_ERRORS_CANT_SEND_INVITES,
     CLANS_REQUEST_ERRORS_CLAN_CONSCRIPTION_CLOSED,
     CLANS_REQUEST_ERRORS_CLAN_IS_FULL,
     CLANS_REQUEST_ERRORS_DEFAULT,
     CLANS_REQUEST_ERRORS_USER_IS_NOT_AUTHENTIFICATED,
     CLANS_REQUEST_ERRORS_FORBIDDEN,
     CLANS_REQUEST_ERRORS_BAD_REQUEST,
     CLANS_REQUEST_ERRORS_EXPORTER_ERROR_WAS_OCCURRED,
     CLANS_REQUEST_ERRORS_SPA_ERROR_WAS_OCCURRED,
     CLANS_REQUEST_ERRORS_GLOBAL_MAP_ERROR_WAS_OCCURRED,
     CLANS_REQUEST_ERRORS_WGRS_ERROR_WAS_OCCURRED,
     CLANS_REQUEST_ERRORS_WGCCFE_ERROR_WAS_OCCURRED,
     CLANS_REQUEST_ERRORS_CLAN_IS_DISBANDED,
     CLANS_REQUEST_ERRORS_STRONGHOLD_IS_NOT_FOUND,
     CLANS_REQUEST_ERRORS_WGCCBE_ERROR_WAS_OCCURRED,
     CLANS_REQUEST_ERRORS_ACCOUNT_IS_BANNED,
     CLANS_REQUEST_ERRORS_ACCOUNT_IN_UNKNOWN,
     CLANS_REQUEST_ERRORS_CLAN_DOES_NOT_EXIST,
     CLANS_REQUEST_ERRORS_CLAN_IS_FULL_,
     CLANS_REQUEST_ERRORS_ACCOUNT_IS_IN_CLAN_ALREADY,
     CLANS_REQUEST_ERRORS_ACCOUNT_IS_NOT_IN_CLAN,
     CLANS_REQUEST_ERRORS_RECRUITING_POLICY_MISMATCH,
     CLANS_REQUEST_ERRORS_ACCOUNT_DOES_NOT_MEET_REQUIREMENTS,
     CLANS_REQUEST_ERRORS_TOO_MANY_INVITES,
     CLANS_REQUEST_ERRORS_INVITE_DOES_NOT_EXIST,
     CLANS_REQUEST_ERRORS_INVITE_IS_NOT_ACTIVE,
     CLANS_REQUEST_ERRORS_TOO_MANY_APPLICATIONS,
     CLANS_REQUEST_ERRORS_APPLICATION_DOES_NOT_EXIST,
     CLANS_REQUEST_ERRORS_APPLICATION_IS_NOT_ACTIVE,
     CLANS_REQUEST_ERRORS_CLAN_IS_NOT_ACTIVE,
     CLANS_NOTIFICATIONS_FROM,
     CLANS_NOTIFICATIONS_ACCEPT,
     CLANS_NOTIFICATIONS_DECLINE,
     CLANS_NOTIFICATIONS_INFO,
     CLANS_NOTIFICATIONS_INVITE,
     CLANS_NOTIFICATIONS_INVITE_ACCEPTED,
     CLANS_NOTIFICATIONS_INVITE_DECLINED,
     CLANS_NOTIFICATIONS_INVITE_EXPIRED,
     CLANS_NOTIFICATIONS_REQUEST,
     CLANS_NOTIFICATIONS_REQUEST_ACCEPTED,
     CLANS_NOTIFICATIONS_REQUEST_DECLINED,
     CLANS_NOTIFICATIONS_INVITES,
     CLANS_NOTIFICATIONS_INVITES_TURNOFF,
     CLANS_NOTIFICATIONS_INVITES_WATCHINVITES,
     CLANS_NOTIFICATIONS_REQUESTS,
     CLANS_NOTIFICATIONS_REQUESTS_WATCHREQUESTS,
     CLANS_NOTIFICATIONS_REQUESTSENT,
     CLANS_NOTIFICATIONS_INVITESENT,
     CLANS_NOTIFICATIONS_INVITESSENT,
     CLANS_NOTIFICATIONS_INVITESENDERROR,
     CLANS_NOTIFICATIONS_INVITESSENDERROR,
     CLANS_NOTIFICATIONS_PERSONAL_APPACCEPTED,
     CLANS_NOTIFICATIONS_PERSONAL_APPDECLINED,
     CLANS_NOTIFICATIONS_INVITEACCEPTED,
     CLANS_NOTIFICATIONS_INVITEDECLINED,
     EXCHANGE_SUCCESS,
     EXCHANGE_NOT_ENOUGH_GOLD,
     EXCHANGE_WALLET_NOT_AVAILABLE,
     EXCHANGE_SERVER_ERROR,
     EXCHANGEXP_SUCCESS,
     EXCHANGEXP_NOT_ENOUGH_GOLD,
     EXCHANGEXP_WALLET_NOT_AVAILABLE,
     EXCHANGEXP_SERVER_ERROR,
     QUESTS_NOQUESTSWITHGIVENID,
     WALLET_AVAILABLE,
     WALLET_AVAILABLE_GOLD,
     WALLET_AVAILABLE_FREEXP,
     WALLET_NOT_AVAILABLE,
     WALLET_NOT_AVAILABLE_GOLD,
     WALLET_NOT_AVAILABLE_FREEXP,
     POTAPOVQUESTS_SELECT_SUCCESS,
     POTAPOVQUESTS_SELECT_SERVER_ERROR,
     POTAPOVQUESTS_SELECT_SERVER_ERROR_WRONG_ARGS_TYPE,
     POTAPOVQUESTS_SELECT_SERVER_ERROR_WRONG_ARGS,
     POTAPOVQUESTS_SELECT_SERVER_ERROR_NOT_ENOUGH_SLOTS,
     POTAPOVQUESTS_SELECT_SERVER_ERROR_NOT_GOTTEN_REWARD,
     POTAPOVQUESTS_SELECT_SERVER_ERROR_NOT_BOUGHT_TILE,
     POTAPOVQUESTS_SELECT_SERVER_ERROR_QUEST_ALREADY_COMPLETED,
     POTAPOVQUESTS_SELECT_SERVER_ERROR_NOT_UNLOCKED_QUEST,
     POTAPOVQUESTS_SELECT_SERVER_ERROR_TOO_MANY_QUESTS_IN_CHAIN,
     POTAPOVQUESTS_SELECT_SERVER_ERROR_LOCKED_BY_VEHICLE_QUEST,
     POTAPOVQUESTS_SELECT_SERVER_ERROR_SEASON_LIMIT_THE_SAME_CLASS,
     POTAPOVQUESTS_REFUSE_SUCCESS,
     POTAPOVQUESTS_REFUSE_SERVER_ERROR,
     POTAPOVQUESTS_REFUSE_SERVER_ERROR_LOCKED_BY_VEHICLE_QUEST,
     POTAPOVQUESTS_SELECT_SERVER_ERROR_FALLOUT_LOCKED_BY_VEHICLE_QUEST,
     POTAPOVQUESTS_REFUSE_SERVER_ERROR_FALLOUT_LOCKED_BY_VEHICLE_QUEST,
     POTAPOVQUESTS_REFUSE_DISABLED,
     POTAPOVQUESTS_REWARD_REGULAR_SUCCESS,
     POTAPOVQUESTS_REWARD_REGULAR_SERVER_ERROR,
     POTAPOVQUESTS_REWARD_REGULAR_SERVER_ERROR_WRONG_ARGS_TYPE,
     POTAPOVQUESTS_REWARD_REGULAR_SERVER_ERROR_NO_REWARD,
     POTAPOVQUESTS_REWARD_REGULAR_SERVER_ERROR_INVALID_STATE,
     POTAPOVQUESTS_REWARD_REGULAR_SERVER_ERROR_DISABLED,
     POTAPOVQUESTS_REWARD_TANKWOMAN_SUCCESS,
     POTAPOVQUESTS_REWARD_TANKWOMAN_SERVER_ERROR,
     POTAPOVQUESTS_REWARD_TANKWOMAN_SERVER_ERROR_WRONG_ARGS_TYPE,
     POTAPOVQUESTS_REWARD_TANKWOMAN_SERVER_ERROR_NO_REWARD,
     POTAPOVQUESTS_REWARD_TANKWOMAN_SERVER_ERROR_INVALID_STATE,
     POTAPOVQUESTS_REWARD_TANKWOMAN_SERVER_ERROR_DISABLED,
     POTAPOVQUESTS_SELECT_DISABLED,
     UNIT_ERRORS_ALREADY_JOINED_UNIT,
     UNIT_ERRORS_CANT_CHANGE_DIVISION,
     UNIT_ERRORS_SORTIES_FORBIDDEN,
     UNIT_ERRORS_UNIT_MGR_ENTITY_CREATION_FAIL,
     UNIT_ERRORS_UNIT_ADD_FAIL,
     UNIT_ERRORS_CANT_FIND_UNIT_MGR,
     UNIT_ERRORS_ADD_PLAYER_FAIL,
     UNIT_ERRORS_NO_AVAILABLE_SLOTS,
     UNIT_ERRORS_NO_UNIT_MGR,
     UNIT_ERRORS_WRONG_UNIT_REQUISITES,
     UNIT_ERRORS_REMOVE_PLAYER_FAIL,
     UNIT_ERRORS_GET_VEHICLE_FAIL,
     UNIT_ERRORS_FAIL_UNIT_METHOD,
     UNIT_ERRORS_BAD_SLOT_IDX,
     UNIT_ERRORS_INSUFFICIENT_ROLE,
     UNIT_ERRORS_NO_UNIT,
     UNIT_ERRORS_JOIN_CTX_LOCK,
     UNIT_ERRORS_CANT_INVITE,
     UNIT_ERRORS_NOT_READY,
     UNIT_ERRORS_NOT_IN_QUEUE,
     UNIT_ERRORS_NOT_IDLE,
     UNIT_ERRORS_NOT_IN_SEARCH,
     UNIT_ERRORS_BAD_JOINING_ACC,
     UNIT_ERRORS_PLAYER_IGNORED,
     UNIT_ERRORS_NOT_INVITED,
     UNIT_ERRORS_GET_READY_VEHICLE_FAIL,
     UNIT_ERRORS_COOLDOWN,
     UNIT_ERRORS_BAD_POINTS_SUM,
     UNIT_ERRORS_BAD_VEHICLE_LEVEL,
     UNIT_WARNINGS_NO_CLAN_MEMBERS,
     UNIT_ERRORS_NO_PLAYER,
     UNIT_ERRORS_SLOT_RESERVED,
     UNIT_ERRORS_SLOT_OCCUPIED,
     UNIT_ERRORS_TOO_MANY_CLOSED_SLOTS,
     UNIT_ERRORS_SLOT_NOT_CLOSED,
     UNIT_WARNINGS_CANT_PICK_LEADER,
     UNIT_ERRORS_RESTRICT_LEGIONARIES,
     UNIT_ERRORS_RESTRICT_INVITED,
     UNIT_ERRORS_VEHICLE_MISMATCH,
     UNIT_ERRORS_NO_VEHICLES,
     UNIT_ERRORS_TOO_MANY_LEGIONARIES,
     UNIT_ERRORS_VEHICLE_NOT_CHOSEN,
     UNIT_ERRORS_ALREADY_IN_SLOT,
     UNIT_WARNINGS_KICKED_CANDIDATE,
     UNIT_WARNINGS_KICKED_PLAYER,
     UNIT_WARNINGS_UNIT_ASSEMBLER_TIMEOUT,
     UNIT_WARNINGS_KICKED_FROM_UNIT_ASSEMBLER,
     UNIT_WARNINGS_INVITE_REMOVED,
     UNIT_WARNINGS_ALREADY_INVITED,
     UNIT_WARNINGS_WAITING_FOR_JOIN,
     UNIT_WARNINGS_CLAN_CHANGED,
     UNIT_WARNINGS_FORT_BATTLE_END,
     UNIT_NOTIFICATION_PLAYEROFFLINE,
     UNIT_NOTIFICATION_PLAYERONLINE,
     UNIT_NOTIFICATION_PLAYERADDED,
     UNIT_NOTIFICATION_PLAYERREMOVED,
     UNIT_NOTIFICATION_GIVELEADERSHIP,
     UNIT_NOTIFICATION_CHANGEDIVISION,
     UNIT_NOTIFICATION_DIVISIONTYPE_MIDDLE,
     UNIT_NOTIFICATION_DIVISIONTYPE_CHAMPION,
     UNIT_NOTIFICATION_DIVISIONTYPE_ABSOLUTE,
     UNITBROWSER_ERRORS_BAD_ACCEPT_CONTEXT,
     PERIPHERY_ERRORS_ISNOTAVAILABLE,
     UNIT_ERRORS_BAD_CLAN,
     UNIT_ERRORS_BAD_ACCOUNT_TYPE,
     UNIT_ERRORS_HAS_IN_ARENA_MEMBERS,
     UNIT_ERRORS_ACCOUNT_RESTORED,
     UNIT_ERRORS_UNIT_RESTORED,
     UNIT_ERRORS_OFFLINE_PLAYER,
     UNIT_ERRORS_TIMEOUT,
     UNIT_ERRORS_BAD_ROSTER_PACK,
     UNIT_ERRORS_CLUB_CHECKOUT_FAIL,
     UNIT_ERRORS_PREV_RATED_BATTLE_IN_PROGRESS,
     IGR_CUSTOMIZATION_BEGIN,
     IGR_CUSTOMIZATION_END,
     INFO_NOAVAILABLE,
     DRR_SCALE_STEP_UP,
     DRR_SCALE_STEP_DOWN,
     FORTIFICATION_FIXEDPLAYERTOBUILDING,
     FORTIFICATION_MODERNIZATIONBUILDING,
     FORTIFICATION_BUILDINGPROCESS,
     FORTIFICATION_DEMOUNTBUILDING,
     FORTIFICATION_DIRECTIONOPENED,
     FORTIFICATION_DIRECTIONCLOSED,
     FORTIFICATION_CREATED,
     FORTIFICATION_ADDORDER,
     FORTIFICATION_ACTIVATEORDER,
     FORTIFICATION_TRANSPORT,
     FORTIFICATION_DEFENCEHOURSET,
     FORTIFICATION_DEFENCEHOURSET_OFFDAY,
     FORTIFICATION_DEFENCEHOURSET_NOOFFDAY,
     FORTIFICATION_VACATIONSET,
     FORTIFICATION_DEFENCEHOURDEACTIVATED,
     FORTIFICATION_FORTBATTLEFINISHED,
     FORTIFICATION_ERRORS_UNKNOWN,
     FORTIFICATION_ERRORS_NOT_SUPPORTED,
     FORTIFICATION_ERRORS_BAD_METHOD,
     FORTIFICATION_ERRORS_BAD_SORTIE_TIME,
     FORTIFICATION_ERRORS_NOT_CREATED,
     FORTIFICATION_ERRORS_ALREADY_CREATED,
     FORTIFICATION_ERRORS_NO_CLAN,
     FORTIFICATION_ERRORS_DUPLICATE_BUILDING_TYPE,
     FORTIFICATION_ERRORS_WRONG_POS,
     FORTIFICATION_ERRORS_NO_BUILDING,
     FORTIFICATION_ERRORS_NOT_ATTACHED_TO_BUILDING,
     FORTIFICATION_ERRORS_STORAGE_OVERFLOW,
     FORTIFICATION_ERRORS_EVENT_COOLDOWN,
     FORTIFICATION_ERRORS_DEFENCE_NOT_POSSIBLE,
     FORTIFICATION_ERRORS_DIR_NOT_OPEN,
     FORTIFICATION_ERRORS_DIR_ALREADY_OPEN,
     FORTIFICATION_ERRORS_NOT_ENOUGH_CLAN_MEMBERS,
     FORTIFICATION_ERRORS_DIR_OCCUPIED,
     FORTIFICATION_ERRORS_BAD_DIR,
     FORTIFICATION_ERRORS_BAD_SORTIE_ID,
     FORTIFICATION_ERRORS_TOO_MANY_PLAYERS_ATTACHED,
     FORTIFICATION_ERRORS_ALREADY_ATTACHED,
     FORTIFICATION_ERRORS_NO_DEST_BUILDING,
     FORTIFICATION_ERRORS_NOT_ENOUGH_RESOURCE,
     FORTIFICATION_ERRORS_CANT_UPGRADE,
     FORTIFICATION_ERRORS_FORT_LEVEL_TOO_LOW,
     FORTIFICATION_ERRORS_TRANSPORT_COOLDOWN,
     FORTIFICATION_ERRORS_TRANSPORT_LIMIT_EXCEEDED,
     FORTIFICATION_ERRORS_BAD_VACATION_START,
     FORTIFICATION_ERRORS_BAD_VACATION_DURATION,
     FORTIFICATION_ERRORS_NOT_A_CLAN_MEMBER,
     FORTIFICATION_ERRORS_INSUFFICIENT_CLAN_ROLE,
     FORTIFICATION_ERRORS_ORDER_ALREADY_IN_PRODUCTION,
     FORTIFICATION_ERRORS_ORDER_ALREADY_ACTIVATED,
     FORTIFICATION_ERRORS_TOO_MANY_ORDERS,
     FORTIFICATION_ERRORS_BUILDING_NOT_READY,
     FORTIFICATION_ERRORS_WRONG_BUILDING,
     FORTIFICATION_ERRORS_START_SCENARIO_NOT_DONE,
     FORTIFICATION_ERRORS_CANT_TRANSPORT,
     FORTIFICATION_ERRORS_NO_ORDER,
     FORTIFICATION_ERRORS_NO_ORDER_DEF,
     FORTIFICATION_ERRORS_NO_ORDER_LEVEL,
     FORTIFICATION_ERRORS_BUILDINGS_STILL_PRESENT,
     FORTIFICATION_ERRORS_DIRECTIONS_STILL_OPEN,
     FORTIFICATION_ERRORS_TOO_MANY_SORTIES,
     FORTIFICATION_ERRORS_METHOD_COOLDOWN,
     FORTIFICATION_ERRORS_BAD_RESOURCE_COUNT,
     FORTIFICATION_ERRORS_CENTER_NOT_AVAILABLE,
     FORTIFICATION_ERRORS_BATTLE_INFO_NOT_AVAILABLE,
     FORTIFICATION_ERRORS_DEF_HOUR_NOT_ACTIVE,
     FORTIFICATION_ERRORS_NO_DATA_FOR_ACTIVATING_ORDER,
     FORTIFICATION_ERRORS_FAILED_TO_BOOK_DIR,
     FORTIFICATION_ERRORS_DIR_LOCKED,
     FORTIFICATION_ERRORS_BASE_DAMAGED,
     FORTIFICATION_ERRORS_ORDER_NOT_SUPPORTED,
     FORTIFICATION_ERRORS_POSITION_OCCUPIED,
     FORTIFICATION_ERRORS_BAD_SORTIE_DIVISION,
     FORTIFICATION_ERRORS_PERIPHERY_NOT_CONNECTED,
     FORTIFICATION_ERRORS_TOO_FEW_OPEN_DIRS,
     FORTIFICATION_ERRORS_SHUTDOWN_ALREADY_REQUESTED,
     FORTIFICATION_ERRORS_SHUTDOWN_NOT_REQUESTED,
     FORTIFICATION_ERRORS_NO_PRODUCTION_ORDER,
     FORTIFICATION_ERRORS_ORDER_ALREADY_SUSPENDED,
     FORTIFICATION_ERRORS_ORDER_NOT_SUSPENDED,
     FORTIFICATION_ERRORS_GLOBAL_PRODUCTION_SUSPEND,
     FORTIFICATION_ERRORS_BUILDING_DAMAGED,
     FORTIFICATION_ERRORS_BASE_NOT_DAMAGED,
     FORTIFICATION_ERRORS_DIRECTION_CONTESTED,
     FORTIFICATION_ERRORS_BASE_DESTROYED,
     FORTIFICATION_ERRORS_BAD_ORDERS_COUNT,
     FORTIFICATION_ERRORS_BAD_HOUR_VALUE,
     FORTIFICATION_ERRORS_BAD_DAY_VALUE,
     FORTIFICATION_ERRORS_BATTLE_DOES_NOT_EXIST,
     FORTIFICATION_ERRORS_UNIT_NOT_READY,
     FORTIFICATION_ERRORS_BAD_FORT_BATTLE_ID,
     FORTIFICATION_ERRORS_WRONG_CLAN,
     FORTIFICATION_ERRORS_ATTACK_DIR_BUSY,
     FORTIFICATION_ERRORS_DEFENCE_DIR_BUSY,
     FORTIFICATION_ERRORS_NON_ALIGNED_TIMESTAMP,
     FORTIFICATION_ERRORS_CLAN_ON_VACATION,
     FORTIFICATION_ERRORS_CLAN_HAS_OFF_DAY,
     FORTIFICATION_ERRORS_DIR_NOT_OPEN_FOR_ATTACKS,
     FORTIFICATION_ERRORS_ALREADY_PLANNED_ATTACK,
     FORTIFICATION_ERRORS_ATTACK_COOLDOWN,
     FORTIFICATION_ERRORS_ATTACK_PREORDER_FAILED,
     FORTIFICATION_ERRORS_SCR_DIR_LOCKED,
     FORTIFICATION_ERRORS_DEST_DIR_LOCKED,
     FORTIFICATION_ERRORS_NO_SUCH_ATTACK,
     FORTIFICATION_ERRORS_ATTACK_NOT_PLANNED,
     FORTIFICATION_ERRORS_DEFENCE_NOT_PLANNED,
     FORTIFICATION_ERRORS_ATTACKS_NOT_LOADED,
     FORTIFICATION_ERRORS_ALREADY_FAVORITE,
     FORTIFICATION_ERRORS_BAD_CLAN_DBID,
     FORTIFICATION_ERRORS_NOT_FAVORITE,
     FORTIFICATION_ERRORS_BAD_DMG,
     FORTIFICATION_ERRORS_CANT_CREATE_CLAN,
     FORTIFICATION_ERRORS_CANT_LOOKUP_CLAN,
     FORTIFICATION_ERRORS_WRONG_PERIPHERY,
     FORTIFICATION_ERRORS_FORT_BATTLES_DISABLED,
     FORTIFICATION_ERRORS_TOO_MANY_DEFENCES,
     FORTIFICATION_ERRORS_CURFEW_HOUR,
     FORTIFICATION_ERRORS_JOIN_CTX_LOCKED,
     FORTIFICATION_ERRORS_ATTACK_TOO_LATE,
     FORTIFICATION_ERRORS_FORBIDDEN_FORT_BATTLE_HOUR,
     FORTIFICATION_ERRORS_BAD_SORTIE_PERIPHERY_ID,
     BUTTONS_GOTOPOLL,
     INVITE_STATUS_WRONG_CLAN,
     INVITE_STATUS_LEGIONARIES_NOT_ALLOWED,
     RALLY_LEAVEDISABLED,
     SQUAD_LEAVEDISABLED,
     BATTLERESULTS_SHARING_SUCCESS,
     BATTLE_REQUEST_SEND_INVITES)

    @staticmethod
    def prebattle_request_name(key):
        outcome = '#system_messages:prebattle/request/name/%s' % key
        if outcome not in SYSTEM_MESSAGES.PREBATTLE_REQUEST_NAME_ENUM:
            LOG_WARNING('locale key "' + outcome + '" was not found')
            return None
        else:
            return outcome

    @staticmethod
    def fortification_request_name(key):
        outcome = '#system_messages:fortification/request/name/%s' % key
        if outcome not in SYSTEM_MESSAGES.FORTIFICATION_REQUEST_NAME_ENUM:
            LOG_WARNING('locale key "' + outcome + '" was not found')
            return None
        else:
            return outcome

    @staticmethod
    def unit_errors(key):
        outcome = '#system_messages:unit/errors/%s' % key
        if outcome not in SYSTEM_MESSAGES.UNIT_ERRORS_ENUM:
            LOG_WARNING('locale key "' + outcome + '" was not found')
            return None
        else:
            return outcome

    @staticmethod
    def fortification_errors(key):
        outcome = '#system_messages:fortification/errors/%s' % key
        if outcome not in SYSTEM_MESSAGES.FORTIFICATION_ERRORS_ENUM:
            LOG_WARNING('locale key "' + outcome + '" was not found')
            return None
        else:
            return outcome

    @staticmethod
    def unit_notification_divisiontype(key):
        outcome = '#system_messages:unit/notification/divisionType/%s' % key
        if outcome not in SYSTEM_MESSAGES.UNIT_NOTIFICATION_DIVISIONTYPE_ENUM:
            LOG_WARNING('locale key "' + outcome + '" was not found')
            return None
        else:
            return outcome

    @staticmethod
    def unitbrowser_errors(key):
        outcome = '#system_messages:unitBrowser/errors/%s' % key
        if outcome not in SYSTEM_MESSAGES.UNITBROWSER_ERRORS_ENUM:
            LOG_WARNING('locale key "' + outcome + '" was not found')
            return None
        else:
            return outcome

    @staticmethod
    def unit_notification(key):
        outcome = '#system_messages:unit/notification/%s' % key
        if outcome not in SYSTEM_MESSAGES.UNIT_NOTIFICATION_ENUM:
            LOG_WARNING('locale key "' + outcome + '" was not found')
            return None
        else:
            return outcome

    @staticmethod
    def unit_warnings(key):
        outcome = '#system_messages:unit/warnings/%s' % key
        if outcome not in SYSTEM_MESSAGES.UNIT_WARNINGS_ENUM:
            LOG_WARNING('locale key "' + outcome + '" was not found')
            return None
        else:
            return outcome

    @staticmethod
    def customization_vehicle(key):
        outcome = '#system_messages:customization/vehicle_%s' % key
        if outcome not in SYSTEM_MESSAGES.CUSTOMIZATION_VEHICLE_ENUM:
            raise Exception, 'locale key "' + outcome + '" was not found'
        return outcome

    @staticmethod
    def all(key):
        outcome = '#system_messages:%s' % key
        if outcome not in SYSTEM_MESSAGES.all_ENUM:
            raise Exception, 'locale key "' + outcome + '" was not found'
        return outcome
