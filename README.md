# Networking-Communication
The initial installment in my adventure of understanding networking. Clearly, before diving in to packets, sniffers and so on, I need to first understand and build the structure used to communicate between machines. To build on this, I also need how to communicate securly between machines as this seems like the next logical step and also because sometimes if you cannot securly send something then you cannot send it at all. Because of this, it's importance is almost on par with that of the communcation structure itself.

Socket is a python module that allows for the writing of TCP/UDP clients, servers and for us to use raw sockets. For the purpose of breaking in or maintaining access to target machines, this module is all that is needed. I have written some simple clients and servers which are two very common communication scripts. I have also created an ssh client/server pair to tunnel traffic using our secure shell.

