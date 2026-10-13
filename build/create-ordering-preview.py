from pathlib import Path

source = Path('build/preview-wager.cjs').read_text(encoding='utf-8')
source = source.replace("currentQuestion:active?(location.search.includes('choices=1')?", "currentQuestion:active?(location.search.includes('ordering=1')?{type:'ordering',id:'order',items:[{id:'h',text:'Traversée de l’Hellespont vers l’Asie'},{id:'g',text:'Bataille de Gaugamèles contre Darius III'},{id:'e',text:'Conquête de l’Égypte'}]}:location.search.includes('choices=1')?")
source = source.replace("['wager','wager-zero']", "['ordering']").replace("'&wager=1'", "'&ordering=1'").replace('wager-preview-profile', 'ordering-preview-profile')
needle = "      const screenshot=await send('Page.captureScreenshot',{format:'png'},sessionId);"
source = source.replace(needle, '''      const inspected = await send('Runtime.evaluate',{expression:'JSON.stringify({cards:document.querySelectorAll(".ordering-card").length,height:document.documentElement.scrollHeight,viewport:innerHeight,rects:Array.from(document.querySelectorAll(".order-handle")).map(e=>{const r=e.getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2}})})',returnByValue:true},sessionId);
      const view=JSON.parse(inspected.result.value);
      if(view.cards!==3 || view.height>view.viewport) throw new Error('Ordering does not fit mobile viewport: '+inspected.result.value);
      const first=view.rects[0], last=view.rects[2];
      await send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[first]},sessionId);
      await send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:first.x,y:last.y+20}]},sessionId);
      await send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]},sessionId);
      const reordered=await send('Runtime.evaluate',{expression:'document.querySelectorAll(".order-text")[2].textContent',returnByValue:true},sessionId);
      if(reordered.result.value!=='Traversée de l’Hellespont vers l’Asie') throw new Error('Touch drag did not move the card');
      const screenshot=await send('Page.captureScreenshot',{format:'png'},sessionId);''')
Path('build/preview-ordering.cjs').write_text(source, encoding='utf-8')
