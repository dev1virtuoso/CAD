import FreeCAD, Part
F=Part.Shape(); F.read('work/out/front_cover.step')
B=Part.Shape(); B.read('work/out/back_cover.step')
def probe(shape,x,y,z,r=0.15):
    b=Part.makeBox(2*r,2*r,2*r,FreeCAD.Vector(x-r,y-r,z-r))
    return round(shape.common(b).Volume,4)
bx,by=-22.337,-20.421
print("button bore centre z9.0 (void 0):", probe(F,bx,by,9.0))
print("button bore r5.2 z9.0 (solid):", probe(F,bx+5.2,by,9.0))
print("between buttons z9.0 (solid):", probe(F,-15.5,by,9.0))
print("LED bore (void):", probe(F,-0.493,-19.405,9.5))
print("usb slot (void):", probe(F,-29.0,25.3,4.2))
print("front bbox z:", round(F.BoundBox.ZMin,2), round(F.BoundBox.ZMax,2))
print("back bbox z:", round(B.BoundBox.ZMin,2), round(B.BoundBox.ZMax,2))
print("back wall at z-6 (solid):", probe(B,0,0,-6.0))
print("back screw hole z-3 (void):", probe(B,-0.49,38.51,-3.0))
print("back boss wall z-3 r2.4 (solid):", probe(B,-0.49+2.4,38.51,-3.0))
print("back counterbore z-6.1 r2.7 (void):", probe(B,-0.49+2.7,38.51,-6.1))
