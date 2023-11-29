# API Specification

## ACCOUNT

### POST `/room/`

Adds a room (done on creation)

**Request**:

```json
{
  "room_name": "string"
}
```

**Returns:**

```json
{
  "room_id": "integer"
}
```

### POST `/room/user/`

Adds a user and creates id

**Request**:

```json
{
"room_id": "integer"
"name": "string"
}
```

**Returns**:

```json
{
  "success": "ok"
}
```

### GET `/room/user/superuser`

Displays information about the superuser

**Returns**:

```json
{
  "id": "integer",
  "name": "string"
}
```

### POST `/room/user/{id}/superuser`

Requests to become the superuser

**Returns**:

```json
{
  "success": "ok"
}
```

### POST `/room/user/{id}/superuser/{new_id}/transfer`

Transfers the superuser to be the new user(must be a superuser)

**Returns**:

```json
{
  "success": "ok"
}
```

### GET `/room/user/{id}/`

Displays user information

**Returns:**

```json
{
"Id": "integer"
"name": "string"
"room_id": "integer"
"points": "integer"
}
```

### PUT `/room/user/{id}/`

Updates user information

**Request**:

```json
{
"Id": "integer"
"name": "string"
"room_id": "integer"
"points": "integer"
}
```

**Returns**:

```json
{
  "success": "ok"
}
```

### DELETE `/room/user/{id}`

Removes a user

**Returns**:

```json
{
  "success": "ok"
}
```

### GET `/room/{room_id}/free_time`

Complex Endpoint 1 - Find an available time for all the users in the room on a specified date where no one has any events scheduled.

**Request**:

```json
{
"room_id": "integer"
"date_wanted": "date"
}
```

**Returns**:

```json
{
  "string"
}
```

### POST `/room/reward`

Complex Endpoint 2 - Finds the user in the specified room id who earned the most points from chores in that month through accumulation. Then, creates a calendar event for the room's shared calendar stating which roommate won the reward this month.

**Request**:

```json
{
"room_id": "integer"
}
```

**Returns**:

```json
{
  "success": "ok"
}
```

## CHORES

### GET `/chore/`

Displays all the chores to be completed and person to complete

**Returns**:

```json
[
  {
    "id": "integer",
    "chore_name": "string",
    "assigned_person": "string",
    "completed": "boolean"
  }
]
```

### GET `/chore/all`

Displays all the created chores that have been completed and to be completed

**Returns**:

```json
[
  {
    "id": "integer",
    "chore_name": "string",
    "completed": "boolean"
  }
]
```

### GET `/chore/{user_id}`

Displays all the chores to be completed and associated user

**Returns**:

```json
[
  {
    "id": "integer",
    "chore_name": "string",
    "completed": "boolean"
  }
]
```

### POST `/chore/`

Creates a new chore to be completed

**Request**:

```json
{
  "chore_name": "string"
}
```

**Returns**:

```json
{
  "success": "ok"
}
```

### PUT `/chore/{chore_id}/claim/{user_id}`

Updates the chore with person to complete

**Returns**:

```json
{
  "success": "ok"
}
```

### POST `/chore/{chore_id}/completed`

Marks the chore as complete(adds points)

**Returns**:

```json
{
  "success": "ok"
}
```

### DELETE `/chore/{chore_id}`

Deletes the chore in case it’s no longer needed

**Returns**:

```json
{
  "success": "ok"
}
```

## SPLIT

### GET `/split/`

Displays all the items in the split

**Returns**:

```json
[
  {
    "id": "integer",
    "name": "string",
    "price": "float",
    "quantity": "integer",
    "user_added": "integer"
  }
]
```

### GET `/split/{user_id}/`

Displays all the items user added

**Returns**:

```json
[
  {
    "id": "integer",
    "name": "string",
    "price": "integer",
    "quantity": "integer",
    "user_added": "integer"
  }
]
```

### GET `/split/{user_id}/pay/`

Displays all the items user must pay for

**Returns**:

```json
[
  {
    "id": "integer",
    "name": "string",
    "price": "integer",
    "quantity": "integer",
    "user_added": "integer"
  }
]
```

### POST `/split/{user_id}/pay/complete/`

Completes the payment

**Request**:

```json
{
  "payment_type": "string",
  "amount": "float"
}
```

**Returns**:

```json
{
  "success": "ok"
}
```

### POST `/split/`

Adds an item to the split database

**Request**:

```json
[
  {
    "name": "string",
    "price": "integer",
    "quantity": "integer"
  }
]
```

**Returns**:

```json
{
  "success": "ok"
}
```

### PUT `/split/{split_id}/update/`

Updates split item information

**Request**:

```json:
[
{
	"name": "string",
	"price": "integer",
	"quantity": "integer"
}
]
```

**Returns**:

```json
{
  "success": "ok"
}
```

### DELETE `/split/{split_id}/delete/`

Deletes an item from the split

**Returns**:

```json
{
  "success": "ok"
}
```

## CALENDAR

### POST `/calendar`

Creates a new calendar

**Returns**:

```json
{
  "success": "ok"
}
```

### GET `/calendar`

Displays the calendar information

**Returns**:

```json
[
{
	"id": "integer",
	"name": "string",
	"date": "string",
	"time": "time"
	"user_id": "integer"
}
]
```

### POST `/calendar/add`

Adds an event to the calendar

**Request**:

```json
[
  {
    "name": "string",
    "date": "string",
    "time": "time"
  }
]
```

**Returns**:

```json
{
  "success": "ok"
}
```

### PUT `/calendar/{event.id}/update`

Update an event to the calendar

**Request**:

```json
[
  {
    "name": "string",
    "date": "string",
    "time": "time"
  }
]
```

**Returns**:

```json
{
  "success": "ok"
}
```

### DELETE /calendar/{event.id}/delete

Removes an event from the calendar

**Returns**:

```json
{
  "success": "ok"
}
```
