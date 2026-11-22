import FreeCAD, Part, math
F=Part.Shape(); F.read('work/out/front_cover.step')
B=Part.Shape(); B.read('work/out/back_cover.step')
def probe(shape,x,y,z,r=0.12):
    b=Part.makeBox(2*r,2*r,2*r,FreeCAD.Vector(x-r,y-r,z-r))
    return round(shape.common(b).Volume,4)
print("--- snap hook (right) ---")
print(" barb pos  front(void 0):", probe(F,37.92,0,4.95), " back(solid):", probe(B,37.92,0,4.95))
print(" notch floor front(solid):", probe(F,37.92,0,4.30))
print(" arm cavity front(void 0):", probe(F,37.6,0,2.0), " back arm(solid):", probe(B,37.6,0,2.0))
print(" foot in back(solid):", probe(B,37.6,0,-0.45))
print("--- seam groove ---")
for z in (-0.5,0.0,0.5):
    print(f"  z={z}: front x@{40.6:.1f}", probe(F,40.6,0,z), end="  ")
    print("outer edge solid" if probe(F,40.9,0,z)>0.001 else "inset")
print("--- buttons / led web ---")
sw2=(-8.113,-20.421); led=(-0.493,-19.405)
print(" sw2 bore centre z10.8 (void 0):", probe(F,sw2[0],sw2[1],10.8))
dx,dy=led[0]-sw2[0],led[1]-sw2[1]; d=math.hypot(dx,dy); ux,uy=dx/d,dy/d
for t in (5.4,5.6,5.8,6.0,6.2,6.4):
    x,y=sw2[0]+ux*t, sw2[1]+uy*t
    print(f"  web t={t:.1f}: front solid={probe(F,x,y,12.0,0.06)}")
print(" led hole (void 0):", probe(F,led[0],led[1],12.0))
print("--- usb slot ---")
print(" slot centre (void 0):", probe(F,-29.0,25.3,6.56))
print(" tie slot (void 0):", probe(F,-29.0,25.3-8.2,6.56))
print("--- snap pin ---")
hx,hy=-0.49,38.51
print(" pin at pcb hole (front solid, pin):", probe(F,hx,hy,0.8))
print(" barb top z-0.2 (solid):", probe(F,hx,hy,-0.2))
