# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/locale/EVENT.py
from debug_utils import LOG_WARNING

class EVENT(object):
    NOTIFICATION_BOMBING = '#event:notification/bombing'
    NOTIFICATION_OBJ_COMPLETE = '#event:notification/obj_complete'
    NOTIFICATION_DEATHZONE = '#event:notification/deathzone'
    RADIALMENU_CHATABOUT = '#event:radialMenu/chatAbout'
    RADIALMENU_CHATWITH = '#event:radialMenu/chatWith'
    RADIALMENU_ALLIES = '#event:radialMenu/allies'
    RADIALMENU_NEXTPAGE = '#event:radialMenu/nextPage'
    RESULTSCREEN_TAB_0 = '#event:resultScreen/tab/0'
    RESULTSCREEN_TAB_1 = '#event:resultScreen/tab/1'
    RESULTSCREEN_STATS_DAMAGE = '#event:resultScreen/stats/damage'
    RESULTSCREEN_STATS_KILL = '#event:resultScreen/stats/kill'
    RESULTSCREEN_STATS_ASSIST = '#event:resultScreen/stats/assist'
    RESULTSCREEN_STATS_ARMOR = '#event:resultScreen/stats/armor'
    RESULTSCREEN_OBJECTIVES_HEADER = '#event:resultScreen/objectives/header'
    RESULTSCREEN_POINTS_WITHOUTBONUS = '#event:resultScreen/points/withoutBonus'
    RESULTSCREEN_CLOSE = '#event:resultScreen/close'
    RESULTSCREEN_ALIVE = '#event:resultScreen/alive'
    RESULTSCREEN_DEAD = '#event:resultScreen/dead'
    RESULTSCREEN_KILLEDBY = '#event:resultScreen/killedBy'
    RESULTSCREEN_BATTLETYPE = '#event:resultScreen/battleType'
    RESULTSCREEN_NEXT = '#event:resultScreen/next'
    RESULTSCREEN_ALLIES = '#event:resultScreen/allies'
    RESULTSCREEN_FRONTMISSIONHEADER = '#event:resultScreen/frontMissionHeader'
    RESULTSCREEN_FRONTMISSIONEARNED = '#event:resultScreen/frontMissionEarned'
    RESULTSCREEN_GENERALMISSIONEARNED = '#event:resultScreen/generalMissionEarned'
    RESULTSCREEN_TOOLTIP_KILLS_HEADER = '#event:resultScreen/tooltip/kills/header'
    RESULTSCREEN_TOOLTIP_KILLS_DESCR = '#event:resultScreen/tooltip/kills/descr'
    RESULTSCREEN_TOOLTIP_DAMAGE_HEADER = '#event:resultScreen/tooltip/damage/header'
    RESULTSCREEN_TOOLTIP_DAMAGE_DESCR = '#event:resultScreen/tooltip/damage/descr'
    RESULTSCREEN_TOOLTIP_ASSIST_HEADER = '#event:resultScreen/tooltip/assist/header'
    RESULTSCREEN_TOOLTIP_ASSIST_DESCR = '#event:resultScreen/tooltip/assist/descr'
    RESULTSCREEN_TOOLTIP_ARMOR_HEADER = '#event:resultScreen/tooltip/armor/header'
    RESULTSCREEN_TOOLTIP_ARMOR_DESCR = '#event:resultScreen/tooltip/armor/descr'
    RESULTSCREEN_TOOLTIP_VEHICLES_HEADER = '#event:resultScreen/tooltip/vehicles/header'
    RESULTSCREEN_TOOLTIP_VEHICLES_DESCR = '#event:resultScreen/tooltip/vehicles/descr'
    RESULTSCREEN_TOOLTIP_OBJECTIVES_HEADER = '#event:resultScreen/tooltip/objectives/header'
    RESULTSCREEN_TOOLTIP_OBJECTIVES_DESCR = '#event:resultScreen/tooltip/objectives/descr'
    RESULTSCREEN_MISSIONS_COMPLETED = '#event:resultScreen/missions/completed'
    RESULTSCREEN_MISSIONS_PROGRESS = '#event:resultScreen/missions/progress'
    RESULTSCREEN_MISSIONS_PROGRESSCREW = '#event:resultScreen/missions/progressCrew'
    VOICEOVER_LANGUAGE_CODE = '#event:voiceover_language_code'
    NEWS_BUTTON = '#event:news/button'
    HANGAR_EXIT = '#event:hangar/exit'
    HANGAR_CLOSE = '#event:hangar/close'
    HANGAR_BACK = '#event:hangar/back'
    HANGAR_BACKTO = '#event:hangar/backTo'
    GENERALS_INFOBTN = '#event:generals/infoBtn'
    GENERALS_ENERGY = '#event:generals/energy'
    VEHICLE_SELECT_TAB_TEAM = '#event:vehicle_select/tab/team'
    VEHICLE_SELECT_TAB_MAP = '#event:vehicle_select/tab/map'
    VEHICLE_SELECT_RESPAWNHINT_TITLE = '#event:vehicle_select/respawnHint/title'
    VEHICLE_SELECT_RESPAWNHINT_SELECTED = '#event:vehicle_select/respawnHint/selected'
    VEHICLE_SELECT_RESPAWNHINT_AVAILABLE = '#event:vehicle_select/respawnHint/available'
    GENERAL_BUY_PAGE_HEADER = '#event:general_buy_page/header'
    GENERAL_BUY_PAGE_TEXT = '#event:general_buy_page/text'
    GENERAL_BUY_PAGE_LEVEL_1_BUNDLENAME = '#event:general_buy_page/level/1/bundleName'
    GENERAL_BUY_PAGE_LEVEL_2_BUNDLENAME = '#event:general_buy_page/level/2/bundleName'
    GENERAL_BUY_PAGE_LEVEL_REACHED = '#event:general_buy_page/level/reached'
    GENERAL_BUY_PAGE_LEVEL_NOTREACHED = '#event:general_buy_page/level/notReached'
    GENERAL_BUY_PAGE_LEVEL_BOUGHT = '#event:general_buy_page/level_bought'
    GENERALS_READY = '#event:generals/ready'
    GENERALS_INBATTLE = '#event:generals/inBattle'
    GENERALS_INPLATOON = '#event:generals/inPlatoon'
    TANK_PARAMS_AVGDAMAGEPERMINUTE = '#event:tank_params/avgDamagePerMinute'
    TANK_PARAMS_SPEEDLIMITS = '#event:tank_params/speedLimits'
    TANK_PARAMS_ARMOR = '#event:tank_params/armor'
    TANK_PARAMS_DESC_ARMOR = '#event:tank_params/desc/armor'
    TANK_PARAMS_MAXHEALTH = '#event:tank_params/maxHealth'
    TANK_PARAMS_DESC_MAXHEALTH = '#event:tank_params/desc/maxHealth'
    TANK_PARAMS_CLIPFIRERATE = '#event:tank_params/clipFireRate'
    TANK_PARAMS_DESC_CLIPFIRERATE = '#event:tank_params/desc/clipFireRate'
    TANK_PARAMS_AVGDAMAGE = '#event:tank_params/avgDamage'
    TANK_PARAMS_DESC_AVGDAMAGE = '#event:tank_params/desc/avgDamage'
    TANK_PARAMS_PIERCINGPOWER = '#event:tank_params/piercingPower'
    TANK_PARAMS_DESC_PIERCINGPOWER = '#event:tank_params/desc/piercingPower'
    TANK_PARAMS_ACCURACY = '#event:tank_params/accuracy'
    TANK_PARAMS_DESC_ACCURACY = '#event:tank_params/desc/accuracy'
    TANK_PARAMS_MOBILITY = '#event:tank_params/mobility'
    TANK_PARAMS_DESC_MOBILITY = '#event:tank_params/desc/mobility'
    SELECTORTOOLTIP_HEADER = '#event:selectorTooltip/header'
    SELECTORTOOLTIP_DESCRIPTION = '#event:selectorTooltip/description'
    SELECTORTOOLTIP_ASSUREDLOWPERFORMANCE_TITLE = '#event:selectorTooltip/assuredLowPerformance/title'
    SELECTORTOOLTIP_ASSUREDLOWPERFORMANCE_DESCRIPTION = '#event:selectorTooltip/assuredLowPerformance/description'
    SELECTORTOOLTIP_POSSIBLELOWPERFORMANCE_TITLE = '#event:selectorTooltip/possibleLowPerformance/title'
    SELECTORTOOLTIP_POSSIBLELOWPERFORMANCE_DESCRIPTION = '#event:selectorTooltip/possibleLowPerformance/description'
    SELECTORTOOLTIP_INFORMATIVELOWPERFORMANCE_DESCRIPTION = '#event:selectorTooltip/informativeLowPerformance/description'
    SELECTORTOOLTIP_FROZEN = '#event:selectorTooltip/frozen'
    TITLE = '#event:title'
    UNITPROGRESSION_TITLE = '#event:unitProgression/title'
    UNITPROGRESSION_GOTPOINTS = '#event:unitProgression/gotPoints'
    UNITPROGRESSION_MAX = '#event:unitProgression/max'
    EVENTPROGRESSION_TITLE = '#event:eventProgression/title'
    EVENTPROGRESSION_GOTPOINTS = '#event:eventProgression/gotPoints'
    EVENTPROGRESSION_MAX = '#event:eventProgression/max'
    UNIT_DESCRIPTION_0 = '#event:unit/description/0'
    UNIT_DESCRIPTION_1 = '#event:unit/description/1'
    UNIT_DESCRIPTION_2 = '#event:unit/description/2'
    UNIT_DESCRIPTION_3 = '#event:unit/description/3'
    UNIT_DESCRIPTION_4 = '#event:unit/description/4'
    UNIT_NAME_0 = '#event:unit/name/0'
    UNIT_NAME_UPPER_0 = '#event:unit/name/upper/0'
    UNIT_NAME_1 = '#event:unit/name/1'
    UNIT_NAME_UPPER_1 = '#event:unit/name/upper/1'
    UNIT_NAME_2 = '#event:unit/name/2'
    UNIT_NAME_UPPER_2 = '#event:unit/name/upper/2'
    UNIT_NAME_3 = '#event:unit/name/3'
    UNIT_NAME_UPPER_3 = '#event:unit/name/upper/3'
    UNIT_NAME_4 = '#event:unit/name/4'
    UNIT_NAME_UPPER_4 = '#event:unit/name/upper/4'
    PREVIEWWINDOW_BUYBUTTON_LABEL = '#event:previewWindow/buyButton/label'
    PREVIEWWINDOW_ACTIONBUTTON_LABEL = '#event:previewWindow/actionButton/label'
    PREVIEWWINDOW_OR = '#event:previewWindow/or'
    PREVIEWWINDOW_MESSAGE = '#event:previewWindow/message'
    PREVIEWWINDOW_SHOP_MESSAGE = '#event:previewWindow/shop/message'
    PREVIEWWINDOW_SHOWBUTTON_LABEL = '#event:previewWindow/showButton/label'
    PREVIEWWINDOW_SHOWBUTTON_HEADER = '#event:previewWindow/showButton/header'
    PREVIEWWINDOW_RESTOREBUTTON_HEADER = '#event:previewWindow/restoreButton/header'
    PREVIEWWINDOW_RESTOREBUTTON_LABEL = '#event:previewWindow/restoreButton/label'
    CHARACTERISTICSPANEL_PROS = '#event:characteristicsPanel/pros'
    CHARACTERISTICSPANEL_CONS = '#event:characteristicsPanel/cons'
    CHARACTERISTICSPANEL_SKILLS = '#event:characteristicsPanel/skills'
    MENU_BASE = '#event:menu/base'
    MENU_BASE_HEADER = '#event:menu/base/header'
    MENU_BASE_DESC = '#event:menu/base/desc'
    MENU_MISSION = '#event:menu/mission'
    MENU_MISSION_HEADER = '#event:menu/mission/header'
    MENU_MISSION_DESC = '#event:menu/mission/desc'
    MENU_SUBDIVISION = '#event:menu/subdivision'
    MENU_SUBDIVISION_HEADER = '#event:menu/subdivision/header'
    MENU_SUBDIVISION_DESC = '#event:menu/subdivision/desc'
    MENU_ORDERS = '#event:menu/orders'
    MENU_ORDERS_HEADER = '#event:menu/orders/header'
    MENU_ORDERS_DESC = '#event:menu/orders/desc'
    MENU_SHOP = '#event:menu/shop'
    MENU_SHOP_HEADER = '#event:menu/shop/header'
    MENU_SHOP_DESC = '#event:menu/shop/desc'
    MENU_ABOUT = '#event:menu/about'
    MENU_ABOUT_HEADER = '#event:menu/about/header'
    MENU_ABOUT_DESC = '#event:menu/about/desc'
    MENU_BERLIN = '#event:menu/berlin'
    MENU_BERLIN_HEADER = '#event:menu/berlin/header'
    MENU_BERLIN_DESC = '#event:menu/berlin/desc'
    HEADER_TITLE = '#event:header/title'
    SUBDIVISION_INFO = '#event:subdivision/info'
    MISSION_REWARD = '#event:mission/reward'
    MISSION_PROGRESS = '#event:mission/progress'
    MISSION_STATUS_COMPLETED = '#event:mission/status/completed'
    MISSION_STATUS_INPROGRESS = '#event:mission/status/inProgress'
    MISSION_STATUS_LOCKED = '#event:mission/status/locked'
    MISSION_PART = '#event:mission/part'
    MISSION_INFO = '#event:mission/info'
    MISSION_INFOPART = '#event:mission/infoPart'
    SHOPTAB_SPECIALOFFERS = '#event:shopTab/specialOffers'
    SHOPTAB_REGULAROFFERS = '#event:shopTab/regularOffers'
    SHOPTAB_MAXLEVEL = '#event:shopTab/maxLevel'
    ENTRYPOINT_BANNER_HEADER = '#event:entryPoint/banner/header'
    ENTRYPOINT_BANNER_ASSAULT = '#event:entryPoint/banner/assault'
    GOALS_CAPTURE_A_TITLE = '#event:goals/capture_A/title'
    GOALS_CAPTURE_A_DESCRIPTION = '#event:goals/capture_A/description'
    GOALS_CAPTURE_A_PROGRESS = '#event:goals/capture_A/progress'
    GOALS_CAPTURE_A_WIN = '#event:goals/capture_A/win'
    GOALS_CAPTURE_A_WIN_2 = '#event:goals/capture_A/win_2'
    GOALS_CAPTURE_A_LOSE = '#event:goals/capture_A/lose'
    GOALS_CAPTURE_B_TITLE = '#event:goals/capture_B/title'
    GOALS_CAPTURE_B_DESCRIPTION = '#event:goals/capture_B/description'
    GOALS_CAPTURE_B_PROGRESS = '#event:goals/capture_B/progress'
    GOALS_CAPTURE_B_WIN = '#event:goals/capture_B/win'
    GOALS_CAPTURE_B_WIN_2 = '#event:goals/capture_B/win_2'
    GOALS_CAPTURE_B_LOSE = '#event:goals/capture_B/lose'
    GOALS_CAPTURE_C_TITLE = '#event:goals/capture_C/title'
    GOALS_CAPTURE_C_DESCRIPTION = '#event:goals/capture_C/description'
    GOALS_CAPTURE_C_PROGRESS = '#event:goals/capture_C/progress'
    GOALS_CAPTURE_C_WIN = '#event:goals/capture_C/win'
    GOALS_CAPTURE_C_WIN_2 = '#event:goals/capture_C/win_2'
    GOALS_CAPTURE_C_LOSE = '#event:goals/capture_C/lose'
    GOALS_KILL_BOSS_TITLE = '#event:goals/kill_boss/title'
    GOALS_KILL_BOSS_DESCRIPTION = '#event:goals/kill_boss/description'
    GOALS_KILL_BOSS_PROGRESS = '#event:goals/kill_boss/progress'
    GOALS_KILL_BOSS_WIN = '#event:goals/kill_boss/win'
    GOALS_KILL_BOSS_WIN_2 = '#event:goals/kill_boss/win_2'
    GOALS_KILL_BOSS_LOSE = '#event:goals/kill_boss/lose'
    GOALS_DEFEND_OBJ_1_TITLE = '#event:goals/defend_obj_1/title'
    GOALS_DEFEND_OBJ_1_DESCRIPTION = '#event:goals/defend_obj_1/description'
    GOALS_DEFEND_OBJ_1_PROGRESS = '#event:goals/defend_obj_1/progress'
    GOALS_DEFEND_OBJ_1_WIN = '#event:goals/defend_obj_1/win'
    GOALS_DEFEND_OBJ_1_WIN_2 = '#event:goals/defend_obj_1/win_2'
    GOALS_DEFEND_OBJ_1_LOSE = '#event:goals/defend_obj_1/lose'
    GOALS_DEFEND_OBJ_2_TITLE = '#event:goals/defend_obj_2/title'
    GOALS_DEFEND_OBJ_2_DESCRIPTION = '#event:goals/defend_obj_2/description'
    GOALS_DEFEND_OBJ_2_PROGRESS = '#event:goals/defend_obj_2/progress'
    GOALS_DEFEND_OBJ_2_WIN = '#event:goals/defend_obj_2/win'
    GOALS_DEFEND_OBJ_2_WIN_2 = '#event:goals/defend_obj_2/win_2'
    GOALS_DEFEND_OBJ_2_LOSE = '#event:goals/defend_obj_2/lose'
    GOALS_SUBSTRING_CAPTURE_A = '#event:goals/substring/capture_A'
    GOALS_SUBSTRING_CAPTURE_B = '#event:goals/substring/capture_B'
    GOALS_SUBSTRING_CAPTURE_C = '#event:goals/substring/capture_C'
    GOALS_SUBSTRING_KILL_BOSS = '#event:goals/substring/kill_boss'
    GOALS_SUBSTRING_DEFEND_OBJ_1 = '#event:goals/substring/defend_obj_1'
    GOALS_SUBSTRING_DEFEND_OBJ_2 = '#event:goals/substring/defend_obj_2'
    AWARDSCREEN_CLOSEBUTTON = '#event:awardScreen/closeButton'
    AWARDSCREEN_VEHICLE_HEADEREXTRA = '#event:awardScreen/vehicle/headerExtra'
    AWARDSCREEN_VEHICLE_HEADER = '#event:awardScreen/vehicle/header'
    AWARDSCREEN_VEHICLE_BUTTON = '#event:awardScreen/vehicle/button'
    AWARDSCREEN_GENERAL_HEADEREXTRA = '#event:awardScreen/general/headerExtra'
    AWARDSCREEN_GENERAL_HEADER = '#event:awardScreen/general/header'
    AWARDSCREEN_GENERAL_BUTTON = '#event:awardScreen/general/button'
    AWARDSCREEN_PLAYER_HEADEREXTRA = '#event:awardScreen/player/headerExtra'
    AWARDSCREEN_PLAYER_HEADER = '#event:awardScreen/player/header'
    PLAYERPANEL_TEAMMATEINFO = '#event:playerPanel/teammateInfo'
    BERLIN_UNIQMAP = '#event:berlin/uniqMap'
    BERLIN_NEWMAP = '#event:berlin/newMap'
    BERLIN_ACCESS_NAME = '#event:berlin/access/name'
    BERLIN_ACCESS_DESC = '#event:berlin/access/desc'
    BERLIN_ACCESS_DAY = '#event:berlin/access/day'
    BERLIN_ACCESS_LEVEL = '#event:berlin/access/level'
    BERLIN_PRIZE_NAME = '#event:berlin/prize/name'
    BERLIN_PRIZE_DESC = '#event:berlin/prize/desc'
    BERLIN_PRIZE_LABEL = '#event:berlin/prize/label'
    BERLIN_DAY_SHORT = '#event:berlin/day/short'
    BERLIN_STARTED_NAME = '#event:berlin/started/name'
    BERLIN_STARTED_DESC = '#event:berlin/started/desc'
    BERLIN_CARD_NAME = '#event:berlin/card/name'
    BERLIN_PACK_NAME = '#event:berlin/pack/name'
    BERLIN_CARD_ALLGENERAL = '#event:berlin/card/allGeneral'
    BERLIN_CARD_ORDERS1 = '#event:berlin/card/orders1'
    BERLIN_CARD_ORDERS2 = '#event:berlin/card/orders2'
    BERLIN_CARD_BUY = '#event:berlin/card/buy'
    HANGAR_TOOLTIP_NOT_ENOUGH_MONEY_BODY = '#event:hangar/tooltip/not_enough_money/body'
    HANGAR_TOOLTIP_FIGHT_BUTTON_DISABLED_BODY = '#event:hangar/tooltip/fight_button_disabled/body'
    HANGAR_TOOLTIP_COMMANDER_NOT_SELECTED_BODY = '#event:hangar/tooltip/commander_not_selected/body'
    HANGAR_TOOLTIP_COMMANDER_IS_LOCKED_BODY = '#event:hangar/tooltip/commander_is_locked/body'
    HANGAR_TOOLTIP_IN_HERO_TANK_VIEW_BODY = '#event:hangar/tooltip/in_hero_tank_view/body'
    BOT_NAME_G81_PZ_IV_AUSFH_SE20_MT0_ELITE = '#event:bot_name/G81_Pz_IV_AusfH_SE20_Mt0_Elite'
    BOT_NAME_G81_PZ_IV_AUSFH_SE20_MT0_REGULAR = '#event:bot_name/G81_Pz_IV_AusfH_SE20_Mt0_Regular'
    BOT_NAME_G81_PZ_IV_AUSFH_SE20_MT1_REGULAR = '#event:bot_name/G81_Pz_IV_AusfH_SE20_Mt1_Regular'
    BOT_NAME_G81_PZ_IV_AUSFH_SE20_MT1_ELITE = '#event:bot_name/G81_Pz_IV_AusfH_SE20_Mt1_Elite'
    BOT_NAME_G03_PZV_PANTHER_SE20_MT2_REGULAR = '#event:bot_name/G03_PzV_Panther_SE20_Mt2_Regular'
    BOT_NAME_G03_PZV_PANTHER_SE20_MT2_ELITE = '#event:bot_name/G03_PzV_Panther_SE20_Mt2_Elite'
    BOT_NAME_G04_PZVI_TIGER_I_SE20_HT1_REGULAR = '#event:bot_name/G04_PzVI_Tiger_I_SE20_Ht1_Regular'
    BOT_NAME_G04_PZVI_TIGER_I_SE20_HT1_ELITE = '#event:bot_name/G04_PzVI_Tiger_I_SE20_Ht1_Elite'
    BOT_NAME_G16_PZVIB_TIGER_II_SE20_HT2_REGULAR = '#event:bot_name/G16_PzVIB_Tiger_II_SE20_Ht2_Regular'
    BOT_NAME_G16_PZVIB_TIGER_II_SE20_HT2_ELITE = '#event:bot_name/G16_PzVIB_Tiger_II_SE20_Ht2_Elite'
    BOT_NAME_G09_HETZER_SE20_AT0_REGULAR = '#event:bot_name/G09_Hetzer_SE20_At0_Regular'
    BOT_NAME_G05_STUG_40_AUSFG_SE20_AT1_REGULAR = '#event:bot_name/G05_StuG_40_AusfG_SE20_At1_Regular'
    BOT_NAME_G40_NASHORN_SE20_AT2_REGULAR = '#event:bot_name/G40_Nashorn_SE20_At2_Regular'
    BOT_NAME_G18_JAGDPANTHER_SE20_AT3_REGULAR = '#event:bot_name/G18_JagdPanther_SE20_At3_Regular'
    BOT_NAME_G37_FERDINAND_SE20_AT4_ELITE = '#event:bot_name/G37_Ferdinand_SE20_At4_Elite'
    BOT_NAME_G44_JAGDTIGER_SE20_AT5_ELITE = '#event:bot_name/G44_JagdTiger_SE20_At5_Elite'
    BOT_NAME_G19_WESPE_SE20_ART1_REGULAR = '#event:bot_name/G19_Wespe_SE20_Art1_Regular'
    BOT_NAME_G02_HUMMEL_SE20_ART2_REGULAR = '#event:bot_name/G02_Hummel_SE20_Art2_Regular'
    BOT_NAME_G42_MAUS_SE20_HT3_BOSS = '#event:bot_name/G42_Maus_SE20_Ht3_Boss'
    POSTMORTEM_PANEL_HAS_LOCKED_LIVES_MESSAGE_TITLE = '#event:postmortem_panel/has_locked_lives_message_title'
    POSTMORTEM_PANEL_HAS_LOCKED_LIVES_MESSAGE_DESCR = '#event:postmortem_panel/has_locked_lives_message_descr'
    POSTMORTEM_PANEL_NO_LIVES_MESSAGE_TITLE = '#event:postmortem_panel/no_lives_message_title'
    POSTMORTEM_PANEL_NO_LIVES_MESSAGE_DESCR = '#event:postmortem_panel/no_lives_message_descr'
    POSTMORTEM_PANEL_RESPAWN_TIMER_TITLE = '#event:postmortem_panel/respawn_timer_title'
    PUNISHMENTWINDOW_REASON_EVENT_DESERTER = '#event:punishmentWindow/reason/event_deserter'
    PUNISHMENTWINDOW_REASON_EVENT_AFK = '#event:punishmentWindow/reason/event_afk'
    SQUAD_GENERAL_INACTIVE = '#event:squad/general_inactive'
    SQUAD_GENERAL_LOCKED = '#event:squad/general_locked'
    ORDER_FILL = '#event:order/fill'
    ORDER_NOTENOUGH = '#event:order/notEnough'
    ORDER_COUNT = '#event:order/count'
    ORDER_ORFILL = '#event:order/orFill'
    ORDER_REVENUENEXTBATTLE = '#event:order/revenueNextBattle'
    ORDER_X1 = '#event:order/x1'
    ORDER_WINDOW_TITLE = '#event:order/window/title'
    ORDER_SELECTWINDOW_TITLE = '#event:order/selectwindow/title'
    ORDER_WINDOW_FREEDAY = '#event:order/window/freeDay'
    ORDER_WINDOW_FREEDAYDESC = '#event:order/window/freeDayDesc'
    ORDER_WINDOW_PERQUEST = '#event:order/window/perQuest'
    ORDER_WINDOW_PERQUESTDESC = '#event:order/window/perQuestDesc'
    ORDER_WINDOW_TOQUEST = '#event:order/window/toQuest'
    ORDER_WINDOW_NOQUESTS = '#event:order/window/noQuests'
    ORDER_WINDOW_BUY = '#event:order/window/buy'
    ORDER_WINDOW_INPREMIUMSHOP = '#event:order/window/inPremiumShop'
    ORDER_WINDOW_BONUSPACK = '#event:order/window/bonusPack'
    ORDER_WINDOW_BONUSPACKS = '#event:order/window/bonusPacks'
    ORDER_WINDOW_DESC = '#event:order/window/desc'
    ORDER_WINDOW_PACKNAME_BEGINNER = '#event:order/window/packName/beginner'
    ORDER_WINDOW_PACKNAME_SPECIALIST = '#event:order/window/packName/specialist'
    ORDER_WINDOW_PACKNAME_MASTER = '#event:order/window/packName/master'
    ORDER_WINDOW_PACKDESCRIPTION_BEGINNER = '#event:order/window/packDescription/beginner'
    ORDER_WINDOW_PACKDESCRIPTION_SPECIALIST = '#event:order/window/packDescription/specialist'
    ORDER_WINDOW_PACKDESCRIPTION_MASTER = '#event:order/window/packDescription/master'
    ORDER_MODIFIER = '#event:order/modifier'
    ORDER_WINDOW_CARDNAME_TIMER = '#event:order/window/cardName/timer'
    ORDER_WINDOW_CARDNAME_BUY = '#event:order/window/cardName/buy'
    ORDER_WINDOW_CARDNAME_FILL = '#event:order/window/cardName/fill'
    ORDER_WINDOW_CARDDESC_TIMER = '#event:order/window/cardDesc/timer'
    ORDER_WINDOW_CARDDESC_BUY = '#event:order/window/cardDesc/buy'
    ORDER_WINDOW_CARDDESC_FILL = '#event:order/window/cardDesc/fill'
    ORDER_WINDOW_EXCHANGEEQUAL = '#event:order/window/exchangeEqual'
    ORDER_WINDOW_EXCHANGE = '#event:order/window/exchange'
    ORDER_WINDOW_TOKENCOUNT = '#event:order/window/tokenCount'
    ORDER_WINDOW_CARDNAME_EXCHANGE = '#event:order/window/cardName/exchange'
    ORDER_WINDOW_CARDDESC_EXCHANGE = '#event:order/window/cardDesc/exchange'
    ORDER_WINDOW_TOKEN_NOTENOUGHT = '#event:order/window/token/notEnought'
    ORDER_WINDOW_TOKEN_DESCRIPTION = '#event:order/window/token/description'
    ORDER_CONFIRM_BUY = '#event:order/confirm/buy'
    ORDER_CONFIRM_CANCEL = '#event:order/confirm/cancel'
    ORDER_CONFIRM_TITLE = '#event:order/confirm/title'
    ORDER_CONFIRM_SHORTTITLE = '#event:order/confirm/shortTitle'
    ORDER_CONFIRM_SIMPLETITLE = '#event:order/confirm/simpleTitle'
    ORDER_CONFIRM_GIFT = '#event:order/confirm/gift'
    ORDER_CONFIRM_COMPOSITION = '#event:order/confirm/composition'
    ENDBATTLE_TITLE_WIN = '#event:endbattle/title/win'
    ENDBATTLE_TITLE_LOSE = '#event:endbattle/title/lose'
    ENDBATTLE_SUBTITLE_WIN_REASON_1 = '#event:endbattle/subtitle/win_reason_1'
    ENDBATTLE_SUBTITLE_LOSE_REASON_1 = '#event:endbattle/subtitle/lose_reason_1'
    ENDBATTLE_SUBTITLE_LOSE_REASON_2 = '#event:endbattle/subtitle/lose_reason_2'
    ENDBATTLE_SUBTITLE_LOSE_REASON_3 = '#event:endbattle/subtitle/lose_reason_3'
    ENDBATTLE_SUBTITLE_LOSE_REASON_4 = '#event:endbattle/subtitle/lose_reason_4'
    ENDBATTLE_SUBTITLE_LOSE_REASON_5 = '#event:endbattle/subtitle/lose_reason_5'
    MARKERS_DISCOUNT = '#event:markers/discount'
    ABOUT_BLOCK_0_MAIN_TITLE = '#event:about/block/0/main_title'
    ABOUT_BLOCK_0_DESC_0 = '#event:about/block/0/desc/0'
    ABOUT_BLOCK_0_DESC_1 = '#event:about/block/0/desc/1'
    ABOUT_BLOCK_0_DESC_2 = '#event:about/block/0/desc/2'
    ABOUT_BLOCK_1_MAIN_TITLE = '#event:about/block/1/main_title'
    ABOUT_BLOCK_1_TITLE_0 = '#event:about/block/1/title/0'
    ABOUT_BLOCK_1_DESC_0 = '#event:about/block/1/desc/0'
    ABOUT_BLOCK_1_TITLE_1 = '#event:about/block/1/title/1'
    ABOUT_BLOCK_1_DESC_1 = '#event:about/block/1/desc/1'
    ABOUT_BLOCK_1_TITLE_2 = '#event:about/block/1/title/2'
    ABOUT_BLOCK_1_DESC_2 = '#event:about/block/1/desc/2'
    ABOUT_BLOCK_1_TITLE_3 = '#event:about/block/1/title/3'
    ABOUT_BLOCK_1_DESC_3 = '#event:about/block/1/desc/3'
    ABOUT_BLOCK_2_MAIN_TITLE = '#event:about/block/2/main_title'
    ABOUT_BLOCK_2_MAIN_DESC = '#event:about/block/2/main_desc'
    ABOUT_BLOCK_2_TITLE_0 = '#event:about/block/2/title/0'
    ABOUT_BLOCK_2_DESC_0 = '#event:about/block/2/desc/0'
    ABOUT_BLOCK_2_TITLE_1 = '#event:about/block/2/title/1'
    ABOUT_BLOCK_2_DESC_1 = '#event:about/block/2/desc/1'
    ABOUT_BLOCK_2_TITLE_2 = '#event:about/block/2/title/2'
    ABOUT_BLOCK_2_DESC_2 = '#event:about/block/2/desc/2'
    ABOUT_BLOCK_3_MAIN_TITLE = '#event:about/block/3/main_title'
    ABOUT_BLOCK_3_MAIN_DESC = '#event:about/block/3/main_desc'
    ABOUT_BLOCK_3_TITLE_0 = '#event:about/block/3/title/0'
    ABOUT_BLOCK_3_DESC_0 = '#event:about/block/3/desc/0'
    ABOUT_BLOCK_3_TITLE_1 = '#event:about/block/3/title/1'
    ABOUT_BLOCK_3_DESC_1 = '#event:about/block/3/desc/1'
    ABOUT_BLOCK_3_TITLE_2 = '#event:about/block/3/title/2'
    ABOUT_BLOCK_3_DESC_2 = '#event:about/block/3/desc/2'
    ABOUT_BLOCK_3_TITLE_3 = '#event:about/block/3/title/3'
    ABOUT_BLOCK_3_DESC_3 = '#event:about/block/3/desc/3'
    ABOUT_BLOCK_3_TITLE_4 = '#event:about/block/3/title/4'
    ABOUT_BLOCK_3_DESC_4 = '#event:about/block/3/desc/4'
    ABOUT_BLOCK_3_DESC_5 = '#event:about/block/3/desc/5'
    ABOUT_BLOCK_3_DESC_6 = '#event:about/block/3/desc/6'
    ABOUT_BLOCK_3_DESC_7 = '#event:about/block/3/desc/7'
    ABOUT_ENDDATE = '#event:about/endDate'
    ABOUT_TANK_T_34_85 = '#event:about/tank_t_34_85'
    ABOUT_TANK_T_34_85M = '#event:about/tank_t_34_85m'
    ABOUT_TANK_T_44_85 = '#event:about/tank_t_44_85'
    ABOUT_TANK_CHURCHILL_IV = '#event:about/tank_churchill_iv'
    ABOUT_TANK_CHURCHILL_VII = '#event:about/tank_churchill_vii'
    ABOUT_TANK_CHURCHILLBLACK_PRINCE = '#event:about/tank_churchillblack_prince'
    ABOUT_TANK_SU_85M = '#event:about/tank_su_85m'
    ABOUT_TANK_SU_100 = '#event:about/tank_su_100'
    ABOUT_TANK_ISU_122C = '#event:about/tank_isu_122c'
    ABOUT_TANK_M4A2_SHERMAN = '#event:about/tank_m4a2_sherman'
    ABOUT_TANK_M4A2_SHERMAN_JUMBO = '#event:about/tank_m4a2_sherman_jumbo'
    ABOUT_TANK_T26E3 = '#event:about/tank_t26e3'
    ABOUT_TANK_IS = '#event:about/tank_is'
    ABOUT_TANK_IS_2 = '#event:about/tank_is_2'
    ABOUT_TANK_IS_2B = '#event:about/tank_is_2b'
    ABOUT_BLOCK_4_MAIN_TITLE = '#event:about/block/4/main_title'
    ABOUT_BLOCK_4_MAIN_DESC = '#event:about/block/4/main_desc'
    ABOUT_BLOCK_4_TITLE_0 = '#event:about/block/4/title/0'
    ABOUT_BLOCK_4_DESC_0 = '#event:about/block/4/desc/0'
    ABOUT_BLOCK_4_TITLE_1 = '#event:about/block/4/title/1'
    ABOUT_BLOCK_4_DESC_1 = '#event:about/block/4/desc/1'
    ABOUT_BLOCK_4_TITLE_2 = '#event:about/block/4/title/2'
    ABOUT_BLOCK_4_DESC_2 = '#event:about/block/4/desc/2'
    ABOUT_BLOCK_4_TITLE_3 = '#event:about/block/4/title/3'
    ABOUT_BLOCK_4_DESC_3 = '#event:about/block/4/desc/3'
    ABOUT_BLOCK_4_TITLE_4 = '#event:about/block/4/title/4'
    ABOUT_BLOCK_4_DESC_4 = '#event:about/block/4/desc/4'
    ABOUT_BLOCK_4_TITLE_5 = '#event:about/block/4/title/5'
    ABOUT_BLOCK_4_DESC_5 = '#event:about/block/4/desc/5'
    ABOUT_BLOCK_5_MAIN_TITLE = '#event:about/block/5/main_title'
    ABOUT_BLOCK_5_MAIN_DESC = '#event:about/block/5/main_desc'
    ABOUT_BLOCK_5_TITLE_0 = '#event:about/block/5/title/0'
    ABOUT_BLOCK_5_DESC_0 = '#event:about/block/5/desc/0'
    ABOUT_BLOCK_6_MAIN_TITLE = '#event:about/block/6/main_title'
    ABOUT_BLOCK_6_MAIN_DESC = '#event:about/block/6/main_desc'
    ABOUT_BLOCK_6_TITLE_0 = '#event:about/block/6/title/0'
    ABOUT_BLOCK_6_DESC_0 = '#event:about/block/6/desc/0'
    ABOUT_BLOCK_7_MAIN_TITLE = '#event:about/block/7/main_title'
    ABOUT_BLOCK_7_LIST_0 = '#event:about/block/7/list/0'
    ABOUT_BLOCK_7_LIST_1 = '#event:about/block/7/list/1'
    ABOUT_BLOCK_7_LIST_2 = '#event:about/block/7/list/2'
    ABOUT_BLOCK_7_LIST_3 = '#event:about/block/7/list/3'
    ABOUT_BLOCK_8_MAIN_TITLE = '#event:about/block/8/main_title'
    ABOUT_BLOCK_8_LIST_0 = '#event:about/block/8/list/0'
    ABOUT_BLOCK_8_LIST_1 = '#event:about/block/8/list/1'
    ABOUT_BLOCK_8_LIST_2 = '#event:about/block/8/list/2'
    ABOUT_BLOCK_9_MAIN_TITLE = '#event:about/block/9/main_title'
    ABOUT_BLOCK_9_TITLE_0 = '#event:about/block/9/title/0'
    ABOUT_BLOCK_9_DESC_0 = '#event:about/block/9/desc/0'
    ABOUT_BLOCK_9_TITLE_1 = '#event:about/block/9/title/1'
    ABOUT_BLOCK_9_DESC_1 = '#event:about/block/9/desc/1'
    ABOUT_BLOCK_9_TITLE_2 = '#event:about/block/9/title/2'
    ABOUT_BLOCK_9_DESC_2 = '#event:about/block/9/desc/2'
    ABOUT_BLOCK_10_TITLE_0 = '#event:about/block/10/title/0'
    ABOUT_BLOCK_10_DESC_0 = '#event:about/block/10/desc/0'
    ABOUT_BLOCK_10_TITLE_1 = '#event:about/block/10/title/1'
    ABOUT_BLOCK_10_DESC_1 = '#event:about/block/10/desc/1'
    ABOUT_BLOCK_11_MAIN_TITLE = '#event:about/block/11/main_title'
    ABOUT_BLOCK_11_MAIN_DESC = '#event:about/block/11/main_desc'
    ABOUT_BLOCK_11_TITLE_0 = '#event:about/block/11/title/0'
    ABOUT_BLOCK_11_DESC_0 = '#event:about/block/11/desc/0'
    ABOUT_GO_TO_THE_BATTLE = '#event:about/go_to_the_battle'
    ABOUT_TO_PAGE_TOP = '#event:about/to_page_top'
    ABOUT_HERO_TANK = '#event:about/hero_tank'
    ABOUT_AVAILABLE = '#event:about/available'
    ABOUT_MORE_INFO = '#event:about/more_info'
    LOADING_EVENT1_HEADER_1 = '#event:loading/event1/header/1'
    LOADING_EVENT1_HEADER_2 = '#event:loading/event1/header/2'
    LOADING_EVENT1_HEADER_3 = '#event:loading/event1/header/3'
    LOADING_EVENT1_HEADER_4 = '#event:loading/event1/header/4'
    LOADING_EVENT1_HEADER_5 = '#event:loading/event1/header/5'
    LOADING_EVENT1_HEADER_6 = '#event:loading/event1/header/6'
    FUELWINDOW_BUYPRICE = '#event:fuelWindow/buyPrice'
    ALL_ENUM = (NOTIFICATION_BOMBING,
     NOTIFICATION_OBJ_COMPLETE,
     NOTIFICATION_DEATHZONE,
     RADIALMENU_CHATABOUT,
     RADIALMENU_CHATWITH,
     RADIALMENU_ALLIES,
     RADIALMENU_NEXTPAGE,
     RESULTSCREEN_TAB_0,
     RESULTSCREEN_TAB_1,
     RESULTSCREEN_STATS_DAMAGE,
     RESULTSCREEN_STATS_KILL,
     RESULTSCREEN_STATS_ASSIST,
     RESULTSCREEN_STATS_ARMOR,
     RESULTSCREEN_OBJECTIVES_HEADER,
     RESULTSCREEN_POINTS_WITHOUTBONUS,
     RESULTSCREEN_CLOSE,
     RESULTSCREEN_ALIVE,
     RESULTSCREEN_DEAD,
     RESULTSCREEN_KILLEDBY,
     RESULTSCREEN_BATTLETYPE,
     RESULTSCREEN_NEXT,
     RESULTSCREEN_ALLIES,
     RESULTSCREEN_FRONTMISSIONHEADER,
     RESULTSCREEN_FRONTMISSIONEARNED,
     RESULTSCREEN_GENERALMISSIONEARNED,
     RESULTSCREEN_TOOLTIP_KILLS_HEADER,
     RESULTSCREEN_TOOLTIP_KILLS_DESCR,
     RESULTSCREEN_TOOLTIP_DAMAGE_HEADER,
     RESULTSCREEN_TOOLTIP_DAMAGE_DESCR,
     RESULTSCREEN_TOOLTIP_ASSIST_HEADER,
     RESULTSCREEN_TOOLTIP_ASSIST_DESCR,
     RESULTSCREEN_TOOLTIP_ARMOR_HEADER,
     RESULTSCREEN_TOOLTIP_ARMOR_DESCR,
     RESULTSCREEN_TOOLTIP_VEHICLES_HEADER,
     RESULTSCREEN_TOOLTIP_VEHICLES_DESCR,
     RESULTSCREEN_TOOLTIP_OBJECTIVES_HEADER,
     RESULTSCREEN_TOOLTIP_OBJECTIVES_DESCR,
     RESULTSCREEN_MISSIONS_COMPLETED,
     RESULTSCREEN_MISSIONS_PROGRESS,
     RESULTSCREEN_MISSIONS_PROGRESSCREW,
     VOICEOVER_LANGUAGE_CODE,
     NEWS_BUTTON,
     HANGAR_EXIT,
     HANGAR_CLOSE,
     HANGAR_BACK,
     HANGAR_BACKTO,
     GENERALS_INFOBTN,
     GENERALS_ENERGY,
     VEHICLE_SELECT_TAB_TEAM,
     VEHICLE_SELECT_TAB_MAP,
     VEHICLE_SELECT_RESPAWNHINT_TITLE,
     VEHICLE_SELECT_RESPAWNHINT_SELECTED,
     VEHICLE_SELECT_RESPAWNHINT_AVAILABLE,
     GENERAL_BUY_PAGE_HEADER,
     GENERAL_BUY_PAGE_TEXT,
     GENERAL_BUY_PAGE_LEVEL_1_BUNDLENAME,
     GENERAL_BUY_PAGE_LEVEL_2_BUNDLENAME,
     GENERAL_BUY_PAGE_LEVEL_REACHED,
     GENERAL_BUY_PAGE_LEVEL_NOTREACHED,
     GENERAL_BUY_PAGE_LEVEL_BOUGHT,
     GENERALS_READY,
     GENERALS_INBATTLE,
     GENERALS_INPLATOON,
     TANK_PARAMS_AVGDAMAGEPERMINUTE,
     TANK_PARAMS_SPEEDLIMITS,
     TANK_PARAMS_ARMOR,
     TANK_PARAMS_DESC_ARMOR,
     TANK_PARAMS_MAXHEALTH,
     TANK_PARAMS_DESC_MAXHEALTH,
     TANK_PARAMS_CLIPFIRERATE,
     TANK_PARAMS_DESC_CLIPFIRERATE,
     TANK_PARAMS_AVGDAMAGE,
     TANK_PARAMS_DESC_AVGDAMAGE,
     TANK_PARAMS_PIERCINGPOWER,
     TANK_PARAMS_DESC_PIERCINGPOWER,
     TANK_PARAMS_ACCURACY,
     TANK_PARAMS_DESC_ACCURACY,
     TANK_PARAMS_MOBILITY,
     TANK_PARAMS_DESC_MOBILITY,
     SELECTORTOOLTIP_HEADER,
     SELECTORTOOLTIP_DESCRIPTION,
     SELECTORTOOLTIP_ASSUREDLOWPERFORMANCE_TITLE,
     SELECTORTOOLTIP_ASSUREDLOWPERFORMANCE_DESCRIPTION,
     SELECTORTOOLTIP_POSSIBLELOWPERFORMANCE_TITLE,
     SELECTORTOOLTIP_POSSIBLELOWPERFORMANCE_DESCRIPTION,
     SELECTORTOOLTIP_INFORMATIVELOWPERFORMANCE_DESCRIPTION,
     SELECTORTOOLTIP_FROZEN,
     TITLE,
     UNITPROGRESSION_TITLE,
     UNITPROGRESSION_GOTPOINTS,
     UNITPROGRESSION_MAX,
     EVENTPROGRESSION_TITLE,
     EVENTPROGRESSION_GOTPOINTS,
     EVENTPROGRESSION_MAX,
     UNIT_DESCRIPTION_0,
     UNIT_DESCRIPTION_1,
     UNIT_DESCRIPTION_2,
     UNIT_DESCRIPTION_3,
     UNIT_DESCRIPTION_4,
     UNIT_NAME_0,
     UNIT_NAME_UPPER_0,
     UNIT_NAME_1,
     UNIT_NAME_UPPER_1,
     UNIT_NAME_2,
     UNIT_NAME_UPPER_2,
     UNIT_NAME_3,
     UNIT_NAME_UPPER_3,
     UNIT_NAME_4,
     UNIT_NAME_UPPER_4,
     PREVIEWWINDOW_BUYBUTTON_LABEL,
     PREVIEWWINDOW_ACTIONBUTTON_LABEL,
     PREVIEWWINDOW_OR,
     PREVIEWWINDOW_MESSAGE,
     PREVIEWWINDOW_SHOP_MESSAGE,
     PREVIEWWINDOW_SHOWBUTTON_LABEL,
     PREVIEWWINDOW_SHOWBUTTON_HEADER,
     PREVIEWWINDOW_RESTOREBUTTON_HEADER,
     PREVIEWWINDOW_RESTOREBUTTON_LABEL,
     CHARACTERISTICSPANEL_PROS,
     CHARACTERISTICSPANEL_CONS,
     CHARACTERISTICSPANEL_SKILLS,
     MENU_BASE,
     MENU_BASE_HEADER,
     MENU_BASE_DESC,
     MENU_MISSION,
     MENU_MISSION_HEADER,
     MENU_MISSION_DESC,
     MENU_SUBDIVISION,
     MENU_SUBDIVISION_HEADER,
     MENU_SUBDIVISION_DESC,
     MENU_ORDERS,
     MENU_ORDERS_HEADER,
     MENU_ORDERS_DESC,
     MENU_SHOP,
     MENU_SHOP_HEADER,
     MENU_SHOP_DESC,
     MENU_ABOUT,
     MENU_ABOUT_HEADER,
     MENU_ABOUT_DESC,
     MENU_BERLIN,
     MENU_BERLIN_HEADER,
     MENU_BERLIN_DESC,
     HEADER_TITLE,
     SUBDIVISION_INFO,
     MISSION_REWARD,
     MISSION_PROGRESS,
     MISSION_STATUS_COMPLETED,
     MISSION_STATUS_INPROGRESS,
     MISSION_STATUS_LOCKED,
     MISSION_PART,
     MISSION_INFO,
     MISSION_INFOPART,
     SHOPTAB_SPECIALOFFERS,
     SHOPTAB_REGULAROFFERS,
     SHOPTAB_MAXLEVEL,
     ENTRYPOINT_BANNER_HEADER,
     ENTRYPOINT_BANNER_ASSAULT,
     GOALS_CAPTURE_A_TITLE,
     GOALS_CAPTURE_A_DESCRIPTION,
     GOALS_CAPTURE_A_PROGRESS,
     GOALS_CAPTURE_A_WIN,
     GOALS_CAPTURE_A_WIN_2,
     GOALS_CAPTURE_A_LOSE,
     GOALS_CAPTURE_B_TITLE,
     GOALS_CAPTURE_B_DESCRIPTION,
     GOALS_CAPTURE_B_PROGRESS,
     GOALS_CAPTURE_B_WIN,
     GOALS_CAPTURE_B_WIN_2,
     GOALS_CAPTURE_B_LOSE,
     GOALS_CAPTURE_C_TITLE,
     GOALS_CAPTURE_C_DESCRIPTION,
     GOALS_CAPTURE_C_PROGRESS,
     GOALS_CAPTURE_C_WIN,
     GOALS_CAPTURE_C_WIN_2,
     GOALS_CAPTURE_C_LOSE,
     GOALS_KILL_BOSS_TITLE,
     GOALS_KILL_BOSS_DESCRIPTION,
     GOALS_KILL_BOSS_PROGRESS,
     GOALS_KILL_BOSS_WIN,
     GOALS_KILL_BOSS_WIN_2,
     GOALS_KILL_BOSS_LOSE,
     GOALS_DEFEND_OBJ_1_TITLE,
     GOALS_DEFEND_OBJ_1_DESCRIPTION,
     GOALS_DEFEND_OBJ_1_PROGRESS,
     GOALS_DEFEND_OBJ_1_WIN,
     GOALS_DEFEND_OBJ_1_WIN_2,
     GOALS_DEFEND_OBJ_1_LOSE,
     GOALS_DEFEND_OBJ_2_TITLE,
     GOALS_DEFEND_OBJ_2_DESCRIPTION,
     GOALS_DEFEND_OBJ_2_PROGRESS,
     GOALS_DEFEND_OBJ_2_WIN,
     GOALS_DEFEND_OBJ_2_WIN_2,
     GOALS_DEFEND_OBJ_2_LOSE,
     GOALS_SUBSTRING_CAPTURE_A,
     GOALS_SUBSTRING_CAPTURE_B,
     GOALS_SUBSTRING_CAPTURE_C,
     GOALS_SUBSTRING_KILL_BOSS,
     GOALS_SUBSTRING_DEFEND_OBJ_1,
     GOALS_SUBSTRING_DEFEND_OBJ_2,
     AWARDSCREEN_CLOSEBUTTON,
     AWARDSCREEN_VEHICLE_HEADEREXTRA,
     AWARDSCREEN_VEHICLE_HEADER,
     AWARDSCREEN_VEHICLE_BUTTON,
     AWARDSCREEN_GENERAL_HEADEREXTRA,
     AWARDSCREEN_GENERAL_HEADER,
     AWARDSCREEN_GENERAL_BUTTON,
     AWARDSCREEN_PLAYER_HEADEREXTRA,
     AWARDSCREEN_PLAYER_HEADER,
     PLAYERPANEL_TEAMMATEINFO,
     BERLIN_UNIQMAP,
     BERLIN_NEWMAP,
     BERLIN_ACCESS_NAME,
     BERLIN_ACCESS_DESC,
     BERLIN_ACCESS_DAY,
     BERLIN_ACCESS_LEVEL,
     BERLIN_PRIZE_NAME,
     BERLIN_PRIZE_DESC,
     BERLIN_PRIZE_LABEL,
     BERLIN_DAY_SHORT,
     BERLIN_STARTED_NAME,
     BERLIN_STARTED_DESC,
     BERLIN_CARD_NAME,
     BERLIN_PACK_NAME,
     BERLIN_CARD_ALLGENERAL,
     BERLIN_CARD_ORDERS1,
     BERLIN_CARD_ORDERS2,
     BERLIN_CARD_BUY,
     HANGAR_TOOLTIP_NOT_ENOUGH_MONEY_BODY,
     HANGAR_TOOLTIP_FIGHT_BUTTON_DISABLED_BODY,
     HANGAR_TOOLTIP_COMMANDER_NOT_SELECTED_BODY,
     HANGAR_TOOLTIP_COMMANDER_IS_LOCKED_BODY,
     HANGAR_TOOLTIP_IN_HERO_TANK_VIEW_BODY,
     BOT_NAME_G81_PZ_IV_AUSFH_SE20_MT0_ELITE,
     BOT_NAME_G81_PZ_IV_AUSFH_SE20_MT0_REGULAR,
     BOT_NAME_G81_PZ_IV_AUSFH_SE20_MT1_REGULAR,
     BOT_NAME_G81_PZ_IV_AUSFH_SE20_MT1_ELITE,
     BOT_NAME_G03_PZV_PANTHER_SE20_MT2_REGULAR,
     BOT_NAME_G03_PZV_PANTHER_SE20_MT2_ELITE,
     BOT_NAME_G04_PZVI_TIGER_I_SE20_HT1_REGULAR,
     BOT_NAME_G04_PZVI_TIGER_I_SE20_HT1_ELITE,
     BOT_NAME_G16_PZVIB_TIGER_II_SE20_HT2_REGULAR,
     BOT_NAME_G16_PZVIB_TIGER_II_SE20_HT2_ELITE,
     BOT_NAME_G09_HETZER_SE20_AT0_REGULAR,
     BOT_NAME_G05_STUG_40_AUSFG_SE20_AT1_REGULAR,
     BOT_NAME_G40_NASHORN_SE20_AT2_REGULAR,
     BOT_NAME_G18_JAGDPANTHER_SE20_AT3_REGULAR,
     BOT_NAME_G37_FERDINAND_SE20_AT4_ELITE,
     BOT_NAME_G44_JAGDTIGER_SE20_AT5_ELITE,
     BOT_NAME_G19_WESPE_SE20_ART1_REGULAR,
     BOT_NAME_G02_HUMMEL_SE20_ART2_REGULAR,
     BOT_NAME_G42_MAUS_SE20_HT3_BOSS,
     POSTMORTEM_PANEL_HAS_LOCKED_LIVES_MESSAGE_TITLE,
     POSTMORTEM_PANEL_HAS_LOCKED_LIVES_MESSAGE_DESCR,
     POSTMORTEM_PANEL_NO_LIVES_MESSAGE_TITLE,
     POSTMORTEM_PANEL_NO_LIVES_MESSAGE_DESCR,
     POSTMORTEM_PANEL_RESPAWN_TIMER_TITLE,
     PUNISHMENTWINDOW_REASON_EVENT_DESERTER,
     PUNISHMENTWINDOW_REASON_EVENT_AFK,
     SQUAD_GENERAL_INACTIVE,
     SQUAD_GENERAL_LOCKED,
     ORDER_FILL,
     ORDER_NOTENOUGH,
     ORDER_COUNT,
     ORDER_ORFILL,
     ORDER_REVENUENEXTBATTLE,
     ORDER_X1,
     ORDER_WINDOW_TITLE,
     ORDER_SELECTWINDOW_TITLE,
     ORDER_WINDOW_FREEDAY,
     ORDER_WINDOW_FREEDAYDESC,
     ORDER_WINDOW_PERQUEST,
     ORDER_WINDOW_PERQUESTDESC,
     ORDER_WINDOW_TOQUEST,
     ORDER_WINDOW_NOQUESTS,
     ORDER_WINDOW_BUY,
     ORDER_WINDOW_INPREMIUMSHOP,
     ORDER_WINDOW_BONUSPACK,
     ORDER_WINDOW_BONUSPACKS,
     ORDER_WINDOW_DESC,
     ORDER_WINDOW_PACKNAME_BEGINNER,
     ORDER_WINDOW_PACKNAME_SPECIALIST,
     ORDER_WINDOW_PACKNAME_MASTER,
     ORDER_WINDOW_PACKDESCRIPTION_BEGINNER,
     ORDER_WINDOW_PACKDESCRIPTION_SPECIALIST,
     ORDER_WINDOW_PACKDESCRIPTION_MASTER,
     ORDER_MODIFIER,
     ORDER_WINDOW_CARDNAME_TIMER,
     ORDER_WINDOW_CARDNAME_BUY,
     ORDER_WINDOW_CARDNAME_FILL,
     ORDER_WINDOW_CARDDESC_TIMER,
     ORDER_WINDOW_CARDDESC_BUY,
     ORDER_WINDOW_CARDDESC_FILL,
     ORDER_WINDOW_EXCHANGEEQUAL,
     ORDER_WINDOW_EXCHANGE,
     ORDER_WINDOW_TOKENCOUNT,
     ORDER_WINDOW_CARDNAME_EXCHANGE,
     ORDER_WINDOW_CARDDESC_EXCHANGE,
     ORDER_WINDOW_TOKEN_NOTENOUGHT,
     ORDER_WINDOW_TOKEN_DESCRIPTION,
     ORDER_CONFIRM_BUY,
     ORDER_CONFIRM_CANCEL,
     ORDER_CONFIRM_TITLE,
     ORDER_CONFIRM_SHORTTITLE,
     ORDER_CONFIRM_SIMPLETITLE,
     ORDER_CONFIRM_GIFT,
     ORDER_CONFIRM_COMPOSITION,
     ENDBATTLE_TITLE_WIN,
     ENDBATTLE_TITLE_LOSE,
     ENDBATTLE_SUBTITLE_WIN_REASON_1,
     ENDBATTLE_SUBTITLE_LOSE_REASON_1,
     ENDBATTLE_SUBTITLE_LOSE_REASON_2,
     ENDBATTLE_SUBTITLE_LOSE_REASON_3,
     ENDBATTLE_SUBTITLE_LOSE_REASON_4,
     ENDBATTLE_SUBTITLE_LOSE_REASON_5,
     MARKERS_DISCOUNT,
     ABOUT_BLOCK_0_MAIN_TITLE,
     ABOUT_BLOCK_0_DESC_0,
     ABOUT_BLOCK_0_DESC_1,
     ABOUT_BLOCK_0_DESC_2,
     ABOUT_BLOCK_1_MAIN_TITLE,
     ABOUT_BLOCK_1_TITLE_0,
     ABOUT_BLOCK_1_DESC_0,
     ABOUT_BLOCK_1_TITLE_1,
     ABOUT_BLOCK_1_DESC_1,
     ABOUT_BLOCK_1_TITLE_2,
     ABOUT_BLOCK_1_DESC_2,
     ABOUT_BLOCK_1_TITLE_3,
     ABOUT_BLOCK_1_DESC_3,
     ABOUT_BLOCK_2_MAIN_TITLE,
     ABOUT_BLOCK_2_MAIN_DESC,
     ABOUT_BLOCK_2_TITLE_0,
     ABOUT_BLOCK_2_DESC_0,
     ABOUT_BLOCK_2_TITLE_1,
     ABOUT_BLOCK_2_DESC_1,
     ABOUT_BLOCK_2_TITLE_2,
     ABOUT_BLOCK_2_DESC_2,
     ABOUT_BLOCK_3_MAIN_TITLE,
     ABOUT_BLOCK_3_MAIN_DESC,
     ABOUT_BLOCK_3_TITLE_0,
     ABOUT_BLOCK_3_DESC_0,
     ABOUT_BLOCK_3_TITLE_1,
     ABOUT_BLOCK_3_DESC_1,
     ABOUT_BLOCK_3_TITLE_2,
     ABOUT_BLOCK_3_DESC_2,
     ABOUT_BLOCK_3_TITLE_3,
     ABOUT_BLOCK_3_DESC_3,
     ABOUT_BLOCK_3_TITLE_4,
     ABOUT_BLOCK_3_DESC_4,
     ABOUT_BLOCK_3_DESC_5,
     ABOUT_BLOCK_3_DESC_6,
     ABOUT_BLOCK_3_DESC_7,
     ABOUT_ENDDATE,
     ABOUT_TANK_T_34_85,
     ABOUT_TANK_T_34_85M,
     ABOUT_TANK_T_44_85,
     ABOUT_TANK_CHURCHILL_IV,
     ABOUT_TANK_CHURCHILL_VII,
     ABOUT_TANK_CHURCHILLBLACK_PRINCE,
     ABOUT_TANK_SU_85M,
     ABOUT_TANK_SU_100,
     ABOUT_TANK_ISU_122C,
     ABOUT_TANK_M4A2_SHERMAN,
     ABOUT_TANK_M4A2_SHERMAN_JUMBO,
     ABOUT_TANK_T26E3,
     ABOUT_TANK_IS,
     ABOUT_TANK_IS_2,
     ABOUT_TANK_IS_2B,
     ABOUT_BLOCK_4_MAIN_TITLE,
     ABOUT_BLOCK_4_MAIN_DESC,
     ABOUT_BLOCK_4_TITLE_0,
     ABOUT_BLOCK_4_DESC_0,
     ABOUT_BLOCK_4_TITLE_1,
     ABOUT_BLOCK_4_DESC_1,
     ABOUT_BLOCK_4_TITLE_2,
     ABOUT_BLOCK_4_DESC_2,
     ABOUT_BLOCK_4_TITLE_3,
     ABOUT_BLOCK_4_DESC_3,
     ABOUT_BLOCK_4_TITLE_4,
     ABOUT_BLOCK_4_DESC_4,
     ABOUT_BLOCK_4_TITLE_5,
     ABOUT_BLOCK_4_DESC_5,
     ABOUT_BLOCK_5_MAIN_TITLE,
     ABOUT_BLOCK_5_MAIN_DESC,
     ABOUT_BLOCK_5_TITLE_0,
     ABOUT_BLOCK_5_DESC_0,
     ABOUT_BLOCK_6_MAIN_TITLE,
     ABOUT_BLOCK_6_MAIN_DESC,
     ABOUT_BLOCK_6_TITLE_0,
     ABOUT_BLOCK_6_DESC_0,
     ABOUT_BLOCK_7_MAIN_TITLE,
     ABOUT_BLOCK_7_LIST_0,
     ABOUT_BLOCK_7_LIST_1,
     ABOUT_BLOCK_7_LIST_2,
     ABOUT_BLOCK_7_LIST_3,
     ABOUT_BLOCK_8_MAIN_TITLE,
     ABOUT_BLOCK_8_LIST_0,
     ABOUT_BLOCK_8_LIST_1,
     ABOUT_BLOCK_8_LIST_2,
     ABOUT_BLOCK_9_MAIN_TITLE,
     ABOUT_BLOCK_9_TITLE_0,
     ABOUT_BLOCK_9_DESC_0,
     ABOUT_BLOCK_9_TITLE_1,
     ABOUT_BLOCK_9_DESC_1,
     ABOUT_BLOCK_9_TITLE_2,
     ABOUT_BLOCK_9_DESC_2,
     ABOUT_BLOCK_10_TITLE_0,
     ABOUT_BLOCK_10_DESC_0,
     ABOUT_BLOCK_10_TITLE_1,
     ABOUT_BLOCK_10_DESC_1,
     ABOUT_BLOCK_11_MAIN_TITLE,
     ABOUT_BLOCK_11_MAIN_DESC,
     ABOUT_BLOCK_11_TITLE_0,
     ABOUT_BLOCK_11_DESC_0,
     ABOUT_GO_TO_THE_BATTLE,
     ABOUT_TO_PAGE_TOP,
     ABOUT_HERO_TANK,
     ABOUT_AVAILABLE,
     ABOUT_MORE_INFO,
     LOADING_EVENT1_HEADER_1,
     LOADING_EVENT1_HEADER_2,
     LOADING_EVENT1_HEADER_3,
     LOADING_EVENT1_HEADER_4,
     LOADING_EVENT1_HEADER_5,
     LOADING_EVENT1_HEADER_6,
     FUELWINDOW_BUYPRICE)
    GOALS_ALL_TITLE_ENUM = (GOALS_CAPTURE_A_TITLE,
     GOALS_CAPTURE_B_TITLE,
     GOALS_CAPTURE_C_TITLE,
     GOALS_KILL_BOSS_TITLE,
     GOALS_DEFEND_OBJ_1_TITLE,
     GOALS_DEFEND_OBJ_2_TITLE)
    GOALS_ALL_DESCRIPTION_ENUM = (GOALS_CAPTURE_A_DESCRIPTION,
     GOALS_CAPTURE_B_DESCRIPTION,
     GOALS_CAPTURE_C_DESCRIPTION,
     GOALS_KILL_BOSS_DESCRIPTION,
     GOALS_DEFEND_OBJ_1_DESCRIPTION,
     GOALS_DEFEND_OBJ_2_DESCRIPTION)
    GOALS_ALL_PROGRESS_ENUM = (GOALS_CAPTURE_A_PROGRESS,
     GOALS_CAPTURE_B_PROGRESS,
     GOALS_CAPTURE_C_PROGRESS,
     GOALS_KILL_BOSS_PROGRESS,
     GOALS_DEFEND_OBJ_1_PROGRESS,
     GOALS_DEFEND_OBJ_2_PROGRESS)
    GOALS_ALL_WIN_ENUM = (GOALS_CAPTURE_A_WIN,
     GOALS_CAPTURE_B_WIN,
     GOALS_CAPTURE_C_WIN,
     GOALS_KILL_BOSS_WIN,
     GOALS_DEFEND_OBJ_1_WIN,
     GOALS_DEFEND_OBJ_2_WIN)
    GOALS_ALL_LOSE_ENUM = (GOALS_CAPTURE_A_LOSE,
     GOALS_CAPTURE_B_LOSE,
     GOALS_CAPTURE_C_LOSE,
     GOALS_KILL_BOSS_LOSE,
     GOALS_DEFEND_OBJ_1_LOSE,
     GOALS_DEFEND_OBJ_2_LOSE)
    UNIT_NAME_ENUM = (UNIT_NAME_0,
     UNIT_NAME_UPPER_0,
     UNIT_NAME_1,
     UNIT_NAME_UPPER_1,
     UNIT_NAME_2,
     UNIT_NAME_UPPER_2,
     UNIT_NAME_3,
     UNIT_NAME_UPPER_3,
     UNIT_NAME_4,
     UNIT_NAME_UPPER_4)
    GOALS_ALL_WIN_ENUM = (GOALS_CAPTURE_A_WIN,
     GOALS_CAPTURE_B_WIN,
     GOALS_CAPTURE_C_WIN,
     GOALS_KILL_BOSS_WIN,
     GOALS_DEFEND_OBJ_1_WIN,
     GOALS_DEFEND_OBJ_2_WIN)
    GOALS_ALL_DESCRIPTION_ENUM = (GOALS_CAPTURE_A_DESCRIPTION,
     GOALS_CAPTURE_B_DESCRIPTION,
     GOALS_CAPTURE_C_DESCRIPTION,
     GOALS_KILL_BOSS_DESCRIPTION,
     GOALS_DEFEND_OBJ_1_DESCRIPTION,
     GOALS_DEFEND_OBJ_2_DESCRIPTION)
    GOALS_ALL_LOSE_ENUM = (GOALS_CAPTURE_A_LOSE,
     GOALS_CAPTURE_B_LOSE,
     GOALS_CAPTURE_C_LOSE,
     GOALS_KILL_BOSS_LOSE,
     GOALS_DEFEND_OBJ_1_LOSE,
     GOALS_DEFEND_OBJ_2_LOSE)
    GOALS_ALL_PROGRESS_ENUM = (GOALS_CAPTURE_A_PROGRESS,
     GOALS_CAPTURE_B_PROGRESS,
     GOALS_CAPTURE_C_PROGRESS,
     GOALS_KILL_BOSS_PROGRESS,
     GOALS_DEFEND_OBJ_1_PROGRESS,
     GOALS_DEFEND_OBJ_2_PROGRESS)

    @classmethod
    def all(cls, key0):
        outcome = '#event:{}'.format(key0)
        if outcome not in cls.ALL_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def getGoalTitle(cls, goalID):
        outcome = '#event:goals/{}/title'.format(goalID)
        if outcome not in cls.GOALS_ALL_TITLE_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def getGoalDescription(cls, goalID):
        outcome = '#event:goals/{}/description'.format(goalID)
        if outcome not in cls.GOALS_ALL_DESCRIPTION_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def getGoalProgress(cls, goalID):
        outcome = '#event:goals/{}/progress'.format(goalID)
        if outcome not in cls.GOALS_ALL_PROGRESS_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def getGoalWin(cls, goalID):
        outcome = '#event:goals/{}/win'.format(goalID)
        if outcome not in cls.GOALS_ALL_WIN_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def getGoalLose(cls, goalID):
        outcome = '#event:goals/{}/lose'.format(goalID)
        if outcome not in cls.GOALS_ALL_LOSE_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def getUnitName(cls, unitID):
        outcome = '#event:unit/name/{}'.format(unitID)
        if outcome not in cls.UNIT_NAME_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def hasGoalWin(cls, goalID):
        outcome = '#event:goals/{}/win'.format(goalID)
        return outcome in cls.GOALS_ALL_WIN_ENUM

    @classmethod
    def hasGoalDescription(cls, goalID):
        outcome = '#event:goals/{}/description'.format(goalID)
        return outcome in cls.GOALS_ALL_DESCRIPTION_ENUM

    @classmethod
    def hasGoalLose(cls, goalID):
        outcome = '#event:goals/{}/lose'.format(goalID)
        return outcome in cls.GOALS_ALL_LOSE_ENUM

    @classmethod
    def hasGoalProgress(cls, goalID):
        outcome = '#event:goals/{}/progress'.format(goalID)
        return outcome in cls.GOALS_ALL_PROGRESS_ENUM
