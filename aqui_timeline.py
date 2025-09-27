from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re

# Global variables

_current_academic_year = [2025, 2026]

_colors = {
    "activity": "red",
    "competition": "blue",
    "exam": "green",
    "resit": "green",
    "holiday": "grey",
    "other": "goldenrod",
}

# Fun set_academic_year
# This function overwrites the default global _current_academic_year. It also checks if two years
# are given as input and if these are consecutive years.
 
def set_academic_year(years: list[int]):
    """
    Update the academic year range.

    Example use: 
        set_academic_year([2026, 2027])
    """
    global _current_academic_year
    if not (isinstance(years, list) and len(years) == 2):
        raise ValueError("Academic year must be a list of two years, e.g. [2025, 2026]")
    if years[1] - years[0] != 1:
        raise ValueError("Academic year must span exactly one year, e.g. [2025, 2026]")
    _current_academic_year = years

# Fun get_academic_year
# This function is called in the funtion plot_timeline and the class Event to force the academic years 
# to update after the aqui_timeline module is imported.

def get_academic_year() -> list[int]:
    """Return the current academic year list."""
    return _current_academic_year

# Fun get_colors
# This function is called in the funtion plot_timeline to force the colors to update after
# the aqui_timeline module is imported. It may also allow the user to see what colors are specified.

def get_colors() -> dict[str, str]:
    """Return the current color mapping for event types."""
    return _colors

# Fun is_valid_color
# This function checks if the inputed color in set_colors is an alphabetic string, HEX or RGB code.

def is_valid_color(value) -> bool:
    """Check if a color string is valid."""
    if isinstance(value, str):
        # Named color (basic check)
        if value.isalpha():
            return True
        # HEX code check
        if re.match(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", value):
            return True
    elif isinstance(value, tuple) and len(value) == 3:
        # RGB tuple check
        return all(isinstance(c, int) and 0 <= c <= 255 for c in value)
    return False

# Fun set_colors
# This function allows the user to specify colors for the timeline. An error is raised if the  
# is_valid_color function returns False.

def set_colors(new_colors: dict[str, str]):
    """
    Update colors that are show on the timeline.

    Example use:
        set_colors({'activity': 'red',           # <- color name
                    'competition': '#FF5733',    # <- HEX  
                    'exam': (0, 128, 255)})      # <- RGB
    """
    for key, value in new_colors.items():
        if not is_valid_color(value):
            raise ValueError(f"Invalid color '{value}' for '{key}'")
    global _colors
    _colors.update(new_colors)

# Fun plot_timeline
# This function takes all user defined events and plots them on the timeline

def plot_timeline(events):
    """Plots the timeline!"""
    ay = get_academic_year()

    fig, ax = plt.subplots(figsize=(12, 4))

    # X-axis limits = academic year
    start = datetime(ay[0], 9, 1)
    end = datetime(ay[1], 8, 31)
    ax.set_xlim(start, end)

    # Baseline
    ax.hlines(1, start, end, linewidth=1, color="black")

    plot_colors = get_colors()

    # Define lengths by type
    vline_lengths = {
        "activity": 1.06,    # long
        "competition": 1.05, # medium
        "other": 1.02        # short
    }

    for ev in events:
        col = plot_colors.get(ev.event_type, "black")

        if ev.event_type in ("exam", "resit", "holiday"):
            ax.fill_between([ev.date, ev.end], 0.995, 1.005, color=col, alpha=0.3)
            mid = ev.date + (ev.end - ev.date) / 2
            label_y = 1.0065 if ev.event_type == "resit" else 0.99
            ax.text(mid, label_y, ev.name, ha="center", va="bottom", fontsize=9, color=col)

        else:
            # pick vline length based on type
            vline_top = vline_lengths.get(ev.event_type, 1.02)  # default short if type unknown

            ax.vlines(ev.date, 1, vline_top, color=col, linewidth=1)
            ax.plot(
                ev.date,
                1,
                marker="o",
                markerfacecolor="white",
                markeredgecolor=col,
                markersize=8,
            )
            ax.annotate(
                ev.name,
                xy=(ev.date, vline_top),
                xytext=(0, 10),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    ax.get_yaxis().set_visible(False)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_position(("data", 0.98))

    plt.tight_layout()
    plt.show()

# class Event 
# This class takes the user defined values: name, event_type, month, and day. These are processed to
# automatically set the correct years and durations of exam weeks and holidays. Two functions allow to
# reset (reset_events) and show some contents (show_events) of all events. 

class Event:
    all_events = []

    def __init__(self, name, event_type, month, day):
        self.name = name        
        self.event_type = event_type
        self.month = month
        self.day = day

        ay = get_academic_year()
        self.year = ay[1] if month < 9 else ay[0]
        self.date = datetime(self.year, self.month, self.day)

        if self.event_type in ("exam", "resit"):
            self.end = self.date + timedelta(days=4)  # day 1 + 4 days
        elif self.event_type == "holiday":
            if self.month == 12:
                self.end = self.date + timedelta(days=13)  # day 1 + 13 days 
            else:
                self.end = datetime(self.year, 8, 31)
        else:
            self.end = self.date

        Event.all_events.append(self)

    @classmethod
    def reset_events(cls):
        cls.all_events = []

    @classmethod
    def show_events(cls):
        for e in cls.all_events:
            print(e)

    def __repr__(self):
        return (
            f"Event({self.name}, {self.event_type}, "
            f"{self.date.strftime('%Y-%m-%d')}, {self.end.strftime('%Y-%m-%d')})"
        )
