## Python

### macOS

```
brew install python@3.13
brew install python-tk@3.13
```

### MS Windows

* Installer for Python 3.13 is [here](https://www.python.org/ftp/python/3.13.14/python-3.13.14-amd64.exe).
* Select a local installation and to have `PATH` updated.

---

## `podman` virtualised environment

### macOS

* Install latest release of `podman` from https://github.com/podman-container-tools/podman/releases

```bash
podman machine init
podman machine start
```

```bash
brew install docker-compose
brew install docker-credential-helper
```

### MS Windows

* Ensure system BIOS has virtualization enabled.
* Install WSL 2: `wsl --install` and `wsl --set-default-version 2`

* Use WindowsTerminal: `winget install Microsoft.WindowsTerminal` to install.

* Install latest release of `podman` from https://github.com/podman-container-tools/podman/releases

```bash
podman machine init
podman machine start
```

* Restart terminal to get changed path.

```bash
python --version  # Check version is 3.13
python -m pip install podman-compose
```

* Create `C:\Users\USER\.config\containers\auth.json`

```json
{
  "credHelpers": {
    "docker.io": "wincred"
  }
}
```

---

## Get image

```bash
podman pull dbrnz/flatmap-author:latest
```

Otherwise will be pulled when container first started.
