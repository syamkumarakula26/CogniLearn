import streamlit as st
from google import genai
import pypdf
import io
import json

st.set_page_config(
    page_title="CogniLearn | AI Study Generator",
    page_icon="🎓",
    layout="wide"
)

# Dark Theme CSS
st.markdown("""
<style>
    /* 1. Base App & Canvas (Clean Crisp White & Slate Accents) */
    .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    /* 1.1 Force slider tick marks and labels to remain permanently visible */
    div[data-testid="stSlider"] div[data-testid="stSliderTickBar"] span {
        visibility: visible !important;
        opacity: 1 !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
    }
    /* 1.2 Your existing slider */
    quiz_difficulty = st.select_slider(
        "Quiz Difficulty",
        options=["Beginner", "Intermediate", "Advanced"],
        value="Intermediate",
        key="quiz_difficulty"
    )

    /* 2. File Uploader & Text Box Styling */
    .stFileUploader section {
        background-color: #ffffff !important;
        border: 2px dashed #cbd5e1 !important;
        border-radius: 10px !important;
    }
    .stFileUploader section * {
        color: #334155 !important;
    }
    .stFileUploader button {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
    }
    .stTextArea textarea {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        color: #0f172a !important;
        font-family: 'Inter', sans-serif;
    }
    .stTextArea textarea::placeholder {
        color: #94a3b8 !important;
        opacity: 1 !important;
    }

    /* 3. Global Buttons & Tabs */
    .stButton > button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #1d4ed8 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 0.15s ease-in-out !important;
    }
    .stButton > button:hover {
        background-color: #1d4ed8 !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
    }
    .stButton > button:disabled {
        background-color: #e2e8f0 !important;
        color: #94a3b8 !important;
        border: 1px solid #cbd5e1 !important;
        cursor: not-allowed !important;
        opacity: 0.7 !important;
        box-shadow: none !important;
    }

    /* Tab Bar */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #e2e8f0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px !important;
        color: #64748b !important;
        font-weight: 500 !important;
        border: none !important;
        background-color: transparent !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #0f172a !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #2563eb !important;
        font-weight: 700 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #2563eb !important;
        height: 3px !important;
        border-radius: 2px !important;
    }

    /* 4. Flashcard Deck Container (Crisp White Card with Soft Shadow) */
    .flashcard-box {
        background: #ffffff;
        border: 2px solid #93c5fd;
        border-radius: 16px;
        padding: 28px;
        min-height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
        margin: 15px 0;
    }
    .flashcard-badge {
        background-color: #2563eb;
        color: #ffffff;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-bottom: 12px;
        width: fit-content;
    }
    .flashcard-title {
        color: #64748b;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .flashcard-text {
        color: #0f172a;
        font-size: 1.25rem;
        font-weight: 600;
        line-height: 1.5;
    }
    .flashcard-answer-box {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        border: 1px solid #bbf7d0;
        border-left-width: 4px;
        padding: 14px 18px;
        border-radius: 6px;
        margin-top: 14px;
    }
    .flashcard-answer-text {
        color: #15803d;
        font-size: 1.05rem;
        font-weight: 500;
    }

    /* 5. Circular Blue Send Button for Tab 4 */
    div[data-testid="stColumn"]:has(button[key="btn_send_doubt"]) button,
    button[key="btn_send_doubt"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 50% !important;
        width: 44px !important;
        height: 44px !important;
        padding: 0 !important;
        font-size: 1.25rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        transition: transform 0.15s ease, background-color 0.15s ease !important;
    }
    button[key="btn_send_doubt"]:hover {
        background-color: #1d4ed8 !important;
        transform: scale(1.05) !important;
    }
</style>
""", unsafe_allow_html=True)

# API Initialization
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Missing `GEMINI_API_KEY` in Streamlit secrets! Please configure it.")
    st.stop()

client = genai.Client(api_key=api_key)

# Global Session State Initializer
for var, default_val in [
    ("cards_data", []),
    ("card_index", 0),
    ("show_card_answer", False),
    ("quiz_res", ""),
    ("summary_res", ""),
    ("qa_res", ""),
    ("last_doubt_query", ""),
    ("academic_level", "Undergraduate (B.Tech)"),
    ("quiz_difficulty", "Intermediate")
]:
    if var not in st.session_state:
        st.session_state[var] = default_val

# Cached PDF Parser
@st.cache_data(show_spinner=False)
def parse_pdf_cached(file_bytes):
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    return "\n".join([page.extract_text() or "" for page in reader.pages])

# Sidebar Settings
# Isolated Sidebar Fragment
@st.fragment
def fragment_sidebar_controls():
    with st.sidebar:
        st.title("🎓 Study Controls")
        
        st.session_state.academic_level = st.selectbox(
            "Academic Level",
            ["Undergraduate (B.Tech)", "High School", "Competitive Exams (GATE/GRE)"],
            index=["Undergraduate (B.Tech)", "High School", "Competitive Exams (GATE/GRE)"].index(
                st.session_state.academic_level
            ),
            key="sb_academic_level"
        )
        
        st.session_state.quiz_difficulty = st.select_slider(
            "Quiz Difficulty",
            options=["Beginner", "Intermediate", "Advanced / Tricky"],
            value=st.session_state.quiz_difficulty,
            key="sb_quiz_difficulty"
        )
        
        st.markdown("---")
        st.markdown("**Hacktoberfest 2026**")
        st.caption("Category: AI Study Flashcard & Quiz Generator")

# Render sidebar fragment
fragment_sidebar_controls()

# Top Header
st.title("🎓 CogniLearn: AI Flashcard & Quiz Generator")
st.markdown(
    "Upload syllabus documents, lecture slides, or raw study notes to generate active-recall "
    "flashcards, structured quizzes, summaries, and solve concept doubts in real time."
)

# Multi-Source Input Section (Fragmented to prevent full page re-renders during uploads)
@st.fragment
def fragment_input_sources():
    col_file, col_text = st.columns([1, 1])

    with col_file:
        uploaded_files = st.file_uploader(
            "Upload Study Documents (.pdf, .txt)",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            key="file_uploader_widget"
        )

        # 1. Track currently uploaded file keys
        current_uploaded_keys = set()

        if uploaded_files:
            for file in uploaded_files:
                file_key = f"File: {file.name}"
                current_uploaded_keys.add(file_key)

                if file_key not in st.session_state.sources_dict:
                    try:
                        if file.name.endswith(".pdf"):
                            pdf_content = parse_pdf_cached(file.getvalue())
                            st.session_state.sources_dict[file_key] = pdf_content.strip()
                        else:
                            txt_content = file.getvalue().decode("utf-8", errors="ignore")
                            st.session_state.sources_dict[file_key] = txt_content.strip()
                    except Exception as e:
                        st.error(f"Error reading {file.name}: {e}")

        # 2. Automatically remove any files that were deleted/removed from the uploader
        stale_file_keys = [
            k for k in st.session_state.sources_dict.keys() 
            if k.startswith("File: ") and k not in current_uploaded_keys
        ]
        for stale_k in stale_file_keys:
            del st.session_state.sources_dict[stale_k]

    with col_text:
        pasted_notes = st.text_area(
            "Or / Also Paste Lecture Notes Here:",
            height=140,
            placeholder="Paste topic definitions, code algorithms, or lecture transcripts...",
            key="pasted_text_widget"
        )
        st.caption("⌨️ Press **Ctrl + Enter** (or click outside the box) to register pasted text.")
        if pasted_notes.strip():
            st.session_state.sources_dict["Pasted Lecture Notes"] = pasted_notes.strip()
        elif "Pasted Lecture Notes" in st.session_state.sources_dict and not pasted_notes.strip():
            st.session_state.sources_dict.pop("Pasted Lecture Notes", None)

    # Status Bar
    total_sources = len(st.session_state.sources_dict)
    total_chars = sum(len(c) for c in st.session_state.sources_dict.values())
    if total_sources > 0:
        st.info(f"✅ Loaded {total_sources} source(s) ({total_chars} total characters). Engine: `gemini-3.5-flash-lite`")

# Global storage for source contents across fragments
if "sources_dict" not in st.session_state:
    st.session_state.sources_dict = {}

fragment_input_sources()

# Helper property to construct prompt payload on-demand
def get_active_study_text():
    combined = []
    for s_name, content in st.session_state.sources_dict.items():
        combined.append(f"=== SOURCE START: {s_name} ===\n{content}\n=== SOURCE END: {s_name} ===")
    return "\n\n".join(combined).strip()

# Shared Streaming Engine Function
def stream_study_engine(task_instruction: str, content: str):
    academic_lvl = st.session_state.get("academic_level", "Undergraduate (B.Tech)")
    quiz_diff = st.session_state.get("quiz_difficulty", "Intermediate")

    prompt = (
        f"You are a master academic educator and curriculum designer.\n"
        f"Target Level: {academic_lvl}\n"
        f"Target Difficulty: {quiz_diff}\n\n"
        f"Task:\n{task_instruction}\n\n"
        f"Instructions:\n"
        f"- Be structured, accurate, and pedagogical.\n"
        f"- Format formulas with LaTeX where applicable ($equation$).\n"
        f"- Do not include conversational small talk.\n\n"
        f"Source Material:\n{content}\n"
    )
    try:
        response_stream = client.models.generate_content_stream(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"❌ Error communicating with AI Engine: {e}"

# UI Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🗂️ Active Recall Flashcards",
    "🎯 Interactive Quiz",
    "📋 High-Yield Summary",
    "💡 Rapid Doubt Solver"
])

# ----------------- TAB 1 (Fragmented) -----------------
with tab1:
    st.subheader("🗂️ Active Recall Flashcard Deck")
    st.caption("Review cards one at a time. Test your memory, click reveal, and cycle through the deck.")

    @st.fragment
    def fragment_flashcards():
        if st.button("✨ Generate Flashcard Deck", key="btn_flashcards"):
            if not get_active_study_text():
                st.warning("Please upload a document or paste notes above first.")
            else:
                with st.spinner("Synthesizing memory cards into deck..."):
                    task = (
                        "Extract 6 to 10 high-impact active recall flashcards from the study material.\n"
                        "CRITICAL: Output ONLY a valid JSON array of objects. Do NOT include markdown code blocks, backticks, or other text.\n"
                        "Schema:\n"
                        "[\n"
                        "  {\n"
                        "    \"source\": \"Name of File or Source\",\n"
                        "    \"topic\": \"Specific Concept/Theorem Name\",\n"
                        "    \"question\": \"The active recall prompt or question\",\n"
                        "    \"answer\": \"Clear, concise answer with key terms or formulas\"\n"
                        "  }\n"
                        "]"
                    )
                    try:
                        response = client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=f"Study Content:\n{get_active_study_text()}\n\nTask:\n{task}"
                        )
                        raw_text = response.text.strip()
                        if raw_text.startswith("```json"):
                            raw_text = raw_text[7:]
                        if raw_text.startswith("```"):
                            raw_text = raw_text[3:]
                        if raw_text.endswith("```"):
                            raw_text = raw_text[:-3]

                        st.session_state.cards_data = json.loads(raw_text.strip())
                        st.session_state.card_index = 0
                        st.session_state.show_card_answer = False
                    except Exception as e:
                        st.error(f"Failed to generate structured flashcards: {e}")

        if st.session_state.cards_data:
            cards = st.session_state.cards_data
            idx = st.session_state.card_index
            total = len(cards)
            current_card = cards[idx]

            col_meta1, col_meta2 = st.columns([3, 1])
            col_meta1.caption(f"📁 **Source:** `{current_card.get('source', 'Study Material')}`")
            col_meta2.markdown(f"<div style='text-align: right; color: #94a3b8; font-weight: 600;'>Card {idx + 1} of {total}</div>", unsafe_allow_html=True)

            answer_block = ""
            if st.session_state.show_card_answer:
                answer_text = current_card.get('answer', '')
                answer_block = (
                    f'<div class="flashcard-answer-box">'
                    f'<span style="font-size: 0.8rem; color: #a7f3d0; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Answer & Key Notes:</span>'
                    f'<div class="flashcard-answer-text">{answer_text}</div>'
                    f'</div>'
                )

            card_html = (
                f'<div class="flashcard-box">'
                f'<div class="flashcard-badge">{current_card.get("topic", "Flashcard")}</div>'
                f'<div class="flashcard-title">Prompt:</div>'
                f'<div class="flashcard-text">{current_card.get("question", "")}</div>'
                f'{answer_block}'
                f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

            def prev_card():
                if st.session_state.card_index > 0:
                    st.session_state.card_index -= 1
                    st.session_state.show_card_answer = False

            def next_card():
                if st.session_state.card_index < total - 1:
                    st.session_state.card_index += 1
                    st.session_state.show_card_answer = False

            def toggle_answer():
                st.session_state.show_card_answer = not st.session_state.show_card_answer

            nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
            with nav_col1:
                st.button("⬅️ Previous", disabled=(idx == 0), key="btn_prev_card", on_click=prev_card, use_container_width=True)
            with nav_col2:
                reveal_label = "🙈 Hide Answer" if st.session_state.show_card_answer else "👁️ Reveal Answer"
                st.button(reveal_label, key="btn_reveal_toggle", on_click=toggle_answer, use_container_width=True)
            with nav_col3:
                st.button("Next ➡️", disabled=(idx == total - 1), key="btn_next_card", on_click=next_card, use_container_width=True)

            st.markdown("---")
            md_export = "# Study Flashcards Deck\n\n"
            for i, c in enumerate(cards, 1):
                md_export += f"### Card {i}: {c.get('topic', 'Topic')} ({c.get('source', '')})\n"
                md_export += f"- **Question:** {c.get('question', '')}\n"
                md_export += f"- **Answer:** {c.get('answer', '')}\n\n"

            st.download_button(
                label="📥 Download Entire Deck (.md)",
                data=md_export,
                file_name="flashcard_deck.md",
                mime="text/markdown"
            )

    fragment_flashcards()

# ----------------- TAB 2 (Fragmented) -----------------
with tab2:
    @st.fragment
    def render_quiz_tab():
        import re
        st.subheader("🎯 Assessment Quiz")
        st.caption("Test your conceptual retention with diagnostic multiple-choice questions.")

        col_btn, _ = st.columns([2, 5])
        with col_btn:
            generate_quiz = st.button("Generate Practice Quiz", use_container_width=True, type="primary")

        if generate_quiz:
            study_text = get_active_study_text()
            if not study_text.strip():
                st.warning("Please upload a PDF or enter notes first.")
                return

            task_prompt = (
                "Generate a diagnostic multiple-choice practice quiz based strictly on the source material.\n\n"
                "Strict Formatting Rules:\n"
                "1. Format each question title as a level 3 Markdown header:\n"
                "   ### Question 1: [Question text here]?\n\n"
                "2. Format EVERY option as an unordered Markdown bullet item on its OWN line. Do NOT combine them into a single line:\n"
                "   * **(A)** Option A text\n"
                "   * **(B)** Option B text\n"
                "   * **(C)** Option C text\n"
                "   * **(D)** Option D text\n\n"
                "3. Place a divider line '---' between questions.\n"
                "4. DO NOT print answers right under the questions.\n"
                "5. When all questions are finished, place this exact delimiter on an isolated line:\n"
                "   [[[ANSWER_KEY_SECTION]]]\n\n"
                "6. After the delimiter, format every answer on 3 separate lines with an extra blank line between them:\n\n"
                "   #### Question 1\n\n"
                "   **Correct Answer:** (B) [Option text here]\n\n"
                "   **Explanation:** [Detailed step-by-step conceptual rationale here]\n\n"
                "   ---\n\n"
            )

            with st.spinner("Compiling diagnostic quiz questions..."):
                try:
                    full_response = "".join(stream_study_engine(task_prompt, study_text))
                    st.session_state.quiz_content = full_response
                except Exception as e:
                    st.error(f"Generation error: {e}")

        # Render quiz
        if "quiz_content" in st.session_state and st.session_state.quiz_content:
            raw_quiz = st.session_state.quiz_content

            split_pattern = r"(\[\[\[ANSWER_KEY_SECTION\]\]\]|---+\s*ANSWER_KEY\s*---+|ANSWER_KEY:?)"
            parts = re.split(split_pattern, raw_quiz, maxsplit=1, flags=re.IGNORECASE)

            if len(parts) >= 3:
                questions_part = parts[0].strip()
                answers_part = parts[2].strip()

                st.markdown(questions_part)
                st.write("")

                # Custom CSS to enlarge the expander title font
                st.markdown(
                    """
                    <style>
                    div[data-testid="stExpander"] details summary p {
                        font-size: 1.15rem !important;
                        font-weight: 700 !important;
                        color: #1e293b !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )

                with st.expander("👁️ Reveal Answer Key & Detailed Solutions", expanded=False):
                    st.markdown("## 📋 Official Solutions & Rationales")
                    st.markdown(answers_part)
            else:
                st.markdown(raw_quiz)

    render_quiz_tab()

# ----------------- TAB 3 (Fragmented) -----------------
with tab3:
    st.subheader("📋 High-Yield Revision Digest")
    st.caption("Summaries organized with dedicated subsections per file.")

    @st.fragment
    def fragment_summary():
        if st.button("Generate Summary Digest", key="btn_summary"):
            if not get_active_study_text():
                st.warning("Please provide study material first.")
            else:
                task = (
                    "Generate a high-yield revision digest grouped strictly by each source.\n\n"
                    "Strict Structure:\n"
                    "1. For every source delimited by '=== SOURCE START: [Name] ===', create a header:\n"
                    "   '### 📋 Summary Digest: [Source Name]'\n"
                    "2. Provide key definitions, core formulas, and bulleted concepts specific to that source.\n"
                    "3. Keep each summary clean and distinct."
                )
                st.session_state.summary_res = st.write_stream(stream_study_engine(task, get_active_study_text()))
        elif st.session_state.summary_res:
            st.markdown(st.session_state.summary_res)

        if st.session_state.summary_res:
            st.download_button(
                label="📥 Download Summary Digest (.md)",
                data=st.session_state.summary_res,
                file_name="summary_digest.md",
                mime="text/markdown"
            )

    fragment_summary()

# ----------------- TAB 4: Instant Doubt Resolution -----------------
with tab4:
    st.subheader("💡 Instant Doubt Resolution")
    st.caption("Ask any question from your notes or general computer science topics. Press **Enter** or click the send button.")

    @st.fragment
    def fragment_doubt():
        col_input, col_btn = st.columns([11, 1], vertical_alignment="bottom")

        with col_input:
            doubt_query = st.text_input(
                "Ask your doubt:",
                placeholder="Ask any doubt or topic question (e.g., LeetCode prep, OS concepts)...",
                key="input_doubt_text",
                label_visibility="collapsed"
            )

        with col_btn:
            send_clicked = st.button("↑", key="btn_send_doubt", help="Send Query")

        study_context = get_active_study_text()

        # Execute only if there is a query and either the button was clicked or the input changed
        should_run = (doubt_query.strip() and send_clicked) or (
            doubt_query.strip() and doubt_query.strip() != st.session_state.last_doubt_query
        )

        if should_run:
            st.session_state.last_doubt_query = doubt_query.strip()

            context_clause = (
                f"Relevant Study Material Uploaded:\n{study_context}\n\n"
                if study_context
                else "No study material was uploaded by the student.\n\n"
            )

            task = (
                f"{context_clause}"
                f"Student Question: '{doubt_query.strip()}'\n\n"
                "Instructions:\n"
                "- If the question relates to the uploaded study material, ground your explanation in that content first.\n"
                "- If the question is outside the uploaded notes (general CS concepts, interview/coding prep, industry guidance), answer it thoroughly, accurately, and encouragingly as an expert computer science mentor.\n"
                "- Use clean bullet points, bold headers, and LaTeX math where applicable ($...$). Avoid repetitive filler."
            )

            with st.spinner("Analyzing and generating explanation..."):
                # Render via stream and capture the response
                st.session_state.qa_res = st.write_stream(stream_study_engine(task, ""))
        else:
            # Display previously generated answer only when not actively streaming
            if st.session_state.qa_res:
                st.markdown(st.session_state.qa_res)

    fragment_doubt()