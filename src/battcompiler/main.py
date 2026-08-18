"""
Automatically Convert a Batch file to EXE using PyInstaller
"""

import subprocess
import sys
import time
import shutil
import os
from pathlib import Path

# Set the Python Executable variable
python = sys.executable

# Function to only print logs if Debug mode is on.
def printf(prv):
    if "--debug" in sys.argv:
        prefix = f"[{time.strftime('%H:%M:%S')}] [{Path(sys.argv[0]).name}]: "
        print(f"{prefix}{prv}")

# Compile the bat file
def compile_file(batfil, bat_file_path, original_bat_path):
    printf(f"Starting compilation of {batfil}")

    # Get absolute path of the batch file
    original_bat_abs = Path(original_bat_path).resolve()
    printf(f"Absolute batch path: {original_bat_abs}")

    if not original_bat_abs.is_file():
        print(f"Error: Batch file not found at {original_bat_abs}")
        return

    # Build PyInstaller command
    command = [
        python,
        "-m",
        "PyInstaller",
        "--onefile",
        "--noconfirm"
    ]

    # Bundle the batch file inside the EXE
    if os.name == 'nt':  # Windows
        add_data = f"{original_bat_abs};."
    else:  # Linux/Mac
        add_data = f"{original_bat_abs}:."
    command.append(f"--add-data={add_data}")
    printf(f"Added data: {add_data}")

    # Check for icon argument
    if icon_arg := next((arg for arg in sys.argv if arg.lower().startswith("--icon:")), None):
        logo_path = icon_arg.split(":", 1)[1]
        logo_path = Path(logo_path).resolve()
        printf(f"Icon path: {logo_path}")

        if not logo_path.is_file():
            print(f"Error: Icon file not found: {logo_path}")
            return

        if not logo_path.suffix.lower() == ".ico":
            print("Error: PyInstaller requires a true .ico file. Please convert this image first.")
            return

        printf("Using custom icon.")
        command.append(f"--icon={logo_path}")
    else:
        printf("No icon provided. Compiling with default Windows icon.")

    # Add temporary Python file
    command.append(".temp/bat.py")
    printf(f"Running command: {' '.join(map(str, command))}")

    # Run PyInstaller - SUPPRESS all output unless --debug
    if "--debug" in sys.argv:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        pyinstaller_output = []
        for line in process.stdout:
            pyinstaller_output.append(line)
            printf(line.rstrip())
        exit_code = process.wait()
        if exit_code != 0:
            print("\nError: PyInstaller failed to compile the program.")
            print(f"PyInstaller exit code: {exit_code}")
            print("".join(pyinstaller_output))
            return
    else:
        # SILENT mode - no output unless something fails
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print("Error: PyInstaller failed to compile the program.")
            print(result.stderr)
            return

    # Check that PyInstaller actually created the EXE
    generated_exe = Path("dist/bat.exe")
    if not generated_exe.is_file():
        print("Error: PyInstaller finished, but dist/bat.exe was not found.")
        return

    # Final EXE path relative to the input file
    final_exe = bat_file_path.with_name(f"{bat_file_path.stem}.exe")

    # Replace existing output if necessary
    if final_exe.exists():
        printf(f"Removing existing output: {final_exe}")
        final_exe.unlink()

    # Move EXE beside the original BAT
    generated_exe.replace(final_exe)

    # Only print success message (users need to know where the EXE is)
    print(f"\n✅ Compiled: {final_exe}")

    printf("Cleaning temporary files.")
    Path(".temp/bat.py").unlink(missing_ok=True)
    Path("bat.spec").unlink(missing_ok=True)
    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree(".temp", ignore_errors=True)
    shutil.rmtree("dist", ignore_errors=True)
    printf("Cleanup complete.")

# Function to convert batch to executable
def convertBatchtoEXE(batfile, bat_file_path):
    file_path = Path(".temp/bat.py")
    printf("Creating temporary Python file")

    # Get the batch filename only (for bundling)
    batch_filename = bat_file_path.name
    printf(f"Batch filename: {batch_filename}")

    # WRAPPER: SILENT - only passes batch output through
    code_content = (
        f"import subprocess\n"
        f"import sys\n"
        f"import os\n"
        f"from pathlib import Path\n\n"
        f"def main():\n"
        f"    if getattr(sys, 'frozen', False):\n"
        f"        base_dir = Path(sys._MEIPASS)\n"
        f"    else:\n"
        f"        base_dir = Path(__file__).parent\n\n"
        f"    batch_file = base_dir / {batch_filename!r}\n\n"
        f"    if not batch_file.exists():\n"
        f"        sys.exit(1)\n\n"
        f"    # Run the batch file - output goes directly to console\n"
        f"    result = subprocess.run(\n"
        f"        [str(batch_file)],\n"
        f"        cwd=str(base_dir),\n"
        f"        shell=True,\n"
        f"        text=True\n"
        f"    )\n"
        f"    sys.exit(result.returncode)\n\n"
        f"if __name__ == '__main__':\n"
        f"    main()\n"
    )

    file_path.write_text(code_content, encoding="utf-8")
    printf(f"Temporary file created at {file_path}")
    
    # Pass the FULL PATH to the original batch file for bundling
    compile_file(file_path, bat_file_path, str(bat_file_path.resolve()))

# This is the entry point that project.scripts will hook into
def start():
    if file_arg := next((arg for arg in sys.argv if arg.lower().startswith("--file:")), None):
        bat_file = file_arg.split(":", 1)[1]
        batch = Path(bat_file)

        if not batch.suffix.lower() in (".bat", ".cmd"):
            print("Error: File must be a .bat or .cmd file. Exiting!")
            sys.exit(1)
            
        if not batch.is_file():
            print(f"Error: File '{bat_file}' not found.")
            sys.exit(1)

        # Create temp directory
        if not Path(".temp").is_dir():
            Path(".temp").mkdir()
            
        convertBatchtoEXE(bat_file, batch)
    else:
        print("Error: No --file argument provided. Exiting!")
        print("Usage: battc --file:script.bat [--icon:icon.ico] [--debug]")
        sys.exit(1)

# Allows you to still run it locally during development via 'python batt.py'
if __name__ == "__main__":
    start()
