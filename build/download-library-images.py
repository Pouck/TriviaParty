"""Download public-domain / freely licensed illustrative photos, retaining credits."""
from pathlib import Path
import importlib.util,json,runpy,shutil,sys
sys.path.insert(0,str(Path(__file__).parent))
OUT=Path('package-examples/library-2026-10-12');ASSETS=OUT/'assets';ASSETS.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('photo_cache',Path('build/download-art-images.py'))
cache=importlib.util.module_from_spec(spec);spec.loader.exec_module(cache)
cache.OUT=OUT;cache.IMAGES=ASSETS
OVERRIDES_FILE=OUT/'photo-overrides.json'
cache.OVERRIDES=json.loads(OVERRIDES_FILE.read_text(encoding='utf-8')) if OVERRIDES_FILE.exists() else {}
PHOTOS={
 'toucan':'Toco toucan','peacock':'Indian peafowl','ostrich':'Common ostrich','owl':'Great horned owl',
 'ladybird':'Coccinella septempunctata','bee':'Western honey bee','ant':'Ant','butterfly':'Monarch butterfly',
 'zebra':'Plains zebra','giraffe':'Giraffe','lion':'Lion','beaver':'North American beaver',
 'octopus':'Common octopus','seahorse':'Seahorse','dolphin':'Common bottlenose dolphin','turtle':'Green sea turtle',
 'seal':'Harbour seal','raven':'Common raven',
 'pizza':'Pizza','sushi':'Sushi','paella':'Paella','baguette':'Baguette','ramen':'Ramen',
 'eiffel':'Eiffel Tower','taj':'Taj Mahal','sydney':'Sydney Opera House','colosseum':'Colosseum',
 'wall':'Great Wall of China','pyramids':'Giza pyramid complex','everest':'Mount Everest','fuji':'Mount Fuji',
 'berlin-wall':'Berlin Wall','montreal':'Montreal','antarctica':'Antarctica',
 'guitar':'Acoustic guitar','piano':'Piano','violin':'Violin','harp':'Harp','saxophone':'Saxophone',
 'trumpet':'Trumpet','accordion':'Accordion','horse':'Horse','wolf':'Wolf','warthog':'Common warthog',
 'forest':'Forest','moon':'Moon','ocean':'Pacific Ocean','river':'Saint Lawrence River',
 'cow':'Cattle','pig':'Pig','mushroom':'Boletus edulis','rose':'Rose','swan':'Mute swan',
 'notre-dame':'Notre-Dame de Paris','whale':'Sperm whale','lake':'Walden Pond','hedgehog':'Hedgehog',
 'basketball':'Basketball','snowmobile':'Snowmobile','liberty-statue':'Statue of Liberty','rushmore':'Mount Rushmore',
 'versailles':'Palace of Versailles',
 'croissant':'Croissant','taco':'Taco','cacao':'Theobroma cacao','tiramisu':'Tiramisu',
}
def topics():return [t for file in Path('build').glob('library-*-data.py') for t in runpy.run_path(str(file))['TOPICS']]
if __name__=='__main__':
 used={q['image'] for t in topics() for mode in ('qcm','buzzer') for q in t[mode] if q.get('image')}
 existing={p['title']:p for file in Path('package-examples').glob('*/PHOTOS.json') if file.parent!=OUT for p in json.loads(file.read_text(encoding='utf-8')) if (file.parent/'assets'/p['file']).exists()}
 failures=[]
 for slug,title in PHOTOS.items():
  if slug not in used:continue
  if not (ASSETS/(slug+'.json')).exists() and title in existing:
   p=existing[title].copy();source=next(file.parent/'assets'/p['file'] for file in Path('package-examples').glob('*/PHOTOS.json') if (file.parent/'assets'/p['file']).exists())
   target=slug+source.suffix;shutil.copy2(source,ASSETS/target);p.update(slug=slug,file=target)
   (ASSETS/(slug+'.json')).write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  try:cache.download((slug,title))
  except Exception as error:failures.append((slug,str(error)));print('RETRY',slug,str(error),flush=True)
 records=[json.loads(file.read_text(encoding='utf-8')) for file in ASSETS.glob('*.json')]
 (OUT/'PHOTOS.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Cached',len(records),'photos. Remaining:',failures,flush=True)
 if failures:sys.exit(1)
