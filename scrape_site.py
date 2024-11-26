import asyncio
import os

from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext

# JavaScript to prevent navigation-like actions
JS_PREVENT_NAVIGATION = """
    // Prevent navigation and simulate clicking all buttons and triggering onclick events
    document.querySelectorAll('button, [onclick], a, form, [data-navigation="true"], [data-back="true"]').forEach(element => {
        // Handle dynamic prevention of navigation-like actions
        const isNavigationElement = element.tagName.toLowerCase() === 'a' && element.href 
                                    || element.hasAttribute('data-navigation') 
                                    || element.id === 'CLOSE_WINDOW';  // Add more custom conditions if needed
        
        // If it's an element that might cause navigation, prevent it
        if (isNavigationElement) {
            element.addEventListener('click', function(event) {
                event.preventDefault();  // Prevent the default navigation
                if (typeof element.onclick === 'function') {
                    element.onclick();  // Trigger onclick if defined
                }
            });
        }
        // Prevent form submissions
        else if (element.tagName.toLowerCase() === 'form') {
            element.addEventListener('submit', function(event) {
                event.preventDefault();  // Prevent form submission
                if (typeof element.onclick === 'function') {
                    element.onclick();  // Trigger onclick if defined
                }
            });
        }
        // Simulate button clicks
        else if (element.tagName.toLowerCase() === 'button') {
            element.click();
        }

        // Trigger onclick for other elements
        else if (typeof element.onclick === 'function') {
            element.onclick();
        }
    });
"""

async def main() -> None:
    # Create a folder to save the text files if it doesn't exist
    output_folder = "page_texts"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    crawler = PlaywrightCrawler(
        # Limit the crawl to max requests. Remove or increase it for crawling all links.
        # max_requests_per_crawl=10,
    )

    # Define the default request handler, which will be called for every request.
    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext) -> None:
        context.log.info(f'Processing {context.request.url} ...')

        # Inject the JS to prevent navigation-like actions before grabbing the page content
        await context.page.evaluate(JS_PREVENT_NAVIGATION)

        # Extract the HTML body content using Playwright
        body_content = await context.page.eval_on_selector("body", "element => element.innerHTML")

        # Save the body content as a .txt file in the output folder
        page_url = context.request.url.replace("https://", "").replace("http://", "").replace("/", "_")  # Clean URL to use as filename
        file_path = os.path.join(output_folder, f"{page_url}.txt")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(body_content)
        context.log.info(f"Page content saved to {file_path}")

        # Enqueue all links found on the page.
        await context.enqueue_links()

    # Run the crawler with the initial list of requests.
    await crawler.run(['https://lucas.lboro.ac.uk/pub-apx/f?p=303:1:::::P1_SEARCH_YEAR:24'])


if __name__ == '__main__':
    asyncio.run(main())
