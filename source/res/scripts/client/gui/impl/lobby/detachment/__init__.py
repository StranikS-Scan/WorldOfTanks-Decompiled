# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/__init__.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel

class BaseViewSetting(object):

    def __init__(self, layoutID, viewClass, isFlashView=False):
        self.layoutID = layoutID
        self.viewClass = viewClass
        self.isFlashView = isFlashView


def getViews():
    from gui.impl.lobby.detachment.barrack_recruits_view import BarrackRecruitsView
    from gui.impl.lobby.detachment.barrack_instructors_view import BarrackInstructorsView
    from gui.impl.lobby.detachment.barrack_detachment_view import BarrackDetachmentsView
    from gui.impl.lobby.detachment.personal_case import PersonalCase
    from gui.impl.lobby.detachment.profile_view import ProfileView
    from gui.impl.lobby.detachment.progression_view import ProgressionView
    from gui.impl.lobby.detachment.learned_skills_view import LearnedSkillsView
    from gui.impl.lobby.detachment.instructors_office_view import InstructorsOfficeView
    return dict([(NavigationViewModel.VEHICLE_LIST, BaseViewSetting(None, None, True)),
     (NavigationViewModel.BARRACK_DETACHMENT, BaseViewSetting(R.views.lobby.detachment.BarrackDetachmentsView(), BarrackDetachmentsView)),
     (NavigationViewModel.BARRACK_INSTRUCTOR, BaseViewSetting(R.views.lobby.detachment.BarrackInstructorsView(), BarrackInstructorsView)),
     (NavigationViewModel.BARRACK_RECRUIT, BaseViewSetting(R.views.lobby.detachment.BarrackRecruitsView(), BarrackRecruitsView)),
     (NavigationViewModel.PERSONAL_CASE_BASE, BaseViewSetting(R.views.lobby.detachment.PersonalCase(), PersonalCase)),
     (NavigationViewModel.PERSONAL_CASE_PROFILE, BaseViewSetting(R.views.lobby.detachment.ProfileView(), ProfileView)),
     (NavigationViewModel.PERSONAL_CASE_PROGRESSION, BaseViewSetting(R.views.lobby.detachment.ProgressionView(), ProgressionView)),
     (NavigationViewModel.PERSONAL_CASE_PERKS_MATRIX, BaseViewSetting(None, None, True)),
     (NavigationViewModel.INSTRUCTORS_LIST, BaseViewSetting(None, None, True)),
     (NavigationViewModel.LEARNED_SKILLS, BaseViewSetting(R.views.lobby.detachment.LearnedSkills(), LearnedSkillsView)),
     (NavigationViewModel.INSTRUCTORS_OFFICE, BaseViewSetting(R.views.lobby.detachment.InstructorsOfficeView(), InstructorsOfficeView))])
