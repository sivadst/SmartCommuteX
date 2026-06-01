class TravelTimePredictor:
    def predict_duration_seconds(
        self, *, base_duration_seconds: float, traffic_score: float, mode: str
    ) -> tuple[float, float]:
        mode_penalty = {
            "walk": 0.05,
            "bike": 0.12,
            "ev": 0.38,
            "rideshare": 0.44,
            "transit": 0.26,
        }.get(mode, 0.2)
        uplift = 1 + ((traffic_score / 100) * mode_penalty)
        predicted = round(base_duration_seconds * uplift, 2)
        reliability = round(max(0.52, 0.98 - ((traffic_score / 100) * mode_penalty)), 3)
        return predicted, reliability

