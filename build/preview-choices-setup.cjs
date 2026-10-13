const fs=require('node:fs');
const file='build/preview-browser-player.cjs';
let s=fs.readFileSync(file,'utf8');
s=s.replace("active?{type:'textAnswer',id:'q',prompt:'Quel est le plus grand océan du monde ?'}:null", "active?(location.search.includes('choices=1')?{type:'multipleChoice',id:'choice',options:['Océan Atlantique','Océan Pacifique','Océan Indien','Océan Arctique']}:{type:'textAnswer',id:'q'}):null");
fs.writeFileSync(file,s);
