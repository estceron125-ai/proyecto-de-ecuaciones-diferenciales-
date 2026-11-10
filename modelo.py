"""Ecuación física del péndulo amortiguado y forzado."""
import math

G = 9.81  # gravedad en m/s²


def torque_aplicado(t, p):
    """Calcula el torque periódico aplicado en el instante t."""
    if p["tipo"] == "Senoidal":
        return p["tau0"] * math.sin(p["Omega"] * t)
    return p["tau0"] * math.cos(p["Omega"] * t)


def derivadas(t, estado, p, lineal=False):
    """
    Devuelve (theta', omega') para integrar con RK4.

    estado = (theta, omega)
    theta' = omega
    omega' = aceleración angular
    """
    theta, omega = estado
    m, L, c = p["m"], p["L"], p["c"]

    # El péndulo completo usa sin(theta).
    # La validación usa sin(theta) ≈ theta (ángulos pequeños).
    termino_gravedad = theta if lineal else math.sin(theta)

    aceleracion = (
        torque_aplicado(t, p)
        - c * omega
        - m * G * L * termino_gravedad
    ) / (m * L**2)

    return omega, aceleracion
