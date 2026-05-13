import streamlit as st
from services.auth.login_wall import render_login_wall
from services.state.session_defaults import inital_session_dafaults
from services.config.workout_config import EXERCISE_OPTIONS
from services.ui.style_loader import load_css, inject_local_font, inject_webrtc_styles
from services.persistence.exercise_repository import init_db
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from services.vision.exercise_video_processor import VideoProcessorClass
from services.tracking.metrics import sync_metrics_update
from services.persistence.exercise_repository import get_user_exercise
import os
import time
import pandas as pd



def main():
    st.set_page_config(
        page_icon="🏋️",
        page_title="AI Real-Time GYM Coach",
        initial_sidebar_state="expanded",
        layout="centered"
        )
    
    load_css(os.path.join(os.getcwd(), "static", "style.css"))
    inject_local_font(os.path.join(os.getcwd(), "static", "AdobeClean.otf"), "AdobeClean")

    init_db()
    
    if not render_login_wall():
        return
    
    inital_session_dafaults()

    workout_started = st.session_state.get("workout_started")

    with st.sidebar:
        st.title("🏋️ Apna AI Coach")

        if st.session_state.username:
            st.caption(f"👤 Login as {st.session_state['username']}")

        st.divider()

        st.subheader("Workout plan")

        if not workout_started:
            plan_exercise = st.selectbox("Exercise", options=EXERCISE_OPTIONS, key="plan_exercise")

            plan_sets = st.number_input("Sets", min_value=1, max_value=10, key="plan_sets", step=1)

            plan_reps = st.number_input("Reps per set", min_value=2, max_value=50, key="plan_reps", step=2)

            st.space()

            start_session_button = st.button("Start Workout", width="stretch", key="start_session_button")

            if start_session_button:
                st.session_state.exercise_type = plan_exercise
                st.session_state.target_sets = int(plan_sets)
                st.session_state.reps_per_set = int(plan_reps)
                st.session_state.reps = 0
                st.session_state.workout_started = True
                st.session_state.set_cycle_started_at = time.time()
                st.session_state.last_saved_sets_completed = 0
                st.session_state.last_notified_sets_completed = 0
                st.session_state.last_notified_workout_complete = False

                st.rerun()
        else:
            exercise = st.session_state.get('plan_exercise')
            sets = st.session_state.get('plan_sets')
            reps = st.session_state.get('plan_reps')

            print(exercise, sets, reps)
            st.info(f"**{exercise}** -- {sets} Sets / {reps} Reps")

            st.space()

            end_session_button = st.button("End Workout", width="stretch", key="end_session_button")


            if end_session_button:
                st.session_state.workout_started = False
                st.rerun()
        
        if workout_started:
            st.divider()

            st.subheader("Progress")

            exercise = st.session_state.get('exercise_type')
            total_reps = st.session_state.get('reps')
            current_set_reps = st.session_state.get('current_set_reps')
            reps_per_set = st.session_state.get('reps_per_set')
            sets_completed = st.session_state.get('sets_completed')
            target_sets = st.session_state.get('target_sets')
            

            st.metric("Total Reps", f"{total_reps}")
            st.metric("Current Set Reps", f"{current_set_reps} / {reps_per_set}")
            st.metric("Sets Completed", f"{sets_completed} / {target_sets}")

            st.divider()

            if exercise == "Squats":
                st.subheader("Squat Metrics")
                st.metric("Knee Angle", f"{st.session_state.knee_angle}°")
                st.metric("Back Angle", f"{st.session_state.back_angle}°")
                st.metric("Depth Status", st.session_state.depth_status)

            elif exercise == "Push-ups":
                st.subheader("Push-up Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Body Alignment", st.session_state.body_alignment)
                st.metric("Hip Position", st.session_state.hip_status)

            elif exercise == "Biceps Curls (Dumbbell)":
                st.subheader("Curl Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Shoulder Stability", st.session_state.shoulder_status)
                st.metric("Swing Detection", st.session_state.swing_status)

            elif exercise == "Shoulder Press":
                st.subheader("Shoulder Press Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Arm Extension", st.session_state.extension_status)
                st.metric("Back Arch", st.session_state.back_arch_status)

            elif exercise == "Lunges":
                st.subheader("Lunge Metrics")
                st.metric("Front Knee Angle", f"{st.session_state.front_knee_angle}°")
                st.metric("Torso Angle", f"{st.session_state.torso_angle}°")
                st.metric("Balance Status", st.session_state.balance_status)


    st.markdown("""
                <p style="font-size:2.75rem; color: rgb(0, 0, 0, 0.90)">
                    AI Real Time GYM Coach
                </p>
            """, unsafe_allow_html=True,
        )

    st.markdown("""
                <p style="font-size:1.52rem; color: rgb(0, 0, 0, 0.90)">
                    Real time pose detection with proactive ai voice coaching
                </p>
            """, unsafe_allow_html=True,
    )


    if not workout_started:
        st.markdown(
            """
            <div style="
                border: 7px dashed rgb(0, 0, 0, 0.40);
                border-radius: 22px;
                padding: 48px 32px;
                text-align: center;
                color: rgb(0, 0, 0, 0.90);
                margin-top: 32px;
                margin-bottom: 32px;
            ">
                <h2 style="color:rgb(0, 0, 0, 0.80); margin-bottom:8px;">👈 Set your workout plan</h2>
                <p style="font-size:1.2rem;">
                    Choose your exercise, sets and reps in the sidebar,<br>
                    then click <strong>Start Workout</strong> to activate the camera and AI coach.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        context = webrtc_streamer(
            key="exercise_analysis",
            mode = WebRtcMode.SENDRECV,
            video_processor_factory = VideoProcessorClass,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={
                "video": True,
                "audio": False
            },
            async_processing = True
        )

        sync_metrics_update(context)

        if context.state.playing:
            time.sleep(0.25)
            st.rerun()
            
        inject_webrtc_styles()

    st.divider()

    st.markdown("""
                <p style="font-size:1.9rem; color: rgb(0, 0, 0, 1)">
                    Workout History
                </p>
            """, unsafe_allow_html=True,
    )

    user_id = st.session_state.get("user_id", 0)

    if isinstance(user_id, int):
        history_rows = get_user_exercise(user_id)

        arr = [
            {
                "Exercise": row['exercise_name'],
                "Reps": row['reps'],
                "Sets": row['sets'],
                "Time (sec)": row['time'],
                "Date": row['created_at']
            }
            for row in history_rows
        ]

        df = pd.DataFrame(arr)

        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            agg_df = df.groupby(["Exercise", "Date"]).agg({
                "Reps": 'sum',
                "Sets": "sum",
                "Time (sec)": "sum"
            }).reset_index()
            agg_df.index += 1
            st.table(agg_df, border="horizontal")
        else:
            st.info("No workout history found.")



if __name__ == "__main__":
    main()
