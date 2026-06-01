class CarbonScoringEngine:
    _emission_factors = {
        "walk": 0.0,
        "bike": 0.0,
        "ev": 0.065,
        "rideshare": 0.192,
        "transit": 0.052,
    }

    _cost_per_km = {
        "walk": 0.0,
        "bike": 0.09,
        "ev": 0.58,
        "rideshare": 0.82,
        "transit": 0.16,
    }

    _base_cost = {
        "walk": 0.0,
        "bike": 0.9,
        "ev": 4.5,
        "rideshare": 5.8,
        "transit": 1.2,
    }

    def emissions_kg(self, *, mode: str, distance_meters: float) -> float:
        kilometers = distance_meters / 1000
        return round(kilometers * self._emission_factors.get(mode, 0.1), 3)

    def trip_cost_usd(self, *, mode: str, distance_meters: float) -> float:
        kilometers = distance_meters / 1000
        return round(self._base_cost.get(mode, 0.0) + (kilometers * self._cost_per_km.get(mode, 0.0)), 2)

    def sustainability_rating(self, emissions_kg: float) -> str:
        if emissions_kg <= 0.05:
            return "A+"
        if emissions_kg <= 0.4:
            return "A"
        if emissions_kg <= 0.9:
            return "B"
        if emissions_kg <= 1.5:
            return "C"
        return "D"

