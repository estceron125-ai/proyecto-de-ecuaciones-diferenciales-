"""Método Runge-Kutta de cuarto orden e integración temporal."""
from math import ceil
from modelo import derivadas, torque_aplicado


def sumar_estado(estado, cambio, factor):
    """Suma factor*cambio al par (angulo, velocidad)."""
    return (
        estado[0] + factor * cambio[0],
        estado[1] + factor * cambio[1]
    )


def paso_rk4(t, estado, h, p, lineal=False):
    """Calcula un paso de tamaño h usando las cuatro pendientes RK4."""
    k1 = derivadas(t, estado, p, lineal)
    k2 = derivadas(t + h/2, sumar_estado(estado, k1, h/2), p, lineal)
    k3 = derivadas(t + h/2, sumar_estado(estado, k2, h/2), p, lineal)
    k4 = derivadas(t + h, sumar_estado(estado, k3, h), p, lineal)

    theta = estado[0] + h * (k1[0] + 2*k2[0] + 2*k3[0] + k4[0]) / 6
    omega = estado[1] + h * (k1[1] + 2*k2[1] + 2*k3[1] + k4[1]) / 6
    return theta, omega


def integrar(p, inicial, h, tiempo_final, lineal=False):
    """Aplica RK4 repetidamente y guarda tiempos, estados y torque."""
    if h <= 0 or tiempo_final <= 0:
        raise ValueError("El paso h y el tiempo final deben ser positivos.")
    if ceil(tiempo_final / h) > 400_000:
        raise ValueError("Hay demasiados pasos; aumenta h o reduce el tiempo.")

    tiempos = [0.0]
    estados = [inicial]

    while tiempos[-1] < tiempo_final:
        paso = min(h, tiempo_final - tiempos[-1])
        nuevo_estado = paso_rk4(
            tiempos[-1], estados[-1], paso, p, lineal
        )
        tiempos.append(tiempos[-1] + paso)
        estados.append(nuevo_estado)

    torques = [torque_aplicado(t, p) for t in tiempos]
    return tiempos, estados, torques
