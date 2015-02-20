__author__ = 'roger'

import sys
import codecs
import xml.etree.cElementTree as etree
import xml.dom.minidom as minidom
import distutils.util

#define user class
class User:
    def __init__(self, id, reputation, displayName, upVotes, downVotes):
        self.id = id
        self.reputation = reputation
        self.displayName = displayName
        self.upVotes = upVotes
        self.downVotes = downVotes
        self.answered = []
        self.tags = {}
        self.hasEdge = False

    def add_answer(self, postID):
        self.answered.append(postID)

    def add_tag_count(self, tagName):
        if tagName in self.tags:
            self.tags[tagName] += 1
        else:
            self.tags[tagName] = 1

    def get_top_tags(self):
        # topTagName = ''
        # topAmount = 0
        # for tagName, amount in self.tags.items():
        #     if amount > topAmount:
        #         topAmount = amount
        #         topTagName = tagName
        # return topTagName
        tagList = []
        for tagName, amount in self.tags.items():
            tagList.append(Tag(tagName,amount))
        return sorted(tagList, key=lambda tagobj: tagobj.number, reverse=True)


class Post:
    def __init__(self, id, ownerId, accepted):
        self.id = id
        self.ownerId = ownerId
        self.accepted = accepted
        self.tags = []

    def add_tags(self, tags):
        self.tags = tags

class Tag:
    def __init__(self, tag, number):
        self.tag = tag
        self.number = number

#list of users
users = {}
posts = {}
tagsDict = {}

#get command line arguments for files
usersFile = 'Users.xml'
postsFile = 'Posts.xml'
dataLocation = ''
acceptedOnlyAnswers = 1
if len(sys.argv) == 3:
    dataLocation = sys.argv[1]
    acceptedOnlyAnswers = distutils.util.strtobool(sys.argv[2])
else:
    print("default usage : StackExchangeConverter.py dataDirectory acceptedAnswersOnlyFlag")
    sys.exit(2)

# open user file
f = open(dataLocation + usersFile, 'r')
tree = etree.iterparse(f)
for event, row in tree:
    if len(row.attrib.keys()) > 0:
        user = User(row.attrib['Id'], row.attrib['Reputation'], row.attrib['DisplayName'], row.attrib['UpVotes'],
                    row.attrib['DownVotes'])
        users[user.id] = user
f.close()

# open post file
f = open(dataLocation + postsFile, 'r')
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
                if acceptedOnlyAnswers and post.accepted == row.attrib['Id'] and \
                                row.attrib.get('OwnerUserId', None) is not None:
                    user = users[row.attrib['OwnerUserId']]
                    user.add_answer(post.ownerId)
                    user.hasEdge = True
                    users[post.ownerId].hasEdge = True
                    for tag in post.tags:
                        user.add_tag_count(tag)
                    del posts[parentId]
                elif not acceptedOnlyAnswers and row.attrib.get('OwnerUserId', None) is not None:
                    user = users[row.attrib['OwnerUserId']]
                    user.add_answer(post.ownerId)
                    user.hasEdge = True
                    users[post.ownerId].hasEdge = True
                    for tag in post.tags:
                        user.add_tag_count(tag)
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
etree.SubElement(attributes, 'attribute', id="0", title="Tag1", type="string")
etree.SubElement(attributes, 'attribute', id="1", title="Tag2", type="string")
etree.SubElement(attributes, 'attribute', id="2", title="Tag3", type="string")
attribute = etree.SubElement(attributes, 'attribute', id="3", title="Reputation", type="integer")
etree.SubElement(attribute, 'default').text = 0
attribute = etree.SubElement(attributes, 'attribute', id="4", title="UpVote", type="integer")
etree.SubElement(attribute, 'default').text = 0
attribute = etree.SubElement(attributes, 'attribute', id="5", title="DownVote", type="integer")
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
    topTags = user.get_top_tags()
    counterFor = 0
    for tag in topTags[:3]:
        attvalue = etree.SubElement(attvalues, 'attvalue')
        attvalue.set('for', str(counterFor))
        counterFor += 1
        attvalue.set('value', tag.tag)
    attvalue = etree.SubElement(attvalues, 'attvalue')
    attvalue.set('for', '3')
    attvalue.set('value', user.reputation)
    attvalue = etree.SubElement(attvalues, 'attvalue')
    attvalue.set('for', '4')
    attvalue.set('value', user.upVotes)
    attvalue = etree.SubElement(attvalues, 'attvalue')
    attvalue.set('for', '5')
    attvalue.set('value', user.downVotes)
    for link in list(set(user.answered)):
        edge = etree.SubElement(edges, 'edge')
        edge.set('id', str(counter))
        edge.set('source', user.id)
        edge.set('target', link)
        counter += 1
del users
del tagsDict

#write xml file (gexf file)
tree = etree.ElementTree(gexf)
f = codecs.open(dataLocation + 'graph.gexf', 'w', encoding="utf-8")
treeString = minidom.parseString(etree.tostring(gexf)).toprettyxml()
f.write(treeString)
f.close()
f = open(dataLocation + 'numberOfUsersWithNoEdge.txt', 'w')
f.write(str(usersWithNoEdge))
f.close()
