import numpy as np, cv2, pickle
from mg import *
I=load('src1.png')
R={'logo':(395,88,690,200),'for_every':(285,792,780,846),'we_stand':(45,846,1030,948),
   'promo':(350,1003,563,1047),'divider':(570,1003,592,1047),'pink':(598,996,728,1054),
   'pink_oct':(372,1735,708,1797),'arabic':(358,1797,722,1858)}
pinkm=(I[:,:,0]>0.72)&(I[:,:,0]-I[:,:,1]>0.22)&(I[:,:,2]-I[:,:,1]>0.0)
full=np.zeros(I.shape[:2],bool); roi={}
for k,(x0,y0,x1,y1) in R.items():
    m=np.zeros(I.shape[:2],bool); m[y0:y1,x0:x1]=True
    if k=='divider':
        md=np.zeros_like(m); md[1005:1049,577:584]=True
    else:
        mn=I.min(2)
        if k in('promo','pink'):
            mu=(mn*255).astype(np.uint8); med=cv2.medianBlur(mu,25).astype(np.float32)/255
            md=dilate(((mn-med)>0.06)&m,3)&m
        else:
            md=dilate((mn>0.94)&m,3)&m
        if k=='logo': md|=dilate(pinkm&m,3)&m
    roi[k]=md; full|=md
P=nc_fill(I,full)
els={}; recon=P.copy()
for k,md in roi.items():
    a=white_matte(I,P)
    if k=='logo':
        d=np.abs(I-P).max(2); a=np.maximum(a,np.clip((d-0.03)/0.2,0,1)*dilate(pinkm,3))
    a=a*md; a[a<0.004]=0
    rgb=unpremult(I,P,a)
    ys,xs=np.where(a>0.004); bb=(int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)); print(k,bb)
    els[k]=(rgb[bb[1]:bb[3],bb[0]:bb[2]].copy(),a[bb[1]:bb[3],bb[0]:bb[2]].copy(),bb)
    recon=recon*(1-a[...,None])+rgb*a[...,None]
err=np.abs(recon-I).max(2); print('recon err',err.mean(),np.percentile(err,99.9),err.max())
np.save('l1/plate.npy',P); pickle.dump(els,open('l1/layers.pkl','wb'))
cv2.imwrite('l1/plate.png',to_u8(P)[:,:,::-1])
cv2.imwrite('l1/mask.png',(full*255).astype(np.uint8))
