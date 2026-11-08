import os
import shutil
import struct

print("=== Running patch_project.py for iOS ===")

# 1. Remove Nintendo Switch SDK
nn_path = "Assets/Scripts/Assembly-CSharp/nn"
if os.path.exists(nn_path):
    print("Removing Switch nn SDK...")
    shutil.rmtree(nn_path, ignore_errors=True)
if os.path.exists(nn_path + ".meta"):
    os.remove(nn_path + ".meta")

# 2. Remove unused Rewired Demos and Switch platform scripts
demos_path = "Assets/Scripts/Assembly-CSharp/Rewired/Demos"
if os.path.exists(demos_path):
    print("Removing Rewired Demos...")
    shutil.rmtree(demos_path, ignore_errors=True)
if os.path.exists(demos_path + ".meta"):
    os.remove(demos_path + ".meta")

switch_plat = "Assets/Scripts/Assembly-CSharp/Rewired/Platforms/Switch"
if os.path.exists(switch_plat):
    print("Removing Rewired Switch platform...")
    shutil.rmtree(switch_plat, ignore_errors=True)
if os.path.exists(switch_plat + ".meta"):
    os.remove(switch_plat + ".meta")

plat_parent = "Assets/Scripts/Assembly-CSharp/Rewired/Platforms"
if os.path.exists(plat_parent):
    try:
        if not os.listdir(plat_parent):
            os.rmdir(plat_parent)
            if os.path.exists(plat_parent + ".meta"):
                os.remove(plat_parent + ".meta")
    except Exception:
        pass

# 3. Stub NintendoManager.cs
nm_path = "Assets/Scripts/Assembly-CSharp/NintendoManager.cs"
nm_code = """using UnityEngine.Events;

public class NintendoManager : PersistentSingleton<NintendoManager>
{
\tprivate const string mountName = "MySave";
\tprivate const string fileName = "MySaveData";
\tprivate static readonly string filePath;
\tprivate bool IsReady;
\tpublic bool IsHandheldMode => true;

\tprivate void Start() {}
\tprivate void AbortBool(string message, UnityAction<bool> onComplete) { onComplete?.Invoke(false); }
\tprivate void AbortString(string message, UnityAction<string> onComplete) { onComplete?.Invoke(""); }
\tpublic void Save(string data, UnityAction<bool> onComplete) { onComplete?.Invoke(true); }
\tpublic void Load(UnityAction<string> onComplete) { onComplete?.Invoke(""); }
}
"""
with open(nm_path, "w", encoding="utf-8") as f:
    f.write(nm_code)
print("Updated NintendoManager.cs")

# 4. Patch ControlMapper.cs (GUIElement parameterless constructor)
cm_path = "Assets/Scripts/Assembly-CSharp/Rewired/UI/ControlMapper/ControlMapper.cs"
if os.path.exists(cm_path):
    with open(cm_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "public GUIElement()" not in content:
        content = content.replace(
            "public GUIElement(GameObject gameObject)",
            "public GUIElement() {}\n\t\t\tpublic GUIElement(GameObject gameObject)"
        )
        with open(cm_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched ControlMapper.cs")

# 5. Patch UnityUITextMeshProGlyphHelper.cs (Tag parameterless constructor)
tm_path = "Assets/Scripts/Assembly-CSharp/Rewired/Glyphs/UnityUI/UnityUITextMeshProGlyphHelper.cs"
if os.path.exists(tm_path):
    with open(tm_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "protected Tag()" not in content:
        content = content.replace(
            "protected Tag(TagType tagType)",
            "protected Tag() {}\n\t\t\tprotected Tag(TagType tagType)"
        )
        with open(tm_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched UnityUITextMeshProGlyphHelper.cs")

# 6. Remove Switch-only DLLs and dummy generated DLLs
switch_dlls = [
    "Rewired_NintendoSwitch.dll",
    "Unity.InputSystem.Switch.dll",
    "UnityEngine.SwitchModule.dll",
    "__Generated.dll"
]
plugins_dir = "Assets/Plugins"
for s_dll in switch_dlls:
    p = os.path.join(plugins_dir, s_dll)
    if os.path.exists(p):
        os.remove(p)
        print(f"Removed {s_dll}")
    if os.path.exists(p + ".meta"):
        os.remove(p + ".meta")

# 7. Fix PE headers on all DLLs to ensure IMAGE_FILE_DLL (0x2000) is set
# This prevents MonoLinker from treating DLLs as executables and crashing on assembly.EntryPoint
for root, dirs, files in os.walk(plugins_dir):
    for f in files:
        if f.endswith(".dll"):
            dll_path = os.path.join(root, f)
            try:
                with open(dll_path, "r+b") as fp:
                    data = fp.read()
                    if len(data) > 0x40 and data[:2] == b"MZ":
                        pe_offset = struct.unpack("<I", data[0x3c:0x40])[0]
                        char_offset = pe_offset + 22
                        characteristics = struct.unpack("<H", data[char_offset:char_offset+2])[0]
                        if not (characteristics & 0x2000):
                            characteristics |= 0x2000
                            fp.seek(char_offset)
                            fp.write(struct.pack("<H", characteristics))
                            print(f"Fixed PE characteristics (IMAGE_FILE_DLL) for {f}")
            except Exception as e:
                print(f"Error checking {f}: {e}")

print("=== Patching complete! ===")
