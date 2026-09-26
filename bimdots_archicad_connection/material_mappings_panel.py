import bpy

from . import material_utils

# Blender may retain strings from dynamic enum items after the callback returns.
# The callback's temporary list does not keep those strings alive after it finishes.
# This cache owns each tuple and its strings while the add-on is loaded.
# Entries are retained so Blender cannot access released strings from an earlier refresh.
material_enum_item_cache = {}

def get_material_enum_items (self, context):
    enum_items = []
    for material in bpy.data.materials:
        material_name = material.name
        if material_name not in material_enum_item_cache:
            material_enum_item_cache[material_name] = (material_name, material_name, "")
        enum_items.append (material_enum_item_cache[material_name])
    return enum_items

class OBJECT_UL_archicad_material_mapping_list (bpy.types.UIList):
    def draw_item (self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row (align = True)
        row.prop (item, "source_name", text = "")
        select_operator = row.operator ("archicad.material_mapping_pick_source", text = "", icon = 'VIEWZOOM')
        select_operator.mapping_index = index
        row.prop (item, "target_material", text = "")

class OBJECT_OT_archicad_material_mapping_pick_source (bpy.types.Operator):
    bl_idname = "archicad.material_mapping_pick_source"
    bl_label = "Select Source Material"
    bl_property = "selected_material_name"

    mapping_index: bpy.props.IntProperty ()
    selected_material_name: bpy.props.EnumProperty (name = "Source Material", items = get_material_enum_items)

    def invoke (self, context, event):
        context.window_manager.invoke_search_popup (self)
        return {'RUNNING_MODAL'}

    def execute (self, context):
        scene = context.scene
        mappings = scene.archicad_material_mappings
        if 0 <= self.mapping_index < len (mappings):
            mappings[self.mapping_index].source_name = self.selected_material_name
        return {'FINISHED'}

class OBJECT_OT_archicad_material_mapping_add (bpy.types.Operator):
    bl_idname = "archicad.material_mapping_add"
    bl_label = "Add Material Mapping"

    def execute (self, context):
        scene = context.scene
        scene.archicad_material_mappings.add ()
        scene.archicad_material_mapping_selected_index = len (scene.archicad_material_mappings) - 1
        return {'FINISHED'}

class OBJECT_OT_archicad_material_mapping_remove (bpy.types.Operator):
    bl_idname = "archicad.material_mapping_remove"
    bl_label = "Remove Material Mapping"

    @classmethod
    def poll (cls, context):
        return context.scene.archicad_material_mappings

    def execute (self, context):
        scene = context.scene
        index = scene.archicad_material_mapping_selected_index
        scene.archicad_material_mappings.remove (index)
        scene.archicad_material_mapping_selected_index = min (index, len (scene.archicad_material_mappings) - 1)
        return {'FINISHED'}

class OBJECT_PT_archicad_material_mapping_panel (bpy.types.Panel):
    bl_label = "Archicad Material Mapping"
    bl_idname = "OBJECT_PT_archicad_material_mapping_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Archicad'

    def draw (self, context):
        scene = context.scene
        layout = self.layout
        row = layout.row ()
        row.template_list (
            "OBJECT_UL_archicad_material_mapping_list", "",
            scene, "archicad_material_mappings",
            scene, "archicad_material_mapping_selected_index",
            rows = 8
        )
        col = row.column (align = True)
        col.operator ("archicad.material_mapping_add", icon = 'ADD', text = "")
        col.operator ("archicad.material_mapping_remove", icon = 'REMOVE', text = "")

classes = (
    material_utils.MaterialMappingItem,
    OBJECT_UL_archicad_material_mapping_list,
    OBJECT_OT_archicad_material_mapping_pick_source,
    OBJECT_OT_archicad_material_mapping_add,
    OBJECT_OT_archicad_material_mapping_remove,
    OBJECT_PT_archicad_material_mapping_panel,
)

def register ():
    for cls in classes:
        bpy.utils.register_class (cls)
    bpy.types.Scene.archicad_material_mappings = bpy.props.CollectionProperty (type = material_utils.MaterialMappingItem)
    bpy.types.Scene.archicad_material_mapping_selected_index = bpy.props.IntProperty ()

def unregister ():
    del bpy.types.Scene.archicad_material_mapping_selected_index
    del bpy.types.Scene.archicad_material_mappings
    for cls in reversed (classes):
        bpy.utils.unregister_class (cls)
