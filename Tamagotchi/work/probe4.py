import FreeCAD, Part, math
F=Part.Shape(); F.read('work/out/front_cover.step')
def probe(shape,x,y,z,r=0.1):
    b=Part.makeBox(2*r,2*r,2*r,FreeCAD.Vector(x-r,y-r,z-r))
    return round(shape.common(b).Volume,4)
sw2=(-8.113,-20.421); led=(-0.493,-19.405)
dx,dy=led[0]-sw2[0], led[1]-sw2[1]; d=math.hypot(dx,dy); ux,uy=dx/d,dy/d
print("centre distance", round(d,3))
for t in [5.0,5.2,5.3,5.35,5.4,5.5,5.6,5.8]:
    x,y=sw2[0]+ux*t, sw2[1]+uy*t
    print(f"  t={t:.2f} from SW2  z=10.10 solid={probe(F,x,y,10.10,0.05):.4f}  z=9.90 solid={probe(F,x,y,9.90,0.05):.4f}")
# also check web between SW1 and SW2 at face
sw1=(-22.337,-20.421)
dx,dy=sw2[0]-sw1[0], sw2[1]-sw1[1]; d2=math.hypot(dx,dy); ux2,uy2=dx/d2,dy/d2
print("sw1-sw2 distance", round(d2,3))
for t in [4.8,5.0,5.2,5.4,5.6,5.8,6.0,6.2]:
    x,y=sw1[0]+ux2*t, sw1[1]+uy2*t
    print(f"  t={t:.2f} from SW1  z=10.10 solid={probe(F,x,y,10.10,0.05):.4f}")
