# Adds small hand-placed islet outlines (OpenStreetMap has no polygons for them) to ../../data/land.json
import json,math
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union,nearest_points
import pois
Q=1e5
def enc(pts):
    xs=[round(x*Q) for x,y in pts]; ys=[round(y*Q) for x,y in pts]
    o=[xs[0],ys[0]]
    for i in range(1,len(xs)): o+=[xs[i]-xs[i-1],ys[i]-ys[i-1]]
    return o
def dec(o):
    x,y=o[0],o[1];pts=[(x/Q,y/Q)]
    for i in range(2,len(o),2): x+=o[i];y+=o[i+1];pts.append((x/Q,y/Q))
    return pts
def blob(lon,lat,rx_m,ry_m,rot=0,n=18):
    out=[]
    for k in range(n):
        a=2*math.pi*k/n; w=1+0.08*math.sin(3*a+lon*1000)+0.05*math.cos(5*a)
        x=rx_m*w*math.cos(a);y=ry_m*w*math.sin(a)
        xr=x*math.cos(rot)-y*math.sin(rot);yr=x*math.sin(rot)+y*math.cos(rot)
        out.append((lon+xr/(111320*math.cos(math.radians(lat))),lat+yr/110540))
    return out
L=json.load(open('land_before_islets.json', encoding='utf-8'))
ISL=[(168.3097,-17.7736,260,200,0.3),   # Erakor Island
     (168.3098,-17.7435,190,150,0.5),   # Iririki Island
     (168.2633,-17.6965,150,110,0.2)]   # Hideaway Island
import shapefile
from shapely.geometry import shape,MultiPoint
base=unary_union([Polygon(dec(o)).buffer(0) for o in L])
feat=[]
for fn in ('gis_osm_roads_free_1','gis_osm_buildings_a_free_1'):
    r=shapefile.Reader(fn)
    for sh in r.iterShapes():
        b=sh.bbox
        if any(b[0]<=lon+0.005 and b[2]>=lon-0.005 and b[1]<=lat+0.005 and b[3]>=lat-0.005 for lon,lat,*_ in ISL): feat.append(shape(sh.__geo_interface__))
for lon,lat,rx,ry,rot in ISL:
    poly=Polygon(blob(lon,lat,rx,ry,rot))
    c=Point(lon,lat);pts=[]
    for g in feat:
        if g.distance(c)>0.0035: continue
        pr=g.intersection(c.buffer(0.0035))
        for q in ([pr] if pr.geom_type in('LineString','Polygon') else list(getattr(pr,'geoms',[]))):
            for x,y in (q.exterior.coords if q.geom_type=='Polygon' else q.coords):
                if not base.contains(Point(x,y)) and Point(x,y).distance(c)<0.0033: pts.append((x,y))
    if len(pts)>=3:
        hull=MultiPoint(pts+list(poly.exterior.coords)).convex_hull.buffer(0.00018)
        poly=hull.simplify(0.00003)
    print(lon,lat,len(pts),round(poly.area*1e10/1e6),'m2-ish')
    L.append(enc(list(poly.exterior.coords)))
json.dump(L,open('../../data/land.json','w', encoding='utf-8', newline=''),separators=(',',':'))
land=unary_union([Polygon(dec(o)).buffer(0) for o in L])
# land-based pins that miss the land: snap in
SNAP={'tannablue','champagne'}
for p in pois.P:
    pt=Point(p['lon'],p['lat'])
    if p['id'] in SNAP and not land.contains(pt):
        poly=[g for g in (land.geoms if land.geom_type=='MultiPolygon' else [land]) if g.distance(pt)<0.01][0]
        q=nearest_points(poly,pt)[0];c=poly.centroid
        dx,dy=c.x-q.x,c.y-q.y;m=math.hypot(dx,dy) or 1
        nl=(q.x+dx/m*0.0004,q.y+dy/m*0.0004)
        print('snap',p['id'],round(p['lon'],5),round(p['lat'],5),'->',round(nl[0],5),round(nl[1],5),land.contains(Point(nl)))
