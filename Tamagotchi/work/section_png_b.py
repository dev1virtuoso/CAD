import json
from PIL import Image, ImageDraw, ImageFont
S=json.load(open('work/section_ybtn.json'))
SC=11.0; W,H=1280,700; X0,Y0=640,330
FONT='/System/Library/Fonts/Hiragino Sans GB.ttc'
f=ImageFont.truetype(FONT,16,index=0); fs=ImageFont.truetype(FONT,13,index=0); fb=ImageFont.truetype(FONT,21,index=0)
COL={'front_cover':(35,85,155),'back_cover':(35,85,155),'pcb':(25,125,75),'comps':(55,55,65)}
def T(x,z): return (X0+x*SC, Y0-z*SC)
img=Image.new('RGB',(W,H),(255,255,255)); d=ImageDraw.Draw(img)
d.polygon([T(-41.03,12.3),T(41.03,12.3),T(41.03,-7.0),T(-41.03,-7.0)],fill=(231,237,246))
d.polygon([T(-37.85,10.3),T(37.85,10.3),T(37.85,-5.0),T(-37.85,-5.0)],fill=(252,252,255))
for n,polys in S.items():
    for p in polys:
        if len(p)>=2: d.line([T(x,z) for x,z in p],fill=COL[n],width=2)
d.line([T(-46,0),T(46,0)],fill=(215,215,222),width=1)
bx=-22.337
# dimension of bore
d.line([(T(bx-4.8,0)[0],T(0,12.7)[1]),(T(bx+4.8,0)[0],T(0,12.7)[1])],fill=(196,90,40),width=1)
d.text((T(bx,0)[0]-86,T(0,12.7)[1]-16),'直通孔 9.6',font=fs,fill=(196,90,40))
d.text((T(bx,0)[0]-86,T(0,12.7)[1]-32),'導引口 10.4',font=fs,fill=(196,90,40))
# finger arrow
ax=T(bx,12.3)[0]
d.line([(ax,128),(ax,T(0,2.6)[1]-8)],fill=(200,60,60),width=3)
d.polygon([(ax-7,T(0,2.6)[1]-4),(ax+7,T(0,2.6)[1]-4),(ax,T(0,2.6)[1]-16)],fill=(200,60,60))
d.text((ax+14,128),'手指直接按開關',font=f,fill=(200,60,60))
# labels
def mark(n,x,z):
    px,py=T(x,z); d.ellipse([px-9,py-9,px+9,py+9],fill=(255,255,255),outline=(196,90,40),width=2)
    tw=d.textlength(str(n),font=fs); d.text((px-tw/2,py-7),str(n),font=fs,fill=(196,90,40))
mark(1,bx-7,9.3); mark(2,bx+11,1.0); mark(3,bx+3.2,-2.6); mark(4,bx+11,5.6)
mark(5,bx+3.2,2.0)
d.text((24,18),'B-B 剖面（穿過按鍵排 Y=-20.4）｜單位 mm',font=fb,fill=(25,30,40))
notes=[(1,'前壁 2.0 mm：直通孔 φ9.6、導引口 φ10.4'),
       (2,'PCB 1.6 mm'),
       (3,'背殼支撐墊 φ5.2 頂住 PCB，按鍵時板子不會彎'),
       (4,'前腔 8.7 mm（開關上方全空，無任何零件）'),
       (5,'TL3342 開關直接外露（4.5×5.2×0.55）')]
for i,(n,txt) in enumerate(notes):
    x=24+(i%2)*600; y=520+(i//2)*30
    d.text((x,y),f'{n}',font=fs,fill=(196,90,40)); d.text((x+16,y),txt,font=fs,fill=(45,45,55))
d.text((24,640),'■ 前/後殼   ■ PCB   ■ 元件',font=f,fill=(60,60,70))
d.text((24,668),'按鍵孔 φ9.6 對正開關中心；指尖穿過 2 mm 前壁即進入空腔、直接壓到開關',font=fs,fill=(95,95,105))
img.save('work/section_BB.png'); print('ok')
