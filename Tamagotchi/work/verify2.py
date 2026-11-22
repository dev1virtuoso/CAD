import FreeCAD, Part
D='work/out/'
A=Part.Shape(); A.read(D+'assembly.step')
for name,y in [('sec_buttons',-20.421),('sec_screen',0.0),('sec_usb',25.30)]:
    box=Part.makeBox(300,300,300,FreeCAD.Vector(-150,y-300,-150))
    s=A.cut(box)
    s.exportStl(D+name+'.stl')
    print(name,"vol",round(s.Volume,1),"bbox",[round(v,1) for v in (s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin,s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax)])
