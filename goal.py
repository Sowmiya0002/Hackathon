import streamlit as st
import google.generativeai as genai
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import plotly.express as px

# Custom CSS for responsive, full-width design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    body {
        background: linear-gradient(to right, #ffafbd, #ffc3a0);
        font-family: 'Poppins', sans-serif;
        margin: 0;
        padding: 0;
    }
    .stApp {
        background: transparent;
        padding: 0 !important;
        margin: 0 !important;
        width: 100vw !important;
        max-width: 100% !important;
        overflow-x: hidden;
    }
    .main-container {
        width: 100%;
        max-width: 100%;
        padding: 20px;
        box-sizing: border-box;
        border-radius: 10px;
    }
    .card {
        background: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
        margin-bottom: 15px;
    }
    .card:hover {
        transform: scale(1.02);
    }
    .title {
        color: #ff6f61;
        font-size: 2.2em;
        text-align: center;
        margin-bottom: 20px;
        font-weight: 600;
    }
    .subtitle {
        color: #ff6f61;
        font-size: 1.3em;
        margin-top: 10px;
        font-weight: 600;
    }
    .stButton>button {
        background-color: #40c4ff;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 14px;
        transition: background-color 0.2s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #0288d1;
    }
    .stSelectbox, .stNumberInput, .stSlider, .stTextInput {
        background: #f5f5f5;
        border-radius: 8px;
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #ff6f61;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #0288d1;
        border-bottom: 2px solid #0288d1;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding: 0 !important;
    }
    /* Responsive Design */
    @media (max-width: 768px) {
        .stApp {
            padding: 0 !important;
        }
        .main-container {
            padding: 10px;
        }
        .title {
            font-size: 1.8em;
            margin-bottom: 15px;
        }
        .subtitle {
            font-size: 1.1em;
        }
        .card {
            padding: 10px;
            margin-bottom: 10px;
        }
        .stButton>button {
            font-size: 12px;
            padding: 6px 12px;
        }
        .stSelectbox, .stNumberInput, .stSlider, .stTextInput {
            font-size: 14px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Configure the API key
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Please set the GEMINI_API_KEY in Streamlit secrets.")
    st.stop()
else:
    genai.configure(api_key="AIzaSyCYZdy-q6TuvRFJP4XN8LSqWQsr4Yehwpg")

# Main container for full-width layout
with st.container():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.markdown("<div class='title'>Financial Goal Planner</div>", unsafe_allow_html=True)

    # Two-column layout (responsive)
    col1, col2 = st.columns([1, 2])

    # Left column: Input fields
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='subtitle'>Your Goals</div>", unsafe_allow_html=True)
        goal = st.selectbox("🎯 Goal:", ["Retirement", "House", "Car", "Gold", "Marriage", "Other"])
        if goal == "Other":
            custom_goal = st.text_input("Specify Goal:")
        else:
            custom_goal = goal
        age = st.number_input("👤 Age:", min_value=18, max_value=100, value=30)
        target_amount = st.number_input("💰 Target ($):", min_value=0.0, value=100000.0, step=1000.0)
        time_frame = st.slider("⏳ Years:", min_value=1, max_value=50, value=10)
        monthly_savings = st.number_input("💸 Monthly ($):", min_value=0.0, value=1000.0, step=100.0)
        if st.button("Plan Now"):
            st.session_state["plan_generated"] = True
        st.markdown("</div>", unsafe_allow_html=True)

    # Right column: Tabbed container
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["📊 Visualizations", "📋 Plan", "🔍 Details"])
        
        if "plan_generated" not in st.session_state or not st.session_state["plan_generated"]:
            with tab1:
                st.write("Enter your details and click 'Plan Now' to see your visualizations!")
        else:
            with st.spinner("Crafting your plan..."):
                # Craft the prompt
                prompt = f"""You are a financial planner. The user has the goal: {custom_goal}. They are {age} years old, can save {monthly_savings} per month for {time_frame} years to reach {target_amount}. Provide:

                1. A savings plan (is the current savings enough?).
                2. Investment ideas.
                3. Budget breakdown (e.g., savings, expenses, investments percentages).
                4. Why this plan suits the user.
                5. Alternative plans or investment options.

                Keep responses concise with specific numbers."""

                try:
                    # Generate the response
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    response = model.generate_content(prompt)
                    response_text = response.text

                    # Parse the response
                    savings_plan = response_text.split("1.")[1].split("2.")[0].strip() if "1." in response_text else "Not provided."
                    investment_suggestions = response_text.split("2.")[1].split("3.")[0].strip() if "2." in response_text and "3." in response_text else "Not provided."
                    budget_breakdown = response_text.split("3.")[1].split("4.")[0].strip() if "3." in response_text and "4." in response_text else "Not provided."
                    reasoning = response_text.split("4.")[1].split("5.")[0].strip() if "4." in response_text and "5." in response_text else "Not provided."
                    alternatives = response_text.split("5.")[1].strip() if "5." in response_text else "Not provided."

                    # Extract budget percentages for pie chart
                    budget_data = {"Savings": 0, "Expenses": 0, "Investments": 0}
                    budget_found = False
                    if budget_breakdown != "Not provided.":
                        for line in budget_breakdown.split("\n"):
                            if "Savings" in line:
                                match = re.search(r"(\d+)%", line)
                                if match:
                                    budget_data["Savings"] = int(match.group(1))
                                    budget_found = True
                            elif "Expenses" in line:
                                match = re.search(r"(\d+)%", line)
                                if match:
                                    budget_data["Expenses"] = int(match.group(1))
                                    budget_found = True
                            elif "Investments" in line:
                                match = re.search(r"(\d+)%", line)
                                if match:
                                    budget_data["Investments"] = int(match.group(1))
                                    budget_found = True

                    # Calculate savings growth for Plotly chart
                    interest_rate = 0.05
                    months = time_frame * 12
                    future_value = 0
                    savings_over_time = []
                    for month in range(1, months + 1):
                        future_value = future_value * (1 + interest_rate / 12) + monthly_savings
                        if month % 12 == 0:
                            savings_over_time.append(future_value)
                    years = list(range(1, time_frame + 1))
                    df = pd.DataFrame({"Year": years, "Savings": savings_over_time})

                    # Visualizations Tab (Default)
                    with tab1:
                        # Interactive Savings Growth Chart
                        st.markdown("<div class='subtitle'>Savings Growth</div>", unsafe_allow_html=True)
                        fig = px.line(df, x="Year", y="Savings", title="", 
                                      labels={"Savings": "Amount ($)"},
                                      color_discrete_sequence=["#ff6f61"])
                        fig.update_layout(showmode="overlay", paper_bgcolor="rgba(0,0,0,0)", 
                                          plot_bgcolor="rgba(0,0,0,0)", 
                                          xaxis_title="Year", yaxis_title="Savings ($)")
                        st.plotly_chart(fig, use_container_width=True)
                        st.write("*5% annual interest, compounded monthly.")

                        # Budget Breakdown Pie Chart
                        if budget_found and sum(budget_data.values()) > 0:
                            st.markdown("<div class='subtitle'>Budget Split</div>", unsafe_allow_html=True)
                            budget_df = pd.DataFrame.from_dict(budget_data, orient="index", columns=["Percentage"])
                            fig, ax = plt.subplots(figsize=(5, 5))
                            ax.pie(budget_df["Percentage"], labels=budget_df.index, autopct='%1.0f%%', 
                                   colors=['#ff9999', '#66b3ff', '#99ff99'])
                            st.pyplot(fig)
                        else:
                            st.write("No budget breakdown available.")

                        # Plan Comparison Bar Chart
                        st.markdown("<div class='subtitle'>Plan Comparison</div>", unsafe_allow_html=True)
                        recommended_savings = future_value
                        alternative_savings = recommended_savings * 1.1
                        comparison_df = pd.DataFrame({
                            "Plan": ["Recommended", "Alternative"],
                            "Total Savings": [recommended_savings, alternative_savings]
                        })
                        fig = px.bar(comparison_df, x="Plan", y="Total Savings", 
                                     color="Plan", color_discrete_map={"Recommended": "#40c4ff", "Alternative": "#ffca28"})
                        fig.update_layout(showmode="overlay", paper_bgcolor="rgba(0,0,0,0)", 
                                          plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Savings ($)")
                        st.plotly_chart(fig, use_container_width=True)
                        st.write("*Alternative assumes 10% higher return.")

                    # Plan Tab
                    with tab2:
                        st.markdown("<div class='subtitle'>Your Plan</div>", unsafe_allow_html=True)
                        st.write(f"**Goal:** {custom_goal}")
                        st.write(f"**Target:** ${target_amount:,.0f}")
                        st.write(f"**Savings Plan:** {savings_plan[:100]}...")
                        st.write(f"**Investments:** {investment_suggestions[:100]}...")

                    # Details Tab
                    with tab3:
                        st.markdown("<div class='subtitle'>Details</div>", unsafe_allow_html=True)
                        st.write(f"**Why This Plan?** {reasoning[:100]}...")
                        st.write(f"**Alternatives:** {alternatives[:100]}...")
                        st.write(f"**Budget:** {budget_breakdown[:100]}...")

                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    # Disclaimer
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("**Disclaimer:** AI-generated advice. Consult a financial advisor.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
