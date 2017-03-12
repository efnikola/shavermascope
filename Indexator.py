import cv2

import SearchCV
import re

t=SearchCV.Finder()
path=t.findpostid("images/post_id_0_39851.jpg")
print(path[1])
#//post_id_(.+?)_+?/.jpg

result=""
string="images/post_id_0_39851.jpg"
counter=0
f = True
for c in string:
    if(c=='.'):
        f=False
    if(counter==3 and f):
        result+=c
    if(c=='_'):
        counter=counter+1

print(result)

#print(p)