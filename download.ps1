##############################################################################
# Blackbox CLI Install Script for Windows PowerShell (Extension Service Version)
#
# This script downloads the latest stable 'blackbox' CLI binary from the
# Extension Upload Service and installs it to your system.
#
# Supported OS: Windows
# Supported Architectures: x86_64
#
# Usage:
#   Invoke-WebRequest -Uri "https://releases.blackbox.ai/api/scripts/omni-cli/download.ps1" -OutFile "download.ps1"; .\download.ps1
#   Or simply: .\download.ps1
#
# Environment variables:
#   $env:BLACKBOX_BIN_DIR     - Directory to which Blackbox will be installed (default: $env:USERPROFILE\.local\bin)
#   $env:BLACKBOX_VERSION     - Optional: specific version to install (e.g., "v1.0.25"). Can be in the format vX.Y.Z, vX.Y.Z-suffix, or X.Y.Z
#   $env:BLACKBOX_PROVIDER    - Optional: provider for blackbox
#   $env:BLACKBOX_MODEL       - Optional: model for blackbox
#   $env:EXTENSION_SERVICE_URL - Extension service URL (default: https://releases.blackbox.ai)
#   $env:CANARY              - Optional: if set to "true", downloads from canary release instead of stable
#   $env:CONFIGURE           - Optional: if set to "false", disables running blackbox configure interactively
##############################################################################

# Set error action preference to stop on errors
$ErrorActionPreference = "Stop"

# --- 1) Variables ---
$PRODUCT_SLUG = "omni-cli"
$OUT_FILE = "blackbox.exe"
$EXTENSION_SERVICE_URL = if ($env:EXTENSION_SERVICE_URL) { $env:EXTENSION_SERVICE_URL } else { "https://releases.blackbox.ai" }

# Set default bin directory if not specified
if (-not $env:BLACKBOX_BIN_DIR) {
    $env:BLACKBOX_BIN_DIR = Join-Path $env:USERPROFILE ".local\bin"
}

# Determine release type
$RELEASE = if ($env:CANARY -eq "true") { "true" } else { "false" }
$CONFIGURE = if ($env:CONFIGURE -eq "false") { "false" } else { "true" }

# --- 2) Detect Architecture ---
$ARCH = $env:PROCESSOR_ARCHITECTURE
if ($ARCH -eq "AMD64") {
    $PLATFORM = "win-x64"
} elseif ($ARCH -eq "ARM64") {
    Write-Error "Windows ARM64 is not currently supported."
    exit 1
} else {
    Write-Error "Unsupported architecture '$ARCH'. Only x86_64 is supported on Windows."
    exit 1
}

# --- 3) Get latest release information from extension service ---
Write-Host "Fetching latest release information for platform: $PLATFORM..." -ForegroundColor Gray

$RELEASE_API_URL = "$EXTENSION_SERVICE_URL/api/v0/latest?product=$PRODUCT_SLUG&platform=$PLATFORM"

try {
    $RELEASE_INFO = Invoke-WebRequest -Uri $RELEASE_API_URL -UseBasicParsing | ConvertFrom-Json
    Write-Host "Successfully fetched release information." -ForegroundColor Green
} catch {
    Write-Error "Failed to fetch release information from $RELEASE_API_URL. Error: $($_.Exception.Message)"
    Write-Host "Please check that the extension service is available and the product '$PRODUCT_SLUG' exists." -ForegroundColor Red
    exit 1
}

# Extract download URL and version
$DOWNLOAD_URL = $RELEASE_INFO.url
$VERSION = $RELEASE_INFO.version

if (-not $DOWNLOAD_URL) {
    Write-Error "Could not parse download URL from release information"
    Write-Host "Release info: $($RELEASE_INFO | ConvertTo-Json)" -ForegroundColor Red
    exit 1
}

# Ensure download URL is absolute
if (-not $DOWNLOAD_URL.StartsWith("http")) {
    $DOWNLOAD_URL = "$EXTENSION_SERVICE_URL$DOWNLOAD_URL"
}

Write-Host "Downloading version $VERSION from: $DOWNLOAD_URL" -ForegroundColor Blue

# --- 4) Download the file ---
# Extract filename from URL
$FILENAME = Split-Path $DOWNLOAD_URL -Leaf
if (-not $FILENAME -or $FILENAME -eq "") {
    $FILENAME = "blackbox-$PLATFORM.zip"
}

try {
    Invoke-WebRequest -Uri $DOWNLOAD_URL -OutFile $FILENAME -UseBasicParsing
    Write-Host "Download completed successfully." -ForegroundColor Green
} catch {
    Write-Error "Failed to download $DOWNLOAD_URL. Error: $($_.Exception.Message)"
    exit 1
}

# --- 5) Create temporary directory for extraction ---
$TMP_DIR = Join-Path $env:TEMP "blackbox_install_$(Get-Random)"
try {
    New-Item -ItemType Directory -Path $TMP_DIR -Force | Out-Null
    Write-Host "Created temporary directory: $TMP_DIR" -ForegroundColor DarkYellow
} catch {
    Write-Error "Could not create temporary extraction directory: $TMP_DIR"
    exit 1
}

# --- 6) Extract the archive ---
Write-Host "Extracting $FILENAME to temporary directory..." -ForegroundColor Gray
try {
    # First extraction - the outer zip file
    Expand-Archive -Path $FILENAME -DestinationPath $TMP_DIR -Force
    Write-Host "First extraction completed successfully." -ForegroundColor Green
} catch {
    Write-Error "Failed to extract $FILENAME. Error: $($_.Exception.Message)"
    Remove-Item -Path $TMP_DIR -Recurse -Force -ErrorAction SilentlyContinue
    exit 1
}

# Clean up the downloaded archive
Remove-Item -Path $FILENAME -Force

# --- 7) Handle nested archive (Windows has zip -> zip -> blackbox-package/) ---
$NESTED_ZIP = Get-ChildItem -Path $TMP_DIR -Filter "*.zip" | Select-Object -First 1
if ($NESTED_ZIP) {
    Write-Host "Found nested zip file: $($NESTED_ZIP.Name)" -ForegroundColor DarkYellow
    Write-Host "Extracting nested Windows archive..." -ForegroundColor Green
    
    try {
        Expand-Archive -Path $NESTED_ZIP.FullName -DestinationPath $TMP_DIR -Force
        Write-Host "Nested extraction completed successfully." -ForegroundColor Green
        
        # Clean up the nested zip file
        Remove-Item -Path $NESTED_ZIP.FullName -Force
    } catch {
        Write-Error "Failed to extract nested archive $($NESTED_ZIP.Name). Error: $($_.Exception.Message)"
        Remove-Item -Path $TMP_DIR -Recurse -Force -ErrorAction SilentlyContinue
        exit 1
    }
}

# --- 8) Determine extraction directory ---
$EXTRACT_DIR = $TMP_DIR
if (Test-Path (Join-Path $TMP_DIR "blackbox-package")) {
    Write-Host "Found blackbox-package subdirectory, using that as extraction directory" -ForegroundColor DarkYellow
    $EXTRACT_DIR = Join-Path $TMP_DIR "blackbox-package"
}

# --- 8) Create bin directory if it doesn't exist ---
if (-not (Test-Path $env:BLACKBOX_BIN_DIR)) {
    Write-Host "Creating directory: $env:BLACKBOX_BIN_DIR" -ForegroundColor DarkYellow
    try {
        New-Item -ItemType Directory -Path $env:BLACKBOX_BIN_DIR -Force | Out-Null
    } catch {
        Write-Error "Could not create directory: $env:BLACKBOX_BIN_DIR"
        Remove-Item -Path $TMP_DIR -Recurse -Force -ErrorAction SilentlyContinue
        exit 1
    }
}

# --- 9) Install blackbox binary ---
$SOURCE_BLACKBOX = Join-Path $EXTRACT_DIR "blackbox.exe"
$DEST_BLACKBOX = Join-Path $env:BLACKBOX_BIN_DIR $OUT_FILE

if (Test-Path $SOURCE_BLACKBOX) {
Write-Host "Moving blackbox to $DEST_BLACKBOX" -ForegroundColor Gray
    try {
        # Remove existing file if it exists to avoid conflicts
        if (Test-Path $DEST_BLACKBOX) {
            Remove-Item -Path $DEST_BLACKBOX -Force
        }
        Move-Item -Path $SOURCE_BLACKBOX -Destination $DEST_BLACKBOX -Force
    } catch {
        Write-Error "Failed to move blackbox.exe to $DEST_BLACKBOX. Error: $($_.Exception.Message)"
        Remove-Item -Path $TMP_DIR -Recurse -Force -ErrorAction SilentlyContinue
        exit 1
    }
} else {
    Write-Error "blackbox.exe not found in extracted files"
    Remove-Item -Path $TMP_DIR -Recurse -Force -ErrorAction SilentlyContinue
    exit 1
}

# --- 10) Install temporal-service if it exists ---
$SOURCE_TEMPORAL_SERVICE = Join-Path $EXTRACT_DIR "temporal-service.exe"
if (Test-Path $SOURCE_TEMPORAL_SERVICE) {
    $DEST_TEMPORAL_SERVICE = Join-Path $env:BLACKBOX_BIN_DIR "temporal-service.exe"
    Write-Host "Moving temporal-service to $DEST_TEMPORAL_SERVICE" -ForegroundColor Gray
    try {
        # Remove existing file if it exists to avoid conflicts
        if (Test-Path $DEST_TEMPORAL_SERVICE) {
            Remove-Item -Path $DEST_TEMPORAL_SERVICE -Force
        }
        Move-Item -Path $SOURCE_TEMPORAL_SERVICE -Destination $DEST_TEMPORAL_SERVICE -Force
    } catch {
        Write-Warning "Failed to move temporal-service.exe: $($_.Exception.Message)"
    }
}

# --- 11) Install temporal CLI if it exists ---
$SOURCE_TEMPORAL = Join-Path $EXTRACT_DIR "temporal.exe"
if (Test-Path $SOURCE_TEMPORAL) {
    $DEST_TEMPORAL = Join-Path $env:BLACKBOX_BIN_DIR "temporal.exe"
    Write-Host "Moving temporal CLI to $DEST_TEMPORAL" -ForegroundColor Gray
    try {
        # Remove existing file if it exists to avoid conflicts
        if (Test-Path $DEST_TEMPORAL) {
            Remove-Item -Path $DEST_TEMPORAL -Force
        }
        Move-Item -Path $SOURCE_TEMPORAL -Destination $DEST_TEMPORAL -Force
    } catch {
        Write-Warning "Failed to move temporal.exe: $($_.Exception.Message)"
    }
}

# --- 12) Copy Windows runtime DLLs if they exist ---
$DLL_FILES = Get-ChildItem -Path $EXTRACT_DIR -Filter "*.dll" -ErrorAction SilentlyContinue
foreach ($dll in $DLL_FILES) {
    $DEST_DLL = Join-Path $env:BLACKBOX_BIN_DIR $dll.Name
    Write-Host "Moving Windows runtime DLL: $($dll.Name)" -ForegroundColor Gray
    try {
        # Remove existing file if it exists to avoid conflicts
        if (Test-Path $DEST_DLL) {
            Remove-Item -Path $DEST_DLL -Force
        }
        Move-Item -Path $dll.FullName -Destination $DEST_DLL -Force
    } catch {
        Write-Warning "Failed to move $($dll.Name): $($_.Exception.Message)"
    }
}

# --- 13) Clean up temporary directory ---
try {
    Remove-Item -Path $TMP_DIR -Recurse -Force
    Write-Host "Cleaned up temporary directory." -ForegroundColor DarkYellow
} catch {
    Write-Warning "Could not clean up temporary directory: $TMP_DIR"
}

# --- 14) Configure Blackbox (Optional) ---
if ($CONFIGURE -eq "true") {
    Write-Host ""
    Write-Host "Configuring Blackbox" -ForegroundColor Green
    Write-Host ""
    try {
        & $DEST_BLACKBOX configure
    } catch {
        Write-Warning "Failed to run blackbox configure. You may need to run it manually later."
    }
} else {
    Write-Host "Skipping 'blackbox configure', you may need to run this manually later" -ForegroundColor DarkYellow
}

# --- 15) Check PATH and add to environment if needed ---
$CURRENT_PATH = $env:PATH
if ($CURRENT_PATH -notlike "*$env:BLACKBOX_BIN_DIR*") {
    Write-Host ""
    Write-Host "Adding $env:BLACKBOX_BIN_DIR to your PATH..." -ForegroundColor Green
    
    try {
        # Get current user PATH
        $currentUserPath = [Environment]::GetEnvironmentVariable('PATH', 'User')
        
        # Check if the path is already in user PATH
        if ($currentUserPath -notlike "*$env:BLACKBOX_BIN_DIR*") {
            Write-Host "Adding Blackbox to user PATH..." -ForegroundColor Green
            
            # Add to user PATH (append with semicolon)
            $newUserPath = if ($currentUserPath) { "$currentUserPath;$env:BLACKBOX_BIN_DIR" } else { "$env:BLACKBOX_BIN_DIR" }
            [Environment]::SetEnvironmentVariable('PATH', $newUserPath, 'User')
            
            # Update current session PATH
            $env:PATH += ";$env:BLACKBOX_BIN_DIR"
            
            Write-Host "PATH successfully updated!" -ForegroundColor Green
            Write-Host "- Added to user environment variables (permanent)" -ForegroundColor Green
            Write-Host "- Updated current session PATH" -ForegroundColor Green
            Write-Host ""
            Write-Host "Note: New terminal sessions will automatically have the updated PATH." -ForegroundColor DarkYellow
        } else {
            Write-Host "PATH entry already exists in user environment variables." -ForegroundColor DarkYellow
            # Still update current session if needed
            if ($env:PATH -notlike "*$env:BLACKBOX_BIN_DIR*") {
                $env:PATH += ";$env:BLACKBOX_BIN_DIR"
                Write-Host "Updated current session PATH." -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "Error: Failed to update PATH automatically. $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please add manually using one of these methods:" -ForegroundColor DarkYellow
        Write-Host "For user PATH (no admin required):" -ForegroundColor DarkYellow
        Write-Host "    [Environment]::SetEnvironmentVariable('PATH', `$env:PATH + ';$env:BLACKBOX_BIN_DIR', 'User')" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "For this session only:" -ForegroundColor DarkYellow
        Write-Host "    `$env:PATH += ';$env:BLACKBOX_BIN_DIR'" -ForegroundColor Cyan
    }
    Write-Host ""
}

Write-Host "Blackbox CLI v$VERSION installed successfully at $DEST_BLACKBOX" -ForegroundColor Green
