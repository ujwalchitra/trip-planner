import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  CircleMarker,
  MapContainer,
  Polyline,
  Popup,
  TileLayer,
  Tooltip,
  useMap,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import {
  ArrowRight,
  CalendarDays,
  Check,
  CloudSun,
  Coffee,
  Compass,
  IndianRupee,
  Download,
  Hotel,
  Landmark,
  LogOut,
  Map,
  MapPin,
  Menu,
  RefreshCw,
  Share2,
  Sparkles,
  Sun,
  Trash2,
  Users,
  Utensils,
  WandSparkles,
  X,
} from "lucide-react";
import "./styles.css";
import "./extras.css";
import "./dark.css";
import "./map.css";
const API = "/api",
  icons = {
    Breakfast: Coffee,
    "Local food": Utensils,
    History: Landmark,
    "Art & culture": Landmark,
    Nature: Sun,
    Nightlife: Sparkles,
    Shopping: Sparkles,
  };
async function api(path, opt = {}) {
  let t = localStorage.roamly_token,
    r = await fetch(API + path, {
      ...opt,
      headers: {
        "Content-Type": "application/json",
        ...(t ? { Authorization: `Bearer ${t}` } : {}),
      },
    });
  if (!r.ok) {
    let d = {};
    try {
      d = await r.json();
    } catch {}
    throw Error(d.detail || "Request failed");
  }
  return r.status === 204 ? null : r.json();
}
function Auth({ done, close }) {
  let [login, setLogin] = useState(false),
    [f, setF] = useState({ name: "", email: "", password: "" }),
    [err, setErr] = useState(""),
    [busy, setBusy] = useState(false);
  async function send(e) {
    e.preventDefault();
    setBusy(true);
    setErr("");
    try {
      let d = await api("/auth/" + (login ? "login" : "register"), {
        method: "POST",
        body: JSON.stringify(f),
      });
      localStorage.roamly_token = d.token;
      done(d.user);
    } catch (x) {
      setErr(x.message);
    }
    setBusy(false);
  }
  return (
    <div className="modal">
      <form className="auth" onSubmit={send}>
        <button type="button" className="close" onClick={close}>
          <X />
        </button>
        <div className="brand">
          <span>
            <Compass />
          </span>
          Roamly
        </div>
        <h2>{login ? "Welcome back" : "Start your journey"}</h2>
        <p>Save and revisit every thoughtfully planned escape.</p>
        {!login && (
          <label>
            Your name
            <input
              required
              value={f.name}
              onChange={(e) => setF({ ...f, name: e.target.value })}
            />
          </label>
        )}
        <label>
          Email
          <input
            required
            type="email"
            value={f.email}
            onChange={(e) => setF({ ...f, email: e.target.value })}
          />
        </label>
        <label>
          Password
          <input
            required
            minLength="6"
            type="password"
            value={f.password}
            onChange={(e) => setF({ ...f, password: e.target.value })}
          />
        </label>
        {err && <div className="error">{err}</div>}
        <button className="generate" disabled={busy}>
          {busy ? "Please wait…" : login ? "Sign in" : "Create account"}
        </button>
        <button
          type="button"
          className="switch"
          onClick={() => setLogin(!login)}
        >
          {login
            ? "New here? Create an account"
            : "Already have an account? Sign in"}
        </button>
      </form>
    </div>
  );
}
function App() {
  let [user, setUser] = useState(null),
    [view, setView] = useState("plan"),
    [trip, setTrip] = useState(null),
    [saved, setSaved] = useState([]),
    [day, setDay] = useState(0),
    [toast, setToast] = useState(""),
    [loading, setLoading] = useState(false),
    [form, setForm] = useState({
      city: "Paris, France",
      start_date: "2026-07-10",
      days_count: 3,
      travelers: "2 adults",
      budget: 150000,
      interests: ["Art & culture", "Local food", "History"],
    });
  let note = (x) => {
    setToast(x);
    setTimeout(() => setToast(""), 2400);
  };
  async function ensureGuest() {
    if (localStorage.roamly_token) return;
    const session = await api("/auth/guest", { method: "POST" });
    localStorage.roamly_token = session.token;
    setUser(session.user);
  }
  useEffect(() => {
    ensureGuest().catch((x) => note(x.message));
    let m = location.pathname.match(/^\/share\/(.+)/);
    if (m)
      api("/shared/" + m[1])
        .then((x) => {
          setTrip(x);
          setView("trip");
        })
        .catch((x) => note(x.message));
  }, []);
  async function myTrips() {
    try {
      await ensureGuest();
      setSaved(await api("/trips"));
      setView("saved");
    } catch (x) {
      note(x.message);
    }
  }
  async function generate() {
    setLoading(true);
    try {
      await ensureGuest();
      let x = await api("/trips", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setTrip(x);
      setDay(0);
      setView("trip");
      note("Your itinerary is ready!");
    } catch (x) {
      note(x.message);
    }
    setLoading(false);
  }
  async function save(next) {
    setTrip(next);
    if (next.id)
      try {
        await api("/trips/" + next.id, {
          method: "PUT",
          body: JSON.stringify({ itinerary: next.itinerary }),
        });
      } catch (x) {
        note(x.message);
      }
  }
  async function share() {
    try {
      let d = await api(`/trips/${trip.id}/share`, { method: "POST" }),
        url = location.origin + d.path;
      await navigator.clipboard?.writeText(url);
      note("Share link copied");
    } catch (x) {
      note(x.message);
    }
  }
  return (
    <div>
      <header>
        <button className="brand" onClick={() => setView("plan")}>
          <span>
            <Compass />
          </span>
          where ujwal wants to go
        </button>
        <nav>
          <button
            className={view === "plan" ? "active" : ""}
            onClick={() => setView("plan")}
          >
            Plan a trip
          </button>
          <button
            className={view === "saved" ? "active" : ""}
            onClick={myTrips}
          >
            My trips
          </button>
          <button
            className={view === "explore" ? "active" : ""}
            onClick={() => setView("explore")}
          >
            Explore
          </button>
        </nav>
        <div className="profile">
          <div className="avatar">UJ</div>
          <span>Ujwal</span>
        </div>
        <button className="mobile">
          <Menu />
        </button>
      </header>
      {view === "plan" && (
        <Planner f={form} set={setForm} go={generate} busy={loading} />
      )}{" "}
      {view === "explore" && (
        <Explore
          choose={(city) => {
            setForm({ ...form, city });
            setView("plan");
            note(`${city} selected`);
          }}
        />
      )}
      {view === "saved" && (
        <Saved
          trips={saved}
          open={(x) => {
            setTrip(x);
            setDay(0);
            setView("trip");
          }}
          remove={async (id) => {
            await api("/trips/" + id, { method: "DELETE" });
            setSaved(saved.filter((x) => x.id !== id));
            note("Trip deleted");
          }}
        />
      )}{" "}
      {view === "trip" && trip && (
        <Trip
          data={trip}
          day={day}
          setDay={setDay}
          share={share}
          back={myTrips}
          save={save}
          note={note}
        />
      )}{" "}
      {toast && (
        <div className="toast">
          <Check />
          {toast}
        </div>
      )}
    </div>
  );
}
function Planner({ f, set, go, busy }) {
  let upd = (k, v) => set({ ...f, [k]: v }),
    ints = [
      "Art & culture",
      "Local food",
      "History",
      "Nature",
      "Shopping",
      "Nightlife",
    ];
  return (
    <main className="landing">
      <section className="intro">
        <div className="eyebrow">
          <Sparkles /> YOUR NEXT STORY STARTS HERE
        </div>
        <h1>
          Where will you
          <br />
          <em>go next?</em>
        </h1>
        <p>
          Tell us what you love. We’ll turn it into a thoughtful, day-by-day
          escape—made just for you.
        </p>
        <div className="trust">
          <div className="faces">
            <b>SK</b>
            <b>JP</b>
            <b>ML</b>
          </div>
          <span>
            <strong>4.9</strong> from 12,000+ happy travelers
          </span>
        </div>
      </section>
      <section className="planner-card">
        <div className="card-head">
          <div>
            <span>01</span>
            <h2>Let's shape your trip</h2>
          </div>
          <p>About 2 minutes</p>
        </div>
        <label>
          <span>Where do you want to go?</span>
          <div className="input">
            <MapPin />
            <input
              value={f.city}
              onChange={(e) => upd("city", e.target.value)}
            />
            <button onClick={() => upd("city", "")}>
              <X />
            </button>
          </div>
        </label>
        <div className="grid2">
          <label>
            <span>When?</span>
            <div className="input">
              <CalendarDays />
              <input
                type="date"
                value={f.start_date}
                onChange={(e) => upd("start_date", e.target.value)}
              />
            </div>
          </label>
          <label>
            <span>For how long?</span>
            <div className="input">
              <CalendarDays />
              <select
                value={f.days_count}
                onChange={(e) => upd("days_count", +e.target.value)}
              >
                {[1, 2, 3, 4, 5, 6, 7].map((n) => (
                  <option key={n}>{n}</option>
                ))}
              </select>
              <small>days</small>
            </div>
          </label>
        </div>
        <div className="grid2">
          <label>
            <span>Who's going?</span>
            <div className="input">
              <Users />
              <select
                value={f.travelers}
                onChange={(e) => upd("travelers", e.target.value)}
              >
                {["2 adults", "Solo traveler", "Family", "Friends"].map((x) => (
                  <option key={x}>{x}</option>
                ))}
              </select>
            </div>
          </label>
          <label>
            <span>Total budget</span>
            <div className="input">
              <IndianRupee />
              <input
                type="number"
                min="100"
                value={f.budget}
                onChange={(e) => upd("budget", +e.target.value)}
              />
              <small>INR</small>
            </div>
          </label>
        </div>
        <label>
          <span>What are you into?</span>
          <div className="chips">
            {ints.map((x) => (
              <button
                key={x}
                className={f.interests.includes(x) ? "selected" : ""}
                onClick={() =>
                  upd(
                    "interests",
                    f.interests.includes(x)
                      ? f.interests.filter((i) => i !== x)
                      : [...f.interests, x],
                  )
                }
              >
                {f.interests.includes(x) && <Check />}
                {x}
              </button>
            ))}
          </div>
        </label>
        <button className="generate" onClick={go} disabled={busy || !f.city}>
          {busy ? (
            <>
              <RefreshCw className="spin" /> Designing your escape…
            </>
          ) : (
            <>
              Create my itinerary <ArrowRight />
            </>
          )}
        </button>
        <p className="fine">
          <WandSparkles /> Smart, weather-aware & route optimized
        </p>
      </section>
    </main>
  );
}
function Explore({ choose }) {
  const destinations = [
    ["Jaipur, Rajasthan, India", "THE PINK CITY", "Forts, bazaars and royal stories", "fort"],
    ["Goa, India", "COASTAL ESCAPE", "Beaches, old quarters and slow sunsets", "coast"],
    ["Varanasi, Uttar Pradesh, India", "ANCIENT INDIA", "Sacred ghats and timeless rituals", "river"],
    ["Kochi, Kerala, India", "BACKWATER CULTURE", "Spice lanes, art and waterfront history", "green"],
    ["Mumbai, Maharashtra, India", "CITY OF DREAMS", "Heritage, food and sea-facing energy", "city"],
    ["Bengaluru, Karnataka, India", "GARDEN CITY", "Design, culture and creative food", "garden"],
    ["Delhi, India", "CAPITAL STORIES", "Monuments, markets and layered history", "capital"],
    ["Hyderabad, Telangana, India", "DECCAN FLAVOURS", "Forts, pearls and legendary biryani", "deccan"],
  ];
  return (
    <main className="explore">
      <section className="explore-head">
        <span>EXPLORE INDIA</span>
        <h1>Find your next <em>story.</em></h1>
        <p>Choose a destination to start planning, or enter any Indian city yourself.</p>
      </section>
      <section className="destination-grid">
        {destinations.map(([city, tag, text, tone], index) => (
          <article className={`destination ${tone}`} key={city}>
            <div className="destination-art">
              <span>{String(index + 1).padStart(2, "0")}</span>
              <MapPin />
            </div>
            <div className="destination-copy">
              <small>{tag}</small>
              <h2>{city.split(",")[0]}</h2>
              <p>{text}</p>
              <button onClick={() => choose(city)}>
                Plan this trip <ArrowRight />
              </button>
            </div>
          </article>
        ))}
      </section>
      <button className="all-india" onClick={() => choose("")}>
        <Compass /> Plan somewhere else in India
      </button>
    </main>
  );
}

function FitRoute({ points }) {
  const map = useMap();
  useEffect(() => {
    if (points.length === 1) map.setView(points[0], 13);
    if (points.length > 1) map.fitBounds(points, { padding: [28, 28] });
  }, [map, points]);
  return null;
}

function ItineraryMap({ stops }) {
  const located = stops.filter(
    (stop) => Number.isFinite(stop.lat) && Number.isFinite(stop.lng),
  );
  const points = located.map((stop) => [stop.lat, stop.lng]);
  if (!points.length)
    return (
      <div className="map-empty">
        <MapPin />
        <strong>Map coordinates unavailable</strong>
        <span>The itinerary is still available in the timeline.</span>
      </div>
    );
  return (
    <div className="realmap">
      <MapContainer center={points[0]} zoom={13} scrollWheelZoom>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FitRoute points={points} />
        {points.length > 1 && (
          <Polyline positions={points} pathOptions={{ color: "#f28a67", weight: 4 }} />
        )}
        {located.map((stop, index) => (
          <CircleMarker
            key={`${stop.name}-${index}`}
            center={[stop.lat, stop.lng]}
            radius={11}
            pathOptions={{ color: "#fff", weight: 2, fillColor: "#f28a67", fillOpacity: 1 }}
          >
            <Tooltip permanent direction="center" className="stop-number">
              {index + 1}
            </Tooltip>
            <Popup>
              <strong>{index + 1}. {stop.name}</strong>
              <br />{stop.time} · {stop.type}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
      <span className="map-key"><i /> Selected day route</span>
    </div>
  );
}

function Saved({ trips, open, remove }) {
  return (
    <main className="saved">
      <div className="savedhead">
        <span>YOUR COLLECTION</span>
        <h1>
          Trips worth <em>remembering.</em>
        </h1>
        <p>Your generated itineraries are safely saved here.</p>
      </div>
      {!trips.length ? (
        <div className="empty">
          <Compass />
          <h2>No trips yet</h2>
          <p>Create your first escape to see it here.</p>
        </div>
      ) : (
        <div className="tripgrid">
          {trips.map((t) => (
            <article key={t.id}>
              <div className="cardvisual">
                <MapPin />
                <span>{t.days_count} DAYS</span>
              </div>
              <div>
                <small>
                  {new Date(t.start_date + "T00:00").toLocaleDateString()}
                </small>
                <h2>{t.city}</h2>
                <p>
                  {t.travelers} · ₹{t.budget.toLocaleString("en-IN")} budget
                </p>
                <footer>
                  <button onClick={() => open(t)}>
                    Open itinerary <ArrowRight />
                  </button>
                  <button onClick={() => remove(t.id)}>
                    <Trash2 />
                  </button>
                </footer>
              </div>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
function Trip({ data, day, setDay, share, back, save, note }) {
  let p = data.itinerary,
    d = p.days[day] || p.days[0],
    total = p.estimated_total || 0;
  function remove(i) {
    let n = structuredClone(data),
      x = n.itinerary.days[day];
    x.stops.splice(i, 1);
    x.spent = x.stops.reduce((a, s) => a + s.cost, 0);
    n.itinerary.estimated_total =
      n.itinerary.days.reduce((a, z) => a + z.spent, 0) +
      n.itinerary.hotel.cost;
    save(n);
    note("Activity removed");
  }
  function regen() {
    let n = structuredClone(data);
    n.itinerary.days[day].stops.reverse();
    n.itinerary.days[day].title = "A fresh perspective";
    save(n);
    note("Day route refreshed");
  }
  return (
    <main className="trip">
      <section className="trip-top">
        <div>
          <button className="back" onClick={back}>
            ← All trips
          </button>
          <div className="titleline">
            <div>
              <span>YOUR {p.city.split(",")[0].toUpperCase()} ESCAPE</span>
              <h1>
                {p.city.split(",")[0]}, <em>your way.</em>
              </h1>
              <p>
                <CalendarDays />{" "}
                {new Date(p.start_date + "T00:00").toLocaleDateString()} ·{" "}
                <Users /> {p.travelers} · <CloudSun /> {d.weather}
              </p>
            </div>
            <div className="actions">
              <button onClick={share}>
                <Share2 />
                Share
              </button>
              <button onClick={() => note("Trip is saved")}>
                <Check />
                Saved
              </button>
              <button className="more" onClick={() => print()}>
                <Download />
              </button>
            </div>
          </div>
        </div>
        <div className="budget">
          <div>
            <span>TRIP BUDGET</span>
            <b>
              ₹{total.toLocaleString("en-IN")}{" "}
              <small>of ₹{p.budget.toLocaleString("en-IN")}</small>
            </b>
          </div>
          <div className="bar">
            <i
              style={{ width: Math.min((total / p.budget) * 100, 100) + "%" }}
            />
          </div>
          <p>
            <strong>
              ₹{Math.max(p.budget - total, 0).toLocaleString("en-IN")}
            </strong>{" "}
            left for little surprises
          </p>
        </div>
      </section>
      <div className="workspace">
        <aside className="days">
          <span>YOUR ITINERARY</span>
          {p.days.map((x, i) => (
            <button
              onClick={() => setDay(i)}
              className={day === i ? "current" : ""}
              key={x.date}
            >
              <b>{String(i + 1).padStart(2, "0")}</b>
              <div>
                <strong>
                  {new Date(x.date + "T00:00").toDateString().toUpperCase()}
                </strong>
                <p>{x.title}</p>
                <small>
                  {x.stops.length} stops · ₹{x.spent.toLocaleString("en-IN")}
                </small>
              </div>
            </button>
          ))}
        </aside>
        <section className="schedule">
          <div className="day-head">
            <div>
              <span>DAY {day + 1}</span>
              <h2>{d.title}</h2>
              <p>{d.subtitle}</p>
            </div>
            <div>
              <span className="weather">
                <Sun /> {d.weather}
              </span>
              <button onClick={regen}>
                <RefreshCw /> Regenerate day
              </button>
            </div>
          </div>
          <div className="timeline">
            {d.stops.map((s, i) => {
              let Icon = icons[s.type] || MapPin;
              return (
                <div className="stop" key={s.name + i}>
                  <div className="time">{s.time}</div>
                  <div className="dot">
                    <Icon />
                  </div>
                  <article>
                    <div className="stopmain">
                      <div>
                        <span>{s.type}</span>
                        <h3>{s.name}</h3>
                        <p>{s.note}</p>
                      </div>
                      <b>
                        {s.cost
                          ? "₹" + s.cost.toLocaleString("en-IN")
                          : "Free"}
                      </b>
                    </div>
                    <footer>
                      <span>↳ {s.travel}</span>
                      <button onClick={() => remove(i)}>
                        <Trash2 />
                      </button>
                    </footer>
                  </article>
                </div>
              );
            })}
          </div>
        </section>
        <aside className="mapcard">
          <ItineraryMap stops={d.stops} />
          <div className="hotel">
            <span>
              <Hotel />
            </span>
            <div>
              <small>YOUR STAY</small>
              <strong>{p.hotel.name}</strong>
              <p>
                {p.hotel.area} · {p.hotel.nights} nights
              </p>
            </div>
            <button onClick={() => note("Booking partner opens here")}>
              View
            </button>
          </div>
          <div className="tip">
            <Sparkles />
            <div>
              <strong>Smart route</strong>
              <p>
                This order saves about <b>{p.route_savings_minutes} minutes</b>{" "}
                of travel.
              </p>
            </div>
          </div>
        </aside>
      </div>
    </main>
  );
}
createRoot(document.getElementById("root")).render(<App />);
