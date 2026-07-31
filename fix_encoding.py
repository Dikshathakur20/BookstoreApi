import os

def fix_encoding(file_path):
    try:
        # Try to read as UTF-8
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✔️ Already UTF-8: {file_path}")
    except UnicodeDecodeError:
        # If fails, read as UTF-16 and save as UTF-8
        try:
            with open(file_path, 'r', encoding='utf-16') as f:
                content = f.read()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {file_path}")
        except:
            # Try other encodings
            try:
                with open(file_path, 'r', encoding='utf-16-le') as f:
                    content = f.read()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed: {file_path}")
            except:
                print(f"❌ Could not fix: {file_path}")

# Fix all Python files in app folder
print("🔍 Scanning for Python files...")

for root, dirs, files in os.walk('app'):
    for file in files:
        if file.endswith('.py'):
            fix_encoding(os.path.join(root, file))

# Fix run.py
if os.path.exists('run.py'):
    fix_encoding('run.py')

print("\n🎉 All files fixed successfully!")