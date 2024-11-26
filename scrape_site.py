import asyncio
import os

from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext

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
    await crawler.run(['https://lucas.lboro.ac.uk/pub-apx/f?p=303:107::APEX_CLONE_SESSION::107:PROG_CODE,PROG_YEAR,SPEC_YEAR:BSUB10,24,24'])


if __name__ == '__main__':
    asyncio.run(main())
