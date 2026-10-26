from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle, DefaultOnToggle, Visibility, OptionSet

class LiveCount(Range):
    """
    Number of unique live shows needed to be 'completed' to finish a game.
    Completion requirements are set further in the options.
    """

    display_name = "Goal Live Show Completion Count"

    range_start = 10
    range_end = 248
    default = 20

class LiveStartCount(Range):
    """
    Number of live shows that you start with unlocked.
    """

    display_name = "Starting Live Show Count"

    range_start = 1
    range_end = 10
    default = 5

class LiveExtraCount(Range):
    """
    Number of live shows available to unlock beyond what is required to reach your goal.
    A value of 0 means you must revieve every single live show item in the pool in order to reach your goal.
    """

    display_name = "Extra Live Show Count"

    range_start = 0
    range_end = 238
    default = 10

class IncludedGroups(OptionSet):
    """
    Select which idol group(s) you want to be included in the randomizer.
    Deselecting any group in this category will remove their Live Shows, Scouting Boxes, and Main Story checks from randomization.
    If no groups are selected, this option will be ignored.
    Nijigasaki and Liella! are advised against being the only groups included, as they have much less content available compared to μ's and Aqours.
    If your selected goal amount or included amount of songs is higher than the number of songs available in the pool,
    the counts will be dropped lower to make clearing your game possible.
    """

    display_name = "Included Idol Groups"

    valid_keys = ["Muse (μ's)","Aqours","Nijigasaki","Liella!"]
    default = ["Muse (μ's)","Aqours","Nijigasaki","Liella!"]
    valid_keys_casefold = False

class LiveDifficulty(Choice):
    """
    Minimum live show difficulty level needed to play for it to be checked.
    To send checks for a track, you must play the track on this difficulty or higher.
    """

    display_name = "Minimum Live Show Difficulty"

    option_easy = 1
    option_normal = 2
    option_hard = 3
    option_expert = 4
    default = option_easy

class LiveRank(Choice):
    """
    Checks will be included for achieving up to the selected Rank on each Live Show at your selected difficulty (or higher).
    Achieving a rank will also check off every rank below it.
    To 'complete' a track, you must achieve at least the rank set here.
    If set to 'Any Rank', clearing a track with any rank will 'complete' it.
    """

    display_name = "Maximum Live Show Rank"

    option_any_rank = 0
    option_c_rank = 1
    option_b_rank = 2
    option_a_rank = 3
    option_s_rank = 4
    default = option_b_rank

class FullComboChecks(Toggle):
    """
    Add an additional check to each live show for achieving a full combo.
    Not required for completion.
    """

    display_name = "Full Combo Checks"

class ShopChecks(Range):
    """
    The number of AP Items (Location Checks) available to buy in the Sticker Shop.
    """

    display_name = "Sticker Shop Checks"

    range_start = 0
    range_end = 50
    default = 25

class IndividualDifficulty(Toggle):
    """
    Adds checks for reaching live show goals for each difficulty individually,
    rather than having a single set of checks for each track as a whole.
    """

    display_name = "Individual Difficulty Checks"

class IncludedDifficulty(OptionSet):
    """
    If 'Individual Difficulty Checks' is on, select which difficulty levels you want to have checks assigned to.
    If no difficulties are chosen, 'Individual Difficulty Checks' will be turned off.
    To 'complete' a track, you must achieve your selected Score Rank on every difficulty selected here.
    """

    display_name = "Included Difficulties"

    valid_keys = ["Easy","Normal","Hard","Expert"]
    valid_keys_casefold = False

class FillerSupportPercentage(Range):
    """
    Percent of all filler items that will send you a support unit.
    """

    display_name = "Support Unit Filler Percent"

    range_start = 0
    range_end = 50
    default = 25

class SendDeathlinks(Toggle):
    """
    Losing a Live Show (Running out of Stamina or quitting early) will send a Deathlink to other players.
    """

    display_name = "Send Deathlinks"

class FullComboDeathlinks(Toggle):
    """
    Completing a live show without achieving a full combo will send a Deathlink to other players.
    """

    display_name = "Combo Break Deathlinks"

class DisplayLanguage(Choice):
    """
    Not currently implemented. The language that will be used for Live Show and Unit names in the APWorld.
    """

    display_name = "Display Language"
    option_english = 1
    option_japanese = 2
    default = option_english
    visibility = Visibility.none

class Unitsanity(Toggle):
    """
    Not currently implemented. Adds a check for obtaining one of EVERY unit, including supports.
    (Will massively inflate the number of checks in your game (Adds 3,771 extra checks), and is highly luck-based.)
    Please do not turn this on.
    """

    display_name = "Unitsanity"
    visibility = Visibility.none

@dataclass
class LLSIFOptions(PerGameCommonOptions):
    live_count: LiveCount
    live_start_count: LiveStartCount
    live_extra: LiveExtraCount
    included_groups: IncludedGroups
    live_difficulty: LiveDifficulty
    live_rank: LiveRank
    fc_checks: FullComboChecks
    shop_checks: ShopChecks
    individual_difficulty: IndividualDifficulty
    included_difficulty: IncludedDifficulty
    filler_support_percentage: FillerSupportPercentage
    send_deathlinks: SendDeathlinks
    fc_deathlinks: FullComboDeathlinks
    display_language: DisplayLanguage
    unitsanity: Unitsanity