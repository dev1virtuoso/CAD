import FreeCAD, Part
s=Part.Shape(); s.read('work/out/front_cover.step')
def probe(x,y,z,r=0.2):
    b=Part.makeBox(2*r,2*r,2*r,FreeCAD.Vector(x-r,y-r,z-r))
    return round(s.common(b).Volume,4)
for name,(x,y) in {'btn4':(23.383,-20.421),'btn1':(-22.337,-20.421)}.items():
    print(name,"centre z9.7:",probe(x,y,9.7)," z9.7 r2.5:",probe(x+2.5,y,9.7)," z9.7 r4:",probe(x+4,y,9.7),
          " z10.1 r2.5:",probe(x+2.5,y,10.1)," z9.0 r2.5:",probe(x+2.5,y,9.0))
# front face plane check: does the front face have holes at r<3 ?
sec = s.section(Part.makePlane(200,200,FreeCAD.Vector(0,0,9.7)))
print("slice wires at 9.7:", len(sec.Wires), "edges", len(sec.Edges))
