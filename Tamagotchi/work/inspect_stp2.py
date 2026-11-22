import FreeCAD, Import, Part
doc = FreeCAD.newDocument("d")
Import.insert('PCB/KiCad_ESP32-C3-SuperMini/ESP32-C3-SuperMini.stp', "d")
for o in doc.Objects:
    try:
        sh = o.Shape
    except Exception:
        continue
    bb = sh.BoundBox
    print(o.Name, o.TypeId, "bbox", [round(v,2) for v in (bb.XMin,bb.YMin,bb.ZMin,bb.XMax,bb.YMax,bb.ZMax)], "vol", round(sh.Volume,1))
    print("   placement", o.Placement)
