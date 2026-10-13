from library_common import *
TOPICS=[topic('recits-autochtones','Récits autochtones — Traditions nommées','Contes et légendes',[
 'https://oneida.on.ca/about/oneida-creation-story/',
 'https://www.historymuseum.ca/wp-content/uploads/2020/06/Creation-of-Haidagwaii-EN-REV1.pdf',
 'https://epe.lac-bac.gc.ca/100/205/301/ic/cdc/world_around_me/world/vr1/pop-ups/legends.htm?nodisclaimer=1',
 'https://www.thecanadianencyclopedia.ca/en/article/glooscap','https://glooscapfirstnation.com/'],[
 mc('Dans le récit oneida de la Femme du Ciel, quel animal porte la nouvelle terre ?','La tortue',['Le loup','L’aigle','Le castor'],'turtle'),
 mc('Quel oiseau est un transformateur dans le récit haïda présenté par GwaaGanad ?','Le corbeau',['Le paon','L’autruche','Le flamant'],'raven'),
 mc('À quel milieu Sedna est-elle liée dans les récits inuit ?','La mer',['Le désert','Les volcans','La jungle']),
 mc('Dans le récit oneida, qui empêche la Femme du Ciel de tomber dans l’eau ?','Des oiseaux',['Des chevaux','Des loups','Des cerfs']),
 mc('Quel héros est associé notamment aux récits mi’kmaq ?','Glooscap',['Zeus','Merlin','Robin des Bois']),
 ],[
 buzz('Dans le récit oneida, la Femme du Ciel arrive-t-elle du ciel ou de la mer ?','Du ciel',aliases=['Ciel']),
 buzz('Quel animal représenté ici apparaît dans les récits marins de Sedna ?','Un phoque','seal',['Phoque']),
 buzz('Quel oiseau noir se transforme en personnage dans des récits haïdas ?','Le corbeau','raven',['Corbeau']),
 buzz('Quel animal plongeur rapporte de la terre dans le récit oneida présenté ici ?','Le rat musqué',aliases=['Rat musqué']),
 buzz('La tradition mi’kmaq de Glooscap vient de quel continent ?','L’Amérique du Nord',aliases=['Amérique du Nord']),
 ],[
 who('La Femme du Ciel',['Mon récit est notamment raconté par les Oneida.','Des oiseaux me portent après ma chute.','Une tortue me reçoit au-dessus de l’eau.','Mon nom français dit que je suis une femme venue du ciel.'],['Femme du Ciel','Sky Woman']),
 who('Le Corbeau',['Je joue un rôle de transformateur dans des récits haïdas.','Je peux prendre une forme humaine.','Mon plumage est noir.','Je suis l’oiseau appelé Raven en anglais.'],['Corbeau','Raven']),
 who('Sedna',['Mon récit est raconté dans plusieurs régions inuit.','Les versions portent des noms et détails différents.','Je suis associée aux animaux marins.','Je suis la figure souvent appelée la maîtresse de la mer.']),
 who('Glooscap',['Je suis un héros de récits wabanaki.','Je suis notamment associé à la tradition mi’kmaq.','Une Première Nation de Nouvelle-Écosse porte mon nom.','Mon nom est aussi écrit Gluskab ou Kluskap.'],['Gluskab','Kluskap','Glooskap']),
 who('La Tortue',['Dans le récit oneida, je reste au-dessus de l’eau.','Je reçois la Femme du Ciel.','La terre grandit sur mon dos.','Le nom Turtle Island rappelle mon rôle.'],['Tortue','Grande Tortue']),
 ])]
