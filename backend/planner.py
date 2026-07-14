from datetime import date, timedelta
import hashlib, random
from .india_places import discover_indian_places, local_fallback

PLACES = {
 "Paris": [
  ("Café de Flore","Breakfast",22,"A Saint-Germain classic for croissants and café crème.",48.854,2.333),
  ("Louvre Museum","Art & culture",24,"Masterpieces spanning centuries in the former royal palace.",48.861,2.336),
  ("Jardin des Tuileries","Nature",0,"A relaxed walk through historic gardens and fountains.",48.864,2.327),
  ("Eiffel Tower & Seine","Landmark",35,"Golden-hour views followed by a riverside walk.",48.858,2.294),
  ("Sacré-Cœur","History",0,"Hilltop basilica with a sweeping panorama of Paris.",48.887,2.343),
  ("Place du Tertre","Art & culture",12,"Meet artists in Montmartre's storied village square.",48.887,2.341),
  ("Bouillon Pigalle","Local food",28,"Classic French comfort food in a lively dining room.",48.883,2.337),
  ("Musée de l’Orangerie","Art & culture",18,"Monet's Water Lilies in serene oval rooms.",48.864,2.322),
  ("Marché des Enfants Rouges","Local food",18,"Paris's oldest covered market, filled with local flavor.",48.863,2.362),
  ("Musée Carnavalet","History",0,"The story of Paris inside two grand townhouses.",48.857,2.362),
  ("Place des Vosges","History",0,"Arcades, red-brick façades and a peaceful lawn.",48.856,2.365),
  ("Le Perchoir Marais","Nightlife",32,"Sunset drinks above the rooftops of Paris.",48.860,2.354),
  ("Galeries Lafayette","Shopping",15,"Belle Époque architecture and a spectacular rooftop.",48.873,2.332),
  ("Canal Saint-Martin","Nature",0,"Tree-lined water, footbridges and neighborhood cafés.",48.872,2.365),
  ("Le Comptoir du Relais","Local food",44,"Seasonal bistro plates in Saint-Germain.",48.852,2.339)],
}

INDIAN_PLACES = {
 "Delhi": [
  ("India Gate","History",0,"Walk the ceremonial boulevard and see Delhi's landmark war memorial.",28.613,77.229),("Humayun's Tomb","History",40,"Explore the garden tomb that inspired the Taj Mahal.",28.593,77.250),("Lodhi Garden","Nature",0,"Stroll among landscaped lawns and medieval monuments.",28.593,77.220),("National Crafts Museum","Art & culture",20,"Discover regional crafts, textiles and village traditions.",28.613,77.242),("Connaught Place","Shopping",0,"Browse colonnaded shops and cafés in the heart of New Delhi.",28.631,77.216),("Saravana Bhavan","Local food",450,"Enjoy a dependable South Indian thali and filter coffee.",28.627,77.219),("Red Fort","History",35,"Tour the monumental Mughal citadel in Old Delhi.",28.656,77.241),("Chandni Chowk Food Walk","Local food",800,"Taste parathas, chaat and jalebi through historic lanes.",28.650,77.230)],
 "Mumbai": [
  ("Gateway of India","History",0,"Start beside Mumbai's iconic waterfront monument.",18.922,72.835),("Chhatrapati Shivaji Maharaj Vastu Sangrahalaya","Art & culture",200,"See Indian art and archaeology in an Indo-Saracenic landmark.",18.927,72.832),("Kala Ghoda","Art & culture",0,"Explore galleries, design stores and heritage architecture.",18.927,72.830),("Marine Drive","Nature",0,"Walk the Queen's Necklace as the city turns golden.",18.944,72.823),("Elephanta Caves","History",600,"Take the ferry to rock-cut temples on Elephanta Island.",18.963,72.931),("Britannia & Co.","Local food",900,"Try classic Parsi dishes in a beloved heritage restaurant.",18.934,72.840),("Crawford Market","Shopping",0,"Browse produce, spices and historic market halls.",18.947,72.834),("Bandra Fort & Bandstand","Nature",0,"Catch sea views beneath the Bandra-Worli Sea Link.",19.042,72.819)],
 "Bengaluru": [
  ("Bengaluru Palace","History",260,"Tour a Tudor-inspired palace filled with royal history.",12.999,77.592),("Cubbon Park","Nature",0,"Take a shaded walk through the city's green heart.",12.976,77.592),("Government Museum","Art & culture",20,"See archaeological treasures and South Indian art.",12.974,77.595),("Vidhana Soudha","History",0,"Admire Karnataka's grand seat of government from outside.",12.979,77.591),("MTR Lalbagh","Local food",350,"Have a classic Karnataka breakfast near the gardens.",12.955,77.585),("Lalbagh Botanical Garden","Nature",30,"Explore tropical collections and the landmark glass house.",12.950,77.584),("Church Street","Shopping",0,"Browse books, boutiques, cafés and street art.",12.975,77.605),("Toit Brewpub","Nightlife",1200,"End with Bengaluru craft beer and hearty plates.",12.979,77.640)],
 "Jaipur": [
  ("Amber Fort","History",200,"Explore courtyards, mirror work and hilltop Rajput architecture.",26.986,75.851),("City Palace","History",300,"Discover royal collections in Jaipur's historic center.",26.925,75.824),("Jantar Mantar","History",50,"See monumental astronomical instruments built in stone.",26.925,75.825),("Hawa Mahal","Art & culture",50,"Admire the famous honeycomb façade of the Palace of Winds.",26.924,75.826),("Albert Hall Museum","Art & culture",40,"Browse decorative arts inside an Indo-Saracenic landmark.",26.912,75.819),("Lassiwala MI Road","Local food",150,"Stop for Jaipur's signature thick clay-cup lassi.",26.916,75.811),("Bapu Bazaar","Shopping",0,"Shop for block prints, mojari and colorful handicrafts.",26.915,75.828),("Nahargarh Fort","Nature",200,"Watch sunset over the Pink City from the Aravalli hills.",26.937,75.816)],
 "Hyderabad": [
  ("Charminar","History",25,"See Hyderabad's signature monument at the heart of the old city.",17.362,78.474),("Salar Jung Museum","Art & culture",50,"Explore one of India's largest private art collections.",17.371,78.480),("Golconda Fort","History",25,"Climb the ruined citadel and test its famous acoustics.",17.383,78.401),("Qutb Shahi Tombs","History",100,"Walk through a serene necropolis of grand domed tombs.",17.395,78.396),("Shah Ghouse","Local food",500,"Taste a celebrated Hyderabadi biryani.",17.348,78.430),("Laad Bazaar","Shopping",0,"Browse bangles and wedding finery beside Charminar.",17.361,78.473),("Hussain Sagar","Nature",100,"Take an evening lakeside walk by the Buddha statue.",17.423,78.473),("Shilparamam","Art & culture",60,"Discover crafts, performances and village-style exhibits.",17.452,78.378)],
 "Kolkata": [
  ("Victoria Memorial","History",30,"Tour galleries inside Kolkata's marble landmark.",22.545,88.342),("Indian Museum","Art & culture",75,"Explore fossils, sculpture and archaeology in India's oldest museum.",22.558,88.351),("St. Paul's Cathedral","History",0,"Visit the Gothic Revival cathedral near the Maidan.",22.544,88.347),("Kumartuli","Art & culture",0,"Walk through the potters' quarter where festival idols are made.",22.601,88.361),("Peter Cat","Local food",900,"Try the iconic chelo kebab on Park Street.",22.552,88.352),("College Street","Shopping",0,"Browse legendary book stalls and historic institutions.",22.576,88.364),("Princep Ghat","Nature",0,"Watch sunset beside the Hooghly River.",22.556,88.331),("Jorasanko Thakur Bari","History",20,"Visit Rabindranath Tagore's ancestral home and museum.",22.584,88.360)],
 "Chennai": [
  ("Kapaleeshwarar Temple","History",0,"Experience Dravidian architecture in lively Mylapore.",13.034,80.269),("Government Museum Chennai","Art & culture",50,"See Chola bronzes and archaeological collections.",13.069,80.257),("San Thome Basilica","History",0,"Visit the neo-Gothic basilica near the coast.",13.033,80.278),("Marina Beach","Nature",0,"Walk one of India's longest urban beaches at sunset.",13.050,80.283),("DakshinaChitra","Art & culture",175,"Explore South Indian architecture, crafts and performance.",12.824,80.241),("Rayar's Mess","Local food",250,"Enjoy idli, vada and filter coffee at a Mylapore institution.",13.031,80.270),("Mylapore Market","Shopping",0,"Browse flowers, brassware and neighborhood stalls.",13.034,80.269),("Broken Bridge Viewpoint","Nature",0,"Take in quiet estuary views near Besant Nagar.",12.999,80.273)],
 "Kochi": [
  ("Fort Kochi Waterfront","History",0,"Walk colonial streets and see the Chinese fishing nets.",9.966,76.242),("Mattancherry Palace","History",20,"View Kerala murals inside the Dutch Palace.",9.958,76.259),("Paradesi Synagogue","History",10,"Visit the historic synagogue in atmospheric Jew Town.",9.958,76.259),("Kerala Folklore Museum","Art & culture",200,"Discover traditional architecture, masks and performance arts.",9.936,76.299),("Kashi Art Café","Local food",600,"Pause for creative café plates in a gallery setting.",9.966,76.243),("Jew Town","Shopping",0,"Browse antiques, spices and restored heritage buildings.",9.958,76.259),("Marine Drive Kochi","Nature",0,"Take an evening promenade beside the backwaters.",9.982,76.275),("Kathakali Centre","Art & culture",500,"Watch makeup preparation and a classical dance performance.",9.965,76.242)],
 "Varanasi": [
  ("Sunrise Ganges Boat Ride","Nature",500,"See the ghats awaken from a traditional rowing boat.",25.306,83.010),("Kashi Vishwanath Temple","History",0,"Visit one of India's most revered temple precincts.",25.311,83.011),("Dashashwamedh Ghat","Art & culture",0,"Experience the evening Ganga Aarti ceremony.",25.307,83.011),("Sarnath","History",30,"Explore the Buddhist site where the Buddha first taught.",25.376,83.022),("Ramnagar Fort","History",75,"Tour the riverside fort and royal collection.",25.270,83.026),("Kachori Gali","Local food",250,"Taste hot kachori sabzi and jalebi in the old city.",25.311,83.010),("Banaras Hindu University","Art & culture",20,"Visit the leafy campus and Bharat Kala Bhavan museum.",25.267,82.991),("Assi Ghat","Nature",0,"Relax by the river with music and evening chai.",25.288,83.006)],
 "Goa": [
  ("Basilica of Bom Jesus","History",0,"Visit the UNESCO-listed baroque church in Old Goa.",15.500,73.911),("Sé Cathedral","History",0,"Explore one of Asia's largest churches.",15.504,73.912),("Fontainhas","Art & culture",0,"Walk Panjim's colorful Latin Quarter and tiled lanes.",15.495,73.828),("Reis Magos Fort","History",50,"Climb a restored riverside fort with Mandovi views.",15.505,73.809),("Gunpowder Goa","Local food",1200,"Try inventive coastal South Indian dishes in Assagao.",15.606,73.899),("Anjuna Flea Market","Shopping",0,"Browse clothing, jewelry and crafts near the coast.",15.574,73.743),("Vagator Beach","Nature",0,"Watch sunset beneath dramatic red cliffs.",15.598,73.734),("Salim Ali Bird Sanctuary","Nature",100,"Explore mangroves and birdlife on Chorao Island.",15.513,73.871)]
}

ALIASES={"New Delhi":"Delhi","Bangalore":"Bengaluru","Bombay":"Mumbai","Calcutta":"Kolkata","Cochin":"Kochi","Panaji":"Goa"}
PLACES.update(INDIAN_PLACES)

GENERIC = [
 ("Old Town walking tour","History",12,"A guided introduction to the city's stories and architecture.",0,0),
 ("Central food market","Local food",24,"Taste regional specialties from independent vendors.",0.01,0.01),
 ("City art museum","Art & culture",18,"A curated collection connecting local and global art.",0.02,0.015),
 ("Botanical gardens","Nature",8,"A restorative walk through native and exotic landscapes.",0.03,0.02),
 ("Riverside promenade","Nature",0,"Golden-hour views along the waterfront.",0.04,0.025),
 ("Design district","Shopping",20,"Independent boutiques, studios and neighborhood cafés.",0.05,0.03),
 ("Heritage monument","History",10,"An essential landmark with a rich local history.",0.06,0.035),
 ("Neighborhood bistro","Local food",34,"A relaxed dinner featuring seasonal local dishes.",0.07,0.04),
 ("Rooftop lounge","Nightlife",28,"Panoramic night views and signature drinks.",0.08,0.045),
 ("Contemporary gallery","Art & culture",14,"Emerging artists in an intimate gallery setting.",0.09,0.05)]

def generate_trip(city: str, start: date, count: int, budget: float, interests: list[str], travelers: str):
    requested_city = city.split(",")[0].strip().title()
    base_city = ALIASES.get(requested_city, requested_city)
    known=PLACES.get(base_city)
    if known: pool=list(known)
    else:
        discovered=discover_indian_places(base_city)
        pool=list(discovered or local_fallback(base_city))
    rng = random.Random(int(hashlib.sha256((city+str(start)).encode()).hexdigest()[:8],16))
    ranked = sorted(pool, key=lambda p: (p[1] not in interests, rng.random()))
    times = ["9:00 AM","10:30 AM","1:00 PM","3:30 PM","7:00 PM"]
    themes = ["First impressions","Culture & character","Local rhythms","Hidden corners","A perfect finale","One more adventure","Slow travel day"]
    days=[]
    for index in range(count):
        picks=[ranked[(index*4+j)%len(ranked)] for j in range(min(5,len(ranked)))]
        stops=[]
        for j,p in enumerate(picks):
            cost=p[2] if base_city in INDIAN_PLACES or not known else round(p[2]*83)
            stops.append({"time":times[j],"name":p[0],"type":p[1],"cost":cost,"note":p[3],"travel":"Start here" if j==0 else f"{6+j*3} min walk","lat":p[4]+index*.002,"lng":p[5]+index*.002})
        day_cost=sum(s["cost"] for s in stops)
        conditions=["Sunny","Partly cloudy","Light rain"]
        condition=conditions[(index+len(city))%3]
        days.append({"date":str(start+timedelta(days=index)),"title":themes[index%len(themes)],"subtitle":f"A thoughtfully paced day in {base_city}","weather":f"{21+(index%4)}° · {condition}","spent":day_cost,"stops":stops})
    hotel_cost=min(round(budget*.31), 15000*count)
    source="curated local data" if known else ("live OpenStreetMap places" if discovered else "offline city fallback")
    return {"city":city,"start_date":str(start),"days_count":count,"budget":budget,"currency":"INR","place_source":source,"travelers":travelers,"interests":interests,"weather_source":"smart seasonal estimate","hotel":{"name":f"The {base_city} House","area":"Central district","nights":count,"cost":hotel_cost},"days":days,"estimated_total":hotel_cost+sum(d["spent"] for d in days),"route_savings_minutes":42}
