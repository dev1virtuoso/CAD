import FreeCAD, Part, json
D='work/out/'
parts={}
for n in ['front_cover','back_cover','pcb','comps']:
    s=Part.Shape(); s.read(D+n+'.step'); parts[n]=s
plane=Part.makePlane(300,300,FreeCAD.Vector(-150,-20.421,150),FreeCAD.Vector(0,1,0),FreeCAD.Vector(1,0,0))
out={}
for n,s in parts.items():
    sec=s.section(plane); polys=[]
    for e in sec.Edges:
        try: pts=e.discretize(Number=30)
        except Exception: continue
        polys.append([[round(p.x,3),round(p.z,3)] for p in pts])
    out[n]=polys
json.dump(out,open('work/section_ybtn.json','w'))
print({k:len(v) for k,v in out.items()})
