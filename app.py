import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from pathlib import Path
from datetime import datetime, date
import json
import uuid
import io
import threading
import hashlib
import hmac
import secrets
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
STUDENTS_DIR = DATA_DIR / "students"
ATTENDANCE_DIR = DATA_DIR / "attendance"
STUDENTS_FILE = DATA_DIR / "students.json"
ADMINS_FILE = DATA_DIR / "admins.json"

for folder in (DATA_DIR, STUDENTS_DIR, ATTENDANCE_DIR):
    folder.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="AttendAI | Smart Attendance", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# ---------- Styling ----------
# ---------- Premium AttendAI Styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #080d1b;
    --panel: #111a2e;
    --panel2: #17223b;
    --blue: #60a5fa;
    --purple: #a78bfa;
    --text: #f1f5f9;
    --muted: #94a3b8;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 15% 0%, #182c50 0%, transparent 38%),
        radial-gradient(ellipse at 90% 10%, #24184b 0%, transparent 30%),
        var(--bg);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: rgba(8, 13, 27, 0.7);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101a30, #0b1120);
    border-right: 1px solid rgba(148,163,184,0.15);
}

[data-testid="stSidebar"] * {
    color: #e2e8f0;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 8px 10px;
    border-radius: 10px;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 36px;
    border-radius: 24px;
    border: 1px solid rgba(147,197,253,0.25);
    background: linear-gradient(120deg,
        rgba(37,99,235,0.23),
        rgba(124,58,237,0.20),
        rgba(17,26,46,0.95));
    box-shadow: 0 18px 55px rgba(0,0,0,0.22);
    margin-bottom: 28px;
}

.hero h1 {
    font-size: 42px;
    font-weight: 800;
    letter-spacing: -1.5px;
    margin: 10px 0;
    color: #ffffff;
}

.hero p {
    font-size: 15px;
    color: #cbd5e1;
    margin-bottom: 0;
}

.hero-badge {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 30px;
    color: #bfdbfe;
    background: rgba(59,130,246,0.15);
    border: 1px solid rgba(96,165,250,0.35);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #15213a, #10182b);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(148,163,184,0.18);
    box-shadow: 0 12px 30px rgba(0,0,0,0.12);
}

div[data-testid="stMetric"] label {
    color: #94a3b8 !important;
    font-size: 13px !important;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 30px;
    font-weight: 800;
}

h1, h2, h3 {
    color: #f8fafc !important;
    letter-spacing: -0.5px;
}

p, label, .stMarkdown {
    color: #cbd5e1;
}

hr {
    border-color: rgba(148,163,184,0.15);
}

.stButton > button,
.stDownloadButton > button {
    background: linear-gradient(100deg, #2563eb, #7c3aed);
    color: white !important;
    border: none;
    border-radius: 11px;
    padding: 10px 18px;
    font-weight: 700;
    transition: all 0.2s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(99,102,241,0.3);
    border: none;
}

input, textarea {
    background-color: #111a2e !important;
    color: white !important;
    border-radius: 10px !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid rgba(148,163,184,0.18);
    border-radius: 14px;
    overflow: hidden;
}

[data-testid="stFileUploader"] {
    background: rgba(17,26,46,0.75);
    border: 1px dashed rgba(96,165,250,0.4);
    border-radius: 14px;
    padding: 12px;
}

.small-note {
    color: #64748b;
    font-size: 12px;
    text-align: center;
}

.section-label {
    color: #93c5fd;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
}

@media (max-width: 768px) {
    .hero {
        padding: 24px;
    }
    .hero h1 {
        font-size: 32px;
    }
}

/* Premium dashboard additions */
.brand-line {display:flex;align-items:center;gap:12px;margin-bottom:8px;}
.kicker {font-size:11px;letter-spacing:2.2px;font-weight:800;color:#93c5fd;text-transform:uppercase;}
.panel-card {background:linear-gradient(145deg,rgba(20,32,55,.96),rgba(12,20,37,.96));border:1px solid rgba(148,163,184,.16);border-radius:18px;padding:20px 22px;min-height:118px;box-shadow:0 12px 35px rgba(0,0,0,.12);}
.panel-card .label {font-size:12px;color:#94a3b8;font-weight:700;letter-spacing:.7px;text-transform:uppercase;}
.panel-card .value {font-size:28px;color:#f8fafc;font-weight:800;margin-top:8px;}
.panel-card .hint {font-size:12px;color:#94a3b8;margin-top:4px;}
.status-pill {display:inline-block;padding:5px 10px;border-radius:20px;font-size:11px;font-weight:800;background:rgba(96,165,250,.12);color:#93c5fd;border:1px solid rgba(96,165,250,.25);}
[data-testid="stForm"] {background:rgba(17,26,46,.55);border:1px solid rgba(148,163,184,.15);padding:20px;border-radius:18px;}
[data-testid="stSelectbox"], [data-testid="stDateInput"], [data-testid="stTextInput"] {border-radius:12px;}
[data-testid="stAlert"] {border-radius:14px;}
div[data-testid="stVerticalBlock"] > div:has(> .hero) {gap:0.5rem;}

</style>
""", unsafe_allow_html=True)
# ---------- Data helpers ----------
def load_students():
    if STUDENTS_FILE.exists():
        try:
            return json.loads(STUDENTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def save_students(students):
    STUDENTS_FILE.write_text(json.dumps(students, indent=2), encoding="utf-8")

# ---------- Admin authentication ----------
def load_admins():
    if ADMINS_FILE.exists():
        try:
            data = json.loads(ADMINS_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []
    return []

def save_admins(admins):
    ADMINS_FILE.write_text(json.dumps(admins, indent=2), encoding="utf-8")

def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000).hex()
    return {"salt": salt, "password_hash": digest}

def verify_password(password, admin):
    try:
        actual = hash_password(password, admin["salt"])["password_hash"]
        return hmac.compare_digest(actual, admin["password_hash"])
    except (KeyError, TypeError):
        return False

def attendance_file(session_date, class_name, subject):
    safe_class = "".join(c if c.isalnum() or c in "-_" else "_" for c in class_name)
    safe_subject = "".join(c if c.isalnum() or c in "-_" else "_" for c in subject)
    return ATTENDANCE_DIR / f"{session_date}_{safe_class}_{safe_subject}.csv"

def pil_to_bgr(pil_img):
    return cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2BGR)

def detector():
    if not hasattr(cv2, "CascadeClassifier"):
        raise RuntimeError(
            "This OpenCV build does not provide CascadeClassifier. "
            "Activate the project .venv and install opencv-python==4.11.0.86."
        )
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    model = cv2.CascadeClassifier(cascade_path)
    if model.empty():
        raise RuntimeError("OpenCV face detector could not be loaded.")
    return model

def detect_faces(pil_img):
    image = pil_to_bgr(pil_img)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = detector().detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(45, 45))
    return image, gray, list(faces)

def crop_signature(gray, box):
    x, y, w, h = [int(v) for v in box]
    crop = gray[max(0,y):y+h, max(0,x):x+w]
    if crop.size == 0:
        return None
    # Lightweight appearance signature for a hackathon demo, NOT a robust biometric embedding.
    crop = cv2.resize(crop, (64, 64), interpolation=cv2.INTER_AREA)
    crop = cv2.equalizeHist(crop)
    vector = crop.astype(np.float32).flatten()
    norm = np.linalg.norm(vector)
    return vector / norm if norm else vector

def compare_signatures(a, b):
    if a is None or b is None:
        return 0.0
    # cosine similarity of normalized grayscale appearance signatures
    return float(np.dot(a, b) / ((np.linalg.norm(a) * np.linalg.norm(b)) + 1e-8))

def read_signature(path):
    image = cv2.imread(str(path))
    if image is None:
        return None
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    # Stored registration crops are face-only images.
    crop = cv2.resize(gray, (64, 64), interpolation=cv2.INTER_AREA)
    vec = crop.astype(np.float32).flatten()
    norm = np.linalg.norm(vec)
    return vec / norm if norm else vec

class LiveAttendanceProcessor(VideoProcessorBase):
    """Live webcam face detector and lightweight appearance matcher for demo use."""
    def __init__(self, students_for_class, session_date, class_name, subject):
        self.students = students_for_class
        self.session_date = session_date
        self.class_name = class_name
        self.subject = subject
        self.lock = threading.Lock()
        self.seen = {}
        self.streaks = {}
        self.auto_marked = set()
        self.face_model = detector()
        self.references = []
        for student in students_for_class:
            sig = read_signature(STUDENTS_DIR / student["face_file"])
            if sig is not None:
                self.references.append((student, sig))

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        boxes = self.face_model.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        for box in boxes:
            x, y, w, h = [int(v) for v in box]
            signature = crop_signature(gray, box)
            ranked = [(compare_signatures(signature, ref), student) for student, ref in self.references]
            ranked.sort(key=lambda item: item[0], reverse=True)
            score, student = ranked[0] if ranked else (0.0, None)
            # Conservative threshold; this simple image signature is not reliable identity verification.
            matched = student is not None and score >= 0.82
            if matched:
                sid = student["student_id"]
                with self.lock:
                    self.streaks[sid] = self.streaks.get(sid, 0) + 1
                    self.seen[sid] = {
                        "student_id": sid,
                        "name": student["name"],
                        "class_name": student.get("class_name", "MCA-A"),
                        "similarity_score": round(float(score), 3),
                        "first_seen": self.seen.get(sid, {}).get("first_seen", datetime.now().strftime("%H:%M:%S")),
                        "status": "Present" if sid in self.auto_marked else "Matching..."
                    }
                    # Auto-mark after a candidate appears consistently across several frames.
                    # This is a hackathon demo, not reliable identity verification.
                    if self.streaks[sid] >= 3 and sid not in self.auto_marked:
                        row = {
                            "student_id": sid, "name": student["name"],
                            "class_name": self.class_name, "subject": self.subject,
                            "date": self.session_date, "status": "Present",
                            "match_status": "Auto-marked from stable live-camera candidate; verify identity",
                            "similarity_score": round(float(score), 3),
                            "review_required": True, "confirmed": False,
                            "first_seen": self.seen[sid]["first_seen"]
                        }
                        try:
                            mark_attendance([row], self.session_date, self.class_name, self.subject)
                            self.auto_marked.add(sid)
                            self.seen[sid]["status"] = "Present (auto-marked; verify)"
                        except Exception as save_error:
                            print(f"[AttendAI] ATTENDANCE SAVE ERROR: {save_error}")
                            self.seen[sid]["status"] = "Save failed - check terminal"
                label_status = "PRESENT*" if student["student_id"] in self.auto_marked else "MATCHING..."
                label = f"{student['name']} - {label_status}"
                color = (40, 180, 100)
            else:
                label = "Unknown / review"
                color = (20, 90, 230)
            cv2.rectangle(image, (x, y), (x+w, y+h), color, 2)
            cv2.putText(image, label[:34], (x, max(22, y-8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2, cv2.LINE_AA)
        return __import__('av').VideoFrame.from_ndarray(image, format="bgr24")

def all_students():
    return load_students()

def mark_attendance(rows, session_date, class_name, subject):
    """Persist attendance to the app-local data/attendance folder."""
    ATTENDANCE_DIR.mkdir(parents=True, exist_ok=True)
    path = attendance_file(session_date, class_name, subject)
    df_new = pd.DataFrame(rows)

    if df_new.empty:
        raise ValueError("No attendance rows were supplied.")

    if path.exists():
        old = pd.read_csv(path)
        combined = pd.concat([old, df_new], ignore_index=True)
        if "student_id" in combined.columns:
            combined = combined.drop_duplicates(subset=["student_id"], keep="last")
        combined.to_csv(path, index=False)
    else:
        df_new.to_csv(path, index=False)

    print(f"[AttendAI] Attendance CSV saved: {path.resolve()}")
    return path

# ---------- Admin Login / First-time Registration ----------
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "admin_username" not in st.session_state:
    st.session_state.admin_username = ""

admins = load_admins()
if not st.session_state.admin_logged_in:
    st.markdown("""
    <div style="max-width:900px;margin:3vh auto 1rem;text-align:center;">
      <div style="font-size:54px;">🎓</div>
      <div style="font-size:42px;font-weight:850;color:#f8fafc;">Attend<span style="color:#60a5fa;">AI</span></div>
      <div style="color:#94a3b8;letter-spacing:2px;font-size:12px;font-weight:700;">SMART ATTENDANCE • ADMIN PORTAL</div>
    </div>
    """, unsafe_allow_html=True)
    left, center, right = st.columns([1, 1.15, 1])
    with center:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        if not admins:
            st.info("First-time setup: create the first administrator account to secure this workspace.")
            tab_login, tab_register = st.tabs(["🔐 Admin Login", "✨ Create Admin"])
        else:
            tab_login = st.container()
            tab_register = None

        with tab_login:
            st.subheader("Welcome back")
            with st.form("admin_login_form"):
                login_username = st.text_input("Admin username", placeholder="Enter your username").strip()
                login_password = st.text_input("Password", type="password", placeholder="Enter your password")
                login_submit = st.form_submit_button("Sign in to dashboard", use_container_width=True, type="primary")
            if login_submit:
                matched = next((a for a in admins if a.get("username", "").casefold() == login_username.casefold()), None)
                if matched and verify_password(login_password, matched):
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_username = matched["username"]
                    st.rerun()
                else:
                    st.error("Username or password is incorrect.")

        if tab_register is not None:
            with tab_register:
                st.subheader("Create administrator")
                with st.form("admin_register_form"):
                    new_username = st.text_input("Choose username", placeholder="e.g. attendai_admin").strip()
                    new_password = st.text_input("Create password", type="password", help="Use at least 8 characters.")
                    confirm_password = st.text_input("Confirm password", type="password")
                    register_submit = st.form_submit_button("Create admin account", use_container_width=True, type="primary")
                if register_submit:
                    if len(new_username) < 3:
                        st.error("Username must contain at least 3 characters.")
                    elif len(new_password) < 8:
                        st.error("Password must contain at least 8 characters.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif any(a.get("username", "").casefold() == new_username.casefold() for a in load_admins()):
                        st.error("That username already exists.")
                    elif load_admins():
                        st.error("Initial setup is already complete. Ask an existing administrator to manage accounts.")
                    else:
                        credentials = hash_password(new_password)
                        save_admins([{"username": new_username, **credentials, "created_at": datetime.now().isoformat(timespec="seconds")}])
                        st.success("Admin account created. You can now sign in from the Admin Login tab.")
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<p class="small-note">Authorized staff only • Passwords are stored as salted hashes, not plain text.</p>', unsafe_allow_html=True)
    st.stop()

# ---------- Sidebar ----------
# ---------- Premium Sidebar ----------
st.sidebar.markdown("""
<div style="padding:18px 8px 24px;">
    <div style="font-size:36px;">🎓</div>
    <div style="font-size:25px;font-weight:800;color:white;">
        Attend<span style="color:#60a5fa;">AI</span>
    </div>
    <div style="font-size:11px;letter-spacing:2px;color:#94a3b8;">
        SMART ATTENDANCE SYSTEM
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(
    '<p style="color:#60a5fa;font-size:11px;'
    'font-weight:800;letter-spacing:2px;">WORKSPACE</p>',
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Register Students",
        "Take Attendance",
        "Attendance Reports"
    ],
    format_func=lambda p: {
        "Dashboard": "📊  Dashboard",
        "Register Students": "👨‍🎓  Students",
        "Take Attendance": "📷  Live Attendance",
        "Attendance Reports": "📁  Reports"
    }[p]
)

st.sidebar.divider()

st.sidebar.markdown("""
<div style="background:rgba(59,130,246,0.09);
            border:1px solid rgba(96,165,250,0.20);
            border-radius:14px;padding:15px;">
    <div style="font-size:13px;font-weight:700;color:white;">
        🚀 AttendAI MVP
    </div>
    <div style="font-size:12px;color:#94a3b8;margin-top:7px;">
        AI-assisted attendance<br>
        Local demo environment
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.caption("Prototype • Teacher review required")
st.sidebar.markdown(f"**👤 Admin:** `{st.session_state.admin_username}`")
if st.sidebar.button("🚪 Log out", use_container_width=True):
    st.session_state.admin_logged_in = False
    st.session_state.admin_username = ""
    st.rerun()
students = all_students()

# ---------- Premium Main Header ----------
st.markdown("""
<div class="hero">
    <div class="hero-badge">✦ AI-ASSISTED CLASSROOM TECHNOLOGY</div>
    <h1>Attendance, reimagined.</h1>
    <p>A smarter classroom workspace for live face detection, attendance analytics and digital reporting.</p>
    <br>
    <div style="color:#93c5fd;font-size:12px;font-weight:800;letter-spacing:.8px;">
        ● LIVE CAMERA &nbsp;&nbsp; • &nbsp;&nbsp; STUDENT REGISTRY &nbsp;&nbsp; • &nbsp;&nbsp; DIGITAL REPORTS
    </div>
</div>
""", unsafe_allow_html=True)

# OpenCV compatibility diagnostic: the app stays open and explains the fix.
if not hasattr(cv2, "CascadeClassifier"):
    st.error(
        "OpenCV installation issue: `cv2.CascadeClassifier` is unavailable. "
        "In the project terminal, activate your `.venv`, then run: "
        "`python -m pip uninstall opencv-python opencv-contrib-python "
        "opencv-python-headless opencv-contrib-python-headless -y` followed by "
        "`python -m pip install opencv-python==4.11.0.86`. "
        "Restart Streamlit after installation."
    )

if page == "Dashboard":
    today = date.today().isoformat()
    all_records = []
    for file in ATTENDANCE_DIR.glob("*.csv"):
        try:
            all_records.append(pd.read_csv(file))
        except Exception as e:
            st.warning(f"Could not read {file.name}: {e}")

    all_df = pd.concat(all_records, ignore_index=True) if all_records else pd.DataFrame()
    today_df = (
        all_df[all_df["date"].astype(str) == today]
        if not all_df.empty and "date" in all_df.columns
        else pd.DataFrame()
    )
    present_today = int((today_df["status"] == "Present").sum()) if not today_df.empty and "status" in today_df.columns else 0
    review_today = int((today_df["review_required"].astype(str).str.lower().isin(["true", "1"])).sum()) if not today_df.empty and "review_required" in today_df.columns else 0
    sessions = len(list(ATTENDANCE_DIR.glob("*.csv")))

    st.markdown('<div class="kicker">Overview / Today at a glance</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registered Students", len(students), help="Students in the local registry")
    c2.metric("Present Today", present_today, help="Saved records dated today")
    c3.metric("Saved Sessions", sessions, help="CSV attendance reports")
    c4.metric("Needs Review", review_today, help="Auto-marked records requiring teacher verification")

    st.write("")
    left, right = st.columns([1.25, 1])
    with left:
        st.markdown("### 📈 Attendance activity")
        if not today_df.empty and "status" in today_df.columns:
            status_counts = today_df["status"].value_counts()
            st.bar_chart(status_counts, use_container_width=True)
        else:
            st.info("Your attendance chart will appear here after the first session is saved.")
    with right:
        st.markdown("### ⚡ Quick actions")
        st.markdown("""
        <div class="panel-card">
            <div class="label">Your workspace</div>
            <div class="value">Ready to start</div>
            <div class="hint">Register students, start the camera, then review and export the report.</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.markdown('<span class="status-pill">TEACHER REVIEW ENABLED</span>', unsafe_allow_html=True)
        st.caption("Camera matching is a demo candidate match, not reliable identity verification.")

    st.markdown("### 🧾 Recent attendance records")
    if all_df.empty:
        st.info("No attendance saved yet. Register demo students, then open Live Attendance.")
    else:
        st.dataframe(all_df.tail(15), use_container_width=True, hide_index=True)

    with st.expander("How AttendAI works", expanded=False):
        st.markdown(
            "1. Register consenting students with a clear, front-facing photo.  \\n"
            "2. Open **Live Attendance** and allow webcam access.  \\n"
            "3. The prototype detects a face and compares a lightweight appearance signature.  \\n"
            "4. Review the suggested records and export the CSV report."
        )
    st.caption("Privacy & accuracy: this hackathon prototype can misidentify people. Obtain consent and verify all records before using them.")

elif page == "Register Students":
    st.markdown('<div class="kicker">People / Student registry</div>', unsafe_allow_html=True)
    st.title("👨‍🎓 Student Registry")
    st.caption("Create a local demo profile for each consenting student.")
    st.write("Use a clear, front-facing photo with one visible face. Use consenting volunteers or mock data for your demo.")
    with st.form("register_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Student name")
            student_id = st.text_input("Student ID / Roll number")
            class_name = st.text_input("Class / Section", value="MCA-A")
        with col2:
            photo = st.file_uploader("Student face photo", type=["jpg", "jpeg", "png"], key="student_photo")
            st.caption("Photo stays in this local project folder.")
        submitted = st.form_submit_button("Register Student", type="primary")
        if submitted:
            if not name.strip() or not student_id.strip() or photo is None:
                st.error("Enter name, student ID and upload a photo.")
            elif any(s["student_id"].lower() == student_id.strip().lower() for s in students):
                st.error("That student ID is already registered.")
            else:
                try:
                    pil = Image.open(photo).convert("RGB")
                    _, gray, faces = detect_faces(pil)
                    if len(faces) == 0:
                        st.error("No face detected. Try a clearer, front-facing image with better lighting.")
                    else:
                        # Choose the largest detected face for registration.
                        box = max(faces, key=lambda b: int(b[2]) * int(b[3]))
                        x, y, w, h = [int(v) for v in box]
                        crop = gray[y:y+h, x:x+w]
                        if crop.size == 0:
                            st.error("Could not crop the face. Try another image.")
                        else:
                            filename = f"{uuid.uuid4().hex}.png"
                            cv2.imwrite(str(STUDENTS_DIR / filename), crop)
                            new_student = {
                                "student_id": student_id.strip(),
                                "name": name.strip(),
                                "class_name": class_name.strip() or "MCA-A",
                                "face_file": filename,
                                "registered_at": datetime.now().isoformat(timespec="seconds")
                            }
                            students.append(new_student)
                            save_students(students)
                            st.success(f"Registered {name.strip()} ({student_id.strip()}).")
                            st.image(pil, caption="Uploaded registration photo", width=260)
                except Exception as e:
                    st.error(f"Could not process image: {e}")
    st.markdown(f"### Registered students <span class=\"status-pill\">{len(students)} TOTAL</span>", unsafe_allow_html=True)
    if students:
        st.dataframe(pd.DataFrame([{k: s.get(k) for k in ["student_id", "name", "class_name", "registered_at"]} for s in students]),
                     use_container_width=True, hide_index=True)
        if st.button("Clear all registered students", type="secondary"):
            for s in students:
                try:
                    (STUDENTS_DIR / s["face_file"]).unlink(missing_ok=True)
                except Exception:
                    pass
            save_students([])
            st.success("Student registry cleared. Refresh the page if needed.")
            st.rerun()

elif page == "Take Attendance":
    st.markdown('<div class="kicker">Session / Live detection</div>', unsafe_allow_html=True)
    st.title("📷 Live Attendance")
    st.info("Start the webcam and let registered students face the camera one at a time. A stable candidate match is automatically written to today's attendance CSV; verify the results because this demo can misidentify people.")
    col1, col2, col3 = st.columns(3)
    with col1:
        class_name = st.text_input("Class / Section", value="MCA-A")
    with col2:
        subject = st.text_input("Subject", value="Computer Vision")
    with col3:
        session_date = st.date_input("Session date", value=date.today()).isoformat()

    students_for_class = [s for s in students if s.get("class_name", "").lower() == class_name.strip().lower()]
    if not students_for_class:
        st.warning("No students registered for this class. Register students first and use the same class name.")
    else:
        st.caption(f"{len(students_for_class)} registered students in {class_name}. For webcam access, open this app on the same computer using http://localhost:8501 or use HTTPS.")
        ctx = webrtc_streamer(
            key=f"attendai-live-camera-{session_date}-{class_name}-{subject}",
            video_processor_factory=lambda: LiveAttendanceProcessor(students_for_class, session_date, class_name, subject),
            media_stream_constraints={"video": True, "audio": False},
            rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
            async_processing=True,
        )
        processor = ctx.video_processor
        seen_records = []
        if processor is not None:
            with processor.lock:
                seen_records = list(processor.seen.values())
        st.markdown("### 🟢 Live detection results")
        st.caption("Green boxes mean a candidate match; red/orange boxes mean unknown/uncertain. Stable matches are auto-marked as Present and flagged for teacher review.")
        st.caption(f"Attendance save folder: {ATTENDANCE_DIR}")
        if seen_records:
            seen_df = pd.DataFrame(seen_records).sort_values("first_seen")
            st.success(f"{len(seen_records)} registered student(s) detected in front of the camera.")
            st.dataframe(seen_df, use_container_width=True, hide_index=True)
            st.warning("Attendance is saved automatically after a stable match, but it is flagged for teacher review. Check names before treating records as final.")
            path = attendance_file(session_date, class_name, subject)
            if path.exists():
                st.success(f"Attendance file updated automatically: {path.name}")
                st.download_button("Download current attendance CSV", data=path.read_bytes(), file_name=path.name, mime="text/csv")
        else:
            st.info("No registered student candidate detected yet. Start the camera and face it with good lighting.")
        if st.button("Clear live detections") and processor is not None:
            with processor.lock:
                processor.seen.clear()
                processor.streaks.clear()
            st.rerun()

elif page == "Attendance Reports":
    st.markdown('<div class="kicker">Records / Export center</div>', unsafe_allow_html=True)
    st.title("📁 Attendance Reports")
    files = sorted(ATTENDANCE_DIR.glob("*.csv"), reverse=True)
    if not files:
        st.info("No saved reports yet. Start live attendance and wait for a stable student match.")
    else:
        chosen = st.selectbox("Select session report", files, format_func=lambda p: p.name)
        df = pd.read_csv(chosen)
        present = int((df["status"] == "Present").sum()) if "status" in df else 0
        review_count = int(df["review_required"].astype(str).str.lower().isin(["true", "1"]).sum()) if "review_required" in df else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Records", len(df))
        c2.metric("Present", present)
        c3.metric("Review Required", review_count)
        if "status" in df.columns:
            st.markdown("### Session breakdown")
            st.bar_chart(df["status"].value_counts(), use_container_width=True)
        st.markdown("### Full report")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download CSV report", data=chosen.read_bytes(), file_name=chosen.name, mime="text/csv", type="primary")

st.divider()
st.markdown('<p class="small-note">AttendAI hackathon prototype • Face recognition can be inaccurate. Always review results and follow consent, privacy and institutional policies.</p>', unsafe_allow_html=True)
