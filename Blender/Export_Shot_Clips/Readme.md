# How to Install the Plugin
========================================================================================================================================
1. Open Blender and Install the Plugin:
   Open Edit > Preferences.
   Select the Add-ons tab and click Install....
   Choose the .py file that has been created and click Install Add-on.

2. Activate the Plugin:
   Search for the plugin name (e.g., "Export Shot Clips Panel") and check the box to activate it.


# How to Use the Plugin
========================================================================================================================================
1. Open Video Sequencer:
   Open the Video Editing layout or create a Video Sequencer window in Blender.

2. Open the Plugin Sidebar:
   Press the N key to open the sidebar, then select the Export Shots tab.

3. Set Export Directory:
   Fill in the Export Directory field with the folder that will be used to store the exported results.

4. Create Shot Adjustment Layer:
   Click the Create Shot Adjustment button and enter the shot number (e.g., 005).
   An adjustment layer will be created with the name shot005.

5. Export Shot Clips:
   Click the Export Shot Clips button. The plugin will:

   - Create a new folder (e.g., export1) in the set directory, with subfolders mp4 and blend inside.
   - Render the video according to the duration of the adjustment layer and save the MP4 file in the mp4 folder.
   - Duplicate the scene, trim other strips to match the shot duration, and save the .blend file in the blend folder.

6. Check Exported Results:
   Open the export1 folder (or the newly created export folder) to see the video file in the mp4 folder and the .blend file in the blend folder.

---
### Credits
MrYapikZ
Website: [expiproject.com](https://expiproject.com)

