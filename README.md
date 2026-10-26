# 🎓 CogniLearn: AI Study Flashcard & Quiz Generator

> High-yield active recall flashcard generator, practice quiz builder, revision digest compiler, and instant CS doubt resolution engine powered by Gemini.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](cognilearn-ai.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

---

## 📌 Overview
Undergraduate students frequently face cognitive overload when parsing technical documentation, operating systems manuals, and lecture transcripts. Passive re-reading yields poor retention compared to active recall and targeted self-assessment.

**CogniLearn** automates curriculum-aligned active learning. By ingesting `.pdf` or `.txt` lecture notes (or pasted raw text), the system parses, isolates, and synthesizes study materials tailored to undergraduate computer science and engineering coursework.

---

## 🚀 Key Features

* **🗂️ Interactive Active-Recall Carousel:** Synthesizes structured flashcards into an interactive card deck with instant reveal toggles and boundary-checked navigation.
* **🎯 Source-Isolated Assessment Quizzes:** Generates multiple-choice diagnostic questions with clearly separated choices, step-by-step logic, and detailed answer keys per source document.
* **📋 High-Yield Revision Digest:** Compiles bulleted formulas, core algorithms, and concept definitions cleanly isolated per uploaded document.
* **💡 Rapid Doubt Resolution:** Instant CS concept clarification and interview/coding guidance supporting dual submission via keyboard Enter or dedicated dispatch action.
* **⚡ Zero-Lag Fragmented Architecture:** Built using modular Streamlit fragments (`@st.fragment`) and in-memory byte caching (`@st.cache_data`) to prevent redundant full-page reruns across every interaction.

---

## 🛠️ Architecture & Tech Stack

* **Frontend Framework:** Streamlit (Custom Light Theme with balanced contrast)
* **AI Model Engine:** `gemini-3.5-flash-lite` via the Google GenAI SDK (`google-genai`)
* **Document Parsing:** `pypdf` (multi-file ingestion and in-memory byte extraction)
* **Test Suite:** `pytest` (automated validation for payload aggregation, markdown stripping, and navigation bounds)

---

## 📦 Local Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/syamkumarakula26/CogniLearn.git](https://github.com/syamkumarakula26/CogniLearn.git)
   cd CogniLearn