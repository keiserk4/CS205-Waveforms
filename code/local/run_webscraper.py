from scraper import scrape_fma
from pathlib import Path

# Set up parameters
# Resolve output path relative to this script and ensure it exists
base_output = (Path(__file__).resolve().parent / '..' / 'songs' / 'mp3').resolve()
base_output.mkdir(parents=True, exist_ok=True)
output_path = str(base_output) + '\\'

genres = ['piano']
page_nums = list(range(1, 5))
song_per_page_limit = 5
overwrite_files = True

scrape_fma(output_path, genres, page_nums, song_per_page_limit, overwrite_files)
