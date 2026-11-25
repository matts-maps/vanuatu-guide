import sys,subprocess,time,json
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8765'],cwd='../..',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1.5)
bad=[];ok=[]
try:
  with sync_playwright() as p:
    br=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for name,vw in (('phone',{'width':390,'height':800}),('desktop',{'width':1280,'height':800})):
      pg=br.new_page(viewport=vw);errs=[]
      pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' and 'Failed to load resource' not in m.text else None);pg.on('response',lambda r:errs.append(f'{r.status} {r.url}') if r.status>=400 and 'favicon' not in r.url else None)
      pg.goto('http://localhost:8765/index.html');pg.wait_for_timeout(4000)
      # land check: canvas has non-sea colours, pins present
      info=pg.evaluate('''()=>{const c=document.getElementById('cv');const x=c.getContext('2d');const d=x.getImageData(0,0,c.width,c.height).data;const seen=new Set();for(let i=0;i<d.length;i+=4*997)seen.add((d[i]>>4)+','+(d[i+1]>>4)+','+(d[i+2]>>4));return {colours:seen.size,pins:document.querySelectorAll('.pin').length}}''')
      (ok if info['colours']>6 and info['pins']>40 else bad).append(f'{name} canvas/pins {info}')
      # weather bar follows the dominant island
      res=[]
      for v in ('168.3,-17.7,9','167.2,-15.5,9','169.3,-19.5,9','167.9,-16.3,9'):
          pg.goto('http://localhost:8765/test.html?v='+v);pg.wait_for_timeout(2500);res.append(pg.inner_text('#wxbar').replace('\n',' | ')[:110])
      (ok if 'Port Vila' in res[0] and 'Santo' in res[1] and 'Tanna' in res[2] and 'Nearest' in res[3] else bad).append(f'{name} weather bar {res}')
      pg.goto('http://localhost:8765/index.html');pg.wait_for_timeout(3000)
      # search names only
      pg.fill('#q','ram');pg.wait_for_timeout(300);items=pg.locator('#list .it b').all_inner_texts()
      (ok if not any('aramount' in i for i in items) else bad).append(f'{name} list filter {items[:4]}')
      pg.fill('#q','');
      # day plans
      pg.click('.modebar button[data-mode=ring]');pg.click('#plansel button:nth-child(3)');pg.wait_for_timeout(300)
      k=pg.locator('#ringlist .it').count();(ok if k==4 else bad).append(f'{name} tanna plan steps {k}')
      # tap size
      h=pg.evaluate("Math.min(...[...document.querySelectorAll('.chip,.modebar button,.tab')].filter(e=>e.offsetParent).map(e=>e.getBoundingClientRect().height))")
      (ok if h>=43 else bad).append(f'{name} min tap height {h}')
      (ok if not errs else bad).append(f'{name} errors {errs[:3]}')
      pg.screenshot(path=f'/tmp/chk_{name}.png');pg.close()
    br.close()
finally: srv.terminate()
print('\n'.join('OK   '+o for o in ok));print('\n'.join('FAIL '+b for b in bad));sys.exit(1 if bad else 0)
