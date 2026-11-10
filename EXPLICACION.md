# Guía para entender y exponer el simulador

## 1. Qué fenómeno representa

El sistema es una masa puntual de masa m unida al extremo de una varilla rígida sin masa de longitud L. El péndulo se mueve en un plano. En el pivote hay fricción viscosa y se aplica un torque periódico.

La variable que se calcula es el ángulo theta. Sus unidades son radianes; el tiempo se mide en segundos.

## 2. De dónde sale la ecuación

La ley de rotación dice:

suma de torques = momento de inercia por aceleración angular

Para una masa puntual al final de una varilla sin masa:

I = m L²

Los torques son:

- Gravedad: -m g L sin(theta), porque trata de regresar el péndulo a la vertical.
- Fricción viscosa: -c theta', porque se opone a la velocidad angular.
- Torque externo: tau0 cos(Omega t), o tau0 sin(Omega t), según la opción de la ventana.

Por tanto:

m L² theta'' + c theta' + m g L sin(theta) = tau0 cos(Omega t)

El programa conserva sin(theta) en la simulación principal. Por eso puede representar ángulos que no sean pequeños.

## 3. Qué significa cada módulo

### modelo.py

Contiene la física:

- torque_aplicado calcula la excitación en el tiempo actual.
- derivadas calcula theta' y omega'. El estado se guarda como el par (theta, omega).
- La aceleración angular se obtiene despejando theta'' de la ecuación diferencial.

### rk4.py

Implementa el método numérico:

- sumar_estado calcula estados intermedios.
- paso_rk4 calcula cuatro pendientes, k1, k2, k3 y k4.
- integrar repite los pasos y guarda el ángulo, la velocidad y el torque para graficarlos.

La idea de RK4 es evaluar la pendiente al comienzo, en dos puntos intermedios y al final del paso, y luego combinar esas cuatro estimaciones.

### validacion.py

La solución analítica sencilla se obtiene para ángulos pequeños:

sin(theta) aproximadamente igual a theta

Con esa aproximación, la ecuación se vuelve lineal. validacion.py calcula la respuesta periódica analítica y compara sus ángulos con la integración RK4.

Para comparar ambas soluciones se usan condiciones iniciales que pertenecen a esa respuesta periódica. Así se evita que aparezca un transitorio adicional y la comparación se mantiene clara.

Se calcula el error global:

E(h) = máximo de |ángulo analítico - ángulo RK4|

Se repite con h, h/2 y h/4. Para RK4, al dividir h por dos, el error global debería bajar aproximadamente por un factor de 16 cuando ya se está en el régimen de convergencia.

### interfaz.py

Crea la ventana:

- Las casillas permiten cambiar las variables del modelo y de la simulación.
- Simular llama al modelo no lineal y dibuja ángulo y torque.
- Validar RK4 llama al modelo linealizado, lo compara con la solución analítica y muestra la tabla de errores.
- El panel derecho dibuja la varilla y la masa usando el ángulo calculado.
- Pausar animación detiene o reanuda el dibujo. La animación solo visualiza los resultados; no resuelve la ecuación.

La longitud del dibujo se normaliza a 1 para que quepa en el panel. El cálculo matemático sí usa el valor físico L de la ventana.

### main.py

Es el punto de inicio. Al ejecutarlo, abre la ventana creada por interfaz.py.

## 4. Cómo probar una variación durante la exposición

1. Pulsen Simular con los valores iniciales.
2. Cambien solo la amplitud tau0 y vuelvan a simular. Comparen el tamaño de las oscilaciones.
3. Cambien solo c. Expliquen que una fricción mayor disipa más energía y suele reducir el movimiento.
4. Cambien Omega. Observen que la respuesta depende de la relación entre la excitación y la frecuencia natural.
5. Pulsen Validar RK4. Comparen las dos curvas y lean la tabla de errores.

Cambien un parámetro a la vez para poder atribuir cada cambio a una causa concreta.

## 5. Preguntas que deben poder responder

### ¿Por qué es una ecuación de segundo orden?

Porque describe la aceleración angular theta'', que es la segunda derivada del ángulo respecto al tiempo.

### ¿Por qué el modelo principal es no lineal?

Porque incluye sin(theta), que no es igual a theta para todos los ángulos.

### ¿Qué representa c?

El amortiguamiento viscoso en el pivote. El torque de fricción se opone a la velocidad angular.

### ¿Para qué se usa la aproximación de ángulo pequeño?

Para convertir sin(theta) en theta y obtener una ecuación lineal cuya respuesta analítica se puede calcular y usar en la validación.

### ¿Qué demuestra la validación?

Que al reducir el paso h, la solución RK4 se acerca a la solución analítica. Una razón de errores cercana a 16 entre pasos consecutivos concuerda con el orden cuatro de RK4.

### ¿La animación es el cálculo?

No. RK4 calcula los estados. La animación toma los ángulos guardados y mueve el dibujo de la varilla y la masa.

## 6. Ejecución

En la terminal, desde la carpeta del proyecto:

    python3 -m pip install -r requirements.txt
    python3 main.py

Para la entrega, completen también la bitácora de IA oficial: registren las herramientas, los prompts usados, qué incorporaron y cómo verificaron los resultados.
