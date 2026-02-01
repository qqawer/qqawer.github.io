import os
import time
import subprocess
import sys

# Configuration
WATCH_DIR = "content"
POLL_INTERVAL = 3  # Seconds between checks
DEBOUNCE_DELAY = 5 # Seconds to wait after a change before pushing (to group edits)

def get_file_states(directory):
    """Returns a dict of filename: mtime for all files in directory recursively."""
    file_states = {}
    for root, _, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            try:
                mtime = os.stat(path).st_mtime
                file_states[path] = mtime
            except FileNotFoundError:
                pass
    return file_states

def git_push():
    """Executes git add, commit, and push."""
    print(f"\n[Auto-Push] Changes detected. Preparing to push...")
    try:
        # Check if there are changes to commit
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout.strip():
            print("[Auto-Push] No git changes detected. Skipping.")
            return

        print("[Auto-Push] Adding files...")
        subprocess.run(["git", "add", "."], check=True)
        
        print("[Auto-Push] Committing...")
        subprocess.run(["git", "commit", "-m", "Auto-update content: Detected changes"], check=True)
        
        print("[Auto-Push] Pushing to remote...")
        subprocess.run(["git", "push"], check=True)
        print("[Auto-Push] Successfully pushed!")
        
    except subprocess.CalledProcessError as e:
        print(f"[Auto-Push] Error executing git command: {e}")

def main():
    print(f"[Auto-Push] Monitoring '{WATCH_DIR}' for changes...")
    
    # Initial state
    last_states = get_file_states(WATCH_DIR)
    
    while True:
        try:
            time.sleep(POLL_INTERVAL)
            current_states = get_file_states(WATCH_DIR)
            
            # Check for changes
            changed = False
            
            # 1. content modified or new files
            if current_states != last_states:
                changed = True
                
            if changed:
                print(f"[Auto-Push] Change detected! Waiting {DEBOUNCE_DELAY}s for file operations to settle...")
                time.sleep(DEBOUNCE_DELAY)
                # Update state before pushing to avoid loops if git changes mtime (unlikely for source files)
                last_states = get_file_states(WATCH_DIR) 
                git_push()
                # Re-snapshot after push just in case
                last_states = get_file_states(WATCH_DIR)
                print(f"[Auto-Push] Resuming monitoring...")
                
        except KeyboardInterrupt:
            print("\n[Auto-Push] Stopped.")
            sys.exit(0)
        except Exception as e:
            print(f"[Error] {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    if not os.path.exists(WATCH_DIR):
        print(f"Error: Directory '{WATCH_DIR}' not found.")
        sys.exit(1)
        
    # Ensure runs from project root
    if not os.path.isdir(".git"):
        print("Warning: .git directory not found. Make sure you are in the project root.")
    
    main()
