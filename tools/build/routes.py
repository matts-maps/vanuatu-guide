import json,heapq,math
from shapely.geometry import Polygon,LineString,Point,MultiPoint
from shapely.ops import unary_union,nearest_points
from shapely.prepared import prep
L=json.load(open('../../data/land.json', encoding='utf-8'))
def dec(o):
    x,y=o[0],o[1];pts=[(x/1e5,y/1e5)]
    for i in range(2,len(o),2): x+=o[i];y+=o[i+1];pts.append((x/1e5,y/1e5))
    return pts
land=unary_union([Polygon(dec(o)).buffer(0) for o in L])
B=land.buffer(0.018).simplify(0.006)
PB=prep(B)
BI=B.buffer(-0.0015);PBI=prep(BI)
polys=list(B.geoms) if B.geom_type=='MultiPolygon' else [B]
def snap(pt):
    p=Point(pt)
    if not PB.contains(p): return pt
    best=None
    for g in polys:
        if g.contains(p):
            q=nearest_points(g.exterior,p)[0]
            for r in g.interiors:
                q2=nearest_points(r,p)[0]
                if q2.distance(p)<q.distance(p):q=q2
            return (q.x,q.y)
    return pt
def free(a,b):
    s=LineString([a,b])
    return not (PBI.intersects(s) and s.intersection(BI).length>1e-5)
def route(a,b,corr=1.0):
    A,Bp=snap(a),snap(b)
    if free(A,Bp): return [A,Bp]
    line=LineString([A,Bp]).buffer(corr)
    nodes=[A,Bp]
    for g in polys:
        if g.intersects(line):
            for ring in [g.exterior]+list(g.interiors):
                for c in ring.coords[:-1]:
                    if line.contains(Point(c)) and not any(h.contains(Point(c)) and h is not g for h in []): nodes.append((c[0]+0,c[1]+0))
    # nudge nodes slightly outward to be free (they lie on boundary)
    n=len(nodes);dist={0:0};prev={};pq=[(0,0)]
    while pq:
        d,i=heapq.heappop(pq)
        if d>dist.get(i,1e9):continue
        if i==1:break
        for j in range(n):
            if j==i:continue
            if free(nodes[i],nodes[j]):
                nd=d+math.dist(nodes[i],nodes[j])
                if nd<dist.get(j,1e9):dist[j]=nd;prev[j]=i;heapq.heappush(pq,(nd,j))
    if 1 not in dist: return [A,Bp]
    path=[1]
    while path[-1]!=0:path.append(prev[path[-1]])
    return [nodes[i] for i in reversed(path)]
if __name__=='__main__':
    ST={'vila':(168.3133,-17.7395),'litz':(167.4438,-16.1127),'lug':(167.1805,-15.5157),'ipota':(169.2885,-18.8582),'lenakel':(169.2661,-19.5331),'mystery':(169.7751,-20.2477),'craig':(167.924,-16.265)}
    LEGS=[('vila','litz'),('litz','lug'),('vila','ipota'),('ipota','lenakel'),('lenakel','mystery'),('vila','craig')]
    out={}
    for a,b in LEGS:
        p=route(ST[a],ST[b]);out[a+'-'+b]=[(round(x,4),round(y,4)) for x,y in p]
        print(a,b,len(p),out[a+'-'+b][:6])
    json.dump(out,open('route_legs.json','w', encoding='utf-8', newline=''))
