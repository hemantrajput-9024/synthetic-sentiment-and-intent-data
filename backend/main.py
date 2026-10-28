from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import joblib
from fastapi import FastAPI, Request
from pydantic import BaseModel, ConfigDict, Field, StringConstraints


PROJECT_DIR = Path(__file__).resolve().parent.parent
ARTIFACT_NAMES = ("label_encoder.pkl", "tfidf_vectorizer.pkl", "xgb_model.pkl")
MODEL_DIR = next(
    (
        directory
        for directory in (Path(__file__).resolve().parent, PROJECT_DIR)
        if all((directory / name).is_file() for name in ARTIFACT_NAMES)
    ),
    PROJECT_DIR,
)
MAX_BATCH_SIZE = 1000
MessageText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: MessageText


class BatchPredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    texts: list[MessageText] = Field(min_length=1, max_length=MAX_BATCH_SIZE)


class ClassProbability(BaseModel):
    label: str
    probability: float


class PredictionResponse(BaseModel):
    text: str
    label: str
    confidence: float
    probabilities: list[ClassProbability]


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionResponse]


@asynccontextmanager
async def lifespan(app: FastAPI):
    encoder = joblib.load(MODEL_DIR / "label_encoder.pkl")
    vectorizer = joblib.load(MODEL_DIR / "tfidf_vectorizer.pkl")
    model = joblib.load(MODEL_DIR / "xgb_model.pkl")
    app.state.encoder = encoder
    app.state.vectorizer = vectorizer
    app.state.model = model
    yield


app = FastAPI(
    title="Signal NLP API",
    description="Sentiment and intent predictions for customer messages.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/model-info")
def model_info(request: Request) -> dict[str, object]:
    encoder = request.app.state.encoder
    vectorizer = request.app.state.vectorizer
    return {
        "classes": [str(label) for label in encoder.classes_],
        "feature_count": len(vectorizer.vocabulary_),
    }


def predict_texts(request: Request, texts: list[str]) -> list[PredictionResponse]:
    vectorizer = request.app.state.vectorizer
    model = request.app.state.model
    encoder = request.app.state.encoder

    features = vectorizer.transform(texts)
    predicted_ids = model.predict(features)
    all_probabilities = model.predict_proba(features)
    labels = [str(label) for label in encoder.classes_]
    predicted_labels = encoder.inverse_transform(predicted_ids)
    predictions = []

    for text, label, probabilities in zip(texts, predicted_labels, all_probabilities):
        ranked_probabilities = sorted(
            (
                ClassProbability(label=class_name, probability=float(probability))
                for class_name, probability in zip(labels, probabilities)
            ),
            key=lambda item: item.probability,
            reverse=True,
        )
        predictions.append(
            PredictionResponse(
                text=text,
                label=str(label),
                confidence=ranked_probabilities[0].probability,
                probabilities=ranked_probabilities,
            )
        )

    return predictions


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest, request: Request) -> PredictionResponse:
    return predict_texts(request, [payload.text])[0]


@app.post("/predict/batch", response_model=BatchPredictionResponse)
def predict_batch(
    payload: BatchPredictionRequest,
    request: Request,
) -> BatchPredictionResponse:
    return BatchPredictionResponse(
        predictions=predict_texts(request, payload.texts)
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
