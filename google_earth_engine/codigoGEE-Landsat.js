// 1) Área de estudio (RECTÁNGULO)
var area = ee.Geometry.Rectangle([
  -78.390720,  // lon_min
   0.276994,   // lat_min
  -78.334243,  // lon_max
   0.332526    // lat_max
]);

// 2) Función para aplicar scaling factors de Landsat 8 (C2 L2)
function applyScaleFactors(image) {
  var opticalBands = image.select('SR_B.*')
                          .multiply(0.0000275)
                          .add(-0.2);
  var thermalBands = image.select('ST_B.*')
                          .multiply(0.00341802)
                          .add(149.0);
  return image
    .addBands(opticalBands, null, true)
    .addBands(thermalBands, null, true);
}

// 3) Función para procesar un año COMPLETO (sin mean)
function downloadYear(year) {

  var landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
      .filterBounds(area)
      .filterDate(year + '-01-01', year + '-12-31')
      .filterMetadata('CLOUD_COVER', 'less_than', 60)
      .map(applyScaleFactors)
      .sort('system:time_start');

  var count = landsat.size().getInfo();
  print('Año ' + year + ' → Imágenes encontradas: ', count);

  if (count === 0) {
    print('No hay imágenes para este año.');
    return;
  }

  var list = landsat.toList(count);

  for (var i = 0; i < count; i++) {

    var img = ee.Image(list.get(i));

    // Extraer fecha real desde system:time_start
    var date = ee.Date(img.get('system:time_start'))
                   .format('YYYY-MM-dd')
                   .getInfo();

    var clipped = img.clip(area);

    // Bandas útiles
    var exportBands = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6'];

    // Añadir capa al mapa
    Map.addLayer(
      clipped,
      {bands: ['SR_B4', 'SR_B3', 'SR_B2'], min: 0, max: 0.3},
      'L8 ' + date,
      false
    );

    // Exportar imagen individual
    Export.image.toDrive({
      image: clipped.select(exportBands),
      description: 'L8_' + date + '_area',
      fileNamePrefix: 'L8_' + date + '_area',
      folder: 'Landsat8_Export',
      crs: 'EPSG:4326',
      region: area,
      scale: 30
    });

  } // fin loop imágenes
}

// 4) Bucle por años
for (var year = 2024; year <= 2024; year++) {
  downloadYear(year);
}

// Centrar mapa
Map.centerObject(area, 12);
Map.addLayer(area, {color: 'yellow'}, 'Área de estudio');