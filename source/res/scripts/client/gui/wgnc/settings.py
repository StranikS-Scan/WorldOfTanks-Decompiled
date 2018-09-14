# Embedded file name: scripts/client/gui/wgnc/settings.py


class WGNC_GUI_TYPE(object):
    UNDEFINED = 0
    POP_UP = 1
    BASIC_WINDOW = 2
    COMPLEX_WINDOW = 4


class WGNC_DATA_PROXY_TYPE(object):
    UNDEFINED = 0
    CLAN_APP = 1
    CLAN_INVITE = 2
    CLAN_APP_DECLINED = 4
    CLAN_APP_ACCEPTED = 8
    CLAN_INVITE_ACCEPTED = 16
    CLAN_INVITE_DECLINED = 18


WGNC_POP_UP_PRIORITIES = ('low', 'medium', 'high')
WGNC_POP_UP_BUTTON_WIDTH = 107
WGNC_GUI_INVALID_SEQS = (WGNC_GUI_TYPE.UNDEFINED, WGNC_GUI_TYPE.BASIC_WINDOW | WGNC_GUI_TYPE.COMPLEX_WINDOW, WGNC_GUI_TYPE.POP_UP | WGNC_GUI_TYPE.BASIC_WINDOW | WGNC_GUI_TYPE.COMPLEX_WINDOW)
WGNC_DEFAULT_ICON = 'InformationIcon'
_WGNC_ICON_TO_LOCAL = {'information': WGNC_DEFAULT_ICON,
 'gold': 'GoldIcon',
 'text_message': 'MessageIcon'}

def convertToLocalIcon(icon):
    result = WGNC_DEFAULT_ICON
    if icon in _WGNC_ICON_TO_LOCAL:
        result = _WGNC_ICON_TO_LOCAL[icon]
    return result


_WGNC_BG_TO_LOCAL = {'battle_defeat': ('BgBattleResultIconDefeat', (288, 167)),
 'battle_draw': ('BgBattleResultIconDraw', (288, 167)),
 'battle_victory': ('BgBattleResultIconVictory', (288, 167)),
 'poll': ('BgPoll', (288, 110))}

def convertToLocalBG(icon):
    result = ('', (0, 0))
    if icon in _WGNC_BG_TO_LOCAL:
        result = _WGNC_BG_TO_LOCAL[icon]
    return result
