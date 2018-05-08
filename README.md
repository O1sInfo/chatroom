# chatroom
A Erogenous Chat Room by Python.
---

### Usage:

* `git clone https://github.com/O1sInfo/chatroom.git`
* `cd server` and run `python3 server.py [-h]`
* `cd client` and run `python3 client.py [h]`

### A Breif Introduction

A multi-user online chat room. Evey client connect to server using a individual thread. All message passing happens using TCP via server. Here are functions you can experience.

* Send a brocast message to all users in your room. Ex: `hi everyone.`
* Send a private message to the user you want. Ex: `@cindy hi.`
* List the available room you can join. Ex: `/list`
* List all users in your room. Ex: `/who`
* Create a room. You can alse set a password. Ex: `/create LOL [password]`
* Join a room. If it's protected, you need pass a password. Ex: `/join LOL [password]`
* Exit the current room. And you will join the Lobby. Ex: `/exit`
* Disconnect server, exit the chat app. Ex:`/bye`

***Thanking for your using. ^_^***  
