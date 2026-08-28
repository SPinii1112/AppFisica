import numpy as np

# Constante de Coulomb (N * m^2 / C^2)
K_E = 8.9875517923e9

class Charge:
    """Clase para representar una carga puntual en 2D/3D."""
    def __init__(self, q: float, x: float, y: float, z: float = 0.0, label: str = ""):
        self.q = q
        self.x = x
        self.y = y
        self.z = z
        self.label = label if label else f"q ({q*1e6:.1f} µC)"

    @property
    def pos(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=float)

def find_zero_field_point_1d(c1: Charge, c2: Charge) -> float | None:
    if c1.q == 0 or c2.q == 0:
        return None
        
    x1, x2 = min(c1.x, c2.x), max(c1.x, c2.x)
    q1 = c1.q if c1.x == x1 else c2.q
    q2 = c2.q if c1.x == x1 else c1.q

    if (q1 * q2) > 0:
        sqrt_q1 = np.sqrt(abs(q1))
        sqrt_q2 = np.sqrt(abs(q2))
        x0 = (x1 * sqrt_q2 + x2 * sqrt_q1) / (sqrt_q1 + sqrt_q2)
        return float(x0)
    else:
        if abs(q1) == abs(q2):
            return None
            
        sqrt_q1 = np.sqrt(abs(q1))
        sqrt_q2 = np.sqrt(abs(q2))
        
        if abs(q1) < abs(q2):
            d = abs(x2 - x1)
            x0 = x1 - (d * sqrt_q1) / (sqrt_q2 - sqrt_q1)
        else:
            d = abs(x2 - x1)
            x0 = x2 + (d * sqrt_q2) / (sqrt_q1 - sqrt_q2)
            
        return float(x0)

def calculate_grid_physics_2d(X: np.ndarray, Y: np.ndarray, charges: list[Charge]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    V = np.zeros_like(X, dtype=float)
    Ex = np.zeros_like(X, dtype=float)
    Ey = np.zeros_like(Y, dtype=float)

    for c in charges:
        dx = X - c.x
        dy = Y - c.y
        r2 = dx**2 + dy**2
        r = np.sqrt(r2)
        
        r_safe = np.maximum(r, 1e-2)
        r3_safe = np.maximum(r**3, 1e-3)

        V += K_E * c.q / r_safe
        E_factor = K_E * c.q / r3_safe
        Ex += E_factor * dx
        Ey += E_factor * dy

    return V, Ex, Ey

def calculate_electric_field_at_point(point: np.ndarray, charges: list[Charge], epsilon: float = 1e-9) -> np.ndarray:
    E = np.zeros(3, dtype=float)
    point = np.array(point, dtype=float)
    
    for c in charges:
        r_vec = point - c.pos
        dist = np.linalg.norm(r_vec)
        if dist < epsilon:
            continue
        unit_vec = r_vec / dist
        E_magnitude = K_E * c.q / (dist**2)
        E += E_magnitude * unit_vec
        
    return E

def calculate_potential_at_point(point: np.ndarray, charges: list[Charge], epsilon: float = 1e-9) -> float:
    V = 0.0
    point = np.array(point, dtype=float)
    for c in charges:
        dist = np.linalg.norm(point - c.pos)
        if dist < epsilon:
            continue
        V += K_E * c.q / dist
    return V

def calculate_force_on_charge(target_idx: int, charges: list[Charge]) -> dict:
    target = charges[target_idx]
    F_total = np.zeros(3, dtype=float)
    steps = []

    for i, c in enumerate(charges):
        if i == target_idx:
            continue
        
        r_vec = target.pos - c.pos
        dist = np.linalg.norm(r_vec)
        if dist == 0:
            continue
            
        unit_vec = r_vec / dist
        F_mag = K_E * abs(target.q * c.q) / (dist**2)
        
        sign = 1.0 if (target.q * c.q) > 0 else -1.0
        F_pair = F_mag * unit_vec * sign
        F_total += F_pair
        
        angle_xy = np.degrees(np.arctan2(F_pair[1], F_pair[0])) % 360
        
        steps.append({
            "source_idx": i,
            "source_label": c.label,
            "source_q": c.q,
            "dist": dist,
            "dx": r_vec[0],
            "dy": r_vec[1],
            "dz": r_vec[2],
            "F_mag": F_mag,
            "F_vec": F_pair,
            "angle_xy": angle_xy,
            "repulsive": (target.q * c.q) > 0
        })

    F_total_mag = np.linalg.norm(F_total)
    angle_total_xy = np.degrees(np.arctan2(F_total[1], F_total[0])) % 360 if F_total_mag > 0 else 0.0

    return {
        "target_label": target.label,
        "target_q": target.q,
        "target_pos": target.pos,
        "steps": steps,
        "F_total": F_total,
        "F_total_mag": F_total_mag,
        "angle_total_xy": angle_total_xy
    }

def simulate_test_charge_trajectory(
    q0: float, 
    m0: float, 
    init_pos: np.ndarray, 
    init_vel: np.ndarray, 
    fixed_charges: list[Charge], 
    t_max: float = 2.0, 
    dt: float = 0.01,
    bounds: float = 10.0
) -> dict:
    pos = np.array(init_pos, dtype=float)
    vel = np.array(init_vel, dtype=float)
    
    trajectory = [pos.copy()]
    times = [0.0]
    
    t = 0.0
    
    def accel(p):
        E = calculate_electric_field_at_point(p, fixed_charges)
        return (q0 * E) / m0

    while t < t_max:
        if np.abs(pos[0]) > bounds * 2 or np.abs(pos[1]) > bounds * 2:
            break
            
        col = False
        for c in fixed_charges:
            if np.linalg.norm(pos - c.pos) < 0.2:
                col = True
                break
        if col:
            break

        k1_v = accel(pos) * dt
        k1_p = vel * dt

        k2_v = accel(pos + 0.5 * k1_p) * dt
        k2_p = (vel + 0.5 * k1_v) * dt

        k3_v = accel(pos + 0.5 * k2_p) * dt
        k3_p = (vel + 0.5 * k2_v) * dt

        k4_v = accel(pos + k3_p) * dt
        k4_p = (vel + k3_v) * dt

        vel += (k1_v + 2*k2_v + 2*k3_v + k4_v) / 6.0
        pos += (k1_p + 2*k2_p + 2*k3_p + k4_p) / 6.0
        t += dt

        trajectory.append(pos.copy())
        times.append(t)

    return {
        "positions": np.array(trajectory),
        "times": np.array(times)
    }
