# ==========================================================
#  Proyecto: Herramienta para el análisis multitemporal
#            de cuerpos de agua
#  Autor: Xavier Escobar Arteus18
#  ==========================================================
import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsDropShadowEffect, QSizeGrip, QMessageBox, QVBoxLayout, QHeaderView
from PySide6.QtCore import QFile, Qt, QStandardPaths, QTimer
from PySide6.QtGui import QColor, QPixmap, QImage
from PySide6 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
import rasterio
from datetime import datetime

class Resultados(QMainWindow):
    def __init__(self, parent=None, codigo=None):
        super().__init__(None)
        
        self._parent_geo = None
        if parent is not None:
            self._parent_geo = parent.saveGeometry()

        # Configuración de la ventana
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1)
        self.clickPosition = None
        self.codigo=codigo
        
        # Establecer el mismo tamaño que la ventana principal
        if parent:
            self.setGeometry(parent.geometry())  # Ajusta el tamaño de la nueva ventana al de la ventana principal

        # Cerrar la ventana principal (el 'parent') al abrir esta ventana
        if parent:
            parent.close()

        # Cargar el archivo .ui para la nueva ventana
        self.cargar_ui()

        # Configuración de botones y acciones
        self.configurar_botones()
        

        # Configuración de sombra en los widgets
        self.agregar_sombra_widgets()

        # Redimensionamiento de la ventana
        self.configurar_redimensionamiento()

        # Conectar eventos de movimiento de la ventana
        self.configurar_eventos_movimiento()
        
        self.tbl = self.ventana.findChild(QtWidgets.QTableWidget, "tbl_Datos")
        if self.tbl is None:
            raise RuntimeError("No existe QTableWidget con nombre 'tbl_Datos' en tu .ui")
       

        # Buscar los datos en la base de datos con el nombre
        self.buscar_datos()
        
        
        
    def cargar_ui(self):
        """Cargar el archivo .ui y establecer la ventana principal"""
        ui_file = QFile(r'C:\Users\LENOVO\Documents\CuerposDeAgua\UI\VentanaResultados.ui')  # Ruta al archivo .ui de la nueva ventana
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ventana = loader.load(ui_file)
        ui_file.close()

        if self.ventana is None:
            print("No se pudo cargar la interfaz.")
            sys.exit(-1)

        self.setCentralWidget(self.ventana)  # Establecer el widget cargado como central
        self.ventana.frm_Graficos.hide()
        self.ventana.frm_Tablas.hide()
        
        
    def configurar_botones(self):
        """Configurar los botones de la interfaz"""
        # Ocultar el botón 'btn_Normal' inicialmente
        self.ventana.btn_Normal.hide()
        self.ventana.comboBox_3.hide()
        self.ventana.comboBox_4.hide()
        self.ventana.label_14.hide()
        self.ventana.label_15.hide()
        self.ventana.comboBox_6.hide()
        self.ventana.comboBox_7.hide()
        self.ventana.label_16.hide()
        self.ventana.label_17.hide()
        
        self.ventana.btn_Minimizar.clicked.connect(self.control_bt_minimizar)
        self.ventana.btn_Maximizar.clicked.connect(self.control_bt_maximizar)
        self.ventana.btn_Normal.clicked.connect(self.control_bt_normal)
        self.ventana.btn_Cerrar.clicked.connect(self.control_bt_Cerrar)
        
       
        self.ventana.btn_Volver.clicked.connect(self.volver_al_menu_principal)
        self.ventana.btn_Img.clicked.connect(self.abrir_cargar_imagen)
        self.ventana.tbtn_Graficos.clicked.connect(self.contenido_Graficos)
        self.ventana.tbtn_Tablas.clicked.connect(self.contenido_Tablas)
        self.ventana.btn_Eliminar.clicked.connect(self.eliminar_medicion)
        self.ventana.lst_Fechas.itemClicked.connect(self.buscar_registro)
        self.ventana.Cbox_Vistas.currentIndexChanged.connect(self.mostrar_vista)
        self.ventana.Cbox_Graficos.currentTextChanged.connect(self.graficar_seleccion)

    def agregar_sombra_widgets(self):
        
        
        """Agregar sombra a los widgets especificados"""
        widgets = [self.ventana.btn_Eliminar, self.ventana.btn_Img, self.ventana.btn_Volver, self.ventana.Cbox_Vistas, self.ventana.lst_Fechas]
        for widget in widgets:
            self.sombra_frame(widget)

    def configurar_redimensionamiento(self):
        """Configurar el redimensionamiento de la ventana con un 'grip'"""
        self.gripSize = 10
        self.grip = QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)  # Definir tamaño del grip
        self.grip.move(self.ventana.width() - self.gripSize, self.ventana.height() - self.gripSize)  # Ubicar el grip en la esquina inferior derecha

    def configurar_eventos_movimiento(self):
        # Conectar los eventos de movimiento de la ventana
        self.ventana.frame_superior.mousePressEvent = self.mousePressEvent
        self.ventana.frame_superior.mouseMoveEvent = self.mouseMoveEvent

    def control_bt_minimizar(self):
        """Minimizar la ventana"""
        self.showMinimized()

    def control_bt_normal(self):
        """Restaurar la ventana al tamaño normal"""
        self.showNormal()
        self.ventana.btn_Normal.hide()
        self.ventana.btn_Maximizar.show()

    def control_bt_maximizar(self):
        """Maximizar la ventana"""
        self.showMaximized()
        self.ventana.btn_Maximizar.hide()
        self.ventana.btn_Normal.show()
         
    def control_bt_Cerrar(self):
        self.close()  # Cerrar la ventana principal
        QApplication.quit()

    def mousePressEvent(self, event):
        """Captura la posición del clic inicial"""
        if event.buttons() == QtCore.Qt.LeftButton:
            self.clickPosition = event.globalPos()  # Registra la posición cuando se hace clic
            event.accept()  # Asegura que el evento se acepte

    def mouseMoveEvent(self, event):
        """Mover la ventana mientras el ratón está presionado"""
        if not self.isMaximized() and event.buttons() == QtCore.Qt.LeftButton:
            if self.clickPosition is not None:
                click_pos = self.clickPosition if isinstance(self.clickPosition, QtCore.QPoint) else self.clickPosition.toPoint()
                global_pos = event.globalPos()
                delta = global_pos - click_pos
                self.move(self.pos() + delta)
                self.clickPosition = global_pos
            event.accept()

        # Maximizar la ventana si el ratón está cerca del borde superior
        if event.globalPos().y() <= 10:
            self.showMaximized()
            self.ventana.btn_Maximizar.hide()
            self.ventana.btn_Normal.show()
        else:
            self.showNormal()
            self.ventana.btn_Normal.hide()
            self.ventana.btn_Maximizar.show()

    def sombra_frame(self, frame):
        """Agregar sombra a los widgets"""
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(40)
        sombra.setXOffset(8)
        sombra.setYOffset(8)
        sombra.setColor(QColor(39, 173, 194, 255))  # Color de la sombra
        frame.setGraphicsEffect(sombra)

    def resizeEvent(self, event):
        """Actualizar la posición del 'grip' al redimensionar la ventana"""
        rect = self.rect()
        self.grip.move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)  # Mover el grip al redimensionar

    def buscar_datos(self):
        """Buscar el nombre en la base de datos y obtener el código y la ubicación"""
        try:
            # Ruta del archivo Excel
            docs = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
            self.archivo_excel = os.path.join(docs, "CuerposDeAgua", "BD", "BaseCuerposDeAgua.xlsx")

            # Cargar el archivo Excel
            df_lagunas = pd.read_excel(self.archivo_excel, sheet_name="LAGUNAS")
            df_mediciones = pd.read_excel(self.archivo_excel, sheet_name="MEDICIONES")

            # Buscar la fila que coincida con el nombre de la laguna
            proyecto = df_lagunas[df_lagunas['codigo'] == self.codigo]

            if proyecto.empty:
                QMessageBox.warning(self, "Error", f"No se encontró el proyecto '{self.codigo}' en el archivo Excel.")
                return

            nombre = proyecto.iloc[0]['nombre']
            ubicacion = proyecto.iloc[0]['ubicacion']

            # Mostrar los datos en los QLabel
            lbl_NomL = self.ventana.findChild(QtWidgets.QLabel, "lbl_NomL")
            lbl_Ubi = self.ventana.findChild(QtWidgets.QLabel, "lbl_Ubi")

            if lbl_NomL and lbl_Ubi:
                lbl_NomL.setText(f" {nombre}")
                lbl_Ubi.setText(f"{ubicacion}") 
            # Buscar todas las fechas correspondientes a este código en la hoja "MEDICIONES"
            mediciones = df_mediciones[df_mediciones['codigo'] == self.codigo]

         
            # Obtener las fechas de la columna 'fecha' (ajusta el nombre de la columna según tu archivo)
            fechas = mediciones['fecha'].dropna().tolist()  # Suponiendo que la columna 'fecha' existe en la hoja "MEDICIONES"

            # Mostrar las fechas en un QListWidget o procesarlas como necesites
            lst_fechas = self.ventana.findChild(QtWidgets.QListWidget, "lst_Fechas")
            
            if lst_fechas:
                lst_fechas.clear()  # Limpiar la lista antes de agregar nuevas fechas
            # 1) convertir fecha a datetime (maneja strings o fechas de Excel)
            mediciones = mediciones.copy()
            mediciones["fecha_dt"] = pd.to_datetime(mediciones["fecha"], errors="coerce")

            # 2) eliminar inválidas y ordenar
            mediciones = mediciones.dropna(subset=["fecha_dt"]).sort_values("fecha_dt")

            # 3) formatear a texto uniforme para mostrar en la lista
            fechas = mediciones["fecha_dt"].dt.strftime("%Y-%m-%d").tolist()

            # 4) quitar duplicados (por si hay repetidas)
            fechas = list(dict.fromkeys(fechas))
            
            if not fechas:  # Si la lista de fechas está vacía
                lst_fechas.addItem("No hay fechas")  # Mostrar el mensaje "No hay fechas"
            else:
                # Agregar las fechas encontradas a la lista
                for fecha in fechas:
                    lst_fechas.addItem(str(fecha))  # Convertir la fecha a string si es necesari
           
            lst_fechas.setFocusPolicy(QtCore.Qt.NoFocus)  
                
            
              
            # Obtener las fechas de lst_fechas (QListWidget)
            lst_fechas = self.ventana.findChild(QtWidgets.QListWidget, "lst_Fechas")
            
            if lst_fechas.count() == 0:
                # Si no hay fechas, poner "Sin Registros"
                lbl_Periodo = self.ventana.findChild(QtWidgets.QLabel, "lbl_Periodo")
                lbl_Periodo.setText("Sin Registros")
            else:
                # Obtener las fechas de los ítems de lst_fechas y convertirlas a datetime
                fechas = []
                for index in range(lst_fechas.count()):
                    item = lst_fechas.item(index)
                    try:
                        fecha = datetime.strptime(item.text(), "%Y-%m-%d")  # Asumiendo formato de fecha "YYYY-MM-DD"
                        fechas.append(fecha)
                    except ValueError:
                        continue  # Si la fecha no se puede convertir, la ignoramos

                if fechas:
                    # Encontrar la fecha más antigua y la más reciente
                    fecha_min = min(fechas).strftime("%Y-%m-%d")
                    fecha_max = max(fechas).strftime("%Y-%m-%d")
                    lbl_Periodo = self.ventana.findChild(QtWidgets.QLabel, "lbl_Periodo")
                    lbl_Periodo.setText(f"{fecha_min} - {fecha_max}")
         
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Hubo un problema al buscar los datos: {str(e)}")
        
        self.cargar_tabla_mediciones()

    def volver_al_menu_principal(self):
        from MenuPrincipal import MiVentana  # Asegúrate de importar correctamente la ventana principal

        """Volver al menú principal"""
        # Crear una instancia de la ventana principal (MiVentana)
        self.menu_principal = MiVentana()
        self.menu_principal.show()
        
        if self._parent_geo is not None:
            QTimer.singleShot(0, lambda: self.menu_principal.restoreGeometry(self._parent_geo))

        # Cerrar la ventana actual (Resultados)
        self.close()
    def abrir_cargar_imagen(self):
        """Abrir la ventana CargarImagen"""
        from MenuImagen import CargarImagen  # Asegúrate de que MenuImagen.py esté en el mismo directorio o ajusta la ruta
        self.menu_subir_imagenes = CargarImagen(self, self.codigo)  # Crear una instancia de Subir Imágenes
        self.menu_subir_imagenes.show()
        self.hide()  
        
    def contenido_Graficos(self):
        """Alternar la visibilidad del frame y cambiar la dirección de la flecha"""
        if self.ventana.frm_Graficos.isVisible():
            # Si el frame es visible, ocultarlo y cambiar la flecha hacia arriba
            self.ventana.frm_Graficos.hide()
            self.ventana.tbtn_Graficos.setArrowType(Qt.RightArrow)  # Flecha hacia arriba
        else:
            # Si el frame no es visible, mostrarlo y cambiar la flecha hacia abajo
            self.ventana.frm_Graficos.show()
            self.ventana.tbtn_Graficos.setArrowType(Qt.DownArrow)  # Flecha hacia abajo
            
            
    def contenido_Tablas(self):
        """Alternar la visibilidad del frame y cambiar la dirección de la flecha"""
        if self.ventana.frm_Tablas.isVisible():
            # Si el frame es visible, ocultarlo y cambiar la flecha hacia arriba
            self.ventana.frm_Tablas.hide()
            self.ventana.tbtn_Tablas.setArrowType(Qt.RightArrow)  # Flecha hacia arriba
        else:
            # Si el frame no es visible, mostrarlo y cambiar la flecha hacia abajo
            self.ventana.frm_Tablas.show()
            self.ventana.tbtn_Tablas.setArrowType(Qt.DownArrow)  # Flecha hacia abajo
            
    def eliminar_medicion(self):
        """Eliminar el registro seleccionado de 'MEDICIONES' basado en la selección de la lista"""
        lw = self.ventana.findChild(QtWidgets.QListWidget, "lst_Fechas")
    
        if lw:
            item = lw.currentItem()  # Obtener el ítem seleccionado
            if not item:  # Verificar si no hay ítem seleccionado
                # Mostrar un mensaje de error si no se seleccionó ningún ítem
                QMessageBox.warning(self, "Selección requerida", "Por favor, selecciona una fecha.")
                return  # Detener la ejecución si no hay ítem seleccionado

            # Obtener el texto del ítem seleccionado (la fecha)
            fecha_seleccionada = item.text()

            # Mostrar una alerta de confirmación
            respuesta = QMessageBox.question(
                self,
                "Confirmar eliminación",
                f"¿Está seguro de eliminar el registro con la fecha '{fecha_seleccionada}'?\nEsto eliminará el registro de 'MEDICIONES'.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
        
            if respuesta == QMessageBox.Yes:
                self.eliminar_registro_mediciones(fecha_seleccionada)
            
                # Eliminar el ítem de la lista en la interfaz
                lw.takeItem(lw.row(item))

    def eliminar_registro_mediciones(self, fecha_seleccionada):
        """Eliminar el registro de 'MEDICIONES' basado en la fecha seleccionada"""
        # Ruta del archivo Excel
        docs = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        archivo_excel = os.path.join(docs, "CuerposDeAgua", "BD", "BaseCuerposDeAgua.xlsx")
    
        try:
            # Cargar el archivo Excel
            df = pd.read_excel(archivo_excel, sheet_name=None)  # Leer ambas hojas (en un diccionario)
        
            # Obtener la hoja "MEDICIONES"
            df_mediciones = df.get("MEDICIONES")
            if df_mediciones is None:
                raise ValueError("No se encontró la hoja 'MEDICIONES' en el archivo Excel.")
        
            # Filtrar el DataFrame de "MEDICIONES" para eliminar la fila correspondiente a la fecha seleccionada
            df_mediciones = df_mediciones[df_mediciones['fecha'] != fecha_seleccionada]
        
            # Guardar los cambios en el archivo Excel
            with pd.ExcelWriter(archivo_excel, engine='openpyxl', mode='w') as writer:
                # Guardar la hoja "LAGUNAS" sin cambios
                df_lagunas = df.get("LAGUNAS")
                if df_lagunas is not None:
                    df_lagunas.to_excel(writer, index=False, sheet_name="LAGUNAS")
            
                # Guardar la hoja "MEDICIONES" con los registros actualizados
                df_mediciones.to_excel(writer, index=False, sheet_name="MEDICIONES")

            # Confirmar eliminación
            QMessageBox.information(self, "Éxito", f"Se ha eliminado el registro con la fecha '{fecha_seleccionada}'.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Hubo un problema al eliminar el registro de 'MEDICIONES': {str(e)}")
            
    
    def buscar_registro(self, item):
        nombre_seleccionado = item.text()

        df = pd.read_excel(self.archivo_excel, sheet_name="MEDICIONES")
        df = df[df["codigo"] == self.codigo].copy()

        df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce")
        fecha_sel = pd.to_datetime(nombre_seleccionado, errors="coerce")
        registro = df[df["fecha_dt"] == fecha_sel]

        if registro.empty:
            print("No se encontró un registro")
            return

        # Guardar el registro seleccionado
        self.registro_actual = registro.iloc[0]

        # Mostrar la vista actual del combo box
        self.mostrar_vista()
    
    def mostrar_vista(self):
        if not hasattr(self, "registro_actual") or self.registro_actual is None:
            print("No hay un registro seleccionado")
            return

        vista = self.ventana.Cbox_Vistas.currentText()

        if vista == "Vista Final":
            ruta = self.registro_actual["ruta_waterMask"]
            self.render_en_widget(ruta, modo="RASTER", cmap="Blues", show_cbar=False)

        elif vista == "NDTI":
            ruta = self.registro_actual["ruta_ndti"]
            self.render_en_widget(
                ruta,
                modo="RASTER",
                cmap="RdYlBu_r",
                vmin=-1,
                vmax=1,
                show_cbar=True
            )

        elif vista == "RGB":
            ruta = self.registro_actual["ruta__rgb"]
            self.render_en_widget(ruta, modo="RGB")
        
    
    def _clear_and_get_layout(self, widget: QtWidgets.QWidget) -> QVBoxLayout:
        layout = widget.layout()
        if layout is None:
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            widget.setLayout(layout)

        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        return layout

    def render_en_widget(self, ruta: str, modo: str, cmap=None, vmin=None, vmax=None, show_cbar=True):
  
        widget = self.ventana.wdg_Imagen
        layout = self._clear_and_get_layout(widget)

        if not ruta or not os.path.exists(ruta):
            lbl = QtWidgets.QLabel("No existe la ruta de la imagen")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl)
            return

        if modo == "RGB":
            # --- Mostrar como imagen normal (PIL -> QImage -> QLabel) ---
            img_pil = Image.open(ruta).convert("RGB")
            w, h = img_pil.size
            data = img_pil.tobytes("raw", "RGB")
           
            qimg = QImage(data, w, h, 3 * w, QImage.Format_RGB888)
            pix = QPixmap.fromImage(qimg)
           
            lbl = QtWidgets.QLabel()
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setPixmap(pix)
            lbl.setScaledContents(False)  # mantenemos proporción con escalado manual
            layout.addWidget(lbl)

            # Escalar al tamaño actual manteniendo proporción
            scaled = pix.scaled(widget.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl.setPixmap(scaled)

            # Guardar refs para reescalado si quieres (opcional)
            widget._img_label = lbl
            widget._img_pixmap = pix

        else:
            # --- Mostrar como raster (matplotlib) ---
            with rasterio.open(ruta) as src:
                img = src.read(1)

            fig = Figure()
            ax = fig.add_axes([0, 0, 0.80, 1])  # ajusta espacio para colorbar
            ax.set_axis_off()
            
            if cmap is None:
                im = ax.imshow(img)
            else:
                cm = plt.get_cmap(cmap).copy()
                cm.set_bad(alpha=0)
                im = ax.imshow(img, cmap=cm, vmin=vmin, vmax=vmax)

            if show_cbar:
                # deja espacio para el colorbar
                ax.set_position([0, 0, 0.80, 1])
                cbar = fig.colorbar(im, ax=ax, orientation="vertical", fraction=0.02, pad=0.01)
                cbar.ax.tick_params(labelsize=6)
            else:
                # ✅ si no hay cbar, ocupa todo el widget
                ax.set_position([0, 0, 1, 1])

            fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

            canvas = FigureCanvas(fig)
            canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            layout.addWidget(canvas)
            canvas.draw()
            plt.close(fig)
    
    def graficar_seleccion(self, texto):
        self.DibujarGraficas(texto)

    def DibujarGraficas(self, tipo: str):
        widget = self.ventana.wdg_Graficos  # <- dibuja EN EL MISMO WIDGET
        layout = self._clear_and_get_layout(widget)

        df = pd.read_excel(self.archivo_excel, sheet_name="MEDICIONES")
        df = df[df["codigo"] == self.codigo].copy()

        if df.empty:
            lbl = QtWidgets.QLabel("No hay datos para graficar")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl)
            return

        # Asegurar fecha datetime (si ya lo tienes bien, igual no estorba)
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        df = df.dropna(subset=["fecha"]).sort_values("fecha")

        fig = Figure()
        ax = fig.add_subplot(111)
        fig.subplots_adjust(left=0.20, right=0.90, top=0.90, bottom=0.20)
        
        
        
        if tipo == "Área vs Fecha":
            ax.plot(df["fecha"], df["area"], marker="o")
            # Ajuste de tamaños
            ax.set_title("Área del cuerpo de agua vs Fecha", fontsize=8)
            ax.set_xlabel("Fecha", fontsize=8)
            ax.set_ylabel("Área", fontsize=8)
            ax.tick_params(axis="both", labelsize=7)   # tamaño de números/fechas
            ax.grid(True)

            fig.autofmt_xdate(rotation=30)  # si quieres

        elif tipo == "NDTI (Media y Mediana) vs Fecha":
            ax.plot(df["fecha"], df["ndti_media"], marker="o", label="Media")
            ax.plot(df["fecha"], df["ndti_mediana"], marker="o", label="Mediana")
            ax.set_title("NDTI (Media y Mediana) vs Fecha", fontsize=8)
            ax.set_xlabel("Fecha", fontsize=8)
            ax.set_ylabel("NDTI",fontsize=8)
            ax.tick_params(axis="both", labelsize=7)
            ax.grid(True)
            fig.autofmt_xdate(rotation=30)  # si quieres
            ax.legend()

        elif tipo == "Banda NDTI (P10-P90) vs Fecha":
            ax.plot(df["fecha"], df["ndti_mediana"], marker="o", label="Mediana")
            ax.fill_between(df["fecha"], df["P10"], df["P90"], alpha=0.2, label="P10–P90")
            ax.set_title("Variabilidad del NDTI (P10–P90)",fontsize=8)
            ax.set_xlabel("Fecha",fontsize=8)
            ax.set_ylabel("NDTI",fontsize=8)
            ax.tick_params(axis="both", labelsize=7)
            ax.grid(True)
            fig.autofmt_xdate(rotation=30)
            ax.legend()

        elif tipo == "Área vs NDTI (Dispersión)":
            ax.scatter(df["area"], df["ndti_mediana"])
            ax.set_title("Área vs NDTI (mediana)",fontsize=8)
            ax.set_xlabel("Área",fontsize=8)
            ax.set_ylabel("NDTI mediana",fontsize=8)
            ax.tick_params(axis="both", labelsize=7)
            fig.autofmt_xdate(rotation=30)
            ax.grid(True)

        elif tipo == "ΔÁrea vs Fecha":
            d = df.copy()
            d["delta_area"] = d["area"].diff()
            ax.plot(d["fecha"], d["delta_area"], marker="o")
            ax.axhline(0, linewidth=1)
            ax.set_title("Cambio de Área entre fechas (ΔÁrea)",fontsize=8)
            ax.set_xlabel("Fecha",fontsize=8)
            ax.set_ylabel("ΔÁrea",fontsize=8)
            ax.tick_params(axis="both", labelsize=7)
            fig.autofmt_xdate(rotation=30)
            ax.grid(True)

        elif tipo == "ΔNDTI vs Fecha":
            d = df.copy()
            d["delta_ndti"] = d["ndti_mediana"].diff()
            ax.plot(d["fecha"], d["delta_ndti"], marker="o")
            ax.axhline(0, linewidth=1)
            ax.set_title("Cambio de NDTI entre fechas (ΔNDTI)",fontsize=8)
            ax.set_xlabel("Fecha",fontsize=8)
            ax.set_ylabel("ΔNDTI (mediana)",fontsize=8)
            ax.tick_params(axis="both", labelsize=7)
            fig.autofmt_xdate(rotation=30)
            ax.grid(True)

        elif tipo == "Dispersión NDTI (P90-P10) vs Fecha":
            d = df.copy()
            d["spread"] = d["P90"] - d["P10"]
            ax.plot(d["fecha"], d["spread"], marker="o")
            ax.set_title("Dispersión del NDTI (P90 - P10)",fontsize=8)
            ax.set_xlabel("Fecha",fontsize=8)
            ax.set_ylabel("P90 - P10",fontsize=8)
            ax.tick_params(axis="both", labelsize=7)
            fig.autofmt_xdate(rotation=30)
            ax.grid(True)

        else:
            ax.text(0.5, 0.5, f"Gráfico no implementado: {tipo}", ha="center", va="center")
            ax.set_axis_off()

        fig.autofmt_xdate(rotation=30)

        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        layout.addWidget(canvas)
        canvas.draw()
        plt.close(fig)
        
    def cargar_tabla_mediciones(self):
        tbl = self.tbl

        if not os.path.exists(self.archivo_excel):
            QMessageBox.warning(self, "Error", f"No existe el Excel:\n{self.archivo_excel}")
            return

        df = pd.read_excel(self.archivo_excel, sheet_name="MEDICIONES")
        df = df[df["codigo"] == self.codigo].copy()

        if df.empty:
            tbl.clear()
            tbl.setRowCount(0)
            tbl.setColumnCount(0)
            return

        df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce")
        df = df.dropna(subset=["fecha_dt"]).sort_values("fecha_dt")

        columnas_deseadas = [
            ("fecha", "Fecha"),
            ("area", "Área"),
            ("ndti_media", "NDTI media"),
            ("ndti_mediana", "NDTI mediana"),
            ("P10", "P10"),
            ("P90", "P90"),
        ]

        if "P10" in df.columns and "P90" in df.columns:
            df["dispersion"] = df["P90"] - df["P10"]
            columnas_deseadas.append(("dispersion", "P90-P10"))

        cols_existentes = [(c, t) for (c, t) in columnas_deseadas if c in df.columns]

        tbl.setRowCount(len(df))
        tbl.setColumnCount(len(cols_existentes))
        tbl.setHorizontalHeaderLabels([t for (_, t) in cols_existentes])

        for r, (_, row) in enumerate(df.iterrows()):
            for c, (col_name, _) in enumerate(cols_existentes):
                if col_name == "fecha":
                    val_str = pd.to_datetime(row["fecha_dt"]).strftime("%Y-%m-%d")
                else:
                    val = row[col_name]
                    if isinstance(val, float):
                        val_str = f"{val:.4f}"
                    else:
                        val_str = "" if pd.isna(val) else str(val)

                item = QtWidgets.QTableWidgetItem(val_str)
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                tbl.setItem(r, c, item)

        tbl.resizeColumnsToContents()
        tbl.resizeRowsToContents()
        tbl.setSortingEnabled(False)
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
