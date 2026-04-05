import numpy as np
from sklearn.linear_model import LogisticRegression
import pickle
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")


class RiskModel:
    """
    AI-powered risk assessment model for insurance premium calculation.

    Predicts disruption probability using:
    - Rain probability (0-1)
    - Temperature (celsius)
    - Historical disruption rate (0-1)
    - Location risk score (0-1, e.g., flood-prone zones)
    - Seasonal trend factor (0-1, e.g., monsoon=high)

    Expected Loss: EL = P × (I_d × D)
    Weekly Premium: Premium = EL × (1 + α + β)
    """

    def __init__(self):
        self.model = LogisticRegression()
        self.is_trained = False
        # Configurable profit margin and safety buffer
        self.profit_margin = 0.05  # α (alpha)
        self.safety_buffer = 0.02  # β (beta)
        self._load_or_train_model()

    def _load_or_train_model(self):
        """Load existing model or train initial model if no saved model exists."""
        if os.path.exists(MODEL_PATH):
            self.load_model()
        else:
            self._train_initial_model()

    def _train_initial_model(self):
        """
        Train initial model with synthetic data based on CLAUDE.md specification.
        Features: [rain_prob, temperature, historical_disruption, location_risk, seasonal_trend]
        """
        X = np.array([
            [0.1, 25, 0.05, 0.1, 0.1],  # Clear day, low risk, non-monsoon
            [0.8, 28, 0.6, 0.7, 0.9],   # High rain prob, flood-prone, monsoon
            [0.9, 30, 0.8, 0.9, 1.0],   # Extreme conditions, high disruption
            [0.2, 22, 0.1, 0.2, 0.3],   # Mild conditions, low historical risk
            [0.5, 35, 0.4, 0.5, 0.8],   # Moderate rain, summer heat, moderate risk
            [0.3, 20, 0.2, 0.3, 0.2],   # Cool, dry, low seasonal impact
            [0.95, 27, 0.9, 0.95, 1.0], # Worst case: heavy rain + flood zone + monsoon
        ])
        y = np.array([0, 1, 1, 0, 1, 0, 1])  # Disruption occurred?
        self.model.fit(X, y)
        self.is_trained = True
        self.save_model()

    def save_model(self):
        """Persist trained model to disk."""
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self.model, f)

    def load_model(self):
        """Load pre-trained model from disk."""
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
                self.is_trained = True

    def retrain(self, historical_data: list, disruption_outcomes: list):
        """
        Retrain model with collected real-world data.

        Args:
            historical_data: List of [rain_prob, temp, hist_disruption, location_risk, seasonal_trend]
            disruption_outcomes: List of actual disruption outcomes (0 or 1)
        """
        X = np.array(historical_data)
        y = np.array(disruption_outcomes)
        self.model.fit(X, y)
        self.is_trained = True
        self.save_model()

    def predict_risk(
        self,
        rain_probability: float,
        temperature: float,
        historical_disruption: float,
        location_risk: float,
        seasonal_trend: float
    ) -> float:
        """
        Predict probability of disruption event occurring.

        Args:
            rain_probability: Probability of rain (0-1)
            temperature: Temperature in celsius
            historical_disruption: Historical disruption rate for area (0-1)
            location_risk: Location risk score e.g., flood-prone zones (0-1)
            seasonal_trend: Seasonal factor e.g., monsoon=high (0-1)

        Returns:
            Probability of disruption (0-1), rounded to 4 decimals
        """
        if not self.is_trained:
            self._load_or_train_model()

        features = np.array([[
            rain_probability,
            temperature,
            historical_disruption,
            location_risk,
            seasonal_trend
        ]])
        prob = self.model.predict_proba(features)[0][1]
        return round(float(prob), 4)

    def calculate_expected_loss(self, daily_income: float, days_lost: int, disruption_probability: float) -> float:
        """
        Calculate expected income loss using formula from CLAUDE.md:
        EL = P × (I_d × D)

        Args:
            daily_income: I_d = average daily income of worker
            days_lost: D = expected working days lost in a week
            disruption_probability: P = probability of disruption (0-1)

        Returns:
            Expected loss amount
        """
        return disruption_probability * (daily_income * days_lost)

    def calculate_weekly_premium(
        self,
        daily_income: float,
        disruption_probability: float,
        days_lost: int = 1,
        profit_margin: float = None,
        safety_buffer: float = None,
        zone_safe_from_waterlogging: bool = False
    ) -> float:
        """
        Calculate weekly premium using formula from CLAUDE.md:
        Premium = EL × (1 + α + β)

        Args:
            daily_income: Average daily income (I_d)
            disruption_probability: Predicted disruption probability (P)
            days_lost: Expected working days lost (D)
            profit_margin: α (alpha) - override default if provided
            safety_buffer: β (beta) - override default if provided

        Returns:
            Weekly premium amount, capped at 10% of weekly income
        """
        alpha = profit_margin if profit_margin is not None else self.profit_margin
        beta = safety_buffer if safety_buffer is not None else self.safety_buffer

        # EL = P × (I_d × D)
        expected_loss = self.calculate_expected_loss(daily_income, days_lost, disruption_probability)

        # Premium = EL × (1 + α + β)
        premium = expected_loss * (1 + alpha + beta)

        # Hyper-local Dynamic Deduction: Charge ₹2 less if safe from water logging
        if zone_safe_from_waterlogging:
            premium -= 2.0

        # Cap premium at 10% of weekly income (7 days)
        max_premium = (daily_income * 7) * 0.10
        return max(0.0, round(min(premium, max_premium), 2))

    def update_model_parameters(self, profit_margin: float = None, safety_buffer: float = None):
        """Update model configuration parameters."""
        if profit_margin is not None:
            self.profit_margin = profit_margin
        if safety_buffer is not None:
            self.safety_buffer = safety_buffer


# Singleton instance for application-wide use
risk_model = RiskModel()
