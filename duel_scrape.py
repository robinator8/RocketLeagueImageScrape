import requests
import shutil
import os
from bs4 import BeautifulSoup as BS
def wikia_scrape():
    
    print('Wikia Scrape Started')
    items = ['wheels', 'toppers']
    colors = ['_black', '_burnt_sienna', '_cobalt', '_crimson', '_forest_green', '_grey', '_lime', '_orange', '_pink', '_purple', '_saffron', '_sky_blue', '_titanium_white']
    # Go through each item of items
    for key in items:
        # Get the tree for the item, and from that tree, find all the <div>'s with the wikia-gallery class
        # It will retry until it gets the correct tree
        while True:
            base_tree = get_tree_wikia(key)
            rarity_tree = base_tree.find_all('span', class_='mw-headline')
            a_tree = base_tree.find_all('div', class_='wikia-gallery')
            
            if len(a_tree) > 0:
                break
        
        # iterate over each div in the tree
        for a in a_tree:
            
            # from each div, find all the divs with the 'wikia-gallery-item' class
            b_tree = a.find_all('div', class_='wikia-gallery-item')
            
            # get the rarity by searching for the h2 somewhere above the current div
            rarity_span = a
            while True: 
                rarity_span = rarity_span.previous_sibling
                try:
                    tag_name = rarity_span.name
                except AttributeError:
                    tag_name = ''
                if tag_name == 'h2':
                    rarity = rarity_span.span.get_text().replace('Wheels', '').replace('Toppers', '').strip()
                    break
            # iterate through each of these dvis
            for b in b_tree:
                
                # from each div, find all <a>'s (anchors/hyperlinks)
                c_tree = b.find_all('a')
                
                # iterate through each of these anchors
                for c in c_tree:
                    
                    # gets the link (href attribute) from the anchor
                    href = c['href']
                    
                    # continues if the href doesn't contain file
                    # this prevents the program from trying to get items that only have one color, or at least one color on the page
                    # items with all the colors will link directly to that item page
                    if 'File:' not in href:
                        
                        # remove the /wiki/ at the start of the hyperlink
                        # our get_tree function already has this included, so we can remove it
                        href = href.replace("/wiki/", "")
                        
                        # gets a tree from the item page, and find all the div's with the 'wikia-gallery-item' class
                        d_tree = get_tree_wikia(href).find_all('div', class_='wikia-gallery-item')
                        
                        # iterate through each of these divs
                        for d in d_tree:
                            
                            # gets a tree from where the <a> 'href' attribute where <a> is the child of the current div
                            # from this new tree, find all the div's with the 'fullMedia' class
                            # these classes contain the links to the images
                            e_tree = get_tree_wikia(d.a["href"].replace("/wiki/", "")).find_all('div', class_='fullMedia')
                            
                            # iterate through each of these new divs
                            for e in e_tree:
                                
                                # set the link to the <a> of the div
                                link = e.a
                                
                                # set the picture src to the href of the anchor
                                src = link["href"]
                                
                                # set the name to the text of the link
                                name = link.get_text().strip().replace('.png', '').replace('_topper', '')
                
                                # sets the item name as follows - visor_sky_blue.png, it will find _sky_blue, remove it, which will leave it with visor.png
                                for color in colors:
                                    if color in name:
                                        item = name.replace(color, '')
                                        break
                                    
                                # where to save the files
                                file_path = "{}/{}/{}/{}.png".format(key, rarity, item, name)
                                
                                print('Getting', name)
                                
                                # the directory of the file_path
                                directory = os.path.dirname(file_path)
                                
                                # creates the directory if it doesn't exist
                                if not os.path.exists(directory):
                                    os.makedirs(directory)
                                    
                                # requests the image and the src link, until the status code is 200 (successful)
                                while True:
                                    r = requests.get(src, stream=True, headers={'User-agent': 'Mozilla/5.0'})
                                    if r.status_code == 200:
                                        break
                                # create/open the file at the file_path, and write the contents of the picture in the file
                                with open(file_path, 'wb') as f:
                                    r.raw.decode_content = True
                                    shutil.copyfileobj(r.raw, f)
    print('Wikia Scrape Done!')
                                    
# Gets the Beatiful Soup tree to make things easier         
def get_tree_wikia(sub):
    return get_tree("http://rocketleague.wikia.com/wiki/" + sub)

def rl_scrape():    
    # Started!
    print('rl Scrape started')
    items = {'bodies', 'wheels', 'boosts', 'antennas', 'decals', 'toppers'}
    
    # iterate through each item in items
    for key in items:
        
        # try to get the site tree until it returns properly
        while True:
            # tree is getting all the divs with the class 'rlg-items-item'
            tree = get_tree_rl(key).find_all('div', class_='rlg-items-item')
            if len(tree) > 0:
                break
        
        # iterate through each div in the tree
        for t in tree:
            # get the <img> tag
            img = t.img
            
            # get the imgae source from that <img> tag
            src = ("https://rocket-league.com" + img['src']).strip()
            
            # get the same of the item
            name = img.h2.get_text().strip().replace(" ", "_")
            
            # get the rarity of the item
            rarity = img.div.get_text().strip()
            
            # set up the file path
            file_path = "{}/{}/{}.png".format(key, rarity, name)
            
            # shows the current object
            print('Getting', name)
            
            # get the directory of the file path
            directory = os.path.dirname(file_path)
            
            # if the directory doesn't exist, create it
            if not os.path.exists(directory):
                os.makedirs(directory)
                
            # request the image at the src, until the status code returned is 200 (successful)
            while True:
                r = requests.get(src, stream=True, headers={'User-agent': 'Mozilla/5.0'})
                if r.status_code == 200:
                    break
            
            # create/open the file, and write the contents of the image downloaded into it
            with open(file_path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
    
    # Completed!
    print('rl Scrape Done!')
                
def get_tree_rl(sub):
    return get_tree("https://rocket-league.com/items/" + sub)

def get_tree(url):
    # Requests the page located at the url
    page = requests.get(url)
    
    # Returns the Beatiful SouptTree
    return BS(page.content, 'html.parser')      

def main():
    print('Duel Scrape Started')
    rl_scrape()
    wikia_scrape()
    print('Duel Scrape Completed')

main()