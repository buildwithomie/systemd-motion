# Publishing Systemd Motion to Public Repositories

## 🎯 **Step-by-Step Publishing Guide**

### 1. **GitHub Repository Setup**

```bash
# Initialize git repository
git init
git add .
git commit -m "Initial release: Systemd Motion v1.0.0"

# Create GitHub repository and push
git remote add origin https://github.com/yourusername/systemd-motion.git
git branch -M main
git push -u origin main

# Create release tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 2. **Debian Package Distribution**

#### Option A: Personal Package Archive (PPA)
```bash
# Install packaging tools
sudo apt install devscripts build-essential

# Build source package
debuild -S

# Upload to PPA
dput ppa:yourusername/systemd-motion ../systemd-motion_1.0.0_source.changes

# Users can then install with:
# sudo add-apt-repository ppa:yourusername/systemd-motion
# sudo apt update
# sudo apt install systemd-motion
```

#### Option B: Direct .deb Distribution
```bash
# Build package
dpkg-buildpackage -us -uc

# Upload .deb file to GitHub Releases
# Users download and install with:
# wget https://github.com/yourusername/systemd-motion/releases/latest/download/systemd-motion_1.0.0_all.deb
# sudo dpkg -i systemd-motion_1.0.0_all.deb
```

### 3. **Snap Store Distribution**

```bash
# Install snapcraft
sudo snap install snapcraft --classic

# Build snap
snapcraft

# Login to Snap Store
snapcraft login

# Register snap name
snapcraft register systemd-motion

# Upload to Snap Store
snapcraft upload systemd-motion_1.0.0_amd64.snap

# Users can then install with:
# sudo snap install systemd-motion
```

### 4. **Flatpak Distribution**

```bash
# Create flatpak manifest
cat > systemd-motion.yml << EOF
app-id: com.github.yourusername.systemd-motion
runtime: org.freedesktop.Platform
runtime-version: '22.08'
sdk: org.freedesktop.Sdk
command: systemd-motion
finish-args:
  - --socket=session-bus
  - --socket=system-bus
  - --share=network
modules:
  - name: systemd-motion
    buildsystem: simple
    build-commands:
      - python3 -m pip install -e .
    sources:
      - type: git
        url: https://github.com/yourusername/systemd-motion.git
        tag: v1.0.0
EOF

# Build flatpak
flatpak-builder build systemd-motion.yml --install --user

# Users can install with:
# flatpak install flathub com.github.yourusername.systemd-motion
```

### 5. **AUR (Arch User Repository)**

```bash
# Create PKGBUILD
cat > PKGBUILD << EOF
pkgname=systemd-motion
pkgver=1.0.0
pkgrel=1
pkgdesc="Systemd Motion Session Manager"
arch=('any')
url="https://github.com/yourusername/systemd-motion"
license=('MIT')
depends=('python' 'python-dbus-next' 'systemd')
makedepends=('python-setuptools')
source=("https://github.com/yourusername/systemd-motion/archive/v\$pkgver.tar.gz")
sha256sums=('SKIP')

package() {
  cd "\$pkgname-\$pkgver"
  python setup.py install --root="\$pkgdir" --optimize=1
}
EOF

# Upload to AUR
# Users can install with: yay -S systemd-motion
```

### 6. **COPR (Fedora)**

```bash
# Create spec file
cat > systemd-motion.spec << EOF
Name:           systemd-motion
Version:        1.0.0
Release:        1%{?dist}
Summary:        Systemd Motion Session Manager
License:        MIT
URL:            https://github.com/yourusername/systemd-motion
Source0:        https://github.com/yourusername/systemd-motion/archive/v%{version}.tar.gz

BuildRequires:  python3-devel python3-setuptools
Requires:       python3 python3-dbus-next systemd

%description
A lightweight session management service that monitors user behavior.

%prep
%setup -q

%build
python3 setup.py build

%install
python3 setup.py install --root %{buildroot}

%files
%license LICENSE
%doc README.md
%{_bindir}/systemd-motion
%{_bindir}/motion-ctl
%{_bindir}/motion-gui
%{python3_sitelib}/motion/
EOF

# Upload to COPR
# Users can install with: sudo dnf copr enable yourusername/systemd-motion
```

## 🚀 **Quick Publishing Commands**

### Build All Packages
```bash
# Build everything
bash scripts/build_packages.sh
```

### GitHub Release
```bash
# Create release with all packages
gh release create v1.0.0 \
  ../systemd-motion_1.0.0_all.deb \
  systemd-motion_1.0.0_amd64.snap \
  --title "Systemd Motion v1.0.0" \
  --notes "Initial release of Systemd Motion"
```

### Publish to All Stores
```bash
# Debian PPA
dput ppa:yourusername/systemd-motion ../systemd-motion_1.0.0_source.changes

# Snap Store
snapcraft upload systemd-motion_1.0.0_amd64.snap

# Flatpak
flatpak-builder build systemd-motion.yml --install --user
```

## 📋 **User Installation Commands**

After publishing, users can install with:

```bash
# Debian/Ubuntu
sudo apt install systemd-motion

# Snap
sudo snap install systemd-motion

# Flatpak
flatpak install flathub com.github.yourusername.systemd-motion

# Arch Linux
yay -S systemd-motion

# Fedora
sudo dnf install systemd-motion
```

## 🎯 **Success Metrics**

- ✅ **GitHub Stars**: Track popularity
- ✅ **Download Counts**: Monitor usage
- ✅ **Issue Reports**: User feedback
- ✅ **Package Updates**: Version adoption

Your application will be available to millions of Linux users worldwide! 🌍
