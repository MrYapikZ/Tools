bl_info = {
    "name": "Export Shot Clips Panel",
    "description": (
        "Create shot adjustment layers and export shot clips as MP4. "
        "Before export, a new folder (exportN) is created automatically with a subfolder 'mp4'. "
        "The shot clip is trimmed to the adjustment layer's length."
    ),
    "author": "MrYapikZ (modified by ChatGPT)",
    "version": (1, 0, 1),
    "blender": (2, 80, 0),
    "location": "Video Sequencer > Sidebar > Export Shots Tab",
    "category": "Sequencer",
}

import bpy
import os
import re


# -------------------------------------------------------------------
# Operator: Create Shot Adjustment Layer
# -------------------------------------------------------------------
class SEQUENCER_OT_create_shot_adjustment(bpy.types.Operator):
    """
    Create a new adjustment layer with a sequential shot number.

    For the first shot, enter a template (e.g. BJL03_SQ01-SH002) via the dialog.
    Subsequent shots will auto-increment the numeric portion (e.g. BJL03_SQ01-SH003).
    """
    bl_idname = "sequencer.create_shot_adjustment"
    bl_label = "Create Shot Adjustment"

    shot_number: bpy.props.StringProperty(name="Shot Number", default="")

    def invoke(self, context, event):
        scene = context.scene
        if scene.sequence_editor:
            # Find existing adjustment strips matching the pattern *-SH###.
            shots = [
                s for s in scene.sequence_editor.sequences_all
                if s.type == 'ADJUSTMENT' and re.match(r'.*-SH\d+$', s.name, re.IGNORECASE)
            ]
            if shots:
                max_num = -1
                prefix = ""
                num_str = ""
                for s in shots:
                    match = re.match(r'(.*-SH)(\d+)$', s.name, re.IGNORECASE)
                    if match:
                        current_prefix = match.group(1)
                        num_str = match.group(2)
                        try:
                            num = int(num_str)
                            if num > max_num:
                                max_num = num
                                prefix = current_prefix
                        except ValueError:
                            pass
                if max_num >= 0:
                    new_number = max_num + 1
                    # Preserve the same digit count
                    self.shot_number = f"{prefix}{str(new_number).zfill(len(num_str))}"
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if not self.shot_number:
            self.report({'ERROR'}, "Shot Number cannot be empty.")
            return {'CANCELLED'}
        scene = context.scene
        if not scene.sequence_editor:
            scene.sequence_editor_create()
        frame_start = scene.frame_current
        frame_end = frame_start + 100  # Arbitrary length; adjust if needed.
        channel = 2  # Adjust channel if necessary

        bpy.ops.sequencer.effect_strip_add(
            frame_start=frame_start,
            frame_end=frame_end,
            channel=channel,
            type='ADJUSTMENT'
        )
        new_strip = scene.sequence_editor.active_strip
        if new_strip:
            new_strip.name = self.shot_number
            self.report({'INFO'}, f"Created adjustment layer: {new_strip.name}")
        else:
            self.report({'WARNING'}, "Adjustment layer not created.")
        return {'FINISHED'}


# -------------------------------------------------------------------
# Operator: Export Shot Clips (Render MP4)
# -------------------------------------------------------------------
class SEQUENCER_OT_export_shot_clips(bpy.types.Operator):
    """
    Render shot clips for adjustment layers whose names follow the pattern *-SH###.
    """
    bl_idname = "sequencer.export_shot_clips"
    bl_label = "Export Shot Clips"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        export_path = context.scene.export_shot_path
        if not export_path:
            self.report({'ERROR'}, "No export directory specified. Please set one in the panel.")
            return {'CANCELLED'}
        scene = context.scene
        if not scene.sequence_editor:
            self.report({'ERROR'}, "No sequence editor found in the current scene.")
            return {'CANCELLED'}
        sequences = scene.sequence_editor.sequences_all

        # Store original render settings.
        orig_frame_start = scene.frame_start
        orig_frame_end = scene.frame_end
        orig_filepath = scene.render.filepath

        # Create a new export folder inside the chosen directory.
        base_export_dir = bpy.path.abspath(export_path)
        n = 1
        while True:
            new_export_dir = os.path.join(base_export_dir, f"export{n}")
            if not os.path.exists(new_export_dir):
                os.makedirs(new_export_dir)
                break
            n += 1

        # Create subfolder for MP4 files.
        mp4_dir = os.path.join(new_export_dir, "mp4")
        os.makedirs(mp4_dir, exist_ok=True)

        shot_found = False

        for seq in sequences:
            # Process only adjustment strips with names matching the pattern *-SH###.
            if seq.type == 'ADJUSTMENT' and re.match(r'.*-SH\d+$', seq.name, re.IGNORECASE):
                shot_found = True
                shot_name = seq.name
                shot_start = int(seq.frame_final_start)
                shot_end = int(seq.frame_final_end) - 1

                self.report({'INFO'}, f"Processing {shot_name}: frames {shot_start} to {shot_end}")

                scene.frame_start = shot_start
                scene.frame_end = shot_end
                mp4_filename = f"{shot_name}.mp4"
                scene.render.filepath = os.path.join(mp4_dir, mp4_filename)
                bpy.ops.render.render(animation=True)

        # Restore original render settings.
        scene.frame_start = orig_frame_start
        scene.frame_end = orig_frame_end
        scene.render.filepath = orig_filepath

        if not shot_found:
            self.report({'WARNING'}, "No adjustment strips with valid shot naming found.")
            return {'CANCELLED'}

        self.report({'INFO'}, "Shot clips exported successfully.")
        return {'FINISHED'}


# -------------------------------------------------------------------
# Panel in the Sequencer Sidebar
# -------------------------------------------------------------------
class SEQUENCER_PT_export_shot_clips_panel(bpy.types.Panel):
    bl_label = "Export Shot Clips"
    bl_idname = "SEQUENCER_PT_export_shot_clips_panel"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Export Shots"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "export_shot_path", text="Export Directory")
        layout.operator("sequencer.export_shot_clips", text="Export Shot Clips")
        layout.operator("sequencer.create_shot_adjustment", text="Create Shot Adjustment")


# -------------------------------------------------------------------
# Registration
# -------------------------------------------------------------------
def register():
    bpy.utils.register_class(SEQUENCER_OT_create_shot_adjustment)
    bpy.utils.register_class(SEQUENCER_OT_export_shot_clips)
    bpy.utils.register_class(SEQUENCER_PT_export_shot_clips_panel)
    bpy.types.Scene.export_shot_path = bpy.props.StringProperty(
        name="Export Path",
        description=(
            "Directory to export shot clips. "
            "A new folder (exportN) with a subfolder 'mp4' will be created here."
        ),
        subtype='DIR_PATH',
        default=""
    )


def unregister():
    del bpy.types.Scene.export_shot_path
    bpy.utils.unregister_class(SEQUENCER_PT_export_shot_clips_panel)
    bpy.utils.unregister_class(SEQUENCER_OT_export_shot_clips)
    bpy.utils.unregister_class(SEQUENCER_OT_create_shot_adjustment)


if __name__ == "__main__":
    register()
