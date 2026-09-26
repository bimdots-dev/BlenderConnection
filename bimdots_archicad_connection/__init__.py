bl_info = {
    "id": "bimdots_archicad_connection",
    "name": "Bimdots Archicad Connection",
    "author": "Bimdots",
    "version": (1, 5, 0),
    "blender": (5, 0, 0),
    "description": "Bimdots Archicad Connection",
    "category": "Import-Export",
}

import sys
import socket
import json
import threading
from urllib.parse import parse_qs, urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from concurrent.futures import Future

import bpy
import mathutils

from . import utils
from . import server_state
from . import object_utils
from . import material_utils
from . import status_panel
from . import material_mappings_panel

PORT = 35400
MAX_PORT = 35420
SOURCE_OBJECT_ID_KEY = "source_object_id"
SOURCE_OBJECT_CHECKSUM_KEY = "source_object_checksum"

server_state.bl_info = bl_info

def get_id_to_object_map (collection):
    id_to_object_map = {}
    for obj in collection.all_objects:
        source_id = obj.get (SOURCE_OBJECT_ID_KEY)
        if source_id is not None:
            id_to_object_map[source_id] = obj
    return id_to_object_map

def get_objects (data: dict) -> dict:
    result = {
        "objects": []
    }

    collection_name = data.get ("model_name")
    model_collection = bpy.data.collections.get (collection_name)
    if model_collection is None:
        return result

    for obj in model_collection.objects:
        result["objects"].append ({
            "id": obj.get (SOURCE_OBJECT_ID_KEY),
            "checksum": obj.get (SOURCE_OBJECT_CHECKSUM_KEY)
        })

    return result

def update_meshes (data: dict) -> dict:
    result = {
        "materials_created": 0,
        "meshes_created": 0,
        "meshes_updated": 0
    }

    collection_name = data.get ("model_name")
    model_collection = object_utils.get_model_collection (collection_name)

    material_list = data.get ("materials")
    mesh_list = data.get ("meshes")

    id_to_object_map = get_id_to_object_map (model_collection)
    material_accessor = material_utils.MaterialAccessor ()
    for mesh_data in mesh_list:
        id = mesh_data.get ("id")
        is_existing = id in id_to_object_map
        if is_existing:
            existing_obj = id_to_object_map[id]
            object_utils.delete_object (existing_obj)

        name = mesh_data.get ("name")
        mesh = bpy.data.meshes.new (name)

        vertices = mesh_data.get ("vertices")
        vertex_coords = [(vertices[i], vertices[i + 1], vertices[i + 2]) for i in range (0, len (vertices), 3)]
        faces = mesh_data.get ("faces")
        mesh.from_pydata (vertex_coords, [], faces)

        normals = mesh_data.get ("normals")
        normal_vectors = [(normals[i], normals[i + 1], normals[i + 2]) for i in range (0, len (normals), 3)]
        if len (normal_vectors) != len (mesh.loops):
            utils.write_log (f"Error: Number of normals ({len (normal_vectors)}) does not match number of loops ({len (mesh.loops)}).")
            continue
        mesh.normals_split_custom_set (normal_vectors)

        uvs = mesh_data.get ("uvs")
        uv_vectors = [(uvs[i], uvs[i + 1]) for i in range (0, len (uvs), 2)]
        if len (uv_vectors) != len (mesh.loops):
            utils.write_log (f"Error: Number of UVs ({len (uv_vectors)}) does not match number of loops ({len (mesh.loops)}).")
            continue
        uv_layer = mesh.uv_layers.new (name = "UVMap")
        for index, uv in enumerate (uv_vectors):
            uv_layer.data[index].uv = uv

        face_materials = mesh_data.get ("face_materials")
        if len (face_materials) != len (faces):
            utils.write_log (f"Error: Number of face materials ({len (face_materials)}) does not match number of faces ({len (faces)}).")
            continue
        
        materialIndexMap: dict[int, int] = {}
        for i in range (0, len (face_materials)):
            material_index = face_materials[i]
            if material_index in materialIndexMap:
                mesh_material_index = materialIndexMap[material_index]
            else:
                material_data = material_list[material_index]
                material = material_accessor.get_material (material_data)
                if material is None:
                    material = material_utils.create_material (material_data)
                    result["materials_created"] += 1
                mesh.materials.append (material)
                new_material_index = len (mesh.materials) - 1
                materialIndexMap[material_index] = new_material_index
                mesh_material_index = new_material_index
            mesh.polygons[i].material_index = mesh_material_index

        mesh.update ()
        mesh.validate ()

        location = mesh_data.get ("location")
        checksum = mesh_data.get ("checksum")

        mesh_obj = bpy.data.objects.new (name, mesh)
        mesh_obj[SOURCE_OBJECT_ID_KEY] = id
        mesh_obj[SOURCE_OBJECT_CHECKSUM_KEY] = checksum

        mesh_obj.location = location
        model_collection.objects.link (mesh_obj)

        if is_existing:
            result["meshes_updated"] += 1
        else:
            result["meshes_created"] += 1

    return result

def get_existing_light (name):
    light_obj = bpy.data.objects.get (name)
    light = bpy.data.lights.get (name)
    if light_obj is not None and light_obj.data == light:
        return light_obj, light_obj.data
    if light_obj is not None:
        utils.delete_object (light_obj)
        return None, None
    return None, None

def update_sun (data: dict) -> dict:
    result = {
        "sun_created": 0,
        "sun_updated": 0
    }

    name = data.get ("name")

    is_existing = True
    light_obj, light = get_existing_light (name)
    if light_obj is None or light is None:
        light = bpy.data.lights.new (name, type = 'SUN')
        light_obj = bpy.data.objects.new (name, light)
        target_collection = object_utils.get_target_collection ()
        target_collection.objects.link (light_obj)
        is_existing = False

    light.color = data.get ("color")
    light.energy = data.get ("energy")
    direction_vector = mathutils.Vector (data.get ("direction"))
    if direction_vector.length > 0:
        rotation_quat = direction_vector.to_track_quat ('-Z', 'Z')
        light_obj.rotation_mode = 'QUATERNION'
        light_obj.rotation_quaternion = rotation_quat

    if is_existing:
        result["sun_updated"] += 1
    else:
        result["sun_created"] += 1

    return result

def delete_objects (data: dict) -> dict:
    result = {
        "objects_deleted": 0
    }

    collection_name = data.get ("model_name")
    model_collection = bpy.data.collections.get (collection_name)
    if model_collection is None:
        return result

    object_id_list = data.get ("object_ids")
    id_to_object_map = get_id_to_object_map (model_collection)
    for object_id in object_id_list:
        if object_id in id_to_object_map:
            object_utils.delete_object (id_to_object_map[object_id])
            result["objects_deleted"] += 1

    return result

class BimdotsRequestHandler (BaseHTTPRequestHandler):
    def do_GET (self):
        parsed_url = urlparse (self.path)
        if parsed_url.path == "/is-alive":
            self._send_success_response ({
                "version": utils.get_addon_version (bl_info)
            })
        else:
            self._send_not_found_response ()

    def do_POST (self):
        content_length = int (self.headers.get ("Content-Length", 0))
        raw_body = self.rfile.read (content_length) if content_length > 0 else b""

        try:
            body = json.loads (raw_body) if raw_body else {}
        except json.JSONDecodeError:
            utils.write_log ("Rejected request: invalid JSON body.")
            self._send_error_response (400, "Request body must be valid JSON.")
            return

        if self.path == "/get-objects":
            return_value = self._run_on_main_thread (lambda: get_objects (body))
            self._send_success_response (return_value)
        elif self.path == "/update-meshes":
            return_value = self._run_on_main_thread (lambda: update_meshes (body))
            self._send_success_response (return_value)
        elif self.path == "/update-sun":
            return_value = self._run_on_main_thread (lambda: update_sun (body))
            self._send_success_response (return_value)
        elif self.path == "/delete-objects":
            return_value = self._run_on_main_thread (lambda: delete_objects (body))
            self._send_success_response (return_value)
        else:
            self._send_not_found_response ()

    def log_message (self, format, *args):
        utils.write_log (f"{self.address_string ()} - {format % args}")

    def _run_on_main_thread (self, func):
        future = Future ()
        def timer_function ():
            try:
                result = func ()
                future.set_result (result)
            except Exception as e:
                utils.write_log (f"Error running function on main thread: {e}")
                future.set_result (None)
            return None
        bpy.app.timers.register (timer_function, first_interval = 0.0)
        return future.result ()

    def _send_json_response (self, status_code, payload):
        body = json.dumps (payload).encode ("utf-8")
        self.send_response (status_code)
        self.send_header ("Content-type", "application/json")
        self.send_header ("Content-length", str(len (body)))
        self.end_headers ()
        self.wfile.write (body)

    def _send_success_response (self, payload: dict):
        self._send_json_response (200, payload)

    def _send_error_response (self, status_code: int, message: str):
        self._send_json_response (status_code, { "error": message })

    def _send_not_found_response (self):
        self._send_error_response (404, "Not found.")

class ExclusivePortHTTPServer (HTTPServer):
    allow_reuse_address = False

    def server_bind (self):
        if sys.platform == "win32":
            self.socket.setsockopt (socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super ().server_bind ()

def start_server ():
    for port in range (PORT, MAX_PORT + 1):
        try:
            server_state.server = ExclusivePortHTTPServer (("localhost", port), BimdotsRequestHandler)
            server_state.port = port
            server_state.server_thread = threading.Thread (target = server_state.server.serve_forever, daemon = True)
            server_state.server_thread.start ()
            utils.write_log (f"Listening on http://localhost:{port}")
            break
        except Exception as e:
            utils.write_log (f"Failed to start server on port {port}")

def stop_server ():
    if server_state.server:
        server_state.server.shutdown ()
        server_state.server.server_close ()
        server_state.server = None
    if server_state.server_thread:
        server_state.server_thread.join (timeout = 2)
        server_state.server_thread = None
    utils.write_log ("Server stopped")

def register ():
    status_panel.register ()
    material_mappings_panel.register ()
    start_server ()

def unregister ():
    stop_server ()
    material_mappings_panel.unregister ()
    status_panel.unregister ()

if __name__ == "__main__":
    register ()
