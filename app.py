import streamlit as st
import plotly.express as px
import numpy as np
from functions.black_scholes import black_scholes, generate_price_matrix
from database.db_storage import (
    init_db,
    store_calculation,
    store_heatmap_data,
    get_calculations,
)

# Set page configuration
st.set_page_config(page_title="Black-Scholes Option Pricing Model", layout="wide")

# Initialize the database
try:
    init_db()
except Exception as e:
    st.sidebar.error(f"Database initialization error: {e}")

# Sidebar for calculation history
with st.sidebar:
    st.title("Calculation History")

    # Add option to refresh history
    if st.button("Refresh History"):
        try:
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error refreshing history: {e}")

    # Get calculation history from database
    try:
        history = get_calculations(limit=10)

        if not history:
            st.info(
                "No calculations yet. Use the CALCULATE button to save your first calculation."
            )
        else:
            for calc in history:
                with st.expander(
                    f"#{calc['id']} - S:{calc['spot_price']}, K:{calc['strike_price']}"
                ):
                    st.write(f"**Timestamp:** {calc['timestamp']}")
                    st.write(f"**Spot Price:** ${calc['spot_price']:.2f}")
                    st.write(f"**Strike Price:** ${calc['strike_price']:.2f}")
                    st.write(f"**Maturity:** {calc['time_to_maturity']:.2f} years")
                    st.write(f"**Volatility:** {calc['volatility']:.2f}")
                    st.write(f"**Risk-Free Rate:** {calc['risk_free_rate']:.2f}")
                    st.write(f"**Call Price:** ${calc['call_price']:.2f}")
                    st.write(f"**Put Price:** ${calc['put_price']:.2f}")
    except Exception as e:
        st.error(f"Failed to load history: {e}")

# Title and description
st.title("📊 Black-Scholes Option Pricing Model")
st.markdown("Created by: Kilo Code")

# Create a two-column layout for inputs
col1, col2 = st.columns([1, 2])

# Input parameters in the left column
with col1:
    st.subheader("Current Asset Price")
    S = st.number_input("", min_value=0.01, value=100.0, step=0.01, key="current_price")

    st.subheader("Strike Price")
    K = st.number_input("", min_value=0.01, value=100.0, step=0.01, key="strike_price")

    st.subheader("Time to Maturity (Years)")
    T = st.number_input("", min_value=0.01, value=1.0, step=0.01, key="maturity")

    st.subheader("Volatility (σ)")
    sigma = st.number_input("", min_value=0.01, value=0.25, step=0.01, key="volatility")

    st.subheader("Risk-Free Interest Rate")
    r = st.number_input("", min_value=0.0, value=0.05, step=0.01, key="interest_rate")

# Initialize session state for storing option prices
if "call_price" not in st.session_state:
    st.session_state.call_price = 0.0
if "put_price" not in st.session_state:
    st.session_state.put_price = 0.0
if "calculation_done" not in st.session_state:
    st.session_state.calculation_done = False

# Add a calculate button
if st.button("CALCULATE", type="primary"):
    # Calculate option prices
    st.session_state.call_price = black_scholes(S, K, T, r, sigma, "call")
    st.session_state.put_price = black_scholes(S, K, T, r, sigma, "put")
    st.session_state.calculation_done = True

    # Store calculation in database
    try:
        # Store the calculation
        calculation_id = store_calculation(
            spot_price=S,
            strike_price=K,
            time_to_maturity=T,
            volatility=sigma,
            risk_free_rate=r,
            call_price=st.session_state.call_price,
            put_price=st.session_state.put_price,
        )

        # Store the heatmap data
        # First, generate the heatmap data
        spot_steps = 20
        vol_steps = 20
        min_spot = max(0.8 * S, 0.01)
        max_spot = 1.2 * S
        min_vol = 0.1
        max_vol = 0.5

        # Generate matrices
        (
            spot_prices,
            volatilities,
            call_prices,
            put_prices,
            call_pnl_matrix,
            put_pnl_matrix,
        ) = generate_price_matrix(
            min_spot,
            max_spot,
            min_vol,
            max_vol,
            K,
            T,
            r,
            st.session_state.call_price,
            st.session_state.put_price,
            spot_steps,
            vol_steps,
        )

        # Store the heatmaps, returned heatmap ID
        _ = store_heatmap_data(
            calculation_id=calculation_id,
            heatmap_type="call_price",
            min_spot=min_spot,
            max_spot=max_spot,
            min_vol=min_vol,
            max_vol=max_vol,
            spot_steps=spot_steps,
            vol_steps=vol_steps,
            heatmap_data=call_prices,
        )

        _ = store_heatmap_data(
            calculation_id=calculation_id,
            heatmap_type="put_price",
            min_spot=min_spot,
            max_spot=max_spot,
            min_vol=min_vol,
            max_vol=max_vol,
            spot_steps=spot_steps,
            vol_steps=vol_steps,
            heatmap_data=put_prices,
        )

        _ = store_heatmap_data(
            calculation_id=calculation_id,
            heatmap_type="call_pnl",
            min_spot=min_spot,
            max_spot=max_spot,
            min_vol=min_vol,
            max_vol=max_vol,
            spot_steps=spot_steps,
            vol_steps=vol_steps,
            heatmap_data=call_pnl_matrix,
        )

        _ = store_heatmap_data(
            calculation_id=calculation_id,
            heatmap_type="put_pnl",
            min_spot=min_spot,
            max_spot=max_spot,
            min_vol=min_vol,
            max_vol=max_vol,
            spot_steps=spot_steps,
            vol_steps=vol_steps,
            heatmap_data=put_pnl_matrix,
        )

        st.success(f"Calculation #{calculation_id} with heatmaps saved to database!")
    except Exception as e:
        st.error(f"Failed to save to database: {e}")

# Use session state values for prices
if not st.session_state.calculation_done:
    # Default initial calculation for display
    call_price = black_scholes(S, K, T, r, sigma, "call")
    put_price = black_scholes(S, K, T, r, sigma, "put")
else:
    call_price = st.session_state.call_price
    put_price = st.session_state.put_price

# Display option prices in the right column
with col2:
    st.subheader("Option Prices")
    price_col1, price_col2 = st.columns(2)

    with price_col1:
        st.metric(
            label="CALL Value",
            value=f"${call_price:.2f}",
            delta=None,
        )

    with price_col2:
        st.metric(
            label="PUT Value",
            value=f"${put_price:.2f}",
            delta=None,
        )

    # Add explanation for P&L
    st.markdown("---")
    st.markdown(
        """**P&L (Profit & Loss)** shows how the value of your option would change at different 
        spot prices and volatilities, compared to the current option price. 
        Green indicates profit, red indicates loss."""
    )

# Heatmap parameters section
st.subheader("Heatmap Parameters")
heatmap_col1, heatmap_col2 = st.columns(2)

with heatmap_col1:
    min_spot = st.number_input(
        "Min Spot Price", min_value=0.01, value=max(0.8 * S, 0.01), step=0.01
    )
    max_spot = st.number_input(
        "Max Spot Price", min_value=min_spot + 0.01, value=1.2 * S, step=0.01
    )

with heatmap_col2:
    min_vol = st.slider(
        "Min Volatility for Heatmap",
        min_value=0.01,
        max_value=1.0,
        value=0.1,
        step=0.01,
    )
    max_vol = st.slider(
        "Max Volatility for Heatmap",
        min_value=min_vol + 0.01,
        max_value=1.0,
        value=0.5,
        step=0.01,
    )

# Generate heatmap data
spot_steps = 20
vol_steps = 20
spot_prices, volatilities, call_prices, put_prices, call_pnl_matrix, put_pnl_matrix = (
    generate_price_matrix(
        min_spot,
        max_spot,
        min_vol,
        max_vol,
        K,
        T,
        r,
        call_price,  # Use the calculated call price instead of a separate purchase price
        put_price,  # Use the calculated put price instead of a separate purchase price
        spot_steps,
        vol_steps,
    )
)

# Create heatmap section
st.header("Options Price - Interactive Heatmap")
st.markdown(
    "Explore how option prices fluctuate with varying 'Spot Prices and Volatility' levels using interactive heatmap parameters, all while maintaining a constant 'Strike Price'."
)

# Create two columns for the heatmaps
heatmap_call_col, heatmap_put_col = st.columns(2)

# Call Price Heatmap
with heatmap_call_col:
    st.subheader("Call Price Heatmap")

    # Create the heatmap using Plotly
    fig_call = px.imshow(
        call_prices,
        labels=dict(x="Spot Price", y="Volatility", color="Call Price ($)"),
        x=spot_prices,
        y=volatilities,
        color_continuous_scale="Viridis",
        aspect="auto",
    )

    # Update layout with improved axis formatting
    fig_call.update_layout(
        height=500,
        xaxis_title="Spot Price",
        yaxis_title="Volatility",
        coloraxis_colorbar=dict(title="Call Price ($)"),
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(0, spot_steps, 4)),
            ticktext=[f"{p:.0f}" for p in spot_prices[::4]],
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(0, vol_steps, 4)),
            ticktext=[f"{v:.2f}" for v in volatilities[::4]],
        ),
    )

    # Display the heatmap
    st.plotly_chart(fig_call, use_container_width=True)

# Put Price Heatmap
with heatmap_put_col:
    st.subheader("Put Price Heatmap")

    # Create the heatmap using Plotly
    fig_put = px.imshow(
        put_prices,
        labels=dict(x="Spot Price", y="Volatility", color="Put Price ($)"),
        x=spot_prices,
        y=volatilities,
        color_continuous_scale="Plasma",
        aspect="auto",
    )

    # Update layout with improved axis formatting
    fig_put.update_layout(
        height=500,
        xaxis_title="Spot Price",
        yaxis_title="Volatility",
        coloraxis_colorbar=dict(title="Put Price ($)"),
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(0, spot_steps, 4)),
            ticktext=[f"{p:.0f}" for p in spot_prices[::4]],
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(0, vol_steps, 4)),
            ticktext=[f"{v:.2f}" for v in volatilities[::4]],
        ),
    )

    # Display the heatmap
    st.plotly_chart(fig_put, use_container_width=True)

# Add annotations to display actual values in the heatmap cells with improved formatting
# Call price annotations
for i in range(vol_steps):
    for j in range(spot_steps):
        # Round to 1 decimal place for cleaner display
        price_value = call_prices[i, j]
        # Only show values at certain intervals to reduce visual clutter
        if i % 2 == 0 and j % 2 == 0:  # Show every other row and column
            text_value = f"{price_value:.1f}"
            fig_call.add_annotation(
                x=j,
                y=i,
                text=text_value,
                showarrow=False,
                font=dict(
                    color="white" if price_value > call_prices.max() * 0.6 else "black",
                    size=8,
                ),
            )

# Put price annotations
for i in range(vol_steps):
    for j in range(spot_steps):
        # Round to 1 decimal place for cleaner display
        price_value = put_prices[i, j]
        # Only show values at certain intervals to reduce visual clutter
        if i % 2 == 0 and j % 2 == 0:  # Show every other row and column
            text_value = f"{price_value:.1f}"
            fig_put.add_annotation(
                x=j,
                y=i,
                text=text_value,
                showarrow=False,
                font=dict(
                    color="white" if price_value > put_prices.max() * 0.6 else "black",
                    size=8,
                ),
            )

# Add P&L Heatmaps
st.header("Profit & Loss at Expiration - Interactive Heatmap")
st.markdown(
    """This heatmap shows the profit or loss at option expiration for different combinations of:
    - Final stock price at expiration (x-axis)
    - Initial option premium paid (y-axis)
    
    **Green regions**: Profit (positive return after deducting the premium paid)
    **Red regions**: Loss (negative return, including the premium paid)"""
)

# Create two columns for the P&L heatmaps
pnl_call_col, pnl_put_col = st.columns(2)

# Create a range of option premiums (y-axis) based on a percentage of the current calculated price
call_premium_current = call_price
put_premium_current = put_price

# Calculate reasonable P&L scale
reasonable_scale = max(call_premium_current, put_premium_current) * 1.5
max_abs_pnl = min(max(reasonable_scale, 5.0), 50.0)

# Create ranges for our heatmaps
# For x-axis (spot prices): Use the same spot price range we already have
# For y-axis (option premiums): Create a range around the current premium
premium_steps = 20
call_premium_range = np.linspace(
    max(0.1, call_premium_current * 0.5), call_premium_current * 1.5, premium_steps
)
put_premium_range = np.linspace(
    max(0.1, put_premium_current * 0.5), put_premium_current * 1.5, premium_steps
)

# Create empty matrices for call and put P&L calculations
call_pnl_by_premium = np.zeros((premium_steps, spot_steps))
put_pnl_by_premium = np.zeros((premium_steps, spot_steps))

# Calculate P&L for calls and puts at different spot prices and premium levels
for i, premium in enumerate(call_premium_range):
    for j, spot in enumerate(spot_prices):
        # Call P&L at expiration: max(0, spot - strike) - premium
        call_pnl_by_premium[i, j] = max(0, spot - K) - premium

for i, premium in enumerate(put_premium_range):
    for j, spot in enumerate(spot_prices):
        # Put P&L at expiration: max(0, strike - spot) - premium
        put_pnl_by_premium[i, j] = max(0, K - spot) - premium

# Call P&L Heatmap
with pnl_call_col:
    st.subheader("Call Option P&L at Expiration")

    # Create heatmap showing call P&L for different spot prices and premium levels
    fig_call_pnl = px.imshow(
        call_pnl_by_premium,
        labels=dict(
            x="Stock Price at Expiration", y="Call Premium Paid", color="P&L ($)"
        ),
        x=spot_prices,
        y=call_premium_range,
        color_continuous_scale="RdYlGn",  # Red-Yellow-Green scale
        aspect="auto",
        color_continuous_midpoint=0,  # Set midpoint at 0 to ensure red for negative, green for positive
        zmin=-max_abs_pnl,  # Consistent scale for negative values
        zmax=max_abs_pnl,  # Consistent scale for positive values
    )

    # Mark the current premium with a horizontal line
    fig_call_pnl.add_hline(
        y=np.argmin(np.abs(call_premium_range - call_premium_current)),
        line_width=2,
        line_dash="dash",
        line_color="white",
        annotation_text="Current premium",
        annotation_position="bottom right",
    )

    # Mark the strike price with a vertical line
    fig_call_pnl.add_vline(
        x=np.argmin(np.abs(spot_prices - K)),
        line_width=2,
        line_dash="dash",
        line_color="white",
        annotation_text=f"Strike: ${K}",
        annotation_position="top left",
    )

    # Update layout
    fig_call_pnl.update_layout(
        height=500,
        xaxis_title="Stock Price at Expiration ($)",
        yaxis_title="Call Premium Paid ($)",
        coloraxis_colorbar=dict(title="P&L ($)"),
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(0, spot_steps, 4)),
            ticktext=[f"${p:.0f}" for p in spot_prices[::4]],
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(0, premium_steps, 4)),
            ticktext=[f"${p:.2f}" for p in call_premium_range[::4]],
        ),
    )

    # Add annotations to display actual values - only show a subset for clarity
    for i in range(0, premium_steps, 3):
        for j in range(0, spot_steps, 3):
            pnl_value = call_pnl_by_premium[i, j]
            text_value = f"{pnl_value:.1f}" if abs(pnl_value) >= 1.0 else ""

            # Use white text for very negative or very positive values (for contrast)
            if pnl_value > 0.25 * max_abs_pnl:  # Green area
                text_color = "white"
            elif pnl_value < -0.25 * max_abs_pnl:  # Red area
                text_color = "white"
            else:  # Yellow/neutral area
                text_color = "black"

            fig_call_pnl.add_annotation(
                x=j,
                y=i,
                text=text_value,
                showarrow=False,
                font=dict(
                    color=text_color,
                    size=8,
                ),
            )

    # Display the heatmap
    st.plotly_chart(fig_call_pnl, use_container_width=True)

# Put P&L Heatmap
with pnl_put_col:
    st.subheader("Put Option P&L at Expiration")

    # Create heatmap showing put P&L for different spot prices and premium levels
    fig_put_pnl = px.imshow(
        put_pnl_by_premium,
        labels=dict(
            x="Stock Price at Expiration", y="Put Premium Paid", color="P&L ($)"
        ),
        x=spot_prices,
        y=put_premium_range,
        color_continuous_scale="RdYlGn",  # Red-Yellow-Green scale
        aspect="auto",
        color_continuous_midpoint=0,  # Set midpoint at 0 to ensure red for negative, green for positive
        zmin=-max_abs_pnl,  # Consistent scale for negative values
        zmax=max_abs_pnl,  # Consistent scale for positive values
    )

    # Mark the current premium with a horizontal line
    fig_put_pnl.add_hline(
        y=np.argmin(np.abs(put_premium_range - put_premium_current)),
        line_width=2,
        line_dash="dash",
        line_color="white",
        annotation_text="Current premium",
        annotation_position="bottom right",
    )

    # Mark the strike price with a vertical line
    fig_put_pnl.add_vline(
        x=np.argmin(np.abs(spot_prices - K)),
        line_width=2,
        line_dash="dash",
        line_color="white",
        annotation_text=f"Strike: ${K}",
        annotation_position="top right",
    )

    # Update layout
    fig_put_pnl.update_layout(
        height=500,
        xaxis_title="Stock Price at Expiration ($)",
        yaxis_title="Put Premium Paid ($)",
        coloraxis_colorbar=dict(title="P&L ($)"),
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(0, spot_steps, 4)),
            ticktext=[f"${p:.0f}" for p in spot_prices[::4]],
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(0, premium_steps, 4)),
            ticktext=[f"${p:.2f}" for p in put_premium_range[::4]],
        ),
    )

    # Add annotations to display actual values - only show a subset for clarity
    for i in range(0, premium_steps, 3):
        for j in range(0, spot_steps, 3):
            pnl_value = put_pnl_by_premium[i, j]
            text_value = f"{pnl_value:.1f}" if abs(pnl_value) >= 1.0 else ""

            # Use white text for very negative or very positive values (for contrast)
            if pnl_value > 0.25 * max_abs_pnl:  # Green area
                text_color = "white"
            elif pnl_value < -0.25 * max_abs_pnl:  # Red area
                text_color = "white"
            else:  # Yellow/neutral area
                text_color = "black"

            fig_put_pnl.add_annotation(
                x=j,
                y=i,
                text=text_value,
                showarrow=False,
                font=dict(
                    color=text_color,
                    size=8,
                ),
            )

    # Display the heatmap
    st.plotly_chart(fig_put_pnl, use_container_width=True)
