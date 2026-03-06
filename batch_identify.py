#!/usr/bin/env python3
"""
Batch Audio Track Identification
Processes all subdirectories in a parent directory
"""

import subprocess
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# Import the identifier from our main script
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
from identify_tracks import TrackIdentifier

class BatchProcessor:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.results_file = self.root_dir / "batch_results.json"
        self.progress_file = self.root_dir / "batch_progress.json"
        self.start_time = datetime.now()
        self.total_folders = 0
        self.processed_folders = 0
        self.total_tracks = 0
        self.identified_tracks = 0
        self.failed_tracks = 0
        self.progress = self.load_progress()

    def load_progress(self):
        """Load previous progress if exists"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {'completed_folders': []}

    def save_progress(self):
        """Save current progress"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)

    def get_folders(self):
        """Get all subdirectories, sorted"""
        folders = [f for f in self.root_dir.iterdir() if f.is_dir()]
        folders.sort()
        return folders

    def count_audio_files(self, folder):
        """Count audio files in a folder"""
        audio_extensions = ['.mp3', '.flac', '.wav', '.m4a', '.ogg']
        count = 0
        for ext in audio_extensions:
            count += len(list(folder.glob(f"*{ext}")))
        return count

    def process_folder(self, folder):
        """Process a single folder"""
        folder_name = folder.name

        # Skip if already processed
        if folder_name in self.progress['completed_folders']:
            file_count = self.count_audio_files(folder)
            print(f"⏭️  SKIPPED (already processed): {folder_name} ({file_count} tracks)")
            return None

        file_count = self.count_audio_files(folder)
        if file_count == 0:
            print(f"⏭️  SKIPPED (no audio files): {folder_name}")
            self.progress['completed_folders'].append(folder_name)
            self.save_progress()
            return None

        print(f"\n{'='*70}")
        print(f"📂 Folder {self.processed_folders + 1}/{self.total_folders}: {folder_name}")
        print(f"   Files: {file_count} audio files")
        print(f"{'='*70}")

        # Process with identifier
        identifier = TrackIdentifier(folder)
        results = identifier.process_folder(folder)

        # Update stats
        self.total_tracks += identifier.stats['total']
        self.identified_tracks += identifier.stats['identified']
        self.failed_tracks += identifier.stats['no_match'] + identifier.stats['errors']

        # Mark as completed
        self.progress['completed_folders'].append(folder_name)
        self.save_progress()

        # Print progress summary
        self.print_progress()

        return {
            'folder': folder_name,
            'tracks': file_count,
            'identified': identifier.stats['identified'],
            'failed': identifier.stats['no_match'] + identifier.stats['errors'],
            'results': results
        }

    def print_progress(self):
        """Print current progress and time estimates"""
        elapsed = datetime.now() - self.start_time

        if self.processed_folders > 0:
            avg_time_per_folder = elapsed.total_seconds() / self.processed_folders
            remaining_folders = self.total_folders - self.processed_folders
            eta_seconds = avg_time_per_folder * remaining_folders
            eta = timedelta(seconds=int(eta_seconds))
        else:
            eta = "calculating..."

        print(f"\n{'='*70}")
        print(f"📊 PROGRESS SUMMARY")
        print(f"{'='*70}")
        print(f"Folders:   {self.processed_folders}/{self.total_folders} ({self.processed_folders/max(1,self.total_folders)*100:.1f}%)")
        print(f"Tracks:    {self.identified_tracks}/{self.total_tracks} identified ({self.identified_tracks/max(1,self.total_tracks)*100:.1f}%)")
        print(f"Failed:    {self.failed_tracks}")
        print(f"Elapsed:   {str(elapsed).split('.')[0]}")
        print(f"ETA:       {eta}")
        print(f"{'='*70}\n")

    def process_all(self):
        """Process all folders in directory"""
        print("🎵 BATCH AUDIO TRACK IDENTIFIER")
        print("="*70)
        print(f"Directory: {self.root_dir}")
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        # Get all folders
        folders = self.get_folders()
        self.total_folders = len(folders)

        print(f"\n📁 Found {self.total_folders} folders")
        print(f"✓ Already processed: {len(self.progress['completed_folders'])}")
        print(f"⏳ Remaining: {self.total_folders - len(self.progress['completed_folders'])}")

        # Process each folder
        all_results = []
        for folder in folders:
            self.processed_folders += 1
            result = self.process_folder(folder)
            if result:
                all_results.append(result)

            # Save results periodically
            if self.processed_folders % 10 == 0:
                self.save_results(all_results)

        # Final save
        self.save_results(all_results)

        # Print final summary
        self.print_final_summary()

    def save_results(self, results):
        """Save batch results"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'total_folders': self.total_folders,
            'processed_folders': self.processed_folders,
            'total_tracks': self.total_tracks,
            'identified_tracks': self.identified_tracks,
            'failed_tracks': self.failed_tracks,
            'success_rate': f"{self.identified_tracks/max(1,self.total_tracks)*100:.1f}%",
            'folders': results
        }

        with open(self.results_file, 'w') as f:
            json.dump(output, f, indent=2)

    def print_final_summary(self):
        """Print final summary"""
        elapsed = datetime.now() - self.start_time

        print(f"\n{'='*70}")
        print("🎉 BATCH PROCESSING COMPLETE!")
        print(f"{'='*70}")
        print(f"Folders processed:    {self.processed_folders}")
        print(f"Total tracks:         {self.total_tracks}")
        print(f"✓ Identified:         {self.identified_tracks} ({self.identified_tracks/max(1,self.total_tracks)*100:.1f}%)")
        print(f"✗ Failed/No match:    {self.failed_tracks}")
        print(f"Total time:           {str(elapsed).split('.')[0]}")
        print(f"Average per track:    {elapsed.total_seconds()/max(1,self.total_tracks):.1f}s")
        print(f"{'='*70}")
        print(f"\n💾 Results saved to: {self.results_file}")
        print(f"📊 Progress saved to: {self.progress_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 batch_identify.py <directory_path>")
        print("\nExample:")
        print("  python3 batch_identify.py '/path/to/unknown/music'")
        print("\nProcesses all subdirectories in the specified directory.")
        print("Progress is saved, so you can resume if interrupted.")
        sys.exit(1)

    directory_path = sys.argv[1]

    if not os.path.exists(directory_path):
        print(f"Error: Directory not found: {directory_path}")
        sys.exit(1)

    if not os.path.isdir(directory_path):
        print(f"Error: Not a directory: {directory_path}")
        sys.exit(1)

    processor = BatchProcessor(directory_path)

    try:
        processor.process_all()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
        print(f"Progress saved. Run again to resume from where you left off.")
        sys.exit(0)


if __name__ == "__main__":
    main()
