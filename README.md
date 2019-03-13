
## Notes  
* Each user can have associated options, like the current currency.

* A transfer can be modelled with comments as separate entities so that 
it is easier to handle 'likes' etc.

* Some constraints could be added to the database (ex. creating a 
movement with amount = 0.). In here we are checking the constraints
in the python part.

* One could use Enums instead of regular strings, but strings are easier to serialize/deserialize,
and developing time is a constraint for this project.

* Balance is maintained in User instead of calculated every time (less stress for the DB). It may be
recalculated in transfers in order to check coherency (?) .
