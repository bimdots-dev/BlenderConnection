import bpy

from . import utils

class MaterialMappingItem (bpy.types.PropertyGroup):
    source_name: bpy.props.StringProperty (name = "Source Material Name")
    target_material: bpy.props.PointerProperty (name = "Target Material", type = bpy.types.Material)

class MaterialAccessor:
    mappings: dict[str, bpy.types.Material]

    def __init__ (self):
        self.mappings = {}
        scene = bpy.context.scene
        if scene is None:
            return None
        mappings = getattr (scene, "archicad_material_mappings", None)
        if mappings is None:
            return None
        for mapping in mappings:
            if mapping.source_name is not None and len (mapping.source_name) > 0 and mapping.target_material is not None:
                self.mappings[mapping.source_name] = mapping.target_material

    def get_material (self, data):
        name = data.get ("name")
        mapped = self.mappings.get (name, None)
        if mapped is not None:
            return mapped

        existing = bpy.data.materials.get (name, None)
        if existing is not None:
            return existing

        return None

def create_material ( data):
    name = data.get ("name")
    color = data.get ("color")
    metallic = data.get ("metallic")
    roughness = data.get ("roughness")
    alpha = data.get ("alpha")

    mat = bpy.data.materials.new (name)
    mat.use_nodes = True
    
    if mat.node_tree is None:
        return mat
    
    principled_node = mat.node_tree.nodes.get ("Principled BSDF")
    if principled_node is None:
        return mat
    
    principled_node.inputs["Base Color"].default_value = (*color, 1.0)
    principled_node.inputs["Metallic"].default_value = metallic
    principled_node.inputs["Roughness"].default_value = roughness
    principled_node.inputs["Alpha"].default_value = alpha

    if "texture" in data:
        texture_data = data["texture"]
        texture_file_path = texture_data.get ("file_path")
        if texture_file_path:
            try:
                img = bpy.data.images.load (texture_file_path, check_existing = True)
                if img.packed_file is None:
                    img.pack ()
                scale = texture_data.get ("scale")
                rotation = texture_data.get ("rotation")

                tex_coord_node = mat.node_tree.nodes.new ("ShaderNodeTexCoord")
                tex_mapping_node = mat.node_tree.nodes.new ("ShaderNodeMapping")
                tex_node = mat.node_tree.nodes.new ("ShaderNodeTexImage")

                tex_node.image = img

                tex_mapping_node.vector_type = 'TEXTURE'
                tex_mapping_node.inputs["Scale"].default_value = (*scale, 1.0)
                tex_mapping_node.inputs["Rotation"].default_value = (0.0, 0.0, rotation)

                mat.node_tree.links.new (tex_coord_node.outputs["UV"], tex_mapping_node.inputs["Vector"])
                mat.node_tree.links.new (tex_mapping_node.outputs["Vector"], tex_node.inputs["Vector"])

                mat.node_tree.links.new (tex_node.outputs["Color"], principled_node.inputs["Base Color"])
                mat.node_tree.links.new (tex_node.outputs["Alpha"], principled_node.inputs["Alpha"])
            except Exception as e:
                utils.write_log (f"Error loading texture from {texture_file_path}: {e}")

    return mat

