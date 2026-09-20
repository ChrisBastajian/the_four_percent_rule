"""
The 4% Rule — Opening Manim Scene
==================================

Covers the very first animated beat of the video:

  1. "Figures are inflation-adjusted backward in time" — show what
     today's $1,000,000 was worth in 1924, then blend that into the
     "$1,000,000" figure used for the rest of the simulation, sitting
     next to a full, white, vertical net-worth bar (sized on the same
     dollars-per-unit scale as the graph, so it visually matches the
     graph's own bars).
  2. A clean line/bar graph appears: years on the x-axis, portfolio
     net worth on the y-axis.
  3. Year-by-year fill logic, for 1924 through 1928 (the bull run
     before the 1929 crash):
       - a growth bar and a withdrawal ($100k) bar appear side by
         side on that year's tick
       - they slide together into one overlaid column
       - the overlay shrinks into a single net-profit bar (the only
         bar left on that tick)
       - a copy of that net-profit bar flies over, docks directly on
         top of the net-worth bar (touching, no gap), and then the
         net-worth bar stretches upward to absorb it while the copy
         fades — one continuous "merge," not a separate pop-and-jump
     Year 1 (1924) runs slow, so narration can match beat-for-beat.
     Years 2-5 (1925-1928) repeat the same logic faster.

Brand styling: light-blue background, blue/black/white for the core
narrative, red reserved for losses and green reserved for profit/gains
(never used for anything else) — see style.py for the shared palette
used across every scene in this project.

Render with (ManimCE):
    manim -pql four_percent_intro_scene.py FourPercentRuleOpening   # quick preview
    manim -pqh four_percent_intro_scene.py FourPercentRuleOpening   # final quality

DATA SOURCES / THINGS TO VERIFY BEFORE FINAL RENDER
----------------------------------------------------
- S&P 500 annual total returns for 1924-1928 below are pulled from
  officialdata.org's S&P 500 return calculator (dividends reinvested).
  That's a secondary aggregator, not a primary dataset — cross-check
  against Shiller's S&P Composite data, Ibbotson/SBBI, or the NYU
  Stern (Damodaran) historical returns spreadsheet before this airs.
- The 1924 inflation-equivalent figure ($51,046 for today's $1,000,000)
  comes from officialdata.org's CPI inflation calculator (multiplier
  19.59x, 1924 -> 2026). Same caveat: verify against BLS CPI data
  directly before filming.

IMPORTANT — verified: does this period actually wipe the portfolio out?
------------------------------------------------------------------------
Ran the full year-by-year simulation (real S&P 500 returns, source:
slickcharts.com "S&P 500 Total Returns by Year Since 1926" for
1926-1955, officialdata.org for 1924-1925) all the way out until the
balance actually crosses zero, not just a few sample years:

    Retire 1924 (5 good years: 1924-1928, peak $2,333,017):
        year 10 (1933): $794,613
        year 15 (1938): $654,494
        year 20 (1943): $135,143
        year 22 (1945): -$79,020  <- runs out, age 71

    Retire 1925 (4 good years: 1925-1928, peak $1,934,234):
        year 10 (1934): $468,071
        year 15 (1939): $188,915
        year 17 (1941): -$17,489  <- runs out, age 66

Both genuinely deplete to zero — this isn't ambiguous, it just takes
the full stretch (17-22 years), not a fast collapse. 1924 is the
closer match to the "five years" bull run in the script and script's
"by 70" line (actual: age 71, one year off — a trivial narration
tweak). 1925 gives a tighter overall timeline to animate (17 years vs
22) at the cost of one fewer good year up front. Both are defensible;
1924 is what's used below since it matches the "five years" framing
exactly. Switch YEARS/RETURNS below to start at 1925 instead if the
shorter runway is worth more than the extra good year.
"""

from manim import *

from style import (
    BACKGROUND, AXIS_LINE,
    INK_PRIMARY, INK_SECONDARY, INK_MUTED,
    BLUE_DEEP, GREEN_PROFIT, RED_LOSS, WHITE,
)

# ---------------------------------------------------------------
# DATA — update these once real/verified numbers are confirmed.
# Everything below derives from these constants; nothing is
# hardcoded a second time.
# ---------------------------------------------------------------

YEARS = [1924, 1925, 1926, 1927, 1928]

# S&P 500 annual total return (with dividends), by year.
# Source: officialdata.org S&P 500 historical return calculator.
RETURNS = [0.2709, 0.2582, 0.1162, 0.3749, 0.4361]

STARTING_BALANCE = 1_000_000
ANNUAL_WITHDRAWAL = 100_000  # the 4%-of-$1,000,000 the hook promises

# What today's $1,000,000 was worth in 1924 dollars.
# Source: officialdata.org CPI inflation calculator (19.59x multiplier).
INFLATION_1924_EQUIVALENT = 51_046

# Shared dollars-per-scene-unit scale. Both the graph's own bars and
# the standalone net-worth bar use this same conversion, so a $1M bar
# looks the same height everywhere on screen.
GRAPH_Y_LENGTH = 4.2
GRAPH_Y_MAX = 2_600_000  # covers the ~$2.33M peak reached by end of 1928

# ---- brand palette (style.py) ----
# Growth / withdrawal / net-change bars carry the one fixed meaning
# from the brand brief: green is profit, red is loss, never anything
# else. The net-worth bar itself isn't a gain/loss figure — it's the
# running total — so it stays white-on-navy-outline, the "black and
# white" side of the palette, and every label/emphasis number uses
# the brand's deep blue instead of an off-brand accent color.
GROWTH_COLOR = GREEN_PROFIT
WITHDRAWAL_COLOR = RED_LOSS
NET_POSITIVE_COLOR = GREEN_PROFIT   # net change is itself a gain -> green
NET_NEGATIVE_COLOR = RED_LOSS       # net change is itself a loss -> red
NETWORTH_FILL = WHITE
NETWORTH_STROKE = BLUE_DEEP
EMPHASIS_COLOR = BLUE_DEEP

BAR_WIDTH = 0.4

config.background_color = BACKGROUND


def value_to_height(value: float) -> float:
    """Dollars -> scene units, on the one shared scale used everywhere."""
    return abs(value) / GRAPH_Y_MAX * GRAPH_Y_LENGTH


def money(value: float) -> str:
    """Full precision: $1,234,567 or -$1,234,567."""
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.0f}"


def money_short(value: float, show_sign: bool = True) -> str:
    """Compact form for on-bar labels: +$244K, -$100K, +$1.72M."""
    sign = ""
    if show_sign:
        sign = "-" if value < 0 else "+"
    absval = abs(value)
    if absval >= 1_000_000:
        body = f"{absval / 1_000_000:.2f}M"
    elif absval >= 1_000:
        body = f"{absval / 1_000:.0f}K"
    else:
        body = f"{absval:.0f}"
    return f"{sign}${body}"


class FourPercentRuleOpening(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        # Build the axes object early (not yet drawn) purely as a
        # coordinate reference, so the intro's net-worth bar can sit
        # on the exact same baseline the graph will use later.
        self.axes = self._make_axes()

        self.networth_tracker = ValueTracker(STARTING_BALANCE)

        self.show_inflation_intro()
        self.reveal_graph_axes()
        self.run_years()
        self.wait(1)

    def _make_axes(self) -> Axes:
        axes = Axes(
            x_range=[YEARS[0] - 1, YEARS[-1] + 1, 1],
            y_range=[0, GRAPH_Y_MAX, 400_000],
            x_length=7.6,
            y_length=GRAPH_Y_LENGTH,
            axis_config={
                "include_numbers": False,
                "include_ticks": True,
                "color": AXIS_LINE,
                "stroke_width": 3,
            },
            tips=False,
        )
        # Shifted left off the right edge so the graph reads as
        # centered in the frame rather than pinned to the right side;
        # the net-worth bar (positioned separately, see bar_x below)
        # sits further out to the left as its own distinct element.
        axes.to_edge(RIGHT, buff=1.7).shift(UP * 0.4)
        return axes

    # ------------------------------------------------------------------
    # STEP 1 — inflation-adjustment intro + the starting net-worth bar
    # ------------------------------------------------------------------
    def show_inflation_intro(self):
        caption = Text(
            "Figures are inflation-adjusted backward in time",
            font_size=22, color=INK_SECONDARY,
        )
        caption.to_edge(UP)
        self.play(FadeIn(caption))

        historical_label = Text(
            "In 1924, this had the same buying power as:",
            font_size=20, color=INK_SECONDARY,
        )
        historical_amount = Text(
            money(INFLATION_1924_EQUIVALENT), font_size=40,
            color=EMPHASIS_COLOR, weight=BOLD,
        )
        historical_group = VGroup(historical_label, historical_amount).arrange(DOWN, buff=0.35)
        historical_group.move_to(ORIGIN)

        self.play(Write(historical_label))
        self.play(FadeIn(historical_amount, scale=0.85))
        self.wait(1)

        # Blend the 1924 figure into the "today's equivalent $1,000,000"
        # figure the rest of the simulation is framed around.
        today_amount = Text(money(STARTING_BALANCE), font_size=40, color=EMPHASIS_COLOR, weight=BOLD)
        today_amount.move_to(historical_amount)

        self.play(FadeOut(historical_label))
        self.play(Transform(historical_amount, today_amount), run_time=1.4)
        self.wait(0.3)

        # Net-worth bar: same width as the graph's own bars, and the
        # same dollars-per-unit scale, so it reads as part of one
        # visual system rather than a separate oversized element.
        # Placed low and to the left, well clear of the graph on the
        # right-hand side of the frame. White fill with a navy outline
        # so it stays crisp against the light-blue background instead
        # of washing out.
        bar_bottom_y = self.axes.c2p(YEARS[0], 0)[1]
        bar_x = -5.4  # pushed further to the side, now that the graph itself sits more centered

        self.net_worth_bar = Rectangle(
            width=BAR_WIDTH,
            height=value_to_height(STARTING_BALANCE),
            fill_color=NETWORTH_FILL,
            fill_opacity=1,
            stroke_color=NETWORTH_STROKE,
            stroke_width=2.5,
        )
        self.net_worth_bar.move_to(
            [bar_x, bar_bottom_y + value_to_height(STARTING_BALANCE) / 2, 0]
        )

        net_worth_caption = Text("Net worth", font_size=16, color=INK_MUTED)
        net_worth_caption.next_to(self.net_worth_bar, DOWN, buff=0.25)

        self.net_worth_label = always_redraw(
            lambda: Text(
                money(self.networth_tracker.get_value()),
                font_size=20,
                color=EMPHASIS_COLOR,
                weight=BOLD,
            ).next_to(net_worth_caption, DOWN, buff=0.15)
        )

        self.play(
            FadeOut(historical_amount),
            FadeIn(self.net_worth_bar, shift=UP),
            Write(net_worth_caption),
            run_time=1.0,
        )
        self.add(self.net_worth_label)
        self.net_worth_caption = net_worth_caption

        self.play(FadeOut(caption))
        self.wait(0.5)

    # ------------------------------------------------------------------
    # STEP 2 — the graph itself: years on x, net worth on y
    # ------------------------------------------------------------------
    def reveal_graph_axes(self):
        axes = self.axes

        x_tick_labels = VGroup(*[
            Text(str(y), font_size=16, color=INK_MUTED).next_to(axes.c2p(y, 0), DOWN, buff=0.2)
            for y in YEARS
        ])

        y_tick_values = [0, 400_000, 800_000, 1_200_000, 1_600_000, 2_000_000, 2_400_000]
        y_tick_labels = VGroup(*[
            Text(
                f"${v/1_000_000:.1f}M" if v else "$0", font_size=14, color=INK_MUTED,
            ).next_to(axes.c2p(YEARS[0] - 1, v), LEFT, buff=0.2)
            for v in y_tick_values
        ])

        x_title = Text("Year", font_size=18, color=INK_SECONDARY).next_to(axes.x_axis, DOWN, buff=0.6)
        y_title = Text("Portfolio Net Worth", font_size=18, color=INK_SECONDARY).rotate(90 * DEGREES)
        y_title.next_to(axes.y_axis, LEFT, buff=0.9)

        self.play(Create(axes), run_time=1.3)
        self.play(Write(x_tick_labels), Write(y_tick_labels), Write(x_title), Write(y_title))
        self.wait(0.4)

        self.x_tick_labels = x_tick_labels

    # ------------------------------------------------------------------
    # STEP 3 — walk through each year with the growth/withdrawal/net logic
    # ------------------------------------------------------------------
    def run_years(self):
        balance = STARTING_BALANCE
        for i, (year, r) in enumerate(zip(YEARS, RETURNS)):
            is_first_year = (i == 0)
            balance = self.animate_year(year, r, balance, slow=is_first_year)

    def animate_year(self, year: int, annual_return: float, balance: float, slow: bool):
        """
        One year's worth of the graph-filling logic: growth bar +
        withdrawal bar appear side by side, slide into an overlay,
        shrink into a single net-profit bar, and a copy of that bar
        docks on top of the net-worth bar and merges into it.
        Returns the ending balance for this year.
        """
        remaining_after_withdrawal = balance - ANNUAL_WITHDRAWAL
        growth_dollars = remaining_after_withdrawal * annual_return
        net_change = growth_dollars - ANNUAL_WITHDRAWAL
        end_balance = remaining_after_withdrawal + growth_dollars

        # Timing: year 1 runs slow and deliberate so narration can land
        # on each number in real time; years 2-5 repeat the same beats
        # at roughly half that duration.
        t = 1.7 if slow else 0.5

        x_center = self.axes.c2p(year, 0)[0]
        baseline_y = self.axes.c2p(year, 0)[1]

        # --- growth bar and withdrawal bar appear side by side ---
        growth_bar = Rectangle(
            width=BAR_WIDTH,
            height=value_to_height(growth_dollars),
            fill_color=GROWTH_COLOR,
            fill_opacity=0.9,
            stroke_width=0,
        )
        growth_bar.move_to([x_center - BAR_WIDTH * 1.15, baseline_y, 0], aligned_edge=DOWN)

        withdrawal_bar = Rectangle(
            width=BAR_WIDTH,
            height=value_to_height(ANNUAL_WITHDRAWAL),
            fill_color=WITHDRAWAL_COLOR,
            fill_opacity=0.9,
            stroke_width=0,
        )
        withdrawal_bar.move_to([x_center + BAR_WIDTH * 1.15, baseline_y, 0], aligned_edge=DOWN)

        growth_label = Text(money_short(growth_dollars), font_size=14, color=GROWTH_COLOR)
        growth_label.next_to(growth_bar, UP, buff=0.12)
        withdrawal_label = Text(money_short(-ANNUAL_WITHDRAWAL), font_size=14, color=WITHDRAWAL_COLOR)
        withdrawal_label.next_to(withdrawal_bar, UP, buff=0.12)

        self.play(
            FadeIn(growth_bar, shift=UP),
            FadeIn(withdrawal_bar, shift=UP),
            run_time=1.4 * t,
        )
        self.play(Write(growth_label), Write(withdrawal_label), run_time=0.8 * t)
        if slow:
            self.wait(0.9)

        # --- slide the two bars together into one overlaid column ---
        # The bars overlap, but the two labels move to sit side by
        # side (not stacked) just above the overlay, so both dollar
        # amounts stay readable at once instead of covering each other.
        overlay_target = [x_center, baseline_y, 0]
        label_y = max(growth_label.get_y(), withdrawal_label.get_y())
        self.play(
            growth_bar.animate.move_to(overlay_target, aligned_edge=DOWN),
            withdrawal_bar.animate.move_to(overlay_target, aligned_edge=DOWN),
            growth_label.animate.move_to([x_center - 0.42, label_y, 0]),
            withdrawal_label.animate.move_to([x_center + 0.42, label_y, 0]),
            run_time=1.2 * t,
        )
        if slow:
            self.wait(0.5)

        # --- overlay shrinks into a single net-profit bar ---
        net_color = NET_POSITIVE_COLOR if net_change >= 0 else NET_NEGATIVE_COLOR
        net_bar = Rectangle(
            width=BAR_WIDTH,
            height=value_to_height(net_change),
            fill_color=net_color,
            fill_opacity=1,
            stroke_width=0,
        )
        net_bar.move_to(overlay_target, aligned_edge=DOWN)
        net_label = Text(money_short(net_change), font_size=14, color=net_color)
        net_label.next_to(net_bar, UP, buff=0.12)

        self.play(
            ReplacementTransform(VGroup(growth_bar, withdrawal_bar), net_bar),
            ReplacementTransform(VGroup(growth_label, withdrawal_label), net_label),
            run_time=1.3 * t,
        )
        if slow:
            self.wait(0.9)

        # --- a copy of the net-profit bar docks on top of the net-worth ---
        # --- bar (touching, no gap), then the bar stretches upward to  ---
        # --- absorb it in one continuous merge                        ---
        flying_copy = net_bar.copy()
        dock_point = self.net_worth_bar.get_top()

        self.play(
            flying_copy.animate.move_to(dock_point, aligned_edge=DOWN),
            FadeOut(net_label),
            run_time=1.1 * t,
        )
        if slow:
            self.wait(0.4)

        new_total_height = value_to_height(end_balance)
        self.play(
            self.net_worth_bar.animate.stretch_to_fit_height(new_total_height, about_edge=DOWN),
            FadeOut(flying_copy),
            self.networth_tracker.animate.set_value(end_balance),
            run_time=1.2 * t,
        )

        if slow:
            self.wait(0.8)

        return end_balance