import FreeCAD, Part, Mesh, MeshPart, sys
src, dst = sys.argv[-2], sys.argv[-1]
s = Part.Shape()
s.read(src)
print("shape valid", s.isValid(), "bbox", s.BoundBox)
m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.3, Relative=False)
print("tris", m.CountFacets)
m.write(dst)
