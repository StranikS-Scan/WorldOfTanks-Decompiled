# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/shared/tooltips/vehicle.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters
from gui.shared.tooltips.vehicle import VehicleInfoTooltipData
from gui.shared.gui_items.Tankman import CrewTypes, BROTHERHOOD_SKILL_NAME, REPAIR_SKILL_NAME

class WinbackExtendedVehicleInfoTooltipData(VehicleInfoTooltipData):

    def _packBlocks(self, *args, **kwargs):
        blocks = super(WinbackExtendedVehicleInfoTooltipData, self)._packBlocks(*args, **kwargs)
        params = self.context.getParams()
        showCrew = params.get('showCrew', False)
        showVehicleSlot = params.get('showVehicleSlot', False)
        allModulesAvailable = params.get('allModulesAvailable', False)
        if showCrew or showVehicleSlot or allModulesAvailable:
            additionalItemsBlocks = [formatters.packTextBlockData(text_styles.middleTitle(backport.text(R.strings.tooltips.vehicle.additional.header())), padding=formatters.packPadding(left=20))]
            if allModulesAvailable:
                additionalItemsBlocks.append(formatters.packImageTextBlockData(title='', desc=text_styles.main(backport.text(R.strings.tooltips.vehicle.allModules.header())), img=backport.image(R.images.gui.maps.icons.quests.bonuses.small.allModules()), imgPadding=formatters.packPadding(left=35, top=10), txtPadding=formatters.packPadding(left=25, top=20)))
            if showCrew:
                tankmenRoleLevels, tankmenSkills = params.get('tmanRoleLevel', ([], []))
                tankmenRoleLevels = set(tankmenRoleLevels)
                tankmenSkills = {tuple(sorted(tankmanSkills)) for tankmanSkills in tankmenSkills}
                crewLevel = tankmenRoleLevels.pop() if len(tankmenRoleLevels) == 1 else -1
                crewSkills = tankmenSkills.pop() if len(tankmenSkills) == 1 else ()
                if crewLevel == CrewTypes.SKILL_100:
                    crewImg = R.images.gui.maps.icons.crewBundles.bonuses.basicRoleBoost_100
                    imgPaddingLeft = 20
                    txtPaddingLeft = 10
                else:
                    crewImg = R.images.gui.maps.icons.quests.bonuses.small.tankmen
                    imgPaddingLeft = 35
                    txtPaddingLeft = 25
                crewText = R.strings.winback.winbackSelectableRewardView.selectedReward.tooltip.rewardVehicle.crew
                if set(crewSkills) == {BROTHERHOOD_SKILL_NAME, REPAIR_SKILL_NAME}:
                    crewSkillsString = backport.text(crewText.skills())
                    txtPaddingTop = 10
                else:
                    crewSkillsString = ''
                    txtPaddingTop = 20
                if crewLevel > 0:
                    crewText = crewText.level
                additionalItemsBlocks.append(formatters.packImageTextBlockData(title='', desc=text_styles.main(backport.text(crewText(), value=crewLevel, skills=crewSkillsString)), img=backport.image(crewImg()), imgPadding=formatters.packPadding(left=imgPaddingLeft, top=10), txtPadding=formatters.packPadding(left=txtPaddingLeft, top=txtPaddingTop)))
            if showVehicleSlot:
                additionalItemsBlocks.append(formatters.packImageTextBlockData(title='', desc=text_styles.main(backport.text(R.strings.tooltips.vehicle.hangarSlot.header())), img=backport.image(R.images.gui.maps.icons.quests.bonuses.small.slots()), imgPadding=formatters.packPadding(left=35, top=10), txtPadding=formatters.packPadding(left=25, top=20)))
            blocks.append(formatters.packBuildUpBlockData(additionalItemsBlocks))
        return blocks


class WinbackDiscountExtendedVehicleInfoTooltipData(VehicleInfoTooltipData):

    def _packBlocks(self, *args, **kwargs):
        blocks = super(WinbackDiscountExtendedVehicleInfoTooltipData, self)._packBlocks(*args, **kwargs)
        if self.context.getParams().get('showDiscount', False):
            blocks.append(formatters.packImageTextBlockData(img=backport.image(R.images.winback.gui.maps.icons.tooltip.info()), desc=text_styles.main(backport.text(R.strings.winback.vehicleDiscountRewardTooltip.description())), imgPadding=formatters.packPadding(left=20, top=4, right=10)))
        return blocks
