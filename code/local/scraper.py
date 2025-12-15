from pathlib import Path
import re
import requests
import wget
import os
import shutil
import json
from bs4 import BeautifulSoup

def scrape_fma(output_path, genres, page_nums, song_per_page_limit, overwrite_files=False):
    '''
    Scraper function to grab songs from the FMA and place into a local folder

    inputs:
        output_path - str - filepath for where the files will be stored
        genres - list - list of string containing the genres to be scraped (aka ['Dance', 'Jazz'])
        page_nums - list - list of pages to scrape 
        song_per_page_limit - int - number of songs to scrape per page (takes from the top) max = 20
        overwrite_files = bool - if True will delete existing songs and rescrape, is False will skip if song exists
    '''
    assert song_per_page_limit <= 20, "Error: Maximum songs per page of 20"

    song_ref_dict = {}

    # Scrape through specified parameters
    for genre in genres:
        
        # Set up folders for each genre
        output_folder_path = output_path + genre + '/'

        # Create or recreate directory for the genre
        output_folder = Path(output_folder_path)
        if overwrite_files:
            if output_folder.exists():
                shutil.rmtree(output_folder)
            output_folder.mkdir(parents=True, exist_ok=True)
        else:
            output_folder.mkdir(parents=True, exist_ok=True)

        clean_urls = []
        song_id = 0
        
        # Go through each page
        for i in page_nums:

            # Grab the HTML webpage and find all the links to each song
            page = requests.get(f"https://freemusicarchive.org/genre/{genre}/?page={i}")
            soup = BeautifulSoup(page.content, 'html.parser')
            playlist_space = soup.find(class_="w-full flex flex-col gap-3 pt-3")
            song_space = playlist_space.find_all(class_="ptxt-track")

            # Collect all href attributes inside the song_space (any instance of href)
            list_of_urls = []
            for tag in song_space:
                for a in tag.find_all(href=True):
                    href = a.get('href')
                    if href:
                        list_of_urls.append(href)

            # Go through and clean each URL before scraping the song (Takes a while)
            for clean_url_link in list_of_urls[0:song_per_page_limit]:
                clean_urls.append(clean_url_link)

                song_name = clean_url_link.split("/")[-1]
                song_page = requests.get(clean_url_link)

                soup = BeautifulSoup(song_page.content, 'html.parser')
                song_data = soup.find(attrs={"data-track-info": True}).get('data-track-info')
                json_song_data = json.loads(song_data)
                file_url = json_song_data['fileUrl']

                try:
                    with requests.get(file_url, stream=True, timeout=30) as song_file:
                        song_file.raise_for_status()

                        downloaded_kb = 0
                        out_path = Path(output_path) / genre / f"Song{song_id}.mp3"
                        with open(out_path, 'wb') as f:
                            for chunk in song_file.iter_content(chunk_size=8192):
                                if not chunk:
                                    continue
                                f.write(chunk)
                                downloaded_kb += len(chunk) // 1024
                                print(f"Downloaded {downloaded_kb} KB of song {song_id}", end='\r', flush=True)
                        print(' ' * 80, end='\r')
                    print(f"Completed download of song {song_id}")
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading {file_url}: {e}")
                    # skip this song and continue
                    continue

                # Iterate song ids
                song_id +=  1

                # Print to keep track of progress
                if song_id % 20 == 0:
                    print(f'Scraped: {song_id} songs')

        # Add URLS to dictionary for later use if needed
        song_ref_dict[genre] = clean_urls

    # Write out the file dictionary as a JSON
    song_id_json = json.dumps(song_ref_dict)

    base_output = (Path(__file__).resolve().parent / '..' / 'songs').resolve()
    base_output.mkdir(parents=True, exist_ok=True)

    json_path = base_output / 'song_id_dict.json'
    json_path.write_text(song_id_json)
    