import FreeCAD, Part, json, os
D='work/out/'
def load(n):
    s=Part.Shape(); s.read(D+n+'.step'); return s
F=load('front_cover'); B=load('back_cover'); A=load('assembly')
print("front",round(F.Volume,1),"back",round(B.Volume,1),"assembly",round(A.Volume,1))
print("front∩back", round(F.common(B).Volume,4))
print("front valid",F.isValid(),"back valid",B.isValid())
# section through buttons (Y=-20.421) and through screen (Y=0)
for name,y in [('sec_buttons',-20.421),('sec_screen',0.0),('sec_usb',25.30)]:
    box=Part.makeBox(200,200,200,FreeCAD.Vector(-100,y,-100))   # keeps y>=y0
    s=A.cut(box)
    s.exportStl(D+name+'.stl')
    print(name,"vol",round(s.Volume,1))
