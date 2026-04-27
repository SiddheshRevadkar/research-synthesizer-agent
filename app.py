"""
Streamlit UI for Research Agent (FINAL VERSION)
"""

import streamlit as st
import httpx
import time
import io
import json
import re
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- CONFIG ----------------

st.set_page_config(page_title="Research Synthesizer Agent", layout="wide")

HISTORY_FILE = "history.json"

# ---------------- HISTORY FUNCTIONS ----------------

def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_history(topic):
    history = load_history()

    history.append({
        "topic": topic,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

# ---------------- PDF FUNCTION ----------------

def generate_pdf(report_text: str):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = []

    for line in report_text.split("\n"):
        if line.strip():
            elements.append(Paragraph(line, styles["Normal"]))
            elements.append(Spacer(1, 10))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------------- ANALYTICS FUNCTION ----------------

def analyze_text(report: str):
    words = re.findall(r'\w+', report.lower())

    stopwords = set([
        "the", "is", "in", "and", "to", "of", "a", "for", "on", "with",
        "as", "by", "an", "are", "at", "from", "that", "this"
    ])

    filtered = [w for w in words if w not in stopwords and len(w) > 3]

    word_count = len(words)
    common_words = Counter(filtered).most_common(5)

    return word_count, common_words

# ---------------- UI ----------------

st.title("🔍 Research Synthesizer Agent")

# Sidebar
st.sidebar.header("🕘 History")

history = load_history()

for item in reversed(history[-5:]):
    st.sidebar.write(f"{item['time']} — {item['topic']}")

# Input
topic = st.text_input(
    "Enter Research Topic",
    placeholder="e.g. Artificial Intelligence in Healthcare"
)

# Button
if st.button("Generate Report"):

    if not topic.strip():
        st.warning("⚠️ Please enter a valid topic")
    else:
        with st.spinner("🔍 Researching deeply... please wait..."):
            start = time.time()

            try:
                response = httpx.post(
                    "http://127.0.0.1:8000/research",
                    json={"topic": topic},
                    timeout=120
                )

                data = response.json()

                if "error" in data:
                    st.error(f"❌ {data['error']}")
                else:
                    # Save history
                    save_history(topic)

                    # Report
                    st.markdown("## 📄 Research Report")
                    st.markdown(data["report"])

                    # PDF Download
                    pdf_file = generate_pdf(data["report"])
                    st.download_button(
                        label="📥 Download Report as PDF",
                        data=pdf_file,
                        file_name="research_report.pdf",
                        mime="application/pdf"
                    )

                    # Sources
                    if data.get("sources"):
                        st.markdown("## 🔗 Sources")
                        for src in data["sources"]:
                            st.markdown(f"- [{src}]({src})")

                    # ----------- ANALYTICS -----------

                    st.markdown("## 📊 Insights & Analysis")

                    try:
                        word_count, common_words = analyze_text(data["report"])

                        st.write(f"📝 Total Words: {word_count}")

                        if common_words:
                            labels = [w[0] for w in common_words]
                            values = [w[1] for w in common_words]

                            fig, ax = plt.subplots()
                            ax.bar(labels, values)
                            ax.set_title("Top Keywords")

                            st.pyplot(fig)

                    except Exception as e:
                        st.warning(f"Analytics error: {str(e)}")

                    # Time
                    st.success(f"⏱ Completed in {round(time.time() - start, 2)} seconds")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")