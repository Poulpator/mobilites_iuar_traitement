import math
import json
import pandas as pd
from pprint import pprint
import geojson
from geojson import LineString, Feature, FeatureCollection
from collections import Counter
from functools import reduce

csv_input = r"C:/Users/Valentin/Downloads/addresses geocode - reponses_202203052239_pour_ggsheet(1).csv"


chemin = """[{"color":"orange","line_points":[{"lat":43.44862,"lng":5.48389},{"lat":43.45012,"lng":5.48328},{"lat":43.45108,"lng":5.47929},{"lat":43.44879,"lng":5.47824},{"lat":43.45161,"lng":5.4735},{"lat":43.45159,"lng":5.46893},{"lat":43.45343,"lng":5.46545},{"lat":43.45517,"lng":5.46463},{"lat":43.45623,"lng":5.46283}]},{"color":"yellow","line_points":[{"lat":43.45623,"lng":5.46283},{"lat":43.4582,"lng":5.46387},{"lat":43.46032,"lng":5.46575},{"lat":43.46285,"lng":5.46584},{"lat":43.46493,"lng":5.46361},{"lat":43.46605,"lng":5.45962},{"lat":43.46621,"lng":5.45657},{"lat":43.46758,"lng":5.45288},{"lat":43.46997,"lng":5.44742},{"lat":43.47112,"lng":5.44365},{"lat":43.47134,"lng":5.44094},{"lat":43.47284,"lng":5.43601},{"lat":43.47547,"lng":5.43203},{"lat":43.47772,"lng":5.42718},{"lat":43.47918,"lng":5.42525},{"lat":43.48558,"lng":5.42471},{"lat":43.49092,"lng":5.4247},{"lat":43.49425,"lng":5.42625},{"lat":43.49609,"lng":5.42951},{"lat":43.49724,"lng":5.43509},{"lat":43.49983,"lng":5.44024},{"lat":43.50307,"lng":5.44492},{"lat":43.50629,"lng":5.44833},{"lat":43.50828,"lng":5.45305},{"lat":43.51031,"lng":5.45521},{"lat":43.51202,"lng":5.45547},{"lat":43.51395,"lng":5.45418},{"lat":43.51658,"lng":5.45053},{"lat":43.51882,"lng":5.44847},{"lat":43.52138,"lng":5.44701},{"lat":43.52281,"lng":5.44508}]},{"color":"blue","line_points":[{"lat":43.52281,"lng":5.44508},{"lat":43.5231,"lng":5.44554},{"lat":43.52185,"lng":5.44751},{"lat":43.52104,"lng":5.44702},{"lat":43.5205,"lng":5.44682},{"lat":43.51947,"lng":5.4467},{"lat":43.51917,"lng":5.44659},{"lat":43.51875,"lng":5.44444},{"lat":43.51816,"lng":5.44392},{"lat":43.51817,"lng":5.44326},{"lat":43.51816,"lng":5.44328}]}]"""
a = json.loads(chemin)

color_coding_transport = {
        "blue" : "marche",
        "green" : "velo", # libre service / personnel ?
        "orange" : "voiture", 
        "violet" : "covoiturage", #covoiturage
        "pink" : "bus", #car bhns ?
        "yellow" : "train",
        "red" : "autre",
        "brown" : "metro",
        "black" : "tram",
        "gray" : "deux_roues"
    }

emission_co2_par_km= {
    #emission de co2 en gramme emise par km
    #source: ADEME "base carbone"
    #emission grise non comprise
    "marche" : 0,
    "velo" : 0, 
    "voiture" : 130 , 
    "covoiturage" : (130/2), #covoiturage
    "bus" : 35, #car bhns ?
    "train" : 24.81,
    "autre" : None,
    "metro" : 2.5,
    "tram" : 2.2 ,
    "deux_roues" : 113  
    }

def translate_color(color):
    return color_coding_transport[color]

def reverse_chemin(json_as_string):
    data = json.loads(json_as_string)
    for i in range(len(data)):
        data[i]["line_points"].reverse()
    data.reverse()
    return data

b = reverse_chemin(chemin)

"""
pprint(a)
print("\n===========\n")
pprint(b)
"""

def GetLatDepart(data_input) :
    if type(data_input) == list: #deja sous json
        data= data_input
    else:
        data = json.loads(data_input)
    return data[0]["line_points"][0]["lat"]


def GetLngDepart(data_input) :
    if type(data_input) == list: #deja sous json
        data= data_input
    else:
        data = json.loads(data_input)
    return data[0]["line_points"][0]["lng"]


def get_distance(lat_1, lng_1, lat_2, lng_2):
    #formule de haversine: distance entre 2 coordonée (en km)

    lng_1, lat_1, lng_2, lat_2 = map(math.radians, [lng_1, lat_1, lng_2, lat_2])
    d_lat = lat_2 - lat_1
    d_lng = lng_2 - lng_1 

    temp = (  
         math.sin(d_lat / 2) ** 2 
       + math.cos(lat_1) 
       * math.cos(lat_2) 
       * math.sin(d_lng / 2) ** 2
    )

    return 6373.0 * (2 * math.atan2(math.sqrt(temp), math.sqrt(1 - temp)))


def get_distance_iuar(lat, lng):
    #distance entre les coordonnés lat, et lng, des coordonées de l'IUAR
    return get_distance(lat, lng, 43.518182, 5.443168)

def distance_ligne(ligne: list):
    #retourne la distance en km d'une ligne
    return sum([get_distance(ligne[i]["lat"], ligne[i]["lng"], ligne[i-1]["lat"], ligne[i-1]["lng"]) for i in range(1,len(ligne))])

def distance_trajet(data_input):
    #retourne la distance reel effectué d'un trajet
    if type(data_input) == list: #deja sous json
        data= data_input
    else:
        data = json.loads(data_input)

    somme = 0
    for elt in data:
        distance_transport = distance_ligne(elt["line_points"])
        somme +=  distance_transport
        
    return somme

def emission_trajet(data_input):
    #retourne les emissions de co2 en gramme d'un trajet
    if type(data_input) == list: #deja sous json
        data= data_input
    else:
        data = json.loads(data_input)

    somme = 0
    for elt in data:
        type_transport = translate_color(elt["color"])
        distance_transport = distance_ligne(elt["line_points"])
        somme +=  emission_co2_par_km[type_transport] * distance_transport
        
    return somme

def GetProfileInter(data_input):
    #retourne le profile de l'intermodale, ex: quelq'un qui vient en bus puis train puis marche -> bus-train-marche
    if type(data_input) == list:  #déja en json
        chemin= data_input
    else:
        chemin = json.loads(data_input)
    #print(chemin)
    liste_transport = [elt["color"] for elt in chemin]
    liste_transport = map(translate_color, liste_transport)
    return "-".join(liste_transport)


def convertToGeojson(data_input):
    if type(data_input) == list:  #déja en json
        data= data_input
    else:
        data = json.loads(data_input)
    feature_list= []
    for elt in data:
        geometry = LineString([(i["lng"],i["lat"]) for i in elt["line_points"]])
        
        properties = {"mode_transport": translate_color(elt["color"])}
        #print(properties)
        feature = Feature(geometry=geometry, properties= properties)
        #print(feature)
        feature_list.append(feature)
    return FeatureCollection(feature_list)
        
print(convertToGeojson(chemin))
geojson.dump(convertToGeojson(chemin), open("myfile.json", "w"))

liste_to_reverse = ["S2P1","S2E0","N0T1", "N4M2"]

df = pd.read_csv(csv_input)

column_name = "self_generated_id"



df["chemin"] = df.apply(lambda row: reverse_chemin(row["chemin"]) if row["self_generated_id"] in liste_to_reverse else row["chemin"], axis=1)

df["longitude"] = df.apply(lambda row: GetLngDepart(row["chemin"]), axis=1)
df["latitude"] = df.apply(lambda row: GetLatDepart(row["chemin"]), axis=1)
df["distance_oiseau_iuar_km"] = df.apply(lambda row: get_distance_iuar(row["latitude"],row["longitude"]), axis=1)

df["mode_transport"] = df.apply(lambda row: GetProfileInter(row["chemin"]), axis=1)
df["emission_co2_gramme"] = df.apply(lambda row: emission_trajet(row["chemin"]), axis=1)
df["distance_reel"] = df.apply(lambda row: distance_trajet(row["chemin"]), axis=1)
#print(df.loc[df['self_generated_id'].isin(liste)])



#sauvegrade chaque trajet dans un fichier geojson individuel
for index, row in df.iterrows():
    fp = open(row["self_generated_id"] + ".json", 'w')
    geojson.dump(convertToGeojson(row["chemin"]), fp)
    fp.close()

#fichier_chemin = open("fichier_chemin.json", "w")
feature_collection_chemins = FeatureCollection([])
for index, row in df.iterrows():
    feature_collection_chemins["features"].extend(convertToGeojson(row["chemin"])["features"])
    
    
geojson.dump(feature_collection_chemins, open("tous_chemins.json", "w"))

df.to_csv("output_addresse_mobilité_iuar.csv", index=False)
