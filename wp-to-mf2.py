from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts, taxonomies, users
from granary import microformats2
import sys,re,string

DEBUG = 1
MF2_TYPES = {
        'bookmark' : 'mf2_bookmark-of',
        'repost' : 'mf2_repost-of',
        'read' : 'mf2_read-of',
        'image' : 'mf2_photo',
        'Like': 'mf2_like-of',
        'Reply' : 'mf2_in-reply-to',
        #TODO: add watch
        }

MF2_URL_CLASSES = {
        'mf2_bookmark-of' : 'response u-bookmark-of h-cite',
        'mf2_repost-of' : 'h-cite response u-repost-of', #'response'
        'mf2_read-of': 'h-cite response u-read-of',
        'mf2_photo' : 'response attachment-large u-photo',
        'mf2_like-of' : 'response u-like-of h-cite',
        'mf2_in-reply-to' : 'h-cite response u-in-reply-to',
        #TODO: add watch
        }
		
#('url', 'name')
MF2_PARSE_FIELDS = {
        'mf2_bookmark-of' : ('url', 'name'),
        #'mf2_repost-of' : 'h-cite response u-repost-of', #'response'
        #'mf2_read-of': 'h-cite response u-read-of',
        #'mf2_photo' : 'response attachment-large u-photo',
        #'mf2_like-of' : 'response u-like-of h-cite',
        #'mf2_in-reply-to' : 'h-cite response u-in-reply-to',
    }

#split garbled string, pull out relevant items
def parse_response_list(respstring, valkey):
    strlist = respstring.split('\"')
    retdict = {}
    i = 0
    while i < len(strlist):
        if strlist[i] in MF2_PARSE_FIELDS[valkey]:
            retdict[strlist[i]] = strlist[i+2]
        i += 1
    return retdict

# pull relevant URL out of garbled metadata
def parse_response_re(respstring):
	#print respstring
	possible_urls = re.findall(r'(http[s?]://[^ \t\n\r\f\v\"]+)', respstring)
	if len(possible_urls) > 1:
		debug_print('too many URLs')
		for i in possible_urls:
			debug_print(i)
	return possible_urls[0]

# find and return particular custom field
def process_mf2_data(fields, valkey):
	#print post.custom_fields
    for i in fields.keys():
        if i == valkey:
            #TODO - add logic for keys in MF2_PARSE_FIELDS
            if valkey == 'mf2_bookmark-of':
                fields[valkey] = parse_response_list(fields[valkey], valkey)
            else:
                fields[valkey] = parse_response_re(fields[valkey])
    return fields


# remove id from xmlrpc returned custom_fields, return dict instead of list
# only returns mf2-relevant data
def get_clean_custom_fields(post):
	fields = {}
	for field in post.custom_fields:
		#confirm if dictionary
		fields[field['key']] = field['value']
	keylist = fields.copy().keys()
	for i in keylist:
		if not i.startswith('mf2'):
			debug_print('popping ' + i)
			fields.pop(i)
	return fields

#prepend response properties URL to post content
def insert_url_content(post, customfields, mf2type):
    usesection = ('Bookmark', 'Like', 'Reply')
    mf2typestr = MF2_TYPES[mf2type]
    if mf2type in usesection:
        urlstringstart = '<section class=\"' + MF2_URL_CLASSES[mf2typestr] + '\"><a href=\"' + customfields[mf2typestr]['url'] + '\" class = \"p-name u-url\">'
        urlstringmid = customfields[mf2typestr]['name'] + '</a>'
        strend = '<p>' + post.content + '</p></section>'
        return urlstringstart + urlstringmid + strend
    #elif mf2type = 'Image':
        urlstringstart = '<img class=\"' + MF2_URL_CLASSES[mf2typestr] + '\"' + customfields[]+ '>'
    else: #default
        return post.content
    

    #section only seems to work on bookmark and like and reply, others put class directly in href linka
    #TODO: parse name from custom field
    
def debug_print(string):
    if DEBUG:
        print(string)
	
blogurl = sys.argv[1]
bloguser = sys.argv[2]
blogpassword = sys.argv[3]

mf2dict = {}
mf2dict["items"] = []

client = Client(blogurl + '/xmlrpc.php', bloguser, blogpassword)
# Get profile of user that is logged in
blogauthor = client.call(users.GetProfile())
author = {}
#author['url'] = blogauthor.url #no URL defined in XML-RPC
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

totalitems = 5

myposts = client.call(posts.GetPosts({'number': totalitems, 'offset': 0, 'post-status': 'publish'}))
for post in myposts:
	#print post.post_status
    postdict = {}
    customfields = {}
    postdict['published'] = post.date #date
    postdict['verb'] = 'post'
    postdict['id'] = post.link #url 
    postdict['url'] = post.link #url also
    postdict['displayName'] = post.title
    postdict['author'] = author
    customfields = get_clean_custom_fields(post)
    debug_print(customfields)
    #postdict['object']
    for trm in post.terms:
    	#print trm.name
        if trm.name in MF2_TYPES:
            debug_print(trm.name)
            customfields = process_mf2_data(customfields, trm.name)
        #TODO: add watch
	#print post.custom_fields
	#print post.post_status
	#print "content: " + post.content + "\n\tterms: " + post.terms + "\n"
    #print( "\n")
    postdict['content'] = post.content
    #postdict['object'] = customfields
    itemdict = {}
    itemdict['@context'] = 'https://www.w3.org/ns/activitystreams'
    itemdict['object'] = postdict
    mf2dict['items'].append(itemdict)
	
mf2dict['totalItems'] = totalitems
debug_print(mf2dict)
debug_print('\n')
mf2 = microformats2.object_to_json(mf2dict)
print(mf2)

#types = client.call(posts.GetPostTypes())
#print types
#post, page, attachment
