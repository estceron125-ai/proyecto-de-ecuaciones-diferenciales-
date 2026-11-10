# Simulador del péndulo amortiguado y forzado

## Qué representa

Se modela una masa puntual al final de una varilla rígida sin masa. La masa se mueve en un plano; el pivote tiene amortiguamiento viscoso y recibe un torque periódico.

La ecuación no lineal es:

m L² θ'' + c θ' + m g L sin(θ) = τ₀ cos(Ωt)

El programa permite escoger torque senoidal o cosenoidal. La simulación principal conserva sin(θ), por lo que representa el péndulo para ángulos generales.

## Archivos

- main.py: abre la aplicación.
- interfaz.py: crea controles, gráficas y dibujo animado.
- modelo.py: contiene la ecuación y el torque aplicado.
- rk4.py: implementa RK4 y avanza la solución en el tiempo.
- validacion.py: compara RK4 con una solución analítica del modelo linealizado.
- requirements.txt: dependencia para dibujar las gráficas.

## Ejecutar en Mac

Desde la Terminal de VS Code, entra a esta carpeta y ejecuta:

    python3 -m pip install -r requirements.txt
    python3 main.py

Tkinter suele venir incluido con Python en macOS. Si aparece un error que dice que no existe tkinter, deben usar una instalación de Python que incluya Tk.

## Controles de la ventana

Se pueden cambiar masa, longitud, amortiguamiento, amplitud y frecuencia del torque, ángulo y velocidad iniciales, paso de tiempo y duración.

- Simular: integra el modelo no lineal y actualiza las gráficas y el dibujo.
- Validar RK4: integra el modelo linealizado con h, h/2 y h/4 y compara con la solución analítica.
- Pausar/Reanudar animación: detiene o continúa el dibujo del péndulo.

## Cómo interpretar la validación

La solución analítica corresponde al modelo linealizado, donde sin(θ) ≈ θ. Durante la validación, RK4 resuelve ese mismo modelo linealizado; así, la diferencia calculada mide el error del método numérico y no la diferencia entre el péndulo lineal y el no lineal.

La tabla muestra el error global máximo de ángulo para cada paso. Al reducir h a la mitad, en el régimen de convergencia de RK4 el error global debe disminuir aproximadamente 16 veces.

## Método

Se reescribe la ecuación de segundo orden como dos ecuaciones de primer orden: θ' = ω y ω' = aceleración angular. RK4 calcula cuatro pendientes (k1, k2, k3 y k4) y las combina para avanzar un paso.
