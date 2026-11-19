"""
Universidad Nacional de Colombia - Sede Medellín
Curso: Programación Orientada a Objetos 2026-2S
Estudiante: Leonardo Angel Iriarte Arrieta

Ejercicio 8.5 - Interfaz gráfica de usuario: Hotel

Programa que gestiona el ingreso y la salida de los huéspedes de un hotel de
diez habitaciones simples. Las habitaciones 1 a 5 cuestan $120.000 por día y
las habitaciones 6 a 10 cuestan $160.000 por día.

El menú principal ofrece dos opciones:
  - Consultar habitaciones: muestra las diez habitaciones y su estado, permite
    elegir una disponible y registrar el ingreso del huésped.
  - Salida de huéspedes: pide el número de habitación, calcula los días de
    alojamiento y el total a pagar, y libera la habitación.

Las fechas se escriben con el formato aaaa-mm-dd.
"""

from __future__ import annotations

import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, simpledialog, ttk

FORMATO_FECHA = "%Y-%m-%d"
FUENTE_TITULO = ("Arial", 13, "bold")
FUENTE_NEGRITA = ("Arial", 10, "bold")
COLOR_DISPONIBLE = "#2e7d32"
COLOR_ERROR = "#b00020"


# ---------------------------------------------------------------------------
# Excepciones propias
# ---------------------------------------------------------------------------
class HotelError(Exception):
    """Error base de las reglas de negocio del hotel."""


class HabitacionInvalidaError(HotelError):
    """El número de habitación no es un entero válido entre 1 y 10."""


class HabitacionOcupadaError(HotelError):
    """Se intenta ocupar una habitación que ya está ocupada."""


class HabitacionNoOcupadaError(HotelError):
    """Se intenta entregar una habitación que no está ocupada."""


class DatoInvalidoError(HotelError):
    """Un campo obligatorio está vacío o tiene un formato incorrecto."""


# ---------------------------------------------------------------------------
# Lógica del negocio
# ---------------------------------------------------------------------------
class Validaciones:
    """Convierte y valida los textos que el usuario escribe en la interfaz."""

    @staticmethod
    def numero_habitacion(texto: str, cantidad: int) -> int:
        """Convierte el texto a un número de habitación entre 1 y cantidad."""
        texto = texto.strip()
        if not (texto.isascii() and texto.isdigit()):
            raise HabitacionInvalidaError("Campo nulo o error en formato de número")
        numero = int(texto)
        if not 1 <= numero <= cantidad:
            raise HabitacionInvalidaError(
                f"El número de habitación debe estar entre 1 y {cantidad}"
            )
        return numero

    @staticmethod
    def texto_obligatorio(valor: str, campo: str) -> str:
        """Verifica que el campo no esté vacío y devuelve el texto sin espacios."""
        valor = valor.strip()
        if not valor:
            raise DatoInvalidoError(f"El campo «{campo}» es obligatorio")
        return valor

    @staticmethod
    def documento(valor: str) -> int:
        """Verifica que el documento de identidad sea obligatorio y numérico."""
        valor = Validaciones.texto_obligatorio(valor, "Doc. Identidad")
        if not (valor.isascii() and valor.isdigit()):
            raise DatoInvalidoError("El documento de identidad debe contener solo dígitos")
        return int(valor)

    @staticmethod
    def fecha(valor: str, campo: str) -> date:
        """Convierte un texto aaaa-mm-dd a fecha."""
        valor = Validaciones.texto_obligatorio(valor, campo)
        try:
            return datetime.strptime(valor, FORMATO_FECHA).date()
        except ValueError:
            raise DatoInvalidoError(
                f"La {campo.lower()} no está en el formato solicitado (aaaa-mm-dd)"
            ) from None


class Huesped:
    """Huésped que ocupa una habitación desde una fecha de ingreso."""

    def __init__(
        self, nombres: str, apellidos: str, documento_identidad: int, fecha_ingreso: date
    ) -> None:
        self._nombres = nombres
        self._apellidos = apellidos
        self._documento_identidad = documento_identidad
        self._fecha_ingreso = fecha_ingreso

    @property
    def nombres(self) -> str:
        return self._nombres

    @property
    def apellidos(self) -> str:
        return self._apellidos

    @property
    def documento_identidad(self) -> int:
        return self._documento_identidad

    @property
    def fecha_ingreso(self) -> date:
        return self._fecha_ingreso

    def obtener_dias_alojamiento(self, fecha_salida: date) -> int:
        """Días entre el ingreso y la salida; la salida debe ser posterior al ingreso."""
        dias = (fecha_salida - self._fecha_ingreso).days
        if dias <= 0:
            raise DatoInvalidoError("La fecha de salida debe ser mayor que la fecha de ingreso")
        return dias


class Habitacion:
    """Habitación del hotel: está disponible o la ocupa un único huésped."""

    def __init__(self, numero: int, precio_dia: int) -> None:
        self._numero = numero
        self._precio_dia = precio_dia
        self._huesped: Huesped | None = None

    @property
    def numero(self) -> int:
        return self._numero

    @property
    def precio_dia(self) -> int:
        return self._precio_dia

    @property
    def huesped(self) -> Huesped | None:
        return self._huesped

    def esta_disponible(self) -> bool:
        return self._huesped is None

    def estado(self) -> str:
        return "Disponible" if self.esta_disponible() else "No disponible"

    def ocupar(self, huesped: Huesped) -> None:
        if not self.esta_disponible():
            raise HabitacionOcupadaError("La habitación está ocupada")
        self._huesped = huesped

    def liberar(self) -> None:
        if self.esta_disponible():
            raise HabitacionNoOcupadaError("La habitación ingresada no ha sido ocupada")
        self._huesped = None

    def calcular_total(self, dias: int) -> int:
        return dias * self._precio_dia


class Hotel:
    """Hotel compuesto por diez habitaciones que se ocupan y se liberan."""

    CANTIDAD_HABITACIONES = 10
    HABITACIONES_PRECIO_BASE = 5
    PRECIO_BASE = 120000
    PRECIO_SUPERIOR = 160000

    def __init__(self) -> None:
        self._habitaciones: list[Habitacion] = [
            Habitacion(
                numero,
                self.PRECIO_BASE
                if numero <= self.HABITACIONES_PRECIO_BASE
                else self.PRECIO_SUPERIOR,
            )
            for numero in range(1, self.CANTIDAD_HABITACIONES + 1)
        ]

    def obtener_habitaciones(self) -> list[Habitacion]:
        return list(self._habitaciones)

    def obtener_habitacion(self, numero: int) -> Habitacion:
        if not 1 <= numero <= self.CANTIDAD_HABITACIONES:
            raise HabitacionInvalidaError(
                f"El número de habitación debe estar entre 1 y {self.CANTIDAD_HABITACIONES}"
            )
        return self._habitaciones[numero - 1]

    def esta_ocupada(self, numero: int) -> bool:
        return not self.obtener_habitacion(numero).esta_disponible()

    def obtener_habitacion_ocupada(self, numero: int) -> Habitacion:
        habitacion = self.obtener_habitacion(numero)
        if habitacion.esta_disponible():
            raise HabitacionNoOcupadaError("La habitación ingresada no ha sido ocupada")
        return habitacion

    def buscar_fecha_ingreso_habitacion(self, numero: int) -> date:
        return self.obtener_habitacion_ocupada(numero).huesped.fecha_ingreso

    def registrar_ingreso(self, numero: int, huesped: Huesped) -> None:
        self.obtener_habitacion(numero).ocupar(huesped)

    def calcular_alojamiento(self, numero: int, fecha_salida: date) -> tuple[int, int]:
        """Devuelve (días de alojamiento, total a pagar) de la habitación ocupada."""
        habitacion = self.obtener_habitacion_ocupada(numero)
        dias = habitacion.huesped.obtener_dias_alojamiento(fecha_salida)
        return dias, habitacion.calcular_total(dias)

    def registrar_salida(self, numero: int) -> None:
        self.obtener_habitacion(numero).liberar()


# ---------------------------------------------------------------------------
# Interfaz gráfica (Tkinter)
# ---------------------------------------------------------------------------
class VentanaHotel(tk.Toplevel):
    """Ventana secundaria del hotel: tamaño fijo, centrada y asociada a la principal."""

    def __init__(self, master: tk.Misc, hotel: Hotel, titulo: str) -> None:
        super().__init__(master)
        self._hotel = hotel
        self.title(titulo)
        self.resizable(False, False)
        self.transient(master)

    @staticmethod
    def centrar(ventana: tk.Misc) -> None:
        """Ubica la ventana en el centro de la pantalla."""
        ventana.update_idletasks()
        ancho, alto = ventana.winfo_reqwidth(), ventana.winfo_reqheight()
        x = (ventana.winfo_screenwidth() - ancho) // 2
        y = (ventana.winfo_screenheight() - alto) // 2
        ventana.geometry(f"+{x}+{y}")

    def hacer_modal(self) -> None:
        """Bloquea las demás ventanas hasta cerrar esta."""
        self.wait_visibility()
        self.grab_set()
        self.focus_set()


class VentanaHabitaciones(VentanaHotel):
    """Muestra las diez habitaciones y su estado, y permite elegir la que se ocupará."""

    COLUMNAS = 5

    def __init__(self, master: tk.Misc, hotel: Hotel) -> None:
        super().__init__(master, hotel, "Habitaciones")
        self._etiquetas_estado: dict[int, ttk.Label] = {}
        self._var_habitacion = tk.IntVar(value=1)
        self._crear_widgets()
        self.actualizar()
        self.bind("<Escape>", lambda _evento: self.destroy())
        self.centrar(self)
        self.hacer_modal()

    def _crear_widgets(self) -> None:
        cuadricula = ttk.Frame(self, padding=(20, 20, 20, 5))
        cuadricula.grid(row=0, column=0)
        for habitacion in self._hotel.obtener_habitaciones():
            fila, columna = divmod(habitacion.numero - 1, self.COLUMNAS)
            celda = ttk.Frame(cuadricula, padding=(10, 8))
            celda.grid(row=fila, column=columna, padx=8, pady=8, sticky="w")
            ttk.Label(celda, text=f"Habitación {habitacion.numero}", font=FUENTE_NEGRITA).pack(
                anchor="w"
            )
            etiqueta = ttk.Label(celda)
            etiqueta.pack(anchor="w")
            ttk.Label(celda, text=f"${habitacion.precio_dia:,}/día".replace(",", ".")).pack(
                anchor="w"
            )
            self._etiquetas_estado[habitacion.numero] = etiqueta

        seleccion = ttk.Frame(self, padding=(20, 5, 20, 20))
        seleccion.grid(row=1, column=0)
        ttk.Label(seleccion, text="Habitación a ocupar:", font=FUENTE_NEGRITA).grid(
            row=0, column=0, padx=5
        )
        ttk.Spinbox(
            seleccion,
            from_=1,
            to=Hotel.CANTIDAD_HABITACIONES,
            width=4,
            state="readonly",
            textvariable=self._var_habitacion,
        ).grid(row=0, column=1, padx=5)
        ttk.Button(seleccion, text="Aceptar", command=self.aceptar).grid(
            row=0, column=2, padx=15
        )

    def actualizar(self) -> None:
        """Refresca el estado de cada habitación según el hotel."""
        for habitacion in self._hotel.obtener_habitaciones():
            self._etiquetas_estado[habitacion.numero].configure(
                text=habitacion.estado(),
                foreground=COLOR_DISPONIBLE if habitacion.esta_disponible() else COLOR_ERROR,
            )

    def aceptar(self) -> None:
        numero = self._var_habitacion.get()
        if self._hotel.esta_ocupada(numero):
            messagebox.showerror("Error", "La habitación está ocupada", parent=self)
            self.actualizar()
            return
        principal = self.master
        self.destroy()
        VentanaIngreso(principal, self._hotel, numero)


class VentanaIngreso(VentanaHotel):
    """Pide la fecha de ingreso y los datos del huésped que ocupará la habitación."""

    def __init__(self, master: tk.Misc, hotel: Hotel, numero_habitacion: int) -> None:
        super().__init__(master, hotel, "Ingreso")
        self._numero = numero_habitacion
        self._var_fecha = tk.StringVar(value=date.today().strftime(FORMATO_FECHA))
        self._var_nombre = tk.StringVar()
        self._var_apellidos = tk.StringVar()
        self._var_documento = tk.StringVar()
        self._crear_widgets()
        self.bind("<Return>", lambda _evento: self.aceptar())
        self.bind("<Escape>", lambda _evento: self.destroy())
        self.centrar(self)
        self.hacer_modal()

    def _crear_widgets(self) -> None:
        marco = ttk.Frame(self, padding=15)
        marco.grid(row=0, column=0)
        ttk.Label(marco, text=f"Habitación: {self._numero}", font=FUENTE_NEGRITA).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )
        ttk.Label(marco, text="Fecha (aaaa-mm-dd):").grid(row=1, column=0, sticky="w", pady=3)
        entrada_fecha = ttk.Entry(marco, textvariable=self._var_fecha, width=24)
        entrada_fecha.grid(row=1, column=1, padx=(8, 0), pady=3)
        entrada_fecha.focus_set()

        ttk.Label(marco, text="Huésped", font=FUENTE_NEGRITA).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(8, 3)
        )
        campos_huesped = (
            ("Nombre:", self._var_nombre),
            ("Apellidos:", self._var_apellidos),
            ("Doc. Identidad:", self._var_documento),
        )
        for fila, (etiqueta, variable) in enumerate(campos_huesped, start=3):
            ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="w", pady=3)
            ttk.Entry(marco, textvariable=variable, width=24).grid(
                row=fila, column=1, padx=(8, 0), pady=3
            )

        botones = ttk.Frame(marco)
        botones.grid(row=6, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(botones, text="Aceptar", command=self.aceptar).grid(row=0, column=0, padx=5)
        ttk.Button(botones, text="Cancelar", command=self.destroy).grid(row=0, column=1, padx=5)

    def aceptar(self) -> None:
        try:
            fecha = Validaciones.fecha(self._var_fecha.get(), "Fecha de ingreso")
            nombres = Validaciones.texto_obligatorio(self._var_nombre.get(), "Nombre")
            apellidos = Validaciones.texto_obligatorio(self._var_apellidos.get(), "Apellidos")
            documento = Validaciones.documento(self._var_documento.get())
            self._hotel.registrar_ingreso(
                self._numero, Huesped(nombres, apellidos, documento, fecha)
            )
        except HotelError as error:
            messagebox.showerror("Error", str(error), parent=self)
            return
        messagebox.showinfo("Mensaje", "El huésped ha sido registrado", parent=self)
        self.destroy()


class VentanaSalida(VentanaHotel):
    """Registra la salida de un huésped: calcula los días, el total y libera la habitación."""

    def __init__(self, master: tk.Misc, hotel: Hotel, numero_habitacion: int) -> None:
        super().__init__(master, hotel, "Salida huéspedes")
        self._numero = numero_habitacion
        self._fecha_ingreso = hotel.buscar_fecha_ingreso_habitacion(numero_habitacion)
        self._var_fecha_salida = tk.StringVar()
        self._var_estado = tk.StringVar(value="Ingrese la fecha de salida")
        self._var_dias = tk.StringVar()
        self._var_total = tk.StringVar()
        self._crear_widgets()
        self._reiniciar_resultado()
        self._var_fecha_salida.trace_add("write", self._validar_fecha)
        self.bind("<Escape>", lambda _evento: self.destroy())
        self.centrar(self)
        self.hacer_modal()

    def _crear_widgets(self) -> None:
        marco = ttk.Frame(self, padding=15)
        marco.grid(row=0, column=0)
        ttk.Label(marco, text=f"Habitación: {self._numero}", font=FUENTE_NEGRITA).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            marco, text=f"Fecha de ingreso: {self._fecha_ingreso.strftime(FORMATO_FECHA)}"
        ).grid(row=1, column=0, sticky="w", pady=3)
        ttk.Label(marco, text="Fecha de salida (aaaa-mm-dd):").grid(
            row=2, column=0, sticky="w", pady=(8, 3)
        )
        entrada = ttk.Entry(marco, textvariable=self._var_fecha_salida, width=24)
        entrada.grid(row=3, column=0, sticky="ew")
        entrada.focus_set()
        self._lbl_estado = ttk.Label(marco, textvariable=self._var_estado)
        self._lbl_estado.grid(row=4, column=0, sticky="w", pady=3)
        self._btn_calcular = ttk.Button(marco, text="Calcular", command=self.calcular)
        self._btn_calcular.grid(row=5, column=0, sticky="ew", pady=(6, 3))
        self._btn_calcular.state(["disabled"])  # Se habilita con una fecha de salida válida
        ttk.Label(marco, textvariable=self._var_dias, font=FUENTE_NEGRITA).grid(
            row=6, column=0, sticky="w", pady=3
        )
        ttk.Label(marco, textvariable=self._var_total, font=FUENTE_NEGRITA).grid(
            row=7, column=0, sticky="w", pady=3
        )
        self._btn_registrar = ttk.Button(
            marco, text="Registrar salida", command=self.registrar_salida
        )
        self._btn_registrar.grid(row=8, column=0, sticky="ew", pady=(6, 0))

    @staticmethod
    def _formato_pesos(valor: int) -> str:
        return f"${valor:,}".replace(",", ".")

    def _reiniciar_resultado(self) -> None:
        """Borra el cálculo anterior y deshabilita el registro de la salida."""
        self._var_dias.set("Cantidad de días: ")
        self._var_total.set("Total: $")
        self._btn_registrar.state(["disabled"])

    def _validar_fecha(self, *_argumentos: object) -> None:
        """Habilita 'Calcular' solo cuando la fecha de salida es válida."""
        self._reiniciar_resultado()
        try:
            fecha = Validaciones.fecha(self._var_fecha_salida.get(), "Fecha de salida")
            self._hotel.calcular_alojamiento(self._numero, fecha)
        except HotelError as error:
            self._btn_calcular.state(["disabled"])
            self._var_estado.set(str(error))
            self._lbl_estado.configure(foreground=COLOR_ERROR)
        else:
            self._btn_calcular.state(["!disabled"])
            self._var_estado.set("Fecha válida")
            self._lbl_estado.configure(foreground=COLOR_DISPONIBLE)

    def calcular(self) -> None:
        try:
            fecha = Validaciones.fecha(self._var_fecha_salida.get(), "Fecha de salida")
            dias, total = self._hotel.calcular_alojamiento(self._numero, fecha)
        except HotelError as error:
            messagebox.showerror("Error", str(error), parent=self)
            return
        self._var_dias.set(f"Cantidad de días: {dias}")
        self._var_total.set(f"Total: {self._formato_pesos(total)}")
        self._btn_registrar.state(["!disabled"])

    def registrar_salida(self) -> None:
        try:
            self._hotel.registrar_salida(self._numero)
        except HotelError as error:
            messagebox.showerror("Error", str(error), parent=self)
            return
        messagebox.showinfo("Mensaje", "Se ha registrado la salida del huésped", parent=self)
        self.destroy()


class AppHotel:
    """Ventana principal con el menú del hotel (usa Hotel y las ventanas secundarias)."""

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._hotel = Hotel()
        root.title("Hotel")
        root.resizable(False, False)

        barra = tk.Menu(root)
        menu = tk.Menu(barra, tearoff=False)
        menu.add_command(label="Consultar habitaciones", command=self.consultar_habitaciones)
        menu.add_command(label="Salida de huéspedes", command=self.salida_huespedes)
        barra.add_cascade(label="Menú", menu=menu)
        root.config(menu=barra)

        marco = ttk.Frame(root, padding=(40, 30))
        marco.grid(row=0, column=0)
        ttk.Label(marco, text="Hotel", font=FUENTE_TITULO).grid(row=0, column=0)
        ttk.Label(marco, text="Gestión de ingreso y salida de huéspedes").grid(
            row=1, column=0, pady=(6, 0)
        )
        ttk.Label(marco, text="Use el menú «Menú» para continuar.").grid(
            row=2, column=0, pady=(2, 0)
        )
        VentanaHotel.centrar(root)

    def consultar_habitaciones(self) -> None:
        VentanaHabitaciones(self._root, self._hotel)

    def salida_huespedes(self) -> None:
        texto = simpledialog.askstring(
            "Salida de huéspedes", "Ingrese número de habitación", parent=self._root
        )
        if texto is None:  # El usuario canceló el cuadro de diálogo
            return
        try:
            numero = Validaciones.numero_habitacion(texto, Hotel.CANTIDAD_HABITACIONES)
            self._hotel.obtener_habitacion_ocupada(numero)
        except HotelError as error:
            messagebox.showerror("Error", str(error), parent=self._root)
            return
        VentanaSalida(self._root, self._hotel, numero)


def main() -> None:
    root = tk.Tk()
    AppHotel(root)
    root.mainloop()


if __name__ == "__main__":
    main()
