#!/usr/bin/env python3
import sys
import os
import yt_dlp
import argparse
import shutil

def check_ffmpeg():
    """Check if FFmpeg is available"""
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        print("❌ Error: FFmpeg is not installed or not in PATH!")
        print("\nPlease install FFmpeg:")
        print("  • Windows: Download from https://ffmpeg.org/download.html")
        print("  • Mac: brew install ffmpeg")
        print("  • Linux: sudo apt install ffmpeg (Ubuntu/Debian)")
        print("\nFFmpeg is required to convert audio to MP3 format.")
        return False
    return True

def download_audio(url, output_dir="downloads", skip_confirmation=False):
    """
    Download audio from YouTube URL (single video or playlist) as high-quality MP3
    """
    # Check FFmpeg availability first
    if not check_ffmpeg():
        return False
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # yt-dlp options for high-quality MP3 extraction
    ydl_opts = {
        'format': 'bestaudio/best',  # Download best audio quality
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        # Add metadata and clean up
        'writethumbnail': False,
        'writeinfojson': False,
        'embed_subs': False,
        'keepvideo': False,  # Don't keep original video file
        # IMPORTANT: Continue on download errors
        'ignoreerrors': True,  # Continue on download/extraction errors
        'abort_on_unavailable_fragment': False,  # Don't abort on fragment errors
        # Fix for YouTube SABR issue - use different clients
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'player_skip': ['webpage', 'configs'],
            }
        },
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get info about the URL to determine if it's a playlist (without downloading)
            print("Analyzing URL...")
            info = ydl.extract_info(url, download=False)
            
            if 'entries' in info:
                # It's a playlist
                available_count = len([e for e in info['entries'] if e is not None])
                total_count = len(info['entries'])
                
                print(f"Found playlist: {info.get('title', 'Unknown')}")
                print(f"Total videos: {total_count}")
                print(f"Available videos: {available_count}")
                
                if total_count != available_count:
                    print(f"⚠️  Note: {total_count - available_count} videos are unavailable and will be skipped")
                
                if not skip_confirmation:
                    # Ask for confirmation
                    response = input("Do you want to download the available videos? (y/n): ")
                    if response.lower() not in ['y', 'yes']:
                        print("Download cancelled.")
                        return False
                
                print("Downloading playlist...")
            else:
                # It's a single video
                print(f"Found video: {info.get('title', 'Unknown')}")
                print("Downloading single video...")
            
            # Now download with the same ydl instance
            ydl.download([url])
            print(f"\n✅ Download completed! Files saved to: {os.path.abspath(output_dir)}")
            
    except yt_dlp.DownloadError as e:
        print(f"❌ Download error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Download YouTube videos/playlists as MP3 files')
    parser.add_argument('url', help='YouTube URL (video or playlist)')
    parser.add_argument('-o', '--output', default='downloads', 
                       help='Output directory (default: downloads)')
    parser.add_argument('--no-confirm', action='store_true',
                       help='Skip confirmation for playlist downloads')
    
    args = parser.parse_args()
    
    # Validate URL
    if 'youtube.com' not in args.url and 'youtu.be' not in args.url:
        print("Error: Please provide a valid YouTube URL")
        sys.exit(1)
    
    print(f"Processing URL: {args.url}")
    print(f"Output directory: {args.output}")
    print("-" * 50)
    
    # Download the audio
    success = download_audio(args.url, args.output, skip_confirmation=args.no_confirm)
    
    if success:
        print("\n✅ All downloads completed successfully!")
    else:
        print("\n❌ Download failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()