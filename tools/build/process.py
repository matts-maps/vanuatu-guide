import shapefile, json, math, os, random, collections, time
from shapely.geometry import shape, Polygon, Point, LineString, mapping
from shapely.ops import unary_union
t0=time.time()
os.makedirs('../../data',exist_ok=True)
Q=1e5
def enc(pts):
    xs=[round(x*Q) for x,y in pts]; ys=[round(y*Q) for x,y in pts]
    o=[xs[0],ys[0]]
    for i in range(1,len(xs)): o+= [xs[i]-xs[i-1],ys[i]-ys[i-1]]
    return o
def parts(s):
    pts=s.points; idx=list(s.parts)+[len(pts)]
    return [pts[idx[i]:idx[i+1]] for i in range(len(idx)-1)]
def dump(name,obj):
    p='../../data/'+name; json.dump(obj,open(p,'w', encoding='utf-8', newline=''),separators=(',',':'),ensure_ascii=False); print(name,os.path.getsize(p)//1024,'KB')
# land (Natural Earth rings, whole country)
d=json.load(open('../source-data/natural-earth-land.geojson', encoding='utf-8'))
W,E,S,N=166.3,170.5,-20.5,-12.9
rings=[]
for f in d['features']:
    g=f['geometry']; polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
    for p in polys:
        r=p[0]; xs=[c[0] for c in r]; ys=[c[1] for c in r]
        if min(xs)>=W and max(xs)<=E and min(ys)>=S and max(ys)<=N: rings.append(r)
print('land rings',len(rings),sum(len(r) for r in rings))
dump('land.json',[enc(r) for r in rings])
# roads
T1={'motorway','trunk','primary','secondary','tertiary','motorway_link','trunk_link','primary_link','secondary_link','tertiary_link'}
T2={'residential','unclassified','living_street','road'}
roads=[[],[],[]]
r=shapefile.Reader('gis_osm_roads_free_1')
for sr in r.iterShapeRecords():
    fc=sr.record['fclass']; t=0 if fc in T1 else 1 if fc in T2 else 2
    tol=[0.00001,0.00001,0.00002][t]
    for part in parts(sr.shape):
        if len(part)<2: continue
        ls=LineString(part).simplify(tol)
        pts=list(ls.coords)
        if len(pts)>=2: roads[t].append(enc(pts))
for i,L in enumerate(roads): dump(f'roads{i+1}.json',L)
# waterways
w=[[],[]]
r=shapefile.Reader('gis_osm_waterways_free_1')
for sr in r.iterShapeRecords():
    t=0 if sr.record['fclass']=='river' else 1
    for part in parts(sr.shape):
        if len(part)>=2: w[t].append(enc(list(LineString(part).simplify(0.00002).coords)))
for i,L in enumerate(w): dump(f'water{i+1}.json',L)
# water areas
wa=[]
r=shapefile.Reader('gis_osm_water_a_free_1')
for sr in r.iterShapeRecords():
    for part in parts(sr.shape):
        if len(part)>=4:
            pg=Polygon(part).simplify(0.00003)
            if not pg.is_empty and pg.geom_type=='Polygon': wa.append(enc(list(pg.exterior.coords)))
dump('waterarea.json',wa)
# places
CLS={'national_capital':0,'city':0,'town':1,'village':2,'hamlet':3,'suburb':3,'island':4}
pl=[]
r=shapefile.Reader('gis_osm_places_free_1')
for sr in r.iterShapeRecords():
    c=CLS.get(sr.record['fclass'])
    if c is None or not sr.record['name']: continue
    x,y=sr.shape.points[0]; pl.append([sr.record['name'],c,round(x,5),round(y,5)])
r=shapefile.Reader('gis_osm_places_a_free_1')
for sr in r.iterShapeRecords():
    if sr.record['fclass']=='island' and sr.record['name']:
        b=sr.shape.bbox; ar=(b[2]-b[0])*(b[3]-b[1])
        pl.append([sr.record['name'],4,round((b[0]+b[2])/2,5),round((b[1]+b[3])/2,5),round(ar,4)])
print('places',len(pl),collections.Counter(p[1] for p in pl))
dump('places.json',pl)
# buildings tiled
CELL=0.1; cells=collections.defaultdict(list)
r=shapefile.Reader('gis_osm_buildings_a_free_1')
n=0
for sr in r.iterShapeRecords():
    s=sr.shape; part=s.points[:s.parts[1]] if len(s.parts)>1 else s.points
    if len(part)<4: continue
    pg=Polygon(part)
    if not pg.is_valid: pg=pg.buffer(0)
    if pg.is_empty: continue
    if pg.geom_type!='Polygon': pg=max(pg.geoms,key=lambda g:g.area)
    sp=pg.simplify(0.000012)
    if sp.is_empty or sp.geom_type!='Polygon': sp=pg
    pts=list(sp.exterior.coords)[:-1]
    if len(pts)<3: continue
    cx,cy=pg.centroid.x,pg.centroid.y
    key=(math.floor(cx/CELL),math.floor(cy/CELL))
    cells[key].append(enc(pts)); n+=1
print('buildings',n,'cells',len(cells))
idx={}
for (ix,iy),L in cells.items():
    nm=f'b_{ix}_{iy}.json'; json.dump(L,open('../../data/'+nm,'w', encoding='utf-8', newline=''),separators=(',',':')); idx[f'{ix}_{iy}']=len(L)
dump('bcells.json',{'cell':CELL,'n':idx})
print('total KB',sum(os.path.getsize('../../data/'+f) for f in os.listdir('../../data'))//1024,'files',len(os.listdir('../../data')),'time',round(time.time()-t0))
