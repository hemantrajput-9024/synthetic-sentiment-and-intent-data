# FastAPI backend

The API loads `label_encoder.pkl`, `tfidf_vectorizer.pkl`, and `xgb_model.pkl`
once when the application starts. It checks the `backend` folder first, then
the project root.

## Run locally

From the project root, install the dependencies in `requirements.txt`, then start
the API in one terminal:

```powershell
python main.py
```

The API is available at `http://127.0.0.1:8000`. Interactive documentation is at
`http://127.0.0.1:8000/docs`.

Start the Streamlit frontend in a second terminal:

```powershell
streamlit run app.py
```

The frontend reads `API_BASE_URL` from the project-root `.env` file. Change it
there if the backend is hosted at a different address.

## Run with Docker Compose

From the project root, build and start the backend:

```powershell
docker compose -f backend/docker-compose.yml up --build
```

Compose serves the API at `http://127.0.0.1:8000`, which matches the frontend's
default `API_BASE_URL`. Stop it with `Ctrl+C`, or run
`docker compose -f backend/docker-compose.yml down` in another terminal.

## Endpoints

- `GET /health` — service health check.
- `GET /model-info` — model class labels and feature count for the frontend.
- `POST /predict` — predict one message:

  ```json
  {"text": "Please cancel my order before it ships."}
  ```

- `POST /predict/batch` — predict up to 1,000 messages:

  ```json
  {"texts": ["The support team was wonderful.", "I need a refund."]}
  ```

Messages must contain 1–1,000 non-whitespace characters. Responses include the
predicted label, confidence, and probabilities for all model classes. Invalid
requests receive FastAPI's standard `422` validation response.
