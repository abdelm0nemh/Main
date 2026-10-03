import numpy as np, cv2
I=cv2.imread('src2.png',cv2.IMREAD_COLOR)[:,:,::-1].astype(np.float32)/255
H,W=I.shape[:2]
# initial bg mask: dark pixels near typical bg
lum=I.mean(2)
cand=(lum<0.25)&(I[:,:,0]>0.15)&(I[:,:,0]<0.4)
cand=cv2.erode(cand.astype(np.uint8),np.ones((9,9),np.uint8))>0
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
x=xx/W-0.5; y=yy/H-0.5
feats=[np.ones_like(x),x,y,x*x,y*y,x*y,x**3,y**3,x*x*y,x*y*y,x**4,y**4,x*x*y*y]
A=np.stack([f[cand] for f in feats],1)
bg=np.zeros_like(I)
for c in range(3):
    coef,*_=np.linalg.lstsq(A,I[:,:,c][cand],rcond=None)
    bg[:,:,c]=sum(k*f for k,f in zip(coef,feats))
res=np.abs(I-bg)[cand]
print('residual mean/95/max',res.mean(),np.percentile(res,95),res.max())
d=np.abs(I-bg).max(2)
fg=d>0.04
n,lab,st,cen=cv2.connectedComponentsWithStats(cv2.dilate(fg.astype(np.uint8),np.ones((15,15),np.uint8)))
for k in range(1,n):
    x0,y0,w,h,a=st[k]
    if a>50: print(k,x0,y0,w,h,a)
np.save('l2/bg.npy',bg)
cv2.imwrite('l2/diff.png',(np.clip(d*4,0,1)*255).astype(np.uint8))
