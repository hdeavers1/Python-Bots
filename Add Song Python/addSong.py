from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

PLAYLIST_FILE = "Add to Playlist.txt"
USER_PROFILE_PATH = ""  # Update this path

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=" + USER_PROFILE_PATH)
    options.add_argument("--window-size=1200,800")  # Set the size (width, height)
    options.add_argument("--window-position=0,0")  # Set the position (x, y)
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)
    return driver

def add_song_to_youtube_playlist(driver, song_title):
    try:
        driver.get("https://www.youtube.com/")
        time.sleep(2)  # Ensure the page loads

        # Find and use the search box
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "search_query"))
        )
        search_box.clear()
        search_box.send_keys(song_title)
        search_box.send_keys(Keys.RETURN)

        # Wait for search results and click the first video
        time.sleep(1)
        first_video = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#video-title > yt-formatted-string"))
        )
        ActionChains(driver).move_to_element(first_video).click().perform()
        print("first video action executed")

        # Wait for the video to load and pause it
        time.sleep(2)  # Adjust this if necessary
        video_player = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "html5-video-player"))
        )
        ActionChains(driver).move_to_element(video_player).send_keys(Keys.SPACE).perform()  # Pause the video
        print("video player action executed")

        # Hover over the three-dot button and click
        dot_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="button-shape"]/button/yt-touch-feedback-shape/div'))
        )
        ActionChains(driver).move_to_element(dot_button).perform()
        time.sleep(1)  # Wait for the hover action to take effect
        ActionChains(driver).move_to_element(dot_button).click().perform()
        print("dot button action executed")

        # Click the Save button
        save_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="items"]/ytd-menu-service-item-renderer[2]/tp-yt-paper-item'))
        )
        ActionChains(driver).move_to_element(save_button).click().perform()
        print("save button action executed")

        # Select the appropriate playlist
        playlist_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="playlists"]/ytd-playlist-add-to-option-renderer[2]'))
        )
        ActionChains(driver).move_to_element(playlist_button).click().perform()
        print("playlist selection action executed")

        # Remove the song from the playlist file
        remove_song_from_playlist_file(song_title)
        time.sleep(2)  # Give some time for the actions to complete

    except Exception as e:
        print(f"Error: {str(e)}")

def remove_song_from_playlist_file(song_title):
    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, 'r', encoding='utf-8') as file:
            songs = file.read().splitlines()
        
        # Remove the song from the list
        if song_title in songs:
            songs.remove(song_title)
        
        # Write the updated list back to the file
        with open(PLAYLIST_FILE, 'w', encoding='utf-8') as file:
            file.write("\n".join(songs))

def main():
    driver = setup_driver()
    while True:
        if os.path.exists(PLAYLIST_FILE):
            with open(PLAYLIST_FILE, 'r', encoding='utf-8') as file:
                songs = file.read().splitlines()
                
            if not songs:
                print("Playlist file is empty. Exiting.")
                break
            
            for song in songs:
                add_song_to_youtube_playlist(driver, song)
                print(f'Added "{song}" to the YouTube playlist and removed from the file.')
        else:
            print(f"Playlist file '{PLAYLIST_FILE}' not found.")
            break
    driver.quit()

if __name__ == '__main__':
    main()
