class RetryManager:
    """
    Generates progressive widening time windows.
    """

    PERIOD_SEQUENCE = [
        "1mo",
        "3mo",
        "6mo",
        "1y",
        "2y",
        "5y",
        "10y",
        "max"
    ]

    def generate_attempt_profiles(self, base_profile: dict, max_attempts: int):
        """
        Returns list of time profiles for retry attempts.
        """

        if "period" not in base_profile:
            return [base_profile]

        base_period = base_profile["period"]

        if base_period not in self.PERIOD_SEQUENCE:
            return [base_profile]

        start_index = self.PERIOD_SEQUENCE.index(base_period)

        profiles = []
        for i in range(start_index, len(self.PERIOD_SEQUENCE)):
            if len(profiles) >= max_attempts:
                break

            profiles.append({
                "period": self.PERIOD_SEQUENCE[i],
                "interval": base_profile["interval"]
            })

        return profiles