import os
import sys
import re

search_dir = sys.argv[1] if len(sys.argv) > 1 else "."
print(f"Scanning for .xcodeproj in: {search_dir}")

found = False
for root, dirs, files in os.walk(search_dir):
    for d in dirs:
        if d.endswith(".xcodeproj"):
            found = True
            pbx = os.path.join(root, d, "project.pbxproj")
            if os.path.exists(pbx):
                with open(pbx, "r", encoding="utf-8") as f:
                    c = f.read()
                
                # Force manual code signing
                c = c.replace("CODE_SIGN_STYLE = Automatic;", "CODE_SIGN_STYLE = Manual;")
                # Remove development team requirements
                c = re.sub(r'DevelopmentTeam = [^;]*;', 'DevelopmentTeam = "";', c)
                c = re.sub(r'DevelopmentTeam\[[^\]]*\] = [^;]*;', 'DevelopmentTeam = "";', c)
                # Remove provisioning profiles
                c = re.sub(r'PROVISIONING_PROFILE_SPECIFIER = [^;]*;', 'PROVISIONING_PROFILE_SPECIFIER = "";', c)
                c = re.sub(r'PROVISIONING_PROFILE = [^;]*;', 'PROVISIONING_PROFILE = "";', c)
                # Clear code sign identity
                c = re.sub(r'CODE_SIGN_IDENTITY = [^;]*;', 'CODE_SIGN_IDENTITY = "";', c)
                c = re.sub(r'CODE_SIGN_IDENTITY\[[^\]]*\] = [^;]*;', 'CODE_SIGN_IDENTITY = "";', c)
                # Force disable signing in all build settings
                c = c.replace("buildSettings = {", 'buildSettings = {\n\t\t\t\tCODE_SIGNING_ALLOWED = NO;\n\t\t\t\tCODE_SIGNING_REQUIRED = NO;\n\t\t\t\tCODE_SIGN_IDENTITY = "";')
                
                with open(pbx, "w", encoding="utf-8") as f:
                    f.write(c)
                print(f"Successfully patched {pbx} for manual unsigned build")

if not found:
    print(f"Warning: No .xcodeproj found in {search_dir}")
