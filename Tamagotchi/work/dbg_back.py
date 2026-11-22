import FreeCAD, Part, json, math, os
P=json.load(open('work/profile.json'))
OUT_OFF=6.0
def spline_face(points,z=0.0):
    bs=Part.BSplineCurve(); bs.interpolate(Points=[FreeCAD.Vector(x,y,z) for x,y in points],PeriodicFlag=True,Tolerance=1e-6)
    return Part.Face(Part.Wire([Part.Edge(bs)]))
def cyl(r,z0,z1,x,y): return Part.makeCylinder(r,z1-z0,FreeCAD.Vector(x,y,z0),FreeCAD.Vector(0,0,1))
back=spline_face(P['off6.0']).extrude(FreeCAD.Vector(0,0,10.0)); back.translate(FreeCAD.Vector(0,0,-10.0))
bot=[e for e in back.Edges if abs(e.BoundBox.ZMin+10)<1e-6 and abs(e.BoundBox.ZMax+10)<1e-6]
back=back.makeFillet(5.0,bot); print("fillet",back.isValid(),round(back.Volume,1))
cav=spline_face(P['off2.8']).extrude(FreeCAD.Vector(0,0,8.0)); cav.translate(FreeCAD.Vector(0,0,-8.0))
back=back.cut(cav); print("cav",back.isValid(),round(back.Volume,1),"null",back.isNull())
holes=[(-0.49,38.51),(-28.43,7.52),(29.99,-10.26)]
for i,(hx,hy) in enumerate(holes):
    b=cyl(3.2,-8.2,0.1,hx,hy)
    back=back.fuse(b)
    print(" fuse boss",i,back.isValid(),round(back.Volume,1),"null",back.isNull())
back=back.removeSplitter(); print("split",back.isValid(),round(back.Volume,1),"null",back.isNull(),"solids",len(back.Solids))
for i,(hx,hy) in enumerate(holes):
    for t,name in [(cyl(1.7,-9.5,-10.0-1,hx,hy),'hole'),(cyl(3.0,-10.1,-9.0,hx,hy),'cb')]:
        r=back.cut(t)
        print("  cut",name,i,"ok",r.isValid(),round(r.Volume,1),"null",r.isNull(),"solids",len(r.Solids))
        if r.isNull(): break
        back=r
print("final",round(back.Volume,1),"valid",back.isValid())
