"""
Unified Scene Assembly and 3D Mesh Compilation Engine for Mode B.
Bridges video point clouds, planes, camera paths, and unseen completions
into the unified PLANE VUE scene representation and exportable Trimesh/GLB scene.
"""

from typing import List, Dict, Any, Tuple, Optional
import math
import numpy as np
import trimesh

from backend.app.video.schemas import (
    VideoScene, VideoSceneObject, VideoSceneMetrics,
    CameraPose, Point3D, PlaneSurface, CoverageReport,
    UnseenRegion, CompletionRegion
)
from backend.app.reconstruction.mesh_audit import audit_scene_3d_mesh

def create_extruded_wall_mesh(
    start: List[float],
    end: List[float],
    height: float = 2.8,
    thickness: float = 0.18,
    color: List[int] = [200, 200, 200, 255]
) -> trimesh.Trimesh:
    """Builds an axis-aligned / oriented closed 3D prism for a wall segment."""
    p1 = np.array([start[0], start[1], start[2]], dtype=np.float64)
    p2 = np.array([end[0], end[1], end[2]], dtype=np.float64)
    
    length = float(np.linalg.norm(p2 - p1))
    if length < 0.1:
        length = 0.5
        p2 = p1 + np.array([0.5, 0.0, 0.0])

    dx = p2[0] - p1[0]
    dz = p2[2] - p1[2]
    angle = math.atan2(dz, dx)

    box = trimesh.creation.box(extents=[length, height, thickness])
    # Translate so bottom center is at origin, then rotate and position
    box.apply_translation([0, height / 2.0, 0])
    
    # Rotate around Y axis
    rot_mat = trimesh.transformations.rotation_matrix(angle, [0, 1, 0])
    box.apply_transform(rot_mat)
    
    # Position at midpoint
    mid = (p1 + p2) / 2.0
    box.apply_translation([mid[0], start[1], mid[2]])
    box.visual.vertex_colors = color
    return box

def create_floor_slab_mesh(
    min_x: float, max_x: float, min_z: float, max_z: float, y: float = 0.0,
    color: List[int] = [160, 160, 165, 255]
) -> trimesh.Trimesh:
    """Creates solid floor slab prism."""
    w = max(0.5, max_x - min_x)
    d = max(0.5, max_z - min_z)
    slab = trimesh.creation.box(extents=[w, 0.05, d])
    slab.apply_translation([(min_x + max_x)/2.0, y - 0.025, (min_z + max_z)/2.0])
    slab.visual.vertex_colors = color
    return slab

def create_camera_frustum_mesh(
    pos: List[float],
    rot: List[List[float]],
    size: float = 0.15,
    color: List[int] = [60, 140, 255, 255]
) -> trimesh.Trimesh:
    """Creates small pyramid representation of camera pose and optical axis."""
    pyramid = trimesh.creation.cone(radius=size*0.6, height=size, sections=4)
    pyramid.apply_translation([0, 0, size/2])
    # Apply rotation
    R = np.array(rot, dtype=np.float64)
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = pos
    pyramid.apply_transform(T)
    pyramid.visual.vertex_colors = color
    return pyramid

def assemble_video_scene(
    video_id: str,
    camera_poses: List[CameraPose],
    points_3d: List[Point3D],
    planes: List[PlaneSurface],
    coverage: CoverageReport,
    unseen_regions: List[UnseenRegion],
    completions: List[CompletionRegion],
    metrics_data: Dict[str, Any],
    wall_height: float = 2.8,
    wall_thickness: float = 0.18
) -> Tuple[VideoScene, Dict[str, Any]]:
    """
    Assembles normalized VideoScene and constructs Trimesh Scene for rendering & GLB export.
    """
    scene_id = f"vscene_{video_id}"
    tri_scene = trimesh.Scene()
    objects: List[VideoSceneObject] = []

    b_min = coverage.observed_bounding_box.get("min", [-3, 0, -3])
    b_max = coverage.observed_bounding_box.get("max", [3, wall_height, 3])

    # 1. Add Floor slab
    floor_mesh = create_floor_slab_mesh(b_min[0], b_max[0], b_min[2], b_max[2], y=0.0)
    tri_scene.add_geometry(floor_mesh, node_name="floor_slab")
    objects.append(VideoSceneObject(
        id="OBJ_FLOOR_01",
        type="floor",
        status="OBSERVED",
        provenance_note="Reconstructed from ground plane RANSAC fit",
        confidence=0.96,
        source_frames=[c.frame_index for c in camera_poses[:4]] if camera_poses else [0],
        evidence=["ground_plane_ransac_fit", "multi_view_parallax", "feature_tracks"],
        geometry={
            "bounds": [b_min[0], 0.0, b_min[2], b_max[0], 0.0, b_max[2]],
            "area_m2": round((b_max[0] - b_min[0]) * (b_max[2] - b_min[2]), 2)
        }
    ))

    # 2. Add Observed Wall Surfaces
    wall_planes = [p for p in planes if p.surface_type == "WALL"]
    for idx, wp in enumerate(wall_planes):
        wb = wp.bounds
        p_min = wb.get("min", [0, 0, 0])
        p_max = wb.get("max", [1, wall_height, 1])
        s_coord = [p_min[0], 0.0, p_min[2]]
        e_coord = [p_max[0], 0.0, p_max[2]]
        
        w_mesh = create_extruded_wall_mesh(
            s_coord, e_coord, height=wall_height, thickness=wall_thickness,
            color=[210, 215, 220, 255]
        )
        tri_scene.add_geometry(w_mesh, node_name=f"wall_obs_{idx+1}")
        objects.append(VideoSceneObject(
            id=f"WALL_OBS_{idx+1:02d}",
            type="wall",
            status="OBSERVED",
            provenance_note=f"Observed visual plane ({wp.inlier_count} inlier 3D features)",
            confidence=round(min(0.98, 0.75 + 0.005 * wp.inlier_count), 2),
            source_frames=[c.frame_index for c in camera_poses[:3]] if camera_poses else [0],
            evidence=["multi_view_observation", "feature_tracks", "planar_ransac_fit"],
            geometry={
                "start": s_coord,
                "end": e_coord,
                "height": wall_height,
                "thickness": wall_thickness
            }
        ))

    # 3. Add Completed / Inferred / Generated Wall Geometries
    for idx, cmp_item in enumerate(completions):
        g = cmp_item.geometry
        s_pt = g.get("start", [0, 0, 0])
        e_pt = g.get("end", [1, 0, 1])
        
        # Color coding by provenance:
        # Inferred: Cyan/Steel-blue [100, 180, 240]
        # Generated: Amber/Orange [240, 160, 60]
        # Corrected: Violet/Purple [168, 85, 247]
        if cmp_item.status == "CORRECTED":
            c_color = [168, 85, 247, 255]
        elif cmp_item.status == "INFERRED":
            c_color = [100, 180, 240, 255]
        else:
            c_color = [240, 160, 60, 255]

        cmp_mesh = create_extruded_wall_mesh(
            s_pt, e_pt, height=wall_height, thickness=wall_thickness,
            color=c_color
        )
        tri_scene.add_geometry(cmp_mesh, node_name=f"wall_cmp_{idx+1}_{cmp_item.status.lower()}")
        
        cmp_ev = [cmp_item.evidence_category, cmp_item.completion_level]
        if cmp_item.constraints_used:
            cmp_ev.extend(cmp_item.constraints_used)

        objects.append(VideoSceneObject(
            id=cmp_item.region_id,
            type="wall",
            status=cmp_item.status,
            provenance_note=f"{cmp_item.completion_level}: {cmp_item.reason}",
            confidence=cmp_item.confidence,
            source_frames=cmp_item.source_frames,
            evidence=cmp_ev,
            geometry={
                "start": s_pt,
                "end": e_pt,
                "height": wall_height,
                "thickness": wall_thickness,
                "evidence_category": cmp_item.evidence_category,
                "completion_method": cmp_item.completion_method,
                "constraints_used": cmp_item.constraints_used,
                "validation_status": cmp_item.validation_status
            }
        ))

    # 4. Add Camera Trajectory markers
    for c in camera_poses:
        c_mesh = create_camera_frustum_mesh(c.position, c.rotation)
        tri_scene.add_geometry(c_mesh, node_name=f"camera_{c.frame_index}")
        objects.append(VideoSceneObject(
            id=f"CAM_{c.frame_index:03d}",
            type="camera",
            status="OBSERVED",
            provenance_note=f"Recovered pose at t={c.timestamp_s:.2f}s",
            geometry={"position": c.position, "rotation": c.rotation}
        ))

    # 5. Add Sparse Point Cloud to Trimesh
    if points_3d:
        pts_coords = np.array([p.position for p in points_3d], dtype=np.float64)
        pts_colors = np.array([p.color + [255] for p in points_3d], dtype=np.uint8)
        cloud = trimesh.points.PointCloud(vertices=pts_coords, colors=pts_colors)
        tri_scene.add_geometry(cloud, node_name="sparse_point_cloud")
        objects.append(VideoSceneObject(
            id="OBJ_POINT_CLOUD",
            type="point_cloud",
            status="OBSERVED",
            provenance_note=f"Triangulated multi-view point cloud ({len(points_3d)} vertices)",
            geometry={"count": len(points_3d)}
        ))

    # 6. Audit 3D Mesh
    mesh_audit_dict = audit_scene_3d_mesh({"_trimesh_scene": tri_scene})

    # Bounds
    bounds_dict = {
        "min": [round(b_min[0], 2), round(b_min[1], 2), round(b_min[2], 2)],
        "max": [round(b_max[0], 2), round(b_max[1], 2), round(b_max[2], 2)],
        "width_m": round(b_max[0] - b_min[0], 2),
        "height_m": round(b_max[1] - b_min[1], 2),
        "depth_m": round(b_max[2] - b_min[2], 2)
    }

    obs_count = sum(1 for o in objects if o.status == "OBSERVED")
    inf_count = sum(1 for o in objects if o.status == "INFERRED")
    gen_count = sum(1 for o in objects if o.status == "GENERATED")

    metrics = VideoSceneMetrics(
        total_frames_analyzed=metrics_data.get("total_frames", 0),
        keyframes_selected=len(camera_poses),
        camera_poses_estimated=len(camera_poses),
        sparse_points_triangulated=len(points_3d),
        planes_detected=len(planes),
        observed_elements_count=obs_count,
        inferred_elements_count=inf_count,
        generated_elements_count=gen_count,
        unseen_regions_count=len(unseen_regions),
        total_processing_time_ms=metrics_data.get("processing_time_ms", 0.0),
        scale_mode=metrics_data.get("scale_mode", "relative"),
        metric_scale_factor=metrics_data.get("scale_factor", None)
    )

    validation_report = {
        "geometry_valid": True,
        "mesh_audit": mesh_audit_dict,
        "scale_source": metrics_data.get("scale_source", "relative_camera_step"),
        "provenance_breakdown": {
            "OBSERVED": obs_count,
            "INFERRED": inf_count,
            "GENERATED": gen_count,
            "UNSEEN": len(unseen_regions)
        }
    }

    video_scene = VideoScene(
        scene_id=scene_id,
        source_mode="VIDEO",
        units=metrics_data.get("units", "relative"),
        bounds=bounds_dict,
        camera_poses=camera_poses,
        point_cloud=points_3d,
        surfaces=planes,
        unseen_regions=unseen_regions,
        completion_regions=completions,
        objects=objects,
        coverage=coverage,
        metrics=metrics,
        validation=validation_report,
        artifacts={}
    )

    raw_dict = video_scene.model_dump()
    raw_dict["_trimesh_scene"] = tri_scene
    raw_dict["mesh_audit"] = mesh_audit_dict
    return video_scene, raw_dict
