import requests
from bs4 import BeautifulSoup

# Supabase API details
supabase_url = "https://ailogxgeobaebkemxgho.supabase.co"
supabase_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFpbG9neGdlb2JhZWJrZW14Z2hvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyNTQ0MDE3MSwiZXhwIjoyMDQxMDE2MTcxfQ.rME9-r7PkqiGozyPHjlMwmv334gb2hq33Ox-BzyStoA"

# URL of the FlightAware airport delays webpage
url = "https://uk.flightaware.com/live/airport/delays"

# Create headers to mimic a real browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


# Function to insert data into Supabase
def insert_into_supabase(airport_name, airport_code, delay_info):
    data = {
        "airport_name": airport_name,
        "airport_code": airport_code,
        "delay_info": delay_info
    }

    headers = {
        "Content-Type": "application/json",
        "apikey": supabase_api_key,
        "Authorization": f"Bearer {supabase_api_key}"
    }

    response = requests.post(f"{supabase_url}/rest/v1/airport_delays", headers=headers, json=data)

    if response.status_code == 201:
        print(f"Successfully inserted: {airport_name} ({airport_code})")
    else:
        print(f"Failed to insert data: {response.status_code} - {response.text}")

# Function to call the delete function in Supabase
def delete_old_data():
    url = f"{supabase_url}/rest/v1/deletedata"
    headers = {
        "apikey": supabase_api_key,
        "Authorization": f"Bearer {supabase_api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print("Old data deleted successfully")
    else:
        print(f"Failed to delete old data: {response.status_code}, {response.text}")



# Send a GET request to the FlightAware URL
try:

    delete_old_data()

    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the table containing the airport delays information
        table = soup.find("table", class_="prettyTable airport_delays")

        if table:  # Check if the table is found
            # Find all rows in the table body
            rows = table.find_all("tr")

            # Iterate through each row to extract the details
            for row in rows:
                # Extract the airport name and code
                airport_name_tag = row.find("span", itemprop="name")
                if airport_name_tag:
                    airport_name = airport_name_tag.text.strip()
                    airport_code = row.find("a", itemprop="url").text.strip()

                    # Extract the delay information
                    delay_info = row.find("ul")  # Check if there are multiple delays listed
                    if delay_info:
                        delay_items = delay_info.find_all("li")
                    else:
                        delay_items = [row.find("td").text.strip().split("currently experiencing")[-1].strip()]

                    # Join the delay information as a single string
                    delay_text = "; ".join([delay.text if hasattr(delay, "text") else delay for delay in delay_items])

                    # Insert data into Supabase
                    insert_into_supabase(airport_name, airport_code, delay_text)
        else:
            print("Table element not found. The website structure might have changed.")

    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred while fetching the webpage: {e}")
