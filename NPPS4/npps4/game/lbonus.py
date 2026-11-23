import pydantic

from .. import idol
from .. import util
from .. import strings
from ..system import achievement
from ..system import ad_model
from ..system import advanced
from ..system import class_system as class_system_module
from ..system import common
from ..system import effort
from ..system import item
from ..system import item_model
from ..system import lbonus
from ..system import museum
from ..system import reward
from ..system import user


class LoginBonusCalendarMonthInfo(pydantic.BaseModel):
    year: int
    month: int
    days: list[lbonus.LoginBonusCalendar]


class LoginBonusCalendarInfo(pydantic.BaseModel):
    current_date: str
    current_month: LoginBonusCalendarMonthInfo
    next_month: LoginBonusCalendarMonthInfo
    get_item: pydantic.SerializeAsAny[common.AnyItem] | None = None


class LoginBonusTotalLogin(pydantic.BaseModel):
    login_count: int
    remaining_count: int = 2147483647  # TODO
    reward: list[pydantic.SerializeAsAny[common.AnyItem]] | None = None


class LoginBonusResponse(achievement.AchievementMixin, common.TimestampMixin):
    sheets: list = pydantic.Field(default_factory=list)
    calendar_info: LoginBonusCalendarInfo
    ad_info: ad_model.AdInfo
    total_login_info: LoginBonusTotalLogin
    license_lbonus_list: list  # TODO
    class_system: class_system_module.ClassSystemData = pydantic.Field(
        default_factory=class_system_module.ClassSystemData
    )  # TODO
    start_dash_sheets: list  # TODO
    effort_point: list[effort.EffortPointInfo]
    limited_effort_box: list  # TODO
    after_user_info: user.UserInfoData
    museum_info: museum.MuseumInfoData
    present_cnt: int


@idol.register("lbonus", "execute", batchable=False, xmc_verify=idol.XMCVerifyMode.CROSS, exclude_none=True)
async def lbonus_execute(context: idol.SchoolIdolUserParams) -> LoginBonusResponse:
    server_timestamp = util.time()
    current_datetime = util.datetime(server_timestamp)

    next_year, next_month_num = current_datetime.year, current_datetime.month + 1
    if next_month_num > 12:
        next_year = next_year + 1
        next_month_num = 1

    current_user = await user.get_current(context)
    current_month = await lbonus.get_calendar(context, current_datetime.year, current_datetime.month)
    next_month = await lbonus.get_calendar(context, next_year, next_month_num)
    login_count = await lbonus.get_login_count(context, current_user)
    lbonuses_day = await lbonus.days_login_bonus(context, current_user, current_datetime.year, current_datetime.month)
    present_count = await reward.count_presentbox(context, current_user)

    has_lbonus = current_datetime.day in lbonuses_day
    get_item = None
    add_effort_amount = 0
    achievement_list = achievement.AchievementContext()
    accomplished_rewards = []
    unaccomplished_rewards = []
    effort_result = []

    current_date = f"{current_datetime.year}-{current_datetime.month}-{current_datetime.day}"

    return LoginBonusResponse(
        calendar_info=LoginBonusCalendarInfo(
            current_date=current_date,
            current_month=LoginBonusCalendarMonthInfo(
                year=current_datetime.year, month=current_datetime.month, days=current_month
            ),
            next_month=LoginBonusCalendarMonthInfo(year=next_year, month=next_month_num, days=next_month),
            get_item=get_item,
        ),
        ad_info=ad_model.AdInfo(),
        total_login_info=LoginBonusTotalLogin(login_count=login_count),
        license_lbonus_list=[],  # TODO
        start_dash_sheets=[],  # TODO
        effort_point=effort_result,
        limited_effort_box=[],  # TODO
        accomplished_achievement_list=await achievement.to_game_representation(
            context, achievement_list.accomplished, accomplished_rewards
        ),
        unaccomplished_achievement_cnt=await achievement.get_achievement_count(context, current_user, False),
        after_user_info=await user.get_user_info(context, current_user),
        added_achievement_list=await achievement.to_game_representation(
            context, achievement_list.new, unaccomplished_rewards
        ),
        new_achievement_cnt=len(achievement_list.new),
        museum_info=await museum.get_museum_info_data(context, current_user),
        present_cnt=present_count,
    )
