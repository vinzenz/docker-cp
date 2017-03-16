docker-cp copy files from and to docker containers with buffers
===============================================================


    usage: docker-cp.local [-h] [--buffer-length N] source dest
    
    Copies files from and to containers
    
    positional arguments:
      source             Source location
      dest               Destination location
    
    optional arguments:
      -h, --help         show this help message and exit
      --buffer-length N  Restrict the size of the buffer used for reading/writing
                         files transfered to and from docker containers