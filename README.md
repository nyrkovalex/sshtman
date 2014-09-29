# SSH Tunnel Manager (sshtman) #

This project aims to provide simple to use cli tunnel manager.

*Software is still work-in-progress and contains some debugging output and probably bugs and missing features. Pull requests are welcome.*

## Requirements ##

1. ssh client installed and available as `ssh` command
2. python3

## Limitations ##

These are subjected to change

1. sshtman supports UNIX-like systems only.
2. sshtman does not provide a way to enter your ssh password or key passphrase yet. For now stick with rsa keys. The are awesome anyway.

## How to use it ##

1. Start a daemon running `sshtmand` script. 
2. Send a command with `sshtman`. 

### Examples ###

* `sshtman open test -u dude -n my.server.org -l 8081 -r 8080` This will open connection named *test* to server *my.server.org* logging as as user *dude* and will establish a tunnel from remote port *8080* to local port *8081*. 
* `sshtman close test` will close the connetion *test*
* `sshtman kill` will kill the daemon process. Don't know why you may need this :)

### Things to consider ###

Probably you may want to run `sshtmand` as a background process, maybe creating an init file for your GNU/Linux distribution or some other kind of startup script for your system. 

Don't forget to add both scripts to your `$PATH` if you plan to run them without specifying the whole path to the executables.