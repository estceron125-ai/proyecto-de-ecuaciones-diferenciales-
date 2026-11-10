"""Ventana, controles, gráficas y dibujo animado del péndulo."""
import math
import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.figure import Figure
from matplotlib.patches import Circle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from rk4 import integrar
from validacion import validar_rk4


class InterfazPendulo:
    def __init__(self, ventana):
        self.ventana = ventana
        ventana.title("Péndulo amortiguado y forzado")
        ventana.geometry("1200x760")

        # Variables usadas por la animación del dibujo.
        self.tiempos_animacion = []
        self.estados_animacion = []
        self.indice = 0
        self.after_id = None
        self.animando = False

        self.crear_controles()
        self.crear_graficas()

    def crear_controles(self):
        """Crea las casillas para parámetros y los botones."""
        marco = ttk.Frame(self.ventana, padding=10)
        marco.pack(side="left", fill="y")

        controles = ttk.LabelFrame(
            marco, text="Parámetros", padding=8
        )
        controles.pack(fill="x")

        valores = [
            ("m (kg)", "0.2"),
            ("L (m)", "0.5"),
            ("c (N·m·s/rad)", "0.01"),
            ("Torque τ₀ (N·m)", "0.05"),
            ("Frecuencia Ω (rad/s)", "2.0"),
            ("Ángulo inicial (rad)", "0.2"),
            ("Velocidad inicial (rad/s)", "0.0"),
            ("Paso h (s)", "0.02"),
            ("Tiempo final (s)", "10")
        ]

        self.cajas = {}
        for fila, (nombre, inicial) in enumerate(valores):
            ttk.Label(controles, text=nombre).grid(
                row=fila, column=0, sticky="w", pady=3
            )
            caja = ttk.Entry(controles, width=12)
            caja.insert(0, inicial)
            caja.grid(row=fila, column=1, pady=3)
            self.cajas[nombre] = caja

        ttk.Label(controles, text="Tipo de torque").grid(
            row=len(valores), column=0, sticky="w", pady=3
        )
        self.tipo = tk.StringVar(value="Cosenoidal")
        ttk.Combobox(
            controles,
            textvariable=self.tipo,
            values=("Cosenoidal", "Senoidal"),
            state="readonly",
            width=12
        ).grid(row=len(valores), column=1, pady=3)

        ttk.Button(
            marco, text="Simular", command=self.simular
        ).pack(fill="x", pady=(8, 3))

        ttk.Button(
            marco, text="Validar RK4", command=self.validar
        ).pack(fill="x", pady=3)

        self.boton_animacion = ttk.Button(
            marco, text="Pausar animación",
            command=self.alternar_animacion
        )
        self.boton_animacion.pack(fill="x", pady=3)

        ttk.Label(
            marco,
            text=(
                "La simulación usa sin(θ).\n"
                "La validación usa sin(θ) ≈ θ."
            )
        ).pack(anchor="w", pady=8)

        self.salida = tk.Text(marco, width=39, height=12, wrap="word")
        self.salida.pack(fill="x", pady=5)
        self.mostrar("Cambia valores y pulsa Simular.")

    def crear_graficas(self):
        """Crea dos gráficas y un panel de dibujo del péndulo."""
        self.figura = Figure(figsize=(9, 6), dpi=100)
        cuadricula = self.figura.add_gridspec(
            2, 2, width_ratios=(1.5, 1)
        )

        # Columna izquierda: ángulo arriba y torque abajo.
        self.ax_angulo = self.figura.add_subplot(cuadricula[0, 0])
        self.ax_torque = self.figura.add_subplot(
            cuadricula[1, 0], sharex=self.ax_angulo
        )

        # Columna derecha: dibujo del péndulo.
        self.ax_pendulo = self.figura.add_subplot(cuadricula[:, 1])
        self.ax_pendulo.set_title("Animación del péndulo")
        self.ax_pendulo.set_xlim(-1.3, 1.3)
        self.ax_pendulo.set_ylim(-1.35, 0.4)
        self.ax_pendulo.set_aspect("equal")
        self.ax_pendulo.axis("off")

        # Línea de equilibrio vertical y pivote fijo.
        self.ax_pendulo.axvline(0, color="gray", linestyle="--")
        self.ax_pendulo.plot(0, 0, "ko")

        # Elementos que moveremos en cada cuadro de la animación.
        self.varilla, = self.ax_pendulo.plot(
            [0, 0], [0, -1], color="steelblue", linewidth=5
        )
        self.masa = Circle((0, -1), 0.12, color="darkorange")
        self.ax_pendulo.add_patch(self.masa)

        self.texto_tiempo = self.ax_pendulo.text(
            0.04, 0.94, "t = 0.00 s\nθ = 0.0°",
            transform=self.ax_pendulo.transAxes,
            verticalalignment="top"
        )

        # Inserta la figura de Matplotlib dentro de la ventana Tkinter.
        self.canvas = FigureCanvasTkAgg(
            self.figura, master=self.ventana
        )
        self.canvas.get_tk_widget().pack(
            side="right", fill="both", expand=True
        )
        self.figura.subplots_adjust(
            left=0.08, right=0.97, top=0.93,
            bottom=0.09, wspace=0.35, hspace=0.35
        )

    def leer_datos(self):
        """Lee casillas y construye los parámetros del modelo."""
        v = {nombre: float(caja.get()) for nombre, caja in self.cajas.items()}

        if not all(math.isfinite(numero) for numero in v.values()):
            raise ValueError("Todos los valores deben ser números finitos.")

        p = {
            "m": v["m (kg)"],
            "L": v["L (m)"],
            "c": v["c (N·m·s/rad)"],
            "tau0": v["Torque τ₀ (N·m)"],
            "Omega": v["Frecuencia Ω (rad/s)"],
            "tipo": self.tipo.get()
        }
        inicial = (
            v["Ángulo inicial (rad)"],
            v["Velocidad inicial (rad/s)"]
        )
        h = v["Paso h (s)"]
        final = v["Tiempo final (s)"]

        if p["m"] <= 0 or p["L"] <= 0:
            raise ValueError("La masa y la longitud deben ser positivas.")
        if p["c"] < 0 or p["tau0"] < 0 or p["Omega"] < 0:
            raise ValueError("c, τ₀ y Ω no pueden ser negativos.")
        if h <= 0 or final <= 0:
            raise ValueError("El paso h y el tiempo final deben ser positivos.")

        return p, inicial, h, final

    def dibujar_resultados(self, tiempos, estados, torques, exacta=None):
        """Actualiza las gráficas con los datos recién calculados."""
        angulos = [estado[0] for estado in estados]

        self.ax_angulo.clear()
        self.ax_torque.clear()

        self.ax_angulo.plot(tiempos, angulos, label="RK4")
        if exacta is not None:
            self.ax_angulo.plot(
                tiempos, exacta, "--", label="Solución analítica"
            )
        self.ax_angulo.set_ylabel("Ángulo θ (rad)")
        self.ax_angulo.grid(True)
        self.ax_angulo.legend()

        self.ax_torque.plot(
            tiempos, torques, color="darkorange",
            label="Torque aplicado"
        )
        self.ax_torque.set_xlabel("Tiempo (s)")
        self.ax_torque.set_ylabel("Torque (N·m)")
        self.ax_torque.grid(True)
        self.ax_torque.legend()

        self.canvas.draw_idle()

    def iniciar_animacion(self, tiempos, estados):
        """Guarda los resultados y comienza a mover el dibujo."""
        if self.after_id is not None:
            self.ventana.after_cancel(self.after_id)

        self.tiempos_animacion = tiempos
        self.estados_animacion = estados
        self.indice = 0
        self.animando = True
        self.boton_animacion.config(text="Pausar animación")
        self.actualizar_pendulo()

    def actualizar_pendulo(self):
        """Coloca la masa según el ángulo en el punto actual."""
        if not self.animando or not self.estados_animacion:
            return

        t = self.tiempos_animacion[self.indice]
        theta = self.estados_animacion[self.indice][0]

        # La figura usa longitud 1: x=sin(theta), y=-cos(theta).
        x = math.sin(theta)
        y = -math.cos(theta)

        self.varilla.set_data([0, x], [0, y])
        self.masa.center = (x, y)
        self.texto_tiempo.set_text(
            f"t = {t:.2f} s\nθ = {math.degrees(theta):.1f}°"
        )
        self.canvas.draw_idle()

        # Saltamos algunos puntos para que el movimiento sea fluido.
        salto = max(1, len(self.estados_animacion) // 250)
        self.indice = (self.indice + salto) % len(self.estados_animacion)

        # Tkinter vuelve a llamar esta función después de 30 milisegundos.
        self.after_id = self.ventana.after(
            30, self.actualizar_pendulo
        )

    def alternar_animacion(self):
        """Pausa o reanuda el dibujo animado."""
        self.animando = not self.animando

        if self.animando:
            self.boton_animacion.config(text="Pausar animación")
            self.actualizar_pendulo()
        else:
            self.boton_animacion.config(text="Reanudar animación")
            if self.after_id is not None:
                self.ventana.after_cancel(self.after_id)
                self.after_id = None

    def simular(self):
        """Resuelve el modelo no lineal con los valores de la ventana."""
        try:
            p, inicial, h, final = self.leer_datos()
            t, y, q = integrar(p, inicial, h, final)

            self.dibujar_resultados(t, y, q)
            self.iniciar_animacion(t, y)
            self.mostrar(
                f"Simulación completa.\n"
                f"Puntos calculados: {len(t)}\n"
                "El modelo incluye sin(θ), sin aproximar el ángulo."
            )
        except Exception as error:
            messagebox.showerror("No se pudo simular", str(error))

    def validar(self):
        """Compara RK4 con la solución analítica del modelo linealizado."""
        try:
            p, _, h, final = self.leer_datos()
            datos = validar_rk4(p, h, final)

            self.dibujar_resultados(
                datos["tiempos"],
                datos["estados"],
                datos["torques"],
                datos["exacta"]
            )
            self.iniciar_animacion(datos["tiempos"], datos["estados"])

            texto = (
                "VALIDACIÓN DEL MODELO LINEALIZADO\n"
                "Se compara RK4 con la solución analítica.\n\n"
                "h (s)          Error máximo       Razón\n"
            )

            resultados = datos["resultados"]
            for i, (paso, error) in enumerate(resultados):
                razon = "-"
                if i > 0 and error > 0:
                    razon = f"{resultados[i-1][1] / error:.2f}"
                texto += f"{paso:<14.6g}{error:<19.6e}{razon}\n"

            texto += (
                "\nAl dividir h por 2, la razón de errores debe acercarse "
                "a 16 cuando RK4 está en su régimen de convergencia."
            )
            self.mostrar(texto)

        except Exception as error:
            messagebox.showerror("No se pudo validar", str(error))

    def mostrar(self, texto):
        """Escribe mensajes y resultados en el cuadro inferior."""
        self.salida.delete("1.0", tk.END)
        self.salida.insert(tk.END, texto)


def iniciar_interfaz():
    """Crea la ventana principal y mantiene abierto el programa."""
    ventana = tk.Tk()
    InterfazPendulo(ventana)
    ventana.mainloop()
