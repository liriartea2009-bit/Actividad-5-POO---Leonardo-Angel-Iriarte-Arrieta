import os
import tkinter as tk
from enum import Enum
from tkinter import ttk, filedialog, messagebox


class TipoCargo(Enum):
    DIRECTIVO = "Directivo"
    ESTRATEGICO = "Estratégico"
    OPERATIVO = "Operativo"


class TipoGenero(Enum):
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"


class Empleado:
    def __init__(self, nombre: str, apellidos: str, cargo: TipoCargo, genero: TipoGenero,
                 salario_dia: float, dias_trabajados: int, otros_ingresos: float,
                 pagos_salud: float, aporte_pensiones: float):
        self.nombre = nombre
        self.apellidos = apellidos
        self.cargo = cargo
        self.genero = genero
        self.salario_dia = salario_dia
        self.dias_trabajados = dias_trabajados
        self.otros_ingresos = otros_ingresos
        self.pagos_salud = pagos_salud
        self.aporte_pensiones = aporte_pensiones

    def calcular_nomina(self) -> float:
        return ((self.salario_dia * self.dias_trabajados) + self.otros_ingresos
                - self.pagos_salud - self.aporte_pensiones)


class ListaEmpleados:
    def __init__(self):
        self.empleados = []

    def agregar_empleado(self, empleado: Empleado) -> None:
        self.empleados.append(empleado)

    def calcular_total_nomina(self) -> float:
        return sum(empleado.calcular_nomina() for empleado in self.empleados)

    def obtener_matriz(self) -> list:
        return [[e.nombre, e.apellidos, f"{e.calcular_nomina():.2f}"] for e in self.empleados]

    def convertir_texto(self) -> str:
        texto = ""
        for e in self.empleados:
            texto += (f"Nombre = {e.nombre}\n"
                      f"Apellidos = {e.apellidos}\n"
                      f"Cargo = {e.cargo.value}\n"
                      f"Género = {e.genero.value}\n"
                      f"Salario por día = ${e.salario_dia}\n"
                      f"Días trabajados = {e.dias_trabajados}\n"
                      f"Otros ingresos = ${e.otros_ingresos}\n"
                      f"Pagos por salud = ${e.pagos_salud}\n"
                      f"Aportes pensiones = ${e.aporte_pensiones}\n"
                      f"Salario mensual = ${e.calcular_nomina():.2f}\n"
                      "---------\n")
        texto += f"Total nómina = ${self.calcular_total_nomina():.2f}"
        return texto


class VentanaAgregarEmpleado:
    def __init__(self, root: tk.Tk, lista: ListaEmpleados):
        self.lista = lista
        self.ventana = tk.Toplevel(root)
        self.ventana.title("Agregar Empleado")
        self.ventana.geometry("340x420")
        self.ventana.resizable(False, False)
        self.campos = {}
        self.var_genero = tk.StringVar(value=TipoGenero.MASCULINO.value)
        self.cmb_cargo = None
        self.spn_dias = None
        self.inicio()

    def inicio(self) -> None:
        marco = ttk.Frame(self.ventana, padding=20)
        marco.pack(fill="both", expand=True)
        orden = ("Nombre", "Apellidos", "Cargo", "Género", "Salario por día",
                 "Días trabajados al mes", "Otros ingresos", "Pagos por salud", "Aporte pensiones")
        for fila, etiqueta in enumerate(orden):
            ttk.Label(marco, text=f"{etiqueta}:").grid(row=fila, column=0, sticky="w", pady=4)
            if etiqueta == "Cargo":
                self.cmb_cargo = ttk.Combobox(marco, values=[c.value for c in TipoCargo],
                                              state="readonly", width=18)
                self.cmb_cargo.current(0)
                self.cmb_cargo.grid(row=fila, column=1, sticky="w", padx=10)
            elif etiqueta == "Género":
                grupo = ttk.Frame(marco)
                for tipo in TipoGenero:
                    ttk.Radiobutton(grupo, text=tipo.value, value=tipo.value,
                                    variable=self.var_genero).pack(side="left", padx=(0, 8))
                grupo.grid(row=fila, column=1, sticky="w", padx=10)
            elif etiqueta == "Días trabajados al mes":
                self.spn_dias = ttk.Spinbox(marco, from_=1, to=31, width=6)
                self.spn_dias.set(30)
                self.spn_dias.grid(row=fila, column=1, sticky="w", padx=10)
            else:
                entrada = ttk.Entry(marco, width=21)
                entrada.grid(row=fila, column=1, sticky="w", padx=10)
                self.campos[etiqueta] = entrada
        botones = ttk.Frame(marco)
        botones.grid(row=len(orden), column=0, columnspan=2, pady=18)
        ttk.Button(botones, text="Agregar", command=self.anadir_empleado).pack(side="left", padx=6)
        ttk.Button(botones, text="Borrar", command=self.limpiar_campos).pack(side="left", padx=6)

    def anadir_empleado(self) -> None:
        try:
            nombre = self.campos["Nombre"].get().strip()
            apellidos = self.campos["Apellidos"].get().strip()
            if not nombre or not apellidos:
                raise ValueError
            cargo = TipoCargo(self.cmb_cargo.get())
            genero = TipoGenero(self.var_genero.get())
            salario_dia = float(self.campos["Salario por día"].get().replace(",", "."))
            dias = int(self.spn_dias.get())
            otros = float(self.campos["Otros ingresos"].get().replace(",", "."))
            salud = float(self.campos["Pagos por salud"].get().replace(",", "."))
            pensiones = float(self.campos["Aporte pensiones"].get().replace(",", "."))
            if not 1 <= dias <= 31 or min(salario_dia, otros, salud, pensiones) < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Campo nulo o error en formato de número",
                                 parent=self.ventana)
            return
        self.lista.agregar_empleado(Empleado(nombre, apellidos, cargo, genero, salario_dia,
                                             dias, otros, salud, pensiones))
        messagebox.showinfo("Mensaje", "El empleado ha sido agregado", parent=self.ventana)
        self.limpiar_campos()

    def limpiar_campos(self) -> None:
        for entrada in self.campos.values():
            entrada.delete(0, tk.END)
        self.cmb_cargo.current(0)
        self.var_genero.set(TipoGenero.MASCULINO.value)
        self.spn_dias.set(30)


class VentanaNomina:
    def __init__(self, root: tk.Tk, lista: ListaEmpleados):
        self.lista = lista
        self.ventana = tk.Toplevel(root)
        self.ventana.title("Nómina de Empleados")
        self.ventana.geometry("420x300")
        self.ventana.resizable(False, False)
        self.tabla = None
        self.lbl_total = None
        self.inicio()

    def inicio(self) -> None:
        ttk.Label(self.ventana, text="Lista de empleados:").pack(anchor="w", padx=20, pady=(15, 5))
        self.tabla = ttk.Treeview(self.ventana, columns=("nombre", "apellidos", "sueldo"),
                                  show="headings", height=7)
        for columna, titulo, ancho in (("nombre", "NOMBRE", 120), ("apellidos", "APELLIDOS", 140),
                                       ("sueldo", "SUELDO", 110)):
            self.tabla.heading(columna, text=titulo)
            self.tabla.column(columna, width=ancho, anchor="w")
        self.tabla.pack(padx=20)
        for fila in self.lista.obtener_matriz():
            self.tabla.insert("", tk.END, values=fila)
        total = self.lista.calcular_total_nomina()
        self.lbl_total = ttk.Label(self.ventana, text=f"Total nómina mensual = $ {total:.2f}")
        self.lbl_total.pack(anchor="w", padx=20, pady=12)


class VentanaPrincipal:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.empleados = ListaEmpleados()
        self.barra_menu = tk.Menu(root)
        self.menu_opciones = tk.Menu(self.barra_menu, tearoff=0)
        self.root.title("Nómina")
        self.root.geometry("280x380")
        self.root.resizable(False, False)
        self.inicio()

    def inicio(self) -> None:
        self.menu_opciones.add_command(label="Agregar empleado", command=self.abrir_agregar_empleado)
        self.menu_opciones.add_command(label="Calcular nómina", command=self.abrir_nomina)
        self.menu_opciones.add_separator()
        self.menu_opciones.add_command(label="Guardar archivo", command=self.guardar_archivo)
        self.barra_menu.add_cascade(label="Menú", menu=self.menu_opciones)
        self.root.config(menu=self.barra_menu)

    def abrir_agregar_empleado(self) -> None:
        VentanaAgregarEmpleado(self.root, self.empleados)

    def abrir_nomina(self) -> None:
        VentanaNomina(self.root, self.empleados)

    def guardar_archivo(self) -> None:
        carpeta = filedialog.askdirectory(title="Seleccione la carpeta de destino")
        if not carpeta:
            return
        try:
            ruta = os.path.join(carpeta, "Nómina.txt")
            with open(ruta, "w", encoding="utf-8") as archivo:
                archivo.write(self.empleados.convertir_texto())
        except OSError:
            messagebox.showerror("Error", "No se pudo crear el archivo Nómina.txt")
            return
        messagebox.showinfo("Mensaje", f"El archivo de la nómina Nómina.txt se ha creado en {carpeta}")


class Principal:
    @staticmethod
    def main() -> None:
        root = tk.Tk()
        VentanaPrincipal(root)
        root.mainloop()


if __name__ == "__main__":
    Principal.main()
