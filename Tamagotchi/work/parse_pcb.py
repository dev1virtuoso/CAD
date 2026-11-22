import re, math, json, sys

def tokenize(s):
    toks=[]; i=0; n=len(s)
    while i<n:
        c=s[i]
        if c in '()':
            toks.append(c); i+=1
        elif c=='"':
            j=i+1; buf=''
            while j<n:
                if s[j]=='\\': buf+=s[j+1]; j+=2
                elif s[j]=='"': break
                else: buf+=s[j]; j+=1
            toks.append(('str',buf)); i=j+1
        elif c.isspace(): i+=1
        else:
            j=i
            while j<n and (not s[j].isspace()) and s[j] not in '()"': j+=1
            toks.append(('atom',s[i:j])); i=j
    return toks

def parse(toks):
    stack=[[]]
    for t in toks:
        if t=='(':
            new=[]; stack[-1].append(new); stack.append(new)
        elif t==')':
            stack.pop()
        else:
            stack[-1].append(t[1])
    return stack[0]

def find_all(node, key):
    out=[]
    for c in node:
        if isinstance(c,list) and c and c[0]==key: out.append(c)
    return out

def get(node, key):
    for c in node:
        if isinstance(c,list) and c and c[0]==key: return c
    return None

def num(x): return float(x)

def collect_edges(node, acc):
    for c in node:
        if not isinstance(c,list) or not c: continue
        k=c[0]
        if k in ('gr_line','gr_arc','gr_circle','gr_rect','gr_poly','gr_curve','gr_bbox'):
            layer = get(c,'layer')
            if layer and layer[1]=='Edge.Cuts':
                acc.append(c)
        # don't recurse into footprint pads etc for edge

def main():
    s=open('PCB/Tamagotchi.kicad_pcb',encoding='utf-8').read()
    root=parse(tokenize(s))[0]
    print("root", root[0])
    # board thickness
    gen=get(root,'general'); print("thickness", get(gen,'thickness'))
    edges=[]
    for c in root:
        if isinstance(c,list) and c and isinstance(c[0],str) and c[0].startswith('gr_'):
            layer=get(c,'layer')
            if layer and layer[1]=='Edge.Cuts': edges.append(c)
    print("EDGE ITEMS:", len(edges))
    for e in edges:
        kind=e[0]; a=get(e,'start'); b=get(e,'end'); mid=get(e,'mid'); c_=get(e,'center')
        w=get(e,'width')
        extra=''
        if kind=='gr_arc':
            extra=f" mid={mid[1:3]}"
        if kind=='gr_circle':
            extra=f" center={c_[1:3]} end={b[1:3]}"
        print(f"  {kind} start={a[1:3] if a else None} end={b[1:3] if b else None}{extra} w={w[1] if w else None}")
    # footprints
    fps=[]
    for c in root:
        if isinstance(c,list) and c and c[0]=='footprint':
            name=c[1]
            at=get(c,'at'); layer=get(c,'layer')
            ref=val=None
            for p in find_all(c,'property'):
                if p[1]=='Reference': ref=p[2]
                if p[1]=='Value': val=p[2]
            pads=[]
            for p in find_all(c,'pad'):
                pat=get(p,'at'); drill=get(p,'drill')
                size=get(p,'size'); ptype=p[2]; pshape=p[3]
                d=None
                if drill:
                    vals=[x for x in drill[1:] if not isinstance(x,list)]
                    d=vals
                pads.append({'num':p[1],'type':ptype,'shape':pshape,'at':[float(x) for x in pat[1:3]],'drill':d,'size':[float(x) for x in size[1:3]] if size else None})
            fps.append({'ref':ref,'val':val,'fp':name,'at':[float(x) for x in at[1:3]],'rot':float(at[3]) if len(at)>3 else 0.0,'layer':layer[1] if layer else None,'pads':pads})
    print("\nFOOTPRINTS:", len(fps))
    for f in sorted(fps,key=lambda x:str(x['ref'])):
        drilled=[p for p in f['pads'] if p['drill'] and any(float(v)>0 for v in p['drill'] if isinstance(p['drill'][0],str)==False)]
        npth=[p for p in f['pads'] if p['type']=='np_thru_hole']
        print(f"  {f['ref']:6s} {str(f['val'])[:28]:28s} {f['fp'].split(':')[-1][:32]:32s} at=({f['at'][0]:.3f},{f['at'][1]:.3f}) rot={f['rot']:.1f} layer={f['layer']} pads={len(f['pads'])} npth={len(npth)}")
        for p in npth: print(f"       NPTH pad {p['num']} drill={p['drill']} size={p['size']} at={p['at']}")
    json.dump({'fps':fps,'edges':[[e[0]]+[x for x in e[1:]] for e in edges]}, open('work/pcb.json','w'), default=str)
main()
