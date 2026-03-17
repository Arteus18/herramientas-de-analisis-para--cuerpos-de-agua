# ==========================================================
#  Proyecto: Herramienta para el análisis multitemporal
#            de cuerpos de agua
#  Autor: Xavier Escobar Arteus18
#  ==========================================================
import sys
import os
from PySide6.QtWidgets import ( 
    QApplication, QMainWindow, QGraphicsDropShadowEffect, 
    QSizeGrip , QMessageBox, QListWidgetItem)
from PySide6.QtCore import QFile, Qt , QStandardPaths
from PySide6.QtGui import QColor, QIcon  # Asegúrate de importar QIcon
from PySide6 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader
import pandas as pd
from MenuNuevo import MenuNuevo  # Importa la nueva ventana
from MenuResultados import Resultados  # Importa la ventana Resultados

class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Eliminar la barra de título
        self.setWindowOpacity(1)  # Establecer la opacidad de la ventana
        self.clickPosition = None  # Inicializar la variable clickPosition

        # Establecer un tamaño inicial para la ventana
        self.resize(675, 600)  # Tamaño en píxeles (ancho, alto)

        # Cargar la UI
        self.cargar_ui()

        # Configuración de botones y acciones
        self.configurar_botones()

        # Configuración de sombra en los widgets
        self.agregar_sombra_widgets()

        # Redimensionamiento de la ventana
        self.configurar_redimensionamiento()

        # Conectar eventos de movimiento de la ventana
        self.configurar_eventos_movimiento()
        
        self.cargar_carpetas()
        
        

    def cargar_ui(self):
        """Cargar el archivo .ui y establecer la ventana principal"""
        ui_file = QFile(r'C:\Users\LENOVO\Documents\CuerposDeAgua\UI\MenuPrincipal.ui')  
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
        self.ventana.btn_Cerrar.clicked.connect(self.close)

        # Conectar el botón 'btn_Nuevo' para abrir la nueva ventana
        self.ventana.btn_Nuevo.clicked.connect(self.abrir_nueva_ventana)

        # Conectar el botón 'btn_Abrir' para abrir la ventana Resultados
        self.ventana.btn_Abrir.clicked.connect(self.abrir_resultados)

        # Conectar el botón 'btn_Eliminar' para eliminar el proyecto
        self.ventana.btn_Eliminar.clicked.connect(self.eliminar_proyecto)
        
        # Conectar el evento de selección del QListWidget
        lw = self.ventana.findChild(QtWidgets.QListWidget, "Wd_List")
        if lw:
            lw.itemSelectionChanged.connect(self.actualizar_label_con_seleccion)
            
    def abrir_nueva_ventana(self):
        """Abrir la nueva ventana y cerrar la ventana principal"""
        
        self.nueva_ventana = MenuNuevo(self)  # Crear la nueva ventana
        self.nueva_ventana.show()  # Mostrar la nueva ventana
    
    def abrir_resultados(self):
        """Abrir la ventana Resultados y pasar el nombre del ítem seleccionado"""
        lw = self.ventana.findChild(QtWidgets.QListWidget, "Wd_List")
        
        if lw:
            item = lw.currentItem()  # Obtener el ítem seleccionado
            if not item:  # Verificar si no hay ítem seleccionado
                # Mostrar un mensaje de error si no se seleccionó ningún ítem
                QMessageBox.warning(self, "Selección requerida", "Por favor, selecciona una laguna.")
                return  # Detener la ejecución si no hay ítem seleccionado
        
        nombre = item.text()  # Obtener el nombre del ítem seleccionado
        
        docs = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        archivo_excel = os.path.join(docs, "CuerposDeAgua", "BD", "BaseCuerposDeAgua.xlsx")
        
        try:
         
            # Cargar el archivo Excel
            df = pd.read_excel(archivo_excel, sheet_name=None)  # Leer ambas hojas (en un diccionario)
           
            # Buscar la fila correspondiente al nombre de la laguna en la hoja LAGUNAS
            df_lagunas = df.get("LAGUNAS")
            if df_lagunas is None:
                raise ValueError("No se encontró la hoja 'LAGUNAS' en el archivo Excel.")
            
            # Buscar el código y la ruta del proyecto de la laguna seleccionada
            proyecto = df_lagunas[df_lagunas['nombre'] == nombre]
            
            if proyecto.empty:
                QMessageBox.warning(self, "Error", f"No se encontró el proyecto '{nombre}' en el archivo Excel.")
                return
          
            codigo = proyecto.iloc[0]['codigo']
            
            self.menu_resultados = Resultados(self, codigo)
            self.menu_resultados.show()

            
            self.close()
            
        except Exception as e:
               
                QMessageBox.critical(self, "Error", f"No se encontro registros del proyecto: {str(e)}")

    def agregar_sombra_widgets(self):
        """Agregar sombra a los widgets especificados"""
        widgets = [self.ventana.btn_Nuevo, self.ventana.btn_Abrir, self.ventana.btn_Eliminar, self.ventana.Wd_List]
        for widget in widgets:
            self.sombra_frame(widget)

    def configurar_redimensionamiento(self):
        """Configurar el redimensionamiento de la ventana con un 'grip'"""
        self.gripSize = 10
        self.grip = QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)  # Definir tamaño del grip
        self.grip.move(self.ventana.width() - self.gripSize, self.ventana.height() - self.gripSize)  # Ubicar el grip en la esquina inferior derecha

    def configurar_eventos_movimiento(self):
        """Conectar los eventos de movimiento de la ventana"""
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

    def mousePressEvent(self, event):
        """Captura la posición del clic inicial"""
        if event.buttons() == QtCore.Qt.LeftButton:
            self.clickPosition = event.globalPos()  # Registra la posición cuando se hace clic
            event.accept()  # Asegura que el evento se acepte

    def mouseMoveEvent(self, event):
        """Mover la ventana mientras el ratón está presionado"""
       
        if not self.isMaximized() and event.buttons() == QtCore.Qt.LeftButton:
            # Verificar que 'clickPosition' no sea None antes de intentar usarla
            if self.clickPosition is not None:
                # Asegurarse de que las posiciones sean del mismo tipo
                click_pos = self.clickPosition if isinstance(self.clickPosition, QtCore.QPoint) else self.clickPosition.toPoint()
                global_pos = event.globalPos()

                # Calcular el desplazamiento y mover la ventana
                delta = global_pos - click_pos
                self.move(self.pos() + delta)

                # Actualizar la posición del ratón
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
     
    def cargar_carpetas(self):
        # Usamos la ruta que contiene las carpetas, por ejemplo:
        docs = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        ruta = os.path.join(docs, "CuerposDeAgua", "Proyectos")  # Modificar según tu ruta

        lw = self.ventana.findChild(QtWidgets.QListWidget, "Wd_List")
    
        if lw is None:
            QMessageBox.critical(self, "Error UI", "No existe el QListWidget")
            return
    
        if not os.path.isdir(ruta):
            QMessageBox.warning(self, "Ruta inválida", f"No existe la carpeta:\n{ruta}")
            lw.clear()
            return

        # Obtener las carpetas en la ruta
        carpetas = sorted(
            [d for d in os.listdir(ruta) if os.path.isdir(os.path.join(ruta, d))],
            key=lambda x: x.lower()
            )
    
        # Limpiar la lista antes de agregar nuevos elementos
        lw.clear()

        # Verificar si no hay carpetas
        if not carpetas:
            item = QListWidgetItem("No hay carpetas en esta ruta")
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)  # Deshabilitar selección
            lw.addItem(item)
        else:
            for nombre in carpetas:
                ruta_completa = os.path.join(ruta, nombre)
                item = QListWidgetItem(nombre)
                icono = QIcon(r'C:\Users\LENOVO\Documents\CuerposDeAgua\Resources\Iconos\Carpetas.png')
                item.setIcon(icono)
                item.setData(Qt.UserRole, ruta_completa)  # Guardar ruta completa
                lw.addItem(item)
                item.setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom)  # Alineación del texto

        lw.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        lw.setFocusPolicy(QtCore.Qt.NoFocus)
    
        
    def actualizar_label_con_seleccion(self):
        """Actualizar el texto del QLabel con el texto del ítem seleccionado"""
        lw = self.ventana.findChild(QtWidgets.QListWidget, "Wd_List")
        lbl_NomL = self.ventana.findChild(QtWidgets.QLabel, "lbl_NomL")

        if lw and lbl_NomL:
            # Obtener el ítem seleccionado
            item = lw.currentItem()
        
        # Verificar si hay un ítem seleccionado
            if item:
                # Establecer el texto del QLabel con el texto del ítem seleccionado
                lbl_NomL.setText(item.text())
                
    def eliminar_proyecto(self):
        """Eliminar el proyecto seleccionado si hay confirmación"""
        lw = self.ventana.findChild(QtWidgets.QListWidget, "Wd_List")
         
        if lw:
            item = lw.currentItem()  # Obtener el ítem seleccionado
            if not item:  # Verificar si no hay ítem seleccionado
                # Mostrar un mensaje de error si no se seleccionó ningún ítem
                QMessageBox.warning(self, "Selección requerida", "Por favor, selecciona una laguna.")
                return  # Detener la ejecución si no hay ítem seleccionado
        
        
        if lw:
            item = lw.currentItem()  # Obtener el ítem seleccionado
            if not item:  # Verificar si no hay ítem seleccionado
                return  # Si no se seleccionó nada, no hacer nada
            
            nombre = item.text()  # Obtener el nombre del ítem seleccionado

            # Mostrar una alerta de confirmación
            respuesta = QMessageBox.question(
                self,
                "Confirmar eliminación",
                f"¿Está seguro de eliminar el proyecto '{nombre}'?\nEsto eliminará el proyecto y sus carpetas.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if respuesta == QMessageBox.Yes:
                self.eliminar_registro_y_carpetas(nombre)
            
                lw.takeItem(lw.row(item)) 

    def eliminar_registro_y_carpetas(self, nombre):
        """Eliminar el registro del Excel y las carpetas asociadas"""
        # Ruta del archivo Excel en la carpeta de Documentos
        docs = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        archivo_excel = os.path.join(docs, "CuerposDeAgua", "BD", "BaseCuerposDeAgua.xlsx")
        
        try:
            # Cargar el archivo Excel
            df = pd.read_excel(archivo_excel, sheet_name=None)  # Leer ambas hojas (en un diccionario)
            
            # Buscar la fila correspondiente al nombre de la laguna en la hoja LAGUNAS
            df_lagunas = df.get("LAGUNAS")
            if df_lagunas is None:
                raise ValueError("No se encontró la hoja 'LAGUNAS' en el archivo Excel.")
            
            # Buscar el código y la ruta del proyecto de la laguna seleccionada
            proyecto = df_lagunas[df_lagunas['nombre'] == nombre]
            
            if proyecto.empty:
                QMessageBox.warning(self, "Error", f"No se encontró el proyecto '{nombre}' en el archivo Excel.")
                return
            
            codigo = proyecto.iloc[0]['codigo']
            ruta_proyecto = proyecto.iloc[0]['ruta_proyecto']

            # Eliminar el proyecto de ambas hojas (LAGUNAS y MEDICIONES)
            for sheet_name, sheet_data in df.items():
                if sheet_name == "LAGUNAS" or sheet_name == "MEDICIONES":
                    df[sheet_name] = sheet_data[sheet_data['codigo'] != codigo]

            # Guardar los cambios en el archivo Excel
            with pd.ExcelWriter(archivo_excel, engine='openpyxl', mode='w') as writer:
                for sheet_name, sheet_data in df.items():
                    sheet_data.to_excel(writer, index=False, sheet_name=sheet_name)

            # Eliminar las carpetas del proyecto
            if os.path.isdir(ruta_proyecto):
                self.eliminar_carpetas(ruta_proyecto)
                QMessageBox.information(self, "Proyecto Eliminado", f"El proyecto '{nombre}' y sus carpetas han sido eliminados exitosamente.")
            else:
                QMessageBox.warning(self, "Error", f"No se encontraron carpetas para el proyecto '{nombre}'.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Hubo un problema al eliminar el proyecto: {str(e)}")

    def eliminar_carpetas(self, ruta_proyecto):
        """Eliminar las carpetas dentro de la ruta del proyecto"""
        try:
            # Eliminar todas las carpetas dentro de la ruta del proyecto
            for root, dirs, files in os.walk(ruta_proyecto, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))  # Eliminar archivos
                for name in dirs:
                    os.rmdir(os.path.join(root, name))  # Eliminar carpetas vacías
            os.rmdir(ruta_proyecto)  # Eliminar la carpeta principal
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Hubo un problema al eliminar las carpetas: {str(e)}")

        
def main():
    """Función principal para ejecutar la aplicación"""
    app = QApplication.instance()
    
    if not app:
        app = QApplication(sys.argv)
    
    mi_app = MiVentana()
    mi_app.show()

    sys.exit(app.exec()) 

if __name__ == "__main__":
    main()
