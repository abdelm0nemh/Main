import numpy as np, cv2, pickle
from mg import *
I=load('src3.png')
def rrect(x0,y0,x1,y1,r,ss=4):
    m=np.zeros((H*1,W*1),np.uint8)
    big=np.zeros((H*ss,W*ss),np.uint8)
    X0,Y0,X1,Y1,R=[int(round(v*ss)) for v in (x0,y0,x1,y1,r)]
    cv2.rectangle(big,(X0+R,Y0),(X1-R,Y1),255,-1); cv2.rectangle(big,(X0,Y0+R),(X1,Y1-R),255,-1)
    for cx,cy in ((X0+R,Y0+R),(X1-R,Y0+R),(X0+R,Y1-R),(X1-R,Y1-R)): cv2.circle(big,(cx,cy),R,255,-1)
    return cv2.resize(big,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)/255
R={'logo':(395,88,690,200),'pink_oct':(375,735,710,790),'arabic':(360,790,722,845),
   'for_me':(180,860,905,1055),'promo':(355,1110,565,1157),'divider':(575,1108,590,1158),'pink':(600,1100,728,1165)}
mn=I.min(2)
pinkm=(I[:,:,0]>0.72)&(I[:,:,0]-I[:,:,1]>0.22)&(I[:,:,2]-I[:,:,1]>0.0)
full=np.zeros(mn.shape,bool); roi={}
mu=(mn*255).astype(np.uint8); med=cv2.medianBlur(mu,25).astype(np.float32)/255
for k,(x0,y0,x1,y1) in R.items():
    m=np.zeros(mn.shape,bool); m[y0:y1,x0:x1]=True
    if k in ('promo','pink','divider','arabic','pink_oct'):
        md=dilate(((mn-med)>0.08)&m,3)&m

    else:
        md=dilate((mn>0.93)&m,3)&m
    if k=='logo': md|=dilate(pinkm&m,3)&m
    roi[k]=md; full|=md
P1=nc_fill(I,full)
pill=rrect(318.5,1088.5,761.5,1176.5,44)
pillm=dilate(pill>0.01,5)
plate=nc_fill(P1,pillm)
plate=plate*(1-pill[...,None])+plate*pill[...,None]  # no-op, clarity
els={}; recon=plate*(1-pill[...,None])+P1*pill[...,None]
for k,md in roi.items():
    a=white_matte(I,P1)
    if k=='logo':
        d=np.abs(I-P1).max(2); a=np.maximum(a,np.clip((d-0.03)/0.2,0,1)*dilate(pinkm,3))
    a=a*md; a[a<0.004]=0
    rgb=unpremult(I,P1,a)
    ys,xs=np.where(a>0.004); bb=(int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)); print(k,bb)
    els[k]=(rgb[bb[1]:bb[3],bb[0]:bb[2]].copy(),a[bb[1]:bb[3],bb[0]:bb[2]].copy(),bb)
    recon=recon*(1-a[...,None])+rgb*a[...,None]
err=np.abs(recon-I).max(2); print('recon err',err.mean(),np.percentile(err,99.9),err.max())
pb=(316,1086,764,1179)
els['pill']=(P1[pb[1]:pb[3],pb[0]:pb[2]].copy(),pill[pb[1]:pb[3],pb[0]:pb[2]].copy(),pb)
np.save('l3/plate.npy',plate); np.save('l3/panel.npy',rrect(115.5,630.5,964.5,1289.5,62))
pickle.dump(els,open('l3/layers.pkl','wb'))
cv2.imwrite('l3/plate.png',to_u8(plate)[:,:,::-1]); cv2.imwrite('l3/p1.png',to_u8(P1)[:,:,::-1])
