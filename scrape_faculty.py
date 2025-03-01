#imports required libraries 
import requests #fetches web pages
from bs4 import BeautifulSoup #get beautiful soup library from bs4 to parse html of webpages
import re #for regular expressions
import pandas as pd #for saving data to CSV
import spacy #for natural language processing (nlp)

#load spaCy English language model 
nlp = spacy.load("en_core_web_sm")

#fetch department faculty page
#(define a function) (name of function) (perameters of function - i.e it's taking in urls)
def fetch_faculty_links(url):
    """
    Fetches the list of faculty profile links from the department's faculty page.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all faculty profile links
        profile_links = []
        for link in soup.find_all('a', href=True):
            # Adjust this condition based on the website
            if "faculty" in link['href'] or "profile" in link['href'] or "persons" in link['href']:
                # If the link is already a full URL, use it as-is
                if link['href'].startswith("http"):
                    profile_links.append(link['href'])
                else:
                    # If the link is relative, construct the full URL
                    base_url = "https://www.roehampton.ac.uk/"  # Replace with the actual base URL
                    full_url = base_url + link['href']
                    profile_links.append(full_url)

        print(f"Found {len(profile_links)} profile links.")
        return profile_links
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

#scrape faculty profiles
def scrape_profile(profile_url):
    try: 
        response = requests.get(profile_url)
        response.raise_for_status() #raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')

        #try to find research interests using common headings
        research_interests = ""
        headings = soup.find_all(['h2', 'h3', 'h4'])
        for heading in headings:
            if "research" in heading.text.lower() or "interests" in heading.text.lower():
                next_element = heading.find_next()
                if next_element:
                    research_interests = next.element.text.strip()
                    break

        if not research_interests: #if you cant find the heading
            page_text = soup.get_text().lower() #get the text from the page
            doc = nlp(page_text) #process text with spacy 

            for sent in doc.sents: #for the senteses in the document
                if "research" in sent.text.lower() or "interest" in sent.text.lower():
                    research_interests = sent.text.strip()
                    break
        return research_interests
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {profile_url}: {e}")
        return ""

def save_to_csv(data,filename):
    df = pd.DataFrame(data, columns=["Profile URL", "Research Interests"])
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}!")

def main():
    # Step 1: Fetch faculty profile links
    department_url = "https://www.roehampton.ac.uk/research/research-and-knowledge-exchange-centres/research-centre-for-inclusive-humanities/staff/"  # Replace with the actual URL
    profile_links = fetch_faculty_links(department_url)

    # Step 2: Scrape each profile
    data = []
    for link in profile_links:
        profile_url = f"https://example-university.edu{link}"  # Adjust if links are relative
        research_interests = scrape_profile(profile_url)
        data.append([profile_url, research_interests])

    # Step 3: Save the data
    save_to_csv(data, "faculty_research_interests.csv")

# Run the script
if __name__ == "__main__":
    main()

    


