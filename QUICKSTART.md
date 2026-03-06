# 🚀 Quick Start Guide

Get up and running with AcoustID Music Identifier in 5 minutes!

## Step 1: Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get install libchromaprint-tools

# macOS
brew install chromaprint

# Fedora/RHEL
sudo dnf install chromaprint-tools
```

Verify installation:
```bash
fpcalc -version
```

## Step 2: Get API Key

1. Go to: https://acoustid.org/new-application
2. Sign up/login (free account)
3. Create a new application
4. Copy your API key

## Step 3: Configure

**Option A: Environment Variable** (Recommended)
```bash
export ACOUSTID_API_KEY="your_key_here"
```

Add to your `~/.bashrc` or `~/.zshrc` to make it permanent:
```bash
echo 'export ACOUSTID_API_KEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

**Option B: Config File**
```bash
cp config.example.json config.json
nano config.json  # Add your API key
```

## Step 4: Test

Test on a single folder with limit:
```bash
python3 identify_tracks.py /path/to/music/folder 5
```

Expected output:
```
🎵 AUDIO TRACK IDENTIFIER
============================================================
Processing: folder_name
Files: 5
============================================================

[1/5] 📁 track001.mp3
  🔍 Generating fingerprint...
  🌐 Querying AcoustID API...
  ✓ MATCH (HIGH - 95.3%)
    Artist: Bob Marley
    Title:  Three Little Birds
    Album:  Exodus
...
```

## Step 5: Batch Process

Process multiple folders:
```bash
python3 batch_identify.py /path/to/parent/directory
```

## Common Workflows

### Organize Unknown Music Collection

```bash
# 1. Identify all tracks
python3 batch_identify.py ~/Music/Unknown

# 2. Check results
cat ~/Music/Unknown/batch_results.json

# 3. Use results to organize files
# (Create your own organizing script based on batch_results.json)
```

### Test Before Full Run

```bash
# Test on first 10 files
python3 identify_tracks.py ~/Music/Unknown/folder1 10

# If results look good, do full batch
python3 batch_identify.py ~/Music/Unknown
```

### Resume Interrupted Processing

```bash
# Start processing
python3 batch_identify.py ~/Music/Unknown

# Press Ctrl+C to interrupt

# Resume from where you left off (reads batch_progress.json)
python3 batch_identify.py ~/Music/Unknown
```

## Troubleshooting

### "fpcalc not found"
→ Install chromaprint (see Step 1)

### "No API key found"
→ Set environment variable or create config.json (see Step 3)

### Low success rate (<50%)
→ Normal for obscure/unreleased music
→ Popular tracks should have 70-90% success rate

## What's Next?

1. **Read full documentation**: See `README.md`
2. **Process your collection**: Run batch identifier
3. **Organize results**: Use JSON output to organize files
4. **Star the project**: Share with others who need it!

## Quick Reference

```bash
# Single folder
python3 identify_tracks.py <folder> [limit]

# Batch process
python3 batch_identify.py <parent_directory>

# Set API key
export ACOUSTID_API_KEY="your_key"

# Check version
fpcalc -version
```

---

**You're ready to go! 🎵**

Questions? Check `README.md` for full documentation.
