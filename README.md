# where ujwal wants to go — AI Trip Planner

Full-stack local-first MVP using React/Vite, FastAPI, and SQLite. Features include secure registration/login, personalized 1–7 day itinerary generation, weather-aware suggestions, route ordering, budget estimates, saved trips, editing, public share links, and print/PDF export.

## Run locally

```powershell
npm install
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload --port 8010
```

In a second terminal run `npm run dev`, then open http://localhost:5173. API docs are at http://localhost:8010/docs.

Set `ROAMLY_SECRET` to a long random value in production. Major Indian cities use curated data. Every other Indian city, district, and town uses live OpenStreetMap discovery with a city-labelled offline fallback. Set a contact-bearing `OSM_USER_AGENT`, respect community service limits, and use self-hosted Nominatim/Overpass endpoints for production traffic.

## Deploy to Render

The included `render.yaml` and `Dockerfile` deploy the frontend and backend as one service. In Render, choose **New → Blueprint**, connect this repository, and apply the detected blueprint. The configured persistent disk keeps saved trips across deployments.
