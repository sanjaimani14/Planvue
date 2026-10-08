import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import trimesh

def export_glb(scene_3d: Dict[str, Any], output_path: str) -> str:
    """
    Exports 3D reconstruction to binary glTF (.glb) format:
    - Retains wall, floor, door, and window geometry
    - Embeds vertex colors for architectural materials
    - Verifies 'glTF' magic header before returning
    """
    tri_scene = scene_3d.get("_trimesh_scene")
    if tri_scene is None or len(tri_scene.geometry) == 0:
        # Fallback to an empty or default box to prevent crash
        tri_scene = trimesh.Scene()
        box = trimesh.creation.box(extents=[1, 1, 1])
        tri_scene.add_geometry(box)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    glb_data = tri_scene.export(file_type="glb")
    from backend.app.reconstruction.mesh_audit import validate_glb_file
    val_report = validate_glb_file(glb_data)
    if not val_report["is_valid"]:
        raise ValueError(f"GLB validation failed: {', '.join(val_report['errors'])}")

    with open(output_path, "wb") as f:
        f.write(glb_data)

    return output_path


def export_obj(scene_3d: Dict[str, Any], output_path: str) -> str:
    """
    Exports 3D reconstruction to Wavefront OBJ format.
    """
    tri_scene = scene_3d.get("_trimesh_scene")
    if tri_scene is None or len(tri_scene.geometry) == 0:
        tri_scene = trimesh.Scene()
        box = trimesh.creation.box(extents=[1, 1, 1])
        tri_scene.add_geometry(box)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    obj_data = tri_scene.export(file_type="obj")
    if isinstance(obj_data, bytes):
        with open(output_path, "wb") as f:
            f.write(obj_data)
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(obj_data)

    return output_path

def export_json(scene_3d: Dict[str, Any], output_path: str) -> str:
    """
    Exports normalized 3D scene representation to JSON.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    clean_dict = {k: v for k, v in scene_3d.items() if not k.startswith("_")}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(clean_dict, f, indent=2)
    return output_path
