from datetime import datetime


class TrafficScoreEstimator:
    _mode_sensitivity = {
        "walk": 0.18,
        "bike": 0.35,
        "ev": 0.82,
        "rideshare": 0.92,
        "transit": 0.58,
    }

    def estimate(self, mode: str, departure_time: datetime, distance_meters: float) -> float:
        hour = departure_time.hour
        peak_multiplier = 1.0
        if 7 <= hour <= 10 or 17 <= hour <= 20:
            peak_multiplier = 1.3
        elif 11 <= hour <= 16:
            peak_multiplier = 0.92

        base = min(distance_meters / 2500, 22)
        sensitivity = self._mode_sensitivity.get(mode, 0.6)
        return round(min(100.0, 18 + (base * peak_multiplier * sensitivity * 2.8)), 2)

