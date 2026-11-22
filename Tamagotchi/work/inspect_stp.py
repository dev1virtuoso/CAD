import FreeCAD, Part
s = Part.Shape(); s.read('PCB/KiCad_ESP32-C3-SuperMini/ESP32-C3-SuperMini.stp')
print("solids", len(s.Solids), "shells", len(s.Shells), "faces", len(s.Faces))
for i,sol in enumerate(s.Solids):
    bb=sol.BoundBox
    print(i, "vol", round(sol.Volume,1), "bbox", [round(v,2) for v in (bb.XMin,bb.YMin,bb.ZMin,bb.XMax,bb.YMax,bb.ZMax)])
print("placement", s.Placement)
