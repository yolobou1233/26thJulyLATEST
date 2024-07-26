from webdriver_manager.chrome import ChromeDriverManager
from utils.threading_controller import FastSearchAlgo
from argparse import ArgumentParser
import tkinter as tk
from threading import Lock, Thread
import logging

class GMapsScraper:
    def __init__(self):
        self._args = None
        self.setup_logging()
        self.stop_scraping = False
        self.result_count = 0

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def arg_parser(self):
        parser = ArgumentParser(description='Command Line Google Map Scraper by Abdul Moez')

        # Input options
        parser.add_argument('-l', '--limit', help='Number of results to scrape (-1 for all results, default: 500)',
                            type=int, default=500)
        parser.add_argument('-u', '--unavailable-text',
                            help='Replacement text for unavailable information (default: "Not Available")', type=str,
                            default="Not Available")
        parser.add_argument('-bw', '--browser-wait', help='Browser waiting time in seconds (default: 15)', type=int,
                            default=15)
        parser.add_argument('-se', '--suggested-ext',
                            help='Suggested URL extensions to try (can be specified multiple times)', action='append',
                            default=[])
        parser.add_argument('-wb', '--windowed-browser', help='Disable headless mode', action='store_false',
                            default=True)
        parser.add_argument('-v', '--verbose', help='Enable verbose mode', action='store_true')
        parser.add_argument('-o', '--output-folder', help='Output folder to store CSV details (default: ./CSV_FILES)',
                            type=str, default='./CSV_FILES')
        parser.add_argument('-d', '--driver-path',
                            help='Path to Chrome driver (if not provided, it will be downloaded)', type=str,
                            default='')

        self._args = parser.parse_args()

    def scrape_maps_data(self, query):
        self.result_count = 0
        limit_results = 500 if self._args.limit == -1 else self._args.limit

        driver_path = self._args.driver_path
        if not self._args.driver_path:
            try:
                driver_path = ChromeDriverManager().install()
            except ValueError:
                self.logger.error("Not able to download the driver which is compatible with your browser.")
                self.logger.info("Head to this site (https://chromedriver.chromium.org/downloads)"
                                 " and find your version driver and pass it with argument -d.")
                return

        print_lock = Lock()
        algo_obj = FastSearchAlgo(
            unavailable_text=self._args.unavailable_text,
            headless=self._args.windowed_browser,
            wait_time=self._args.browser_wait,
            suggested_ext=self._args.suggested_ext,
            output_path=self._args.output_folder,
            workers=1,
            result_range=limit_results,
            verbose=self._args.verbose,
            driver_path=driver_path,
            print_lock=print_lock
        )

        def update_result_count(count):
            self.result_count = count
            result_label.config(text=f"Results Scraped: {self.result_count}")
            result_label.update_idletasks()  # Force the GUI to update immediately

        def scrape_with_update():
            algo_obj.fast_search_algorithm([query], update_result_count, lambda: self.stop_scraping)

        scraping_thread = Thread(target=scrape_with_update)
        scraping_thread.start()

    def run(self):
        root = tk.Tk()
        root.title("Google Maps Scraper")

        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack(padx=10, pady=10)

        tk.Label(frame, text="Enter Search Query:", font=("Helvetica", 14)).grid(row=0, column=0, pady=10)
        query_entry = tk.Entry(frame, width=50, font=("Helvetica", 14))
        query_entry.grid(row=0, column=1, pady=10, padx=10)

        global result_label
        result_label = tk.Label(frame, text="Results Scraped: 0", font=("Helvetica", 12))
        result_label.grid(row=1, columnspan=2, pady=10)

        def on_start_click():
            query = query_entry.get()
            if query:
                self.stop_scraping = False
                self.scrape_maps_data(query)

        def on_stop_click():
            self.stop_scraping = True

        start_button = tk.Button(frame, text="Start Scraper", command=on_start_click, font=("Helvetica", 12))
        start_button.grid(row=2, column=0, pady=20)

        stop_button = tk.Button(frame, text="Stop Scraper", command=on_stop_click, font=("Helvetica", 12))
        stop_button.grid(row=2, column=1, pady=20)

        root.mainloop()

if __name__ == '__main__':
    App = GMapsScraper()
    App.arg_parser()
    App.run()
