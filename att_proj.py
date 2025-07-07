import streamlit as st
from datetime import datetime
from geopy.distance import geodesic
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Attendance Logger", layout="centered")
st.title("📋 STH Facility Attendant Form")

# Full facility data provided by the user
facility_data = [
    {"Facility": "State office", "Landmark": "KadunaNorth", "Latitude": 10.51509, "Longitude": 7.43844, "Postal code": "800283"},
    {"Facility": "Jibrin Maigwari General Hospital", "Landmark": "BirninGwari", "Latitude": 10.65826, "Longitude": 6.53479, "Postal code": "800119"},
    {"Facility": "Amina Hospital", "Landmark": "Chikun", "Latitude": 10.4554067, "Longitude": 7.4258814, "Postal code": "800282"},
    {"Facility": "Sabon Tasha General Hospital", "Landmark": "Chikun", "Latitude": 10.4489626, "Longitude": 7.478136, "Postal code": "800104"},
    {"Facility": "Sabo Tsaha Primary Health Center", "Landmark": "Chikun", "Latitude": 10.4564222, "Longitude": 7.4538917, "Postal code": "800104"},
    {"Facility": "Kujama Rural Hospital", "Landmark": "Chikun", "Latitude": 10.4061661, "Longitude": 7.704165, "Postal code": "802130"},
    {"Facility": "Ahmadu Bello University Teaching Hospital Shika Zaria", "Landmark": "Giwa", "Latitude": 11.0748561, "Longitude": 7.6826276, "Postal code": "810282"},
    {"Facility": "General Hospital Giwa", "Landmark": "Giwa", "Latitude": 11.2482513, "Longitude": 7.4768502, "Postal code": "810105"},
    {"Facility": "Jaji Comprehensive Health Center", "Landmark": "Igabi", "Latitude": 10.8236673, "Longitude": 7.5701068, "Postal code": "800102"},
    {"Facility": "Rigasa General Hospital", "Landmark": "Igabi", "Latitude": 10.54579, "Longitude": 7.35651, "Postal code": "800103"},
    {"Facility": "Turunku Rural Hospital", "Landmark": "Igabi", "Latitude": 10.8035916, "Longitude": 7.7101077, "Postal code": "800101"},
    {"Facility": "Ikara General Hospital", "Landmark": "Igabi", "Latitude": 11.1547035, "Longitude": 8.2316977, "Postal code": "801126"},
    {"Facility": "Kwoi General Hospital", "Landmark": "Jaba", "Latitude": 9.4604752, "Longitude": 7.9955248, "Postal code": "801106"},
    {"Facility": "Kafanchan Family Health Unit", "Landmark": "Jema'a", "Latitude": 9.5831722, "Longitude": 8.2915233, "Postal code": "801116"},
    {"Facility": "Kafanchan General Hospital", "Landmark": "Jema'a", "Latitude": 9.5831722, "Longitude": 8.2915233, "Postal code": "801116"},
    {"Facility": "Foltz Medical Center - Katari", "Landmark": "Kachia", "Latitude": 9.6964232, "Longitude": 7.4534875, "Postal code": "802157"},
    {"Facility": "Kachia General Hospital", "Landmark": "Kachia", "Latitude": 9.8601862, "Longitude": 7.96255, "Postal code": "802101"},
    {"Facility": "Doka Rural Hospital", "Landmark": "Kachia", "Latitude": 9.9227924, "Longitude": 7.4312123, "Postal code": "802118"},
    {"Facility": "Badarawa Primary Health Center", "Landmark": "KadunaNorth", "Latitude": 10.5592211, "Longitude": 7.4477926, "Postal code": "800213"},
    {"Facility": "Barau Dikko Specialist Hospital", "Landmark": "KadunaNorth", "Latitude": 10.5253783, "Longitude": 7.4420041, "Postal code": "802125"},
    {"Facility": "Federation of Muslim Women Association of Nigeria (FOMWAN) Hospital", "Landmark": "KadunaNorth", "Latitude": 10.5576883, "Longitude": 7.4521891, "Postal code": "800283"},
    {"Facility": "Kawo General Hospital", "Landmark": "KadunaNorth", "Latitude": 10.5829333, "Longitude": 7.4463913, "Postal code": "800283"},
    {"Facility": "Giwa Hospital", "Landmark": "KadunaNorth", "Latitude": 10.54384, "Longitude": 7.4330866, "Postal code": "800283"},
    {"Facility": "Jowako Hospital", "Landmark": "KadunaSouth", "Latitude": 10.5141785, "Longitude": 7.4327164, "Postal code": "800283"},
    {"Facility": "Police Medical Center", "Landmark": "KadunaNorth", "Latitude": 10.5083044, "Longitude": 7.4408297, "Postal code": "800283"},
    {"Facility": "Salamat Hospital", "Landmark": "KadunaSouth", "Latitude": 10.5105616, "Longitude": 7.4048481, "Postal code": "800282"},
    {"Facility": "Zakari Isah Memorial Clinic", "Landmark": "KadunaNorth", "Latitude": 10.5092126, "Longitude": 7.43175, "Postal code": "800283"},
    {"Facility": "Gwamna Awan General Hospital", "Landmark": "KadunaSouth", "Latitude": 10.465898, "Longitude": 7.4023337, "Postal code": "800282"},
    {"Facility": "Harmony Hospital", "Landmark": "KadunaSouth", "Latitude": 10.4772698, "Longitude": 7.4371777, "Postal code": "800282"},
    {"Facility": "Makera I Primary Health Center", "Landmark": "KadunaSouth", "Latitude": 10.4691094, "Longitude": 7.4122172, "Postal code": "800282"},
    {"Facility": "Maneks Hospital", "Landmark": "KadunaSouth", "Latitude": 10.4678021, "Longitude": 7.4135583, "Postal code": "800282"},
    {"Facility": "Barnawa Primary Health Center", "Landmark": "KadunaSouth", "Latitude": 10.4816, "Longitude": 7.42964, "Postal code": "800282"},
    {"Facility": "Sefa Hospital", "Landmark": "KadunaSouth", "Latitude": 10.5391763, "Longitude": 7.4203914, "Postal code": "800283"},
    {"Facility": "St. Gerald's Hospital - Kaduna", "Landmark": "KadunaSouth", "Latitude": 10.4679478, "Longitude": 7.4214052, "Postal code": "800282"},
    {"Facility": "Yusuf Dantsoho Memorial Hospital", "Landmark": "KadunaSouth", "Latitude": 10.5211417, "Longitude": 7.417315, "Postal code": "800282"},
    {"Facility": "Kagarko General Hospital", "Landmark": "Kagarko", "Latitude": 9.4895499, "Longitude": 7.6816829, "Postal code": "802113"},
    {"Facility": "Idon Rural Hospital", "Landmark": "Kajuru", "Latitude": 10.1083293, "Longitude": 7.9113984, "Postal code": "800252"},
    {"Facility": "Manchok Maternal and Child Health Clinic", "Landmark": "Kaura", "Latitude": 9.6687091, "Longitude": 8.5122343, "Postal code": "801114"},
    {"Facility": "Kaura Rural Hospital", "Landmark": "Kaura", "Latitude": 9.667003, "Longitude": 8.4714648, "Postal code": "801112"},
    {"Facility": "Turaki Buga Memorial Hospital", "Landmark": "Kaura", "Latitude": 9.63452, "Longitude": 8.39633, "Postal code": "801113"},
    {"Facility": "Rural Hospital Kauru", "Landmark": "Kauru", "Latitude": 10.5732974, "Longitude": 8.1436652, "Postal code": "800106"},
    {"Facility": "Pambegua General Hospital", "Landmark": "Kubau", "Latitude": 10.68278636, "Longitude": 8.274129118, "Postal code": "811108"},
    {"Facility": "Hunkuyi General Hospital", "Landmark": "Kudan", "Latitude": 11.2597332, "Longitude": 7.6484487, "Postal code": "812104"},
    {"Facility": "General Hospital Saminaka", "Landmark": "Lere", "Latitude": 10.4148417, "Longitude": 8.6778333, "Postal code": "801159"},
    {"Facility": "General Hospital Makarfi", "Landmark": "Makarfi", "Latitude": 11.3798125, "Longitude": 7.8854057, "Postal code": "812103"},
    {"Facility": "Major Ibrahim Bello Abdullahi Memorial Hospital Sabongari", "Landmark": "SabonGari", "Latitude": 11.1065561, "Longitude": 7.7271235, "Postal code": "810103"},
    {"Facility": "Gwantu General Hospital", "Landmark": "Sanga", "Latitude": 9.22265, "Longitude": 8.46275, "Postal code": "801131"},
    {"Facility": "Maigana General Hospital", "Landmark": "Soba", "Latitude": 11.0275239, "Longitude": 7.9390537, "Postal code": "810101"},
    {"Facility": "St. Louis Hospital - Zonkwa", "Landmark": "ZangonKataf", "Latitude": 9.7781454, "Longitude": 8.2777168, "Postal code": "802106"},
    {"Facility": "Zonkwa Regional Hospital", "Landmark": "ZangonKataf", "Latitude": 9.7700651, "Longitude": 8.2808499, "Postal code": "802106"},
    {"Facility": "Zango-Kataf General Hospital", "Landmark": "ZangonKataf", "Latitude": 9.8280814, "Longitude": 8.3987504, "Postal code": "802106"},
    {"Facility": "Anna-Kitcher Hospital", "Landmark": "Zaria", "Latitude": 11.0748561, "Longitude": 7.682676, "Postal code": "810282"},
    {"Facility": "Hajiya Gambo Sawaba Hospital", "Landmark": "Zaria", "Latitude": 11.04043, "Longitude": 7.69805, "Postal code": "810282"},
    {"Facility": "Muslim Specialist Hospital", "Landmark": "KadunaNorth", "Latitude": 11.0790931, "Longitude": 7.687342, "Postal code": "810282"},
    {"Facility": "National Tuberculosis And Leprosy Training Center - Zaria", "Landmark": "Zaria", "Latitude": 11.0404511, "Longitude": 7.6427805, "Postal code": "810282"},
    {"Facility": "St. Luke's Hospital, Wusasa", "Landmark": "Zaria", "Latitude": 11.0764519, "Longitude": 7.6792299, "Postal code": "810282"},
    {"Facility": "Virtual Hospital", "Landmark": "Chikun", "Latitude": 10.456995, "Longitude": 7.454195, "Postal code": "810282"},
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
    today = datetime.now().date()
    min_date = datetime(2025, 1, 1).date()
    selected_date = st.date_input("📅 Select today's date", today, min_value=min_date, max_value=today)

# --- Manual Fallback ---
with st.expander("📍 Get My Location Manually"):
    st.markdown("""
    If automatic GPS is slow or blocked, click below to open an external site, copy your location, and paste it here.
    """)
    gps_url = "https://gps-coordinates.org/my-location.php"
    st.markdown(f"[🌐 Open GPS Website]({gps_url})", unsafe_allow_html=True)

    col_lat, col_lon = st.columns(2)
    with col_lat:
        manual_lat = st.text_input("🔢 Latitude (from website)", "")
    with col_lon:
        manual_lon = st.text_input("🔢 Longitude (from website)", "")

    if manual_lat and manual_lon:
        st.success(f"📍 Manual Location Set: Latitude {manual_lat}, Longitude {manual_lon}")

# Add the 'Get My Location Automatically' button below the expander
get_location_auto = st.button("Get My Location Automatically")
if get_location_auto:
    st.info("_GPS is taking time to load... pls, explore the Get My Location manually option._")

# --- Submit to Google Sheet ---
submit_to_sheet = st.button("✅ Submit Attendance to Google Sheet")

if submit_to_sheet:
    lat, lon, timestamp = None, None, None
    valid_coords = True
    if manual_lat and manual_lon:
        try:
            lat_val = float(manual_lat)
            lon_val = float(manual_lon)
            # Validate latitude and longitude ranges
            if not (-90 <= lat_val <= 90 and -180 <= lon_val <= 180):
                valid_coords = False
            else:
                lat = lat_val
                lon = lon_val
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            valid_coords = False
        if not valid_coords:
            st.error("❌ Wrong input, please input correct coordinates of your location.")
    else:
        st.error("❌ No location data to submit.")

    if valid_coords and lat is not None and lon is not None and timestamp is not None:
        selected_facility = next((f for f in facility_data if f["Facility"] == selected_facility_name), None)
        if selected_facility:
            # Calculate distance
            facility_coord = (selected_facility["Latitude"], selected_facility["Longitude"])
            user_coord = (lat, lon)
            distance_km = geodesic(facility_coord, user_coord).km
            if distance_km > 0.5:
                punctuality_status = "not in the facility"
            else:
                punctuality_status = "arrived at the facility"

            # Determine punctuality outcome
            try:
                time_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").time()
                punctuality_outcome = "You came on time" if (time_obj.hour < 8 or (time_obj.hour == 8 and time_obj.minute <= 45)) else "You are late"
            except Exception:
                punctuality_outcome = "Invalid timestamp"

            # Prepare row for Google Sheet in the specified order
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
                punctuality_status,   # Punctuality Check
                round(distance_km, 7), # Distance
                punctuality_outcome    # Punctuality Outcome
            ]
            try:
                scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                service_account_info = dict(st.secrets["google_service_account"])
                creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
                client = gspread.authorize(creds)
                sheet = client.open("Attendant tracker")
                worksheet = sheet.sheet1
                # Ensure header exists in the specified order
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



