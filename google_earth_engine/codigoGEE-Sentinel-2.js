// 1) Área de estudio
var area = ee.Geometry.Rectangle([
  -78.390720,  // lon_min
   0.276994,   // lat_min
  -78.334243,  // lon_max
   0.332526    // lat_max
]);

// 2) Máscara de nubes Sentinel-2
function maskS2clouds(image) {
  var qa = image.select('QA60');
  var cloudBitMask  = 1 << 10; // nubes
  var cirrusBitMask = 1 << 11; // cirros

  var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
      .and(qa.bitwiseAnd(cirrusBitMask).eq(0));

  return image.updateMask(mask).divide(10000);
}

// 3) Colección Sentinel-2 (todo 2019)
var start = ee.Date('2025-01-01');
var end   = ee.Date('2025-11-01');

var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(area)
    .filterDate(start, end)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 80))
    .map(maskS2clouds)
    .sort('system:index');   // ordenar por ID, que incluye la fecha

print('Número de imágenes:', s2.size());

// 4) Bandas necesarias para el análisis (agua y color)
var bandsForStudy = ['B3', 'B8', 'B11', 'B4', 'B2'];  // Verde, NIR, SWIR1, Rojo, Azul

// 5) Visualizar cada imagen individual y exportarla
var visRGB = {bands: ['B4', 'B3', 'B2'], min: 0, max: 0.3};

// Convertir la colección a lista
var list = s2.toList(s2.size());
var n = list.size().getInfo();

for (var i = 0; i < n; i++) {
  var img = ee.Image(list.get(i));

  // Sacar fecha desde el system:index: 'YYYYMMDD...'
  var idStr   = ee.String(img.get('system:index'));
  var yyyymmdd = idStr.slice(0, 8);                        // '20200206'
  var dateStr = ee.Date.parse('yyyyMMdd', yyyymmdd)
                       .format('YYYY-MM-dd')
                       .getInfo();

  // Mostrar en el mapa la imagen con las bandas de color verdadero
  Map.addLayer(img.clip(area), visRGB, 'S2 ' + dateStr, false);

  // Exportar la imagen para análisis posterior (composición mensual o total)
  Export.image.toDrive({
    image: img.select(bandsForStudy),  // Solo las bandas necesarias
    description: 'S2_' + dateStr + '_area',  // Nombre del archivo
    fileNamePrefix: 'S2_' + dateStr + '_area',
    folder: 'Sentinel2_Export',           // Carpeta en Google Drive
    crs: 'EPSG:4326',                    // Sistema de referencia
    region: area,                        // Área de estudio
    scale: 10                            // Resolución de 10 m (banda 2, 3, 4, 8)
  });
}

Map.centerObject(area, 13);
Map.addLayer(area, {color: 'yellow'}, 'Área de estudio');

