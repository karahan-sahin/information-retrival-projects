import re
import string

def tokenize(file):
    # -i: file
    # -o: dictionary: {currentID: {"title": title_tokens, "body": body_tokens}}

    # Open and read the file 
    f = open(file, "r", encoding="latin-1")
    text = f.read()

    # All news in the document
    news = {}


    # News start to end
    # <REUTERS TOPICS="NO" LEWISSPLIT="TRAIN" CGISPLIT="TRAINING-SET" OLDID="5546" NEWID="3">
    reuter_start = re.compile(
        r"<REUTERS [(A-Z)(\W)]*(\d*)\W NEWID=\W(\d*)\W>(.|\n)*?(</REUTERS>)")
    reuter_matches = re.finditer(reuter_start, text)


    for match in reuter_matches:

        # String containing match start and end
        s = match.start()
        e = match.end()

        document = text[s:e]


        # ID
        ## Find tag and Assign currentID
        start_tag = re.search(r"NEWID=\W(\d*)\W>", document)  # LIST
        currentID = int(start_tag.group(1))

        # TITLE
        try:
            # Capture title tag and content
            title = re.search(r"(<TITLE>)((.|\n)*?)(</TITLE>)", document)  # LIST
            title_content = title.group(2).lower() # case-folded content
        # In case of NO TITLE assign Empty content
        except AttributeError:
            title_content = " "
            pass

        
        # Get stopwords (list)
        stopwords = open("stopwords.txt", "r").read()
        stopwords = stopwords.split("\n")

        # Split punctuations
        r = re.compile(r'[\s{}]+'.format(re.escape(string.punctuation))) 

        
        # Title tokens removal
        title_tokens_raw = re.split(r, title_content)    # Split non-word and digits
        title_tokens = [token for token in title_tokens_raw 
                if token not in stopwords                # Remove stopword
                ]
        
        # BODY
        try:
            # Capture body tag and content
            body = re.search(r"(<BODY>)((.|\n)*?)(</BODY>)", document)  # LIST
            # Case folding and selecting content regex group
            body_content = body.group(2).lower() # case-folded
        # In case of NO BODY assign Empty content
        except AttributeError:
            body_content = " "
            pass

        # Body tokens removal
        body_tokens_raw = re.split(r, body_content) # Split non-word and digits
        body_tokens = [token for token in body_tokens_raw
                if token not in stopwords           # Remove stopwords
                ]

        # A dictionary as the key: ID and value: dict{title, body}
        news_update = {currentID: {"title": title_tokens, "body": body_tokens}}

        # Update All news
        news.update(news_update)

    f.close()

    return news



