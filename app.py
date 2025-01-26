import streamlit as st  # type: ignore
import pandas as pd  # type: ignore

# Title for the app
st.title("Progressive Lot Size and Adjusted Loss Support Calculator")

# Sidebar inputs for number of trades, commission, profit/loss, and target win per trade
num_trades = st.sidebar.slider(
    "Number of Trades", min_value=1, max_value=20, value=11)
commission_per_lot = st.sidebar.number_input(
    "Commission per 1 Lot (in $)", min_value=0.0, value=1.5, step=0.1)
profit_per_0_01_lot = st.sidebar.number_input(
    "Profit per 0.01 Lot (in $)", min_value=0.01, value=1.2, step=0.1)
loss_per_0_01_lot = st.sidebar.number_input(
    "Loss per 0.01 Lot (in $)", min_value=0.01, value=1.0, step=0.1)
target_win_per_trade = st.sidebar.number_input(
    "Target Win per Trade (in $)", min_value=0.0, value=1.0, step=0.1)

# Description for Progressive Lot Size Table
st.write(f"""
### Progressive Lot Size Calculation
This table shows the progression of lot sizes required for a strategy where:
- Each win after a sequence of losses recovers all previous losses and ensures a net cumulative profit of **${target_win_per_trade} × Trade Number**.
- Commission is **${commission_per_lot}** per 1 lot per trade.
- Profit without commission is ±**${profit_per_0_01_lot}** per 0.01 lot.
- Loss without commission is ±**${loss_per_0_01_lot}** per 0.01 lot.
- Thus, net profit if win on L lots = ({profit_per_0_01_lot * 100 - commission_per_lot}) × L dollars.
- Net loss if lose on L lots = (-{loss_per_0_01_lot * 100 + commission_per_lot}) × L dollars.

**Key formula:**
After (n-1) losses with cumulative loss \( C_(n-1) \), the nth trade lot size \( L_n \) must satisfy:
`({profit_per_0_01_lot * 100 - commission_per_lot}) × L_n = (n × {target_win_per_trade}) - C_(n-1)`
""")

# Initialize variables for Progressive Lot Size Calculation
cumulative_loss = 0.0
data = []

for n in range(1, num_trades + 1):
    # Calculate lot size for nth trade
    L_n = ((n * target_win_per_trade) - cumulative_loss) / \
        (profit_per_0_01_lot * 100 - commission_per_lot)

    # Calculate outcomes
    win_amount = (profit_per_0_01_lot * 100 - commission_per_lot) * L_n
    lose_amount = -(loss_per_0_01_lot * 100 + commission_per_lot) * L_n

    # If this trade loses, update cumulative loss
    hypothetical_cumulative_loss = cumulative_loss + lose_amount

    # Store data for display
    data.append({
        "Trade #": n,
        "Desired Total Profit if Win": f"${target_win_per_trade * n:.2f}",
        "Lot Size (L)": round(L_n, 5),
        "If Win": f"${win_amount:,.4f}",
        "Cumulative Profit if Win at This Trade": f"${target_win_per_trade * n:.2f}",
        "If Lose": f"${lose_amount:,.4f}",
        "Cumulative Loss if Lose": f"${hypothetical_cumulative_loss:,.4f}"
    })

    # Update cumulative_loss for the next iteration calculation
    cumulative_loss = hypothetical_cumulative_loss

# Convert to DataFrame for Progressive Lot Size Calculation
df = pd.DataFrame(data)

# Display the Progressive Lot Size Table
st.subheader("Progressive Lot Size Table")
st.table(df)

# Description for Adjusted Loss Support Table
st.write("""
### Adjusted Plan Loss Support Table with Lot Size for Last Trade
This table calculates:
- The adjusted number of consecutive losses each account plan can support (deducting one loss for safety).
- **8%**, **5%**, and **13%** of the account size.
- The **lot size in the last supported trade** before reaching the maximum loss limit.
""")

# Define account plans for Adjusted Loss Support Table
plans = [
    {"Account Size": 6000, "Max Overall Loss": 600},
    {"Account Size": 15000, "Max Overall Loss": 1500},
    {"Account Size": 25000, "Max Overall Loss": 2500},
    {"Account Size": 50000, "Max Overall Loss": 5000},
    {"Account Size": 100000, "Max Overall Loss": 10000},
    {"Account Size": 200000, "Max Overall Loss": 20000},
]


def calculate_loss_support_with_last_lot(plans):
    results = []

    for plan in plans:
        cumulative_loss = 0.0
        max_loss = plan["Max Overall Loss"]
        losses_supported = 0
        last_trade_lot_size = 0.0

        # Simulate losses until exceeding the maximum loss limit
        for n in range(1, 100):  # Simulate a maximum of 100 trades
            # Calculate lot size for nth trade
            L_n = ((n * target_win_per_trade) - cumulative_loss) / \
                (profit_per_0_01_lot * 100 - commission_per_lot)

            # Calculate loss for this trade
            lose_amount = -(loss_per_0_01_lot * 100 + commission_per_lot) * L_n

            # Update cumulative loss
            cumulative_loss += lose_amount

            # Track the lot size for the last supported trade
            if cumulative_loss <= -max_loss:
                losses_supported = n - 1  # Last trade before exceeding the limit
                break
            last_trade_lot_size = L_n

        # Deduct one loss for safety
        adjusted_losses_supported = max(losses_supported - 1, 0)

        # Calculate percentages
        eight_percent = 0.08 * plan["Account Size"]
        five_percent = 0.05 * plan["Account Size"]
        thirteen_percent = 0.13 * plan["Account Size"]

        # Add the results for the plan
        results.append({
            "Account Size": f"${plan['Account Size']:,}",
            "Max Overall Loss": f"${plan['Max Overall Loss']:,}",
            "Losses Supported (Adjusted)": adjusted_losses_supported,
            "8% of Account Size": f"${eight_percent:,.2f}",
            "5% of Account Size": f"${five_percent:,.2f}",
            "13% of Account Size": f"${thirteen_percent:,.2f}",
            "Lot Size in Last Trade": round(last_trade_lot_size, 5)
        })

    return pd.DataFrame(results)


# Generate the Adjusted Loss Support Table with Last Trade Lot Size
adjusted_table_with_last_lot = calculate_loss_support_with_last_lot(plans)

# Display the Adjusted Loss Support Table with Lot Size for Last Trade
st.subheader("Adjusted Plan Loss Support Table with Lot Size for Last Trade")
st.table(adjusted_table_with_last_lot)

# Allow users to download the Adjusted Loss Support Table with Lot Size for Last Trade
csv = adjusted_table_with_last_lot.to_csv(index=False)
st.download_button(
    label="Download Adjusted Table with Lot Size for Last Trade as CSV",
    data=csv,
    file_name="adjusted_loss_support_with_last_lot.csv",
    mime="text/csv"
)
