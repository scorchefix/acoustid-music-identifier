#!/usr/bin/env python3
"""
Audio Track Identification using AcoustID API
Identifies audio files using acoustic fingerprinting and tags them with proper metadata
"""

import subprocess
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Configuration - Load from config file or environment variable
def load_api_key():
    """Load API key from config file or environment variable"""
    # Try environment variable first
    api_key = os.environ.get('ACOUSTID_API_KEY')
    if api_key:
        return api_key

    # Try config file
    config_file = Path(__file__).parent / 'config.json'
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            return config.get('api_key')

    print("ERROR: No API key found!")
    print("Please set ACOUSTID_API_KEY environment variable or create config.json")
    print("Get your free API key at: https://acoustid.org/new-application")
    sys.exit(1)

ACOUSTID_API_KEY = load_api_key()
ACOUSTID_API_URL = "https://api.acoustid.org/v2/lookup"
FPCALC_PATH = "fpcalc"  # Assumes fpcalc is in PATH
RATE_LIMIT_DELAY = 0.5  # seconds between API calls

class TrackIdentifier:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.stats = {
            'total': 0,
            'identified': 0,
            'no_match': 0,
            'errors': 0,
            'skipped': 0
        }

    def get_fingerprint(self, file_path):
        """Generate acoustic fingerprint using fpcalc"""
        try:
            result = subprocess.run(
                [FPCALC_PATH, '-json', str(file_path)],
                capture_output=True,
                text=True,
                check=True
            )
            data = json.loads(result.stdout)
            return data.get('duration'), data.get('fingerprint')
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Fingerprint failed: {e}")
            return None, None
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON decode error: {e}")
            return None, None
        except FileNotFoundError:
            print(f"  ✗ fpcalc not found. Please install chromaprint.")
            return None, None

    def query_acoustid(self, duration, fingerprint):
        """Query AcoustID API for track identification"""
        params = {
            'client': ACOUSTID_API_KEY,
            'duration': int(duration),
            'fingerprint': fingerprint,
            'meta': 'recordings releasegroups'
        }

        try:
            url = f"{ACOUSTID_API_URL}?{urlencode(params)}"
            req = Request(url)
            req.add_header('User-Agent', 'AcoustIDMusicIdentifier/1.0')

            with urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                return data
        except (URLError, HTTPError) as e:
            print(f"  ✗ API error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"  ✗ Response parse error: {e}")
            return None

    def extract_metadata(self, api_response):
        """Extract best metadata from AcoustID response"""
        if not api_response or api_response.get('status') != 'ok':
            return None

        results = api_response.get('results', [])
        if not results:
            return None

        # Get the best match (highest score)
        best_match = max(results, key=lambda x: x.get('score', 0))

        if best_match.get('score', 0) < 0.5:  # Confidence threshold
            return None

        recordings = best_match.get('recordings', [])
        if not recordings:
            return None

        recording = recordings[0]

        # Extract metadata
        metadata = {
            'title': recording.get('title', 'Unknown Title'),
            'artist': 'Unknown Artist',
            'album': 'Unknown Album',
            'date': '',
            'score': best_match.get('score', 0),
            'id': recording.get('id', '')
        }

        # Get artist name
        if 'artists' in recording and recording['artists']:
            metadata['artist'] = recording['artists'][0].get('name', 'Unknown Artist')

        # Get album from release groups
        if 'releasegroups' in recording and recording['releasegroups']:
            release = recording['releasegroups'][0]
            metadata['album'] = release.get('title', 'Unknown Album')

        return metadata

    def identify_file(self, file_path):
        """Identify a single audio file"""
        print(f"\n📁 {file_path.name}")

        # Generate fingerprint
        print("  🔍 Generating fingerprint...")
        duration, fingerprint = self.get_fingerprint(file_path)

        if not duration or not fingerprint:
            self.stats['errors'] += 1
            return None

        # Query AcoustID
        print("  🌐 Querying AcoustID API...")
        time.sleep(RATE_LIMIT_DELAY)  # Rate limiting

        response = self.query_acoustid(duration, fingerprint)
        metadata = self.extract_metadata(response)

        if not metadata:
            print("  ✗ No match found")
            self.stats['no_match'] += 1
            return None

        # Display result
        score = metadata['score']
        confidence = "HIGH" if score > 0.8 else "MEDIUM" if score > 0.6 else "LOW"

        print(f"  ✓ MATCH ({confidence} - {score:.1%})")
        print(f"    Artist: {metadata['artist']}")
        print(f"    Title:  {metadata['title']}")
        print(f"    Album:  {metadata['album']}")

        self.stats['identified'] += 1
        return metadata

    def process_folder(self, folder_path, limit=None):
        """Process all audio files in a folder"""
        folder = Path(folder_path)

        # Support multiple audio formats
        audio_extensions = ['*.mp3', '*.flac', '*.wav', '*.m4a', '*.ogg']
        audio_files = []
        for ext in audio_extensions:
            audio_files.extend(folder.glob(ext))

        audio_files = sorted(audio_files)

        if limit:
            audio_files = audio_files[:limit]

        print(f"\n{'='*60}")
        print(f"Processing: {folder.name}")
        print(f"Files: {len(audio_files)}")
        print(f"{'='*60}")

        results = []
        for i, audio_file in enumerate(audio_files, 1):
            self.stats['total'] += 1
            print(f"\n[{i}/{len(audio_files)}]", end=" ")

            metadata = self.identify_file(audio_file)
            if metadata:
                results.append({
                    'file': audio_file.name,
                    'metadata': metadata
                })

        return results

    def print_stats(self):
        """Print identification statistics"""
        print(f"\n{'='*60}")
        print("IDENTIFICATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total processed:  {self.stats['total']}")
        print(f"✓ Identified:     {self.stats['identified']} ({self.stats['identified']/max(1,self.stats['total'])*100:.1f}%)")
        print(f"✗ No match:       {self.stats['no_match']}")
        print(f"✗ Errors:         {self.stats['errors']}")
        print(f"{'='*60}")

    def save_results(self, results, output_file):
        """Save identification results to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 identify_tracks.py <folder_path> [limit]")
        print("\nExample:")
        print("  python3 identify_tracks.py '/path/to/music/folder' 10")
        print("\nIdentifies audio files in the folder using acoustic fingerprinting.")
        print("Optionally limit the number of files to process.")
        sys.exit(1)

    folder_path = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None

    if not os.path.exists(folder_path):
        print(f"Error: Folder not found: {folder_path}")
        sys.exit(1)

    print("🎵 AUDIO TRACK IDENTIFIER")
    print("=" * 60)

    identifier = TrackIdentifier(folder_path)
    results = identifier.process_folder(folder_path, limit)
    identifier.print_stats()

    # Save results
    output_file = Path(folder_path) / "identification_results.json"
    identifier.save_results(results, output_file)

    print("\n✅ Processing complete!")


if __name__ == "__main__":
    main()
