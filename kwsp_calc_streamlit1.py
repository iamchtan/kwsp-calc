import streamlit as st
from datetime import datetime, timedelta
import pandas as pd  # Added for displaying the withdrawal schedule as a table

# Streamlit UI
st.title("KWSP Retirement Calculator")
st.write("Calculate your KWSP maximum starting monthly withdrawal amount to deplete your savings over a specified period.")
st.write("Yearly increments are based on the inflation rate entered to counter its effects.")

# Input fields
initial_balance = st.number_input("Initial Balance (RM)", min_value=0.0, value=1300000.0, step=1000.0)
dividend_rate = st.number_input("Annual Dividend Rate (%)", min_value=0.0, value=5.2, step=0.1) / 100
inflation_rate = st.number_input("Annual Inflation Rate (%)", min_value=0.0, value=5.0, step=0.1) / 100
years = st.number_input("Time Period (Years)", min_value=1, value=20, step=1)

# Calculate button
if st.button("Calculate Max Starting Withdrawal"):
    # Validate inputs
    if initial_balance <= 0 or years <= 0:
        st.error("Initial balance and years must be positive.")
    elif dividend_rate < 0 or inflation_rate < 0:
        st.error("Dividend and inflation rates must be non-negative.")
    else:
        # Calculate days
        start_date = datetime(2025, 1, 1)
        end_date = start_date + timedelta(days=365 * years + years // 4 + 1)
        days = (end_date - start_date).days
        target_balance = 0
        tolerance = 100

        # Function to calculate final balance
        def calculate_final_balance(start_withdrawal):
            withdrawal_schedule = {year: start_withdrawal * (1 + inflation_rate)**(year - 1) for year in range(1, years + 1)}
            def get_monthly_withdrawal(year):
                return withdrawal_schedule.get(year, start_withdrawal * (1 + inflation_rate)**(year - 1))

            balance = initial_balance
            current_date = start_date
            daily_balance_sum = 0
            days_in_year = 0
            current_year = 1

            for day in range(days):
                current_date = start_date + timedelta(days=day)
                year = min(current_date.year - 2024, years)
                withdrawal = 0
                if current_date.day == (current_date + timedelta(days=1)).replace(day=1).day:
                    withdrawal = get_monthly_withdrawal(year)
                    balance -= withdrawal
                daily_balance_sum += balance
                days_in_year += 1
                if current_date.month == 12 and current_date.day == 31 and year <= years:
                    dividend = (daily_balance_sum / days_in_year) * dividend_rate
                    balance += dividend
                    daily_balance_sum = 0
                    days_in_year = 0
                    current_year += 1
            return balance

        # Binary search for max starting withdrawal
        low = 100
        high = initial_balance / (12 * years) * 2
        max_iterations = 100
        start_withdrawal = 0
        for _ in range(max_iterations):
            mid = (low + high) / 2
            final_balance = calculate_final_balance(mid)
            if abs(final_balance - target_balance) < tolerance:
                start_withdrawal = mid
                break
            elif final_balance > target_balance:
                low = mid
            else:
                high = mid

        # Final calculation for details
        withdrawal_schedule = {year: start_withdrawal * (1 + inflation_rate)**(year - 1) for year in range(1, years + 1)}
        balance = initial_balance
        current_date = start_date
        daily_balance_sum = 0
        days_in_year = 0
        yearly_dividends = []
        current_year = 1

        for day in range(days):
            current_date = start_date + timedelta(days=day)
            year = min(current_date.year - 2024, years)
            withdrawal = 0
            if current_date.day == (current_date + timedelta(days=1)).replace(day=1).day:
                withdrawal = withdrawal_schedule.get(year, start_withdrawal * (1 + inflation_rate)**(year - 1))
                balance -= withdrawal
            daily_balance_sum += balance
            days_in_year += 1
            if current_date.month == 12 and current_date.day == 31 and year <= years:
                dividend = (daily_balance_sum / days_in_year) * dividend_rate
                balance += dividend
                yearly_dividends.append(dividend)
                daily_balance_sum = 0
                days_in_year = 0
                current_year += 1

        final_balance = balance
        total_withdrawals = sum(withdrawal_schedule[year] * 12 for year in range(1, years + 1))
        total_dividends = sum(yearly_dividends)

        # Display results
        st.success(f"**Results**")
        st.write(f"Initial Balance: RM {initial_balance:,.2f}")
        st.write(f"Dividend Rate: {dividend_rate*100:.2f}%")
        st.write(f"Inflation Rate: {inflation_rate*100:.2f}%")
        st.write(f"Time Period: {years} years")
        st.write(f"**Maximum Starting Monthly Withdrawal**: RM {start_withdrawal:,.2f}")
        st.write(f"**Final Balance**: RM {final_balance:,.2f}")
        st.write(f"**Total Withdrawals**: RM {total_withdrawals:,.2f}")
        st.write(f"**Total Dividends**: RM {total_dividends:,.2f}")

        # Display Annual Withdrawal Schedule
        st.write("**Annual Withdrawal Schedule**")
        schedule_data = []
        for year in range(1, years + 1):
            monthly_amount = withdrawal_schedule[year]
            annual_amount = monthly_amount * 12
            schedule_data.append({
                "Year": year,
                "Monthly Withdrawal (RM)": f"{monthly_amount:,.2f}",
                "Annual Withdrawal (RM)": f"{annual_amount:,.2f}"
            })
        schedule_df = pd.DataFrame(schedule_data)
        st.table(schedule_df)