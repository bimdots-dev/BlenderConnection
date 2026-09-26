import bpy

from . import utils
from . import server_state

class OBJECT_PT_archicad_status_panel (bpy.types.Panel):
    bl_label = "Archicad Connection Status"
    bl_idname = "OBJECT_PT_archicad_status_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Archicad'

    def draw (self, context):
        status_text = "Running" if server_state.server is not None else "Not running"
        status_icon = 'CHECKMARK' if server_state.server is not None else 'X'
        col = self.layout.column (align=True)
        col.label (text = f"Port: {server_state.port if server_state.port is not None else 'N/A'}", icon = 'NETWORK_DRIVE')
        col.label (text = f"Status: {status_text}", icon = status_icon)
        col.label (text = f"Version: {utils.get_addon_version (server_state.bl_info)}", icon = 'INFO_LARGE')

classes = (
    OBJECT_PT_archicad_status_panel,
)

def register ():
    for cls in classes:
        bpy.utils.register_class (cls)

def unregister ():
    for cls in reversed (classes):
        bpy.utils.unregister_class (cls)
