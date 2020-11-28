from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts, taxonomies, users
from granary import microformats2
import re

MF2_URL_CLASSES = {
        'mf2_bookmark-of' : 'response u-bookmark-of h-cite'
        #'mf2_repost-of' : #'response'
        #'mf2_read-of': #
        #'mf2_photo' :
        #'mf2_like-of' :
        #'mf2_in-reply-to' : #
        }

# pull relevant URL out of garbled metadata
def parse_response(respstring):
	#print respstring
	possible_urls = re.findall(r'(http[s?]://[^ \t\n\r\f\v\"]+)', respstring)
	if len(possible_urls) > 1:
		print('too many URLs')
		for i in possible_urls:
			print(i)
	return possible_urls[0]

# find and return particular custom field
def process_mf2_data(post, valkey):
	#print post.custom_fields
    for i in post.custom_fields:
        if i['key'] == valkey:
            i['key'] = parse_response(i['value'])
    return post


# remove id from xmlrpc returned custom_fields, return dict instead of list
def get_clean_custom_fields(post):
	fields = {}
	for field in post.custom_fields:
		#confirm if dictionary
		fields[field['key']] = field['value']
	return fields

#prepend response properties URL to post content
def insert_url_content(post, mf2type):
    urlstring = '<section class=\"' + MF2_URL_CLASSES[mf2type] + '\"><a href=\"' + parse_response(post.custom_fields[mf2type]) + '\" class = \"p-name u-url\">'
    
	
mf2dict = {}
mf2dict["items"] = []

client = Client('https://pilch.me/xmlrpc.php', 'pilch', 'wdEFhUrLTr4N')
# Get profile of user that is logged in
blogauthor = client.call(users.GetProfile())
author = {}
author['url'] = 'https://pilch.me/author/pilch' #blogauthor.url
author['type'] = "person"
author['id'] = blogauthor.id
author['nickname'] = blogauthor.nickname
#author['image'] = {}
#author['image']['url'] = #image url - xmlrpc does not return this
author['displayName'] = blogauthor.display_name

# print term names and IDs
#terms = client.call(taxonomies.GetTerms('kind'))
#for term in terms:
#	print "name: " + term.name + ", id: " + term.id

myposts = client.call(posts.GetPosts({'number': 5, 'offset': 0, 'post-status': 'publish'}))
for post in myposts:
	#print post.post_status
    postdict = {}
    customfields = {}
    postdict['published'] = post.date #date
    postdict['verb'] = 'post'
    postdict['id'] = post.id
    postdict['url'] = post.link #url
    postdict['title'] = post.title
    postdict['attributedTo'] = author
    customfields = get_clean_custom_fields(post)
    print(customfields)
    #postdict['object']
    for trm in post.terms:
    	#print trm.name
        if trm.name == 'Bookmark':
            print( 'Bookmark')
            process_mf2_data(post, 'mf2_bookmark-of')
        elif trm.name == 'Repost':
            print( 'Repost')
            process_mf2_data(post, 'mf2_repost-of')
        elif trm.name == 'Read':
            print( 'Read')
            process_mf2_data(post, 'mf2_read-of')
        elif trm.name == 'Image':
            print( 'Image')
            process_mf2_data(post, 'mf2_photo')
        elif trm.name == 'Like':
            print( 'Like')
            process_mf2_data(post, 'mf2_like-of')
        elif trm.name == 'Reply':
            print( 'Reply')
            process_mf2_data(post, 'mf2_in-reply-to')
	#print post.custom_fields
	#print post.post_status
	#print "content: " + post.content + "\n\tterms: " + post.terms + "\n"
    #print( "\n")
    postdict['content'] = post.content
    itemdict = {}
    itemdict['@context'] = 'https://www.w3.org/ns/activitystreams'
    itemdict['object'] = postdict
    mf2dict['items'].append(itemdict)
	
print(mf2dict)
print('\n')
mf2 = microformats2.object_to_json(mf2dict)
print(mf2)

#types = client.call(posts.GetPostTypes())
#print types
#post, page, attachment
