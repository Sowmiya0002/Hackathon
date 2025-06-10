import streamlit as st
import google.generativeai as genai
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt  # Added import for matplotlib.pyplot

# Custom CSS for modern UI
st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #e0eafc, #cfdef3);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stApp {
        background: transparent;
    }
    .card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .title {
        color: #2c3e50;
        font-size: 2.5em;
        text-align: center;
        margin-bottom: 20px;
    }
    .subtitle {
        color: #34495e;
        font-size: 1.5em;
        margin-top: 20px;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
    .stSelectbox, .stNumberInput, .stSlider {
        background: #f7f9fc;
        border-radius: 10px;
        padding: 10px;
    }
   arrow: #ffffff;
    </style>
""", unsafe_allow_html=True)

# Configure the API key
genai.configure(api_key="AIzaSyCYZdy-q6TuvRFJP4XN8LSqWQsr4Yehwpg")

st.markdown("<div class='title'>Financial Goal Planner</div>", unsafe_allow_html=True)
st.write("Plan your financial future with ease! Enter your details to get a personalized savings plan.")

# Input fields in a card
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        goal = st.selectbox("🎯 Select your financial goal:", ["Retirement Planning", "Saving for a House", "Saving for a Car", "Gold Savings", "Marriage Saving", "Other"])
        if goal == "Other":
            custom_goal = st.text_input("Please specify your goal:")
        else:
            custom_goal = goal
        age = st.number_input("👤 Your age:", min_value=18, max_value=100, value=30)
    with col2:
        target_amount = st.number_input("💰 Target amount:", min_value=0.0, value=100000.0, step=1000.0)
        time_frame = st.slider("⏳ Time frame (years):", min_value=1, max_value=50, value=10)
        monthly_savings = st.number_input("💸 Monthly savings:", min_value=0.0, value=1000.0, step=100.0)
    st.markdown("</div>", unsafe_allow_html=True)

# Button to generate plan
if st.button("Generate Your Plan"):
    with st.spinner("Generating your financial plan..."):
        # Craft the prompt
        prompt = f"""You are a financial planner. The user has the following goal: {custom_goal}. They are {age} years old, can save {monthly_savings} per month for {time_frame} years to achieve a target of {target_amount}. Please provide:

        1. A tailored savings plan, including whether the current savings are sufficient or how much more is needed.
        2. Investment suggestions to reach the goal.
        3. A budget breakdown if applicable (e.g., percentage for savings, expenses, investments).
        4. Explain why this plan is suitable for the user's situation.
        5. Provide alternative plans or additional investment suggestions for better returns or risk management.

        Please be detailed and provide specific numbers where possible."""

        try:
            # Generate the response
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            response_text = response.text

            # Parse the response for structured data
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

            # Tabs for dashboard
            tab1, tab2, tab3 = st.tabs(["📋 Your Plan", "📊 Visualizations", "🔍 Details"])
            
            with tab1:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='subtitle'>Your Personalized Plan</div>", unsafe_allow_html=True)
                st.write(f"**Goal:** {custom_goal}")
                st.write(f"**Target Amount:** ${target_amount:,.2f}")
                st.write(f"**Time Frame:** {time_frame} years")
                st.write(f"**Monthly Savings:** ${monthly_savings:,.2f}")
                st.markdown("#### Savings Plan")
                st.write(savings_plan)
                st.markdown("#### Investment Suggestions")
                st.write(investment_suggestions)
                st.markdown("</div>", unsafe_allow_html=True)

            with tab2:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                # Savings Growth Chart
                st.markdown("<div class='subtitle'>Savings Growth Over Time</div>", unsafe_allow_html=True)
                interest_rate = 0.05  # Assuming 5% annual interest
                months = time_frame * 12
                future_value = 0
                savings_over_time = []
                for month in range(1, months + 1):
                    future_value = future_value * (1 + interest_rate / 12) + monthly_savings
                    if month % 12 == 0:
                        savings_over_time.append(future_value)
                years = list(range(1, time_frame + 1))
                df = pd.DataFrame({"Year": years, "Savings": savings_over_time})
                st.line_chart(df.set_index("Year"))
                st.write("**Note:** Assumes a 5% annual interest rate compounded monthly.")

                # Budget Breakdown Pie Chart
                if budget_found and sum(budget_data.values()) > 0:
                    st.markdown("<div class='subtitle'>Budget Breakdown</div>", unsafe_allow_html=True)
                    budget_df = pd.DataFrame.from_dict(budget_data, orient="index", columns=["Percentage"])
                    fig, ax = plt.subplots(figsize=(6, 6))
                    ax.pie(budget_df["Percentage"], labels=budget_df.index, autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99'])
                    st.pyplot(fig)
                else:
                    st.write("Budget breakdown not available or incomplete in the response.")

                # Plan Comparison Bar Chart
                st.markdown("<div class='subtitle'>Plan Comparison</div>", unsafe_allow_html=True)
                recommended_savings = future_value
                alternative_savings = recommended_savings * 1.1  # Assume alternative plan yields 10% more
                comparison_df = pd.DataFrame({
                    "Plan": ["Recommended Plan", "Alternative Plan"],
                    "Total Savings": [recommended_savings, alternative_savings]
                })
                st.bar_chart(comparison_df.set_index("Plan"))
                st.write("**Note:** Alternative plan assumes a 10% higher return for comparison.")
                st.markdown("</div>", unsafe_allow_html=True)

            with tab3:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='subtitle'>Additional Details</div>", unsafe_allow_html=True)
                st.markdown("#### Why This Plan?")
                st.write(reasoning)
                st.markdown("#### Alternative Plans")
                st.write(alternatives)
                st.markdown("#### Budget Breakdown")
                st.write(budget_breakdown)
                st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred: {e}")

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.write("**Disclaimer:** The suggestions provided are generated by an AI model and should not be considered as professional financial advice. Please consult with a qualified financial advisor before making any investment decisions.")
st.markdown("</div>", unsafe_allow_html=True)
