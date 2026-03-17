# ==========================================================
#  Proyecto: Herramienta para el análisis multitemporal
#            de cuerpos de agua
#  Autor: Xavier Escobar Arteus18
#  ==========================================================
import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsDropShadowEffect
    , QSizeGrip, QMessageBox)
from PySide6.QtCore import QFile, QStandardPaths
from PySide6.QtGui import QColor
from PySide6 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QTimer
import pandas as pd
from MenuResultados import Resultados


class MenuNuevo(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(None)  
        
        self._parent_geo = None
        if parent is not None:
            self._parent_geo = parent.saveGeometry()
 
        # Definir ruta fija para la base de datos (en la carpeta Documentos por defecto)
        docs = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        carpeta_bd = os.path.join(docs, "CuerposDeAgua", "BD")
        os.makedirs(carpeta_bd, exist_ok=True)  # Crear carpeta si no existe
        self.db_path = os.path.join(carpeta_bd, "BaseCuerposDeAgua.xlsx")

        # Configuración de la ventana
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1)
        self.clickPosition = None
        

        # Cargar el archivo .ui para la nueva ventana
        self.cargar_ui()
        
        # Establecer el mismo tamaño que la ventana principal
        if parent:
            self.setGeometry(parent.geometry())  # Ajusta el tamaño de la nueva ventana al de la ventana principal

        # Cerrar la ventana principal (el 'parent') al abrir esta ventana
        if parent:
            parent.close()
                    
        # Configuración de botones y acciones
        self.configurar_botones()

        # Configuración de sombra en los widgets
        self.agregar_sombra_widgets()

        # Redimensionamiento de la ventana
        self.configurar_redimensionamiento()

        # Conectar eventos de movimiento de la ventana
        self.configurar_eventos_movimiento()

    def cargar_ui(self):
        """Cargar el archivo .ui y establecer la ventana principal"""
        ui_file = QFile(r'C:\Users\LENOVO\Documents\CuerposDeAgua\UI\MenuCrear.ui')  # Ruta al archivo .ui de la nueva ventana
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ventana = loader.load(ui_file)
        ui_file.close()

        if self.ventana is None:
            print("No se pudo cargar la interfaz.")
            sys.exit(-1)

        self.setCentralWidget(self.ventana)  # Establecer el widget cargado como central
        
        
        
    def configurar_botones(self):
        """Configurar los botones de la interfaz"""
        # Ocultar el botón 'btn_Normal' inicialmente
        self.ventana.btn_Normal.hide()

        # Conectar botones de control de la ventana
        self.ventana.btn_Minimizar.clicked.connect(self.control_bt_minimizar)
        self.ventana.btn_Maximizar.clicked.connect(self.control_bt_maximizar)
        self.ventana.btn_Normal.clicked.connect(self.control_bt_normal)
        self.ventana.btn_Cerrar.clicked.connect(self.control_bt_Cerrar)
        self.ventana.btn_Crear.clicked.connect(self.guardar_laguna_excel)  # Conectar el botón "Crear"
        self.ventana.btn_Cancelar.clicked.connect(self.volver_al_menu_principal)

    def agregar_sombra_widgets(self):
        """Agregar sombra a los widgets especificados"""
        widgets = [self.ventana.btn_Crear, self.ventana.btn_Cancelar, self.ventana.frame_Registro]
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

    def guardar_laguna_excel(self):
        # ===== Leer campos básicos ======
        codigo = self._get_text("txt_Cd")
        nombre = self._get_text("txt_Lag")   # si txt_lag realmente es nombre
        ubic = self._get_text("txt_Ubi")
        
        if not codigo or not nombre or not ubic:
            QMessageBox.warning(self, "Campos vacíos", "Llena Código, Nombre y Ubicación.")
            return

        # Leer/crear hoja LAGUNAS
        df_lagunas = self._leer_hoja(self.db_path, "LAGUNAS", ["codigo", "nombre", "ubicacion", "ruta_proyecto"])

        # Validación: Verificar si ya existe un registro con el mismo código o el mismo nombre
        mask_codigo = df_lagunas["codigo"].astype(str) == str(codigo)
        mask_nombre = df_lagunas["nombre"].astype(str) == str(nombre)

        if mask_codigo.any():
            QMessageBox.warning(
                self,
                "Advertencia",
                f"El código '{codigo}' ya existe en la base de datos. No se puede crear otro registro con el mismo código."
            )
            return

        if mask_nombre.any():
            QMessageBox.warning(
                self,
                "Advertencia",
                f"El nombre '{nombre}' ya existe en la base de datos. No se puede crear otro registro con el mismo nombre."
            )
            return

        # Si no existe, crear la nueva laguna
        docs = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        ruta_proyecto = os.path.join(docs, "CuerposDeAgua","Proyectos", nombre)
        os.makedirs(ruta_proyecto, exist_ok=True)

        # Insertar el nuevo registro
        df_lagunas = pd.concat([df_lagunas, pd.DataFrame([{
            "codigo": codigo,
            "nombre": nombre,
            "ubicacion": ubic,
            "ruta_proyecto": ruta_proyecto
        }])], ignore_index=True)

        # Crear también MEDICIONES vacía (opcional, para que exista desde ya)
        df_med = self._leer_hoja(self.db_path, "MEDICIONES", ["codigo", "fecha", "area", "ndti_media", "ndti_mediana","P10","P25","P70","P90","ruta_waterMask","ruta_ndti","ruta__rgb"])

        try:
            with pd.ExcelWriter(self.db_path, engine="openpyxl", mode="w") as writer:
                df_lagunas.to_excel(writer, index=False, sheet_name="LAGUNAS")
                df_med.to_excel(writer, index=False, sheet_name="MEDICIONES")

            QMessageBox.information(self, "OK", f"Laguna guardada/actualizada:\n{ruta_proyecto}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")

        """Abrir la nueva ventana y cerrar la ventana principal"""
    
        self.nueva_ventana = Resultados(self, codigo)  # Crear la nueva ventana
        self.nueva_ventana.show()  # Mostrar la nueva ventana

    def _leer_hoja(self, ruta: str, hoja: str, columnas: list[str]) -> pd.DataFrame:
        """Lee una hoja; si no existe, crea DataFrame vacío con columnas."""
        if os.path.exists(ruta):
            try:
                df = pd.read_excel(ruta, sheet_name=hoja)
                # asegurar columnas
                for c in columnas:
                    if c not in df.columns:
                        df[c] = ""
                return df[columnas]
            except Exception:
                pass
        return pd.DataFrame(columns=columnas)

    def _get_text(self, object_name: str) -> str:
        w = self.ventana.findChild(QtWidgets.QLineEdit, object_name)
        if w is None:
            QMessageBox.critical(self, "Error UI", f"No existe el QLineEdit: {object_name}")
            return ""
        return w.text().strip()

    def _get_text_optional(self, object_name: str) -> str:
        w = self.ventana.findChild(QtWidgets.QLineEdit, object_name)
        if w is None:
            return ""
        return w.text().strip()
   
    def volver_al_menu_principal(self):
        # Import local para evitar import circular
        from MenuPrincipal import MiVentana  # <- pon aquí el nombre real de tu archivo .py principal

        self.menu_principal = MiVentana()
        self.menu_principal.show()

        if self._parent_geo is not None:
            QTimer.singleShot(0, lambda: self.menu_principal.restoreGeometry(self._parent_geo))

        self.close()
        
