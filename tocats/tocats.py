import sys
import glx.apphelper
import os
import glx.helper as helper
from glx.community import Community
from glx.mothership import Mothership
from decimal import *

CONFIG_TEMPLATE = "config_template.toml"
APPNAME = "tocats"
__version__ = "0.5"

STATIONS_SEQUENCE=["nihonbashi","shinagawa","kawasaki","kanagawa","hodogaya","totsuka","fujisawa","hiratsuka","oiso","odawara","hakone","mishima","numazu","hara","yoshiwara","kanbara","yui","okitsu","ejiri","fuchu","mariko","okabe","fujieda","shimada","kanaya","nissaka","kakegawa","fukuroi","mitsuke","hamamatsu","maisaka","arai","shirasuka","futagawa","yoshida","goyu","akasaka","fujikawa","okazaki","chiryu","narumi","miya","kuwana","yokkaichi","ishiyakushi","shono","kameyama","seki","sakashita","tsuchiyama","minakuchi","ishibe","kusatsu","otsu","kyoto"]
    
STATION_FIXES={
    "hamamtsu":"hamamatsu",
    "maizaka":"maisaka",
    "sakanoshita":"sakashita",
    "pond carp carp_chiryu":"chiryu",
    "stone yakushi":"ishiyakushi",
    "kyoshi_kyoto":"kyoto",
    "palace":"miya"
}

def main(community_name):
    config_template = os.path.join(os.path.dirname(os.path.abspath(__file__)),CONFIG_TEMPLATE)
    config = helper.load_app_config(community_name,APPNAME,config_template)
    if not config:
        return False
    
    glx.apphelper.appupdate(calc_value,APPNAME,config,"tokaido-cats",community_name) 

def calc_value(asset_list):


    mothership = Mothership()

    pdict = mothership.project_dict("tokaido-cats") 

    assets = []
    stats = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    for a in asset_list:
        for attribute in pdict[int(a)]["attributes"]:
            if attribute["trait_type"] == "Cat":
                station = attribute["value"].lower()
                if station in STATION_FIXES:
                    station = STATION_FIXES[station]
                if station not in STATIONS_SEQUENCE:
                    print("!!!!",">"+station+"<",a)

                stats[STATIONS_SEQUENCE.index(station)]+=1

    # find the longest sequence
    seq = 0
    longest = 0
    extras = 0   # keeps track of how many assets are in the sequence
                # if sequence is 3 long, but there are 2 instances of each asset,
                # then extras is 6
    total = 0   # number of total assets on the wallet

    for i in stats:
        total += i
        if i==0:
            if longest < seq:
                longest = seq
            seq = 0
        else:
            seq +=1

    if longest < seq:
        longest = seq

    # longest must be at least 5 and divisible by 5
    if longest < 5:
        longest = 0
    longest = longest - longest%5

    # extras is everything else
    extras = total - longest

    # each 5 in sequence gets you 1 point
    points = longest*20

    # deducing 0.2 point for each extras
    points = points - (0.4*extras)

    # we could be below zero...
    if points < 0:
        points = 0

    # consolidation price 
    # if the wallet has at least one tocat
    if points < 10 and total > 0:
        points = 10

    points = int(points/100)

    # for testing
    print("version:",__version__)
    print(stats)
    print("total:",total)
    print("extras:",extras)
    print("longest:",longest)
    print("points:",points)
    print("--------------------")
    return points

def cli():
    p = glx.apphelper.setup_parser()
    p.add_argument("list",nargs="?", help="list cards with tokaido cats attribute")
    p.add_argument("--stats", action="store_true")
    args = p.parse_args()
    community_name = glx.apphelper.process_common_args(args,__version__,APPNAME)

    if args.stats:
        mothership = Mothership()
        pdict = mothership.project_dict("tokaido-cats") 
        stats={}

        for k,v in pdict.items():
            for attribute in v["attributes"]:
                if attribute["trait_type"] == "Cat":
                    station = attribute["value"].lower()
                    if station in STATION_FIXES:
                        station = STATION_FIXES[station]
                    if station in STATIONS_SEQUENCE:
                        if station not in stats:
                            stats[station] = []
                        stats[station].append(k)
            
        for s in STATIONS_SEQUENCE:
            if s in stats:
                print(s,len(stats[s]))
            else:
                print(s,"NO instances!!!")
        exit(0)
        
    if args.list:
        # get attribute id
        config = helper.load_app_config(community_name,APPNAME)
        if not config:
            print("Config file missing")
            exit(0)

        if args.collection:
            collection_id = args.collection
        else:
            collection_id = 1
        
        print("Cards with tokaido cats:")
        helper.prettyrow([("id",3,"r"),("val",3,"r")])
        community = Community(community_name)
        hs = sorted(community.collection(collection_id).attribute(config["attribute_id"]).instances(), key=lambda d: d["card_id"])
        for ins in hs:
            card_id = ins["card_id"]
            if ins["interacted_with"]:
                interacted = "*"
            else:
                interacted = "-"
            value = ins["value"]
            helper.prettyrow([(card_id,3,"r"),(value,3,"r")])
            #print(ins)
        exit(0)
    main(community_name)
