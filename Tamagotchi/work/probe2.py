import FreeCAD, Part
F=Part.Shape(); F.read('work/out/front_cover.step')
def probe(shape,x,y,z,r=0.15):
    b=Part.makeBox(2*r,2*r,2*r,FreeCAD.Vector(x-r,y-r,z-r))
    return round(shape.common(b).Volume,4)
bx,by=-22.337,-20.421
print("button bore z9.0 (void 0):", probe(F,bx,by,9.0))
print("button bore z8.5 (void 0):", probe(F,bx,by,8.5))
print("recess floor z9.5 r2.8 (void 0):", probe(F,bx+2.8,by,9.5))
print("recess wall z9.5 r3.3 (solid):", probe(F,bx+3.3,by,9.5))
print("front face z10.0 r3.3 (solid):", probe(F,bx+3.3,by,10.0))
print("between buttons z9.0 mid (solid):", probe(F,-15.5,-20.421,9.0))
