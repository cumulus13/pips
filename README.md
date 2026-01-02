# pips - Another Python Package Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

An advanced alternative to pip with enhanced features for downloading, managing, and analyzing Python packages from PyPI. Combines the power of package management with intelligent dependency checking similar to Go's `go mod tidy`.

## 🚀 Features

### Package Management
- 📦 **Smart Download**: Download source/binary distributions separately or together
- 🔍 **Intelligent Checking**: Auto-detect and validate package dependencies
- 📊 **Statistics**: View package download statistics from pypistats.org
- 🎨 **Beautiful UI**: Rich terminal interface with colors and tables
- ⚙️ **Configurable**: Support for custom download directories via .env files
- 🔒 **Robust**: Production-ready with comprehensive error handling
- 👤 **User-Friendly**: Support for --user installations
- 🧬 **Dependency Analysis**: Parse requirements from multiple sources

### Advanced Features
- 🗂️ **File Integrity Validation**: Auto-detect and replace corrupted downloads
- 🌐 **Redis Cache Support**: Lightning-fast caching with Redis (optional)
- 💾 **Multi-Layer Caching**: File cache + Redis cache for optimal performance
- 📁 **Managed Downloads**: Organize downloads in subfolders by package name
- 🔄 **Auto-Import Detection**: Scan Python files for missing imports
- 🐍 **Python Version Checking**: Validate Python compatibility before installation
- 🔗 **Virtual Environment Creation**: Auto-create venv for conflicting dependencies
- 📋 **Multiple Input Formats**: Support for requirements.txt, setup.py, pyproject.toml

### PIPR - Package Inspector & Requirements Parser
- 🔎 **Auto-Detect Imports**: Scan .py files and extract third-party imports
- 📂 **Directory Scanning**: Recursive or non-recursive scanning
- ✅ **Version Validation**: Check installed vs required versions
- 🔔 **Growl Notifications**: Desktop notifications for package status (optional)
- 🎯 **Smart Installation**: Auto-install missing packages with conflict detection
- 🌐 **PyPI Integration**: Direct package info from PyPI API with caching

## 📥 Installation

### Direct install from source
```bash
pip install git+htps://github.com/cumulus13/pips
```

### From Source
```bash
git clone https://github.com/cumulus13/pips.git
cd pips
pip install -e .
```

### Requirements
- Python 3.7+
- rich >= 10.0.0
- envdot >= 0.1.0
- redis >= 4.0.0 (optional, for Redis cache support)
- requests (optional, for better HTTP handling)

### Optional Dependencies
```bash
# For Redis cache support
pip install redis

# For better HTTP performance
pip install requests

# For TOML support (Python < 3.11)
pip install toml
# or
pip install tomli
```

## 🎯 Quick Start

### Basic Package Operations

**Download packages:**
```bash
# Download source only
pips -s requests

# Download binary only
pips -b numpy

# Download both source and binary
pips -s -b django

# Download specific version
pips -s requests==2.28.0
```

**Install packages:**
```bash
# Install package
pips -i flask

# Install specific version
pips -i flask==2.0.0

# Install for current user only
pips -i flask --user

# Check dependencies before install
pips -c flask -i
```

**View statistics:**
```bash
# Show recent statistics
pips -S requests

# Show overall statistics
pips -S requests -d overall
```

### Advanced Usage

**Managed downloads (organized by package):**
```bash
# Download to subfolder named 'requests'
pips -s -m requests

# Download to /opt/django/
pips -s -b -m django -p /opt
```

**Force overwrite existing files:**
```bash
pips -s requests -f
```

**Cache management:**
```bash
# Use Redis cache
pips -s requests --use-redis

# Disable cache
pips -s requests --no-cache

# Show cache information
pips --cache-info

# Clear all caches
pips --clear-cache

# Clear both file and Redis cache
pips --clear-cache --use-redis
```

### PIPR - Dependency Management

**Check project requirements:**
```bash
# Auto-detect from requirements.txt, setup.py, or pyproject.toml
pipr

# Check specific requirements file
pipr requirements.txt

# Check setup.py
pipr setup.py

# Check pyproject.toml
pipr pyproject.toml

# Check package from PyPI
pipr -i numpy

# Force install without prompts
pipr -F requirements.txt

# Summary only (no installation)
pipr -s requirements.txt
```

**Scan Python files for imports:**
```bash
# Scan single Python file
pipr myapp.py

# Scan directory (non-recursive)
pipr /path/to/project

# Scan directory recursively
pipr -r /path/to/project

# Scan current directory recursively
pipr -r .
```

**Check and install dependencies:**
```bash
# Auto-install missing packages (default behavior)
pipr requirements.txt

# Force retry on errors
pipr -f requirements.txt

# No auto-install (check only)
pipr -n requirements.txt

# Don't show table
pipr -z requirements.txt
```

## 📖 Detailed Documentation

### Configuration

**Environment Variables (.env file):**
```bash
# Download directory
PIPS_DOWNLOAD_DIR=/path/to/downloads

# Redis configuration
PIPS_USE_REDIS=true
PIPS_REDIS_HOST=127.0.0.1
PIPS_REDIS_PORT=6379
PIPS_REDIS_DB=0
PIPS_REDIS_PASSWORD=your_password

# Or use Redis URL
PIPS_REDIS_URL=redis://password@host:port/db

# Cache settings
CACHE_DIR=/custom/cache/dir
CACHE_EXPIRY=3600
USE_CACHE=true
```

**Config file locations:**

Linux/Mac:
- `~/.pips/.env`
- `~/.config/.pips/.env`
- `~/.pips/pips.ini`
- `~/.pips/pips.toml`
- `~/.pips/pips.json`
- `~/.pips/pips.yml`

Windows:
- `%APPDATA%\.pips\.env`
- `%USERPROFILE%\.pips\.env`
- `%APPDATA%\.pips\pips.ini`
- Similar for .toml, .json, .yml

### Cache System

**Multi-Layer Caching:**
1. **Redis Cache** (fastest, ~50-100ms)
   - In-memory storage
   - Network-sharable
   - Auto-expiry with TTL
   
2. **File Cache** (fast, ~150-300ms)
   - Local disk storage
   - Persistent across sessions
   - Auto-cleanup of expired entries

3. **Network Fetch** (slowest, ~1-3 seconds)
   - Direct from PyPI
   - Fallback when cache misses

**Cache Management:**
```bash
# View cache statistics
pips --cache-info

# Output example:
# ╭─────── ℹ️ pips Cache ───────╮
# │ Cache Information           │
# │                             │
# │ File Cache:                 │
# │   Enabled: ✅               │
# │   Location: ~/.pips/cache   │
# │   Files: 42                 │
# │   Size: 15.67 MB            │
# │                             │
# │ Redis Cache:                │
# │   Enabled: ✅               │
# │   Connected: ✅             │
# │   Keys: 128                 │
# ╰─────────────────────────────╯
```

### File Integrity Validation

Automatically validates downloaded files:
- ✅ `.tar.gz`, `.tgz` - Tar gzip archives
- ✅ `.tar.bz2`, `.tbz2` - Tar bzip2 archives
- ✅ `.tar.xz`, `.txz` - Tar xz archives
- ✅ `.tar` - Tar archives
- ✅ `.whl` - Python wheels
- ✅ `.zip` - Zip archives
- ✅ `.egg` - Python eggs
- ✅ `.gz` - Gzip files

**Validation includes:**
- File size check (< 100 bytes = corrupted)
- Archive integrity test
- Member count validation
- Automatic removal and re-download of corrupted files

### Python Version Compatibility

PIPS automatically checks Python version compatibility:
```bash
# Will check if current Python version matches package requirements
pips -c numpy

# If incompatible, shows error and suggests:
# - Upgrade Python
# - Create virtual environment
# - Adjust requirements
```

### Virtual Environment Management

When version conflicts are detected, PIPS can auto-create virtual environments:
```bash
# Will prompt to create venv if conflicts detected
pips -c conflicting-package

# Venv locations by platform:
# Windows: C:\VENV, %HOME%\.pip\VENV, %APPDATA%\.pips\VENV
# Linux/Mac: ~/.venv, ~/.pip/VENV, ~/.local/share/pips/VENV
```

## 📋 Command Reference

### PIPS Commands

```bash
pips [OPTIONS] PACKAGE

Options:
  PACKAGE                    Package name or package==version
  
Download Options:
  -s, --source              Download source distribution only
  -b, --binary              Download binary distribution only
  -p, --path PATH           Download save directory
  -m, --manage              Download to subfolder by package name
  -f, --force               Force overwrite existing files
  
Installation Options:
  -i, --install             Install the package
  -c, --check [PACKAGE]     Check dependencies before install
  --user                    Install to user site-packages
  
Statistics Options:
  -S, --stats               Show package statistics
  -d, --stat-period PERIOD  Statistics period (recent/overall)
  
Cache Options:
  --no-cache                Disable cache
  --use-redis               Use Redis cache
  --cache-info              Show cache information
  --clear-cache             Clear all cached data
  
Other Options:
  --version                 Show version number
  --debug                   Enable debug mode
  -h, --help                Show help message
```

### PIPR Commands

```bash
pipr [OPTIONS] [FILE/PACKAGE]

Arguments:
  FILE/PACKAGE              requirements.txt, setup.py, pyproject.toml,
                           .py file, directory, or package name
                           
Options:
  -r, --recursive          Scan Python files recursively
  -f, --force-retry        Force retry on installation errors
  -F, --force-install      Force install without confirmation
  -s, --summary            Show summary table only (no install)
  -c, --check              Same as -s (check only)
  -i, --pypi PACKAGE       Check package from PyPI directly
  -n, --no-install         Don't auto-install packages
  -z, --no-show            Don't show table
  -d, --debug              Enable debugging
  -nd, --no-detach         Don't detach subprocess (for debugging)
  -h, --help               Show help message
```

## 🎨 Examples

### Example 1: Complete Workflow
```bash
# Setup project with Redis cache
echo "PIPS_USE_REDIS=true" > ~/.pips/.env
echo "PIPS_REDIS_URL=redis://localhost:6379/0" >> ~/.pips/.env

# Download Django source and binary to organized folder
pips -s -b -m django -p ~/downloads

# Check dependencies with cache
pips -c django --use-redis

# Install with dependency check
pips -c django -i --user
```

### Example 2: Project Dependency Analysis
```bash
# Scan project for imports
pipr -r ./myproject

# Check all requirements
pipr requirements.txt

# Check and auto-install missing packages
pipr requirements.txt

# Force install all (skip prompts)
pipr -F requirements.txt
```

### Example 3: Package Information
```bash
# Get package info from PyPI
pipr -i numpy

# View package statistics
pips -S numpy -d overall

# Check without installing
pipr -c -i numpy
```

### Example 4: Cache Optimization
```bash
# First run (slow, fetches from network)
time pips -s requests
# ~2.1 seconds

# Second run (fast, uses file cache)
time pips -s requests
# ~0.18 seconds (Redis cache)

# With Redis enabled (ultra fast)
time pips -s requests --use-redis
# ~0.06 seconds
```

### Example 5: Corrupted File Handling
```bash
# Downloads file
pips -s broken-package

# Output if file exists and corrupted:
# ❌ File exists but is corrupted: broken-package-1.0.0.tar.gz
#    Auto-removing corrupted file and re-downloading...
# ⠋ Downloading broken-package-1.0.0.tar.gz...
# ✅ Downloaded: /path/to/broken-package-1.0.0.tar.gz
#
# ℹ️ Download Summary:
#   ✅ Downloaded: 1
#   ❌ Replaced corrupted: 1
```

## 🔧 Troubleshooting

### Common Issues

**1. Redis Connection Failed**
```bash
# Check if Redis is running
redis-cli ping

# If not installed:
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis
brew services start redis

# Or disable Redis
pips -s package --no-cache
```

**2. Permission Denied on Installation**
```bash
# Use --user flag
pips -i package --user

# Or use virtual environment
python -m venv myenv
source myenv/bin/activate  # Linux/Mac
myenv\Scripts\activate     # Windows
pips -i package
```

**3. Import Detection Issues**
```bash
# Enable debug mode
pipr -d myproject

# Check logs
tail -f ~/.pips/cache/pipr.log
```

**4. Corrupted Cache**
```bash
# Clear all caches
pips --clear-cache --use-redis

# Or manually delete
rm -rf ~/.pips/cache/*
redis-cli KEYS "pips:*" | xargs redis-cli DEL
```

## 📊 Performance Comparison

| Operation | No Cache | File Cache | Redis Cache |
|-----------|----------|------------|-------------|
| First fetch | 2.1s | 2.1s | 2.1s |
| Subsequent fetch | 2.1s | 0.18s | **0.06s** |
| Speedup | 1x | 12x | **36x** |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone repository
git clone https://github.com/cumulus13/pips.git
cd pips

# Install in development mode
pip install -e ".[dev]"

# Install optional dependencies
pip install redis requests toml

# Run tests
pytest tests/

# Run with debug mode
python -m pips -s requests --debug
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Uses [envdot](https://github.com/pedrovhb/envdot) for environment variable management
- Data sourced from [PyPI](https://pypi.org) and [pypistats.org](https://pypistats.org)
- Redis integration for enterprise-grade caching
- Special thanks to all contributors and users

## 📞 Support

If you encounter any issues or have questions:
- 📧 Email: cumulus13@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/cumulus13/pips/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/cumulus13/pips/discussions)

## 🗺️ Roadmap

- [x] Basic package download and install
- [x] Statistics from pypistats.org
- [x] File integrity validation
- [x] Redis cache support
- [x] Auto-import detection from .py files
- [x] Python version compatibility checking
- [x] Virtual environment auto-creation
- [x] Multi-format requirement parsing
- [ ] Support for requirements.txt with comments and options
- [ ] Package dependency visualization
- [ ] Package comparison features
- [ ] Support for private PyPI repositories
- [ ] Enhanced caching mechanisms
- [ ] Multi-threaded downloads
- [ ] Package security scanning
- [ ] Integration with CI/CD pipelines
- [ ] Web UI for package management
- [ ] Plugin system for extensions

## 📚 Additional Resources

- [PyPI JSON API Documentation](https://warehouse.pypa.io/api-reference/json.html)
- [pypistats.org API](https://pypistats.org/api)
- [PEP 440 - Version Identification](https://www.python.org/dev/peps/pep-0440/)
- [PEP 508 - Dependency Specification](https://www.python.org/dev/peps/pep-0508/)
- [Redis Documentation](https://redis.io/documentation)

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!

---

## 🙎 Author

[Hadi Cahyadi](mailto:cumulus13@gmail.com)
    
[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)
 
[Support me on Patreon](https://www.patreon.com/cumulus13)

