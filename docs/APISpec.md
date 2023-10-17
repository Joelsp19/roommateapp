API SPECIFICATION

ACCOUNT

POST /room/
Adds a room (done on creation)

Returns:
{ 
“room_id”: “integer”
 }

POST /room/user/
Adds a user and creates id

Request:
{
“room_id”: “integer”
“name”: “string
}

GET /room/user/superuser
Displays information about the superuser

Returns:
{
“id”: “integer”,
“name”: “string”
}

POST /room/user/{id}/superuser
Requests to become the superuser

POST /room/user/{id}/superuser/{new_id}/transfer
Transfers the superuser to be the new user(must be a superuser)

GET /room/user/{id}/
Displays user information 

Returns:
{
“Id”: “integer”
“name”: “string”
“room_id”: “integer”
“points”: “integer”
}

PUT /room/user/{id}/
Updates user information

Request:
{
“Id”: “integer”
“name”: “string”
“room_id”: “integer”
“points”: “integer”
}

DELETE /room/user/{id}
Removes a user

No need for request or return


CHORES

GET /chore/
Displays all the chores to be completed and person to complete

Returns:
[
{
“id”: “integer”,
“chore_name”: “string”,
“assigned_person”: “string”,
“completed”: “boolean”
}
]

GET /chore/all
Displays all the created chores that have been completed and to be completed

Returns:
[
{
“id”: “integer”,
“chore_name”: “string”,
“completed”: “boolean”
}
]

GET /chore/{user_id}
Displays all the chores to be completed and associated user

Returns:
[
{
“id”: “integer”,
“chore_name”: “string”,
“completed”: “boolean”
}
]

POST /chore/
Creates a new chore to be completed
Request:
{
“chore_name”: “string”
}

PUT /chore/{chore_id}/claim/{user_id}
Updates the chore with person(s) to complete

No request or return needed

POST /chore/{chore_id}/completed
Marks the chore as complete(adds points)

DELETE  /chore/{chore_id}
Deletes the chore in case it’s no longer needed

No request or return needed


SPLIT

GET /split/
Displays all the items in the split
Returns:
[
{
	“id”: “integer”,
	“name”: “string”,
	“price”: “integer”,
	“quantity”: “integer”
	“user_added”: “integer”
}
]

GET /split/{user_id}/
Displays all the items user added

Returns:
[
{
	“id”: “integer”,
	“name”: “string”,
	“price”: “integer”,
	“quantity”: “integer”
	“user_added”: “integer”
}
]

GET /split/{user_id}/pay/
Displays all the items user must pay for

Returns:
[
{
	“id”: “integer”,
	“name”: “string”,
	“price”: “integer”,
	“quantity”: “integer”
	“user_added”: “integer”
}
]

POST /split/{user_id}/pay/complete/
Completes the payment

Request:
{
“payment _type”: “string”,
“amount”: “float”
}

POST /split/
Adds an item to the split database

Request:
[
{
	“name”: “string”,
	“price”: “integer”,
	“quantity”: “integer”
}
]

PUT /split/{split_id}/update/
Updates split item information

Request:
[
{
	“name”: “string”,
	“price”: “integer”,
	“quantity”: “integer”
}
]

DELETE  /split/{split_id}/delete/
Deletes an item from the split

No request or respone needed


CALENDAR

POST /calendar
Creates a new calendar

GET /calendar
Displays the calendar information

[
{
	“id”: “integer”,
	“name”: “string”,
	“date”: “string”,
	“time”: “time”
	“user_id”: “integer”
}
]

POST /calendar/add
Adds an event to the calendar
Request:
[
{
	“name”: “string”,
	“date”: “string”,
	“time”: “time”
}
]

PUT /calendar/{event.id}/update
Update an event to the calendar

Request:
[
{
	“name”: “string”,
	“date”: “string”,
	“time”: “time”
}
]

DELETE /calendar/{event.id}/delete
Removes an event from the calendar

No request or response needed

EXAMPLE FLOWS

Example 1
“As a roommate, I want to be able 
to create tasks that my roommates can see and access so that my roommates can understand and do their respective tasks.
to be able to see a history of who has done what chores in the past so I can tell who is not doing their part or who is doing more than expected”

My roommates are Roxanne (user_id = 2) and Fred (user_id = 3). I want Fred to do the dishes and Roxanne to take out the trash. Then I want to see everyone’s chores to be completed. I also want to see what chores have been completed in the past.

I can call POST /chore/ and add information about doing the dishes to be completed and set the person to complete to be Fred. This returns an id of 2001.
Then I call POST /chore/ again and create a take out trash task but forget to indicate that Roxanne should be doing it. This returns an id of 2002.
Then, I can call PUT /chore/2002/claim/2 to claim the task for Roxanne.
Anyone can see all chores to be completed by calling GET /chore
To see all chores that have been completed I can call GET /chore/all. Fred has been slacking!!!


Example 2
“As a roommate, I want to be able 
to see a complete list of currently unfinished tasks so I can prioritize what to do
to be able to mark tasks as done to notify my roommates”

My roommates are Roxanne (user_id = 2) and Fred (user_id = 3). From the previous scenario, Fred has a task to do the dishes and Roxanne has a task to take out the trash. Fred wants to see what tasks that he has to do. Roxanne completed her task to take out the trash so she wants to mark it as done.  

Fred can call GET /chore/3 to see his chores. Now he can prioritize his tasks. 
Roxanne has taken out the trash so she calls POST /chore/2002/completed. 

Example 3
“As a roommate, I want 
to be able to track grocery expenses broken down by each roommate to know how much I owe
to be able to add grocery items to a list of grocery expenses to split evenly among my roommates.”

My roommates are Roxanne (user_id = 2) and Fred (user_id = 3). I just went grocery shopping and bought some milk and eggs to be shared with everyone. Now I want to split the price among my roommates. 

To add milk and eggs to the split tab I can call POST /split/ and pass in “milk” and its price(say $6). And then call POST/split/ again and pass in “eggs” and its price (say $12)
Now Roxanne wants to see how much she owes me. So she calls GET /split/2/pay/ which then shows her {“milk”: $2, “eggs”: $4}. 
Fred was sussed out by the expensive price for eggs and wants to see what the original price was. He calls GET /split/ and the original result is displayed - {“milk”: $6, “eggs”: $12}. He realizes that eggs are expensive. 
