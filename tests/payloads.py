import uuid

def unique_name (prefix):
    return f"{prefix}_{uuid.uuid4 ().hex}"

def make_material (name, color = (1.0, 0.0, 0.0), alpha = 1.0, texture = None):
    material = {
        "name": name,
        "color": list (color),
        "metallic": 0.0,
        "roughness": 0.5,
        "alpha": alpha
    }
    if texture is not None:
        material["texture"] = texture
    return material

def make_triangle_mesh (id, checksum = "checksum", name = None, location = (0, 0, 0), material_index = 0):
    return {
        "id": id,
        "name": name if name is not None else id,
        "checksum": checksum,
        "location": list (location),
        "vertices": [
            0.0, 0.0, 0.0,
            1.0, 0.0, 0.0,
            1.0, 1.0, 0.0
        ],
        "normals": [
            0.0, 0.0, 1.0,
            0.0, 0.0, 1.0,
            0.0, 0.0, 1.0
        ],
        "uvs": [
            0.0, 0.0,
            1.0, 0.0,
            1.0, 1.0
        ],
        "faces": [
            [0, 1, 2]
        ],
        "face_materials": [
            material_index
        ]
    }

def make_quad_mesh (id, checksum = "checksum", face_materials = (0, 0)):
    return {
        "id": id,
        "name": id,
        "checksum": checksum,
        "location": [0, 0, 0],
        "vertices": [
            0.0, 0.0, 0.0,
            1.0, 0.0, 0.0,
            1.0, 1.0, 0.0,
            0.0, 1.0, 0.0
        ],
        "normals": [0.0, 0.0, 1.0] * 6,
        "uvs": [
            0.0, 0.0,
            1.0, 0.0,
            1.0, 1.0,
            0.0, 0.0,
            1.0, 1.0,
            0.0, 1.0
        ],
        "faces": [
            [0, 1, 2],
            [0, 2, 3]
        ],
        "face_materials": list (face_materials)
    }

def make_mesh_with_faces (id, faces, checksum = "checksum"):
    corner_count = sum (len (face) for face in faces)
    return {
        "id": id,
        "name": id,
        "checksum": checksum,
        "location": [0, 0, 0],
        "vertices": [
            0.0, 0.0, 0.0,
            1.0, 0.0, 0.0,
            1.0, 1.0, 0.0,
            0.0, 1.0, 0.0
        ],
        "normals": [0.0, 0.0, 1.0] * corner_count,
        "uvs": [0.0, 0.0] * corner_count,
        "faces": faces,
        "face_materials": [0] * len (faces)
    }

def make_update_meshes_payload (model_name, meshes, materials = None):
    return {
        "model_name": model_name,
        "materials": materials if materials is not None else [make_material ("Red")],
        "meshes": meshes
    }
