#!/usr/bin/python

import sys,os,shutil,json
import cgi
import redis
import time

#Change to your local folder from Lupa
path = "/home/rec/shared/storm/Lupa" 

fs = cgi.FieldStorage()


id_text = fs.getvalue('id')
title = fs.getvalue('title')
text = fs.getvalue('text')




r = redis.StrictRedis(host='localhost', port=6379, db=0)

if r.zrank('text_id_list',id_text) is None: #return null si no existeix la id_noticia
 	r.zadd('text_id_list',id_text,id_text)	#Llistat de totes les ids de les noticies
 	r.hmset(id_text,{"id":id_text,"tittle":title,"text":text}) #hash key -> id values -> id,titol,text
 	r.lpush('text_queue',id_text)#Afegim la id a la cua de lectura de storm

recommendationsGenerated = False
while not recommendationsGenerated:
	if(r.zcard('recommendations_'+str(id_text))<5):
		time.sleep(5)
	else:
		recommendationsGenerated = True


os.chdir(path)
os.system('/home/rec/shared/apache-maven-3.2.1/bin/mvn -q exec:java -Dexec.mainClass="cat.tv3.eng.rec.recomana.lupa.visualization.GenerateAllVisualization" -Dexec.args="172.21.110.182 6379"')
os.system("cp -rf /home/rec/shared/storm/Lupa/data_toVisualize/ /home/rec/shared/Apache-httpd/LupaVisualization/json/data_toVisualize/")

results2 = {}
results2['id'] = id_text
results2['title'] = title
results2['text'] = text

#myjson = json.load(sys.stdin)
# Do something with 'myjson' object

print 'Content-Type: application/json\n\n'
print json.dumps(results2)    # or "json.dump(result, sys.stdout)"

