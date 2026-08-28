import numpy as np
import plotly.graph_objects as go
from physics_engine import Charge, calculate_grid_physics_2d

def plot_force_only_2d(charges: list[Charge], bounds: float = 5.0, zero_field_x: float | None = None) -> go.Figure:
    """
    Gráfico de Fuerza Eléctrica (Ley de Coulomb) con marcador opcional de Punto Nulo (E = 0).
    """
    fig = go.Figure()

    if len(charges) >= 2:
        c1, c2 = charges[0], charges[1]
        
        # Línea de separación
        fig.add_trace(go.Scatter(
            x=[c1.x, c2.x], y=[c1.y, c2.y],
            mode="lines+text",
            text=["", f"d = {abs(c2.x - c1.x):.1f} m"],
            textposition="top center",
            line=dict(color="#AAAAAA", width=2, dash="dash"),
            showlegend=False
        ))

        # Flechas de fuerza F
        mismo_signo = (c1.q * c2.q) > 0
        dir1 = -1.0 if mismo_signo else 1.0
        dir2 = 1.0 if mismo_signo else -1.0

        fig.add_annotation(
            x=c1.x + dir1 * 0.8, y=c1.y,
            ax=c1.x, ay=c1.y,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowsize=1.5, arrowwidth=3,
            arrowcolor="#00FFCC", opacity=0.9
        )
        
        fig.add_annotation(
            x=c2.x + dir2 * 0.8, y=c2.y,
            ax=c2.x, ay=c2.y,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowsize=1.5, arrowwidth=3,
            arrowcolor="#00FFCC", opacity=0.9
        )

    # 🌟 Marcador de Punto de Campo Cero (E = 0)
    if zero_field_x is not None:
        fig.add_trace(go.Scatter(
            x=[zero_field_x], y=[0.0],
            mode="markers+text",
            name="Campo Nulo (E=0)",
            text=["⭐ <b>E = 0</b>"],
            textposition="top center",
            textfont=dict(color="#FFD700", size=14, family="Arial Black"),
            marker=dict(size=18, color="#FFD700", symbol="star", line=dict(color="white", width=1.5)),
            hovertemplate="<b>Punto donde E = 0 N/C</b><br>X: %{x:.2f} m<extra></extra>"
        ))

    # Dibujar Cargas
    for c in charges:
        color = "#FF3366" if c.q > 0 else ("#3399FF" if c.q < 0 else "#AAAAAA")
        text_sign = "+" if c.q > 0 else ("-" if c.q < 0 else "0")

        fig.add_trace(go.Scatter(
            x=[c.x], y=[c.y],
            mode="markers+text",
            name=c.label,
            text=[f"<b>{text_sign}</b>"],
            textposition="middle center",
            textfont=dict(color="white", size=18, family="Arial Black"),
            marker=dict(size=28, color=color, line=dict(color="white", width=2)),
            hovertemplate=f"<b>{c.label}</b><br>q: {c.q*1e6:.1f} µC<extra></extra>"
        ))

    fig.update_layout(
        title="<b>Fuerza Eléctrica entre Cargas (Ley de Coulomb)</b>",
        xaxis=dict(title="Posición X (m)", range=[-bounds, bounds], gridcolor="#333"),
        yaxis=dict(title="Posición Y (m)", range=[-bounds, bounds], gridcolor="#333", scaleanchor="x", scaleratio=1),
        template="plotly_dark",
        margin=dict(l=30, r=30, t=50, b=30),
        showlegend=False
    )
    return fig

def plot_2d_field_and_potential(
    charges: list[Charge],
    grid_size: int = 25,
    bounds: float = 5.0,
    show_vectors: bool = True,
    show_contour: bool = True,
    show_equipotentials: bool = True,
    trajectory: np.ndarray = None,
    zero_field_x: float | None = None
) -> go.Figure:
    x_range = np.linspace(-bounds, bounds, grid_size)
    y_range = np.linspace(-bounds, bounds, grid_size)
    X, Y = np.meshgrid(x_range, y_range)

    V, Ex, Ey = calculate_grid_physics_2d(X, Y, charges)

    v_max = np.percentile(np.abs(V), 95) if len(charges) > 0 else 10.0
    V_clipped = np.clip(V, -v_max, v_max)

    fig = go.Figure()

    if show_contour:
        fig.add_trace(go.Heatmap(
            x=x_range, y=y_range, z=V_clipped,
            colorscale="RdBu_r", zsmooth="fast",
            colorbar=dict(title="Potencial V", x=1.02),
            showscale=True, hoverinfo="none"
        ))

    if show_vectors:
        step = max(1, grid_size // 12)
        X_sub = X[::step, ::step].flatten()
        Y_sub = Y[::step, ::step].flatten()
        Ex_sub = Ex[::step, ::step].flatten()
        Ey_sub = Ey[::step, ::step].flatten()

        E_norm = np.hypot(Ex_sub, Ey_sub)
        E_norm_safe = np.where(E_norm == 0, 1e-9, E_norm)
        scale_factor = (bounds / 12.0)
        u_scaled = (Ex_sub / E_norm_safe) * scale_factor * 0.4
        v_scaled = (Ey_sub / E_norm_safe) * scale_factor * 0.4

        for xi, yi, ui, vi, mag in zip(X_sub, Y_sub, u_scaled, v_scaled, E_norm):
            if mag < 1e-4:
                continue
            fig.add_annotation(
                x=xi + ui, y=yi + vi, ax=xi, ay=yi,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=1.5,
                arrowcolor="yellow", opacity=0.7
            )

    if zero_field_x is not None:
        fig.add_trace(go.Scatter(
            x=[zero_field_x], y=[0.0],
            mode="markers+text",
            name="E = 0",
            text=["⭐ <b>E=0</b>"],
            textposition="top center",
            textfont=dict(color="#FFD700", size=14, family="Arial Black"),
            marker=dict(size=18, color="#FFD700", symbol="star", line=dict(color="white", width=1.5))
        ))

    if trajectory is not None and len(trajectory) > 0:
        fig.add_trace(go.Scatter(
            x=trajectory[:, 0], y=trajectory[:, 1],
            mode="lines+markers", name="Trayectoria",
            line=dict(color="#00FFCC", width=3, dash="dot"),
            marker=dict(size=4, color="#00FFCC")
        ))

    for c in charges:
        color = "#FF3366" if c.q > 0 else ("#3399FF" if c.q < 0 else "#AAAAAA")
        text_sign = "+" if c.q > 0 else ("-" if c.q < 0 else "0")
        fig.add_trace(go.Scatter(
            x=[c.x], y=[c.y],
            mode="markers+text",
            text=[f"<b>{text_sign}</b>"],
            textposition="middle center",
            textfont=dict(color="white", size=16, family="Arial Black"),
            marker=dict(size=24, color=color, line=dict(color="white", width=2)),
            hovertemplate=f"<b>{c.label}</b><extra></extra>"
        ))

    fig.update_layout(
        title="<b>Líneas y Vectores de Campo Eléctrico (E)</b>",
        xaxis=dict(title="X (m)", range=[-bounds, bounds], gridcolor="#333"),
        yaxis=dict(title="Y (m)", range=[-bounds, bounds], gridcolor="#333", scaleanchor="x", scaleratio=1),
        template="plotly_dark",
        margin=dict(l=30, r=30, t=50, b=30),
        showlegend=False
    )
    return fig
