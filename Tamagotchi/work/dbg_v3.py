import FreeCAD, Part
F=Part.Shape(); F.read('work/out/front_cover.step')
P=Part.Shape(); P.read('work/out/pcb.step')
B=Part.Shape(); B.read('work/out/back_cover.step')
inter=P.common(F)
print("inter volume", round(inter.Volume,3), "solids", len(inter.Solids), "shells", len(inter.Shells))
for s in inter.Solids:
    bb=s.BoundBox
    print("  solid vol", round(s.Volume,3), "bbox", [round(v,2) for v in (bb.XMin,bb.YMin,bb.ZMin,bb.XMax,bb.YMax,bb.ZMax)])
ib=B.common(F)
print("front/back inter", round(ib.Volume,3), "solids", len(ib.Solids))
for s in ib.Solids:
    bb=s.BoundBox
    print("  solid vol", round(s.Volume,3), "bbox", [round(v,2) for v in (bb.XMin,bb.YMin,bb.ZMin,bb.XMax,bb.YMax,bb.ZMax)])
