from django.shortcuts import render
from typing import Any, Dict, List, Tuple
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
import pytz
import math


def get_number_positions() -> Tuple[Dict[int, int], Dict[int, int]]:
    """Calculate positions for both 12-hour and 60-minute/second numbers."""
    # Define number names
    hour_names = {
        1: "one",
        2: "two",
        3: "three",
        4: "four",
        5: "five",
        6: "six",
        7: "seven",
        8: "eight",
        9: "nine",
        10: "ten",
        11: "eleven",
        12: "twelve",
    }

    all_names = {
        **hour_names,
        13: "thirteen",
        14: "fourteen",
        15: "fifteen",
        16: "sixteen",
        17: "seventeen",
        18: "eighteen",
        19: "nineteen",
        20: "twenty",
        21: "twenty-one",
        22: "twenty-two",
        23: "twenty-three",
        24: "twenty-four",
        25: "twenty-five",
        26: "twenty-six",
        27: "twenty-seven",
        28: "twenty-eight",
        29: "twenty-nine",
        30: "thirty",
        31: "thirty-one",
        32: "thirty-two",
        33: "thirty-three",
        34: "thirty-four",
        35: "thirty-five",
        36: "thirty-six",
        37: "thirty-seven",
        38: "thirty-eight",
        39: "thirty-nine",
        40: "forty",
        41: "forty-one",
        42: "forty-two",
        43: "forty-three",
        44: "forty-four",
        45: "forty-five",
        46: "forty-six",
        47: "forty-seven",
        48: "forty-eight",
        49: "forty-nine",
        50: "fifty",
        51: "fifty-one",
        52: "fifty-two",
        53: "fifty-three",
        54: "fifty-four",
        55: "fifty-five",
        56: "fifty-six",
        57: "fifty-seven",
        58: "fifty-eight",
        59: "fifty-nine",
        60: "sixty",
    }

    # Sort hours
    hour_positions = sorted(
        [(num, name) for num, name in hour_names.items()], key=lambda x: x[1]
    )
    hour_map = {num: idx + 1 for idx, (num, _) in enumerate(hour_positions)}

    # Sort all numbers
    all_positions = sorted(
        [(num, name) for num, name in all_names.items()], key=lambda x: x[1]
    )
    all_map = {num: idx + 1 for idx, (num, _) in enumerate(all_positions)}

    return hour_map, all_map


def calculate_hand_angles(
    hours: int,
    minutes: int,
    seconds: int,
    hour_map: Dict[int, int],
    all_map: Dict[int, int],
) -> Dict[str, float]:
    """Calculate angles for all clock hands."""
    # Convert 24-hour format to 12-hour format
    hours_12 = hours % 12 or 12  # Convert 0 to 12

    # Calculate angles in degrees
    hour_angle = (hour_map[hours_12] - 3 + minutes / 60) * 30  # 30 degrees per hour
    minute_angle = (all_map[minutes + 1] - 15) * 6  # 6 degrees per minute
    second_angle = (all_map[seconds + 1] - 15) * 6  # 6 degrees per second

    # Convert to radians
    return {
        "hour_angle": math.radians(hour_angle),
        "minute_angle": math.radians(minute_angle),
        "second_angle": math.radians(second_angle),
    }


def get_available_timezones() -> List[Tuple[str, str]]:
    """Get list of available timezones with their display names."""
    return [(tz, tz.replace("_", " ").title()) for tz in pytz.common_timezones]


def get_clock_data(timezone_name: str = "UTC") -> Dict[str, Any]:
    """Generate all clock data for the current time in the specified timezone."""
    # Get timezone
    tz = pytz.timezone(timezone_name)

    # Get current time in the specified timezone
    now = timezone.now().astimezone(tz)

    hour_map, all_map = get_number_positions()
    angles = calculate_hand_angles(now.hour, now.minute, now.second, hour_map, all_map)

    return {
        "hours": now.hour % 12,
        "minutes": now.minute,
        "seconds": now.second,
        "digital_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "is_am": now.hour < 12,
        "hour_map": hour_map,
        "all_map": all_map,
        "timezone": timezone_name,
        "timezone_display": timezone_name.replace("_", " ").title(),
        **angles,
    }


def index(request: HttpRequest) -> Any:
    """Render the main page with clock data."""
    # Get timezone from session or default to UTC
    timezone_name = request.session.get("timezone", "UTC")
    context = get_clock_data(timezone_name)
    context["available_timezones"] = get_available_timezones()
    return render(request, "core/index.html", context)


def get_time_data(request: HttpRequest) -> JsonResponse:
    """Return current time data as JSON for AJAX updates."""
    # Get timezone from session or default to UTC
    timezone_name = request.session.get("timezone", "UTC")
    clock_data = get_clock_data(timezone_name)
    # Convert angles to degrees for JavaScript
    return JsonResponse(
        {
            "hours": clock_data["hours"],
            "minutes": clock_data["minutes"],
            "seconds": clock_data["seconds"],
            "digital_time": clock_data["digital_time"],
            "is_am": clock_data["is_am"],
            "hour_angle": math.degrees(clock_data["hour_angle"]),
            "minute_angle": math.degrees(clock_data["minute_angle"]),
            "second_angle": math.degrees(clock_data["second_angle"]),
            "timezone": clock_data["timezone"],
            "timezone_display": clock_data["timezone_display"],
        }
    )


def set_timezone(request: HttpRequest) -> JsonResponse:
    """Set the user's timezone preference."""
    timezone_name = request.POST.get("timezone", "UTC")
    if timezone_name in pytz.common_timezones:
        request.session["timezone"] = timezone_name
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Invalid timezone"})
