import requests
from bs4 import BeautifulSoup
from google import genai


def get_page_content(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    return response.content

def extract_links(soup):
        links = []
        for a_tag in soup.find_all("a", href=True):
            links.append(a_tag["href"])
        return links

def process_data(numpages):
    url = "https://www.wellsfargojobs.com/en/jobs"  # URL of the page to be scraped
    html_content = get_page_content(url)

    soup = BeautifulSoup(html_content, "html.parser")
    """links = extract_links(soup) """
    print("--------------------------------------------------\n")

    for x in range(int(numpages)):
        pageurl=url+"?page="+str(x+1)+"#results"
        print(pageurl)

        html_content = get_page_content(pageurl)
        soup = BeautifulSoup(html_content, "html.parser")
        with open("jobdata_file.html", "a") as file:
            file.write(clean_body_content(str(soup.select_one('body'))))


        print("------------------PAGE-------------------------------- :"+str(x))
def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")

    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Get text or further process the content
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content


def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
    ]
def geminiclient(prompt):

    client = genai.Client(api_key="AIzaSyD1thkapG6ZV4Ih7SfJQDUiqmLojzVvoGw")

    myfile = client.files.upload(file='jobdata_file.html')


    with open("jobdata_file.html","r") as file:
        file_content = file.read()
    print("\n\n\n")
    print(file_content)
    response = client.models.generate_content(
        model='gemini-2.5-pro-preview-03-25',
        contents=[file_content,prompt]
    )
    print(response.text)
    return response.text

if __name__ == "__main__":
    """process_data(40)"""
    geminiclient("How Many Vice President jobs?")
