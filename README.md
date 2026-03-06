# 🎵 AcoustID Music Identifier

Identify unknown music files using acoustic fingerprinting via the [AcoustID](https://acoustid.org/) API and [MusicBrainz](https://musicbrainz.org/) database.

Perfect for organizing large collections of untagged or poorly tagged music files!

## ✨ Features

- 🔍 **Acoustic fingerprinting** - Identifies music by audio content, not metadata
- 📊 **High accuracy** - Typically 60-90% success rate on popular music
- 🚀 **Batch processing** - Process entire directories with resume capability
- 💾 **Progress tracking** - Saves progress, resume from where you left off
- 📝 **JSON output** - Machine-readable results for further processing
- 🎼 **Multiple formats** - Supports MP3, FLAC, WAV, M4A, OGG
- 🆓 **Free & open-source** - Uses free AcoustID API

## 📋 Requirements

### System Dependencies

**Chromaprint (fpcalc)** - Audio fingerprinting tool

```bash
# Debian/Ubuntu
sudo apt-get install libchromaprint-tools

# Fedora/RHEL/CentOS
sudo dnf install chromaprint-tools

# macOS
brew install chromaprint

# Windows
# Download from: https://acoustid.org/chromaprint
```

### Python

- Python 3.6 or higher
- No external Python packages required (uses stdlib only!)

## 🚀 Quick Start

### 1. Get an API Key

Get your free API key from AcoustID:
1. Visit https://acoustid.org/new-application
2. Register/login and create a new application
3. Copy your API key

### 2. Configure

**Option A: Environment Variable (Recommended)**
```bash
export ACOUSTID_API_KEY="your_api_key_here"
```

**Option B: Config File**
```bash
cp config.example.json config.json
# Edit config.json and add your API key
```

### 3. Run

**Identify a single folder:**
```bash
python3 identify_tracks.py /path/to/music/folder
```

**Batch process multiple folders:**
```bash
python3 batch_identify.py /path/to/parent/directory
```

## 📖 Usage

### Single Folder Identification

Identify all audio files in a single folder:

```bash
python3 identify_tracks.py /path/to/music/folder
```

**With limit** (test on first 10 files):
```bash
python3 identify_tracks.py /path/to/music/folder 10
```

**Output:**
- Console output with results
- `identification_results.json` saved in the folder

### Batch Processing

Process all subdirectories in a parent directory:

```bash
python3 batch_identify.py /path/to/unknown/music
```

**Features:**
- Processes each subdirectory automatically
- Saves progress after each folder
- Can resume if interrupted (Ctrl+C)
- Shows ETA and success rate
- Creates `batch_results.json` and `batch_progress.json`

**Example output:**
```
🎵 BATCH AUDIO TRACK IDENTIFIER
======================================================================
Directory: /path/to/unknown/music
Started: 2026-03-06 15:30:00
======================================================================

📁 Found 166 folders
✓ Already processed: 0
⏳ Remaining: 166

======================================================================
📂 Folder 1/166: Unknown_Folder_001
   Files: 12 audio files
======================================================================

[1/12] 📁 track001.mp3
  🔍 Generating fingerprint...
  🌐 Querying AcoustID API...
  ✓ MATCH (HIGH - 95.3%)
    Artist: Artist Name
    Title:  Track Title
    Album:  Album Name
...
```

## 📊 Understanding Results

### Confidence Levels

- **HIGH** (>80%) - Very likely correct
- **MEDIUM** (60-80%) - Probably correct, verify if important
- **LOW** (50-60%) - Less certain, manually verify

### Success Rates

Typical success rates depend on your music collection:
- **Popular/mainstream music**: 70-90%
- **Independent/underground**: 50-70%
- **Rare/obscure**: 20-50%
- **Unreleased/bootlegs**: <20%

### Output Files

**identification_results.json** (single folder):
```json
[
  {
    "file": "track001.mp3",
    "metadata": {
      "title": "Song Title",
      "artist": "Artist Name",
      "album": "Album Name",
      "score": 0.953,
      "id": "musicbrainz-recording-id"
    }
  }
]
```

**batch_results.json** (batch processing):
```json
{
  "timestamp": "2026-03-06T15:30:00",
  "total_folders": 166,
  "total_tracks": 2041,
  "identified_tracks": 1236,
  "failed_tracks": 805,
  "success_rate": "60.7%",
  "folders": [...]
}
```

## 🔧 Configuration

### config.json Options

```json
{
  "api_key": "YOUR_API_KEY",           // Your AcoustID API key
  "rate_limit_delay": 0.5,             // Delay between API calls (seconds)
  "confidence_threshold": 0.5,          // Minimum confidence score (0-1)
  "fpcalc_path": "fpcalc"              // Path to fpcalc binary
}
```

### Environment Variables

- `ACOUSTID_API_KEY` - Your API key (recommended method)

## 💡 Tips & Best Practices

### Rate Limiting

The free AcoustID API has rate limits:
- Default: 0.5 seconds between requests (2 per second)
- For faster processing, consider supporting AcoustID or getting higher limits

### Batch Processing Tips

1. **Start small** - Test on a few folders first
2. **Use limits** - Test with `identify_tracks.py /folder 10` first
3. **Resume capability** - Press Ctrl+C to stop, run again to resume
4. **Monitor progress** - Check `batch_progress.json` for status

### Handling Unmatched Files

Files that can't be identified are usually:
- Obscure/unreleased tracks
- Poor quality recordings
- Very short clips
- Corrupted files
- Classical music (often poorly indexed)

### Organizing Results

You can use the JSON output to:
- Write ID3 tags programmatically
- Move files to organized folders
- Generate reports
- Import into music management software

## 🛠️ Troubleshooting

### "fpcalc not found"

Install chromaprint (see Requirements section)

### "No API key found"

Set `ACOUSTID_API_KEY` environment variable or create `config.json`

### Low success rate

- Check audio quality (corrupt files won't match)
- Try popular/mainstream tracks first to verify setup
- Some collections (classical, unreleased) have lower match rates

### API errors

- Check internet connection
- Verify API key is valid
- Check rate limiting (reduce requests per second)

## 📚 How It Works

1. **Fingerprinting**: Uses chromaprint (fpcalc) to generate acoustic fingerprint
2. **API Query**: Sends fingerprint to AcoustID API
3. **Database Lookup**: AcoustID queries MusicBrainz database
4. **Metadata Extraction**: Returns artist, title, album information
5. **Confidence Score**: Each match has a confidence score (0-1)

## 🤝 Contributing

This is a simple, self-contained tool. Feel free to:
- Report bugs via GitHub issues
- Submit pull requests for improvements
- Share your success stories!

## 📄 License

MIT License - Feel free to use, modify, and distribute

## 🙏 Credits

- **AcoustID** - Free acoustic fingerprinting service
- **MusicBrainz** - Open music encyclopedia
- **Chromaprint** - Audio fingerprinting library

## 📞 Support

- AcoustID Documentation: https://acoustid.org/webservice
- MusicBrainz: https://musicbrainz.org/
- Chromaprint: https://acoustid.org/chromaprint

## 🎯 Real-World Example

```bash
# Identify 2,041 unknown tracks
$ python3 batch_identify.py ~/Music/Unknown

🎵 BATCH AUDIO TRACK IDENTIFIER
======================================================================
Started: 2026-03-06 14:00:00
======================================================================

📁 Found 166 folders
Processing...

🎉 BATCH PROCESSING COMPLETE!
======================================================================
Folders processed:    166
Total tracks:         2,041
✓ Identified:         1,236 (60.7%)
✗ Failed/No match:    805
Total time:           36:04
Average per track:    1.1s
======================================================================

Results: batch_results.json (420 KB)
```

**Results:**
- 60.7% success rate (1,236 tracks identified)
- Average 1.1 seconds per track
- Ready to organize into proper library structure!

---

**Made with ❤️ for music lovers who want to organize their collections**

🎵 Enjoy your newly identified music! 🎵
