__author__ = 'roger'

import sys
import xml.etree.cElementTree as etree
import logging

#define user class
class User:
    def __init__(self, id, reputation, displayName, upVotes, downVotes):
       self.id = id
       self.reputation = reputation
       self.displayName = displayName
       self.upVotes = upVotes
       self.downVotes = downVotes
       self.acceptedAnswersPost = []
       self.tags = {}

    def add_accepted_answer(self, postID):
        self.acceptedAnswersPost.append(postID)

    def add_tag_count(self, tagName):
        if tagName in self.tags:
            self.tags[tagName] += 1
        else:
            self.tags[tagName] = 1

class Post:
    def __init__(self, id, ownerId, accepted):
        self.id = id
        self.ownerId = ownerId
        self.accepted = accepted

#list of users
users = {}
posts = {}

#get command line arguments for files
usersFile = '/Users.xml'
postsFile = '/Posts.xml'
dataLocation = ''
if len(sys.argv) == 2:
    dataLocation = sys.argv[1]
else:
    print("default usage : StackExchangeConverter.py dataDirectory")
    sys.exit(2)

# open user file
f = open(dataLocation+usersFile, 'r')
tree = etree.iterparse(f)
for event, row in tree:
    if len(row.attrib.keys()) > 0:
        user = User(row.attrib['Id'], row.attrib['Reputation'], row.attrib['DisplayName'], row.attrib['UpVotes'], row.attrib['DownVotes'])
        users[user.id] = user
f.close()

# open post file
f = open(dataLocation+postsFile, 'r')
tree = etree.iterparse(f)
for event, row in tree:
    if len(row.attrib.keys()) > 0:
        postType = row.attrib['PostTypeId']
        if postType == '1':
            #TODO parse tags out
            if row.attrib.get('AcceptedAnswerId', None) is not None and row.attrib.get('OwnerUserId', None) is not None:
                post = Post(row.attrib['Id'], row.attrib['OwnerUserId'], row.attrib['AcceptedAnswerId'])
                posts[post.id] = post
        elif postType == '2':
            parentId = row.attrib['ParentId']
            post = posts.get(parentId, None)
            if post is not None:
                if post.accepted == row.attrib['Id'] and row.attrib.get('OwnerUserId', None) is not None:
                    users[row.attrib['OwnerUserId']].add_accepted_answer(parentId)
                    del posts[parentId]

#build xml file
gexf = etree.Element('gexf', xmlns="http://www.gexf.net/1.2draft", version="1.2")
gexf.set('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
gexf.set('xsi:schemaLocation', "http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd")
meta = etree.SubElement(gexf, 'meta', lastmodifieddate="2015-02-15")
etree.SubElement(meta, 'creator').text = 'Stephanie Durand and Roger Lamb'
etree.SubElement(meta, 'description').text = 'Stack Exchange Network'
graph = etree.SubElement(gexf, 'graph', defaultedgetype="directed")
attributes = etree.SubElement(graph, 'attributes')
attributes.set('class', "node")
etree.SubElement(attributes, 'attribute', id="0", title="Tag", type="string")
attribute = etree.SubElement(attributes, 'attribute', id="1", title="Reputation", type="integer")
etree.SubElement(attribute, 'default').text = 0
attribute = etree.SubElement(attributes, 'attribute', id="2", title="UpVote", type="integer")
etree.SubElement(attribute, 'default').text = 0
attribute = etree.SubElement(attributes, 'attribute', id="3", title="DownVote", type="integer")
etree.SubElement(attribute, 'default').text = 0
nodes = etree.SubElement(gexf, 'nodes')

#build nodes
for user in users.values():
    node = etree.SubElement(nodes, 'node')
    node.set('id', user.id)
    node.set('label', user.displayName)
    etree.SubElement(node, 'attvalues')

#write xml file (gexf file)
tree = etree.ElementTree(gexf)
tree.write(dataLocation+'/graph.gexf', encoding="utf-8", xml_declaration=True)
