# -*- coding: UTF-8 -*-
import os
import sys
import requests
import json

def getInternalId(prodName):
 # query to rest search API to get the internal ID of a product through its name
 cmd = "https://sobloo.eu/api/v1/services/search?f=identification.externalId:eq:" + prodName + "&include=previews,identification&pretty=true"
 # this API does not need authentication
 r = requests.get(cmd, verify=False)
 if( r.status_code != requests.codes.ok ):
   print("Error: %s  for the request cmd <%s>." % (r.status_code,cmd))
   internalId = -1
 else:
  # the returned json object contains the internal Id (only one product returned)
  #print(r.json())
  j = r.json()
  if j["totalnb"] == 0:
   print("No matching products found")
   internalId = -1
  else:
   internalId = j['hits'][0]['data']['uid'] 
 return internalId 

def downloadProd(prodName):
 # Get product internal Id 
 iid = getInternalId(prodName)
 if (iid == -1):
  print("Product %s not found" % (prodName))
  return -1
 # once we get the internal ID of the product we can start downloading it through the API
 # note the APIKEY injection in the headers to authenticate
 cmd = "https://sobloo.eu/api/v1/services/download/" + iid
 # we inject here the APIKEY got from our account page
 headers={"Authorization":"Apikey " + APIKEY}
 r = requests.get(cmd, headers=headers, verify=False)
 if( r.status_code != requests.codes.ok ):
   print("Error: %s  for the request cmd <%s>." % (r.status_code,cmd))
   return -1
 else: 
  # Write the data in the current directory
  filename = prodName + ".zip"
  with open(filename, "w+b") as f: 
    f.write(r.content)
  return 0

def listProductGeoname(typeGeo,zegeoname):
    # Careful the search query does not allow going beyond the 10000th element
    # So a query such as &&from=9999&&size=2 ends with an HTTP 500 error, same for &&from=10000&&size=1
    if (typeGeo == "country"):
        filter = "enrichment.geonames.states.name"
    elif (typeGeo == "allgeo"):
        filter = "enrichment.geonames.name"
    elif (typeGeo == "county"):
        filter = "enrichment.geonames.counties.name"
    elif (typeGeo == "city"):
        filter = "enrichment.geonames.counties.cities.name"
    elif (typeGeo == "village"):
        filter = "enrichment.geonames.counties.villages.name"
    else:
        filter = "all"
        
    offset = 0
    nbReturn=1000
    #cmd = "https://sobloo.eu/api/v1/services/search?f=" + filter + ":like:" + zegeoname
    cmd = "https://sobloo.eu/api/v1/services/search?f=" + filter + ":like:" + zegeoname +"&&size=" + str(nbReturn)
    ret = callAPI(cmd,0)
    if (ret != -1):
        try:
            nbHits=ret.json()["totalnb"]
            print("nbElements returned: %s" % nbHits)
            if (nbHits == 0):
                print("No hits !")
                return
            
            if (nbHits > nbReturn):
                nbCalls=int((nbHits/nbReturn))
                for i in range(0,nbCalls):
                    cmd = "https://sobloo.eu/api/v1/services/search?f=" + filter + ":like:" + zegeoname + "&&from=" + str(i*nbReturn) + "&&size=" + str(nbReturn)
                    ret2 = callAPI(cmd,0)
                    printProductDetail(ret2.json())
            else:
                printProductDetail(ret.json())  
        except:
            print("Unexpected exception %s" % (sys.exc_info()[0]))    
    else:
        print("No elements returned")
   


def callAPI(cmd, auth):
 if (auth == 1):
  # we inject here the APIKEY got from our account page
  headers={"Authorization":"Apikey " + APIKEY}
  r = requests.get(cmd, headers=headers, verify=False)  
 else:
  # this API does not need authentication
  r = requests.get(cmd, verify=False)
 
 if( r.status_code != requests.codes.ok ):
   print("Error: %s  for the request cmd <%s>." % (r.status_code,cmd))
   return -1
 else:
  # return the response
  return r

def is_empty(any_structure):
    if any_structure:
        return False
    else:
        return True
    
def printProductDetail(jsonObject):
    if is_empty(jsonObject):
        print("The object to be printed is empty.")
        return -1
    
    for elements in jsonObject["hits"]:
        uid="empty"
        try:
            uid = elements["data"]["uid"]
            ident=elements["data"]["identification"]
            acq = elements["data"]["acquisition"]
            prodName= elements["data"]["identification"]["externalId"]
            prodType=elements["data"]["identification"]["type"]
            prodLevel=elements["data"]["production"]["levelCode"]
            geoname= elements["data"]["enrichment"]["geonames"]
            uid = elements["data"]["uid"]
            orbit=elements["data"]["orbit"]
            sizeMB = elements["data"]["archive"]["size"]
            location=elements["data"]["spatialCoverage"]["geometry"]["centerPoint"]
            ident = elements["data"]["identification"]
            print("uid: %s name: %s acq: %s" % (uid,prodName,acq))
        except:
            print("Unexpected exception %s while rendering object with uid: %s ." % (sys.exc_info()[0],uid))
    
        
def wfsQuery():
 # Works OK for GetFeature & GetCapabilities
 cmd = "https://sobloo.eu/api/v1/services/wfs?service=WFS&version=3.0.0&request=GetCapabilities"
 ret = callAPI(cmd,0)
 if (ret != -1):
  print(ret.content)

def openSearchQuery():
  cmd = "https://sobloo.eu/api/v1/services/opensearch"
  ret = callAPI(cmd,0)
  if (ret != -1):
   print(ret.content)  

def listSentinelProducts(familly):
 #familly must be something like Sentinel-1A
 cmd = "https://sobloo.eu/api/v1/services/search?f=acquisition.missionName:eq:" + familly
 ret = callAPI(cmd,0)
 if (ret != -1):
  print(ret.content) 

def oneProductMeta(prodName):
 # query to get one product from its name
 cmd = "https://sobloo.eu/api/v1/services/search?f=identification.externalId:eq:" + prodName + "&include=previews,identification&pretty=true"
 ret = callAPI(cmd,0)
 if(ret != -1 ):
  j = ret.json()
  print("Nb product(s): %s" % (j["totalnb"]))
  # Check that there is only one product 
  if( j["totalnb"] != 1):
   print("Error, there are more than one product to display")
  else:
   print(ret.content)

def getQuickLook(prodName):
 iid = getInternalId(prodName)
 if (iid == -1):
  print("No corresponding data.")
 else:
  cmd = "https://sobloo.eu/api/v1/services/quicklook/" + iid
  ret = callAPI(cmd,0)
  if (ret != -1):    
   # Write the data in the current directory
   filename = "quicklook_" + prodName + ".png"
   with open(filename, "w+b") as f: 
    f.write(ret.content)
   return 0

def testWMTS():
 #cmd = "https://sobloo.eu/api/v1/services/wmts?service=WMTS&request=GetCapabilities"
 #https://sobloo.eu/api/v1/services/wmts/1d6cc991-4ca8-4a00-b113-26556c347396/tiles/1.0.0/default/rgb/EPSG4326/12/3946/933.png
 prodname = "1d6cc991-4ca8-4a00-b113-26556c347396/tiles/1.0.0/default/rgb/EPSG4326/12/3946/"
 tilename = "933.png"
 cmd = "https://sobloo.eu/api/v1/services/wmts/" + prodname + tilename
 ret = callAPI(cmd,1)
 if (ret != -1):
  # Write the data in the current directory
   filename = tilename
   with open(filename, "w+b") as f:
    f.write(ret.content)
   return 0



#
############## Main ##################
APIKEY="PUT_YOUR_API_KEY_HERE"
productname = "S2A_MSIL1C_20161126T051712_N0204_R033_T39DVC_20161126T051850"

# WFS does not work

#wfsQuery()

#listSentinelProducts("Sentinel-2A")

#oneProductMeta(productname)

#getQuickLook(productname)

downloadProd(productname)


#testWMTS()

#listProductGeoname("all","grd")

