#!/usr/bin/env python3

# File: pips.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2026-01-01
# Description: pips - Another Python Package Manager, A robust alternative to pip with enhanced features for downloading and managing Python packages.
# License: MIT

"""
pips - Another Python Package Manager
A robust alternative to pip with enhanced features for downloading and managing Python packages.
"""

import sys
import os
import traceback

tprint = None  # type: ignore

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

if len(sys.argv) > 1 and any('--debug' == arg for arg in sys.argv):
    print("🐞 Debug mode enabled [GitDate]")
    os.environ["DEBUG"] = "1"
    os.environ['LOGGING'] = "1"
    os.environ.pop('NO_LOGGING', None)
    os.environ['TRACEBACK'] = "1"
    os.environ["LOGGING"] = "1"
    LOG_LEVEL = "DEBUG"
    
elif str(os.getenv('DEBUG', '0')).lower() in ['1', 'true', 'ok', 'on', 'yes']:
    print("🐞 Debug mode enabled [GitDate]")
    os.environ['LOGGING'] = "1"
    os.environ.pop('NO_LOGGING', None)
    os.environ['TRACEBACK'] = "1"
    os.environ["LOGGING"] = "1"
    LOG_LEVEL = "DEBUG"
else:
    os.environ['NO_LOGGING'] = "1"

    def debug(*args, **kwargs):
        pass

exceptions = ['requests']

try:
    from richcolorlog import setup_logging, print_exception as tprint  # type: ignore
    logger = setup_logging('pips', exceptions=exceptions, level=LOG_LEVEL, log_file=True, log_file_name='pips.log')
except:
    import logging

    for exc in exceptions:
        logging.getLogger(exc).setLevel(logging.CRITICAL)
    
    try:
        from .custom_logging import get_logger  # type: ignore
    except ImportError:
        from custom_logging import get_logger  # type: ignore
        
    LOG_LEVEL = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    logger = get_logger('pips', level=LOG_LEVEL)

logger.debug("finish load richcolorlog")

if not tprint:
    def tprint(*args, **kwargs):
        traceback.print_exc()

import argparse
try:
    from licface import CustomRichHelpFormatter
except:
    CustomRichHelpFormatter = argparse.RawDescriptionHelpFormatter
import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import urllib.parse
import tarfile
import zipfile
import gzip
import hashlib
import time
import pickle

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, SpinnerColumn
    from rich.panel import Panel
    from rich import box
except ImportError:
    print("Error: 'rich' library is required. Install it with: pip install rich")
    logger.error("'rich' library is required. Install it with: pip install rich")
    sys.exit(1)

try:
    from envdot import load_env  # type: ignore
except ImportError:
    print("Warning: 'envdot' not found. .env file support disabled.")
    logger.warning("'envdot' not found. .env file support disabled.")
    load_env = None

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    from .pipr import PIPR  # type: ignore
except:
    from pipr import PIPR  # type: ignore


from pypi_info import PackageInfoDisplay  # type: ignore

console = Console()

def get_config_file():
    config_file = None
    if sys.platform == 'win32':
        config_file_list = [
            Path(os.path.expandvars('%APPDATA%')) / '.pips' / Path('.env'),
            Path(os.path.expandvars('%USERPROFILE%')) / '.pips' / Path('.env'),

            Path(os.path.expandvars('%APPDATA%')) / '.pips' / f"{Path(__file__).stem}.ini",
            Path(os.path.expandvars('%USERPROFILE%')) / '.pips' / f"{Path(__file__).stem}.ini",

            Path(os.path.expandvars('%APPDATA%')) / '.pips' / f"{Path(__file__).stem}.toml",
            Path(os.path.expandvars('%USERPROFILE%')) / '.pips' / f"{Path(__file__).stem}.toml",

            Path(os.path.expandvars('%APPDATA%')) / '.pips' / f"{Path(__file__).stem}.json",
            Path(os.path.expandvars('%USERPROFILE%')) / '.pips' / f"{Path(__file__).stem}.json",

            Path(os.path.expandvars('%APPDATA%')) / '.pips' / f"{Path(__file__).stem}.yml",
            Path(os.path.expandvars('%USERPROFILE%')) / '.pips' / f"{Path(__file__).stem}.yml",

        ]
    else:    
        config_file_list = [
            Path(os.path.expanduser('~')) / '.pips' / Path('.env'),
            Path(os.path.expanduser('~')) / '.config' / '.pips' / Path('.env'),
            Path(os.path.expanduser('~')) / '.config' / Path('.env'),

            Path(os.path.expanduser('~')) / '.pips' / f"{Path(__file__).stem}.ini",
            Path(os.path.expanduser('~')) / '.config' / '.pips' / f"{Path(__file__).stem}.ini",
            Path(os.path.expanduser('~')) / '.config' / f"{Path(__file__).stem}.ini",
            
            Path(os.path.expanduser('~')) / '.pips' / f"{Path(__file__).stem}.toml",
            Path(os.path.expanduser('~')) / '.config' / '.pips' / f"{Path(__file__).stem}.toml",
            Path(os.path.expanduser('~')) / '.config' / f"{Path(__file__).stem}.toml",
            
            Path(os.path.expanduser('~')) / '.pips' / f"{Path(__file__).stem}.json",
            Path(os.path.expanduser('~')) / '.config' / '.pips' / f"{Path(__file__).stem}.json",
            Path(os.path.expanduser('~')) / '.config' / f"{Path(__file__).stem}.json",
            
            Path(os.path.expanduser('~')) / '.pips' / f"{Path(__file__).stem}.yml",
            Path(os.path.expanduser('~')) / '.config' / '.pips' / f"{Path(__file__).stem}.yml",
            Path(os.path.expanduser('~')) / '.config' / f"{Path(__file__).stem}.yml",
            
            ]
    for cf in config_file_list:
        if cf.is_file():
            config_file = cf
            break
        
    if config_file and not config_file.parent.is_dir():
        config_file.parent.mkdir(parents=True, exist_ok=True)

    config_file = config_file or Path(__file__).parent / Path('.env')

    return config_file

def get_version():
    """
    Get the version of the ddf module.
    Version is taken from the __version__.py file if it exists.
    The content of __version__.py should be:
    version = "0.33"
    """
    try:
        version_file = Path(__file__).parent / "__version__.py"
        if version_file.is_file():
            with open(version_file, "r") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        parts = line.split("=")
                        if len(parts) == 2:
                            return parts[1].strip().strip('"').strip("'")
    except Exception as e:
        if os.getenv('TRACEBACK') and os.getenv('TRACEBACK') in ['1', 'true', 'True']:
            print(traceback.format_exc())
        else:
            print(f"ERROR: {e}")

    return "1.0.0"

def get_redis_config() -> Dict[str, Any]:
    """Get Redis configuration from config file or environment"""
    config = {
        'host': os.getenv('PIPS_REDIS_HOST', '127.0.0.1'),
        'port': int(os.getenv('PIPS_REDIS_PORT', '6379')),
        'db': int(os.getenv('PIPS_REDIS_DB', '0')),
        'password': os.getenv('PIPS_REDIS_PASSWORD', ''),
        'socket_timeout': int(os.getenv('PIPS_REDIS_TIMEOUT', '5')),
        'socket_connect_timeout': int(os.getenv('PIPS_REDIS_CONNECT_TIMEOUT', '5')),
    }
    
    # Parse Redis URL if provided (redis://user:pass@host:port/db)
    redis_url = os.getenv('PIPS_REDIS_URL', '')
    if redis_url:
        try:
            # Parse redis://[password@]host:port/db
            import re
            pattern = r'redis://(?:([^@]+)@)?([^:]+):(\d+)/(\d+)'
            match = re.match(pattern, redis_url)
            if match:
                password, host, port, db = match.groups()
                config['host'] = host
                config['port'] = int(port)
                config['db'] = int(db)
                if password:
                    config['password'] = password
                logger.debug(f"Parsed Redis URL: {host}:{port}/{db}")
        except Exception as e:
            logger.warning(f"Failed to parse Redis URL: {e}")
    
    # Remove empty password
    if not config['password']:
        config.pop('password', None)
    
    return config

class Icons:
    """Unicode icons for different message types"""
    SUCCESS = "✅ "
    ERROR = "❌ " 
    WARNING = "⚠️ "
    INFO = "ℹ️ "
    GIT = "🔧 "
    GITHUB = "🐙 "
    VERSION = "📦 "
    TAG = "🏷️ "
    REMOTE = "🌐 "
    FOLDER = "📁 "
    FILE = "📄 "
    LOCK = "🔒 "
    UNLOCK = "🔓 "
    SEARCH = "🔍 "
    CLIPBOARD = "📋 "
    CONFIG = "⚙️ "
    TIME = "⏰ "
    NOTIFICATION = "🔔 "
    DOWNLOAD = "⬇️ "
    RELEASE = "🎯 "
    USERNAME = "🙎 "
    OWNER = "🚹 "
    NODE = "📮 "
    KEY = "🔑 "
    DATE = "📅 "
    EMAIL = "📧 "
    LINK = "🔗 "
    MARK = "🔖 "
    FIND = "🔎 "
    BLOCK = "🧱 "
    COLOR = "🎨 "
    PENDING = "📧 "
    CANCEL = "⛔ "
    CHAPTER = "🎬 "
    STATS = "📈 "
    BUG = "🪲 "

class PipsError(Exception):
    """Base exception for pips errors"""
    pass

class PyPIClient:
    """Client for interacting with PyPI JSON API"""
    
    PYPI_BASE_URL = "https://pypi.org/pypi"
    PYPISTATS_BASE_URL = "https://pypistats.org/api"
    CACHE_DIR = Path.home() / '.pips' / 'cache'
    CACHE_EXPIRY = 3600  # 1 hour in seconds
    REDIS_PREFIX = "pips:"  # Redis key prefix
    
    def __init__(self, use_cache: bool = True, use_redis: bool = False):
        self.session_headers = {
            'User-Agent': 'pips/1.0.0 (Python Package Manager)',
            # 'Accept-Encoding': 'gzip, deflate',  # Enable compression
            'Connection': 'keep-alive'  # Reuse connection
        }
        self.use_cache = use_cache
        self.use_redis = use_redis and REDIS_AVAILABLE
        self.redis_client = None
        
        # Initialize Redis if enabled
        if self.use_redis:
            self._init_redis()
        
        # Initialize file cache
        if use_cache:
            self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    def _init_redis(self) -> None:
        """Initialize Redis connection"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, falling back to file cache")
            self.use_redis = False
            return
        
        try:
            redis_config = get_redis_config()
            logger.debug(f"Connecting to Redis: {redis_config.get('host')}:{redis_config.get('port')}/{redis_config.get('db')}")
            
            self.redis_client = redis.Redis(
                decode_responses=True,  # Get strings instead of bytes
                **redis_config
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"Redis connected: {redis_config.get('host')}:{redis_config.get('port')}/{redis_config.get('db')}")
            
        except redis.ConnectionError as e:
            logger.warning(f"Redis connection failed: {e}, falling back to file cache")
            self.redis_client = None
            self.use_redis = False
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}, falling back to file cache")
            self.redis_client = None
            self.use_redis = False
    
    def _get_redis_key(self, cache_key: str) -> str:
        """Get Redis key with prefix"""
        return f"{self.REDIS_PREFIX}{cache_key}"
    
    def _get_from_redis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from Redis cache"""
        if not self.use_redis or not self.redis_client:
            return None
        
        try:
            redis_key = self._get_redis_key(cache_key)
            data_str = self.redis_client.get(redis_key)
            
            if data_str:
                data = json.loads(data_str)
                logger.debug(f"Redis cache hit: {cache_key}")
                return data
            
            logger.debug(f"Redis cache miss: {cache_key}")
            return None
            
        except redis.RedisError as e:
            logger.warning(f"Redis get error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.warning(f"Redis data decode error: {e}")
            # Remove corrupted data
            try:
                self.redis_client.delete(redis_key)
            except:
                pass
            return None
        except Exception as e:
            logger.warning(f"Redis error: {e}")
            return None
    
    def _save_to_redis(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Save data to Redis cache"""
        if not self.use_redis or not self.redis_client:
            return
        
        try:
            redis_key = self._get_redis_key(cache_key)
            data_str = json.dumps(data)
            
            # Set with expiration
            self.redis_client.setex(
                redis_key,
                self.CACHE_EXPIRY,
                data_str
            )
            logger.debug(f"Redis cached: {cache_key} (TTL: {self.CACHE_EXPIRY}s)")
            
        except redis.RedisError as e:
            logger.warning(f"Redis set error: {e}")
        except Exception as e:
            logger.warning(f"Redis save error: {e}")
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for a given key"""
        # Use hash to avoid filesystem issues with special characters
        key_hash = hashlib.md5(cache_key.encode()).hexdigest()
        return self.CACHE_DIR / f"{key_hash}.cache"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from file cache if valid"""
        if not self.use_cache:
            return None
        
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        try:
            # Check if cache is expired
            cache_age = time.time() - cache_path.stat().st_mtime
            if cache_age > self.CACHE_EXPIRY:
                logger.debug(f"File cache expired for: {cache_key}")
                cache_path.unlink()
                return None
            
            # Load from cache
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            
            logger.debug(f"File cache hit for: {cache_key} (age: {cache_age:.1f}s)")
            return data
            
        except Exception as e:
            logger.warning(f"File cache read error: {e}")
            # Remove corrupted cache
            if cache_path.exists():
                cache_path.unlink()
            return None
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Save data to file cache"""
        if not self.use_cache:
            return
        
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            logger.debug(f"File cached: {cache_key}")
        except Exception as e:
            logger.warning(f"File cache write error: {e}")
    
    def _fetch_json(self, url: str, cache_key: Optional[str] = None) -> Dict[str, Any]:
        """Fetch JSON data with caching support (Redis first, then file)"""
        # Try Redis cache first (faster)
        if cache_key and self.use_redis:
            cached_data = self._get_from_redis(cache_key)
            if cached_data:
                return cached_data
        
        # Try file cache second
        if cache_key and self.use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                # Promote to Redis cache for next time
                if self.use_redis:
                    self._save_to_redis(cache_key, cached_data)
                return cached_data
        
        # Fetch from network
        try:
            request = Request(url, headers=self.session_headers)
            with urlopen(request, timeout=10) as response:  # Reduced timeout from 30 to 10
                data_response = response.read()
                logger.debug(f"response.read(): {data_response}")
                logger.debug(f"response.read().decode('utf-8'): {data_response.decode('utf-8')}")
                data = json.loads(data_response.decode('utf-8'))
            
            # Save to both caches
            if cache_key:
                if self.use_redis:
                    self._save_to_redis(cache_key, data)
                if self.use_cache:
                    self._save_to_cache(cache_key, data)
            
            return data
            
        except HTTPError as e:
            if e.code == 404:
                logger.exception(e)
                raise PipsError(f"{Icons.ERROR} Resource not found (404)")
            raise PipsError(f"{Icons.ERROR} HTTP Error {e.code}: {e.reason}")
        except URLError as e:
            logger.exception(e)
            raise PipsError(f"{Icons.ERROR} Failed to connect: {e.reason}")
        except Exception as e:
            logger.exception(e)
            raise PipsError(f"{Icons.ERROR} Fetch error: {str(e)}")
    
    def get_package_info(self, package_name: str) -> Dict[str, Any]:
        """Fetch package information from PyPI"""
        url = f"{self.PYPI_BASE_URL}/{package_name}/json"
        cache_key = f"package_info:{package_name}"
        logger.debug(f"url: {url}")
        
        try:
            return self._fetch_json(url, cache_key)
        except HTTPError as e:
            if e.code == 404:
                logger.exception(e)
                raise PipsError(f"{Icons.ERROR} Package '{package_name}' not found on PyPI")
            raise
        except Exception as e:
            logger.exception(e)
            raise

    def get_package_version(self, package_name: str, version: str) -> Dict[str, Any]:
        """Fetch specific version information from PyPI"""
        url = f"{self.PYPI_BASE_URL}/{package_name}/{version}/json"
        cache_key = f"package_version:{package_name}:{version}"
        
        try:
            return self._fetch_json(url, cache_key)
        except HTTPError as e:
            if e.code == 404:
                logger.exception(e)
                raise PipsError(f"{Icons.ERROR} Version '{version}' not found for package '{package_name}'")
            raise
        except Exception as e:
            logger.exception(e)
            raise
    
    def get_package_requirements(self, package_name: str, version: Optional[str] = None) -> List[Tuple[str, str]]:
        """Fetch package requirements from PyPI"""
        if version:
            data = self.get_package_version(package_name, version)
        else:
            data = self.get_package_info(package_name)

        try:
            info = data.get('info', {})
            requires_dist = info.get('requires_dist', [])

            deps = PackageInfoDisplay()._parse_dependencies(requires_dist)
            logger.debug(f"deps: {deps}")
            if deps and deps.get('core'):
                requirements = [(i['name'], i.get('version') if i.get('version') != 'any' else '') for i in deps.get('core')]
                return requirements
            
            return requires_dist or []
        except HTTPError as e:
            if e.code == 404:
                logger.exception(e)
                raise PipsError(f"{Icons.ERROR} Package '{package_name}' not found on PyPI")
            raise
        except Exception as e:
            logger.exception(e)
            raise

    def get_package_stats(self, package_name: str, period: str = "recent") -> Dict[str, Any]:
        """Fetch package statistics from pypistats.org"""
        url = f"{self.PYPISTATS_BASE_URL}/packages/{package_name}/{period}"
        cache_key = f"package_stats:{package_name}:{period}"
        
        try:
            return self._fetch_json(url, cache_key)
        except HTTPError as e:
            logger.exception(e)
            if e.code == 404:
                raise PipsError(f"{Icons.ERROR} Statistics not found for package '{package_name}'")
            raise
        except Exception as e:
            logger.exception(e)
            raise
    
    def clear_cache(self, clear_redis: bool = False) -> Tuple[int, int]:
        """Clear cache files and optionally Redis cache"""
        file_count = 0
        redis_count = 0
        
        # Clear file cache
        if self.CACHE_DIR.exists():
            for cache_file in self.CACHE_DIR.glob("*.cache"):
                try:
                    cache_file.unlink()
                    file_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete cache file: {e}")
        
        # Clear Redis cache
        if clear_redis and self.use_redis and self.redis_client:
            try:
                pattern = f"{self.REDIS_PREFIX}*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    redis_count = self.redis_client.delete(*keys)
                logger.info(f"Cleared {redis_count} Redis keys")
            except Exception as e:
                logger.exception(e)
                logger.warning(f"Failed to clear Redis cache: {e}")
        
        logger.info(f"Cleared {file_count} file cache(s), {redis_count} Redis cache(s)")
        return file_count, redis_count
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information"""
        info = {
            'file_cache': {
                'enabled': self.use_cache,
                'location': str(self.CACHE_DIR),
                'count': 0,
                'size_mb': 0
            },
            'redis_cache': {
                'enabled': self.use_redis,
                'connected': self.redis_client is not None,
                'count': 0
            }
        }
        
        # Count file cache
        if self.CACHE_DIR.exists():
            cache_files = list(self.CACHE_DIR.glob("*.cache"))
            info['file_cache']['count'] = len(cache_files)
            info['file_cache']['size_mb'] = sum(f.stat().st_size for f in cache_files) / (1024 * 1024)
        
        # Count Redis cache
        if self.use_redis and self.redis_client:
            try:
                pattern = f"{self.REDIS_PREFIX}*"
                keys = self.redis_client.keys(pattern)
                info['redis_cache']['count'] = len(keys)
            except Exception as e:
                logger.exception(e)
                logger.warning(f"Failed to get Redis cache info: {e}")
        
        return info

class PackageDownloader:
    """Handle package downloads"""
    
    def __init__(self, save_dir: str, manage_mode: bool = False, package_name: str = None, force_overwrite: bool = False):
        """
        Initialize downloader with save directory
        
        Args:
            save_dir: Base directory for downloads
            manage_mode: If True, create subfolder with package name
            package_name: Name of package (used when manage_mode is True)
            force_overwrite: If True, overwrite existing files without asking
        """
        self.base_dir = Path(save_dir)
        self.manage_mode = manage_mode
        self.package_name = package_name
        self.force_overwrite = force_overwrite
        
        # Determine actual save directory
        if manage_mode and package_name:
            self.save_dir = self.base_dir / package_name
            logger.debug(f"Manage mode enabled. Save dir: {self.save_dir}")
        else:
            self.save_dir = self.base_dir
            
        self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def _validate_file_integrity(self, filepath: Path) -> bool:
        """
        Validate file integrity based on file type
        
        Returns:
            bool: True if file is valid, False if corrupted
        """
        if not filepath.exists():
            return False
        
        try:
            file_ext = filepath.suffix.lower()
            file_name = filepath.name.lower()
            
            # Check if file size is suspiciously small (< 100 bytes usually means corrupted)
            if filepath.stat().st_size < 100:
                logger.warning(f"File too small (< 100 bytes), likely corrupted: {filepath}")
                return False
            
            # Validate based on file type
            if file_name.endswith('.tar.gz') or file_name.endswith('.tgz'):
                # Validate tar.gz file
                with tarfile.open(filepath, 'r:gz') as tar:
                    # Try to list members - if this fails, file is corrupted
                    members = tar.getmembers()
                    if len(members) == 0:
                        logger.warning(f"Tar.gz file has no members: {filepath}")
                        return False
                logger.debug(f"Valid tar.gz file: {filepath}")
                return True
                
            elif file_name.endswith('.tar.bz2') or file_name.endswith('.tbz2'):
                # Validate tar.bz2 file
                with tarfile.open(filepath, 'r:bz2') as tar:
                    members = tar.getmembers()
                    if len(members) == 0:
                        logger.warning(f"Tar.bz2 file has no members: {filepath}")
                        return False
                logger.debug(f"Valid tar.bz2 file: {filepath}")
                return True
                
            elif file_name.endswith('.tar.xz') or file_name.endswith('.txz'):
                # Validate tar.xz file
                with tarfile.open(filepath, 'r:xz') as tar:
                    members = tar.getmembers()
                    if len(members) == 0:
                        logger.warning(f"Tar.xz file has no members: {filepath}")
                        return False
                logger.debug(f"Valid tar.xz file: {filepath}")
                return True
                
            elif file_ext == '.tar':
                # Validate tar file
                with tarfile.open(filepath, 'r') as tar:
                    members = tar.getmembers()
                    if len(members) == 0:
                        logger.warning(f"Tar file has no members: {filepath}")
                        return False
                logger.debug(f"Valid tar file: {filepath}")
                return True
                
            elif file_ext == '.whl' or file_ext == '.zip' or file_ext == '.egg':
                # Validate wheel/zip/egg file (they're all zip archives)
                with zipfile.ZipFile(filepath, 'r') as zf:
                    # Test the zip file
                    bad_file = zf.testzip()
                    if bad_file is not None:
                        logger.warning(f"Corrupted file in archive: {bad_file}")
                        return False
                    # Check if there are any files
                    if len(zf.namelist()) == 0:
                        logger.warning(f"Zip file has no members: {filepath}")
                        return False
                logger.debug(f"Valid zip/wheel/egg file: {filepath}")
                return True
                
            elif file_ext == '.gz':
                # Validate gzip file
                with gzip.open(filepath, 'rb') as gz:
                    # Try to read first few bytes
                    gz.read(10)
                logger.debug(f"Valid gzip file: {filepath}")
                return True
                
            else:
                # For unknown file types, assume valid if file exists and has size > 100 bytes
                logger.debug(f"Unknown file type, assuming valid: {filepath}")
                return True
                
        except tarfile.TarError as e:
            logger.warning(f"Invalid tar file: {filepath} - {str(e)}")
            return False
        except zipfile.BadZipFile as e:
            logger.warning(f"Invalid zip/wheel file: {filepath} - {str(e)}")
            return False
        except gzip.BadGzipFile as e:
            logger.warning(f"Invalid gzip file: {filepath} - {str(e)}")
            return False
        except EOFError as e:
            logger.warning(f"Truncated/corrupted file: {filepath} - {str(e)}")
            return False
        except Exception as e:
            logger.warning(f"Error validating file: {filepath} - {str(e)}")
            # If we can't validate, assume corrupted to be safe
            return False
    
    def _get_unique_filename(self, filepath: Path) -> Path:
        """Generate unique filename if file exists"""
        if not filepath.exists():
            return filepath
        
        base = filepath.stem
        ext = filepath.suffix
        parent = filepath.parent
        counter = 1
        
        while True:
            new_filepath = parent / f"{base}_{counter}{ext}"
            if not new_filepath.exists():
                return new_filepath
            counter += 1
    
    def _handle_existing_file(self, filepath: Path) -> Tuple[bool, Path]:
        """
        Handle existing file
        
        Returns:
            tuple: (should_download, final_filepath)
                - should_download: True if file should be downloaded
                - final_filepath: Path where file should be saved
        """
        if not filepath.exists():
            return True, filepath
        
        # Check file integrity first
        is_valid = self._validate_file_integrity(filepath)
        
        if not is_valid:
            console.print(f"\n{Icons.ERROR} [bold red]File exists but is corrupted:[/bold red] {filepath.name}")
            console.print(f"   [yellow]Auto-removing corrupted file and re-downloading...[/yellow]")
            logger.warning(f"Corrupted file detected, auto-removing: {filepath}")
            try:
                filepath.unlink()
            except Exception as e:
                logger.error(f"Failed to remove corrupted file: {e}")
                raise PipsError(f"{Icons.ERROR} Failed to remove corrupted file: {str(e)}")
            return True, filepath
        
        # File is valid, check force overwrite
        if self.force_overwrite:
            logger.info(f"Force overwrite enabled. Removing valid file: {filepath}")
            filepath.unlink()
            return True, filepath
        
        # Get file size for display
        file_size = filepath.stat().st_size
        size_mb = file_size / (1024 * 1024)
        
        console.print(f"\n{Icons.INFO} [bold cyan]File already exists (valid):[/bold cyan] {filepath.name}")
        console.print(f"{Icons.FILE} [dim]Size: {size_mb:.2f} MB[/dim]")
        console.print(f"\n{Icons.CONFIG} Options:")
        console.print("  [cyan]s[/cyan] - Skip this file")
        console.print("  [cyan]o[/cyan] - Overwrite existing file")
        console.print("  [cyan]r[/cyan] - Rename and keep both files")
        console.print("  [cyan]a[/cyan] - Overwrite all (don't ask again)")
        
        while True:
            try:
                choice = console.input("\n[bold cyan]Choose action [s/o/r/a]:[/bold cyan] ").lower().strip()
                
                if choice == 's':
                    console.print(f"{Icons.INFO} [yellow]Skipped:[/yellow] {filepath.name}")
                    logger.info(f"Skipped existing file: {filepath}")
                    return False, filepath
                
                elif choice == 'o':
                    logger.info(f"Overwriting file: {filepath}")
                    filepath.unlink()
                    return True, filepath
                
                elif choice == 'r':
                    new_filepath = self._get_unique_filename(filepath)
                    console.print(f"{Icons.INFO} [cyan]New filename:[/cyan] {new_filepath.name}")
                    logger.info(f"Renamed to: {new_filepath}")
                    return True, new_filepath
                
                elif choice == 'a':
                    self.force_overwrite = True
                    logger.info("Force overwrite all enabled")
                    filepath.unlink()
                    return True, filepath
                
                else:
                    console.print(f"{Icons.WARNING} [red]Invalid choice. Please enter s, o, r, or a[/red]")
                    
            except KeyboardInterrupt:
                console.print(f"\n{Icons.CANCEL} [yellow]Skipping file...[/yellow]")
                return False, filepath
    
    def download_file(self, url: str, filename: str) -> Optional[Path]:
        """Download a file with progress bar"""
        filepath = self.save_dir / filename
        
        # Handle existing file
        should_download, final_filepath = self._handle_existing_file(filepath)
        
        if not should_download:
            return None
        
        try:
            request = Request(url, headers={'User-Agent': 'pips/1.0.0'})
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                console=console
            ) as progress:
                
                with urlopen(request, timeout=60) as response:
                    total_size = int(response.headers.get('Content-Length', 0))
                    
                    task = progress.add_task(
                        f"[bold #00FFFF]Downloading {final_filepath.name}...",
                        total=total_size
                    )
                    
                    with open(final_filepath, 'wb') as f:
                        while True:
                            chunk = response.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                            progress.update(task, advance=len(chunk))
            
            console.print(f"{Icons.SUCCESS} [bold #FFFF00]Downloaded[/]: {final_filepath}")
            logger.info(f"Downloaded: {final_filepath}")
            return final_filepath
            
        except Exception as e:
            if final_filepath.exists():
                final_filepath.unlink()
            logger.exception(e)
            raise PipsError(f"{Icons.ERROR} Download failed: {str(e)}")
    
    def filter_files(self, files: List[Dict], source_only: bool = False, 
                     binary_only: bool = False) -> List[Dict]:
        """Filter package files by type"""
        if not source_only and not binary_only:
            return files
        
        filtered = []
        for file in files:
            package_type = file.get('packagetype', '')
            
            if source_only and package_type == 'sdist':
                filtered.append(file)
            elif binary_only and package_type in ('bdist_wheel', 'bdist_egg'):
                filtered.append(file)
        
        return filtered

class PackageInstaller:
    """Handle package installation"""
    
    def __init__(self, user_install: bool = False):
        self.user_install = user_install
    
    def install_package(self, package_spec: str) -> bool:
        """Install a package using pip"""
        cmd = [sys.executable, '-m', 'pip', 'install']
        
        if self.user_install:
            cmd.append('--user')
        
        cmd.append(package_spec)
        
        try:
            with console.status(f"{Icons.INFO} [bold #AAAAFF]Installing {package_spec}...") as status:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            
            if result.returncode == 0:
                console.print(f"{Icons.SUCCESS} [bold #FFFF00]Successfully installed:[/] {package_spec}")
                logger.info(f"Successfully installed: {package_spec}")
                return True
            else:
                console.print(f"{Icons.ERROR} [bold red]Installation failed for:[/] {package_spec}")
                console.print(f"{Icons.WARNING} [white on #0000FF]{result.stderr}[/]")
                logger.error(f"Installation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            console.print(f"{Icons.ERROR} [bold red]Installation timeout for:[/] {package_spec}")
            logger.error(f"Installation timeout for: {package_spec}")
            return False
        except Exception as e:
            console.print(f"{Icons.ERROR} [bold red]Installation error:[/] {str(e)}")
            logger.exception(e)
            return False

class StatisticsDisplay:
    """Display package statistics"""
    
    @staticmethod
    def display_stats(package_name: str, stats_data: Dict[str, Any], period: str):
        """Display formatted statistics"""
        
        if 'data' not in stats_data:
            console.print(f"{Icons.WARNING} [bold #FFFF00]No statistics data available[/]")
            return
        
        # Create summary table
        table = Table(
            title=f"{Icons.VERSION} [bold cyan]Statistics for {package_name}[/bold cyan]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta"
        )
        
        table.add_column("Period", style="cyan", no_wrap=True)
        table.add_column("Downloads", style="green", justify="right")
        
        data = stats_data['data']
        total_downloads = 0
        
        if period == "recent":
            # Recent stats (last day)
            for entry in data[:7]:  # Show last 7 days
                date = entry.get('date', 'N/A')
                downloads = entry.get('downloads', 0)
                total_downloads += downloads
                table.add_row(date, f"{downloads:,}")
        else:
            # Monthly/overall stats
            for entry in data:
                category = entry.get('category', 'N/A')
                downloads = entry.get('downloads', 0)
                total_downloads += downloads
                table.add_row(category, f"{downloads:,}")
        
        console.print(table)
        
        # Summary panel
        summary = Panel(
            f"[bold green]Total Downloads:[/bold green] [yellow]{total_downloads:,}[/yellow]",
            title="[bold]Summary[/bold]",
            border_style="green"
        )
        console.print(summary)

def parse_package_spec(package_spec: str) -> tuple:
    """Parse package specification (package or package==version)"""
    if '==' in package_spec:
        parts = package_spec.split('==')
        return parts[0].strip(), parts[1].strip()
    return package_spec.strip(), None

def get_save_directory(custom_path: Optional[str]) -> str:
    """Get save directory from argument, env, or default"""
    if custom_path:
        return custom_path
    
    # Try to load from .env
    if load_env:
        load_env(get_config_file())
        env_path = os.getenv('PIPS_DOWNLOAD_DIR')
        if env_path:
            return env_path
    
    return os.getcwd()

def validate_version(package_info: Dict, version: str) -> bool:
    """Validate if version exists for package"""
    available_versions = list(package_info.get('releases', {}).keys())
    return version in available_versions

def main():
    parser = argparse.ArgumentParser(
        description='pips - Another Python Package Manager',
        formatter_class=CustomRichHelpFormatter,
        epilog="""
Examples:
  pips -s requests              # Download source only (latest)
  pips -s requests==2.28.0      # Download specific version source
  pips -b numpy                 # Download binary only
  pips -s -b django             # Download both source and binary
  pips -i flask                 # Install package
  pips -i flask==2.0.0 --user   # Install specific version for user
  pips -S requests              # Show statistics
  pips -S requests -d month     # Show monthly statistics
  pips -s -i requests -p /tmp   # Download and install
  pips -s -m requests           # Download to subfolder 'requests'
  pips -s -b -m django -p /opt  # Download to /opt/django/
  pips -s requests -f           # Force overwrite existing files
  pips -b numpy -m -f           # Download to subfolder, force overwrite
  pips -s requests --no-cache   # Fetch without using cache
  pips -s requests --use-redis  # Use Redis cache
  pips --cache-info             # Show cache information
  pips --clear-cache            # Clear all cached data
  pips --clear-cache --use-redis # Clear file and Redis cache
        """
    )
    
    parser.add_argument('package', nargs='?', help=f'{Icons.VERSION} Package name or package==version')
    parser.add_argument('-s', '--source', action='store_true', 
                        help=f'{Icons.REMOTE} Download source distribution only')
    parser.add_argument('-b', '--binary', action='store_true',
                        help=f'{Icons.TAG} Download binary distribution only')
    parser.add_argument('-p', '--path', type=str,
                        help=f'{Icons.FOLDER} Download save directory (can be set in .env as PIPS_DOWNLOAD_DIR)')
    parser.add_argument('-m', '--manage', action='store_true', 
                        help=f"{Icons.NODE} Download and save in subfolder by package name")
    parser.add_argument('-f', '--force', action='store_true',
                        help=f"{Icons.UNLOCK} Force overwrite existing files without prompting")
    parser.add_argument('-i', '--install', action='store_true',
                        help=f'{Icons.INFO} Install the package')
    parser.add_argument('-c', '--check', nargs='?',
                        help=f'{Icons.BLOCK} Check before install the package')
    parser.add_argument('-S', '--stats', action='store_true',
                        help=f'{Icons.STATS} Show package statistics')
    parser.add_argument('-d', '--stat-period', type=str, default='recent',
                        choices=['recent', 'overall'],
                        help=f'{Icons.DATE} Statistics period (recent=last day, overall=all time)')
    parser.add_argument('--user', action='store_true',
                        help=f'{Icons.USERNAME} Install to user site-packages')
    parser.add_argument('--no-cache', action='store_true',
                        help=f'{Icons.CANCEL} Disable cache for package information')
    parser.add_argument('--use-redis', action='store_true',
                        help=f'{Icons.REMOTE} Use Redis cache (if available and configured)')
    parser.add_argument('--clear-cache', action='store_true',
                        help=f'{Icons.BLOCK} Clear all cached package information')
    parser.add_argument('--cache-info', action='store_true',
                        help=f'{Icons.INFO} Show cache information')
    parser.add_argument('--version', action='version', version=f'pips v{get_version()}', help = f"{Icons.MARK} Show version number")
    parser.add_argument('--debug', action='store_true', help=f'{Icons.BUG} Enable debug mode')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()

    package_name = None
    version = None
    
    # Load environment config
    if load_env:
        load_env(get_config_file())
    
    # Handle cache info command
    if args.cache_info:
        use_redis = args.use_redis or str(os.getenv('PIPS_USE_REDIS', '')).lower() in ['1', 'true', 'yes', 'on']
        client = PyPIClient(use_cache=True, use_redis=use_redis)
        info = client.get_cache_info()
        
        console.print(Panel(
            f"[bold cyan]Cache Information[/bold cyan]\n\n"
            f"[yellow]File Cache:[/yellow]\n"
            f"  Enabled: {'✅' if info['file_cache']['enabled'] else '❌'}\n"
            f"  Location: {info['file_cache']['location']}\n"
            f"  Files: {info['file_cache']['count']}\n"
            f"  Size: {info['file_cache']['size_mb']:.2f} MB\n\n"
            f"[yellow]Redis Cache:[/yellow]\n"
            f"  Enabled: {'✅' if info['redis_cache']['enabled'] else '❌'}\n"
            f"  Connected: {'✅' if info['redis_cache']['connected'] else '❌'}\n"
            f"  Keys: {info['redis_cache']['count']}",
            title=f"{Icons.INFO} [bold]pips Cache[/bold]",
            border_style="cyan"
        ))
        return 0
    
    # Handle clear cache command
    if args.clear_cache:
        use_redis = args.use_redis or str(os.getenv('PIPS_USE_REDIS', '')).lower() in ['1', 'true', 'yes', 'on']
        client = PyPIClient(use_cache=True, use_redis=use_redis)
        file_count, redis_count = client.clear_cache(clear_redis=use_redis)
        
        console.print(f"{Icons.SUCCESS} [bold green]Cache cleared:[/bold green]")
        console.print(f"  File cache: {file_count} file(s)")
        if use_redis:
            console.print(f"  Redis cache: {redis_count} key(s)")
        return 0
    
    # Validate arguments
    if not args.package and not args.check:
        parser.print_help()
        return 1
    
    if not any([args.source, args.binary, args.install, args.stats, args.check]):
        console.print(f"{Icons.ERROR} [red]Error:[/red] Please specify at least one action (-s, -b, -i, -c, or -S)")
        logger.error("No action specified")
        return 1
    
    try:
        # Parse package specification
        package_name, version = parse_package_spec(args.package or (args.check if args.check != True else None))  # type: ignore
        logger.debug(f"Package: {package_name}, Version: {version}")
        
        # Initialize client with cache settings
        use_cache = not args.no_cache
        use_redis = args.use_redis or str(os.getenv('PIPS_USE_REDIS', '')).lower() in ['1', 'true', 'yes', 'on']
        
        client = PyPIClient(use_cache=use_cache, use_redis=use_redis)
        
        if args.no_cache:
            console.print(f"{Icons.INFO} [dim]Cache disabled[/dim]")
        elif use_redis and client.redis_client:
            redis_config = get_redis_config()
            console.print(f"{Icons.REMOTE} [dim]Using Redis cache: {redis_config['host']}:{redis_config['port']}/{redis_config['db']}[/dim]")
        
        # Show package header
        console.print(Panel(
            f"[bold cyan]Package:[/bold cyan] {package_name}" + 
            (f"\n[bold cyan]Version:[/bold cyan] {version}" if version else ""),
            title=f"[bold]{Icons.VERSION} pips[/bold]",
            border_style="cyan"
        ))
        
        # Fetch package info with timing
        fetch_start = time.time()
        with console.status(f"{Icons.SEARCH} [cyan]Fetching package information..."):
            if version:
                package_info = client.get_package_version(package_name, version)
            else:
                package_info = client.get_package_info(package_name)
                version = package_info['info']['version']  # Get latest version
        fetch_time = time.time() - fetch_start
        
        logger.info(f"Package info fetched: {package_name} v{version} in {fetch_time:.2f}s")
        
        # Show fetch time with cache indicator
        if fetch_time < 0.5:
            if use_redis and client.redis_client:
                console.print(f"[dim]Fetched in {fetch_time:.2f}s (Redis cache)[/dim]")
            else:
                console.print(f"[dim]Fetched in {fetch_time:.2f}s (file cache)[/dim]")
        else:
            console.print(f"[dim]Fetched in {fetch_time:.2f}s[/dim]")
        
        # Download operations
        if args.source or args.binary:
            save_dir = get_save_directory(args.path)
            
            # Initialize downloader with manage mode
            downloader = PackageDownloader(
                save_dir=save_dir,
                manage_mode=args.manage,
                package_name=package_name,
                force_overwrite=args.force
            )
            
            actual_save_dir = downloader.save_dir
            
            if args.manage:
                console.print(f"{Icons.FOLDER} [bold cyan]Save directory:[/bold cyan] {actual_save_dir} [dim](managed mode)[/dim]")
            else:
                console.print(f"{Icons.FOLDER} [bold cyan]Save directory:[/bold cyan] {actual_save_dir}")
            
            if args.force:
                console.print(f"{Icons.UNLOCK} [yellow]Force overwrite mode enabled[/yellow]")
            
            logger.debug(f"Save directory: {actual_save_dir}")
            
            # Get files for the specific version
            if version in package_info.get('releases', {}):
                files = package_info['releases'][version]
            else:
                files = package_info.get('urls', [])
            
            # Filter files
            files_to_download = downloader.filter_files(
                files,
                source_only=args.source,
                binary_only=args.binary
            )
            
            if not files_to_download:
                console.print(f"{Icons.WARNING} [yellow]Warning:[/yellow] No matching files found for specified type")
                logger.warning("No matching files found")
            else:
                console.print(f"{Icons.INFO} [cyan]Found {len(files_to_download)} file(s) to download[/cyan]")
                logger.info(f"Found {len(files_to_download)} files to download")
                
                downloaded_count = 0
                skipped_count = 0
                corrupted_count = 0
                
                for file_info in files_to_download:
                    url = file_info['url']
                    filename = file_info['filename']
                    
                    # Check if file was corrupted before download
                    filepath = downloader.save_dir / filename
                    was_corrupted = filepath.exists() and not downloader._validate_file_integrity(filepath)
                    
                    result = downloader.download_file(url, filename)
                    
                    if result:
                        downloaded_count += 1
                        if was_corrupted:
                            corrupted_count += 1
                    else:
                        skipped_count += 1
                
                # Summary
                console.print(f"\n{Icons.INFO} [bold cyan]Download Summary:[/bold cyan]")
                console.print(f"  {Icons.SUCCESS} Downloaded: [green]{downloaded_count}[/green]")
                if corrupted_count > 0:
                    console.print(f"  {Icons.ERROR} Replaced corrupted: [red]{corrupted_count}[/red]")
                if skipped_count > 0:
                    console.print(f"  {Icons.WARNING} Skipped: [yellow]{skipped_count}[/yellow]")
                
                logger.info(f"Download summary - Downloaded: {downloaded_count}, Corrupted: {corrupted_count}, Skipped: {skipped_count}")
        
        # Install operation
        if args.install:
            if args.check and args.check == True:
                if not package_name:
                    package_name, version = parse_package_spec(args.package or (args.check if args.check != True else None))  # type: ignore
                    logger.debug(f"Package: {package_name}, Version: {version}")
        
                requirements = client.get_package_requirements(package_name, version)
                logger.emergency(f"requirements: {requirements}")  # type: ignore
                # Check and install packages (auto mode is now default)
                reqs, to_install, python_conflicts, version_conflicts, missing_packages = PIPR().check_packages(
                        requirements,
                        force_retry=True,
                        force_install=False,
                        summary_only=False,
                        show=True,
                        auto_mode=True,
                        pypi_package_name=package_name,
                        send_notification=False,
                    )

                logger.debug(f"reqs: {reqs}")
                logger.debug(f"to_install: {to_install}")
                logger.debug(f"python_conflicts: {python_conflicts}")
                logger.debug(f"version_conflicts: {version_conflicts}")
                logger.debug(f"missing_packages: {missing_packages}")


                if (not version_conflicts or not python_conflicts):
                    installer = PackageInstaller(user_install=args.user)
                    package_spec = f"{package_name}=={version}" if version else package_name
                    installer.install_package(package_spec)
                else:
                    console.print(f"{Icons.ERROR} [red]Installation aborted due to conflicts[/red]")
                    logger.error("Installation aborted due to conflicts")
            else:
                installer = PackageInstaller(user_install=args.user)
                package_spec = f"{package_name}=={version}" if version else package_name
                installer.install_package(package_spec)
        
        if args.check and args.check != True:
            if not package_name:
                package_name, version = parse_package_spec(args.check)
                logger.debug(f"Package: {package_name}, Version: {version}")
    
            requirements = client.get_package_requirements(package_name, version)
            logger.emergency(f"requirements: {requirements}")  # type: ignore
            # Check and install packages (auto mode is now default)
            reqs, to_install, python_conflicts, version_conflicts, missing_packages = PIPR().check_packages(
                    requirements,
                    force_retry=True,
                    force_install=False,
                    summary_only=False,
                    show=True,
                    auto_mode=True,
                    pypi_package_name=package_name,
                    send_notification=False,
                )

            logger.debug(f"reqs: {reqs}")
            logger.debug(f"to_install: {to_install}")
            logger.debug(f"python_conflicts: {python_conflicts}")
            logger.debug(f"version_conflicts: {version_conflicts}")
            logger.debug(f"missing_packages: {missing_packages}")

        # Statistics operation
        if args.stats:
            with console.status(f"{Icons.STATS} [cyan]Fetching statistics..."):
                stats_data = client.get_package_stats(package_name, args.stat_period)
            
            StatisticsDisplay.display_stats(package_name, stats_data, args.stat_period)
        
        console.print(f"\n{Icons.SUCCESS} [bold green]All operations completed successfully![/bold green]")
        logger.info("All operations completed successfully")
        return 0
        
    except PipsError as e:
        console.print(f"{Icons.ERROR} [red]Error:[/red] {str(e)}")
        logger.error(f"PipsError: {str(e)}")
        if os.getenv('TRACEBACK') == '1':
            tprint()
        return 1
    except KeyboardInterrupt:
        console.print(f"\n{Icons.CANCEL} [yellow]Operation cancelled by user[/yellow]")
        logger.warning("Operation cancelled by user")
        return 130
    except Exception as e:
        console.print(f"{Icons.ERROR} [bold red]Unexpected error:[/] {str(e)}")
        logger.exception("Unexpected error occurred")
        if os.getenv('TRACEBACK') == '1':
            tprint()
        return 1

if __name__ == '__main__':
    sys.exit(main())
