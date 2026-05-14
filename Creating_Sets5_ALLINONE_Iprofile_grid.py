# -*- coding: ascii -*-
# Abaqus/CAE Python 2.7
#
# Creating_Sets5_ALLINONE.py
#
# 1) Creates all sets (and a few specific part/asm surfaces you already rely on)
# 2) Creates assembly surfaces automatically from ALL assembly sets
# 3) Combines two selected EDGE-surfaces into one EDGE-surface + EDGE-set
#
# NOTE:
# - This script assumes instances exist:
#     S_full-1, S_half_web-1, Patches-1, Lower_Skin-1
# - JSON files are taken from the SAME case folder as STEP files:
#     <CASE_DIR>\Sfull_Shalf.json
#     <CASE_DIR>\Sfull_patches.json

from abaqus import *
from abaqusConstants import *
import os, json, codecs, math

MODEL = "Model-1"

# ============================================================
# CASE DIRECTORY
# ============================================================
if 'CASE_DIR' not in globals() or not CASE_DIR:
    raise RuntimeError(
        "CASE_DIR is not defined.\n"
        "This script must be launched by RUN_ALL_PIPELINE.py with CASE_DIR set "
        "to the Rhino Compute generated case folder."
    )

CASE_DIR = os.path.normpath(CASE_DIR)


# Optional design variables written by MASTER_GH_TO_ABAQUS3.py
DESIGN_VARS_JSON = os.path.join(CASE_DIR, "design_vars.json")

def _read_design_vars():
    if not os.path.isfile(DESIGN_VARS_JSON):
        return {}
    try:
        f = open(DESIGN_VARS_JSON, "r")
        try:
            data = json.load(f)
        finally:
            f.close()
        if isinstance(data, dict):
            return data
    except:
        pass
    return {}

DESIGN_VARS = _read_design_vars()

def _get_design_height(default_value):
    try:
        return float(DESIGN_VARS.get("Height", default_value))
    except:
        return float(default_value)

# JSON names inside the CASE folder
JSON_NAME_SFULL_SHALF   = "Sfull_Shalf.json"
JSON_NAME_SFULL_PATCHES = "Sfull_patches.json"

def _case_path():
    return CASE_DIR

JSON_SFULL_SHALF   = os.path.join(_case_path(), JSON_NAME_SFULL_SHALF)
JSON_SFULL_PATCHES = os.path.join(_case_path(), JSON_NAME_SFULL_PATCHES)

# ============================================================
# Parts
# ============================================================
PART_SFULL     = "S_full"
PART_SHALF_WEB = "S_half_web"
PART_PATCHES   = "Patches"
PART_LOWERSKIN = "Lower_Skin"

# ============================================================
# Instances
# ============================================================
INST_SFULL     = "S_full-1"
INST_SHALF_WEB = "S_half_web-1"
INST_PATCHES   = "Patches-1"
INST_LOWERSKIN = "Lower_Skin-1"

# ============================================================
# Names: sets / surfaces
# ============================================================
SET_SHALF_WEB_TOP_EDGES = "SET_SHALF_WEB_TOP_EDGES"
SET_SHALF_WEB_BOT_EDGES = "SET_SHALF_WEB_BOTTOM_EDGES"

SURF_UPPER_PATCHES_SNEG = "SURF_UPPER_PATCHES_SNEG"
SURF_LOWER_PATCHES_SPOS = "SURF_LOWER_PATCHES_SPOS"
SURF_LOWER_PATCHES_SNEG = "SURF_LOWER_PATCHES_SNEG"

SET_SFULL_WEB_END_EDGES = "SET_SFULL_WEB_END_EDGES"
SET_SHALF_WEB_END_EDGES = "SET_SHALF_WEB_END_EDGES"

# NEW: mesh-based S_half interface region
SET_SHALF_WEB_MESH_ELEMS = "SET_SHALF_WEB_MESH_ELEMS"
SURF_SHALF_WEB_MESH = "SURF_SHALF_WEB_MESH"

SET_SFULL_BOT_FLANGE_LOWER_FACES = "SET_SFULL_BOT_FLANGE_LOWER_FACES"
SURF_SFULL_BOT_FLANGE_SNEG       = "SURF_SFULL_BOT_FLANGE_SNEG"

SET_LOWERSKIN_UPPER_FACES = "SET_LOWERSKIN_UPPER_FACES"
SURF_LOWERSKIN_TOP_SPOS   = "SURF_LOWERSKIN_TOP_SPOS"

SET_LOWERSKIN_EDGE_LEFT   = "SET_LOWERSKIN_EDGE_LEFT"
SET_LOWERSKIN_EDGE_RIGHT  = "SET_LOWERSKIN_EDGE_RIGHT"
SET_LOWERSKIN_EDGE_TOP    = "SET_LOWERSKIN_EDGE_TOP"
SET_LOWERSKIN_EDGE_BOTTOM = "SET_LOWERSKIN_EDGE_BOTTOM"

SET_SFULL_BND_EDGE_LEFT   = "SET_SFULL_BOUNDARY_EDGE_LEFT"
SET_SFULL_BND_EDGE_RIGHT  = "SET_SFULL_BOUNDARY_EDGE_RIGHT"
SET_SFULL_BND_EDGE_TOP    = "SET_SFULL_BOUNDARY_EDGE_TOP"
SET_SFULL_BND_EDGE_BOTTOM = "SET_SFULL_BOUNDARY_EDGE_BOTTOM"

SET_SFULL_PATCH_IFACE_EDGES   = "SET_SFULL_PATCH_IFACE_EDGES"
SET_PATCHES_SFULL_IFACE_EDGES = "SET_PATCHES_SFULL_IFACE_EDGES"

# ============================================================
# Tuning
# ============================================================
Z_TOL_EDGES = 0.6
Z_LAYER_TOL = 0.5

DEFAULT_HEIGHT = 20.0
DESIGN_HEIGHT = _get_design_height(DEFAULT_HEIGHT)
Z_TARGET_BOT = -0.5 * DESIGN_HEIGHT
Z_TOL_FACE   = 2.0
NZ_HORIZ_MIN = 0.60

BND_TOL_XY      = 2.0
ONLY_FREE_EDGES = True
LOWERSKIN_Z_TOL = 2.0

PICK_TOL = 2.0
ANGLE_W  = 5.0

# Mesh-based region creation for S_half_web interface
SHALF_MESH_PICK_TOL = 6.0  # mm; good starting value for ~4 mm mesh

EXCLUDE_VERTICAL_EDGES = True
VERT_Z_MIN = 0.80

# ============================================================
# Auto-surface creation from assembly sets
# ============================================================
EDGE_SURF_PREFIX = "SURF_EDGES__"
FACE_SURF_PREFIX = "SURF_FACES__"
SURF_OVERWRITE = True

# ============================================================
# Combine 2 edge-surfaces
# ============================================================
DO_COMBINE_TOP_EDGES = True
COMBINE_SURF_A   = "SURF_EDGES__SET_LOWERSKIN_EDGE_TOP"
COMBINE_SURF_B   = "SURF_EDGES__SET_SFULL_BOUNDARY_EDGE_TOP"
COMBINE_SURF_OUT = "SURF_EDGES__COMBINED_TOP_EDGES"
COMBINE_SET_OUT  = "SET_EDGES__COMBINED_TOP_EDGES"
COMBINE_OVERWRITE = True

print("=" * 72)
print("Creating_Sets5_ALLINONE2_mesh_shalf.py")
print("CASE_DIR        :", CASE_DIR)
print("DESIGN_HEIGHT   :", DESIGN_HEIGHT)
print("Z_TARGET_BOT    :", Z_TARGET_BOT)
print("Z_TOL_FACE      :", Z_TOL_FACE)
print("=" * 72)


# =========================================================================
# Helpers
# =========================================================================
def _safe_delete_set(asm, name):
    try:
        if name in asm.sets.keys():
            del asm.sets[name]
    except:
        pass

def _safe_delete_part_surface(part, name):
    try:
        if name in part.surfaces.keys():
            del part.surfaces[name]
    except:
        pass

def _safe_delete_asm_surface(asm, name):
    try:
        if name in asm.surfaces.keys():
            del asm.surfaces[name]
    except:
        pass

def _edge_mid(edge):
    try:
        return edge.pointOn[0]
    except:
        return None

def _face_point(face):
    try:
        return face.pointOn[0]
    except:
        return None

def _face_normal(face, pt):
    try:
        return face.getNormal(pt)
    except:
        return None

def _rep_face_normal_points_up(face_obj):
    p = _face_point(face_obj)
    n = _face_normal(face_obj, p)
    if n is None:
        return True
    return (n[2] > 0.0)

def _infer_edge_z_limits(edge_container):
    zmin = None
    zmax = None
    for e in edge_container:
        p = _edge_mid(e)
        if p is None:
            continue
        z = p[2]
        if (zmin is None) or (z < zmin): zmin = z
        if (zmax is None) or (z > zmax): zmax = z
    if zmin is None or zmax is None:
        raise RuntimeError("Could not infer z-limits from edges.")
    return zmin, zmax

def _is_free_edge(edge):
    try:
        fs = edge.getFaces()
        if fs is None:
            return True
        return (len(fs) == 1)
    except:
        return True

def _face_bbox_z(face_obj):
    try:
        bb = face_obj.getBoundingBox()
        return bb['low'][2], bb['high'][2]
    except:
        p = _face_point(face_obj)
        if p is None:
            return None, None
        return p[2], p[2]

def _is_horizontal_face(face_obj):
    p = _face_point(face_obj)
    if p is None:
        return (False, None)
    n = _face_normal(face_obj, p)
    if n is None:
        return (False, None)
    if abs(n[2]) < NZ_HORIZ_MIN:
        return (False, n)
    return (True, n)

def _dedupe_faces_by_index(faces):
    uniq = []
    seen = set()
    for f in faces:
        try:
            idx = int(f.index)
        except:
            idx = id(f)
        if idx in seen:
            continue
        seen.add(idx)
        uniq.append(f)
    return uniq

def _facearray_from_face_indices(inst, face_indices):
    fa = None
    for idx in face_indices:
        try:
            one = inst.faces[idx:idx+1]
        except:
            continue
        fa = one if fa is None else (fa + one)
    return fa

def _edgearray_from_edge_indices(inst, edge_indices):
    ea = None
    for idx in edge_indices:
        try:
            one = inst.edges[idx:idx+1]
        except:
            continue
        ea = one if ea is None else (ea + one)
    return ea

def _collect_candidate_edge_midpoints(inst, only_free=True, z_target=None, z_tol=None):
    out = []
    for e in inst.edges:
        if only_free and (not _is_free_edge(e)):
            continue
        p = _edge_mid(e)
        if p is None:
            continue
        if (z_target is not None) and (z_tol is not None):
            if abs(p[2] - z_target) > z_tol:
                continue
        try:
            idx = int(e.index)
        except:
            continue
        out.append((idx, p))
    return out

def _bounds_xy(edge_mid_list):
    xs = [p[0] for (_, p) in edge_mid_list]
    ys = [p[1] for (_, p) in edge_mid_list]
    if len(xs) == 0 or len(ys) == 0:
        raise RuntimeError("Could not compute XY bounds (no candidate edges).")
    return min(xs), max(xs), min(ys), max(ys)

def _pick_edge_by_point(inst, pt, max_dist):
    x, y, z = float(pt[0]), float(pt[1]), float(pt[2])
    try:
        res = inst.edges.getClosest(coordinates=((x, y, z),))
        if res is None or len(res) == 0:
            return None, 1e99
        e = res[0][0]
        d = res[0][2]
        if d <= max_dist:
            return e, d
        return None, d
    except:
        pass
    try:
        e = inst.edges.findAt(((x, y, z),))
        return e, 0.0
    except:
        return None, 1e99

def _edge_key(e):
    try:
        return int(e.index)
    except:
        return id(e)

def _dedupe_edges(edges):
    out = []
    seen = set()
    for e in edges:
        k = _edge_key(e)
        if k in seen:
            continue
        seen.add(k)
        out.append(e)
    return out

def _design_width_value(default=999.0):
    try:
        dv = globals().get('DESIGN_VARS', {}) or {}
        return float(dv.get('Width', default))
    except:
        return float(default)

def _vsub(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def _norm(v):
    return math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])

def _unit(v):
    n = _norm(v)
    if n <= 1e-18:
        return (0.0, 0.0, 0.0)
    return (v[0]/n, v[1]/n, v[2]/n)

def _dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def _edge_dir(obj, e):
    try:
        vts = e.getVertices()
        if vts is None or len(vts) < 2:
            return (0.0, 0.0, 0.0)
        pA = obj.vertices[vts[0]].pointOn[0]
        pB = obj.vertices[vts[1]].pointOn[0]
        return _unit((pB[0]-pA[0], pB[1]-pA[1], pB[2]-pA[2]))
    except:
        return (0.0, 0.0, 0.0)

def _choose_edge_by_vote_and_dir(inst, p0, mid, p1):
    seg_dir = _unit(_vsub(p1, p0))

    e_mid, d_mid = _pick_edge_by_point(inst, mid, PICK_TOL)
    e0,   d0    = _pick_edge_by_point(inst, p0,  PICK_TOL)
    e1,   d1    = _pick_edge_by_point(inst, p1,  PICK_TOL)

    cands = []
    for e, d in [(e_mid, d_mid), (e0, d0), (e1, d1)]:
        if e is None:
            continue
        cands.append((e, d))
    if len(cands) == 0:
        return None

    counts = {}
    best_d = {}
    obj = {}
    for e, d in cands:
        k = _edge_key(e)
        obj[k] = e
        counts[k] = counts.get(k, 0) + 1
        if (k not in best_d) or (d < best_d[k]):
            best_d[k] = d

    best_k = None
    for k in counts.keys():
        if best_k is None or counts[k] > counts[best_k]:
            best_k = k

    tied = [k for k in counts.keys() if counts[k] == counts[best_k]]
    if len(tied) == 1:
        return obj[best_k]

    best_k2 = None
    best_score = 1e99
    for k in tied:
        e = obj[k]
        d = best_d[k]
        edir = _edge_dir(inst, e)
        c = abs(_dot(edir, seg_dir))
        ang_pen = (1.0 - c)
        score = d + (ANGLE_W * PICK_TOL * ang_pen)
        if score < best_score:
            best_score = score
            best_k2 = k

    return obj[best_k2] if best_k2 is not None else obj[best_k]

def _require_instance(asm, name):
    if name not in asm.instances.keys():
        raise RuntimeError("Missing instance '%s'. Run import+assemble first." % name)

def _require_file(path):
    if not os.path.isfile(path):
        raise RuntimeError("Missing file: %s" % path)


# =========================================================================
# (1) S_half_web TOP/BOTTOM free-edge sets (ASM)
# =========================================================================
def create_shalf_web_top_and_bottom_edge_sets():
    model = mdb.models[MODEL]
    asm = model.rootAssembly
    _require_instance(asm, INST_SHALF_WEB)
    inst = asm.instances[INST_SHALF_WEB]

    z_bot, z_top = _infer_edge_z_limits(inst.edges)

    top_edges = []
    bot_edges = []
    for e in inst.edges:
        if not _is_free_edge(e):
            continue
        p = _edge_mid(e)
        if p is None:
            continue
        if abs(p[2] - z_top) <= Z_TOL_EDGES:
            try:
                top_edges.append(inst.edges.findAt((p,)))
            except:
                pass
        if abs(p[2] - z_bot) <= Z_TOL_EDGES:
            try:
                bot_edges.append(inst.edges.findAt((p,)))
            except:
                pass

    _safe_delete_set(asm, SET_SHALF_WEB_TOP_EDGES)
    _safe_delete_set(asm, SET_SHALF_WEB_BOT_EDGES)

    if len(top_edges) == 0 or len(bot_edges) == 0:
        raise RuntimeError("S_half_web top/bottom edge selection failed. Increase Z_TOL_EDGES.")

    asm.Set(name=SET_SHALF_WEB_TOP_EDGES, edges=_dedupe_edges(top_edges))
    asm.Set(name=SET_SHALF_WEB_BOT_EDGES, edges=_dedupe_edges(bot_edges))

    print("Created:", SET_SHALF_WEB_TOP_EDGES, "edges=", len(top_edges), "z_top=", z_top)
    print("Created:", SET_SHALF_WEB_BOT_EDGES, "edges=", len(bot_edges), "z_bot=", z_bot)


# =========================================================================
# (2) Patch Surfaces (PART-level)
# =========================================================================
def _infer_patch_z_split_from_part(part):
    zmin = None
    zmax = None
    for f in part.faces:
        p = _face_point(f)
        if p is None:
            continue
        z = p[2]
        if (zmin is None) or (z < zmin):
            zmin = z
        if (zmax is None) or (z > zmax):
            zmax = z
    if zmin is None or zmax is None:
        raise RuntimeError("Could not infer patch z split from part.")
    zmid = 0.5 * (zmin + zmax)
    return zmin, zmid, zmax

def _build_facearray_via_findAt(face_container, faces):
    pts = []
    for f in faces:
        p = _face_point(f)
        if p is not None:
            pts.append(p)
    if len(pts) == 0:
        raise RuntimeError("No face points for findAt.")
    CHUNK = 200
    sub = pts[:CHUNK]
    return face_container.findAt(*[(p,) for p in sub])

def create_patch_surfaces_part_level():
    model = mdb.models[MODEL]
    if PART_PATCHES not in model.parts.keys():
        raise RuntimeError("Missing part '%s'." % PART_PATCHES)

    part = model.parts[PART_PATCHES]

    zmin, zmid, zmax = _infer_patch_z_split_from_part(part)

    upper_faces = []
    lower_faces = []
    for f in part.faces:
        p = _face_point(f)
        if p is None:
            continue
        if p[2] > (zmid + Z_LAYER_TOL):
            upper_faces.append(f)
        elif p[2] < (zmid - Z_LAYER_TOL):
            lower_faces.append(f)

    if len(upper_faces) == 0 or len(lower_faces) == 0:
        raise RuntimeError("Patch layer split failed. Reduce Z_LAYER_TOL.")

    repU = upper_faces[0]
    nU = _face_normal(repU, _face_point(repU))
    repL = lower_faces[0]
    nL = _face_normal(repL, _face_point(repL))

    use_side_U_SNEG = 2 if (nU is not None and nU[2] > 0.0) else 1
    use_side_L_SPOS = 1 if (nL is not None and nL[2] > 0.0) else 2
    use_side_L_SNEG = 2 if (nL is not None and nL[2] > 0.0) else 1

    fa_upper = _build_facearray_via_findAt(part.faces, upper_faces)
    fa_lower = _build_facearray_via_findAt(part.faces, lower_faces)

    _safe_delete_part_surface(part, SURF_UPPER_PATCHES_SNEG)
    _safe_delete_part_surface(part, SURF_LOWER_PATCHES_SPOS)
    _safe_delete_part_surface(part, SURF_LOWER_PATCHES_SNEG)

    if use_side_U_SNEG == 2:
        part.Surface(name=SURF_UPPER_PATCHES_SNEG, side2Faces=fa_upper)
    else:
        part.Surface(name=SURF_UPPER_PATCHES_SNEG, side1Faces=fa_upper)

    if use_side_L_SPOS == 1:
        part.Surface(name=SURF_LOWER_PATCHES_SPOS, side1Faces=fa_lower)
    else:
        part.Surface(name=SURF_LOWER_PATCHES_SPOS, side2Faces=fa_lower)

    if use_side_L_SNEG == 2:
        part.Surface(name=SURF_LOWER_PATCHES_SNEG, side2Faces=fa_lower)
    else:
        part.Surface(name=SURF_LOWER_PATCHES_SNEG, side1Faces=fa_lower)

    print("Created PART surfaces:", SURF_UPPER_PATCHES_SNEG, SURF_LOWER_PATCHES_SPOS, SURF_LOWER_PATCHES_SNEG)


# =========================================================================
# (3) JSON Interface: S_full <-> S_half_web
#     S_full = assembly edge set from JSON
#     S_half = mesh-based part surface from JSON segment proximity
# =========================================================================
def create_sfull_and_shalf_end_edges_from_json(model, json_path):
    asm = model.rootAssembly
    _require_instance(asm, INST_SFULL)
    _require_instance(asm, INST_SHALF_WEB)
    _require_file(json_path)

    instS = asm.instances[INST_SFULL]
    partH = model.parts[PART_SHALF_WEB]

    f = codecs.open(json_path, 'r', 'utf-8-sig')
    j = json.load(f)
    f.close()

    sfull_recs = j.get("S_full_iface", {}).get("edges", [])
    shalf_recs = j.get("S_half_web_iface", {}).get("edges", [])

    if len(sfull_recs) == 0 or len(shalf_recs) == 0:
        raise RuntimeError("JSON has 0 edges in S_full_iface or S_half_web_iface.")

    try:
        base_tol = float(j.get('params', {}).get('join_tol', PICK_TOL))
    except:
        base_tol = PICK_TOL

    width_val = _design_width_value(999.0)

    retry_tols = [base_tol]
    if width_val <= 2.5:
        retry_tols.extend([max(base_tol, 5.0), max(base_tol, 8.0)])
    else:
        retry_tols.append(max(base_tol, 5.0))

    seen_tol = set()
    retry_tols = [t for t in retry_tols
                  if not (round(float(t), 6) in seen_tol or
                          seen_tol.add(round(float(t), 6)))]

    def _mid_from_record(rec):
        mid = rec.get("mid", None)
        p0 = rec.get("p0", None)
        p1 = rec.get("p1", None)
        if mid is None and (p0 is not None) and (p1 is not None):
            mid = [
                0.5 * (float(p0[0]) + float(p1[0])),
                0.5 * (float(p0[1]) + float(p1[1])),
                0.5 * (float(p0[2]) + float(p1[2]))
            ]
        return mid

    def _pick_sfull_edge(rec, tol):
        mid = _mid_from_record(rec)
        p0 = rec.get("p0", None)
        p1 = rec.get("p1", None)

        if mid is None:
            return None, "missing mid/p0/p1"

        if (p0 is not None) and (p1 is not None):
            e = _choose_edge_by_vote_and_dir(instS, p0, mid, p1)
            if e is not None:
                return e, None

        e, d = _pick_edge_by_point(instS, mid, tol)
        if e is not None:
            return e, None

        return None, "closest miss"

    def _dist_point_to_segment(pt, a, b):
        ax, ay, az = float(a[0]), float(a[1]), float(a[2])
        bx, by, bz = float(b[0]), float(b[1]), float(b[2])
        px, py, pz = float(pt[0]), float(pt[1]), float(pt[2])

        abx = bx - ax
        aby = by - ay
        abz = bz - az

        apx = px - ax
        apy = py - ay
        apz = pz - az

        ab2 = abx*abx + aby*aby + abz*abz
        if ab2 <= 1e-18:
            dx = px - ax
            dy = py - ay
            dz = pz - az
            return math.sqrt(dx*dx + dy*dy + dz*dz)

        t = (apx*abx + apy*aby + apz*abz) / ab2
        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0

        qx = ax + t * abx
        qy = ay + t * aby
        qz = az + t * abz

        dx = px - qx
        dy = py - qy
        dz = pz - qz
        return math.sqrt(dx*dx + dy*dy + dz*dz)

    def _elem_centroid(elem):
        try:
            nds = elem.getNodes()
        except:
            return None
        if nds is None or len(nds) == 0:
            return None
        sx = sy = sz = 0.0
        n = 0
        for nd in nds:
            c = nd.coordinates
            sx += float(c[0])
            sy += float(c[1])
            sz += float(c[2])
            n += 1
        if n == 0:
            return None
        return (sx / n, sy / n, sz / n)

    def _elem_min_node_dist_to_segment(elem, a, b):
        try:
            nds = elem.getNodes()
        except:
            return 1e99
        if nds is None or len(nds) == 0:
            return 1e99
        best = 1e99
        for nd in nds:
            d = _dist_point_to_segment(nd.coordinates, a, b)
            if d < best:
                best = d
        return best

    def _build_shalf_mesh_region(records):
        selected_labels = set()

        for rec in records:
            p0 = rec.get("p0", None)
            p1 = rec.get("p1", None)
            mid = _mid_from_record(rec)

            if p0 is None or p1 is None or mid is None:
                continue

            seg_len = math.sqrt(
                (float(p1[0]) - float(p0[0]))**2 +
                (float(p1[1]) - float(p0[1]))**2 +
                (float(p1[2]) - float(p0[2]))**2
            )

            pick_tol = max(SHALF_MESH_PICK_TOL, 0.35 * seg_len)

            for elem in partH.elements:
                ctr = _elem_centroid(elem)
                if ctr is None:
                    continue

                d_ctr = _dist_point_to_segment(ctr, p0, p1)
                d_nd  = _elem_min_node_dist_to_segment(elem, p0, p1)

                if (d_ctr <= pick_tol) or (d_nd <= 0.60 * pick_tol):
                    try:
                        selected_labels.add(int(elem.label))
                    except:
                        pass

        if len(selected_labels) == 0:
            return None

        labels = tuple(sorted(selected_labels))
        try:
            elems = partH.elements.sequenceFromLabels(labels=labels)
        except:
            elems = None
            for el in partH.elements:
                try:
                    lbl = int(el.label)
                except:
                    continue
                if lbl in selected_labels:
                    one = partH.elements[el.index:el.index+1]
                    elems = one if elems is None else (elems + one)

        return elems

    _safe_delete_set(asm, SET_SFULL_WEB_END_EDGES)
    try:
        if SET_SHALF_WEB_MESH_ELEMS in partH.sets.keys():
            del partH.sets[SET_SHALF_WEB_MESH_ELEMS]
    except:
        pass
    try:
        if SURF_SHALF_WEB_MESH in partH.surfaces.keys():
            del partH.surfaces[SURF_SHALF_WEB_MESH]
    except:
        pass

    pickedS = []
    missedS = 0
    last_diag = []

    for tol in retry_tols:
        pickedS = []
        missedS = 0
        diag = []

        for i, recS in enumerate(sfull_recs):
            eS, errS = _pick_sfull_edge(recS, tol)
            if eS is None:
                missedS += 1
                diag.append("S_full[%d] miss err=%s tol=%.3f" % (i, str(errS), tol))
                continue
            pickedS.append(eS)

        pickedS = _dedupe_edges(pickedS)
        if len(pickedS) > 0:
            print("S_full JSON->edge match succeeded | Width=", width_val,
                  "| tol=", tol, "| S_full=", len(pickedS), "| missedS=", missedS)
            break
        last_diag = diag[:]

    if len(pickedS) == 0:
        msg = "JSON->S_full end edges: picked 0. Width=%s Tried tolerances=%s" % (width_val, retry_tols)
        if last_diag:
            msg += " Diagnostics: " + " | ".join(last_diag[:8])
        raise RuntimeError(msg)

    shalf_mesh_elems = _build_shalf_mesh_region(shalf_recs)
    if shalf_mesh_elems is None or len(shalf_mesh_elems) == 0:
        raise RuntimeError("S_half_web mesh region selection produced 0 elements. Increase SHALF_MESH_PICK_TOL.")

    asm.Set(name=SET_SFULL_WEB_END_EDGES, edges=pickedS)
    partH.Set(name=SET_SHALF_WEB_MESH_ELEMS, elements=shalf_mesh_elems)
    partH.Surface(name=SURF_SHALF_WEB_MESH, side1Elements=shalf_mesh_elems)

    print("Created ASM set:", SET_SFULL_WEB_END_EDGES, "edges=", len(pickedS), "tols=", retry_tols)
    print("Created PART mesh set:", SET_SHALF_WEB_MESH_ELEMS, "elements=", len(shalf_mesh_elems))
    print("Created PART mesh surface:", SURF_SHALF_WEB_MESH, "elements=", len(shalf_mesh_elems))


# =========================================================================
# (4) S_full bottom flange underside faces set + surface (ASM)
# =========================================================================
def create_sfull_bottom_flange_lower_set_and_surface():
    model = mdb.models[MODEL]
    asm = model.rootAssembly
    _require_instance(asm, INST_SFULL)
    instS = asm.instances[INST_SFULL]

    cand = []
    for f0 in instS.faces:
        okH, n = _is_horizontal_face(f0)
        if not okH:
            continue
        zlow, zhigh = _face_bbox_z(f0)
        if zlow is None:
            continue
        if abs(zlow - Z_TARGET_BOT) <= Z_TOL_FACE:
            cand.append(f0)

    if len(cand) == 0:
        raise RuntimeError("No S_full bottom flange faces selected. Increase Z_TOL_FACE or relax NZ_HORIZ_MIN.")

    fa_list = _dedupe_faces_by_index(cand)
    idxs = []
    seen = set()
    for ff in fa_list:
        idx = int(ff.index)
        if idx in seen:
            continue
        seen.add(idx)
        idxs.append(idx)

    fa = _facearray_from_face_indices(instS, idxs)
    if fa is None or len(fa) == 0:
        raise RuntimeError("Could not build FaceArray for S_full bottom flange faces.")

    _safe_delete_set(asm, SET_SFULL_BOT_FLANGE_LOWER_FACES)
    asm.Set(name=SET_SFULL_BOT_FLANGE_LOWER_FACES, faces=fa)

    normal_up = _rep_face_normal_points_up(fa[0])
    _safe_delete_asm_surface(asm, SURF_SFULL_BOT_FLANGE_SNEG)

    if normal_up:
        asm.Surface(name=SURF_SFULL_BOT_FLANGE_SNEG, side2Faces=fa)
    else:
        asm.Surface(name=SURF_SFULL_BOT_FLANGE_SNEG, side1Faces=fa)

    print("Created:", SET_SFULL_BOT_FLANGE_LOWER_FACES, "faces=", len(fa))
    print("Created ASM surface:", SURF_SFULL_BOT_FLANGE_SNEG, "faces=", len(fa))


# =========================================================================
# (5) Lower_Skin upper face set + surface (ASM)
# =========================================================================
def create_lowerskin_upper_set_and_surface():
    model = mdb.models[MODEL]
    asm = model.rootAssembly
    _require_instance(asm, INST_LOWERSKIN)
    instK = asm.instances[INST_LOWERSKIN]

    cand = []
    for f0 in instK.faces:
        okH, n = _is_horizontal_face(f0)
        if not okH:
            continue
        zlow, zhigh = _face_bbox_z(f0)
        if zhigh is None:
            continue
        if abs(zhigh - Z_TARGET_BOT) <= Z_TOL_FACE:
            cand.append(f0)

    if len(cand) == 0:
        raise RuntimeError("No Lower_Skin upper faces selected. Increase Z_TOL_FACE or relax NZ_HORIZ_MIN.")

    fa_list = _dedupe_faces_by_index(cand)
    idxs = []
    seen = set()
    for ff in fa_list:
        idx = int(ff.index)
        if idx in seen:
            continue
        seen.add(idx)
        idxs.append(idx)

    fa = _facearray_from_face_indices(instK, idxs)
    if fa is None or len(fa) == 0:
        raise RuntimeError("Could not build FaceArray for Lower_Skin upper faces.")

    _safe_delete_set(asm, SET_LOWERSKIN_UPPER_FACES)
    asm.Set(name=SET_LOWERSKIN_UPPER_FACES, faces=fa)

    normal_up = _rep_face_normal_points_up(fa[0])
    _safe_delete_asm_surface(asm, SURF_LOWERSKIN_TOP_SPOS)

    if normal_up:
        asm.Surface(name=SURF_LOWERSKIN_TOP_SPOS, side1Faces=fa)
    else:
        asm.Surface(name=SURF_LOWERSKIN_TOP_SPOS, side2Faces=fa)

    print("Created:", SET_LOWERSKIN_UPPER_FACES, "faces=", len(fa))
    print("Created ASM surface:", SURF_LOWERSKIN_TOP_SPOS, "faces=", len(fa))


# =========================================================================
# (6) Lower_Skin perimeter edge sets (ASM)
# =========================================================================
def create_lowerskin_perimeter_edge_sets():
    model = mdb.models[MODEL]
    asm = model.rootAssembly
    _require_instance(asm, INST_LOWERSKIN)
    instK = asm.instances[INST_LOWERSKIN]

    cand = _collect_candidate_edge_midpoints(
        instK, only_free=ONLY_FREE_EDGES,
        z_target=Z_TARGET_BOT, z_tol=LOWERSKIN_Z_TOL
    )
    if len(cand) == 0:
        raise RuntimeError("No candidate Lower_Skin edges found. Increase LOWERSKIN_Z_TOL or disable ONLY_FREE_EDGES.")

    xmin, xmax, ymin, ymax = _bounds_xy(cand)

    left_idx, right_idx, top_idx, bottom_idx = [], [], [], []
    for (idx, p) in cand:
        if abs(p[0] - xmin) <= BND_TOL_XY:
            left_idx.append(idx)
        if abs(p[0] - xmax) <= BND_TOL_XY:
            right_idx.append(idx)
        if abs(p[1] - ymax) <= BND_TOL_XY:
            top_idx.append(idx)
        if abs(p[1] - ymin) <= BND_TOL_XY:
            bottom_idx.append(idx)

    def _mk(name, idxs):
        _safe_delete_set(asm, name)
        ea = _edgearray_from_edge_indices(instK, sorted(list(set(idxs))))
        if ea is None or len(ea) == 0:
            print("WARN:", name, "created 0 edges (increase BND_TOL_XY).")
            return
        asm.Set(name=name, edges=ea)
        print("Created:", name, "edges=", len(ea))

    _mk(SET_LOWERSKIN_EDGE_LEFT, left_idx)
    _mk(SET_LOWERSKIN_EDGE_RIGHT, right_idx)
    _mk(SET_LOWERSKIN_EDGE_TOP, top_idx)
    _mk(SET_LOWERSKIN_EDGE_BOTTOM, bottom_idx)

    print("--- Lower_Skin bounds --- xmin=%.3f xmax=%.3f ymin=%.3f ymax=%.3f" % (xmin, xmax, ymin, ymax))


# =========================================================================
# (7) S_full boundary edge sets (ASM)
# =========================================================================
def create_sfull_boundary_edge_sets():
    model = mdb.models[MODEL]
    asm = model.rootAssembly
    _require_instance(asm, INST_SFULL)
    instS = asm.instances[INST_SFULL]

    cand = _collect_candidate_edge_midpoints(instS, only_free=ONLY_FREE_EDGES)
    if len(cand) == 0:
        raise RuntimeError("No candidate S_full edges found. Disable ONLY_FREE_EDGES if needed.")

    xmin, xmax, ymin, ymax = _bounds_xy(cand)

    left_idx, right_idx, top_idx, bottom_idx = [], [], [], []
    for (idx, p) in cand:
        if abs(p[0] - xmin) <= BND_TOL_XY:
            left_idx.append(idx)
        if abs(p[0] - xmax) <= BND_TOL_XY:
            right_idx.append(idx)
        if abs(p[1] - ymax) <= BND_TOL_XY:
            top_idx.append(idx)
        if abs(p[1] - ymin) <= BND_TOL_XY:
            bottom_idx.append(idx)

    def _mk(name, idxs):
        _safe_delete_set(asm, name)
        ea = _edgearray_from_edge_indices(instS, sorted(list(set(idxs))))
        if ea is None or len(ea) == 0:
            print("WARN:", name, "created 0 edges (increase BND_TOL_XY).")
            return
        asm.Set(name=name, edges=ea)
        print("Created:", name, "edges=", len(ea))

    _mk(SET_SFULL_BND_EDGE_LEFT, left_idx)
    _mk(SET_SFULL_BND_EDGE_RIGHT, right_idx)
    _mk(SET_SFULL_BND_EDGE_TOP, top_idx)
    _mk(SET_SFULL_BND_EDGE_BOTTOM, bottom_idx)

    print("--- S_full bounds --- xmin=%.3f xmax=%.3f ymin=%.3f ymax=%.3f" % (xmin, xmax, ymin, ymax))


# =========================================================================
# (8) JSON Interface: S_full <-> Patches edge sets (ASM)
# =========================================================================
def create_sfull_patches_interface_sets_from_json(json_path):
    model = mdb.models[MODEL]
    asm = model.rootAssembly
    _require_instance(asm, INST_SFULL)
    _require_instance(asm, INST_PATCHES)
    _require_file(json_path)

    instS = asm.instances[INST_SFULL]
    instP = asm.instances[INST_PATCHES]

    f = codecs.open(json_path, 'r', 'utf-8-sig')
    j = json.load(f)
    f.close()

    sfull_recs = j.get("S_full_touch", {}).get("edges", [])
    patch_recs = j.get("Patches_touch", {}).get("edges", [])

    if len(sfull_recs) == 0 or len(patch_recs) == 0:
        raise RuntimeError("JSON has 0 edges in S_full_touch or Patches_touch.")

    pickedS, missedS = [], 0
    for r in sfull_recs:
        mid = r.get("mid", None)
        p0  = r.get("p0", None)
        p1  = r.get("p1", None)
        if mid is None:
            continue

        if (p0 is not None) and (p1 is not None):
            e = _choose_edge_by_vote_and_dir(instS, p0, mid, p1)
        else:
            e, d = _pick_edge_by_point(instS, mid, PICK_TOL)

        if e is None:
            missedS += 1
            continue

        if EXCLUDE_VERTICAL_EDGES:
            edir = _edge_dir(instS, e)
            if abs(edir[2]) >= VERT_Z_MIN:
                continue

        pickedS.append(e)

    pickedS = _dedupe_edges(pickedS)

    pickedP, missedP = [], 0
    for r in patch_recs:
        mid = r.get("mid", None)
        if mid is None:
            continue
        e, d = _pick_edge_by_point(instP, mid, PICK_TOL)
        if e is None:
            missedP += 1
            continue
        pickedP.append(e)

    pickedP = _dedupe_edges(pickedP)

    _safe_delete_set(asm, SET_SFULL_PATCH_IFACE_EDGES)
    _safe_delete_set(asm, SET_PATCHES_SFULL_IFACE_EDGES)

    if len(pickedS) == 0:
        raise RuntimeError("Picked 0 S_full iface edges. Increase PICK_TOL or disable EXCLUDE_VERTICAL_EDGES.")
    if len(pickedP) == 0:
        raise RuntimeError("Picked 0 Patches iface edges. Increase PICK_TOL.")

    asm.Set(name=SET_SFULL_PATCH_IFACE_EDGES, edges=pickedS)
    asm.Set(name=SET_PATCHES_SFULL_IFACE_EDGES, edges=pickedP)

    print("Created:", SET_SFULL_PATCH_IFACE_EDGES, "edges=", len(pickedS), "missed=", missedS,
          "EXCLUDE_VERTICAL_EDGES=", EXCLUDE_VERTICAL_EDGES)
    print("Created:", SET_PATCHES_SFULL_IFACE_EDGES, "edges=", len(pickedP), "missed=", missedP)


# =========================================================================
# (9) Convert ALL assembly sets to assembly surfaces
# =========================================================================
def _sanitize(name):
    bad = [' ', '-', '.', ':', '/', '\\', '[', ']', '(', ')', '{', '}', ',']
    out = name
    for b in bad:
        out = out.replace(b, '_')
    return out[:70]

def _has_edges(set_obj):
    try:
        return (set_obj.edges is not None) and (len(set_obj.edges) > 0)
    except:
        return False

def _has_faces(set_obj):
    try:
        return (set_obj.faces is not None) and (len(set_obj.faces) > 0)
    except:
        return False

def create_surfaces_from_all_assembly_sets():
    model = mdb.models[MODEL]
    asm = model.rootAssembly

    n_edge = 0
    n_face = 0
    n_skip = 0

    set_names = asm.sets.keys()
    set_names.sort()

    for sname in set_names:
        s = asm.sets[sname]
        made_any = False

        if _has_edges(s):
            surf_name = EDGE_SURF_PREFIX + _sanitize(sname)
            if SURF_OVERWRITE:
                _safe_delete_asm_surface(asm, surf_name)
            try:
                asm.Surface(name=surf_name, side1Edges=s.edges)
                n_edge += 1
                made_any = True
            except Exception as e:
                print("WARN: failed edge surface for set:", sname, "->", str(e))

        if _has_faces(s):
            surf_name = FACE_SURF_PREFIX + _sanitize(sname)
            if SURF_OVERWRITE:
                _safe_delete_asm_surface(asm, surf_name)
            try:
                asm.Surface(name=surf_name, side1Faces=s.faces)
                n_face += 1
                made_any = True
            except Exception as e:
                print("WARN: failed face surface for set:", sname, "->", str(e))

        if not made_any:
            n_skip += 1

    print("---- DONE: surfaces created from assembly sets ----")
    print("Edge-surfaces created :", n_edge)
    print("Face-surfaces created :", n_face)
    print("Sets skipped (no edges/faces):", n_skip)


# =========================================================================
# (10) Combine two EDGE-based assembly surfaces
# =========================================================================
def _get_edge_sequence_from_surface(surf):
    try:
        ed = surf.side1Edges
        if ed and len(ed) > 0:
            return ed
    except:
        pass
    try:
        ed = surf.side2Edges
        if ed and len(ed) > 0:
            return ed
    except:
        pass
    try:
        ed = surf.edges
        if ed and len(ed) > 0:
            return ed
    except:
        pass
    return None

def combine_two_edge_surfaces_and_make_set(surf_a, surf_b, surf_out, set_out):
    model = mdb.models[MODEL]
    asm = model.rootAssembly

    if surf_a not in asm.surfaces.keys():
        raise RuntimeError("Surface not found: %s" % surf_a)
    if surf_b not in asm.surfaces.keys():
        raise RuntimeError("Surface not found: %s" % surf_b)

    sa = asm.surfaces[surf_a]
    sb = asm.surfaces[surf_b]

    ea = _get_edge_sequence_from_surface(sa)
    eb = _get_edge_sequence_from_surface(sb)

    if ea is None or len(ea) == 0:
        raise RuntimeError("No edges found on surface: %s" % surf_a)
    if eb is None or len(eb) == 0:
        raise RuntimeError("No edges found on surface: %s" % surf_b)

    if COMBINE_OVERWRITE:
        _safe_delete_asm_surface(asm, surf_out)
        _safe_delete_set(asm, set_out)

    try:
        eall = ea + eb
        asm.Surface(name=surf_out, side1Edges=eall)
        asm.Set(name=set_out, edges=eall)
        print("Created combined surface+set (mode ea+eb):", surf_out, set_out, "edges=", len(eall))
        return
    except Exception as e:
        print("WARN: combine mode (ea+eb) failed:", str(e))

    asm.Surface(name=surf_out, side1Edges=(ea, eb))
    asm.Set(name=set_out, edges=(ea, eb))
    print("Created combined surface+set (mode tuple):", surf_out, set_out, "edges=", (len(ea) + len(eb)))


# =========================================================================
# RUN ALL
# =========================================================================
def main():
    model = mdb.models[MODEL]
    asm = model.rootAssembly

    _require_instance(asm, INST_SFULL)
    _require_instance(asm, INST_SHALF_WEB)
    _require_instance(asm, INST_PATCHES)
    _require_instance(asm, INST_LOWERSKIN)

    print("CASE_DIR:", _case_path())
    print("JSON_SFULL_SHALF  :", JSON_SFULL_SHALF)
    print("JSON_SFULL_PATCHES:", JSON_SFULL_PATCHES)

    _require_file(JSON_SFULL_SHALF)
    _require_file(JSON_SFULL_PATCHES)

    create_shalf_web_top_and_bottom_edge_sets()
    create_patch_surfaces_part_level()

    create_sfull_and_shalf_end_edges_from_json(model, JSON_SFULL_SHALF)

    create_sfull_bottom_flange_lower_set_and_surface()
    create_lowerskin_upper_set_and_surface()

    create_lowerskin_perimeter_edge_sets()
    create_sfull_boundary_edge_sets()

    create_sfull_patches_interface_sets_from_json(JSON_SFULL_PATCHES)

    create_surfaces_from_all_assembly_sets()

    if DO_COMBINE_TOP_EDGES:
        combine_two_edge_surfaces_and_make_set(
            COMBINE_SURF_A, COMBINE_SURF_B,
            COMBINE_SURF_OUT, COMBINE_SET_OUT
        )

    print("DONE: sets + surfaces (+ optional combine) created.")

main()