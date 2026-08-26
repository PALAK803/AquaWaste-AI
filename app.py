import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

# ============================================================
# AQUAWASTE AI
# AI-Powered Water & Waste Management Assistant
# ============================================================

st.set_page_config(
    page_title="AquaWaste AI",
    page_icon="💧",
    layout="wide"
)

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 700;
}
.subtitle {
    font-size: 20px;
}
.card {
    padding: 20px;
    border-radius: 12px;
    background-color: #f5f7fa;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA
# ============================================================

@st.cache_data
def create_water_data():

    usage = [
        420, 435, 410, 450, 440, 460, 455,
        430, 445, 425, 450, 470, 465, 480,
        455, 460, 475, 490, 485, 500, 495,
        510, 520, 505, 515, 525, 530, 900
    ]

    dates = pd.date_range(
        end=pd.Timestamp.today(),
        periods=len(usage),
        freq="D"
    )

    data = pd.DataFrame({
        "Date": dates,
        "Water Usage (Liters)": usage,
        "Household Members": [4] * len(usage)
    })

    return data


@st.cache_data
def create_waste_data():

    data = pd.DataFrame({
        "Waste Category": [
            "Organic",
            "Plastic",
            "Paper",
            "Glass",
            "Metal",
            "E-Waste"
        ],
        "Quantity (kg)": [
            12,
            6,
            4,
            3,
            2,
            1
        ]
    })

    return data


water_df = create_water_data()
waste_df = create_waste_data()


# ============================================================
# WASTE KNOWLEDGE BASE
# ============================================================

waste_database = {

    "plastic bottle": {
        "category": "Plastic / Recyclable",
        "recommendation":
            "Empty and rinse the bottle where appropriate, "
            "then use the local plastic or recycling collection stream."
    },

    "plastic bag": {
        "category": "Plastic",
        "recommendation":
            "Avoid unnecessary single-use plastic and follow "
            "local plastic collection guidelines."
    },

    "newspaper": {
        "category": "Paper",
        "recommendation":
            "Keep paper clean and dry and place it in the "
            "appropriate paper/recycling collection stream."
    },

    "cardboard": {
        "category": "Paper / Cardboard",
        "recommendation":
            "Flatten clean cardboard and use the appropriate "
            "paper or cardboard recycling stream."
    },

    "banana peel": {
        "category": "Organic Waste",
        "recommendation":
            "Place it in an appropriate organic-waste or "
            "composting stream."
    },

    "food waste": {
        "category": "Organic Waste",
        "recommendation":
            "Use the appropriate organic-waste or composting stream."
    },

    "vegetable waste": {
        "category": "Organic Waste",
        "recommendation":
            "Use the appropriate organic-waste or composting stream."
    },

    "glass bottle": {
        "category": "Glass",
        "recommendation":
            "Handle carefully and use the appropriate glass "
            "collection or recycling stream."
    },

    "aluminium can": {
        "category": "Metal / Recyclable",
        "recommendation":
            "Empty the container and use the appropriate "
            "metal or recycling collection stream."
    },

    "battery": {
        "category": "Hazardous / E-Waste",
        "recommendation":
            "Do not place batteries in ordinary household waste. "
            "Use an authorized collection or recycling channel."
    },

    "mobile phone": {
        "category": "E-Waste",
        "recommendation":
            "Use an authorized e-waste collection or recycling channel."
    },

    "laptop": {
        "category": "E-Waste",
        "recommendation":
            "Use an authorized e-waste collection or recycling channel."
    }
}


# ============================================================
# WATER FUNCTIONS
# ============================================================

def calculate_water_metrics(data):

    total = data["Water Usage (Liters)"].sum()

    average = data["Water Usage (Liters)"].mean()

    latest = data.iloc[-1]["Water Usage (Liters)"]

    members = data.iloc[-1]["Household Members"]

    per_person = latest / members

    return total, average, latest, per_person


def detect_water_anomalies(data):

    model = IsolationForest(
        contamination=0.08,
        random_state=42
    )

    predictions = model.fit_predict(
        data[["Water Usage (Liters)"]]
    )

    result = data.copy()

    result["Anomaly"] = predictions == -1

    return result


def get_water_status(per_person):

    if per_person < 100:
        return "Low", "🟢"

    elif per_person <= 150:
        return "Moderate", "🟡"

    else:
        return "High", "🔴"


# ============================================================
# WASTE FUNCTIONS
# ============================================================

def analyze_waste_item(item):

    item = item.lower().strip()

    if item in waste_database:
        return waste_database[item]

    for key in waste_database:

        if key in item or item in key:
            return waste_database[key]

    return None


def calculate_waste_statistics():

    total = waste_df["Quantity (kg)"].sum()

    recyclable_categories = [
        "Plastic",
        "Paper",
        "Glass",
        "Metal"
    ]

    recyclable = waste_df[
        waste_df["Waste Category"].isin(recyclable_categories)
    ]["Quantity (kg)"].sum()

    percentage = (recyclable / total) * 100

    return total, recyclable, percentage


# ============================================================
# SUSTAINABILITY SCORE
# ============================================================

def calculate_sustainability_score():

    total, average, latest, per_person = calculate_water_metrics(
        water_df
    )

    total_waste, recyclable, recyclable_percentage = (
        calculate_waste_statistics()
    )

    # Illustrative project metric
    water_score = np.clip(
        100 - max(average - 120, 0) * 0.35,
        35,
        100
    )

    waste_score = np.clip(
        45 + recyclable_percentage * 0.55,
        35,
        100
    )

    overall_score = (
        water_score + waste_score
    ) / 2

    return (
        round(water_score),
        round(waste_score),
        round(overall_score),
        round(recyclable_percentage)
    )


# ============================================================
# AI ADVISOR
# ============================================================

def sustainability_advisor(question):

    question = question.lower()

    analyzed_data = detect_water_anomalies(water_df)

    recent_anomaly = analyzed_data.tail(7)["Anomaly"].any()

    total, average, latest, per_person = calculate_water_metrics(
        water_df
    )

    total_waste, recyclable, recyclable_percentage = (
        calculate_waste_statistics()
    )

    _, _, score, _ = calculate_sustainability_score()

    # WATER QUESTIONS

    if (
        "water" in question
        or "leak" in question
        or "consumption" in question
        or "usage" in question
    ):

        if recent_anomaly:

            return (
                "⚠️ **Unusual water consumption detected.**\n\n"
                f"Latest usage: **{latest:.0f} L**\n\n"
                f"Average usage: **{average:.0f} L/day**\n\n"
                "Possible reasons may include leakage, unusual "
                "household activity or a measurement issue.\n\n"
                "💡 **Recommendation:** Check taps, pipes, toilets "
                "and other water fixtures and continue monitoring "
                "daily consumption."
            )

        return (
            f"💧 Your average water consumption is "
            f"**{average:.0f} L/day**.\n\n"
            f"Latest per-person usage is approximately "
            f"**{per_person:.1f} L/person/day**.\n\n"
            "Continue monitoring daily usage and investigate "
            "sudden increases."
        )

    # WASTE QUESTIONS

    if (
        "waste" in question
        or "plastic" in question
        or "recycle" in question
    ):

        return (
            f"♻️ Total tracked waste is **{total_waste:.1f} kg**.\n\n"
            f"Approximately **{recyclable_percentage}%** belongs "
            "to the recyclable categories tracked by this prototype.\n\n"
            "💡 Focus on reducing avoidable waste and correctly "
            "segregating organic, recyclable and e-waste streams."
        )

    # SCORE QUESTIONS

    if (
        "score" in question
        or "sustainable" in question
        or "improve" in question
    ):

        return (
            f"🌱 Your current sustainability score is "
            f"**{score}/100**.\n\n"
            "To improve it:\n\n"
            "• Reduce unnecessary water consumption\n"
            "• Investigate unusual water usage\n"
            "• Reduce avoidable waste\n"
            "• Improve waste segregation\n"
            "• Increase responsible recycling"
        )

    return (
        "🤖 I can help you with:\n\n"
        "• Water consumption\n"
        "• Water anomalies\n"
        "• Waste management\n"
        "• Recycling\n"
        "• Sustainability score\n\n"
        "Try asking: **How can I reduce my water consumption?**"
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("💧 AquaWaste AI")
st.sidebar.caption(
    "AI-Powered Water & Waste Management Assistant"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "💧 Water Management",
        "♻️ Waste Management",
        "🤖 AI Sustainability Advisor",
        "📊 Analytics",
        "🌱 Sustainability Score",
        "ℹ️ About Project"
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="main-title">💧♻️ AquaWaste AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'AI-Powered Water & Waste Management Assistant'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        "A sustainability-focused prototype that combines "
        "water monitoring, machine-learning anomaly detection, "
        "waste management and intelligent recommendations."
    )

    st.divider()

    total, average, latest, per_person = (
        calculate_water_metrics(water_df)
    )

    total_waste, recyclable, recyclable_percentage = (
        calculate_waste_statistics()
    )

    _, _, score, _ = calculate_sustainability_score()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "💧 Total Water",
        f"{total:,.0f} L"
    )

    col2.metric(
        "📈 Average / Day",
        f"{average:,.0f} L"
    )

    col3.metric(
        "♻️ Total Waste",
        f"{total_waste:.1f} kg"
    )

    col4.metric(
        "🌱 Sustainability",
        f"{score}/100"
    )

    st.divider()

    analyzed = detect_water_anomalies(water_df)

    anomaly_count = analyzed["Anomaly"].sum()

    left, right = st.columns(2)

    with left:

        st.subheader("💧 Water Status")

        status, icon = get_water_status(per_person)

        st.write(
            f"{icon} **{status} water usage**"
        )

        st.write(
            f"Latest per-person consumption: "
            f"**{per_person:.1f} L/day**"
        )

        if anomaly_count > 0:

            st.warning(
                f"🚨 AI detected {anomaly_count} unusual "
                "water-consumption record(s)."
            )

    with right:

        st.subheader("♻️ Waste Status")

        st.write(
            f"Recyclable percentage: "
            f"**{recyclable_percentage}%**"
        )

        st.info(
            "Follow local waste collection and recycling "
            "guidelines for actual disposal."
        )

    st.divider()

    st.subheader("🤖 AI Insight")

    st.info(
        sustainability_advisor(
            "water consumption"
        )
    )


# ============================================================
# WATER MANAGEMENT
# ============================================================

elif page == "💧 Water Management":

    st.title("💧 Water Management")

    st.write(
        "Monitor water consumption and identify unusual "
        "usage patterns using machine learning."
    )

    total, average, latest, per_person = (
        calculate_water_metrics(water_df)
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total", f"{total:,.0f} L")
    col2.metric("Average", f"{average:,.0f} L/day")
    col3.metric("Latest", f"{latest:,.0f} L")
    col4.metric("Per Person", f"{per_person:.1f} L")

    st.subheader("📈 Water Consumption Trend")

    chart_data = water_df.set_index("Date")[
        ["Water Usage (Liters)"]
    ]

    st.line_chart(chart_data)

    st.subheader("🤖 AI Anomaly Detection")

    analyzed = detect_water_anomalies(water_df)

    anomalies = analyzed[
        analyzed["Anomaly"]
    ]

    if len(anomalies) > 0:

        st.warning(
            f"🚨 {len(anomalies)} unusual water-usage "
            "record(s) detected."
        )

        st.dataframe(
            anomalies,
            use_container_width=True
        )

    else:

        st.success(
            "🟢 No unusual patterns detected."
        )

    st.subheader("💡 Water Saving Recommendations")

    recommendations = [
        "Monitor water consumption daily.",
        "Check taps and pipes when sudden usage increases occur.",
        "Repair leaking fixtures promptly.",
        "Avoid unnecessary running water.",
        "Use water-efficient practices for cleaning and bathing."
    ]

    for recommendation in recommendations:

        st.write(
            "• " + recommendation
        )


# ============================================================
# WASTE MANAGEMENT
# ============================================================

elif page == "♻️ Waste Management":

    st.title("♻️ Waste Management")

    st.write(
        "Enter a waste item to receive a category and "
        "general disposal recommendation."
    )

    item = st.text_input(
        "Enter waste item",
        placeholder="Example: plastic bottle"
    )

    if st.button(
        "Analyze Waste",
        type="primary"
    ):

        if item.strip() == "":

            st.warning(
                "Please enter a waste item."
            )

        else:

            result = analyze_waste_item(item)

            if result:

                st.success(
                    f"Category: **{result['category']}**"
                )

                st.info(
                    "💡 " + result["recommendation"]
                )

            else:

                st.warning(
                    "This item is not currently available "
                    "in the prototype knowledge base."
                )

    st.divider()

    st.subheader("📊 Waste Composition")

    total_waste, recyclable, percentage = (
        calculate_waste_statistics()
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Waste",
        f"{total_waste:.1f} kg"
    )

    col2.metric(
        "Recyclable",
        f"{recyclable:.1f} kg"
    )

    col3.metric(
        "Recyclable %",
        f"{percentage:.0f}%"
    )

    st.bar_chart(
        waste_df.set_index(
            "Waste Category"
        )["Quantity (kg)"]
    )

    st.dataframe(
        waste_df,
        use_container_width=True
    )


# ============================================================
# AI ADVISOR
# ============================================================

elif page == "🤖 AI Sustainability Advisor":

    st.title("🤖 AI Sustainability Advisor")

    st.write(
        "Ask a sustainability-related question and "
        "receive a contextual recommendation based on "
        "the project's water and waste data."
    )

    question = st.text_area(
        "Ask your question",
        placeholder=(
            "Example: How can I reduce my water consumption?"
        )
    )

    if st.button(
        "Get AI Recommendation",
        type="primary"
    ):

        if question.strip() == "":

            st.warning(
                "Please enter a question."
            )

        else:

            response = sustainability_advisor(
                question
            )

            st.markdown("### Recommendation")

            st.info(response)

    st.subheader("Try asking:")

    st.write(
        "• Why is my water usage high?"
    )

    st.write(
        "• How can I reduce plastic waste?"
    )

    st.write(
        "• How can I improve my sustainability score?"
    )


# ============================================================
# ANALYTICS
# ============================================================

elif page == "📊 Analytics":

    st.title("📊 Sustainability Analytics")

    st.subheader("💧 Water Analytics")

    st.dataframe(
        water_df,
        use_container_width=True
    )

    st.line_chart(
        water_df.set_index("Date")[
            ["Water Usage (Liters)"]
        ]
    )

    st.subheader("♻️ Waste Analytics")

    st.bar_chart(
        waste_df.set_index(
            "Waste Category"
        )["Quantity (kg)"]
    )

    total_waste, recyclable, percentage = (
        calculate_waste_statistics()
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Total Waste",
        f"{total_waste:.1f} kg"
    )

    col2.metric(
        "Recyclable %",
        f"{percentage:.0f}%"
    )


# ============================================================
# SUSTAINABILITY SCORE
# ============================================================

elif page == "🌱 Sustainability Score":

    st.title("🌱 Sustainability Score")

    water_score, waste_score, overall, percentage = (
        calculate_sustainability_score()
    )

    st.metric(
        "Overall Sustainability Score",
        f"{overall}/100"
    )

    st.progress(
        overall / 100
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "💧 Water Score",
        f"{water_score}/100"
    )

    col2.metric(
        "♻️ Waste Score",
        f"{waste_score}/100"
    )

    st.divider()

    st.subheader(
        "How the score is calculated"
    )

    st.write(
        "The prototype combines a water-management "
        "component and a waste-management component."
    )

    st.write(
        f"💧 Water component: {water_score}/100"
    )

    st.write(
        f"♻️ Waste component: {waste_score}/100"
    )

    st.write(
        f"🔄 Tracked recyclable percentage: {percentage}%"
    )

    st.caption(
        "This is an illustrative project metric and "
        "not an official environmental rating."
    )


# ============================================================
# ABOUT
# ============================================================

elif page == "ℹ️ About Project":

    st.title("ℹ️ About AquaWaste AI")

    st.subheader("Project Objective")

    st.write(
        "AquaWaste AI is a sustainability-focused prototype "
        "designed to help users understand water-consumption "
        "patterns and improve waste-management practices."
    )

    st.subheader("🎯 SDG Alignment")

    st.write(
        "**Primary SDG:** SDG 6 — Clean Water and Sanitation"
    )

    st.write(
        "**Secondary SDG:** SDG 12 — Responsible Consumption "
        "and Production"
    )

    st.write(
        "**Related SDG:** SDG 11 — Sustainable Cities "
        "and Communities"
    )

    st.subheader("🤖 Where AI is Used")

    st.write(
        "1. Isolation Forest machine learning is used "
        "to identify unusual water-consumption patterns."
    )

    st.write(
        "2. A contextual recommendation engine provides "
        "sustainability guidance based on user questions "
        "and project data."
    )

    st.subheader("⚠️ Responsible AI")

    st.write(
        "The water data used in this prototype is "
        "demonstration data. An anomaly indicates an "
        "unusual pattern but does not prove that a leak "
        "exists. Waste recommendations are general guidance "
        "and should be checked against local rules."
    )

    st.subheader("🚀 Future Scope")

    st.write(
        "Future versions could connect real smart-water "
        "meters, municipal waste databases, local recycling "
        "rules, forecasting models and advanced AI assistants."
    )

    st.success(
        "AquaWaste AI — AI for Sustainability Internship Project"
    )
