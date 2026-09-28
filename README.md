# 🏋️ FitAI - Personalized Workout Plan Generator

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Groq API](https://img.shields.io/badge/Groq_API-F05032?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com/)
[![Python 3.13](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

An AI-powered single-page Streamlit web application that collects structured inputs about a user's fitness goals, experience level, equipment access, frequency, and physical limitations to generate a safe, highly tailored weekly workout plan using **Groq LLM** (`qwen/qwen3.8-27b`).

---

## 🌟 Key Features & Requirements Matrix

| Rubric Requirement / Feature | Status | Details |
| :--- | :---: | :--- |
| **Structured Inputs** | ✅ Complete | Dropdowns for Goal & Experience, Slider for Days (1-7), Equipment Dropdown, Optional Injuries Free-Text. |
| **Prompt Design** | ✅ Complete | Strict constraint adherence (Equipment compliance, injury adaptation, day-by-day markdown output, safety disclaimers). |
| **Type Hints & Clean Code** | ✅ Complete | Python dataclasses, full type hints (`typing`), docstrings, modular function separation (`generator.py` & `app.py`). |
| **Error Handling** | ✅ Complete | Input validation (no crashes on invalid/0 days), Groq API exception handling (`AuthenticationError`, `RateLimitError`, `APIConnectionError`). |
| **Session Persistence** | 🌟 Stretch Goal | Generated plan saved in `st.session_state` so it persists across reruns. |
| **Regenerate Plan** | 🌟 Stretch Goal | One-click button to generate fresh workout variations. |
| **Download Plan** | 🌟 Stretch Goal | Download your custom plan directly as `.md` file. |
| **Exercise Swap Tool** | 🌟 Stretch Goal | Interactive mini-feature to request alternative exercises respecting equipment & injury constraints. |

---

## 🛠️ Project Structure

```text
WorkoutPlanGenerator/
├── app.py                  # Main Streamlit web application (UI & layout)
├── generator.py            # Core logic (validation, prompt engineering, Groq API call)
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── README.md               # Documentation & setup instructions
└── tests/
    └── test_generator.py   # Unit tests for input validation & prompt structure
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or higher installed.
- A free **Groq API Key** from [Groq Console](https://console.groq.com/keys).

### 2. Clone & Install Dependencies
```bash
# Clone the repository
git clone https://github.com/your-username/WorkoutPlanGenerator.git
cd WorkoutPlanGenerator

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration (Optional)
Copy `.env.example` to `.env` and set your Groq API key:
```bash
GROQ_API_KEY=your_groq_api_key_here
```
*Note: You can also enter your API Key directly in the app's sidebar UI.*

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```
Open http://localhost:8501 in your browser!

---

## 🧪 Running Unit Tests

Run the test suite to verify input validation and prompt construction logic:

```bash
python -m unittest discover tests
```

---

## 🎨 UI Screenshots & Interface Design
- **Dark Mode Modern Aesthetic**: Clean typography with Google Font *Plus Jakarta Sans* & sleek CSS styling.
- **Interactive Badges**: Summarizes active client profile parameters once generated.
- **Safety Callout Alerts**: Highlights medical disclaimers if injuries or limitations are provided.

---
Sample Output:
<img width="1834" height="946" alt="image" src="https://github.com/user-attachments/assets/71b41253-36d5-461a-ae53-a60a7a8a61fa" />
<img width="1777" height="984" alt="image" src="https://github.com/user-attachments/assets/724c08ce-17aa-4fc8-9c37-2726f5ab8fab" />
<img width="1555" height="747" alt="image" src="https://github.com/user-attachments/assets/338b9988-d124-4eea-a359-d19817b53cee" />




