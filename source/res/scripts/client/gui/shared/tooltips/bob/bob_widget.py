# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/bob/bob_widget.py
import typing
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.bob.bob_helpers import getShortSkillName, getTeamIDFromTeamToken
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.formatters import packBobProgressionTableBlockData
from helpers import dependency, time_utils
from skeletons.gui.game_control import IBobController
if typing.TYPE_CHECKING:
    from gui.bob.bob_data_containers import TeamSkillData, TeamData

class SkillTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(SkillTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.BOB_SKILL_INFO)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(340)

    def _packBlocks(self, *args, **kwargs):
        skill = self.context.buildItem(*args, **kwargs)
        if skill is not None and skill.isActiveAt(time_utils.getServerUTCTime()):
            shortSkillName = getShortSkillName(skill.skill)
            blocks = [self.__packActivatedSkillHeaderBlock(shortSkillName)]
            if skill.count_left > 0:
                blocks.append(self.__packCountLeftBlock(skill.count_left))
        else:
            blocks = [self.__packDisableSkillBlock()]
        return [formatters.packBuildUpBlockData(blocks=blocks, padding=formatters.packPadding(bottom=-14))]

    @staticmethod
    def __packActivatedSkillHeaderBlock(shortSkillName):
        return formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(R.strings.bob.widget.tooltip.activatedSkill.title(), skillName=backport.text(R.strings.bob.skill.dyn(shortSkillName)()))), desc=text_styles.main(backport.text(R.strings.bob.skill.description.dyn(shortSkillName)())))

    @staticmethod
    def __packCountLeftBlock(countLeft):
        return formatters.packImageTextBlockData(title=text_styles.tutorial(backport.text(R.strings.bob.widget.tooltip.activatedSkill.count(), countLeft=countLeft)), img=backport.image(R.images.gui.maps.icons.bob.hangar.widget.count_icon()), padding=formatters.packPadding(top=10))

    def __packDisableSkillBlock(self):
        if self.context.getParams().get('isPlayerBlogger', False):
            descriptionR = R.strings.bob.widget.tooltip.disabledSkill.descriptionForBlogger
        else:
            descriptionR = R.strings.bob.widget.tooltip.disabledSkill.description
        return formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(R.strings.bob.widget.tooltip.disabledSkill.title())), desc=text_styles.main(backport.text(descriptionR())))


class ProgressionTooltipData(BlocksTooltipData):
    __bobController = dependency.descriptor(IBobController)

    def __init__(self, context):
        super(ProgressionTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.BOB_SKILL_INFO)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(340)
        self._isAllZeroScore = None
        return

    def _packBlocks(self, *args, **kwargs):
        self._isAllZeroScore = self.__bobController.isAllZeroScore()
        blocks = [self.__packTitleBlock(), self.__packProgressionTable(), self.__packLevelBlock(self.context.getParams().get('personalLevel', 1))]
        rewardsCount = self.context.getParams().get('rewardsCount', 0)
        if rewardsCount > 0 and not self._isAllZeroScore:
            blocks.append(self.__packPersonalRewardBlock(rewardsCount))
        blocks.append(self.__packDescriptionBlock())
        if not self.context.getParams().get('teams', []):
            blocks.append(self.__packTryLaterErrorBlock())
        elif self._isAllZeroScore:
            blocks.append(self.__packWaitFirstResultsInfoBlock())
        else:
            blocks.append(self.__packUpdatingDataInfoBlock())
        return [formatters.packBuildUpBlockData(blocks=blocks, padding=formatters.packPadding(bottom=-14))]

    @staticmethod
    def __packTitleBlock():
        return formatters.packTextBlockData(text=text_styles.highTitle(backport.text(R.strings.bob.widget.tooltip.progression.title())), padding=formatters.packPadding(bottom=5, top=-5))

    def __packProgressionTable(self):
        blocks = []
        teamText = text_styles.stats(backport.text(R.strings.bob.widget.tooltip.progression.column.team()))
        progress = text_styles.stats(backport.text(R.strings.bob.widget.tooltip.progression.column.progress()))
        place = text_styles.stats(backport.text(R.strings.bob.widget.tooltip.progression.column.place()))
        blocks.append(packBobProgressionTableBlockData(teamText, progress, place))
        teamsData = self.context.getParams().get('teams', [])
        if teamsData and not self._isAllZeroScore:
            blocks.extend(self.__packTeamsTableScoreTable(teamsData))
        else:
            blocks.extend(self.__packDefaultTeamsScoreTable())
        return formatters.packBuildUpBlockData(blocks=blocks, padding=formatters.packPadding())

    def __packTeamsTableScoreTable(self, teamsData):
        blocks = []
        teamsData.sort(key=lambda t: t.rank)
        currentTeamID = self.context.getParams().get('currentTeamID', -1)
        for team in teamsData:
            isCurrentTeam = team.team == currentTeamID
            style = text_styles.statusAttention if isCurrentTeam else text_styles.main
            teamName = style(backport.text(R.strings.bob.widget.tooltip.dyn('blogger_' + str(team.team))()))
            progress = style(team.score)
            place = style(team.rank)
            blocks.append(formatters.packSeparatorBlockData(width=340))
            blocks.append(packBobProgressionTableBlockData(teamName, progress, place, isCurrentTeam))

        return blocks

    def __packDefaultTeamsScoreTable(self):
        blocks = []
        currentTeamID = self.context.getParams().get('currentTeamID', -1)
        for teamToken in self.__bobController.teamTokens:
            teamID = getTeamIDFromTeamToken(teamToken)
            isCurrentTeam = teamID == currentTeamID
            style = text_styles.statusAttention if isCurrentTeam else text_styles.main
            teamName = style(backport.text(R.strings.bob.widget.tooltip.dyn('blogger_' + str(teamID))()))
            dashStr = style(backport.text(R.strings.common.common.dash()))
            blocks.append(formatters.packSeparatorBlockData(width=340))
            blocks.append(packBobProgressionTableBlockData(teamName, dashStr, dashStr, isCurrentTeam, isLikeHidden=True))

        return blocks

    @staticmethod
    def __packLevelBlock(level):
        return formatters.packTextBlockData(text=text_styles.highTitle(backport.text(R.strings.bob.widget.tooltip.progression.level(), level=level)))

    @staticmethod
    def __packPersonalRewardBlock(rewardsCount):
        if rewardsCount < 10:
            icon = backport.image(R.images.gui.maps.icons.bob.hangar.widget.counter())
            valuePaddingLeft = -27
        else:
            icon = backport.image(R.images.gui.maps.icons.bob.hangar.widget.counter_2())
            valuePaddingLeft = -34
        return formatters.packTitleDescParameterWithIconBlockData(icon=icon, title=text_styles.middleTitle(backport.text(R.strings.bob.widget.tooltip.progression.personalReward())), value=text_styles.warning(rewardsCount), valueAtRight=True, iconPadding=formatters.packPadding(top=-11, left=-10), valuePadding=formatters.packPadding(left=valuePaddingLeft), iconZIndex=0, padding=formatters.packPadding(bottom=-20))

    @staticmethod
    def __packDescriptionBlock():
        return formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.bob.widget.tooltip.progression.description())), padding=formatters.packPadding(top=10))

    @staticmethod
    def __packUpdatingDataInfoBlock():
        return formatters.packImageTextBlockData(title=text_styles.tutorial(backport.text(R.strings.bob.widget.tooltip.progression.updateData())), img=backport.image(R.images.gui.maps.icons.library.attentionIconFilled()), imgPadding=formatters.packPadding(top=2), padding=formatters.packPadding(top=10))

    @staticmethod
    def __packTryLaterErrorBlock():
        return formatters.packImageTextBlockData(title=text_styles.alert(backport.text(R.strings.messenger.client_error.shared.TRY_LATER())), img=backport.image(R.images.gui.maps.icons.library.alertIcon1()), imgPadding=formatters.packPadding(top=-1), padding=formatters.packPadding(top=10))

    @staticmethod
    def __packWaitFirstResultsInfoBlock():
        return formatters.packImageTextBlockData(title=text_styles.tutorial(backport.text(R.strings.bob.widget.tooltip.progression.waitFirstResults())), img=backport.image(R.images.gui.maps.icons.library.attentionIconFilled()), imgPadding=formatters.packPadding(top=2), padding=formatters.packPadding(top=10))
