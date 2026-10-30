import numpy as np, cv2, sys, os
rng=np.random.default_rng(7)
W,H=1080,1350
SRC='/sessions/dazzling-upbeat-knuth/mnt/amaru_black'
OUT=sys.argv[1]; os.makedirs(OUT,exist_ok=True)

def noise(h,w,scale,oct=4,seed=0):
    r=np.random.default_rng(seed); acc=np.zeros((h,w)); amp=1; tot=0
    for o in range(oct):
        s=max(2,int(scale/(2**o)))
        n=r.random((h//s+2,w//s+2))
        acc+=amp*cv2.resize(n,(w,h),interpolation=cv2.INTER_CUBIC); tot+=amp; amp*=0.5
    return acc/tot

def blend(img,col,mask):
    m=mask[...,None]; return img*(1-m)+np.array(col,float)*m if np.ndim(col)==1 else img*(1-m)+col*m

def leaf_mask(p0,p1,width,bend=0.15,shape='lance'):
    # returns mask, and per-pixel u (along) v (across) coords
    p0=np.array(p0,float); p1=np.array(p1,float); d=p1-p0; L=np.linalg.norm(d); t=d/L; n=np.array([-t[1],t[0]])
    yy,xx=np.mgrid[0:H,0:W]; P=np.stack([xx-p0[0],yy-p0[1]],-1)
    u=(P@t)/L; v=P@n
    v=v-bend*L*4*u*(1-u)  # curved midrib
    if shape=='lance': prof=width*np.clip(np.sin(np.pi*np.clip(u,0,1))**0.7,0,1)
    else: prof=width*np.clip(1-np.abs(2*u-1)**2.2,0,1)  # strap
    prof=np.maximum(prof,1e-3)
    m=((u>0)&(u<1)&(np.abs(v)<prof)).astype(float)
    return m,u,v/prof

def draw_leaf(img,p0,p1,width,base,blur=0,bend=0.15,shape='lance',veins=True,light=1.0,seed=0):
    m,u,vn=leaf_mask(p0,p1,width,bend,shape)
    base=np.array(base,float)
    tex=noise(H,W,40,3,seed)
    shade=(0.75+0.35*np.clip(1-np.abs(vn),0,1)**0.6)*(0.9+0.2*tex)*light
    # fold: one side darker
    shade*=np.where(vn>0,1.0,0.82)
    col=np.nan_to_num(base[None,None,:]*shade[...,None])
    if veins:
        mid=np.exp(-(vn*width/2.2)**2)
        col=col*(1-0.35*mid[...,None])+np.array([200,235,210])*0.35*mid[...,None]*light
        lat=(np.sin((u*38 - np.abs(vn)*2.2)*np.pi)**40)*(np.abs(vn)<0.95)
        col=col*(1-0.12*lat[...,None])+np.array([180,220,200])*0.12*lat[...,None]
    edge=cv2.GaussianBlur(m,(0,0),1.2)
    if blur>0:
        col=cv2.GaussianBlur(col*edge[...,None],(0,0),blur); e=cv2.GaussianBlur(edge,(0,0),blur)
        col=col/np.maximum(e,1e-3)[...,None]; edge=e
    return img*(1-edge[...,None])+col*edge[...,None]

def bokeh_bg(c1,c2,seed,spots=None):
    n=noise(H,W,300,4,seed)
    img=np.array(c1,float)*(1-n[...,None])+np.array(c2,float)*n[...,None]
    if spots:
        r=np.random.default_rng(seed)
        layer=np.zeros((H,W,3))
        for _ in range(spots[0]):
            x,y=r.integers(0,W),r.integers(0,H); rad=r.integers(15,55)
            cv2.circle(layer,(int(x),int(y)),int(rad),[float(c)*f for c in spots[1] for f in [r.uniform(0.3,1)]] if False else (np.array(spots[1],float)*r.uniform(0.3,1)).tolist(),-1,cv2.LINE_AA)
        img+=cv2.GaussianBlur(layer,(0,0),6)*0.5
    return img

def vignette(img,s=0.45):
    yy,xx=np.mgrid[0:H,0:W]; d=np.sqrt(((xx-W/2)/W)**2+((yy-H/2)/H)**2)
    return img*(1-s*np.clip(d*1.6,0,1)**2)[...,None]

def light_dir(img,ang=( -0.3,-0.4),s=0.25):
    yy,xx=np.mgrid[0:H,0:W]; g=( (xx/W-0.5)*ang[0]+(yy/H-0.5)*ang[1])
    return img*(1+s*g/0.5)[...,None]*1.0

def jewel(idx):
    f=[x for x in os.listdir(SRC) if x.startswith('%02d_'%idx)][0]
    im=cv2.imread(os.path.join(SRC,f)).astype(float)
    lum=im.max(2)
    m=np.clip((lum-38)/40,0,1)
    k=(m>0.5).astype('uint8'); n,lab,st,_=cv2.connectedComponentsWithStats(k)
    big=(lab==1+np.argmax(st[1:,4])).astype('uint8')
    big=cv2.dilate(big,np.ones((9,9),np.uint8))
    m=m*big
    m=cv2.GaussianBlur(m,(3,3),0)
    x,y,w,h=cv2.boundingRect((m>0.05).astype('uint8'))
    im=im[y:y+h,x:x+w]; m=m[y:y+h,x:x+w]
    # unpremultiply-ish: remove black fringe, slightly brighten for daylight
    im=np.clip(im/np.maximum(m,0.35)[...,None],0,255)
    im=np.clip(im*1.12+6,0,255)
    return im,m

def place(img,piece,cx,cy,height,angle,shadow=(18,26),sh_blur=14,sh_dark=0.55,contact=0.35):
    im,m=piece; s=height/im.shape[0]
    im=cv2.resize(im,None,fx=s,fy=s,interpolation=cv2.INTER_AREA); m=cv2.resize(m,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
    h,w=m.shape; D=int(np.hypot(h,w))+40
    ci=np.zeros((D,D,3)); cm=np.zeros((D,D)); oy,ox=(D-h)//2,(D-w)//2
    ci[oy:oy+h,ox:ox+w]=im; cm[oy:oy+h,ox:ox+w]=m
    R=cv2.getRotationMatrix2D((D/2,D/2),angle,1)
    ci=cv2.warpAffine(ci,R,(D,D),flags=cv2.INTER_CUBIC); cm=cv2.warpAffine(cm,R,(D,D),flags=cv2.INTER_LINEAR)
    x0,y0=int(cx-D/2),int(cy-D/2)
    full_m=np.zeros((H,W)); full_i=np.zeros((H,W,3))
    ys,xs=slice(max(y0,0),min(y0+D,H)),slice(max(x0,0),min(x0+D,W))
    full_m[ys,xs]=cm[ys.start-y0:ys.stop-y0, xs.start-x0:xs.stop-x0]
    full_i[ys,xs]=ci[ys.start-y0:ys.stop-y0, xs.start-x0:xs.stop-x0]
    Msh=np.float32([[1,0,shadow[0]],[0,1,shadow[1]]])
    sh=cv2.warpAffine(full_m,Msh,(W,H)); sh=cv2.GaussianBlur(sh,(0,0),sh_blur)*sh_dark
    ct=cv2.GaussianBlur(cv2.warpAffine(full_m,np.float32([[1,0,4],[0,1,6]]),(W,H)),(0,0),3)*contact
    img=img*(1-np.clip(sh+ct,0,0.85))[...,None]
    # reflect environment tint subtly onto gold
    env=cv2.GaussianBlur(img,(0,0),40)
    gold=full_i*0.93+env*0.07
    return img*(1-full_m[...,None])+gold*full_m[...,None]

def pair(img,idx,c1,c2,h,a1,a2,**kw):
    p=jewel(idx)
    img=place(img,p,*c1,h,a1,**kw); img=place(img,p,*c2,h,a2,**kw); return img

def finish(img,name,grain=3.0):
    img=img+np.random.default_rng(1).normal(0,grain,img.shape)
    img=vignette(img,0.35)
    cv2.imwrite(os.path.join(OUT,name),np.clip(img,0,255).astype('uint8'),[cv2.IMWRITE_JPEG_QUALITY,95])

# BGR colors
G_DARK=(30,60,25); G_MID=(50,110,45); G_LIGHT=(110,185,120)

# 01 Tairona - Heliconia
def s01():
    img=bokeh_bg((18,40,14),(45,95,40),11,(40,(120,200,140)))
    for i,(a,b,w,bl) in enumerate([((-100,200),(700,-80),130,18),((1200,300),(500,1000),150,16),((900,-50),(1150,700),110,20),((-80,1100),(500,1450),120,14)]):
        img=draw_leaf(img,a,b,w,(40,105,45),blur=bl,seed=i)
    # heliconia bracts (lobster claw) along zigzag stem upper right, slightly blurred
    layer=img.copy()
    stem=[(720,80),(860,1000)]
    for k in range(6):
        t=k/5.5; cx=720+140*t; cy=90+150*k; side=1 if k%2==0 else -1
        p0=(cx,cy); p1=(cx+side*230,cy-70)
        layer=draw_leaf(layer,p0,p1,46,(40,40,215),blur=0,bend=-0.25*side,veins=False,seed=20+k,light=1.05)
        # yellow/green tip
        layer=draw_leaf(layer,(p1[0]-side*70,p1[1]+18),p1,22,(60,200,235),veins=False,bend=-0.1*side,seed=30+k)
        cv2.line(layer,(int(cx),int(cy)),(int(cx+side*20),int(cy+150)),(20,60,110),10,cv2.LINE_AA)
    layer=cv2.GaussianBlur(layer,(0,0),5)
    img=layer
    # foreground broad leaf, sharp
    img=draw_leaf(img,(-150,1400),(1150,500),330,(45,120,50),bend=0.08,seed=3,light=1.1)
    img=light_dir(img)
    img=pair(img,1,(330,930),(600,860),330,12,-8)
    finish(img,'01_tairona_plant.jpg')

# 02 Zenu fresh caña flecha leaves
def s02():
    img=bokeh_bg((25,55,30),(70,140,90),12,(30,(160,230,200)))
    for i in range(9):
        y=rng.integers(-200,1500); ang=rng.uniform(-0.5,-0.2); L=1700
        p0=(-300,y); p1=(-300+L*np.cos(ang),y+L*np.sin(ang))
        img=draw_leaf(img,p0,p1,rng.integers(40,70),(85,175,125),blur=rng.choice([0,0,2,8]),bend=rng.uniform(-0.04,0.04),shape='strap',seed=40+i,light=rng.uniform(0.85,1.1))
    img=light_dir(img,s=0.2)
    img=pair(img,2,(380,700),(680,640),380,20,8)
    finish(img,'02_zenu_plant.jpg')

# 03 Quimbaya - guadua
def s03():
    img=bokeh_bg((60,75,55),(160,175,150),13,(25,(220,235,220)))  # misty
    # blurred wax palm fronds
    for i in range(14):
        a=rng.uniform(-np.pi,0); c=(800,150)
        img=draw_leaf(img,c,(c[0]+700*np.cos(a),c[1]+500*np.sin(a)+350),35,(70,110,70),blur=14,shape='strap',veins=False,seed=60+i)
    # guadua culm: horizontal-ish cylinder
    yy,xx=np.mgrid[0:H,0:W]; ang=np.deg2rad(-8); cx,cy=540,820; R=230
    d=(-(xx-cx)*np.sin(ang)+(yy-cy)*np.cos(ang)); along=(xx-cx)*np.cos(ang)+(yy-cy)*np.sin(ang)
    m=(np.abs(d)<R).astype(float); z=np.clip(d/R,-1,1)
    shade=0.45+0.75*np.clip(np.sqrt(1-z**2)*0.9-0.35*z,0,1.2)
    tex=noise(H,W,25,3,5); streak=noise(H,W,6,2,9)
    base=np.array([50,140,95])
    col=base*shade[...,None]*(0.88+0.2*tex[...,None])*(0.94+0.1*streak[...,None])
    spec=np.exp(-((z+0.45)/0.12)**2)*0.5
    col+=np.array([170,230,220])*spec[...,None]
    for nx in (-420,360):
        node=np.exp(-((along-nx)/9)**2)
        col=col*(1-0.45*node[...,None])+np.array([90,170,190])*0.25*node[...,None]
        ring=np.exp(-((along-nx-14)/4)**2); col+=np.array([120,180,170])*0.3*ring[...,None]
    e=cv2.GaussianBlur(m,(0,0),1.5)
    img=img*(1-e[...,None])+col*e[...,None]
    img=light_dir(img,s=0.18)
    img=pair(img,3,(420,830),(660,800),380,-4,6,shadow=(14,26),sh_blur=10)
    finish(img,'03_quimbaya_plant.jpg')

def fibers(img,n,color,seed,width=(2,5),dir_ang=-0.3,curl=60,area=(0,0,W,H)):
    r=np.random.default_rng(seed)
    layer=np.zeros((H,W,3)); mask=np.zeros((H,W)); shadow=np.zeros((H,W))
    for i in range(n):
        x0=r.uniform(area[0]-300,area[2]); y0=r.uniform(area[1],area[3])
        L=r.uniform(600,1600); a=dir_ang+r.normal(0,0.12)
        t=np.linspace(0,1,80); ph=r.uniform(0,6); fr=r.uniform(0.5,2)
        xs=x0+L*t*np.cos(a)-curl*np.sin(t*fr*np.pi+ph)*np.sin(a)
        ys=y0+L*t*np.sin(a)+curl*np.sin(t*fr*np.pi+ph)*np.cos(a)
        pts=np.stack([xs,ys],1).astype(np.int32)
        w=int(r.uniform(*width)); c=np.array(color)*r.uniform(0.8,1.12)
        cv2.polylines(shadow,[pts+[3,5]],False,1,w+2,cv2.LINE_AA)
        cv2.polylines(layer,[pts],False,c.tolist(),w,cv2.LINE_AA)
        cv2.polylines(mask,[pts],False,1,w,cv2.LINE_AA)
        hl=pts-[0,max(1,w//3)]
        cv2.polylines(layer,[hl],False,(np.minimum(c*1.25,255)).tolist(),max(1,w//3),cv2.LINE_AA)
    sh=cv2.GaussianBlur(shadow,(0,0),3)*0.45
    img=img*(1-sh[...,None]); m=np.clip(mask,0,1)
    return img*(1-m[...,None])+layer*m[...,None]

# 04 Zenu raw fibers
def s04():
    img=bokeh_bg((60,95,120),(120,165,195),14)
    tex=noise(H,W,8,2,4); img*= (0.9+0.15*tex)[...,None]
    for k,(n,c,s) in enumerate([(160,(150,190,215),1),(180,(170,210,230),2),(140,(185,222,238),3)]):
        img=fibers(img,n,c,s,width=(3,8))
    img=light_dir(img,s=0.22)
    img=pair(img,4,(370,700),(690,660),380,-10,6,shadow=(16,24),sh_blur=10)
    finish(img,'04_zenu_plant.jpg')

def weave(img,area,cell=58,seed=0,angle=0,stripe=True):
    x0,y0,x1,y1=area
    yy,xx=np.mgrid[0:H,0:W].astype(float)
    a=np.deg2rad(angle); u=(xx*np.cos(a)+yy*np.sin(a)); v=(-xx*np.sin(a)+yy*np.cos(a))
    iu=np.floor(u/cell); iv=np.floor(v/cell); fu=u/cell-iu; fv=v/cell-iv
    over=((iu+iv)%2==0)
    cream=np.array([175,215,232]); black=np.array([35,32,30])
    # pattern: cream/black stripes per strand (zenu motif)
    r=np.random.default_rng(seed)
    pat_u=r.random(400)<0.3; pat_v=r.random(400)<0.3
    su=pat_u[(iu.astype(int))%400]; sv=pat_v[(iv.astype(int))%400]
    colU=np.where(su[...,None] if stripe else False,black,cream); colV=np.where(sv[...,None] if stripe else False,black,cream)
    # strand along u (horizontal) occupies when over
    shadeU=0.6+0.5*np.sin(np.pi*fv)**0.7*(0.75+0.25*np.sin(np.pi*fu)); shadeV=0.6+0.5*np.sin(np.pi*fu)**0.7*(0.75+0.25*np.sin(np.pi*fv))
    tex=noise(H,W,5,2,seed+3)
    fib=0.92+0.12*np.sin(v*1.7+tex*6)*0+0.1*tex
    col=np.where(over[...,None],colU*shadeU[...,None],colV*shadeV[...,None])*fib[...,None]
    gap=np.minimum(np.minimum(fu,1-fu),np.minimum(fv,1-fv)); gapd=np.clip(gap/0.06,0,1)
    col=col*(0.35+0.65*gapd[...,None])
    m=np.zeros((H,W)); m[int(y0):int(y1),int(x0):int(x1)]=1; m=cv2.GaussianBlur(m,(0,0),2)
    return img*(1-m[...,None])+col*m[...,None]

# 05 Zenu woven braid
def s05():
    img=np.zeros((H,W,3))
    img=weave(img,(0,0,W,H),cell=62,seed=5,angle=45)
    # depth of field: blur top & bottom
    b=cv2.GaussianBlur(img,(0,0),6); yy=np.mgrid[0:H,0:W][0]; f=np.clip(np.abs(yy-760)/520,0,1)[...,None]**1.5
    img=img*(1-f)+b*f
    img=light_dir(img,s=0.25)
    img=pair(img,5,(360,760),(700,700),370,8,-6,shadow=(14,22),sh_blur=9,sh_dark=0.6)
    finish(img,'05_zenu_plant.jpg')

# 06 Zenu half woven + leaves + fibers
def s06():
    img=bokeh_bg((50,85,110),(110,155,185),16)
    img=weave(img,(0,760,W,H),cell=50,seed=8,angle=0)
    # loose strands emerging upward from weave
    r=np.random.default_rng(3)
    for i in range(10):
        x=40+i*105+r.uniform(-10,10)
        amp=r.uniform(-60,60); ph=r.uniform(0,3)
        pts=np.array([[x+amp*t**1.5+12*np.sin(t*3+ph), 780-t*(600+r.uniform(0,0)) ] for t in np.linspace(0,1,60)],np.int32)
        c=(175,215,232) if i%3 else (40,36,34)
        cv2.polylines(img,[pts+[4,6]],False,(img.mean()*0.4,)*3,24,cv2.LINE_AA)
        cv2.polylines(img,[pts],False,c,22,cv2.LINE_AA)
        cv2.polylines(img,[pts-[5,0]],False,tuple(min(255,v*1.2) for v in c),5,cv2.LINE_AA)
    img=draw_leaf(img,(1150,120),(450,-60),70,(85,175,125),shape='strap',bend=0.05,seed=71)
    img=fibers(img,18,(160,200,222),9,width=(2,4),area=(0,40,W,300),dir_ang=0.1,curl=25)
    img=light_dir(img,s=0.22)
    img=pair(img,6,(380,980),(720,930),330,6,-4,shadow=(14,22),sh_blur=9,sh_dark=0.6)
    finish(img,'06_zenu_plant.jpg')

for f in sys.argv[2:] if len(sys.argv)>2 else ['s01','s02','s03','s04','s05','s06']:
    globals()[f](); print('done',f)
