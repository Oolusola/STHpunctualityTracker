import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo  # For timezone handling
from geopy.distance import geodesic
import gspread
from google.oauth2.service_account import Credentials
import time

st.set_page_config(page_title="Attendance Logger", layout="centered")
st.title("📋 Daily Attendance Tracker")

# Full facility data provided by the user
facility_data = [
    {"Facility": "State office", "Landmark": "KadunaNorth", "Latitude": 10.51509, "Longitude": 7.43844, "Postal code": "800283"},
    {"Facility": "Jibrin Maigwari General Hospital", "Landmark": "BirninGwari", "Latitude": 10.65826, "Longitude": 6.53479, "Postal code": "800119"},
    {"Facility": "Amina Hospital", "Landmark": "Chikun", "Latitude": 10.4554067, "Longitude": 7.4258814, "Postal code": "800282"},
    {"Facility": "Sabon Tasha General Hospital", "Landmark": "Chikun", "Latitude": 10.4489626, "Longitude": 7.478136, "Postal code": "800104"},
    {"Facility": "Kaduna CSCC", "Landmark": "Chikun", "Latitude": 10.5036, "Longitude": 7.4337, "Postal code": "800283"},
]

# --- Inputs ---
name = st.text_input("👤 Enter your name")
facility_names = [f["Facility"] for f in facility_data]
selected_facility_name = st.selectbox("🏥 Select your facility", facility_names)

col1, col2 = st.columns(2)
with col1:
    designation_options = [
        "I3TR", "TSP", "EDEC", "M&E Officer", "Case Manager", "Adhernce Nurse", "Data Clerck", "Focal Person"
    ]
    designation = st.selectbox("👨‍💼 Select your designation", designation_options)

with col2:
    today = datetime.now(ZoneInfo("Africa/Lagos")).date()
    min_date = datetime(2025, 1, 1).date()
    selected_date = st.date_input("🗕️ Select today's date", today, min_value=min_date, max_value=today)

# --- Manual Fallback ---
with st.expander("📍 Get My Location Manually"):
    st.markdown("""
    If automatic GPS is slow or blocked, click below to open an external site, copy your location, and paste it here.
    """)
    gps_url = "https://gps-coordinates.org/my-location.php"
    st.markdown(f"[🌐 Open GPS Website]({gps_url})", unsafe_allow_html=True)

    col_lat, col_lon = st.columns(2)
    with col_lat:
        manual_lat = st.text_input("📉 Latitude (from website)", "")
    with col_lon:
        manual_lon = st.text_input("📉 Longitude (from website)", "")

    if manual_lat and manual_lon:
        st.success(f"📍 Manual Location Set: Latitude {manual_lat}, Longitude {manual_lon}")

# --- Location Button ---
get_location_auto = st.button("📍 Get My Location Automatically")
if get_location_auto:
    st.info("_GPS is taking time to load... pls, explore the Get My Location manually option._")

# --- Camera Input Logic ---
if "camera_started" not in st.session_state:
    st.session_state.camera_started = False
if "photo_taken" not in st.session_state:
    st.session_state.photo_taken = False
if "photo_preview" not in st.session_state:
    st.session_state.photo_preview = None
if "show_preview" not in st.session_state:
    st.session_state.show_preview = False

if st.button("📸 Take a photo for verification"):
    st.session_state.camera_started = True
    st.session_state.photo_taken = False
    st.session_state.show_preview = False

if st.session_state.camera_started and not st.session_state.photo_taken:
    photo = st.camera_input("📸 Please take your selfie")
    if photo:
        st.session_state.photo_taken = True
        st.session_state.camera_started = False
        st.session_state.photo_preview = photo
        st.success("✅ Your selfie has been taken and submitted for verification.")
        st.session_state.show_preview = True
        time.sleep(2)
        st.session_state.show_preview = False

if st.session_state.show_preview:
    st.image(st.session_state.photo_preview, caption="Your submitted selfie", use_container_width=True)

# --- Submit to Google Sheet ---
submit_to_sheet = st.button("✅ Submit Attendance to Google Sheet")

if submit_to_sheet:
    lat, lon, timestamp = None, None, None
    valid_coords = True
    if manual_lat and manual_lon:
        try:
            lat_val = float(manual_lat)
            lon_val = float(manual_lon)
            if not (-90 <= lat_val <= 90 and -180 <= lon_val <= 180):
                valid_coords = False
            else:
                lat = lat_val
                lon = lon_val
                timestamp = datetime.now(ZoneInfo("Africa/Lagos")).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            valid_coords = False
        if not valid_coords:
            st.error("❌ Wrong input, please input correct coordinates of your location.")
    else:
        st.error("❌ No location data to submit.")

    if valid_coords and lat is not None and lon is not None and timestamp is not None:
        selected_facility = next((f for f in facility_data if f["Facility"] == selected_facility_name), None)
        if selected_facility:
            facility_coord = (selected_facility["Latitude"], selected_facility["Longitude"])
            user_coord = (lat, lon)
            distance_km = geodesic(facility_coord, user_coord).km
            punctuality_status = "not in the facility" if distance_km > 0.5 else "arrived at the facility"

            try:
                time_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").time()
                punctuality_outcome = "You came on time" if (time_obj.hour < 8 or (time_obj.hour == 8 and time_obj.minute <= 45)) else "You are late"
            except Exception:
                punctuality_outcome = "Invalid timestamp"

            row = [
                selected_facility["Facility"],
                selected_facility["Landmark"],
                selected_facility["Postal code"],
                name,
                str(selected_date),
                designation,
                timestamp,
                lat,
                lon,
                punctuality_status,
                round(distance_km, 7),
                punctuality_outcome
            ]
            try:
                scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                service_account_info = dict(st.secrets["google_service_account"])
                creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
                client = gspread.authorize(creds)
                sheet = client.open("Attendant tracker")
                worksheet = sheet.sheet1
                header = ["Facility Name", "Landmark", "Postal Code", "Name", "Date", "Designation", "Timestamp", "Latitude", "Longitude", "Punctuality Check", "Distance", "Punctuality Outcome"]
                if worksheet.row_values(1) != header:
                    worksheet.insert_row(header, 1)
                worksheet.append_row(row)
                st.success("✅ Attendance submitted to Google Sheet!")
            except Exception as e:
                error_message = str(e)
                if (
                    'Failed to resolve' in error_message or
                    'NameResolutionError' in error_message or
                    'getaddrinfo failed' in error_message or
                    'Max retries exceeded with url' in error_message
                ):
                    st.error("❌ You don't have network connection, please connect to a stronger network and try again.")
                else:
                    st.error(f"❌ Failed to submit to Google Sheet: {e}")
        else:
            st.error("❌ Facility not found for submission.")
