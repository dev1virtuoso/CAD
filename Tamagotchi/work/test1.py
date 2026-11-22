import FreeCAD, Part, json, math, time
p=json.load(open('work/profile.json'))
def wire(points):
    bs=Part.BSplineCurve()
    bs.interpolate(Points=[FreeCAD.Vector(x,y,0) for x,y in points], PeriodicFlag=True, Tolerance=1e-6)
    e=Part.Edge(bs)
    w=Part.Wire([e])
    return w
t=time.time()
w=wire(p['off6.0'])
print("wire closed",w.isClosed(),"valid",w.isValid(),"len",round(w.Length,3))
f=Part.Face(w)
print("face area",round(f.Area,2), "t",round(time.time()-t,2))
sol=f.extrude(FreeCAD.Vector(0,0,20.2))
sol.translate(FreeCAD.Vector(0,0,-10.0))
print("solid vol",round(sol.Volume,1),"valid",sol.isValid(),"faces",len(sol.Faces))
t=time.time()
# find top edge (z=10.2)
top=[e for e in sol.Edges if abs(e.BoundBox.ZMin-10.2)<1e-6 and abs(e.BoundBox.ZMax-10.2)<1e-6]
bot=[e for e in sol.Edges if abs(e.BoundBox.ZMin+10.0)<1e-6 and abs(e.BoundBox.ZMax+10.0)<1e-6]
print("top edges",len(top),"bot",len(bot))
try:
    fil=sol.makeFillet(5.0, top)
    print("fillet top ok", fil.isValid(), "vol", round(fil.Volume,1), "t",round(time.time()-t,2))
except Exception as ex:
    print("fillet fail", ex)
