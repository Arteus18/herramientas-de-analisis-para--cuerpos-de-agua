# Herramienta para el análisis multitemporal de cuerpos de agua

Este repositorio contiene los archivos, scripts y códigos utilizados en el desarrollo de una herramienta para el análisis multitemporal de cuerpos de agua a partir de imágenes satelitales Landsat-8 y Sentinel-2. El proyecto incluye los métodos evaluados durante la fase de pruebas, los scripts empleados en Google Earth Engine para la búsqueda y exportación de imágenes, y el programa final desarrollado en Python con interfaz gráfica.

## Contenido del repositorio

El repositorio se organiza en las siguientes secciones:

- **metodo_1/**  
  Contiene el notebook correspondiente al primer método evaluado.

- **metodo_2/**  
  Contiene el notebook correspondiente al segundo método evaluado.

- **google_earth_engine/**  
  Incluye los scripts desarrollados en Google Earth Engine para la búsqueda, filtrado y exportación de imágenes satelitales Landsat-8 y Sentinel-2.

- **herramienta_final/**  
  Contiene el código fuente de la aplicación final desarrollada en Python, junto con los archivos de interfaz gráfica, módulos auxiliares y demás recursos necesarios para su funcionamiento.

## Descripción general del proyecto

La herramienta desarrollada permite realizar un análisis multitemporal de cuerpos de agua mediante imágenes satelitales. El flujo general de procesamiento incluye la adquisición de imágenes, el preprocesamiento, la aplicación de una máscara de nubes, la segmentación del cuerpo de agua mediante el índice NDWI, el procesamiento morfológico de la máscara binaria y el cálculo del área. De manera complementaria, se utiliza el índice NDTI para evaluar la calidad de la escena.

## Tecnologías utilizadas

- **Python**
- **Spyder**
- **Qt Designer**
- **Google Earth Engine**
- **Jupyter Notebook**
- **Pandas**
- **NumPy**
- **Rasterio**
- **Matplotlib**
- **scikit-image**

## Requisitos

Para ejecutar el programa final se recomienda contar con:

- Python 3.x
- Las librerías necesarias instaladas en el entorno de trabajo
- Spyder, en caso de querer abrir y editar el proyecto en el mismo entorno de desarrollo
- Qt Designer, para modificar la interfaz gráfica si es necesario

## Uso del repositorio

Este repositorio puede emplearse para:

- Revisar los métodos evaluados durante el desarrollo del proyecto
- Consultar los scripts utilizados en Google Earth Engine
- Analizar la estructura y funcionamiento del programa final
- Reproducir o adaptar la herramienta para estudios similares

## Autor

**Xavier Escobar Arteus18**

## Licencia

Este proyecto se distribuye bajo la licencia **MIT**, lo que permite su uso, modificación y distribución, siempre que se conserve la referencia al autor y la licencia original.
