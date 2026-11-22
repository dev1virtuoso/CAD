import FreeCAD, Part
D='work/out/'
parts={}
for n in ['front_cover','back_cover','pcb','comps']:
    s=Part.Shape(); s.read(D+n+'.step'); parts[n]=s
for name,y0 in [('secA',0.0),('secB',-20.421)]:
    box=Part.makeBox(300,300,300,FreeCAD.Vector(-150,y0-300,-150))  # keep y>=y0
    for n,s in parts.items():
        c=s.cut(box)
        if c.Volume>0.01:
            c.exportStl(f'{D}{name}_{n}.stl')
            print(name,n,round(c.Volume,1))
