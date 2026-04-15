import subprocess
import sys

def run_test_module(name):
    print(f"\n🚀 Executing: {name}...")
    # Get absolute path to the venv python
    python_exe = sys.executable 
    
    result = subprocess.run([python_exe, f"tests/{name}"], capture_output=False)
    return result.returncode == 0

def main():
    print("="*60)
    print("🌟 TEAM PORTAL BACKEND - PRODUCTION TEST SUITE")
    print("="*60)

    modules = [
        "test_organizations.py",
        "test_users.py",
        "test_audit.py"
    ]

    success_count = 0
    for mod in modules:
        if run_test_module(mod):
            success_count += 1
        else:
            print(f"⚠️ MODULE {mod} FAILED!")

    print("\n" + "="*60)
    print(f"📊 FINAL REPORT: {success_count}/{len(modules)} Modules Passed")
    print("="*60)

    if success_count == len(modules):
        print("🏆 ALL SYSTEMS NOMINAL - PRODUCTION READY")
        sys.exit(0)
    else:
        print("🛑 SYSTEM UNSTABLE - FIX DETECTED ISSUES")
        sys.exit(1)

if __name__ == "__main__":
    main()
