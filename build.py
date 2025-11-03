#!/usr/bin/env python3
"""
Build script for creating executables locally.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"⚙️  {description}")
    print(f"   Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {e}")
        print(f"   stdout: {e.stdout}")
        print(f"   stderr: {e.stderr}")
        return False

def main():
    """Main build function."""
    print("🚀 Building Weak Chess Engines")
    print("=" * 50)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        if not run_command("pip install pyinstaller", "Installing PyInstaller"):
            return False
    
    # Create output directory
    output_dir = Path("release")
    if output_dir.exists():
        print(f"🗂️  Cleaning existing release directory...")
        shutil.rmtree(output_dir)
    output_dir.mkdir()
    
    # Engine scripts to build
    engines = [
        ("scripts/random_engine.py", "random_engine"),
        ("scripts/alphabetical_engine.py", "alphabetical_engine"),
        ("scripts/reverse_alphabetical_engine.py", "reverse_alphabetical_engine"),
        ("scripts/pi_engine.py", "pi_engine"),
        ("scripts/euler_engine.py", "euler_engine"),
        ("scripts/suicide_king_engine.py", "suicide_king_engine"),
        ("scripts/blunder_engine.py", "blunder_engine"),
        ("scripts/greedy_capture_engine.py", "greedy_capture_engine"),
        ("scripts/shuffle_engine.py", "shuffle_engine"),
        ("scripts/anti_positional_engine.py", "anti_positional_engine"),
        ("scripts/color_square_engine.py", "color_square_engine"),
        ("scripts/opposite_color_square_engine.py", "opposite_color_square_engine"),
        ("scripts/swarm_engine.py", "swarm_engine"),
        ("scripts/runaway_engine.py", "runaway_engine"),
        ("scripts/huddle_engine.py", "huddle_engine"),
        ("scripts/mirror_y_engine.py", "mirror_y_engine"),
        ("scripts/mirror_x_engine.py", "mirror_x_engine"),
        ("scripts/reverse_start_engine.py", "reverse_start_engine"),
        ("scripts/CCCP_engine.py", "CCCP_engine"),
        ("scripts/passafist_engine.py", "passafist_engine"),
        ("scripts/single_player_engine.py", "single_player_engine"),
        ("scripts/strangler_engine.py", "strangler_engine"),
        ("scripts/mover_engine.py", "mover_engine"),
        ("scripts/opening_book_engine.py", "opening_book_engine"),
        ("scripts/rare_opening_book_engine.py", "rare_opening_book_engine"),
        ("scripts/lawyer_engine.py", "lawyer_engine"),
        ("scripts/criminal_engine.py", "criminal_engine"),
        ("scripts/paralegal_engine.py", "paralegal_engine")
    ]
    
    successful_builds = 0
    total_engines = len(engines)
    
    for script_path, engine_name in engines:
        print(f"\n🔨 Building {engine_name}")
        print("-" * 30)
        
        # Check if script exists
        if not Path(script_path).exists():
            print(f"❌ Script not found: {script_path}")
            continue
        
        # Build command
        cmd = f"pyinstaller --onefile --distpath release --name {engine_name} {script_path}"
        
        if run_command(cmd, f"Building {engine_name}"):
            successful_builds += 1
            
            # Check if executable was created
            if sys.platform == "win32":
                exe_path = output_dir / f"{engine_name}.exe"
            else:
                exe_path = output_dir / engine_name
            
            if exe_path.exists():
                file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
                print(f"   📦 Executable created: {exe_path} ({file_size:.1f} MB)")
            else:
                print(f"   ⚠️  Warning: Executable not found at expected location")
    
    # Clean up PyInstaller temporary files
    for temp_dir in ["build", "dist"]:
        if Path(temp_dir).exists():
            print(f"🧹 Cleaning up {temp_dir}/")
            shutil.rmtree(temp_dir)
    
    # Remove .spec files
    for spec_file in Path(".").glob("*.spec"):
        print(f"🧹 Removing {spec_file}")
        spec_file.unlink()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Build Summary")
    print("=" * 50)
    print(f"✅ Successful builds: {successful_builds}/{total_engines}")
    
    if successful_builds > 0:
        print(f"📁 Executables location: {output_dir.absolute()}")
        print("\n📋 Built engines:")
        for exe_file in output_dir.iterdir():
            if exe_file.is_file():
                file_size = exe_file.stat().st_size / (1024 * 1024)  # MB
                print(f"   • {exe_file.name} ({file_size:.1f} MB)")
    
    if successful_builds == total_engines:
        print("\n🎉 All engines built successfully!")
        print("\n💡 Usage:")
        print("   1. Copy the executables to your chess GUI engines folder")
        print("   2. Register them as UCI engines in your chess software")
        print("   3. Enjoy playing against weak opponents!")
    else:
        print(f"\n⚠️  {total_engines - successful_builds} engines failed to build")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)