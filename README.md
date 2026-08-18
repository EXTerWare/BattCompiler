# BattCompiler

An automation utility that compiles Windows Batch files (`.bat` / `.cmd`) into standalone executable (`.exe`) files. 

It works by cleanly wrapping your batch script execution inside an isolated, temporary Python routine and compiling it with PyInstaller under the hood.

## Features
- **Zero-Configuration Bundling**: Generates true, standalone single-file executables (`--onefile`).
- **Auto-Dependency Handling**: Automatically ensures PyInstaller is available on the machine.
- **Custom Icons**: Supports custom `.ico` file embedding for personalized branding.
- **Auto-Cleanup**: Safely purges intermediate spec files and build directories on finish.

## Installation
Install `BattCompiler` globally via `pip`:
```bash
pip install BattCompiler
```

## Usage
Once installed, the global terminal shortcut `battc` becomes active on your system.

### Basic Compilation
Pass your target batch file using the `--file:` parameter:
```bash
battc --file:my_script.bat
```

### Adding a Custom Icon
You can pass a custom Windows icon file using the `--icon:` flag:
```bash
battc --file:my_script.bat --icon:assets/favicon.ico
```

### Debug Logging
To view real-time compilation footprints and PyInstaller runtime traces, append the `--debug` parameter:
```bash
battc --file:my_script.bat --debug
```
