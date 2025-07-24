from datetime import datetime, timedelta
import pandas as pd


def detect_jump_without_current(df: pd.DataFrame, t: datetime, jump_threshold: timedelta) -> bool:
    prev = df[df["timestamp"] < t].tail(1)
    next_ = df[df["timestamp"] > t].head(1)

    if prev.empty or next_.empty:
        return False

    prev_state, prev_time = prev.iloc[0]["State"], prev.iloc[0]["timestamp"]
    next_state, next_time = next_.iloc[0]["State"], next_.iloc[0]["timestamp"]

    return prev_state != next_state and (next_time - prev_time) <= jump_threshold


def detect_jump_with_current(df: pd.DataFrame, t: datetime, current_state: str, jump_threshold: timedelta) -> bool:
    prev = df[df["timestamp"] < t].tail(1)
    next_ = df[df["timestamp"] > t].head(1)

    if prev.empty or next_.empty:
        return False

    prev_state, prev_time = prev.iloc[0]["State"], prev.iloc[0]["timestamp"]
    next_state, next_time = next_.iloc[0]["State"], next_.iloc[0]["timestamp"]

    jump_window = (next_time - prev_time) <= jump_threshold
    state_discontinuity = (
        current_state != prev_state or current_state != next_state
    )

    return jump_window and state_discontinuity