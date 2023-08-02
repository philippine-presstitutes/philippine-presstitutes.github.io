from string import punctuation
import json
import re

# Of certain users, did they have high activity (menitoed other users, posts heavily), low follower count, 
# and recent creation date -> these are indicators of accounts created to amplify pro-Duterte messaging

# make a count dictionary of commenter_id for comments and user for posts
# try for all of the ones that just had abuse comments

def create_dictionary():
    abuse_terms = {}
    with open('nlp/abuse-terms-all.txt') as abuse_terms_file:
        for line in abuse_terms_file:
            type = line.split()[-1].replace('type=', '')
            term = " ".join(line.split()[0:-1])
            abuse_terms[term] = {'type': type, 'count': 0}
    return abuse_terms

# helper function return true if the text has abuse
def is_abuse(newtext):
    abuse_terms = create_dictionary()
    for term in abuse_terms:
        if re.search(r"\b" + re.escape(term) + r"\b", newtext):
            return True
    return False

# put it to a json file 
def count_users(reporter, abuse):
    user_count = {}
    user_to_texts = {}

    # go through user in posts
    with open('extracted_data/'+reporter+'_posts_extracted.json') as data_file:    
        data = json.load(data_file)
        posts = data['posts']
        for post in posts:
            user = post['user'] 
            ogtext = post['text']
            newtext=" ".join([i.strip(punctuation) for i in ogtext.split()])
            if user in user_count:
                user_count[user] += 1
                user_to_texts[user].append(ogtext)
            elif not abuse or (abuse and is_abuse(newtext)):
                if user not in user_count:
                    user_count[user] = 0
                    user_to_texts[user] = []
                user_count[user] += 1
                user_to_texts[user].append(ogtext)

    # go through description of videos and comments
    # extracted_data/__posts_extracted_comments.html
    # combine the title and description of a video to one
    with open('extracted_data/'+reporter+'_posts_extracted_comments.json') as data_file:    
        data = json.load(data_file)
        posts = data['videos']
        for post in posts:
            user = post['user']
            title = post['title']
            description = post['description']
            newtext = " ".join([i.strip(punctuation) for i in title.split()])
            newtext += " ".join([i.strip(punctuation) for i in description.split()])
            
            if user in user_count:
                user_count[user] += 1
                user_to_texts[user].append(ogtext)
            elif not abuse or (abuse and is_abuse(newtext)):
                if user not in user_count:
                    user_count[user] = 0
                    user_to_texts[user] = []
                user_count[user] += 1
                user_to_texts[user].append(ogtext)

            if 'comments' in post:
                comments = post['comments']
                for comment in comments:
                    user = comment['commenter_id']
                    ogtext = comment['comment_text']
                    newtext=" ".join([i.strip(punctuation) for i in ogtext.split()])

                    if user in user_count:
                        user_count[user] += 1
                        user_to_texts[user].append(ogtext)
                    elif not abuse or (abuse and is_abuse(newtext)):
                        if user not in user_count:
                            user_count[user] = 0
                            user_to_texts[user] = []
                        user_count[user] += 1
                        user_to_texts[user].append(ogtext)
    
    # sort
    myKeys = list(user_count.keys())
    myKeys.sort()
    user_count = dict(sorted(user_count.items(), key=lambda item: item[1], reverse=True))

    top_25 = []
    max = 25
    for user in user_count:
        user_details = {"user": user,
                        "name": "",
                        "texts_count": user_count[user],
                        "texts": user_to_texts[user],
                        "account_created": "",
                        "follower_count": "",
                        "profile": "",
                        "notes": ","}
        top_25.append(user_details)
        max -= 1
        if max <= 0:
            break
    # add to json
    sublabel = "all"
    if abuse:
        sublabel = "abuse"

    # Write findings to files
    with open('social_media/'+reporter+'_users_'+sublabel+'.json', 'w') as file:
        json.dump(top_25, file, indent=4, sort_keys=True, default=str)

# get profiles of these people
def get_profiles():
    pass

count_users('ranada', True)
print("..........")
count_users('tordesillas', True)
# do a get_profile of top 10
# do a manual deep dive on the top 10 