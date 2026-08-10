# Bootstrap Scripts

Three equivalent scripts are provided to create the repository directory structure.

## Linux / macOS

```bash
chmod +x create_structure.sh
./create_structure.sh
```

Custom directory:

```bash
./create_structure.sh my-repository
```

## Windows PowerShell

```powershell
.\create_structure.ps1
```

Custom directory:

```powershell
.\create_structure.ps1 -Root "my-repository"
```

If PowerShell execution policy blocks the script:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\create_structure.ps1
```

## Python

```bash
python create_structure.py
```

Custom directory:

```bash
python create_structure.py my-repository
```
