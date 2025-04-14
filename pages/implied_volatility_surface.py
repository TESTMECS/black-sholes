import streamlit as st
import numpy as np
import pandas as pd
from functions.black_scholes import black_scholes
from functions.implied_volatility import (
    generate_iv_surface,
    generate_theoretical_iv_surface,
)
from functions.visualization import (
    create_iv_surface_plot,
    create_iv_heatmap,
    create_iv_contour,
)

# Set page configuration
st.set_page_config(
    page_title="Implied Volatility Surface - Black-Scholes Model",
    layout="wide",
)

# Page title
st.title("Implied Volatility Surface Visualization")
st.markdown(
    """
    This page visualizes the implied volatility surface across different strike prices and expiration dates.
    The implied volatility surface shows how volatility varies with strike price (volatility smile/skew) 
    and time to expiration (term structure).
    """
)

# Create tabs for different visualization modes
tab1, tab2 = st.tabs(["Theoretical Surface", "Market Data"])

# Tab 1: Theoretical Surface
with tab1:
    st.header("Theoretical Implied Volatility Surface")
    st.markdown(
        """
        This visualization shows a theoretical implied volatility surface with smile and term structure effects.
        Adjust the parameters to see how they affect the shape of the surface.
        """
    )

    # Create columns for parameters
    col1, col2, col3 = st.columns(3)

    with col1:
        # Basic parameters
        S = st.number_input(
            "Current Stock Price ($)", min_value=1.0, value=100.0, step=1.0
        )
        r = (
            st.number_input(
                "Risk-Free Rate (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.1
            )
            / 100
        )
        base_volatility = (
            st.number_input(
                "Base Volatility (%)",
                min_value=1.0,
                max_value=100.0,
                value=20.0,
                step=1.0,
            )
            / 100
        )

    with col2:
        # Strike range parameters
        min_strike = st.number_input(
            "Minimum Strike Price ($)",
            min_value=1.0,
            value=max(50.0, 0.5 * S),
            step=1.0,
        )
        max_strike = st.number_input(
            "Maximum Strike Price ($)",
            min_value=min_strike + 1.0,
            value=min(150.0, 1.5 * S),
            step=1.0,
        )
        strike_steps = st.slider(
            "Strike Price Steps", min_value=5, max_value=50, value=20
        )

    with col3:
        # Expiration range parameters
        min_expiry = st.number_input(
            "Minimum Expiration (Years)",
            min_value=0.01,
            max_value=10.0,
            value=0.1,
            step=0.1,
        )
        max_expiry = st.number_input(
            "Maximum Expiration (Years)",
            min_value=min_expiry + 0.1,
            max_value=10.0,
            value=2.0,
            step=0.1,
        )
        expiry_steps = st.slider(
            "Expiration Steps", min_value=3, max_value=30, value=10
        )

    # Advanced parameters
    st.subheader("Advanced Parameters")
    col1, col2 = st.columns(2)

    with col1:
        smile_factor = st.slider(
            "Volatility Smile Factor",
            min_value=0.0,
            max_value=1.0,
            value=0.4,
            step=0.05,
            help="Controls the strength of the volatility smile effect. Higher values create a more pronounced smile.",
        )

    with col2:
        term_structure_factor = st.slider(
            "Term Structure Factor",
            min_value=0.0,
            max_value=0.5,
            value=0.1,
            step=0.01,
            help="Controls how volatility changes with time to expiration. Higher values create a steeper term structure.",
        )

    # Visualization options
    st.subheader("Visualization Options")
    col1, col2 = st.columns(2)

    with col1:
        plot_type = st.selectbox(
            "Plot Type",
            options=["3D Surface", "Heatmap", "Contour", "All"],
            index=0,
        )

    with col2:
        colorscale = st.selectbox(
            "Color Scale",
            options=[
                "Viridis",
                "Plasma",
                "Inferno",
                "Magma",
                "Cividis",
                "Turbo",
                "Blues",
                "Greens",
                "Reds",
                "YlOrRd",
                "RdBu",
                "Jet",
                "Rainbow",
                "Spectral",
            ],
            index=0,
        )

    # Generate the theoretical IV surface
    strikes, expirations, iv_surface = generate_theoretical_iv_surface(
        S=S,
        min_strike=min_strike,
        max_strike=max_strike,
        min_expiry=min_expiry,
        max_expiry=max_expiry,
        r=r,
        base_volatility=base_volatility,
        strike_steps=strike_steps,
        expiry_steps=expiry_steps,
        smile_factor=smile_factor,
        term_structure_factor=term_structure_factor,
    )

    # Display the plots based on the selected plot type
    if plot_type == "3D Surface" or plot_type == "All":
        st.subheader("3D Surface Plot")
        fig_surface = create_iv_surface_plot(
            strikes,
            expirations,
            iv_surface,
            title="Implied Volatility Surface",
            colorscale=colorscale,
        )
        st.plotly_chart(fig_surface, use_container_width=True)

    if plot_type == "Heatmap" or plot_type == "All":
        st.subheader("Heatmap")
        fig_heatmap = create_iv_heatmap(
            strikes,
            expirations,
            iv_surface,
            title="Implied Volatility Heatmap",
            colorscale=colorscale,
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

    if plot_type == "Contour" or plot_type == "All":
        st.subheader("Contour Plot")
        fig_contour = create_iv_contour(
            strikes,
            expirations,
            iv_surface,
            title="Implied Volatility Contour",
            colorscale=colorscale,
        )
        st.plotly_chart(fig_contour, use_container_width=True)

    # Display the data table
    if st.checkbox("Show Data Table"):
        st.subheader("Implied Volatility Data")

        # Create a DataFrame for display
        df = pd.DataFrame(
            iv_surface,
            index=[f"{t:.2f}y" for t in expirations],
            columns=[f"${k:.0f}" for k in strikes],
        )

        st.dataframe(df.style.format("{:.2%}"), use_container_width=True)

# Tab 2: Market Data
with tab2:
    st.header("Market Data Implied Volatility Surface")
    st.markdown(
        """
        This visualization allows you to upload market option prices and calculate the implied volatility surface.
        You can either upload a CSV file with market data or use the sample data provided.
        """
    )

    # Option to use sample data or upload
    data_source = st.radio(
        "Data Source",
        options=["Use Sample Data", "Upload CSV"],
        index=0,
    )

    if data_source == "Use Sample Data":
        st.info("Using sample market data with a typical volatility smile pattern.")

        # Create sample data
        S_sample = 100.0
        r_sample = 0.05

        # Create a grid of strikes and expirations
        strikes_sample = np.linspace(80, 120, 9)
        expirations_sample = np.array([0.25, 0.5, 0.75, 1.0, 1.5, 2.0])

        # Generate option prices with a volatility smile
        market_prices = np.zeros((len(expirations_sample), len(strikes_sample)))

        for i, T in enumerate(expirations_sample):
            for j, K in enumerate(strikes_sample):
                # Create a volatility smile effect
                moneyness = K / S_sample
                vol = 0.2 + 0.15 * (moneyness - 1) ** 2 + 0.03 * T

                # Calculate the option price
                market_prices[i, j] = black_scholes(
                    S_sample, K, T, r_sample, vol, "call"
                )

        # Calculate the implied volatility surface
        iv_surface_sample = generate_iv_surface(
            market_prices,
            S_sample,
            strikes_sample,
            expirations_sample,
            r_sample,
            "call",
        )

        # Display the 3D surface plot
        fig_surface = create_iv_surface_plot(
            strikes_sample,
            expirations_sample,
            iv_surface_sample,
            title="Sample Market Implied Volatility Surface",
            colorscale="Viridis",
        )
        st.plotly_chart(fig_surface, use_container_width=True)

        # Display the heatmap
        fig_heatmap = create_iv_heatmap(
            strikes_sample,
            expirations_sample,
            iv_surface_sample,
            title="Sample Market Implied Volatility Heatmap",
            colorscale="Viridis",
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

    else:
        st.info(
            """
            Upload a CSV file with market option prices. The file should have the following format:
            - First column: Strike prices
            - First row: Expiration times in years
            - The rest of the cells: Option prices for each strike and expiration
            """
        )

        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

        if uploaded_file is not None:
            try:
                # Read the CSV file
                df = pd.read_csv(uploaded_file, index_col=0)

                # Extract strikes, expirations, and prices
                strikes_upload = df.index.values.astype(float)
                expirations_upload = df.columns.values.astype(float)
                market_prices_upload = df.values

                # Get parameters for IV calculation
                S_upload = st.number_input(
                    "Current Stock Price ($)", min_value=1.0, value=100.0, step=1.0
                )
                r_upload = (
                    st.number_input(
                        "Risk-Free Rate (%)",
                        min_value=0.0,
                        max_value=20.0,
                        value=5.0,
                        step=0.1,
                    )
                    / 100
                )
                option_type = st.selectbox(
                    "Option Type", options=["call", "put"], index=0
                )

                # Calculate the implied volatility surface
                iv_surface_upload = generate_iv_surface(
                    market_prices_upload,
                    S_upload,
                    strikes_upload,
                    expirations_upload,
                    r_upload,
                    option_type,
                )

                # Display the 3D surface plot
                fig_surface = create_iv_surface_plot(
                    strikes_upload,
                    expirations_upload,
                    iv_surface_upload,
                    title="Uploaded Market Implied Volatility Surface",
                    colorscale="Viridis",
                )
                st.plotly_chart(fig_surface, use_container_width=True)

                # Display the heatmap
                fig_heatmap = create_iv_heatmap(
                    strikes_upload,
                    expirations_upload,
                    iv_surface_upload,
                    title="Uploaded Market Implied Volatility Heatmap",
                    colorscale="Viridis",
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)

            except Exception as e:
                st.error(f"Error processing the uploaded file: {e}")
                st.error("Please make sure the file format is correct.")
        else:
            st.warning("Please upload a CSV file with market option prices.")

# Add explanatory text at the bottom
st.markdown("""
## Understanding the Implied Volatility Surface

The implied volatility surface is a three-dimensional representation of implied volatility across different strike prices and expiration dates. It provides valuable insights into market expectations and risk pricing.

### Key Features:

1. **Volatility Smile/Skew**: The curve formed by implied volatilities across different strike prices for a fixed expiration date. This often forms a smile or skew shape, indicating that out-of-the-money options have higher implied volatilities than at-the-money options.

2. **Term Structure**: How implied volatility changes with time to expiration for a fixed strike price. This reflects the market's expectation of future volatility over different time horizons.

3. **Surface Dynamics**: The entire surface evolves over time as market conditions change, reflecting shifts in market sentiment and risk perception.

### Applications:

- **Risk Management**: Identifying areas of high implied volatility can help in risk assessment and hedging strategies.
- **Option Pricing**: More accurate pricing of exotic options by incorporating the volatility surface.
- **Trading Strategies**: Identifying potential arbitrage opportunities or relative value trades.
- **Market Sentiment**: Gauging market expectations about future price movements and uncertainty.
""")
