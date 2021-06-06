from duckpy import Client

class DuckDuckGoSearch:
    def __init__(self, the_query='devhub.co.il'):
        self.query = the_query
        self.client = Client()
        # self.result_info = []

    def search_method(self):
        results = self.client.search(self.query)
        return results


if __name__ == "__main__":
    print(f"The application started for testing from {__file__}.")

    google_search = DuckDuckGoSearch('devhub israel')
    search = google_search.search_method()


    # urls_list = [r'https://rnd.ebay.co.il/', r'https://www.ebay.co.il/sell/israel-ebay-shipping-platform-manual/', r'https://www.gov.il/en/departments/israel_national_cyber_directorate']
    # website_description = Search()
    # for links_index in urls_list:
    #     website_description.search_description(links_index)
    #     print("Link: {}\nTitle:{}\nDescription:{}".format(links_index,
    #                                                        website_description.website_title,
    #                                                        website_description.website_description))

    print("Finished.")