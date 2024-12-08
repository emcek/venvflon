## 0.3.2
* fix parsing cli arguments
* fix crashing when starting

## 0.3.1
* increase timer for creating symlink with PowerShell5 to 1.2 sec
* add `-t` and `--timer` cli parameter to specify sleeping timer form pwsh5 and pwsh7 option
* add more unit tests

## 0.3.0
* Change cli argument (`-p` or `--pwsh`) as triple choice `0`, `5`, `7` to use **Python**, **PowerShell5** or **PowerShell7** respectively to create symbolic link
* Fix unlink for Python
* Status bar show correct current Python selected
* When change cwd show it in tittle

## 0.2.0
* Changing current working directory during running
* Add cli argument (`-p` or `--py`) to use Python to create symbolic link
* Add SECURITY information

## 0.1.0
* First beta release
