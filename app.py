import streamlit as st
import pandas as pd
import os
from datetime import date

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Church Admin", layout="wide")

# ---------------- DARK UI ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #1f2933, #2c3e50);
    color: white;
}

h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: white !important;
}

input, textarea {
    background-color: #34495e !important;
    color: white !important;
    border-radius: 8px !important;
}

div[data-baseweb="select"] {
    background-color: #34495e !important;
    color: white !important;
}

.stButton>button {
    background-color: #1abc9c;
    color: white;
    border-radius: 10px;
    height: 45px;
}

section[data-testid="stSidebar"] {
    background-color: #1f2a36 !important;
}

table {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- CONFIG ----------------
CHURCHES = ["Sharon Mandhiram", "Abraham raraju Mandhiram", "Karagraharam Mandhiam", "Saradhapetta Mandhiram"]
DATA_FOLDER = "data"

USERS = {
    "pastor": {"admin": "admin123"},
    "member": {"user": "1234"}
}

os.makedirs(DATA_FOLDER, exist_ok=True)

# ---------------- UTIL ----------------
def get_file(church):
    return f"{DATA_FOLDER}/{church}.xlsx"

def load_data(church):
    return pd.read_excel(get_file(church)) if os.path.exists(get_file(church)) else pd.DataFrame()

def save_data(church, data):
    file = get_file(church)
    if os.path.exists(file):
        old = pd.read_excel(file)
        data = pd.concat([old, data], ignore_index=True)
    data.to_excel(file, index=False)

def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------------- LOGIN ----------------
def login():
    st.title("🙏 Church Login")

    role = st.radio("Role", ["Member", "Pastor"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS[role.lower()] and USERS[role.lower()][username] == password:
            st.session_state.role = role.lower()
            st.session_state.page = "main"
            st.rerun()
        else:
            st.error("Invalid credentials")

# ---------------- SIDEBAR ----------------
def sidebar():
    st.sidebar.title("⚙️ Admin Panel")
    return st.sidebar.radio("Navigation", ["Dashboard", "Add Member", "Logout"])

# ---------------- CHURCH SELECT ----------------
def select_church():
    st.title("⛪ Select Church")

    church = st.selectbox("Choose Church", CHURCHES)

    if st.button("Continue"):
        st.session_state.church = church
        st.session_state.page = "form"
        st.rerun()

# ---------------- FORM ----------------
def form():
    st.title("📝 Add Member")

    with st.form("form"):
        name = st.text_input("Name")
        christian_name = st.text_input("Christian Name")
        surname = st.text_input("Surname")

        dob = st.date_input("DOB", min_value=date(1800,1,1), max_value=date(2100,12,31))
        age = calculate_age(dob)
        st.text_input("Age", value=age, disabled=True)

        phone = st.text_input("Phone")
        alt_phone = st.text_input("Alternate Phone")

        baptized = st.selectbox("Baptized", ["Yes", "No"])
        living_status = st.selectbox("Living Status", ["Active", "Inactive"])

        family_no = st.text_input("Family No")

        family_status = st.multiselect(
            "Family Status",
            ["Wife", "Husband", "Mother", "Father", "Son/Daughter"]
        )

        children = st.number_input("No of Children", 0)

        address = st.text_area("Address")
        occupation = st.text_input("Occupation")

        passport = st.file_uploader("Passport Photo")
        family = st.file_uploader("Family Photo")

        submit = st.form_submit_button("Preview")

        if submit:
            st.session_state.data = {
                "Name": name,
                "Christian Name": christian_name,
                "Surname": surname,
                "DOB": str(dob),
                "Age": age,
                "Phone": phone,
                "Alt Phone": alt_phone,
                "Baptized": baptized,
                "Living Status": living_status,
                "Family No": family_no,
                "Family Role": ", ".join(family_status),
                "Children": children,
                "Address": address,
                "Occupation": occupation,
                "Church": st.session_state.church
            }

            st.session_state.images = {"passport": passport, "family": family}
            st.session_state.page = "preview"
            st.rerun()

# ---------------- PREVIEW ----------------
def preview():
    st.title("🔍 Preview")

    data = st.session_state.data

    for k, v in data.items():
        st.write(f"**{k}:** {v}")

    if st.session_state.images["passport"]:
        st.image(st.session_state.images["passport"], width=150)

    if st.session_state.images["family"]:
        st.image(st.session_state.images["family"], width=200)

    if st.button("Save"):
        df = pd.DataFrame([data])
        save_data(data["Church"], df)
        st.success("Saved Successfully ✅")
        st.session_state.page = "main"
        st.rerun()

# ---------------- DASHBOARD ----------------
def dashboard():
    st.title("📊 Dashboard")

    all_data = []

    for church in CHURCHES:
        df = load_data(church)
        if not df.empty:
            df["Church"] = church
            all_data.append(df)

    if not all_data:
        st.warning("No data")
        return

    df = pd.concat(all_data)

    st.subheader("Baptized Analysis")
    st.bar_chart(df.groupby(["Church","Baptized"]).size().unstack().fillna(0))

    st.subheader("Living Status Analysis")
    st.bar_chart(df.groupby(["Church","Living Status"]).size().unstack().fillna(0))

    if st.session_state.role == "pastor":
        st.dataframe(df)

        st.download_button(
            "Download Data",
            df.to_csv(index=False),
            file_name="church_data.csv"
        )

# ---------------- MAIN ----------------
def main():
    page = sidebar()

    if page == "Dashboard":
        if st.session_state.role == "pastor":
            dashboard()
        else:
            st.warning("Access Denied")

    elif page == "Add Member":
        st.session_state.page = "select_church"
        st.rerun()

    elif page == "Logout":
        # 🔥 CLEAR SESSION COMPLETELY
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.session_state.page = "login"
        st.rerun()

# ---------------- ROUTER ----------------
if st.session_state.page == "login":
    login()

elif st.session_state.page == "main":
    main()

elif st.session_state.page == "select_church":
    select_church()

elif st.session_state.page == "form":
    form()

elif st.session_state.page == "preview":
    preview()
