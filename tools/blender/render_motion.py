#!/usr/bin/env python3
"""Utro 7 original 3D motion prototype.
Run inside Blender: blender -b -t 4 -P tools/blender/render_motion.py -- --avatar woman --exercise march
No external models, animations, materials or assets are used.
Output Blender scene (.blend), PNG frames, silent H.264 MP4 and JPEG poster.
"""
import argparse
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
parser = argparse.ArgumentParser()
parser.add_argument("--avatar", choices=("woman", "man"), default="woman")
parser.add_argument("--exercise", choices=("march", "squat", "pushup"), default="march")
parser.add_argument("--frames", type=int, default=32)
parser.add_argument("--size", type=int, default=560)
parser.add_argument("--output", default="")
args = parser.parse_args(argv)
ROOT = Path(__file__).resolve().parents[2]
DEST = Path(args.output) if args.output else ROOT / "assets" / "motion" / "v1"
FRAME_DIR = DEST / "_frames" / (args.avatar + "-" + args.exercise)
DEST.mkdir(parents=True, exist_ok=True)
FRAME_DIR.mkdir(parents=True, exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials):
    bpy.data.materials.remove(m)

def mat(name, rgb, roughness=0.86):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    shader = m.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Roughness"].default_value = roughness
    return m

WOMAN = args.avatar == "woman"
skin = mat("skin warm", (.85, .52, .35) if WOMAN else (.72, .42, .28))
shirt = mat("training top", (.035, .74, .68) if WOMAN else (.08, .38, .84))
shorts = mat("training shorts", (.97, .29, .09) if WOMAN else (.08, .14, .36))
shoes = mat("light trainers", (.93, .96, .95))
hairmat = mat("hair", (.28, .11, .055) if WOMAN else (.115, .085, .065))
eyes = mat("eyes", (.055, .1, .14))
stage_mat = mat("studio floor", (.91, .935, .952))
nosemat = mat("nose", (.82, .48, .32))

def sphere(name, material, segments=24, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    for poly in o.data.polygons:
        poly.use_smooth = True
    return o

def segment(name, material):
    return sphere(name, material, 20, 12)

parts = {}
parts["torso"] = segment("torso • fitted athletic top", shirt)
parts["pelvis"] = sphere("hip center • sportswear", shorts)
parts["neck"] = segment("neck", skin)
parts["head"] = sphere("head", skin)
parts["hair"] = sphere("hair cap", hairmat)
parts["nose"] = sphere("nose", nosemat, 16, 10)
parts["eye_l"] = sphere("eye left", eyes, 12, 8)
parts["eye_r"] = sphere("eye right", eyes, 12, 8)
for side in ("l", "r"):
    parts[side + "_upper_arm"] = segment(side + " upper arm", skin)
    parts[side + "_forearm"] = segment(side + " forearm", skin)
    parts[side + "_hand"] = sphere(side + " hand", skin, 16, 10)
    parts[side + "_thigh"] = segment(side + " thigh", shorts)
    parts[side + "_shin"] = segment(side + " shin", skin)
    parts[side + "_knee"] = sphere(side + " knee", skin, 16, 10)
    parts[side + "_shoe"] = sphere(side + " running shoe", shoes, 20, 12)
if WOMAN:
    parts["ponytail"] = segment("ponytail hair", hairmat)
else:
    parts["sideburn_l"] = sphere("left short hair", hairmat, 16, 10)
    parts["sideburn_r"] = sphere("right short hair", hairmat, 16, 10)

def vec(p):
    return Vector(p)

def place_ball(o, p, scale, frame):
    o.location = vec(p)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = (1,0,0,0)
    o.scale = scale
    o.keyframe_insert(data_path="location", frame=frame)
    o.keyframe_insert(data_path="scale", frame=frame)

def place_link(o, a, b, width, frame):
    p, q = vec(a), vec(b)
    v = q - p
    if v.length < .0001:
        v.z = .001
    o.location = (p + q) / 2
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(v)
    o.scale = (width, width, v.length / 2 + width * .45)
    o.keyframe_insert(data_path="location", frame=frame)
    o.keyframe_insert(data_path="rotation_quaternion", frame=frame)
    o.keyframe_insert(data_path="scale", frame=frame)

def positions(frame):
    angle = 2 * math.pi * (frame - 1) / args.frames
    depth = (1 - math.cos(angle)) / 2
    lift = (max(0, math.sin(angle)), max(0, -math.sin(angle)))
    p = {}
    if args.exercise in ("march", "squat"):
        hipz = 1.01 - (.41 * depth if args.exercise == "squat" else 0) + (.012 * math.sin(2 * angle) if args.exercise == "march" else 0)
        lean = -.10 * depth if args.exercise == "squat" else 0
        p["pelvis"] = (0, 0, hipz)
        p["shoulder"] = (0, lean, hipz + .44)
        p["neck"] = (0, lean - .01, hipz + .57)
        p["head"] = (0, lean - .015, hipz + .74)
        for i, side in enumerate(("l","r")):
            sign = -1 if side == "l" else 1
            xh = sign * (.145 if WOMAN else .115)
            xs = sign * (.265 if WOMAN else .32)
            if args.exercise == "squat":
                p[side + "_hip"] = (xh, 0, hipz - .01)
                p[side + "_knee"] = (xh*1.05, -.29*depth, .58 - .12*depth)
                p[side + "_ankle"] = (xh, -.05, .105)
                p[side + "_foot"] = (xh, -.16, .085)
                p[side + "_shoulder"] = (xs, lean, hipz+.42)
                p[side + "_elbow"] = (xs*.9, lean - .27 - .12*depth, hipz+.20)
                p[side + "_wrist"] = (xs*.9, lean - .48, hipz+.25)
            else:
                k = lift[i]
                p[side + "_hip"] = (xh, 0, hipz)
                p[side + "_knee"] = (xh, -.24*k, .58+.22*k)
                p[side + "_ankle"] = (xh, -.32*k, .12+.32*k)
                p[side + "_foot"] = (xh, -.15-.32*k, .085+.32*k)
                p[side + "_shoulder"] = (xs, 0, hipz+.43)
                p[side + "_elbow"] = (xs*1.25, -.17*(1-k), hipz+.23+.13*(1-k))
                p[side + "_wrist"] = (xs*1.1, -.28*(1-k), hipz+.08+.20*(1-k))
        face = "front"
    else:
        # Horizontal side-view whole-body push-up. Pelvis follows the shoulder
        # slightly to keep a continuous head-to-heel line through the motion.
        shz = .73 - .34*depth
        hipz = .53 - .23*depth
        p["pelvis"] = (.39, 0, hipz)
        p["shoulder"] = (-.54, 0, shz)
        p["neck"] = (-.70, 0, shz+.06)
        p["head"] = (-.89, -.005, shz+.10)
        for side in ("l","r"):
            sign = -1 if side == "l" else 1
            yy = sign*.18
            p[side + "_hip"] = (.46, yy*.55, hipz-.06)
            p[side + "_knee"] = (.95, yy*.5, .26 - .07*depth)
            p[side + "_ankle"] = (1.40, yy*.5, .115)
            p[side + "_foot"] = (1.48, yy*.5, .08)
            p[side + "_shoulder"] = (-.55, yy, shz)
            p[side + "_elbow"] = (-.62-.16*depth, yy*1.42, .31-.11*depth)
            p[side + "_wrist"] = (-.75, yy*1.45, .115)
        face = "side"
    return p, face

def rig_frame(frame):
    P, facing = positions(frame)
    torso_radius = .206 if WOMAN else .231
    place_link(parts["torso"],P["pelvis"],P["shoulder"],torso_radius,frame)
    place_ball(parts["pelvis"],P["pelvis"],(.216 if WOMAN else .18,.165,.140),frame)
    place_link(parts["neck"],P["shoulder"],P["neck"],.068,frame)
    place_ball(parts["head"],P["head"],(.142,.126,.178) if WOMAN else (.147,.133,.17),frame)
    h=vec(P["head"])
    facevector = Vector((-.14,0,-.016)) if facing=="side" else Vector((0,-.13,-.02))
    place_ball(parts["nose"],h+facevector,(.035,.042,.031),frame)
    if facing=="side":
        # Both eyes visible in oblique view, on either side of the nose.
        eyes_pos=(h+Vector((-.105,-.067,.035)),h+Vector((-.101,.070,.035)))
        hair_pos=h+Vector((.02,.012,.112))
    else:
        eyes_pos=(h+Vector((-.054,-.113,.027)),h+Vector((.054,-.113,.027)))
        hair_pos=h+Vector((0,.007,.128))
    place_ball(parts["eye_l"],eyes_pos[0],(.013,.012,.013),frame)
    place_ball(parts["eye_r"],eyes_pos[1],(.013,.012,.013),frame)
    place_ball(parts["hair"],hair_pos,(.145,.132,.084),frame)
    if WOMAN:
        # Ponytail follows the head; only the appearance changes across avatars.
        place_link(parts["ponytail"],hair_pos+Vector((.055,.085,.01)),hair_pos+Vector((.13,.115,-.19)),.071,frame)
    else:
        for side in ("l","r"):
            sign=-1 if side=="l" else 1
            place_ball(parts["sideburn_"+side],hair_pos+Vector((sign*.116,0,-.07)),(.035,.056,.071),frame)
    for side in ("l","r"):
        place_link(parts[side+"_upper_arm"],P[side+"_shoulder"],P[side+"_elbow"],.085 if WOMAN else .105,frame)
        place_link(parts[side+"_forearm"],P[side+"_elbow"],P[side+"_wrist"],.073 if WOMAN else .091,frame)
        place_ball(parts[side+"_hand"],P[side+"_wrist"],(.066,.060,.080),frame)
        place_link(parts[side+"_thigh"],P[side+"_hip"],P[side+"_knee"],.115 if WOMAN else .135,frame)
        place_link(parts[side+"_shin"],P[side+"_knee"],P[side+"_ankle"],.09 if WOMAN else .10,frame)
        place_ball(parts[side+"_knee"],P[side+"_knee"],(.082,.082,.082),frame)
        place_ball(parts[side+"_shoe"],P[side+"_foot"],(.11,.175,.067),frame)

# Studio and camera.
bpy.ops.mesh.primitive_plane_add(size=20, location=(0,0,-.03))
floor=bpy.context.object
floor.name="shadow-catching studio floor"
floor.data.materials.append(stage_mat)
scene=bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x=args.size
scene.render.resolution_y=args.size
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGBA"
scene.render.film_transparent=False
scene.render.fps=20
scene.frame_start=1
scene.frame_end=args.frames
scene.render.filepath=str(FRAME_DIR/"frame_")
scene.camera=None
scene.world.color=(.9,.93,.97)
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.90,.935,.96,1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.80

def aim_at(obj,target):
    v=Vector(target)-obj.location
    obj.rotation_euler=v.to_track_quat("-Z","Y").to_euler()

bpy.ops.object.camera_add()
cam=bpy.context.object
cam.name="orthographic fitness demonstration camera"
if args.exercise=="pushup":
    cam.location=(.15,-6.0,2.0)
    aim_at(cam,(.18,0,.69))
    cam.data.ortho_scale=3.75
elif args.exercise=="squat":
    cam.location=(3.3,-6.3,2.6)
    aim_at(cam,(0,0,1.01))
    cam.data.ortho_scale=2.90
else:
    cam.location=(1.7,-6.4,2.6)
    aim_at(cam,(0,0,1.0))
    cam.data.ortho_scale=2.90
cam.data.type="ORTHO"
scene.camera=cam

def light(name,loc,power,size):
    bpy.ops.object.light_add(type="AREA",location=loc)
    l=bpy.context.object
    l.name=name
    l.data.energy=power
    l.data.shape="DISK"
    l.data.size=size
    aim_at(l,(0,0,1))

light("large soft key",(-3,-4,5),620,5)
light("front fill",(3,-3,3.7),270,4)
light("rim",(1,3,3.7),380,4.5)

scene.view_settings.view_transform="Standard"
if hasattr(scene,"eevee"):
    try:
        scene.eevee.taa_render_samples=16
    except Exception:
        pass

for frame in range(1,args.frames+1):
    rig_frame(frame)
scene.frame_set(1)
name=args.avatar+"-"+args.exercise
bpy.ops.wm.save_as_mainfile(filepath=str(DEST/(name+".blend")))
print("UTRO7_SCENE_READY",name,args.frames,args.size,flush=True)
bpy.ops.render.render(animation=True)
print("UTRO7_FRAMES_COMPLETE",name,flush=True)
