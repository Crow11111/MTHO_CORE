import os
import glob

def find_recent_files(directory, limit=15):
    files_with_times = []
    
    # Walk through the directory, ignore .git, .gemini, venv, etc.
    for root, dirs, files in os.walk(directory):
        if '.git' in root or '.gemini' in root or 'venv' in root or '__pycache__' in root or 'node_modules' in root:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            try:
                mtime = os.path.getmtime(file_path)
                files_with_times.append((mtime, file_path))
            except Exception:
                pass
                
    # Sort files by modification time descending
    files_with_times.sort(key=lambda x: x[0], reverse=True)
    
    print(f"--- Top {limit} recently modified files in {directory} ---")
    import datetime
    for mtime, path in files_with_times[:limit]:
        time_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        # Print path relative to directory
        rel_path = os.path.relpath(path, directory)
        print(f"[{time_str}] {rel_path}")

if __name__ == "__main__":
    find_recent_files("c:\\ATLAS_CORE")
