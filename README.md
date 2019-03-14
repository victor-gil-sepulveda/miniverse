# Try it

Install docker and docker-compose. In my system I had to issue these commands  

    sudo apt-get install docker.io
    sudo apt-get install docker-compose

Download/clone this repository. Inside the ```miniverse``` folder, run:  

    sudo docker-compose up

(Note that in my system, it is required to run docker commands as root). Finally
you can try the test client with:

    python miniverse/example.py


## Notes  
* Each user can have associated options, like the current currency.

* A transfer can be modelled with comments as separate entities so that 
it is easier to handle 'likes' etc.

* Some constraints could be added to the database (ex. creating a 
transaction with amount = 0). In here we are checking some the constraints
in the python part. Some constraints are missing though, for instance, 
checking that a transfer must have different users (however an autotransfer should 
be legal, why not!).

* One could use Enums instead of regular strings, but strings are easier to serialize/deserialize,
and developing time is a constraint for this project.

* Balance is maintained in User instead of calculated every time (less stress for the DB). It may be
recalculated in transfers in order to check coherency (?).
