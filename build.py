import PyInstaller.__main__
import os
import shutil
import subprocess

def refresh_icon_cache():
    try:
        # Kill the Windows Explorer process
        subprocess.run(['taskkill', '/F', '/IM', 'explorer.exe'], capture_output=True)
        
        # Delete icon cache files
        appdata = os.environ.get('LOCALAPPDATA', '')
        icon_cache_paths = [
            os.path.join(appdata, 'IconCache.db'),
            os.path.join(appdata, 'Microsoft\\Windows\\Explorer\\iconcache_*.db'),
            os.path.join(appdata, 'Microsoft\\Windows\\Explorer\\thumbcache_*.db')
        ]
        
        for cache_path in icon_cache_paths:
            try:
                if '*' in cache_path:
                    # Handle wildcard paths
                    directory = os.path.dirname(cache_path)
                    pattern = os.path.basename(cache_path)
                    base_pattern = pattern.split('*')[0]
                    for file in os.listdir(directory):
                        if file.startswith(base_pattern):
                            full_path = os.path.join(directory, file)
                            os.remove(full_path)
                else:
                    if os.path.exists(cache_path):
                        os.remove(cache_path)
            except:
                pass
        
        # Restart Explorer
        subprocess.Popen('explorer.exe')
    except:
        pass

def build_exe():
    # Get the directory where build.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to your icon file - assuming it's in the same directory as build.py
    icon_path = os.path.join(current_dir, 'icon.ico')
    
    # Verify icon exists
    if not os.path.exists(icon_path):
        print(f"Error: icon.ico not found in {current_dir}")
        print("Please place your icon.ico file in the same directory as build.py")
        return
    
    # Clean previous builds
    for path in ['build', 'dist']:
        if os.path.exists(path):
            shutil.rmtree(path)
    if os.path.exists('Project-Sunny.spec'):
        os.remove('Project-Sunny.spec')
    
    print("Building executable...")
    
    # Create version file
    version_info = """# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'luxx'),
        StringStruct(u'FileDescription', u'Project Sunny Password Cracker'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'sunny'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2024 luxx'),
        StringStruct(u'OriginalFilename', u'Project Sunny.exe'),
        StringStruct(u'ProductName', u'Project Sunny'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ])
  ]
)"""
    
    version_file = os.path.join(current_dir, 'version.txt')
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    # PyInstaller options
    options = [
        'Sunny.py',  # Your main script
        '--onefile',  # Create a single executable
        '--console',  # Show console for debugging - remove later if you want
        f'--icon={icon_path}',  # Set icon
        '--name=Project-Sunny',  # Name of the executable
        '--clean',  # Clean cache
        '--uac-admin',  # Request admin privileges
        f'--version-file={version_file}',  # Add version info
        # Add required hidden imports
        '--hidden-import=win32gui',
        '--hidden-import=colorama',
        '--hidden-import=rarfile',
        '--hidden-import=py7zr',
    ]
    
    # Run PyInstaller
    PyInstaller.__main__.run(options)
    
    # Clean up version file
    if os.path.exists(version_file):
        os.remove(version_file)
    
    print("Refreshing Windows icon cache...")
    refresh_icon_cache()
    
    print("Build complete! Check the 'dist' folder for your executable.")
    print("Icon Was Not Found Nah JK if this is the first time you're running this script, it's fine.")

if __name__ == "__main__":
    build_exe() 