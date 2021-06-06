import requests

# get the API KEY here: https://developers.google.com/custom-search/v1/overview
API_KEY = ""
# get your Search Engine ID on your CSE control panel
SEARCH_ENGINE_ID = ""
MAX_SEARCH_RESULTS = 0

class Gsearch:
    def __init__(self, the_query='devhub.co.il'):
        self.query = the_query
        self.search_results = ''
        self.titles_list = []
        self.links_list = []
        self.display_link = []
        self.snippet = []
        self.html_formatted_snippet = []
        self.html_formatted_link = []

    def results(self):
        # the search query
        query = self.query
        # using the first page
        page = 1
        # constructing the URL
        # doc: https://developers.google.com/custom-search/v1/using_rest
        # calculating start, (page=2) => (start=11), (page=3) => (start=21)
        start = (page - 1) * 4 + 1
        url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}&count={MAX_SEARCH_RESULTS}"

        # make the API request
        self.search_results = requests.get(url).json()

        data = self.search_results
        # get the result items
        search_items = data['items'] #['data']["items"]
        # iterate over 10 results found
        for search_item_index in range(len(search_items)):
            search_data = search_items[search_item_index]
            # get the page title
            self.titles_list.append(search_data["title"])
            # page snippet
            self.snippet.append(search_data["snippet"])
            # HTML snippet (bolded keywords)
            self.html_formatted_snippet.append(search_data["htmlSnippet"])
            # HTML link (bolded keywords)
            self.html_formatted_link.append(search_data["htmlFormattedUrl"])
            # extract the page url
            self.links_list.append(search_data["link"])
        return


if __name__ == "__main__":
    import configparser, os

    configparser_class = configparser.ConfigParser()
    thisfolder = os.path.dirname(os.path.abspath(__file__))
    config_file = configparser_class.read(os.path.join(thisfolder, 'config.ini'))
    # Google CSE keys
    SEARCH_ENGINE_ID = configparser_class.get('DEFAULT', 'GOOGLE_CSE_ENGINE_ID')
    API_KEY = configparser_class.get('DEFAULT', 'GOOGLE_CSE_API')

    gsearch = Gsearch(the_query='devhub')
    gsearch.results()
    # search_class.results()
    # print("links_list:", '\n'.join(gsearch.links_list + gsearch.titles_list))
    # print("titles_list:", '\n'.join(gsearch.titles_list))

