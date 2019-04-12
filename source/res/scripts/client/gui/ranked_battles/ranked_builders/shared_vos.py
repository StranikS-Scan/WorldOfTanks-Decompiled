# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_builders/shared_vos.py
import logging
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles import ranked_formatters
from gui.ranked_battles.ranked_helpers import getShieldSizeByRankSize, makeStatTooltip
from gui.shared.formatters import text_styles, icons
_logger = logging.getLogger(__name__)
__ANIMATION_DATA_FIELDS = ['top',
 'bottom',
 'left',
 'right']

def buildRankVO(rank, isEnabled=False, hasTooltip=False, imageSize=RANKEDBATTLES_ALIASES.WIDGET_MEDIUM, shieldStatus=None, showShieldLabel=True, shieldAnimated=False):
    shield = None
    if shieldStatus is not None:
        prevShieldHP, shieldHP, _, shieldState, newShieldState = shieldStatus
        if shieldState != newShieldState or shieldHP > 0:
            shieldSize = getShieldSizeByRankSize(imageSize)
            shortcut = R.images.gui.maps.icons.rankedBattles.ranks.shields
            shield = {'state': shieldState,
             'newState': newShieldState,
             'size': shieldSize,
             'img': backport.image(shortcut.dyn(attr='{}'.format(shieldSize))()),
             'plateImg': '',
             'prevLabel': '',
             'label': ''}
            if showShieldLabel:
                shield['prevLabel'] = str(prevShieldHP)
                shield['label'] = str(shieldHP)
                shield['plateImg'] = backport.image(shortcut.plate.empty.dyn(attr='{}'.format(shieldSize))())
            if shieldAnimated:
                shield['animationData'] = {'topImg': backport.image(shortcut.dyn(attr='{}_{}'.format(shieldSize, RANKEDBATTLES_ALIASES.SHIELD_PART_TOP))()),
                 'bottomImg': backport.image(shortcut.dyn(attr='{}_{}'.format(shieldSize, RANKEDBATTLES_ALIASES.SHIELD_PART_BOTTOM))()),
                 'rightImg': backport.image(shortcut.dyn(attr='{}_{}'.format(shieldSize, RANKEDBATTLES_ALIASES.SHIELD_PART_RIGHT))()),
                 'leftImg': backport.image(shortcut.dyn(attr='{}_{}'.format(shieldSize, RANKEDBATTLES_ALIASES.SHIELD_PART_LEFT))())}
    return {'imageSrc': rank.getIcon(imageSize),
     'smallImageSrc': rank.getIcon(RANKEDBATTLES_ALIASES.WIDGET_SMALL),
     'isEnabled': isEnabled,
     'rankID': str(rank.getID()),
     'hasTooltip': hasTooltip,
     'shield': shield}


def buildRankTooltipVO(rank, isEnabled=False, imageSize=RANKEDBATTLES_ALIASES.WIDGET_MEDIUM, shieldStatus=None):
    shieldImage = None
    plateImage = None
    if shieldStatus is not None:
        _, shieldHP, _, _, _ = shieldStatus
        if shieldHP > 0:
            shieldImage = backport.image(R.images.gui.maps.icons.rankedBattles.ranks.shields.dyn(imageSize)())
            hpShortcut = R.images.gui.maps.icons.rankedBattles.ranks.shields.plate
            plateImage = backport.image(hpShortcut.dyn(imageSize).num(shieldHP)())
    return {'rankImage': rank.getIcon(imageSize),
     'shieldImage': shieldImage,
     'plateImage': plateImage,
     'isEnabled': isEnabled}


def getStatVO(value, statKey, iconKey, tooltipKey):
    return {'icon': iconKey,
     'label': text_styles.alignText(text_styles.main(backport.text(R.strings.ranked_battles.rankedBattleMainView.stats.dyn(statKey)())), 'center'),
     'value': value,
     'tooltip': makeStatTooltip(tooltipKey)}


def getEfficiencyVO(currentSeasonEfficiency, currentSeasonEfficiencyDiff):
    delta = ''
    if currentSeasonEfficiencyDiff is not None:
        if currentSeasonEfficiencyDiff > 0:
            delta = text_styles.concatStylesToSingleLine(icons.makeImageTag(backport.image(R.images.gui.maps.icons.rankedBattles.league.delta_plus()), 11, 16, -3), text_styles.bonusAppliedText(ranked_formatters.getFloatPercentStrStat(currentSeasonEfficiencyDiff)))
        if currentSeasonEfficiencyDiff < 0:
            delta = text_styles.concatStylesToSingleLine(icons.makeImageTag(backport.image(R.images.gui.maps.icons.rankedBattles.league.delta_minus()), 11, 16, -3), text_styles.error(ranked_formatters.getFloatPercentStrStat(currentSeasonEfficiencyDiff)))
    return {'icon': 'efficiency',
     'label': '',
     'value': ranked_formatters.getFloatPercentStrStat(currentSeasonEfficiency),
     'delta': delta}


def getRatingVO(rating):
    return {'icon': 'position',
     'label': '',
     'value': ranked_formatters.getIntegerStrStat(rating)}
