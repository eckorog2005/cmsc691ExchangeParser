__author__ = 'roger'

import sys
import codecs
import xml.etree.cElementTree as etree
import xml.dom.minidom as minidom
#import lxml as etree
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
       self.hasEdge = False

    def add_accepted_answer(self, postID):
        self.acceptedAnswersPost.append(postID)

    def add_tag_count(self, tagName):
        if tagName in self.tags:
            self.tags[tagName] += 1
        else:
            self.tags[tagName] = 1

    def get_top_tag(self):
        topTagName = ''
        topAmount = 0
        for tagName, amount in self.tags.items():
            if amount > topAmount:
                topAmount = amount
                topTagName = tagName
        return topTagName

class Post:
    def __init__(self, id, ownerId, accepted):
        self.id = id
        self.ownerId = ownerId
        self.accepted = accepted
        self.tags = []

    def add_tags(self, tags):
        self.tags = tags

#list of users
users = {}
posts = {}

#get command line arguments for files
usersFile = 'Users.xml'
postsFile = 'Posts.xml'
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
                if row.attrib.get('Tags', None) is not None:
                    tags = row.attrib['Tags']
                    tags = tags.replace('><', ',')
                    tags = tags.replace('>', '')
                    tags = tags.replace('<', '')
                    tagList = tags.split(',')
                    owner = users[row.attrib['OwnerUserId']]
                    for tag in tagList:
                        owner.add_tag_count(tag)
                    post.add_tags(tagList)
                posts[post.id] = post
        elif postType == '2':
            parentId = row.attrib['ParentId']
            post = posts.get(parentId, None)
            if post is not None:
                if post.accepted == row.attrib['Id'] and row.attrib.get('OwnerUserId', None) is not None:
                    user = users[row.attrib['OwnerUserId']]
                    user.add_accepted_answer(post.ownerId)
                    user.hasEdge = True
                    users[post.ownerId].hasEdge = True
                    for tag in post.tags:
                        user.add_tag_count(tag)
                    del posts[parentId]
f.close()
del posts

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
edges = etree.SubElement(gexf, 'edges')

#build nodes and edges
counter = 0
usersWithNoEdge = 0
for user in users.values():
    if not user.hasEdge:
        usersWithNoEdge += 1
        continue
    node = etree.SubElement(nodes, 'node')
    node.set('id', user.id)
    node.set('label', user.displayName)
    attvalues = etree.SubElement(node, 'attvalues')
    topTag = user.get_top_tag()
    if topTag is not '':
        attvalue = etree.SubElement(attvalues, 'attvalue')
        attvalue.set('for', '0')
        attvalue.set('value', topTag)
    attvalue = etree.SubElement(attvalues, 'attvalue')
    attvalue.set('for', '1')
    attvalue.set('value', user.reputation)
    attvalue = etree.SubElement(attvalues, 'attvalue')
    attvalue.set('for', '2')
    attvalue.set('value', user.upVotes)
    attvalue = etree.SubElement(attvalues, 'attvalue')
    attvalue.set('for', '3')
    attvalue.set('value', user.downVotes)
    for link in user.acceptedAnswersPost:
        edge = etree.SubElement(edges, 'edge')
        edge.set('id', str(counter))
        edge.set('source', user.id)
        edge.set('target', link)
        counter += 1
del users

#write xml file (gexf file)
tree = etree.ElementTree(gexf)
f = codecs.open(dataLocation+'graph.gexf', 'w', "utf-8")
f.write(minidom.parseString(etree.tostring(gexf, encoding="utf-8")).toprettyxml())
f.close()
f = open(dataLocation+'numberOfUsersWithNoEdge.txt', 'w')
f.write(str(usersWithNoEdge))
f.close()
