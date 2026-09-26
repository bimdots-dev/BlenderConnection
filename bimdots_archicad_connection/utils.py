import bpy

def write_log (message):
    print (f"[Archicad Connection] {message}", flush = True)

def get_addon_version (bl_info):
    version_tuple = bl_info.get ("version", ())
    return ".".join (str (part) for part in version_tuple)
