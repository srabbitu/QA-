import numpy as np, cv2, json
from PIL import Image
T='/root/.claude/projects/-home-user-QA-/b3677a6b-6327-5896-8220-0da572bf7c59/tool-results/mcp-Canva-blob-'
FR='/home/user/QA-/promo/pixel/frames/'
L=[ # name, blob, box(x0,y0,x1,y1) in 600x338, extra exclude rects
 ('S01_city_morning','pup','1794293379454-0c61yq',[100,150,240,310],[]),
 ('S02_phone_rings','pup','1794293428371-o3y8az',[155,55,345,250],[]),
 ('S02_phone_rings','phone','1794293435909-2yongm',[330,180,560,320],[]),
 ('S03_round1','pup','1794293443638-bum359',[50,190,170,310],[]),
 ('S03_round1','boss','1794293478171-1gvyti',[285,0,600,215],[[285,0,600,30]]),
 ('S04_ko','pup','1794293478171-1gvyti',[40,170,240,320],[]),
 ('S04_ko','boss','1794293779345-9co2px',[270,0,600,225],[]),
 ('S05_drift','boat','1794293779345-9co2px',[0,170,240,338],[]),
 ('S09b_qa_gate','frog','1794293795568-c7xfsc',[330,0,430,62],[]),
 ('S13_rematch','pup','1794293795568-c7xfsc',[45,180,215,305],[]),
 ('S13_rematch','boss','1794293808587-exxi8i',[340,60,590,230],[]),
 ('S06_harbor_welcome','terry','1794293808587-exxi8i',[130,70,300,280],[]),
 ('S09b_qa_gate','pup','1794293868665-2rstqf',[255,165,390,290],[]),
 ('S10_deflect','pup','1794293876492-zpqu1o',[20,60,330,300],[]),
 ('S11_bubble_tea','pup','1794293884431-t9jins',[225,140,385,295],[]),
 ('S12_level_up','pup','1794293892510-mdf74z',[215,90,400,300],[]),
 ('S14_win','phone','1794294117402-nt4r33',[290,125,490,320],[]),
 ('S14_win','pup','1794294152935-nvxq79',[90,110,292,320],[]),
]
masks={}
meta={}
for scene,name,blob,box,exc in L:
    a=np.array(Image.open(T+blob+'.png').convert('RGB')).astype(float)
    mag=np.array([255,0,255.])
    d=np.sqrt(((a-mag)**2).sum(-1))
    al=np.clip((d-60)/90,0,1)
    m=np.zeros_like(al); x0,y0,x1,y1=box; m[y0:y1,x0:x1]=1
    for e in exc: m[e[1]:e[3],e[0]:e[2]]=0
    al*=m
    # unblend magenta
    c=np.where(al[...,None]>0.05,(a-(1-al[...,None])*mag)/np.maximum(al[...,None],0.05),0)
    c=np.clip(c,0,255)
    # use original frame colors where solid (cleaner)
    orig=np.array(Image.open(FR+scene+'.png').convert('RGB')).astype(float)
    solid=al>0.9
    c[solid]=orig[solid]
    rgba=np.dstack([c,al*255]).astype(np.uint8)
    ys,xs=np.where(al>0.1)
    bb=[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1]
    Image.fromarray(rgba).crop(bb).save(f'layers/{scene}__{name}.png')
    meta.setdefault(scene,{})[name]={'x':bb[0],'y':bb[1],'w':bb[2]-bb[0],'h':bb[3]-bb[1]}
    masks.setdefault(scene,np.zeros(al.shape))
    masks[scene]=np.maximum(masks[scene],al)
for scene,mk in masks.items():
    orig=cv2.imread(FR+scene+'.png')
    mm=(mk>0.08).astype(np.uint8)*255
    mm=cv2.dilate(mm,np.ones((7,7),np.uint8))
    pl=cv2.inpaint(orig,mm,6,cv2.INPAINT_TELEA)
    cv2.imwrite(f'plates/{scene}.png',pl)
json.dump(meta,open('layers.json','w'),indent=1)
print(json.dumps(meta)[:600])
