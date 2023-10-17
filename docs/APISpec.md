# API Specification

## CHORES
#### GET `/chore/`
Displays all the chores to be completed and person to complete

#### GET `/chore/all`
Displays all the created chores that have been completed and to be completed

#### GET `/chore/{user_id}`
Displays all the chores to be completed and associated user

#### POST `/chore/`
Creates a new chore to be completed

#### PUT `/chore/{chore_id}/claim/{user_id}`
Updates the chore with person(s) to complete

#### POST `/chore/{chore_id}/completed`
Marks the chore as complete(adds points)

#### DELETE  `/chore/{chore_id}`
Deletes the chore in case it’s no longer needed

## SPLIT

#### GET `/split/`
Displays all the items in the split

#### GET `/split/{user_id}/`
Displays all the items user added

#### GET `/split/{user_id}/pay/`
Displays all the items user must pay for

#### POST `/split/{user_id}/pay/complete/`
Completes the payment

#### POST `/split/`
Adds an item to the split database

#### PUT `/split/{split_id}/update/`
Updates split item information

#### DELETE  `/split/{split_id}/delete/`
Deletes an item from the split
