## 0.7.3
* Add support for Python 3.14

## 0.7.2
* Add uv version to status bar

## 0.7.1
* Fix bug when first Python version is removed from the list

## 0.7.0
* Create symbolic link from real virtual environment
* Make new virtual environment based on uv python list

## 0.6.2
* Show number of installed packages during sync

* ## 0.6.1
* Make window bigger at start

## 0.6.0
* add button to sync venv based on `.venvflon.yaml'
* Show total time of synchronization on button itself
* resize widgets with mian window

## 0.5.1
* Manually include Tkinter libraries is not needed
* Remove a symbolic link only when it exists

## 0.5.0
* add drag and drop to cwd entry
* make flon GUI more nicer

## 0.4.1
* Update statusbar when change cwd

## 0.4.0
* Select at the start current venv which symlink point to

## 0.3.3
* Show output or error in statusbar
* Fix handling cwd without any venv

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
