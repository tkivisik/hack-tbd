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

def subselect(longitude_center, latitude_center, degrees_from_center):
    longmin = longitude_center+degrees_from_center
    latmin = latitude_center+degrees_from_center
    longmax = longitude_center-degrees_from_center
    latmax = latitude_center-degrees_from_center
    print("{}, {}, {}, {}".format(longmin, longmax, latmin, latmax))
    return (longmin, longmax, latmin, latmax)

def no_subselect(extent):
    longmin = extent['lonmin']
    latmin = extent['latmin']
    longmax = extent['lonmax']
    latmax = extent['latmax']
    return longmin, latmin, longmax, latmax

def main():
    base_dir = '/home/sobloo/hack-tbd/original-sobloo'
    conf_file = base_dir + "/eodagconf.yml"
    dag = EODataAccessGateway(user_conf_file_path = conf_file)
    product_type = 'S2_MSI_L1C'


    # Hungary
    longitude_center = 18.282810
    latitude_center = 46.127194
#    # Sweden
#    longitude_center = 18.330000
#    latitude_center = 59.400000
    degrees_from_center = 0.0035
    extent = make_map_rectangle(longitude_center=longitude_center,
        latitude_center=latitude_center,
        degrees_from_center=degrees_from_center)

    dag.set_preferred_provider(provider='airbus-ds')
    #prodTypeList = dag.list_product_types('airbus-ds')
    #print(prodTypeList)

    products = dag.search(product_type,startTimeFromAscendingNode='2016-01-17',completionTimeFromAscendingNode='2018-09-20',geometry=extent,cloudCover=1)
    #products = dag.search(product_type)
    for i in range(len(products)):
        try:
            print('{} : {}'.format(i, products[i]))
            #print(products)
            product = products[i]
            xx, yy = product.as_dict()['geometry']['coordinates'][0][4]

            #longmin, latmin, longmax, latmax = subselect(longitude_center=xx, latitude_center=yy, degrees_from_center=degrees_from_center)
            longmin, latmin, longmax, latmax = no_subselect(extent=extent)



            VIR = product.get_data(crs='epsg:4326', resolution=0.0001, band='B04', extent=(longmin, latmin, longmax, latmax))
            NIR = product.get_data(crs='epsg:4326', resolution=0.0001, band='B08', extent=(longmin, latmin, longmax, latmax))
            NDVI = (NIR - VIR * 1.) / (NIR + VIR)

            plt.imshow(NDVI, cmap='RdYlGn', aspect='auto')
            hms = datetime.datetime.now().strftime('%H%M%S')
            plt.savefig('{}/img/ndvi-{}.png'.format(base_dir, hms))
        except Exception as e:
            print('Exception: {}'.format(e))
            continue

if __name__ == '__main__':
    main()
