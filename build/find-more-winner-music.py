exec(open('build/find-winner-music.py',encoding='utf-8-sig').read().split('queries=')[0])
queries={'beethoven':'Beethoven Symphony No.9 Finale filetype:audio','kiev':'Great Gate Kiev filetype:audio','william-tell':'William Tell Overture finale filetype:audio'}
exec(open('build/find-winner-music.py',encoding='utf-8-sig').read().split('def get')[1].join(['def get','']).split('with concurrent')[0])
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(get,queries.items()))
