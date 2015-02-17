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
       self.acceptedAnswerPost = []

    def add_accepted_answer(self, postID):
        self.acceptedAnswerPost.append(postID)

#list of users
users = []

#get command line arguments for files, use default if not available
usersFile = '/home/roger/Desktop/Users.xml'
postsFile = '/home/roger/Desktop/Posts.xml'
if len(sys.argv) == 3:
    usersFile = sys.argv[1]
    postsFile = sys.argv[2]

# open user file
f = open('/home/roger/Desktop/Users.xml', 'r')
tree = etree.iterparse(f)
for event, row in tree:
    print row.attrib.keys()
    print row.attrib.values()
    user = User(row.attrib['Id'], row.attrib['Reputation'],row.attrib['DisplayName'], row.attrib['UpVotes'], row.attrib['DownVotes'])
    users.append(user)
f.close()
f = open('/home/roger/Desktop/Posts.xml', 'r')