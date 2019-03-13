
## Notes  

* One could use Enums instead of regular strings, but strings are easier to serialize/deserialize,
and developing time is a constraint for this project.

* Balance is maintained in User instead of calculated every time (less stress for the DB). It may be
recalculated in transfers in order to check coherency (?) .
