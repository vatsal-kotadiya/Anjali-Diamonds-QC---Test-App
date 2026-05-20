import streamlit as st
active = st.session_state.get("active", True)
if active:
    diamond_id = st.text_input("ID")
    audio = st.audio_input("Record")
    submit = st.button("Submit", disabled=not (diamond_id and audio))
    if submit:
        st.success(f"Submitted {diamond_id} and audio size {len(audio.getvalue())}")
        st.session_state["active"] = False
