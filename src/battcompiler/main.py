"""
Automatically Convert a Batch file to EXE using PyInstaller
"""

import subprocess
import sys
import time
import shutil
from pathlib import Path

# Set the Python Executable variable
python = sys.executable

# Function to only print logs if Debug mode is on.
def printf(prv):
    if "--debug" in sys.argv:
        prefix = f"[{time.strftime('%H:%M:%S')}] [{Path(sys.argv[0]).name}]: "
        print(f"{prefix}{prv}")

# Compile the bat file
def compile_file(batfil, bat_file_path):
    print("Compiling batch!")
    printf(f"Starting compilation of {batfil}")

    # Build PyInstaller command
    command = [
        python,
        "-m",
        "PyInstaller",
        "--onefile",
        "--noconfirm"
    ]

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

    # Run PyInstaller
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
        if "--debug" not in sys.argv:
            print("\nPyInstaller output:")
            print("".join(pyinstaller_output))
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

    print(f"Compilation successful! EXE created at:")
    print(final_exe)

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

    code_content = (
        f"import subprocess\n"
        f"subprocess.run({batfile!r}, shell=True, text=True)\n"
    )

    file_path.write_text(code_content, encoding="utf-8")
    printf(f"Temporary file created at {file_path}")
    compile_file(file_path, bat_file_path)

# This is the entry point that project.scripts will hook into
def start():
    if file_arg := next((arg for arg in sys.argv if arg.lower().startswith("--file:")), None):
        bat_file = file_arg.split(":", 1)[1]
        batch = Path(bat_file)

        if bat_file.lower().endswith((".bat", ".cmd")):
            if batch.is_file():
                print("The file exists!")
                if not Path(".temp").is_dir():
                    Path(".temp").mkdir()
                convertBatchtoEXE(bat_file, batch)
            else:
                print("Error: File not found.")
                sys.exit(1)
        else:
            print("Error: File must be a .bat or .cmd file. Exiting!")
            sys.exit(1)
    else:
        print("Error: No --file argument provided. Exiting!")
        sys.exit(1)

# Allows you to still run it locally during development via 'python batt.py'
if __name__ == "__main__":
    start()
