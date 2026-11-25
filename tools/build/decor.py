import json, math, random, os
from shapely.geometry import Polygon, Point, MultiPolygon
from shapely.ops import unary_union
from shapely.prepared import prep
random.seed(11)
Q=1e5
def enc(pts):
    xs=[round(x*Q) for x,y in pts]; ys=[round(y*Q) for x,y in pts]
    o=[xs[0],ys[0]]
    for i in range(1,len(xs)): o+=[xs[i]-xs[i-1],ys[i]-ys[i-1]]
    return o
import shapefile
from shapely.geometry import shape
polys=[]
for sr in shapefile.Reader('gis_osm_places_a_free_1').iterShapeRecords():
    if sr.record['fclass']!='island': continue
    g=shape(sr.shape.__geo_interface__).buffer(0)
    for p in (g.geoms if g.geom_type=='MultiPolygon' else [g]):
        if not p.is_empty: polys.append(Polygon(p.exterior))
land=[p.simplify(0.00003) for p in polys]
json.dump([enc(list(p.exterior.coords)) for p in land if p.geom_type=='Polygon' and not p.is_empty],open('../../data/land.json','w'),separators=(',',':'))
print('land',os.path.getsize('../../data/land.json')//1024,'KB',len(land))
def sample(polys,inner,outer,levels,per_area,maxn=4000):
    pts=[];all_=[]
    for p in polys:
        if p.area<0.0004: continue
        band=p.buffer(-inner)
        if outer is not None: band=band.difference(p.buffer(-outer))
        if band.is_empty: continue
        pb=prep(band); x0,y0,x1,y1=band.bounds
        for lv,r in enumerate(levels):
            n=int(band.area/(r*r)*2.2)+10
            for _ in range(n):
                x=random.uniform(x0,x1);y=random.uniform(y0,y1)
                if not pb.contains(Point(x,y)): continue
                if any((x-a)**2+(y-b)**2<r*r for a,b,_ in all_): continue
                all_.append((x,y,lv)); pts.append([round(x,5),round(y,5),lv])
    return pts
hills=sample(land,0.012,None,[0.12,0.06,0.03,0.016],1)
palms=sample(land,0.0012,0.007,[0.06,0.03,0.016,0.009],1)
print('hills',len(hills),'palms',len(palms))
G=unary_union(land); GP=prep(G.buffer(0.04))
def sea(tx,ty):
    for _ in range(4000):
        x=tx+random.uniform(-.25,.25);y=ty+random.uniform(-.25,.25)
        if not GP.contains(Point(x,y)): return [round(x,4),round(y,4)]
cre=[]
for kind,tx,ty in [('boat',168.10,-17.50),('dolphin',168.75,-17.55),('dolphin',168.35,-17.95),('fish',168.72,-17.80),('fish',168.70,-17.90),('ship',168.25,-17.88),('plane',168.15,-17.35),
   ('boat',167.0,-15.0),('dolphin',167.7,-16.8),('fish',167.3,-16.5),('dolphin',169.6,-19.5),('ship',169.4,-19.1),('boat',166.8,-14.6),('fish',168.4,-16.6),('dolphin',168.3,-15.6),('plane',167.2,-15.6),('fish',169.1,-18.7),('boat',168.9,-18.3)]:
    p=sea(tx,ty)
    if p: cre.append([kind]+p)
json.dump({'hills':hills,'palms':palms,'creatures':cre},open('../../data/decor.json','w'),separators=(',',':'))
print(os.path.getsize('../../data/decor.json')//1024,'KB',len(cre))
