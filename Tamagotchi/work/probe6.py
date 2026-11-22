import FreeCAD, Part
F=Part.Shape(); F.read('work/out/front_cover.step')
B=Part.Shape(); B.read('work/out/back_cover.step')
def probe(shape,x,y,z,r=0.12):
    b=Part.makeBox(2*r,2*r,2*r,FreeCAD.Vector(x-r,y-r,z-r))
    return round(shape.common(b).Volume,4)
base=36.07
print("arm  x=%.2f z=2.0 : front(0)=%s back(1)=%s" % (base+0.6, probe(F,base+0.6,0,2.0), probe(B,base+0.6,0,2.0)))
print("barb x=%.2f z=4.60: front(0)=%s back(1)=%s" % (base+1.5, probe(F,base+1.5,0,4.60), probe(B,base+1.5,0,4.60)))
print("barb x=%.2f z=4.90: front(0)=%s back(1)=%s" % (base+1.4, probe(F,base+1.4,0,4.90), probe(B,base+1.4,0,4.90)))
print("wall x=%.2f z=2.0 : front(1)=%s" % (base+2.0, probe(F,base+2.0,0,2.0)))
print("notch x=%.2f z=4.60: front(0)=%s" % (base+1.5, probe(F,base+1.5,0,4.60)))
pin=(-0.49,38.51)
print("pin half x=%+.2f z=-0.2: front(1)=%s" % (pin[0]+0.6, probe(F,pin[0]+0.6,pin[1],-0.2)))
print("pin half x=%+.2f z=1.3: front(1)=%s" % (pin[0]+0.6, probe(F,pin[0]+0.6,pin[1],1.3)))
