import csv,json,math
rows=[r for r in csv.DictReader(open('../source-data/ourairports-vanuatu.csv',encoding='utf-8')) if r['iso_country']=='VU' and r['type']!='closed']
old=json.load(open('trans.json', encoding='utf-8'))
keep=[t for t in old if t[1]!='Airport' and not t[0].startswith('Port Vila main port')]
new=[]
for r in rows:
    nm=r['name'];mu=(r['municipality'] or '').strip()
    if mu and mu.lower() not in nm.lower(): nm+=f' ({mu})'
    src='OurAirports'+(f", code {r['iata_code']}" if r['iata_code'] else '')
    new.append([nm,'Airport',round(float(r['longitude_deg']),5),round(float(r['latitude_deg']),5),src])
new.sort(key=lambda t:t[0])
# World Port Index main port
keep.append(['Port Vila main port (World Port Index)','Port',168.31667,-17.73333,'World Port Index (NGA)'])
json.dump(new+keep,open('trans.json','w', encoding='utf-8', newline=''),ensure_ascii=False)
# move flight endpoints to nearest new airport
def d(a,b):return math.hypot((a[0]-b[0])*math.cos(math.radians(a[1])),a[1]-b[1])*111
oldair=[t for t in old if t[1]=='Airport']
routes=json.load(open('routes.json', encoding='utf-8'))
for rt in routes:
    if rt[1]!='Flight':continue
    for i in (0,-1):
        pt=rt[2][i];best=min(new,key=lambda n:d(pt,(n[2],n[3])))
        if d(pt,(best[2],best[3]))<2: rt[2][i]=[best[2],best[3]]; 
        else: print('NO MATCH',rt[0],pt)
json.dump(routes,open('routes.json','w', encoding='utf-8', newline=''))
print(len(new),'airports;',len(keep),'other')
