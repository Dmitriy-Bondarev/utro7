#!/usr/bin/env python3
import struct, zlib, pathlib, math
root=pathlib.Path(__file__).parent
def inside(x,y,poly):
    c=False
    j=len(poly)-1
    for i in range(len(poly)):
        a,b=poly[i],poly[j]
        if ((a[1]>y)!=(b[1]>y)) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
            c=not c
        j=i
    return c
def pngchunk(name,data):
    return struct.pack('>I',len(data))+name+data+struct.pack('>I',zlib.crc32(name+data)&0xffffffff)
def make(name,n):
    poly=[(.24,.27),(.78,.27),(.78,.37),(.54,.79),(.38,.79),(.61,.39),(.24,.39)]
    rows=[]
    for y in range(n):
        row=bytearray([0])
        for x in range(n):
            t=y/max(1,n-1)
            v=math.hypot((x-n*.15)/n,(y-n*.06)/n)
            r=int(max(0,min(255,20-7*t+max(0,1-v)*5)))
            g=int(max(0,min(255,198-85*t+max(0,1-v)*16)))
            b=int(max(0,min(255,245-16*t)))
            hit=sum(inside((x+sx)/n,(y+sy)/n,poly) for sy in (.25,.75) for sx in (.25,.75))/4
            if hit:
                r=int(r*(1-hit)+242*hit);g=int(g*(1-hit)+250*hit);b=int(b*(1-hit)+255*hit)
            row.extend((r,g,b,255))
        rows.append(bytes(row))
    ihdr=struct.pack('>2I5B',n,n,8,6,0,0,0)
    out=b'\x89PNG\r\n\x1a\n'+pngchunk(b'IHDR',ihdr)+pngchunk(b'IDAT',zlib.compress(b''.join(rows),8))+pngchunk(b'IEND',b'')
    (root/name).write_bytes(out)
    print(name,len(out))
make('icon-192.png',192)
make('icon-512.png',512)
make('apple-touch-icon.png',180)
