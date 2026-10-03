import numpy as np, cv2, pickle
from mg import *
I=load('src2.png'); bg=np.load('l2/bg.npy')
d=np.abs(I-bg).max(2)
R={'logo':(380,80,700,215),'for_every':(250,415,600,471),'woman':(250,471,830,592),
   'we_care':(600,1195,830,1247),'about':(250,1247,830,1390),'line_l':(255,1500,450,1515),
   'line_r':(630,1500,830,1515),'promo':(440,1485,640,1528),'pink':(430,1530,650,1610),
   'pink_oct':(370,1735,715,1797),'arabic':(355,1797,725,1865),
   'ribbon_tr':(740,0,1080,335),'ribbon_bl':(0,1580,335,1920)}
white=['for_every','woman','we_care','about','line_l','line_r','promo','pink','pink_oct','arabic']
out={}
recon=bg.copy()
for k,(x0,y0,x1,y1) in R.items():
    m=np.zeros(d.shape,bool); m[y0:y1,x0:x1]=True
    if k in white:
        a=white_matte(I,bg)*m; a[a<0.004]=0; rgb=unpremult(I,bg,a)
    else:
        a=np.clip((d-0.01)/0.14,0,1)*m; rgb=unpremult(I,bg,a)
    ys,xs=np.where(a>0.01); bb=(xs.min(),ys.min(),xs.max()+1,ys.max()+1)
    print(k,bb)
    out[k]=(rgb[bb[1]:bb[3],bb[0]:bb[2]].copy(),a[bb[1]:bb[3],bb[0]:bb[2]].copy(),bb)
    recon=recon*(1-a[...,None])+rgb*a[...,None]
px=(268,605,812,1185)
recon[px[1]:px[3],px[0]:px[2]]=I[px[1]:px[3],px[0]:px[2]]
err=np.abs(recon-I).max(2)
print('recon err mean',err.mean(),'p99.9',np.percentile(err,99.9),'max',err.max())
pickle.dump({'els':out,'photo':I[px[1]:px[3],px[0]:px[2]].copy(),'pbb':px},open('l2/layers.pkl','wb'))
cv2.imwrite('l2/err.png',(np.clip(err*10,0,1)*255).astype(np.uint8))
