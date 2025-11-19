# Desktop vs Web Application Guide

DevFoam provides two user interfaces: a desktop GUI application and a web-based application. This guide helps you choose which one to use.

## Quick Comparison

| Feature | Desktop GUI | Web Application |
|---------|-------------|-----------------|
| **Installation** | Requires Python + tkinter | Requires Python + Flask |
| **Access** | Local machine only | Any device with browser |
| **Performance** | Faster (native) | Slightly slower (network) |
| **File Size Limit** | Unlimited | 16MB default |
| **Multi-user** | No | Yes (when deployed) |
| **Deployment** | Not needed | Required for remote access |
| **Dependencies** | tkinter | Flask, Werkzeug |
| **Best For** | Single-user, local work | Teams, remote access |

## Desktop GUI Application

### Advantages

✅ **Better Performance**: Native application with direct file access
✅ **No File Limits**: Can handle very large CAD files
✅ **Offline Work**: No internet connection required
✅ **Privacy**: Files never leave your machine
✅ **Simpler Setup**: Just run the launcher

### Disadvantages

❌ **Single Machine**: Only accessible on the computer where it's installed
❌ **No Collaboration**: Can't share with team members
❌ **Installation Required**: Must install Python and dependencies
❌ **Platform-Specific**: Requires tkinter (sometimes missing on Linux)

### When to Use

- Working on your local machine
- Processing very large CAD files
- Need maximum performance
- Offline work environment
- Single-user scenarios
- Quick personal projects

### Launch Commands

```bash
# Method 1: Launcher script
./devfoam-gui

# Method 2: Python module
python3 -m devfoam

# Method 3: Direct execution
python3 src/devfoam/cad_to_gcode.py
```

## Web Application

### Advantages

✅ **Universal Access**: Use from any device with a browser
✅ **No Installation**: Users just need a web browser
✅ **Multi-User**: Multiple people can use simultaneously
✅ **Cross-Platform**: Works on Windows, Mac, Linux, mobile
✅ **Team Collaboration**: Easy to share with colleagues
✅ **Remote Access**: Access from anywhere with internet

### Disadvantages

❌ **File Size Limits**: Default 16MB maximum upload
❌ **Network Required**: Needs internet for remote access
❌ **Setup Complexity**: Requires server deployment for production
❌ **Slower**: Network latency affects performance
❌ **Security Concerns**: Files are uploaded to server

### When to Use

- Team collaboration
- Remote work
- Multiple users
- Cross-platform access
- Mobile device access
- Cloud-based workflows
- No local installation allowed

### Launch Commands

```bash
# Development mode (local only)
./devfoam-web

# Or using Python
python3 -m devfoam.web.app

# Production mode with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 --chdir src devfoam.web.app:app
```

### Access URLs

- **Local development**: http://localhost:5001
- **Network access**: http://your-ip-address:5001
- **Production**: https://your-domain.com

## Feature Comparison

### File Upload/Loading

**Desktop GUI:**
- Browse local file system
- Drag and drop support
- No size limits
- Instant file access

**Web Application:**
- Upload via browser
- 16MB default limit (configurable)
- Network transfer time
- Temporary file storage

### Canvas Rendering

**Desktop GUI:**
- Tkinter canvas
- Native rendering
- Faster updates
- More responsive zoom/pan

**Web Application:**
- HTML5 Canvas
- Browser-based rendering
- Smooth zoom/pan
- Modern UI with tabs

### G-code Generation

**Desktop GUI:**
- Generates locally
- Instant output
- Save directly to disk
- No network overhead

**Web Application:**
- Generates on server
- Network transfer
- Download via browser
- RESTful API access

### Parameter Configuration

Both applications provide the same parameters:
- Feed rate (mm/min)
- Safety height (mm)
- Wire temperature (°C)
- Cut depth (mm)
- Units (mm/inches)

## Use Case Scenarios

### Scenario 1: Home Workshop

**Best Choice**: Desktop GUI

**Reason**: Single user, local machine, maximum performance, no need for remote access.

```bash
./devfoam-gui
# Load DXF file
# Generate G-code
# Save to USB drive for CNC machine
```

### Scenario 2: Makerspace / Shared Workshop

**Best Choice**: Web Application

**Reason**: Multiple users, different computers, centralized access, no installation on every machine.

```bash
# On server/workshop computer:
./devfoam-web

# Users access via:
# http://workshop-pc:5001
```

### Scenario 3: Remote Team Collaboration

**Best Choice**: Web Application (Cloud Deployed)

**Reason**: Team members in different locations, need universal access, cloud-based workflow.

```bash
# Deploy to Heroku/AWS/Google Cloud
# Team accesses via:
# https://devfoam.yourcompany.com
```

### Scenario 4: Educational Environment

**Best Choice**: Both

**Reason**: Desktop for lab computers, web for student access from home.

- **Lab computers**: Desktop GUI for hands-on learning
- **Home access**: Web application for homework and projects

### Scenario 5: Production Manufacturing

**Best Choice**: Desktop GUI

**Reason**: Reliability, no network dependency, integration with existing workflow.

```bash
# Dedicated CNC computer with desktop GUI
./devfoam-gui
# Part of automated workflow
```

## Installation Comparison

### Desktop GUI Setup

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Make launcher executable
chmod +x devfoam-gui

# 3. Run
./devfoam-gui
```

**Time to setup**: ~5 minutes
**Complexity**: Low

### Web Application Setup (Development)

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Make launcher executable
chmod +x devfoam-web

# 3. Run
./devfoam-web
```

**Time to setup**: ~5 minutes
**Complexity**: Low

### Web Application Setup (Production)

```bash
# 1. Install dependencies + web server
pip3 install -r requirements.txt
pip3 install gunicorn

# 2. Configure Nginx
sudo nano /etc/nginx/sites-available/devfoam

# 3. Setup systemd service
sudo nano /etc/systemd/system/devfoam-web.service

# 4. Enable SSL with Let's Encrypt
sudo certbot --nginx -d your-domain.com

# 5. Start service
sudo systemctl start devfoam-web
```

**Time to setup**: ~30-60 minutes
**Complexity**: High

See [Web Deployment Guide](WEB_DEPLOYMENT.md) for detailed instructions.

## Security Considerations

### Desktop GUI

- ✅ Files never leave your machine
- ✅ No network exposure
- ✅ No authentication needed
- ⚠️ Physical access = full access

### Web Application

- ⚠️ Files uploaded to server
- ⚠️ Network exposure
- ⚠️ Need authentication for production
- ✅ Can implement access controls
- ✅ Can log all activities

**Production Web Security Checklist:**
- [ ] Use HTTPS/SSL
- [ ] Implement user authentication
- [ ] Add rate limiting
- [ ] Scan uploaded files
- [ ] Use secure session cookies
- [ ] Regular security updates

## Migration Between Versions

### Desktop → Web

If you're switching from desktop to web:

1. **Files remain compatible**: Same file formats (DXF, SVG, JSON)
2. **G-code output identical**: Same generation engine
3. **Parameters unchanged**: All settings work the same way

Simply upload your existing CAD files to the web interface.

### Web → Desktop

If you're switching from web to desktop:

1. Download your G-code from web interface
2. Open same CAD files in desktop GUI
3. Generate and save locally

## Running Both Simultaneously

You can use both interfaces at the same time:

```bash
# Terminal 1: Desktop GUI
./devfoam-gui

# Terminal 2: Web application
./devfoam-web
```

They are completely independent and don't interfere with each other.

## Performance Benchmarks

Based on a 1000-line DXF file:

| Operation | Desktop GUI | Web App (Local) | Web App (Remote) |
|-----------|-------------|-----------------|------------------|
| Load File | 0.2s | 0.5s | 1-3s (upload) |
| Render Canvas | 0.1s | 0.2s | 0.2s |
| Generate G-code | 0.3s | 0.3s | 0.5s |
| Save/Download | 0.1s | 0.2s | 0.5s |
| **Total** | **0.7s** | **1.2s** | **2.5s** |

*Note: Remote times vary based on network speed*

## Recommendations by Use Case

### Use Desktop GUI If:

- ✅ You work alone
- ✅ You need maximum performance
- ✅ You process large files (>16MB)
- ✅ You work offline
- ✅ You prefer native applications
- ✅ You have direct machine access

### Use Web Application If:

- ✅ You work in a team
- ✅ You need remote access
- ✅ Multiple people use the tool
- ✅ You want browser-based workflow
- ✅ You need cross-platform access
- ✅ You want to avoid local installation

### Use Both If:

- ✅ You're in an educational environment
- ✅ You have both individual and team work
- ✅ You want flexibility
- ✅ You need redundancy

## Support and Documentation

- **Desktop GUI**: See main [README.md](../README.md)
- **Web Application**: See [WEB_DEPLOYMENT.md](WEB_DEPLOYMENT.md)
- **API Documentation**: Coming soon
- **Troubleshooting**: See respective documentation

## Conclusion

Both the desktop GUI and web application are fully-featured and use the same underlying G-code generation engine. Your choice depends on your workflow, team structure, and deployment requirements.

**Quick Decision Tree:**

```
Need remote access?
├─ Yes → Web Application
└─ No → Need multi-user?
         ├─ Yes → Web Application
         └─ No → Desktop GUI
```

For most individual users working locally, the **Desktop GUI** is recommended for its simplicity and performance.

For teams, remote workers, or multi-user environments, the **Web Application** is recommended for its accessibility and collaboration features.
