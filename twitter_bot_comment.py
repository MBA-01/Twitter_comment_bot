from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time
import datetime
import logging
import random
import openai
import json
import signal
import sys
from datetime import datetime, timedelta




USERNAME = "EMAIL"   #Email
PASSWORD = "PASSWORD"              #Password
MY_TWITTER_HANDLE = "USERNAME"    #Username          Your Twitter handle to skip your own posts




openai.api_key = "sk-7m9eX0t6JY5hY1X4uGpZG3BlbkFJ1IwL2Wwv6t0O2wK4M9eV"

# Configuration
MAX_DAILY_COMMENTS = 500
COMMENT_DELAY = 15  # 5 minutes between comments
SESSION_DURATION = 6  # hours

now_time_hist_file = datetime.now().strftime("%Y%m%d%H%M%S")
COMMENT_HISTORY_FILE = f"comment_history_{now_time_hist_file}.json"
INITIAL_POST_TIMESTAMP = None
MIN_WAIT_TIME = 15  # 0.5 minutes in seconds
MAX_WAIT_TIME = 30  # 2 minutes in seconds

# Global counters
daily_comment_count = 0 
last_reset_date = datetime.now().date()

# Setup logging
logging.basicConfig(
    filename=f'twitter_bot_{datetime.now().strftime("%Y%m%d%H%M%S")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def signal_handler(sig, frame):
    print('Exiting gracefully...')
    sys.exit(0)

def set_options():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return chrome_options

def reset_daily_counters():
    global daily_comment_count, last_reset_date
    current_date = datetime.datetime.now().date()
    if current_date > last_reset_date:
        daily_comment_count = 0
        last_reset_date = current_date
        logging.info("Daily counters reset")

def check_login_status(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Profile']"))
        )
        return True
    except:
        logging.warning("Login status check failed")
        return False

def login_twitter(driver):
    try:
        driver.get("https://x.com/login")
        time.sleep(3)

        # Enter username
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='username']"))
        )
        username_input.send_keys(USERNAME)
        username_input.send_keys(Keys.RETURN)
        time.sleep(2)

        try:
            # Handle additional username verification if needed
            username_label = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//label[.//span[text()='Phone or username']]"))
            )
            input_field = driver.find_element(By.XPATH, "//label[.//span[text()='Phone or username']]//input")
            input_field.send_keys(MY_TWITTER_HANDLE)
            input_field.send_keys(Keys.RETURN)
        except TimeoutException:
            pass

        # Enter password
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.send_keys(PASSWORD)
        password_input.send_keys(Keys.RETURN)
        time.sleep(3)

        return True
    except Exception as e:
        logging.error(f"Login failed: {str(e)}")
        return False

def navigate_to_following(driver):
    try:
        link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[.//span[text()='Following']]"))
        )
        link.click()
        time.sleep(5)
        return True
    except Exception as e:
        logging.error(f"Failed to navigate to Following feed: {str(e)}")
        return False


# Need to activate the key
def generate_response(tweet_text):
    '''try:
        prompt = f"""
        Tweet: {tweet_text}
        Write a friendly, engaging reply. Keep it:
        - Natural and conversational
        - Related to the tweet's content
        - Under 280 characters
        - Without hashtags or mentions
        """
        
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=60,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logging.error(f"Failed to generate response: {str(e)}")
        return None'''
    value = tweet_text + " " + "TEST1"
    return value

def comment_on_post(driver, post):
    global daily_comment_count
    
    try:
        if daily_comment_count >= MAX_DAILY_COMMENTS:
            logging.info("Daily comment limit reached")
            return False
        print('step 1 .. find and click reply button')
        # Find and click reply button
        reply_button = post.find_element(By.XPATH, ".//button[@data-testid='reply']")
        reply_button.click()
        time.sleep(2)
        print('step 2 .. generate response')

        # Get tweet text and generate response
        tweet_text = post.find_element(By.XPATH, ".//div[@data-testid='tweetText']").text
        print(tweet_text)
        comment = generate_response(tweet_text)
        
        if not comment:
            logging.info("Failed to generate response")
            print('ERROR - Comment generation failled')
            return False
        print('step 3 .. enter comment in place')

        # Enter comment
        comment_box = driver.find_element(By.XPATH, "//div[@data-testid='tweetTextarea_0']")
        comment_box.send_keys(comment)
        time.sleep(1)
        print('step 4 .. submit')

        # Submit comment
        reply_button = driver.find_element(By.XPATH, "//button[@data-testid='tweetButton']")
        reply_button.click()
        
        daily_comment_count += 1
        logging.info(f"Successfully commented on post. Daily count: {daily_comment_count}")
        
        print('step 5 .. applying delays')
        
        # Random delay between comments
        time.sleep(random.uniform(15, 30))

        print('last step 6 .. finish delays')
        
        return True

    except Exception as e:
        logging.error(f"Error commenting on post: {str(e)}")
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        print("ESCAPE - 1")
        return False

def load_comment_history():
    try:
        with open(COMMENT_HISTORY_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_comment_history(history):
    with open(COMMENT_HISTORY_FILE, 'w') as f:
        json.dump(history, f)

def is_already_commented(driver,post, comment_history):
    try:
        tweet_link = post.find_element(By.XPATH, ".//a[contains(@href, '/status/')]").get_attribute('href')
        tweet_id = tweet_link.split('/')[-1]
        return tweet_id in comment_history
    except Exception as e:
        print(f"Error checking comment history: {e}")
        return False
    finally:
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        print("ESCAPE-2")


def get_post_timestamp(driver,post):
    try:
        time_element = post.find_element(By.XPATH, ".//time")
        return time_element.get_attribute('datetime')
    except Exception as e:
        print(f"Error getting timestamp: {e}")
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        print("ESCAPE-3")
        return None

def process_posts(driver):
    global INITIAL_POST_TIMESTAMP
    comment_history = load_comment_history()
    
    while True:
        try:
            # Scroll to top and refresh
            driver.execute_script("window.scrollTo(0, 0)")
            driver.refresh()
            time.sleep(5)
            driver.execute_script("window.scrollBy(0, 1000);")

            # Check for "Show new posts" button
            try:
                show_posts_button = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Show') and contains(text(),'posts')]/ancestor::button"))
                )
                show_posts_button.click()
                time.sleep(2)
            except TimeoutException:
                pass
            except Exception as ex:
                webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                print("ESCAPE-4")
                print("Maybe here's the shitty shit that's I'm looking for") #YOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO

            # Get all visible posts
            posts = WebDriverWait(driver, 10).until(
                
                EC.presence_of_all_elements_located((By.XPATH, "//article[@data-testid='tweet']"))
            )

            # If this is the first run, set the initial timestamp
            if INITIAL_POST_TIMESTAMP is None and posts:
                INITIAL_POST_TIMESTAMP = get_post_timestamp(driver,posts[0])
                print(f"Initial timestamp set to: {INITIAL_POST_TIMESTAMP}")

            # Process posts from newest to oldest
            for post in posts:
                try:
                    # Get post timestamp
                    current_post_timestamp = get_post_timestamp(driver,post)
                    if not current_post_timestamp:
                        continue

                    # Skip if post is older than our initial timestamp
                    if current_post_timestamp <= INITIAL_POST_TIMESTAMP and INITIAL_POST_TIMESTAMP is not None:
                        continue

                    # Skip if already commented
                    if is_already_commented(driver,post, comment_history):
                        continue

                    # Skip own posts
                    username = post.find_element(By.XPATH, ".//div[@data-testid='User-Name']").text
                    if MY_TWITTER_HANDLE in username:
                        continue

                    # Comment on post | | | NEED TO GET BACK
                    if comment_on_post(driver, post):
                        # Save to comment history
                        tweet_link = post.find_element(By.XPATH, ".//a[contains(@href, '/status/')]").get_attribute('href')
                        tweet_id = tweet_link.split('/')[-1]
                        comment_history[tweet_id] = datetime.now().isoformat()
                        save_comment_history(comment_history)
                        
                        # Random wait between 2-5 minutes
                        wait_time = random.uniform(MIN_WAIT_TIME, MAX_WAIT_TIME)
                        print(f"Waiting for {wait_time/60:.2f} minutes before next action")
                        
                        #SCROLL DOWN - 1000px
                        driver.execute_script("window.scrollBy(0, 1000);")

                        time.sleep(wait_time)

                except Exception as e:
                    print(f"Error processing individual post: {e}")
                    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    print("ESCAPE-5")
                    continue

        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(30)

signal.signal(signal.SIGINT, signal_handler)


def main():
    while True:
        driver = None
        try:
            logging.info("_________Starting new session__________")
            service = Service(executable_path="chromedriver.exe")
            driver = webdriver.Chrome(service=service, options=set_options())

            if not login_twitter(driver):
                print("ERROR LOGIN")
                raise Exception("Login failed")

            if not navigate_to_following(driver):
                print("ERROR NAVIGATING to FOLLOWING SECTION")
                raise Exception("Failed to navigate to Following feed")
            print("______Logging and Navigation are Clear !_____")
            process_posts(driver)

        except Exception as e:
            logging.error(f"Critical error occurred: {str(e)}")
            print(str(e))
            print("SOME WEIRD ERROR OCCURED, CHECK THE EXCEPTION MESSAGE")
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            print("ESCAPE-6")

        finally:
            try:
                if driver:
                    driver.quit()
                    print("QUITING")
            except:
                pass
            time.sleep(60)  # Wait before restart

if __name__ == "__main__":
    while True:
        try:
            main()
        except :
            main.driver.quit()