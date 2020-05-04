# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/secret_event/sound_constants.py
from gui.Scaleform.framework.entities.view_sound import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER

class SOUND(CONST_CONTAINER):
    SECRET_EVENT_HANGAR_SPACE = 'ev_2020_secret_event_hangar'
    SECRET_EVENT_AWARD_SPACE = 'ev_2020_secret_event_award'
    SECRET_EVENT_TANK_SPACE = 'ev_2020_secret_event_tank'
    SECRET_EVENT_SHOP_SPACE = 'ev_2020_secret_event_shop'
    SECRET_EVENT_BERLIN_SPACE = 'ev_2020_secret_event_berlin'
    HANGAR_SPACE_STATE = 'STATE_hangar_view'
    BERLIN_STATE = 'STATE_ev_2020_secret_event_hangar_berlin'
    HANGAR_OVERLAY_STATE = 'STATE_overlay_hangar_general'
    TANK_PREVIEW_STATE = 'STATE_hangar_tank_view'
    SHOP_STATE = 'STATE_hangar_place'
    VIDEO_OVERLAY_STATE = 'STATE_video_overlay'
    SHOP_ENTER_EVENT = 'shop_enter'
    SHOP_EXIT_EVENT = 'shop_exit'
    SECRET_EVENT_BANNER_SOUND_EVENT = 'ev_2020_secret_event_hangar_ui_banner'
    SECRET_EVENT_TEAM_HIGHLIGHT_SOUND_EVENT = 'ev_2020_secret_event_hangar_ui_team_highlight'
    SECRET_EVENT_MISSION_PROGRESS_SOUND_EVENT = 'ev_2020_secret_event_hangar_ui_team_progress_bar'
    SECRET_EVENT_ORDER_CONFIRM_SOUND_EVENT = 'ev_2020_secret_event_hangar_ui_anim_order'
    SECRET_EVENT_POSTBATTLE_EFFICIENCY_SOUND_EVENT = 'ev_2020_secret_event_hangar_ui_postbattle_effectivity'
    SECRET_EVENT_POSTBATTLE_MAIN_POINTS_SOUND_EVENT = 'ev_2020_secret_event_hangar_ui_postbattle_main_points'
    SECRET_EVENT_POSTBATTLE_PRIKAZ_SOUND_EVENT = 'ev_2020_secret_event_hangar_ui_postbattle_main_prikaz'
    SECRET_EVENT_POSTBATTLE_PROGRESS_BAR_SOUND_EVENT = 'ev_2020_secret_event_hangar_ui_postbattle_progress_bar'
    SECRET_EVENT_POSTBATTLE_MAIN_POINTS_NO_PRIKAZ_SOUND_EVENT = 'ev_2020_secret_event_hangar_ui_postbattlemain_points_no_prikaz'
    SECRET_EVENT_POSTBATTLE_SUBDIVISION_BAR_SOUND_EVENT = 'ev_2020_secret_event_hangar_ui_postbattle_slide'
    SECRET_EVENT_POSTBATTLE_NO_PRIKAZ_SOUND_EVENT = 'ev_2020_secret_event_hangar_ui_postbattle_notification_no_prikaz'


AWARD_SETTINGS = CommonSoundSpaceSettings(name=SOUND.SECRET_EVENT_AWARD_SPACE, entranceStates={SOUND.HANGAR_OVERLAY_STATE: '{}_on'.format(SOUND.HANGAR_OVERLAY_STATE),
 SOUND.SHOP_STATE: '{}_garage'.format(SOUND.SHOP_STATE)}, exitStates={SOUND.HANGAR_OVERLAY_STATE: '{}_off'.format(SOUND.HANGAR_OVERLAY_STATE)}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
BUYING_SETTINGS = CommonSoundSpaceSettings(name=SOUND.SECRET_EVENT_SHOP_SPACE, entranceStates={SOUND.SHOP_STATE: '{}_shop'.format(SOUND.SHOP_STATE)}, exitStates={SOUND.SHOP_STATE: '{}_garage'.format(SOUND.SHOP_STATE)}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=SOUND.SHOP_ENTER_EVENT, exitEvent=SOUND.SHOP_EXIT_EVENT)
ACTION_WIDGET_SETTINGS = CommonSoundSpaceSettings(name=SOUND.SECRET_EVENT_TANK_SPACE, entranceStates={SOUND.HANGAR_OVERLAY_STATE: '{}_off'.format(SOUND.HANGAR_OVERLAY_STATE),
 SOUND.TANK_PREVIEW_STATE: '{}_proposal'.format(SOUND.TANK_PREVIEW_STATE)}, exitStates={SOUND.TANK_PREVIEW_STATE: '{}_main'.format(SOUND.TANK_PREVIEW_STATE)}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
ACTION_VIEW_SETTINGS = CommonSoundSpaceSettings(name=SOUND.SECRET_EVENT_HANGAR_SPACE, entranceStates={SOUND.HANGAR_OVERLAY_STATE: '{}_on'.format(SOUND.HANGAR_OVERLAY_STATE),
 SOUND.HANGAR_SPACE_STATE: '{}_02'.format(SOUND.HANGAR_SPACE_STATE)}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
ACTION_BERLIN_SETTINGS = CommonSoundSpaceSettings(name=SOUND.SECRET_EVENT_BERLIN_SPACE, entranceStates={SOUND.HANGAR_OVERLAY_STATE: '{}_on'.format(SOUND.HANGAR_OVERLAY_STATE),
 SOUND.BERLIN_STATE: '{}_on'.format(SOUND.BERLIN_STATE),
 SOUND.HANGAR_SPACE_STATE: '{}_02'.format(SOUND.HANGAR_SPACE_STATE)}, exitStates={SOUND.BERLIN_STATE: '{}_off'.format(SOUND.BERLIN_STATE)}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
ACTION_HANGAR_SETTINGS = CommonSoundSpaceSettings(name=SOUND.SECRET_EVENT_HANGAR_SPACE, entranceStates={SOUND.HANGAR_OVERLAY_STATE: '{}_off'.format(SOUND.HANGAR_OVERLAY_STATE),
 SOUND.SHOP_STATE: '{}_garage'.format(SOUND.SHOP_STATE),
 SOUND.HANGAR_SPACE_STATE: '{}_02'.format(SOUND.HANGAR_SPACE_STATE)}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
