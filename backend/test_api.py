import os
os.environ["ROAMLY_SECRET"]="test-secret"
os.environ["ROAMLY_OFFLINE"]="1"
from fastapi.testclient import TestClient
from .main import app
from .database import DB_PATH

def test_complete_trip_flow():
    if DB_PATH.exists(): DB_PATH.unlink()
    with TestClient(app) as client:
        auth=client.post('/api/auth/register',json={'name':'Alex Morgan','email':'alex@example.com','password':'secret1'})
        assert auth.status_code==201
        headers={'Authorization':'Bearer '+auth.json()['token']}
        trip=client.post('/api/trips',headers=headers,json={'city':'Paris, France','start_date':'2026-07-10','days_count':3,'budget':2000,'travelers':'2 adults','interests':['History']})
        assert trip.status_code==201 and len(trip.json()['itinerary']['days'])==3
        trip_id=trip.json()['id']
        assert len(client.get('/api/trips',headers=headers).json())==1
        shared=client.post(f'/api/trips/{trip_id}/share',headers=headers).json()['share_token']
        assert client.get('/api/shared/'+shared).status_code==200
        assert client.delete(f'/api/trips/{trip_id}',headers=headers).status_code==204

def test_indian_city_returns_local_places_and_inr():
    with TestClient(app) as client:
        guest=client.post('/api/auth/guest').json()
        headers={'Authorization':'Bearer '+guest['token']}
        response=client.post('/api/trips',headers=headers,json={'city':'Jaipur, India','start_date':'2026-11-10','days_count':2,'budget':80000,'travelers':'2 adults','interests':['History','Local food']})
        assert response.status_code==201
        plan=response.json()['itinerary']
        names={stop['name'] for day in plan['days'] for stop in day['stops']}
        assert plan['currency']=='INR'
        assert {'Amber Fort','Hawa Mahal','City Palace'} & names
        assert max(stop['cost'] for day in plan['days'] for stop in day['stops']) < 5000

def test_any_indian_town_has_a_named_offline_plan():
    with TestClient(app) as client:
        guest=client.post('/api/auth/guest').json()
        headers={'Authorization':'Bearer '+guest['token']}
        response=client.post('/api/trips',headers=headers,json={'city':'Madurai, Tamil Nadu, India','start_date':'2026-12-10','days_count':1,'budget':30000,'travelers':'Solo traveler','interests':['History']})
        plan=response.json()['itinerary']
        assert response.status_code==201
        assert plan['place_source']=='offline city fallback'
        assert all('Madurai' in stop['name'] for stop in plan['days'][0]['stops'])
