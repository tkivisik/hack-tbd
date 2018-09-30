import matplotlib.pyplot as plt
from datetime import date
import ipyleaflet as ipyl
import ipywidgets as ipyw
#import eodag.api.core.SatImagesAPI as satimagesapi
#import eodag as dag2
from eodag.api.core import EODataAccessGateway
import datetime

def make_map_rectangle(longitude_center, latitude_center, degrees_from_center=0.05):
    lonmin = longitude_center - degrees_from_center
    lonmax = longitude_center + degrees_from_center
    latmin = latitude_center - degrees_from_center
    latmax = latitude_center + degrees_from_center

    extent = {
        'lonmin': lonmin,
        'lonmax': lonmax,
        'latmin': latmin,
        'latmax': latmax
        }
    return extent

def main():
    base_dir = '/home/sobloo/hack-tbd/original-sobloo'
    conf_file = base_dir + "/eodagconf.yml"
    dag = EODataAccessGateway(user_conf_file_path = conf_file)
    product_type = 'S2_MSI_L1C'
    extent = make_map_rectangle(longitude_center=18.330000, latitude_center=59.400000, degrees_from_center=0.1)
#    {
#    'lonmin': 18.294550,
#    'lonmax': 18.361420,
#    'latmin': 59.397867,
#    'latmax': 59.414504
#    }
    #  'lonmin': 1.306000,
    #  'lonmax': 1.551819,
    #  'latmin': 43.527642,
    #  'latmax': 43.662905
    #}

    dag.set_preferred_provider(provider='airbus-ds')
    #prodTypeList = dag.list_product_types('airbus-ds')
    #print(prodTypeList)

    products = dag.search(product_type,startTimeFromAscendingNode='2016-01-17',completionTimeFromAscendingNode='2017-12-20',geometry=extent,cloudCover=1)
    #products = dag.search(product_type)
    for i in range(len(products)):
        print('{} : {}'.format(i, products[i]))
    #print(products)
    product = products[0]
    xx, yy = product.as_dict()['geometry']['coordinates'][0][4]

    const = 0.05
    longmin = xx-const
    latmin = yy-const
    longmax = xx+const
    latmax = yy+const
    print("{}, {}, {}, {}".format(longmin, longmax, latmin, latmax))

    VIR = product.get_data(crs='epsg:4326', resolution=0.0001, band='B04', extent=(longmin, latmin, longmax, latmax))
    NIR = product.get_data(crs='epsg:4326', resolution=0.0001, band='B08', extent=(longmin, latmin, longmax, latmax))
    NDVI = (NIR - VIR * 1.) / (NIR + VIR)

    plt.imshow(NDVI, cmap='RdYlGn', aspect='auto')
    hms = datetime.datetime.now().strftime('%H%M%S')
    plt.savefig('{}/img/ndvi_toulouse-{}.png'.format(base_dir, hms))

if __name__ == '__main__':
    main()
