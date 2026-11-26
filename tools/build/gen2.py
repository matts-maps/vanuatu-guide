import json, pois
data={'cats':{k:{'n':v[0],'c':v[1]} for k,v in pois.cats.items()},'pois':pois.P}
html=open('template.html', encoding='utf-8').read().replace('/*DATA*/',json.dumps(data,ensure_ascii=False)).replace('/*WX*/',open('wx.json', encoding='utf-8').read()).replace('/*STAYS*/',open('stays.json', encoding='utf-8').read()).replace('/*TRANS*/',open('trans.json', encoding='utf-8').read()).replace('/*ROUTES*/',open('routes.json', encoding='utf-8').read())
open('../../index.html','w', encoding='utf-8', newline='').write(html)
# test copy with query-string view override
t=html.replace("renderList();renderRing();draw();","""renderList();renderRing();draw();
{const q=new URLSearchParams(location.search).get('v');if(q){const [lo,la,zz]=q.split(',').map(Number);cx=mx(lo);cy=my(la);z=zz;limit();draw();if(new URLSearchParams(location.search).get('sel'))select(new URLSearchParams(location.search).get('sel'),true);setTimeout(()=>{window.addEventListener('error',e=>console.log('ERR',e.message));try{draw()}catch(e){console.log('DRAWERR',e.message,e.stack)}console.log('drawn done z',z);document.body.innerHTML='<img style="width:100%" src="'+cv.toDataURL('image/png')+'">'},6000)}}""")
open('../../test.html','w', encoding='utf-8', newline='').write(t)
print(len(html))
