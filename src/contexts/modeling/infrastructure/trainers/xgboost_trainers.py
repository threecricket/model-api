import io
from typing import Any, Callable

import joblib
import numpy as np
import xgboost as xgb
from sklearn.metrics import accuracy_score, log_loss, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from contexts.modeling.domain.ports.model_trainer import FitResult, PredictResult
from contexts.modeling.infrastructure.trainers.sklearn_trainers import _split_data


class _XGBoostTrainer:
    def __init__(
        self,
        model_type: str,
        factory: Callable[..., Any],
        is_classifier: bool,
    ) -> None:
        self._model_type = model_type
        self._factory = factory
        self._is_classifier = is_classifier

    @property
    def model_type(self) -> str:
        return self._model_type

    def fit(self, X: np.ndarray, y: np.ndarray, options: dict) -> FitResult:
        hyperparams = options.get("hyperparams", {})
        model = self._factory(**hyperparams)

        X_train, X_eval, y_train, y_eval = _split_data(X, y, options)
        model.fit(X_train, y_train)

        metrics = self._compute_metrics(model, X_eval, y_eval)
        return FitResult(artifact=model, metrics=metrics)

    def predict(self, artifact: Any, X: np.ndarray) -> PredictResult:
        probabilities = None

        if self._is_classifier and hasattr(artifact, "predict_proba"):
            proba = artifact.predict_proba(X)
            probabilities = [[float(p) for p in row] for row in proba]
            predictions = [
                float(row[1]) if len(row) > 1 else float(row[0]) for row in proba
            ]
        else:
            raw_predictions = artifact.predict(X)
            predictions = [float(value) for value in raw_predictions]

        return PredictResult(predictions=predictions, probabilities=probabilities)

    def serialize(self, artifact: Any) -> bytes:
        buffer = io.BytesIO()
        joblib.dump(artifact, buffer)
        return buffer.getvalue()

    def deserialize(self, data: bytes) -> Any:
        return joblib.load(io.BytesIO(data))

    def _compute_metrics(self, model: Any, X: np.ndarray, y: np.ndarray) -> dict[str, float]:
        predictions = model.predict(X)

        if self._is_classifier:
            metrics: dict[str, float] = {
                "accuracy": float(accuracy_score(y, predictions)),
            }
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(X)
                if len(set(y.tolist())) > 1:
                    metrics["log_loss"] = float(log_loss(y, proba))
            return metrics

        return {
            "mse": float(mean_squared_error(y, predictions)),
            "r2": float(r2_score(y, predictions)),
        }


XGBOOST_TRAINERS = [
    _XGBoostTrainer("xgboost.classifier", xgb.XGBClassifier, is_classifier=True),
    _XGBoostTrainer("xgboost.regressor", xgb.XGBRegressor, is_classifier=False),
]
