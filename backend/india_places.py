"""Nationwide Indian place discovery backed by OpenStreetMap.

The public endpoints can be replaced with self-hosted services through environment
variables. Results are cached in memory to avoid repeated community-API requests.
"""
import os
from functools import lru_cache
import httpx

NOMINATIM=os.getenv("NOMINATIM_URL","https://nominatim.openstreetmap.org")
OVERPASS=os.getenv("OVERPASS_URL","https://overpass-api.de/api/interpreter")
HEADERS={"User-Agent":os.getenv("OSM_USER_AGENT","where-ujwal-wants-to-go/1.0 (local trip planner)")}

def _category(tags):
    tourism=tags.get("tourism",""); amenity=tags.get("amenity",""); historic=tags.get("historic","")
    if amenity in {"restaurant","cafe","fast_food","food_court"}: return "Local food"
    if tourism in {"museum","gallery","artwork"}: return "Art & culture"
    if tourism in {"viewpoint","attraction","theme_park","zoo"}: return "Landmark"
    if historic or tags.get("heritage"): return "History"
    if tags.get("leisure") in {"park","garden","nature_reserve"}: return "Nature"
    if tags.get("shop") in {"mall","department_store","craft","marketplace"}: return "Shopping"
    return "Landmark"

def _cost(category):
    return {"Local food":450,"Art & culture":100,"History":50,"Nature":0,"Shopping":0,"Landmark":50}.get(category,0)

def _description(name,category,city):
    text={"Local food":"Enjoy a well-known local food stop", "Art & culture":"Discover local art, collections and culture", "History":"Explore an important piece of regional history", "Nature":"Take a restorative break in a local green space", "Shopping":"Browse local products, crafts and everyday finds", "Landmark":"Visit one of the area's notable sights"}[category]
    return f"{text} at {name} in {city}."

@lru_cache(maxsize=256)
def discover_indian_places(city):
    """Return OSM places for any settlement that geocodes inside India."""
    if os.getenv("ROAMLY_OFFLINE")=="1": return []
    try:
        with httpx.Client(headers=HEADERS,timeout=8,follow_redirects=True) as client:
            geo=client.get(f"{NOMINATIM}/search",params={"q":f"{city}, India","format":"jsonv2","limit":1,"countrycodes":"in","addressdetails":1}).json()
            if not geo or geo[0].get("address",{}).get("country_code")!="in": return []
            lat,lng=float(geo[0]["lat"]),float(geo[0]["lon"])
            query=f'''[out:json][timeout:18];(
              nwr(around:12000,{lat},{lng})[tourism~"attraction|museum|gallery|viewpoint|zoo"];
              nwr(around:12000,{lat},{lng})[historic];
              nwr(around:9000,{lat},{lng})[leisure~"park|garden|nature_reserve"];
              nwr(around:7000,{lat},{lng})[amenity~"restaurant|cafe"][name];
              nwr(around:7000,{lat},{lng})[shop~"mall|department_store|craft"][name];
            );out center tags 80;'''
            elements=client.post(OVERPASS,data={"data":query},timeout=30).json().get("elements",[])
        found=[]; seen=set()
        for item in elements:
            tags=item.get("tags",{}); name=tags.get("name:en") or tags.get("name")
            point=item.get("center",item); plat=point.get("lat"); plng=point.get("lon")
            if not name or not plat or not plng or name.casefold() in seen: continue
            seen.add(name.casefold()); category=_category(tags)
            found.append((name,category,_cost(category),_description(name,category,city),float(plat),float(plng)))
        # Keep variety while preferring named, useful POIs.
        found.sort(key=lambda p: ({"History":0,"Art & culture":1,"Landmark":2,"Nature":3,"Local food":4,"Shopping":5}.get(p[1],9),p[0]))
        return found[:30] if len(found)>=5 else []
    except (httpx.HTTPError,ValueError,KeyError):
        return []

def local_fallback(city):
    """City-labelled offline plan when community map services are unreachable."""
    return [
      (f"{city} heritage walk","History",0,f"Explore the historic heart and architectural character of {city}.",0,0),
      (f"{city} local market","Shopping",0,f"Browse regional produce, crafts and everyday life in {city}.",.01,.01),
      (f"{city} food trail","Local food",500,f"Sample the dishes and street-food traditions associated with {city}.",.02,.015),
      (f"{city} city museum","Art & culture",50,f"Learn about the art, people and history of {city}.",.03,.02),
      (f"{city} central park","Nature",0,f"Slow down with a green-space break in {city}.",.04,.025),
      (f"{city} sunset viewpoint","Landmark",0,f"End the day with a broad view across {city}.",.05,.03),
      (f"Old {city} neighborhood","History",0,f"Walk through one of {city}'s established neighborhoods.",.06,.035),
      (f"Regional restaurant in {city}","Local food",700,f"Try a relaxed dinner featuring regional recipes.",.07,.04)]
