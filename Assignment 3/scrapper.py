import re
import json
from urllib import request
from html import unescape
from collections import defaultdict

def extract_book_name(html) -> str:
    """
    Extract name of the book from html script

    -i: html script -> string
    -o: book name -> string
    """

    # Regex for Book Name Div --> H1 tags
    rbook_name = re.compile(r'(<h1.*>)((.|\n)*)(<\/h1>)')
    # Select the content between tags and strip from non-words
    book_name = re.search(pattern= rbook_name, string= html).group(2).strip("\n").strip(" ")
    # Turn HTML entities to non-word utf-8 character
    book_name = unescape(book_name)

    return book_name

def extract_authors(html) -> list:
    """
    Extracting list of authors from html script

    -i: html script -> string
    -o: authors -> list
    """

    # Regex for Authors Div -> Unique div 
    rbook_authors = re.compile(r'<span itemprop="name">(.+?)(?=<\/span>)') # Only content between tags are selected via paranthesis 
    # Findall function returns a list
    authors = re.findall(pattern= rbook_authors, string= html)
    # Turn HTML entities to non-word utf-8 character
    authors = unescape(authors)

    return authors

def extract_description(html) -> str:
    """
    Extracting description content

    -i: HTML script -> string
    -o: description content -> string
    """

    # Regex for Description Div -> unique id
    rdescription_container = re.compile(r'((?<=<div id="description" class="readable stacked" style="right:0">))((.|\n)+?)((?=\s{6}<\/div>))')
    
    # Try if the book has description or not
    try: 
        description_cont = re.search(pattern= rdescription_container, string= html).group(2)
        # Regex for non-displayed spans
        rspan = re.compile(r'(<span.+?style="display:none">)((.|\n)+?)(<\/span>)')

        # Try it has preview or not
        # Since there are two spans, if length of description is short, there is no non-displayed span
        try: # if
            span = re.search(pattern=rspan, string= description_cont).group(2)
        
        except AttributeError: #If description is short
            rspan = re.compile(r'(<span.+?(style="display:none")?>)((.|\n)+?)(<\/span>)') 
            span = re.search(pattern=rspan, string= description_cont).group(3)

        # Substitute HTML tags, newlines and space more than 2 characters with space
        description = re.sub(r'<.+?>|\n|\s{2,}', " ", span)
        # Turn HTML entities to non-word utf-8 character
        description = unescape(description)

    # If no description, empty description
    except AttributeError:
        description = " "

    return description

def extract_genres(html) -> dict:
    """
    Extracting Genres and their votes as a dictionary

    -i: HTML script -> string
    -o: dict -> Genres-> str 
                Votes -> int
    """

    # Regex for Containers including Genres and Votes
    rgenre_container = re.compile(r'<div class="elementList ">((.|\n)+?)<div class="clear">')

    # List of divs containing different genres and their votes
    genre_containers = re.findall(pattern=rgenre_container,string=html)
    # Regex for Name of Genre in given div
    rgenres = re.compile(pattern= r'<a class="actionLinkLite bookPageGenreLink" .+?>((?:.|\n)+?)<\/a>')
    # Regex for Vote of that Genre in given div
    rvotes = re.compile(pattern=r'<a title="(\d*).+?>') 

    # Genre dictionary -> keys: Genres, values: votes
    # Default dict -> int enables incrementing without key error
    genres = defaultdict(int)
    for container, _ in genre_containers:

        # List of genres in one container
        genre = re.findall(pattern=rgenres, string=container) # One genre might have supra-genres eg. Fiction->Fantasy
        # Exract its vote
        votes = re.search(pattern=rvotes, string=container).group(1) 

        # Append vote count for all given genres 
        for g in genre:
            genres[g] += int(votes)

    return genres

def extract_recommendation(html) -> list:
    """
    Exracting 18 recommendation as a list

    -i: html script -> string
    -o: recommmendations -> list
    """

    # Regex for Recommended Div -> Unique div class='carouselRow' <ul> within 
    rrecommended_container = re.compile(r'<div class=\'carouselRow\'.+?>\n<ul>((.|\n)+?)</ul>')

    # Select the content in between unordered list
    container = re.search(pattern=rrecommended_container, string=html).group(1)
    # For each list item, recommendation is in alt tag of images
    recommended = re.findall(pattern=r'alt=\"(.+?)\"', string=container)  
    # Turn HTML entities to non-word utf-8 character
    recommended = [unescape(book) for book in recommended]

    return recommended

def html_parser(URL) -> dict:
    """
    Send request to URL and parse the content, then return a dictionary of relevant info

    -i: URL -> string
    -o: info dict -> Title -> string
                     Authors -> list
                     Description -> string
                     Genres -> dict
                     Recommendations -> list

    """

    # Send request for HTML script
    resp = request.urlopen(URL)
    # Read script
    data = resp.read()
    # Decode data to string with utf-8 encoding
    html = data.decode("utf-8")

    # Check if HTML, if not return None
    if not html.startswith("<!DOCTYPE html>"): return

    # Book name
    book_name = extract_book_name(html)

    # Author(s)
    authors = extract_authors(html)

    # Description
    description = extract_description(html)

    # Genres
    genres = extract_genres(html)

    # Recommended Books
    recommended = extract_recommendation(html)

    info = {
        "Title": book_name, 
        "Authors": authors,
        "Description": description,
        "Genres": genres,
        "Recommended": recommended,
        "URL": URL
    }

    return info

def main():

    # Get urls from achieve
    with open("books.txt") as f_in:
        urls = f_in.readlines()
    
    # Strip
    urls = [url.strip('\n') for url in urls]

    # Storage for Books
    books = dict()

    # Iterate over url list
    for url in urls:
        
        # Extract html script as string
        info = html_parser(url)

        # Check if HTML
        if not info:
            continue

        # Book name
        book_name = info["Title"]

        # Author(s)
        authors = info["Authors"]

        # Description
        description = info["Description"]

        # Genres
        genres = info["Genres"]

        # Recommended Books
        recommended = info["Recommended"]

        books[book_name] = {
            "Authors": authors,
            "Description": description,
            "Genres": genres,
            "Recommended": recommended,
            "URL": url
        }

        # Dump content in json file
        with open("books.json","w",encoding="utf-8") as f:
            json.dump(books,f,ensure_ascii = False)

if __name__ == "__main__":
    print("Parsing data...")
    main()