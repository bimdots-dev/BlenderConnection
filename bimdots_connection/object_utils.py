import bpy

def get_target_collection ():
    if bpy.context.view_layer is not None:
        return bpy.context.view_layer.active_layer_collection.collection
    if bpy.context.scene is not None:
        return bpy.context.scene.collection
    return bpy.context.collection

def get_model_collection (model_name):
    target_collection = get_target_collection ()
    if target_collection is None:
        return None
    model_collection = bpy.data.collections.get (model_name)
    if model_collection is None:
        model_collection = bpy.data.collections.new (model_name)
        target_collection.children.link (model_collection)
    return model_collection

def delete_object (obj):
    obj_data = obj.data
    bpy.data.objects.remove (obj)
    if isinstance (obj_data, bpy.types.Mesh):
        bpy.data.meshes.remove (obj_data)
    elif isinstance (obj_data, bpy.types.Light):
        bpy.data.lights.remove (obj_data)
