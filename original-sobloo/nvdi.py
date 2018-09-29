import matplotlib.pyplot as plt
from datetime import date
import ipyleaflet as ipyl
import ipywidgets as ipyw
#import eodag.api.core.SatImagesAPI as satimagesapi
#import eodag as dag2
from eodag.api.core import EODataAccessGateway

base_dir = '/sources/TutoDownload'
conf_file = base_dir + "/eodagconf.yml"
dag = EODataAccessGateway(user_conf_file_path = conf_file)
product_type = 'S2_MSI_L1C'
extent = {
  'lonmin': 1.306000,
  'lonmax': 1.551819,
  'latmin': 43.527642,
  'latmax': 43.662905
}
dag.set_preferred_provider(provider='airbus-ds')
#prodTypeList = dag.list_product_types('airbus-ds')
#print(prodTypeList)

#products = dag.search(product_type,startTimeFromAscendingNode='2018-05-01',completionTimeFromAscendingNode=date.today().isoformat(),geometry=extent,cloudCover=1)
products = dag.search(product_type)
print(products)
product = products[0]

VIR = product.get_data(crs='epsg:4326', resolution=0.0001, band='B04', extent=(1.435905, 43.586857, 1.458907, 43.603827))
NIR = product.get_data(crs='epsg:4326', resolution=0.0001, band='B08', extent=(1.435905, 43.586857, 1.458907, 43.603827))
NDVI = (NIR - VIR * 1.) / (NIR + VIR)

plt.imshow(NDVI, cmap='RdYlGn', aspect='auto')
plt.savefig('%s/img/ndvi_toulouse.png' % base_dir)


