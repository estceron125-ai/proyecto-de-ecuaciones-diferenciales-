"""Solución analítica lineal y validación de convergencia de RK4."""
import math
from rk4 import integrar
from modelo import G


def preparar_solucion(p):
    """
    Calcula amplitud, desfase y condiciones iniciales para la respuesta
    sinusoidal estable del modelo linealizado.
    """
    I = p["m"] * p["L"]**2
    wn2 = G / p["L"]
    gamma = p["c"] / (2 * I)
    Omega = p["Omega"]

    denominador = math.sqrt(
        (wn2 - Omega**2)**2 + (2 * gamma * Omega)**2
    )
    if denominador < 1e-14:
        raise ValueError(
            "No se puede usar este caso analítico: hay resonancia "
            "sin amortiguamiento. Prueba con c mayor que cero."
        )

    amplitud = (p["tau0"] / I) / denominador
    desfase = math.atan2(2 * gamma * Omega, wn2 - Omega**2)
    fase = 0 if p["tipo"] == "Cosenoidal" else -math.pi / 2

    # La solución estable es theta(t)=A*cos(Omega*t+fase-desfase).
    def exacta(t):
        return amplitud * math.cos(Omega*t + fase - desfase)

    # Se eligen condiciones iniciales sobre esa solución estable.
    theta0 = exacta(0)
    omega0 = -amplitud * Omega * math.sin(fase - desfase)

    return exacta, (theta0, omega0), amplitud, desfase


def validar_rk4(p, h, tiempo_final):
    """Compara RK4 con la solución analítica para h, h/2 y h/4."""
    exacta, inicial, amplitud, desfase = preparar_solucion(p)
    h_base = min(h, tiempo_final / 20)
    resultados = []

    for paso in (h_base, h_base/2, h_base/4):
        # En la validación usamos la misma ecuación lineal que la solución exacta.
        tiempos, estados, torques = integrar(
            p, inicial, paso, tiempo_final, lineal=True
        )

        # Error global: máximo error angular en todos los puntos de tiempo.
        error = max(
            abs(estado[0] - exacta(t))
            for t, estado in zip(tiempos, estados)
        )
        resultados.append((paso, error))

    tiempos, estados, torques = integrar(
        p, inicial, h_base, tiempo_final, lineal=True
    )
    curva_exacta = [exacta(t) for t in tiempos]

    return {
        "inicial": inicial,
        "resultados": resultados,
        "tiempos": tiempos,
        "estados": estados,
        "torques": torques,
        "exacta": curva_exacta
    }
