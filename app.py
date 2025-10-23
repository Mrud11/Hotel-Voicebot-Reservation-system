import streamlit as st
from datetime import datetime
from main import (
    record_and_transcribe,
    text_to_speech_bytes,
    search_hotels,
    prepare_comparison,
    ask_llm,
    save_booking,
    generate_receipt,
)

st.set_page_config(page_title="Smart Hotel Reservation System", page_icon="🏨")
st.title("Smart Hotel Reservation System")
st.write("Use your voice or text to search and book hotels in India.")

# Initialize session state values
if "step" not in st.session_state:
    st.session_state.step = "search"
if "hotels_df" not in st.session_state:
    st.session_state.hotels_df = None
if "booking_details" not in st.session_state:
    st.session_state.booking_details = None

def voice_or_text_input(label_voice, label_text, key_voice, key_text):
    voice_text = ""
    if st.button(label_voice):
        st.info("Listening, please speak now...")
        voice_text = record_and_transcribe()
        st.success(f"Recognized: {voice_text}")
        st.session_state[key_voice + "_temp"] = voice_text

    default_val = st.session_state.get(key_voice + "_temp", "")
    typed_text = st.text_input(label_text, value=default_val, key=key_text)
    return st.session_state.get(key_voice + "_temp", "") or typed_text

if st.session_state.step == "search":
    city = st.text_input("City or Location", key="city")
    check_in = st.date_input("Check-in Date", key="check_in")
    check_out = st.date_input("Check-out Date", key="check_out")
    adults = st.number_input("Adults", min_value=1, max_value=10, value=2, key="adults")

    query = voice_or_text_input(
        "Record your search query",
        "Or type your query here",
        "voice_search_query",
        "typed_search_query"
    )

    if st.button("Search Hotels") and (city or query):
        search_text = query.strip() if query else f"Find hotels in {city} from {check_in} to {check_out} for {adults} adults."

        ai_response = ask_llm(search_text)
        if ai_response.startswith("LLM API error"):
            st.error(ai_response)
        else:
            st.subheader("🤖 Assistant response:")
            st.write(ai_response)
            st.audio(text_to_speech_bytes(ai_response), format="audio/mp3")

        hotels_raw = search_hotels(city, check_in.strftime("%Y-%m-%d"), check_out.strftime("%Y-%m-%d"), adults)
        df_hotels = prepare_comparison(hotels_raw)

        if df_hotels.empty:
            st.warning("No hotels found, please try different criteria.")
        else:
            st.session_state.hotels_df = df_hotels
            st.session_state.step = "select"
            # Clear voice/text queries after search
            st.session_state.voice_search_query_temp = ""
            st.session_state.typed_search_query = ""

elif st.session_state.step == "select":
    st.subheader("Select Hotel to Book")
    df = st.session_state.hotels_df
    st.dataframe(df.reset_index(drop=True))

    selected_hotel = voice_or_text_input(
        "Record hotel name to select",
        "Or select hotel by typing",
        "voice_selected_hotel",
        "typed_selected_hotel"
    )

    # Validate selection to existing hotel names
    valid_hotels = df["Name"].tolist()
    if selected_hotel not in valid_hotels:
        st.warning("Please choose a valid hotel name from the list.")
        selected_hotel = None

    user_name = voice_or_text_input(
        "Record your full name",
        "Or type your full name",
        "voice_user_name",
        "typed_user_name"
    )

    if st.button("Confirm Booking") and selected_hotel and user_name.strip():
        hotel_info = df[df["Name"] == selected_hotel].iloc[0]
        booking = {
            "Name": user_name,
            "Hotel": hotel_info["Name"],
            "Address": hotel_info["Address"],
            "Check-in": st.session_state.check_in.strftime("%Y-%m-%d"),
            "Check-out": st.session_state.check_out.strftime("%Y-%m-%d"),
            "Price": hotel_info["Min Price (₹)"],
            "Rating": hotel_info["Rating"],
            "Booking Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        save_booking(booking)
        st.session_state.booking_details = booking
        st.session_state.step = "confirm"

elif st.session_state.step == "confirm":
    details = st.session_state.booking_details
    st.success(f"Booking confirmed at {details['Hotel']}!")

    confirmation_msg = f"Booking confirmed for {details['Hotel']}. Thank you, {details['Name']}."
    st.audio(text_to_speech_bytes(confirmation_msg), format="audio/mp3")

    receipt_file = generate_receipt(details)
    with open(receipt_file, "rb") as f:
        st.download_button("Download booking receipt", f, file_name="booking_receipt.txt")

    if st.button("Start New Search"):
        # Clear all session state values to restart the flow
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()
