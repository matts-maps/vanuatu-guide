import shapefile, json, os, collections
from shapely.geometry import LineString
Q=1e5
def enc(pts):
    xs=[round(x*Q) for x,y in pts]; ys=[round(y*Q) for x,y in pts]
    o=[xs[0],ys[0]]
    for i in range(1,len(xs)): o+=[xs[i]-xs[i-1],ys[i]-ys[i-1]]
    return o
def tier(fc,L):
    if fc.startswith(('motorway','trunk','primary')): return 0
    if fc.startswith(('secondary','tertiary')): return 1
    if fc in('residential','unclassified','living_street','road'): return 2 if L>0.0012 else 3
    if fc in('service','track','track_grade1','track_grade2','track_grade3','track_grade4','track_grade5'): return 4
    return 5
out=[[] for _ in range(6)];cnt=collections.Counter()
r=shapefile.Reader('gis_osm_roads_free_1')
for sr in r.iterShapeRecords():
    fc=sr.record['fclass'];pts=sr.shape.points;idx=list(sr.shape.parts)+[len(pts)]
    for i in range(len(idx)-1):
        part=pts[idx[i]:idx[i+1]]
        if len(part)<2:continue
        ls=LineString(part);t=tier(fc,ls.length);cnt[(t,fc)]+=1
        c=list(ls.simplify([.00002,.00002,.00002,.00002,.00003,.00003][t]).coords)
        if len(c)>=2:out[t].append(enc(c))
for i,L in enumerate(out):
    p=f'../../data/roads{i+1}.json';json.dump(L,open(p,'w', encoding='utf-8', newline=''),separators=(',',':'));print(p,len(L),os.path.getsize(p)//1024,'KB')
