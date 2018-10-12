# subalive
Subprocess handling with alive keeping for python

With this package you can start a python script in a new subprocess from a master script and it makes sure that if the master exits/terminates, the slave will detect it and quit.

Just instantiate the two classes in your master and slave script, and that's it.

Works with python 3.6

# Example
## master

    from subalive import SubAliveMaster
    
    # start subprocess with alive keeping
    SubAliveMaster(<path to your slave script>)
    
    # do your stuff
    # ...
    
## slave

    from subalive import SubAliveSlave

    # start alive checking
    SubAliveSlave()

    # do your stuff
    # ...

# Usage

    >> python master.py
