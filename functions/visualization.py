import plotly.graph_objects as go
import numpy as np


def create_iv_surface_plot(
    strikes: np.ndarray,
    expirations: np.ndarray,
    iv_surface: np.ndarray,
    title: str = "Implied Volatility Surface",
    colorscale: str = "Viridis",
):
    """
    Create a 3D surface plot of implied volatility.

    Parameters:
    -----------
    strikes : np.ndarray
        Array of strike prices
    expirations : np.ndarray
        Array of expiration times in years
    iv_surface : np.ndarray
        2D array of implied volatilities with shape (len(expirations), len(strikes))
    title : str
        Plot title
    colorscale : str
        Colorscale for the surface plot

    Returns:
    --------
    plotly.graph_objects.Figure
        3D surface plot figure
    """
    # Create a meshgrid for the surface plot
    strike_grid, expiry_grid = np.meshgrid(strikes, expirations)

    # Create the 3D surface plot
    fig = go.Figure(
        data=[
            go.Surface(
                x=strike_grid,
                y=expiry_grid,
                z=iv_surface,
                colorscale=colorscale,
                colorbar=dict(title="Implied Volatility"),
                hovertemplate=(
                    "Strike: %{x:.2f}<br>Expiry: %{y:.2f} years<br>IV: %{z:.2%}<br>"
                ),
            )
        ]
    )

    # Update layout
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title="Strike Price",
            yaxis_title="Time to Expiration (Years)",
            zaxis_title="Implied Volatility",
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True),
            zaxis=dict(showgrid=True),
            camera=dict(eye=dict(x=1.5, y=-1.5, z=1.0)),
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        height=700,
    )

    return fig


def create_iv_heatmap(
    strikes: np.ndarray,
    expirations: np.ndarray,
    iv_surface: np.ndarray,
    title: str = "Implied Volatility Heatmap",
    colorscale: str = "Viridis",
):
    """
    Create a heatmap of implied volatility.

    Parameters:
    -----------
    strikes : np.ndarray
        Array of strike prices
    expirations : np.ndarray
        Array of expiration times in years
    iv_surface : np.ndarray
        2D array of implied volatilities with shape (len(expirations), len(strikes))
    title : str
        Plot title
    colorscale : str
        Colorscale for the heatmap

    Returns:
    --------
    plotly.graph_objects.Figure
        Heatmap figure
    """
    # Create the heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=iv_surface,
            x=strikes,
            y=expirations,
            colorscale=colorscale,
            colorbar=dict(title="Implied Volatility"),
            hovertemplate=(
                "Strike: %{x:.2f}<br>Expiry: %{y:.2f} years<br>IV: %{z:.2%}<br>"
            ),
        )
    )

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Strike Price",
        yaxis_title="Time to Expiration (Years)",
        margin=dict(l=0, r=0, b=0, t=30),
        height=500,
    )

    return fig


def create_iv_contour(
    strikes: np.ndarray,
    expirations: np.ndarray,
    iv_surface: np.ndarray,
    title: str = "Implied Volatility Contour",
    colorscale: str = "Viridis",
):
    """
    Create a contour plot of implied volatility.

    Parameters:
    -----------
    strikes : np.ndarray
        Array of strike prices
    expirations : np.ndarray
        Array of expiration times in years
    iv_surface : np.ndarray
        2D array of implied volatilities with shape (len(expirations), len(strikes))
    title : str
        Plot title
    colorscale : str
        Colorscale for the contour plot

    Returns:
    --------
    plotly.graph_objects.Figure
        Contour plot figure
    """
    # Create the contour plot
    fig = go.Figure(
        data=go.Contour(
            z=iv_surface,
            x=strikes,
            y=expirations,
            colorscale=colorscale,
            colorbar=dict(title="Implied Volatility"),
            hovertemplate=(
                "Strike: %{x:.2f}<br>Expiry: %{y:.2f} years<br>IV: %{z:.2%}<br>"
            ),
            contours=dict(
                showlabels=True,
                labelfont=dict(size=12, color="white"),
            ),
        )
    )

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Strike Price",
        yaxis_title="Time to Expiration (Years)",
        margin=dict(l=0, r=0, b=0, t=30),
        height=500,
    )

    return fig
