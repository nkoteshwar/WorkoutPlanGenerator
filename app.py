"""
Workout Plan Generator - Streamlit Web Application.

A modern, single-page Streamlit application that collects structured user inputs
and generates personalized, safety-conscious workout plans via the Groq API.
"""

import os
import streamlit as st
from dotenv import load_dotenv

from generator import (
    generate_workout_plan,
    swap_exercise,
    VALID_GOALS,
    VALID_EXPERIENCE,
    VALID_EQUIPMENT,
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="FitAI | Personalized Workout Plan Generator",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for a modern visual interface
CUSTOM_CSS = """
<style>
    /* Global Styling */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 50%, #1E1B4B 100%);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38BDF8, #818CF8, #C084FC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: #94A3B8;
        max-width: 800px;
    }

    /* Metric Badges */
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 1rem;
    }

    .badge-item {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 600;
        color: #E2E8F0;
    }

    /* Input Card Container */
    .card-box {
        background: #0F172A;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #334155;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }

    /* Disclaimer Alert */
    .disclaimer-box {
        background-color: rgba(234, 179, 8, 0.1);
        border-left: 4px solid #EAB308;
        padding: 1rem 1.25rem;
        border-radius: 6px;
        color: #FEF08A;
        margin-bottom: 1.5rem;
        font-size: 0.95rem;
    }

    /* Buttons Styling */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #2563EB 0%, #4F46E5 100%);
        color: white;
        font-weight: 700;
        font-size: 1rem;
        padding: 0.6rem 1.8rem;
        border-radius: 8px;
        border: none;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
    }

    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45);
        background: linear-gradient(90deg, #1D4ED8 0%, #4338CA 100%);
    }

    /* Secondary Action Button */
    div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px);
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #64748B;
        font-size: 0.85rem;
        border-top: 1px solid #334155;
        margin-top: 3rem;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize Session State
if "workout_plan" not in st.session_state:
    st.session_state["workout_plan"] = None
if "plan_inputs" not in st.session_state:
    st.session_state["plan_inputs"] = None
if "swap_result" not in st.session_state:
    st.session_state["swap_result"] = None

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/dumbbell.png", width=64)
    st.title("FitAI Settings")
    st.caption("Powered by Groq Llama 3 & DeepMind AI principles")

    st.markdown("---")
    
    # API Key Handling
    env_api_key = os.getenv("GROQ_API_KEY", "").strip()
    
    if env_api_key:
        st.success("API Key loaded from `.env`", icon="✅")
        with st.expander("🔑 Override API Key (Optional)"):
            custom_key = st.text_input(
                "Custom Groq API Key",
                type="password",
                help="Leave blank to use the key from your .env file."
            )
        api_key_input = custom_key.strip() if custom_key.strip() else env_api_key
    else:
        api_key_input = st.text_input(
            "Groq API Key",
            type="password",
            help="Get a free Groq API key from https://console.groq.com/keys"
        ).strip()

        if api_key_input:
            st.success("API Key set!", icon="✅")
        else:
            st.warning("Please enter your Groq API key or set GROQ_API_KEY in .env", icon="🔑")

    st.markdown("---")

    # LLM Model Selection
    selected_model = st.selectbox(
        "Select Model",
        options=AVAILABLE_MODELS,
        index=0,
        help="Choose the Groq LLM model to power your trainer."
    )

    st.markdown("---")
    st.markdown(
        """
        ### 📋 About FitAI
        This application acts as a personal trainer to create personalized,
        safe, and structured workout plans tailored to your goals, equipment, 
        and physical limitations.
        
        **Assignment Specs**:
        - Single-page Streamlit App
        - Structured input form
        - Groq API Integration
        - Robust error handling
        - Custom exercise swap tool
        """
    )


# --- MAIN CONTENT AREA ---
# Hero Header
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-title">🏋️ AI Personal Workout Generator</div>
        <div class="hero-subtitle">
            Get a tailored, exercise-by-exercise weekly training program designed specifically for your goals, 
            schedule, available equipment, and physical needs.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- SECTION 1: STRUCTURED INPUT FORM ---
st.markdown("### 🎯 STEP 1: Tell Us About Yourself")

with st.form("workout_form"):
    col1, col2 = st.columns(2)

    with col1:
        fitness_goal = st.selectbox(
            "🎯 Primary Fitness Goal *",
            options=VALID_GOALS,
            index=0,
            help="What is your main target for this workout split?"
        )

        experience_level = st.selectbox(
            "📈 Experience Level *",
            options=VALID_EXPERIENCE,
            index=1,
            help="Select your current familiarity with strength training."
        )

        days_per_week = st.slider(
            "🗓️ Days Available per Week *",
            min_value=1,
            max_value=7,
            value=4,
            help="How many days per week can you commit to exercising?"
        )

    with col2:
        equipment = st.selectbox(
            "🏋️ Equipment Access *",
            options=VALID_EQUIPMENT,
            index=2,
            help="What equipment do you have access to?"
        )

        session_duration = st.select_slider(
            "⏱️ Target Session Duration (Minutes)",
            options=[15, 30, 45, 60, 75, 90, 120],
            value=45,
            help="Preferred duration for each workout session."
        )

        injuries_limitations = st.text_area(
            "⚠️ Injuries or Physical Limitations (Optional)",
            placeholder="e.g., Lower back pain, bad knees, no overhead pressing, shoulder impingement...",
            help="Mention any active injuries, pain points, or movements to avoid.",
            height=100
        )

    submit_button = st.form_submit_button("🔥 Generate Workout Plan", use_container_width=True)


# --- GENERATION LOGIC ---
if submit_button:
    # Validate API key
    if not api_key_input.strip():
        st.error("🔑 Groq API Key is missing! Please enter your API Key in the sidebar.", icon="🚫")
    else:
        with st.spinner("🧠 Personal Trainer AI is designing your custom workout plan..."):
            result = generate_workout_plan(
                fitness_goal=fitness_goal,
                experience_level=experience_level,
                days_per_week=days_per_week,
                equipment=equipment,
                injuries_limitations=injuries_limitations,
                session_duration=session_duration,
                api_key=api_key_input.strip(),
                model_name=selected_model
            )

            if result["success"]:
                st.session_state["workout_plan"] = result["plan"]
                st.session_state["plan_inputs"] = result["raw_inputs"]
                st.toast("Workout plan generated successfully!", icon="🎉")
            else:
                st.error(f"❌ Error generating plan: {result['error']}", icon="🚨")


# --- SECTION 2: WORKOUT PLAN DISPLAY ---
if st.session_state["workout_plan"]:
    st.markdown("---")
    st.markdown("### 📝 Your Customized Weekly Workout Plan")

    inputs_used = st.session_state.get("plan_inputs", {})

    # Display Badges of Active Profile
    if inputs_used:
        st.markdown(
            f"""
            <div class="badge-container">
                <span class="badge-item">🎯 Goal: {inputs_used.get('fitness_goal')}</span>
                <span class="badge-item">📈 Level: {inputs_used.get('experience_level')}</span>
                <span class="badge-item">🗓️ Frequency: {inputs_used.get('days_per_week')} Days/Week</span>
                <span class="badge-item">🏋️ Equipment: {inputs_used.get('equipment')}</span>
                <span class="badge-item">⏱️ Duration: ~{inputs_used.get('session_duration')} mins</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Action Toolbar (Regenerate & Download)
    col_reg, col_dl, col_space = st.columns([1.5, 1.5, 5])

    with col_reg:
        if st.button("🔄 Regenerate Plan", key="btn_regenerate"):
            with st.spinner("Generating fresh variation..."):
                res = generate_workout_plan(
                    fitness_goal=inputs_used.get("fitness_goal", fitness_goal),
                    experience_level=inputs_used.get("experience_level", experience_level),
                    days_per_week=inputs_used.get("days_per_week", days_per_week),
                    equipment=inputs_used.get("equipment", equipment),
                    injuries_limitations=inputs_used.get("injuries_limitations", injuries_limitations),
                    session_duration=inputs_used.get("session_duration", session_duration),
                    api_key=api_key_input.strip(),
                    model_name=selected_model
                )
                if res["success"]:
                    st.session_state["workout_plan"] = res["plan"]
                    st.rerun()
                else:
                    st.error(res["error"])

    with col_dl:
        plan_text = st.session_state["workout_plan"]
        st.download_button(
            label="📥 Download Plan (.md)",
            data=plan_text,
            file_name="My_Custom_Workout_Plan.md",
            mime="text/markdown",
            key="btn_download"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Render Plan Output
    st.markdown(st.session_state["workout_plan"])

    st.markdown("---")

    # --- SECTION 3: STRETCH GOAL FEATURE - SWAP AN EXERCISE ---
    st.markdown("### 🔄 Mini-Feature: Swap an Exercise")
    st.caption("Don't like a specific exercise in your plan? Request a safe, equivalent swap below!")

    with st.expander("🛠️ Open Exercise Swapping Tool", expanded=False):
        swap_col1, swap_col2 = st.columns(2)
        with swap_col1:
            orig_ex = st.text_input("Exercise to replace", placeholder="e.g., Barbell Back Squat")
        with swap_col2:
            target_group = st.text_input("Target Muscle Group / Movement", placeholder="e.g., Quadriceps / Legs")

        if st.button("Find Alternative Exercise", key="btn_swap"):
            if not orig_ex or not target_group:
                st.warning("Please fill in both exercise name and target muscle group.")
            elif not api_key_input.strip():
                st.error("Please enter your Groq API key in sidebar.")
            else:
                with st.spinner("Finding safe replacement..."):
                    swap_res = swap_exercise(
                        original_exercise=orig_ex,
                        target_muscle_group=target_group,
                        equipment=inputs_used.get("equipment", equipment),
                        injuries_limitations=inputs_used.get("injuries_limitations", injuries_limitations),
                        api_key=api_key_input.strip(),
                        model_name=selected_model
                    )
                    st.session_state["swap_result"] = swap_res

        if st.session_state.get("swap_result"):
            sw = st.session_state["swap_result"]
            if sw.get("success"):
                st.success("Suggested Alternative:")
                st.markdown(sw.get("suggestion"))
            else:
                st.error(sw.get("error"))

# Footer
st.markdown(
    """
    <div class="footer">
        Built for AI Engineering Cohort Assignment | Powered by Groq API & Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
