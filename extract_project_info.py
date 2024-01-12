from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup


def open_browser(playwright):
    # Launch the browser
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    return browser, page


def close_browser(browser):
    browser.close()


def scrape_upwork(page, URL):
    jobs_posted = ""
    hire_rate = ""
    budget = ""
    status = ""
    try:
        # Navigate to the Upwork job page
        page.goto(URL, timeout=120000)

        # Wait for the element that contains the jobs posted and hire rate info
        page.wait_for_selector('li[data-qa="client-job-posting-stats"]', timeout=120000)

        # Extract the jobs posted
        jobs_posted = page.query_selector('li[data-qa="client-job-posting-stats"] strong').text_content().strip()

        # Extract the hire rate
        hire_rate = page.query_selector(
            'li[data-qa="client-job-posting-stats"] div.text-body-sm').text_content().strip()

        # print(f"Jobs Posted: {jobs_posted}")
        # print(f"Hire Rate: {hire_rate}")

        # Wait for the elements that contain the budget amount and status info
        page.wait_for_selector('div[data-test="BudgetAmount"]', timeout=120000)

        # Extract the budget amounts
        budget_elements = page.query_selector_all('div[data-test="BudgetAmount"] strong')
        budgets = [element.text_content().strip() for element in budget_elements]
        budget = '-'.join(budgets)
        # Extract the status (Hourly/Fixed rate)
        status = page.query_selector('div.description').text_content()

        # print("Budgets:", '-'.join(budgets))
        # print("Status:", status)
    except Exception as e:
        print("Playwright failed to extract from url", URL, "due to", e)

    return jobs_posted, hire_rate, budget, status


if __name__ == "__main__":
    with sync_playwright() as playwright:
        browser, page = open_browser(playwright)
        scrape_upwork(page, 'https://www.upwork.com/jobs/~010820d957fd353fc1')
        scrape_upwork(page, 'https://www.upwork.com/jobs/Coding-instagram-bot_~01e6edd1e30225d34e?source=rss')
        close_browser(browser)
