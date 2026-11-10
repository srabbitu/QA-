import numpy as np, cv2, json
from PIL import Image
FR='/home/user/QA-/promo/pixel/frames/S08_disc_masters.png'
a=np.array(Image.open(FR).convert('RGB')).astype(int); r,g,b=a[...,0],a[...,1],a[...,2]
crit={'red':(r>140)&(g<100)&(b<90)&(r-g>80),
      'blue':(b>140)&(r<90)&(b-r>90)&(g<170),
      'green':(g>r+25)&(g>b+25)&(g<200),
      'purple':(b>r)&(r>g+10)&(b>110)&(r<200)}
C=[('red','L',[8,110,100,182]),('red','R',[158,132,192,184]),
   ('blue','L',[172,118,232,180]),('blue','R',[272,132,312,176]),
   ('green','L',[296,136,331,184]),('green','R',[393,136,448,184]),
   ('purple','L',[420,136,443,188]),('purple','R',[498,136,580,198])]
meta={};allm=np.zeros(a.shape[:2],np.uint8)
for col,side,(x0,y0,x1,y1) in C:
    m=np.zeros(a.shape[:2],bool); m[y0:y1,x0:x1]=crit[col][y0:y1,x0:x1]
    m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((3,3),np.uint8)).astype(bool)
    # include dark outline pixels adjacent to cape
    dark=(a.sum(-1)<180)
    ring=cv2.dilate(m.astype(np.uint8),np.ones((3,3),np.uint8)).astype(bool)&dark
    ring[:y0,:]=0;ring[y1:,:]=0;ring[:,:x0]=0;ring[:,x1:]=0
    m=m|ring
    ys,xs=np.where(m)
    bb=[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1]
    rgba=np.dstack([a,m*255]).astype(np.uint8)
    nm=f'cape_{col}{side}'
    Image.fromarray(rgba).crop(bb).save(f'layers/S08_disc_masters__{nm}.png')
    meta[nm]={'x':bb[0],'y':bb[1],'w':bb[2]-bb[0],'h':bb[3]-bb[1],'cape':side}
    allm|=m.astype(np.uint8)
mm=cv2.dilate(allm*255,np.ones((3,3),np.uint8))
pl=cv2.inpaint(cv2.imread(FR),mm,5,cv2.INPAINT_TELEA)
cv2.imwrite('plates/S08_disc_masters.png',pl)
L=json.load(open('../px/layers.json')); L['S08_disc_masters']=meta; json.dump(L,open('../px/layers.json','w'),indent=1)
# preview: masks overlay
ov=a.copy(); ov[allm.astype(bool)]=[255,0,255]
Image.fromarray(ov.astype(np.uint8)).resize((1200,676),Image.NEAREST).save('cape_mask.png')
print(meta)
