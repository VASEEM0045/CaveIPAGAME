import os
import shutil

print("=== Running patch_project.py for iOS ===")

# 1. Remove Nintendo Switch SDK
nn_path = "Assets/Scripts/Assembly-CSharp/nn"
if os.path.exists(nn_path):
    print("Removing Switch nn SDK...")
    shutil.rmtree(nn_path, ignore_errors=True)
if os.path.exists(nn_path + ".meta"):
    os.remove(nn_path + ".meta")

# 2. Remove unused Rewired Demos
demos_path = "Assets/Scripts/Assembly-CSharp/Rewired/Demos"
if os.path.exists(demos_path):
    print("Removing Rewired Demos...")
    shutil.rmtree(demos_path, ignore_errors=True)
if os.path.exists(demos_path + ".meta"):
    os.remove(demos_path + ".meta")

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

print("=== Patching complete! ===")
