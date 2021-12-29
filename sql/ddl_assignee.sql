/*
DB Name: doggyremindersdb
Table Name: assignee
.open doggyremindersdb
*/

CREATE TABLE IF NOT EXISTS assignee (
        assignee_id INTEGER PRIMARY KEY, /* unique id for a person who can be assigned to respond to a reminder */
        first_name TEXT /* first name of the assignee */
)

