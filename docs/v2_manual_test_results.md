## Room Workflow
### "As a roommate, I want to be able
- to create a room and add myself as a user
- to see a specific user in my room
- to update a specifc user in my room
- to delete a user from my room 

#### Scenario: I just created an account on the roommate app, now I want to to create a room and add my roommates, Roxanne and Fred. Unfortunately, a couple days later, I received news that Fred had passed away(as a barrel owner, his manager works him really hard). Now I want to remove Fred from the room - RIP Fred! 

+ To create a room I can call **POST `/room/`** and give my room a name - "POTION PEEPS", this returns a unique room_id, say 1
+ Now I want to add myself so I can call **POST `/room/user`** and pass in my name ("Roommate") and room id (1), this returns a user_id, say 4. I also add Roxanne and Fred by passing in their names to **POST `/room/user`** with a room_id (1), this returns their user ids - say 5 for Roxanne, and 6 for Fred
+ Now, I realized I mispelled Roxanne's name, so to update this name I can run **POST `/room/user/{id}`** and pass in the correct spelling
+ I want to see Fred's information, so I can call **GET `/room/user/{id}`** and this will return all of his information - "name": Fred, "room_id": 1, "points": 0, "id": 6}
+ Now, Fred is dead. Time to remove him from our room. I can run **DELETE `/room/user/{id}`** by passing in Fred's id (6). No more Fred. 

## Testing Results

### /room/ -Create a room
curl -X 'POST' \
  'https://roommate-app-gs9w.onrender.com/room/' \
  -H 'accept: application/json' \
  -H 'access_token: ad6db9c3b176f5cf7e72ad357f2b139f' \
  -H 'Content-Type: application/json' \
  -d '{
  "room_name": "string"
}'
Response:
{
  "room_id": 2
}

### /room/user -Add a user
curl -X 'POST' \
  'https://roommate-app-gs9w.onrender.com/room/user' \
  -H 'accept: application/json' \
  -H 'access_token: ad6db9c3b176f5cf7e72ad357f2b139f' \
  -H 'Content-Type: application/json' \
  -d '{
  "room_id": 2,
  "name": "John"
}'
Response:
{
  "success": "ok"
}

### /room/user/{id} -See a specific user
curl -X 'GET' \
  'https://roommate-app-gs9w.onrender.com/room/user/2' \
  -H 'accept: application/json' \
  -H 'access_token:  ad6db9c3b176f5cf7e72ad357f2b139f'
  Response:
  {
  "id": 2,
  "name": "John",
  "room_id": 2,
  "points": null
}

### /room/user/{id} -Update a specific user
curl -X 'POST' \
  'http://127.0.0.1:4000/room/user/2' \
  -H 'accept: application/json' \
  -H 'access_token: testroommateapp' \
  -H 'Content-Type: application/json' \
  -d '{
  "id": 2,
  "name": "John",
  "room_id": 2,
  "points": 100
}'
Response:
{
  "success": "ok"
}

### /room/user/{id} -Delete user from room
curl -X 'DELETE' \
  'http://127.0.0.1:4000/room/user/2' \
  -H 'accept: application/json' \
  -H 'access_token: testroommateapp'
Response:
{
"success": "ok"
}


## Chores Workflow
### "As a roommate, I want to be able
- to display chores assigned to a specific roommate
- to create new chores and reassign existing chores to other roommates
- to mark chores as completed
- to display all the current chores and which roommate needs to complete them (not part of v2)
- to see all chores, both completed and yet to be completed  (not part of v2)

#### Scenario: It's been a month since Roxanne and I (John) moved in. I want to create a few chores to buy groceries, clean the kitchen, empty the shower drain, and take out the trash. I'll be adding all 4 chores and assigning two to each of us. While Roxanne tried emptying the drain, she realized that we don't need to since it's not clogged, so we'll just mark it complete. Thus, to make it fair, we'll reassign one of my tasks to her since buying the groceries took too long.

+ To create the 4 chores I can call **POST `/chore/`** and give them a chore_name, mark them all to be false for completed and assign either myself (user_id = 7) or Roxanne (user_id = 8) to them. This will return a unique chore_id, say 8.
+ Now I want to see which chores are assigned to me so I can call **GET `/chore/chore/{id}/`** and pass in Roxanne's user id, 8, this will return a list of tasks: Empty Shower Drain and Take Out Trash, including their chore_id and completed status.
+ Next, we need to mark the empty shower drain as completed, so we can run **POST `/chore/chore/{choreid}/completed/`** and pass in the choreid, which is 10. This will return a response regarding the success, ex: 'ok'
+ Lastly, I'll be reassigning the clean the kitchen task to Roxanne by running **POST `/chore/{choreid}/claim/{user_id}/`** and pass in the choreid and userid, 9 and 8 respectively. This will also return a response regarding the success.

## Testing Results

### /chore/ - Create a chore
curl -X 'POST' \
  'https://roommate-app-gs9w.onrender.com/chore/' \
  -H 'accept: application/json' \
  -H 'access_token: ad6db9c3b176f5cf7e72ad357f2b139f' \
  -H 'Content-Type: application/json' \
  -d '{
  "chore_name": "Buy Groceries",
  "completed": false,
  "assigned_user_id": 7
}'

Response:
{
  "chore_id": 8
}

curl -X 'POST' \
  'https://roommate-app-gs9w.onrender.com/chore/' \
  -H 'accept: application/json' \
  -H 'access_token: ad6db9c3b176f5cf7e72ad357f2b139f' \
  -H 'Content-Type: application/json' \
  -d '{
  "chore_name": "Clean Kitchen",
  "completed": false,
  "assigned_user_id": 7
}'

Response:
{
  "chore_id": 9
}

curl -X 'POST' \
  'https://roommate-app-gs9w.onrender.com/chore/' \
  -H 'accept: application/json' \
  -H 'access_token: ad6db9c3b176f5cf7e72ad357f2b139f' \
  -H 'Content-Type: application/json' \
  -d '{
  "chore_name": "Empty Shower drain",
  "completed": false,
  "assigned_user_id": 8
}'

Response:
{
  "chore_id": 10
}

curl -X 'POST' \
  'https://roommate-app-gs9w.onrender.com/chore/' \
  -H 'accept: application/json' \
  -H 'access_token: ad6db9c3b176f5cf7e72ad357f2b139f' \
  -H 'Content-Type: application/json' \
  -d '{
  "chore_name": "Take out trash",
  "completed": false,
  "assigned_user_id": 8
}'

Response:
{
  "chore_id": 11
}

### /chore/chore/{id}/ - Get current chores assigned to a roommate
curl -X 'GET' \
  'https://roommate-app-gs9w.onrender.com/chore/chore/8' \
  -H 'accept: application/json' \
  -H 'access_token: ad6db9c3b176f5cf7e72ad357f2b139f'
  
Response:
[
  {
    "id": 10,
    "chore_name": "Empty Shower Drain",
    "completed": false
  },
  {
    "id": 11,
    "chore_name": "Take out trash",
    "completed": false
  }
]

### /chore/chore/{choreid}/completed/ - Mark a chore as completed
curl -X 'POST' \
  'https://roommate-app-gs9w.onrender.com/chore/chore/10/completed' \
  -H 'accept: application/json' \
  -H 'access_token: ad6db9c3b176f5cf7e72ad357f2b139f' \
  -d ''

Response:
{
  "success": "ok"
}

### /chore/{choreid}/claim/{user_id}/ - Reassign chore to a different roommate
curl -X 'POST' \
  'https://roommate-app-gs9w.onrender.com/chore/9/claim/8' \
  -H 'accept: application/json' \
  -H 'access_token: ad6db9c3b176f5cf7e72ad357f2b139f' \
  -d ''
  
Response:
{
"success": "ok"
}


## Split Workflow
### "As a roommate, I want to be able
- to add an item to the split
- to display all the items and relevant info in the split
- to display all the items a specific roommate added
- to display all the items a specific roommate needs to pay for
- to complete the payment for a specific roommate (not part of v2)
- to delete an item from the split

#### Scenario: When I went grocery shopping, I bought milk, eggs, and bread, and will be adding all those items to the split. Roxanne actually ordered some protein bars from Amazon as well, so she'll be adding that to the split as well. However, we realized that I'm allergic to one of the ingredients in the bar, so Roxanne will be eating them alone, and thus, we'll be removing it from the split.

+ To add the 4 items to the split Roxanne and I can call **POST `/split/`** and pass in a name for the item, price, quantity, and which roommate is adding the item. This will return a response regarding the success.
+ Next, I want to check all items in the split, so I can call **GET `/split/`** which will return a list of the id, name, price, quantity, and roommate that added the item for each item.
+ Now, I want to check which items I added to the split specifically, so I can run **GET `/split/{user_id}/`** and pass in my user_id, 7, which will return a list of the items that I added.
+ I want to make sure that I pay my share of the split, so I can call **GET `/split/{user_id}/pay/`** and this will return a list of the items that I need to pay for, with price indicating my share of how much to pay. For example, since there are only two of us, since I paid 5 dollars for the bread, Roxanne's share would be 2.5 dollars.
+ Finally, since I'll allergic to the protein bars, Roxanne will be deleting that item from the split by running **DELETE `/split/{split_id}/delete/`** and passing in the item id of the bars, 11. This will return a response regarding the success.

## Testing Results

### /split/ - Add an item to the split
curl -X 'POST' \
  'https://roommate-app-gs9w.onrender.com/split/' \
  -H 'accept: application/json' \
  -H 'access_token: ad6db9c3b176f5cf7e72ad357f2b139f' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "milk",
  "price": 7,
  "quantity": 1,
  "user_added": 7
}'

Response:
{
  "success": "ok"
}

curl -X 'POST' \
  'https://roommate-app-gs9w.onrender.com/split/' \
  -H 'accept: application/json' \
  -H 'access_token: ad6db9c3b176f5cf7e72ad357f2b139f' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "bread",
  "price": 5,
  "quantity": 2,
  "user_added": 7
}'

Response:
{
  "success": "ok"
}

curl -X 'POST' \
  'https://roommate-app-gs9w.onrender.com/split/' \
  -H 'accept: application/json' \
  -H 'access_token: ad6db9c3b176f5cf7e72ad357f2b139f' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "eggs",
  "price": 15,
  "quantity": 36,
  "user_added": 8]7
}'

Response:
{
  "success": "ok"
}

curl -X 'POST' \
  'https://roommate-app-gs9w.onrender.com/split/' \
  -H 'accept: application/json' \
  -H 'access_token: ad6db9c3b176f5cf7e72ad357f2b139f' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "protein bars",
  "price": 30,
  "quantity": 25,
  "user_added": 8
}'

Response:
{
  "success": "ok"
}

### /split/ - Get all items in the split
curl -X 'GET' \
  'https://roommate-app-gs9w.onrender.com/split/' \
  -H 'accept: application/json' \
  -H 'access_token: ad6db9c3b176f5cf7e72ad357f2b139f'
  
Response:
[
  {
    "id": 11,
    "name": "protein bars",
    "price": 30,
    "quantity": 25,
    "user_added": 8
  },
  {
    "id": 4,
    "name": "milk",
    "price": 7,
    "quantity": 1,
    "user_added": 7
  },
  {
    "id": 6,
    "name": "eggs",
    "price": 15,
    "quantity": 36,
    "user_added": 7
  },
  {
    "id": 5,
    "name": "bread",
    "price": 5,
    "quantity": 2,
    "user_added": 7
  }
]

### /split/{user_id}/ - Displays all the items this roommate added
curl -X 'GET' \
  'https://roommate-app-gs9w.onrender.com/split/7/' \
  -H 'accept: application/json' \
  -H 'access_token: ad6db9c3b176f5cf7e72ad357f2b139f'

Response:
[
  {
    "id": 4,
    "name": "milk",
    "price": 7,
    "quantity": 1,
    "user_added": 7
  },
  {
    "id": 6,
    "name": "eggs",
    "price": 15,
    "quantity": 36,
    "user_added": 7
  },
  {
    "id": 5,
    "name": "bread",
    "price": 5,
    "quantity": 2,
    "user_added": 7
  }
]

### /split/{user_id}/pay/ - Displays all the items the rommate needs to pay for
curl -X 'GET' \
  'https://roommate-app-gs9w.onrender.com/split/8/pay/' \
  -H 'accept: application/json' \
  -H 'access_token: ad6db9c3b176f5cf7e72ad357f2b139f'
  
Response:
[
  {
    "id": 4,
    "name": "milk",
    "price": 3.5,
    "quantity": 1,
    "user_added": 7
  },
  {
    "id": 6,
    "name": "eggs",
    "price": 7.5,
    "quantity": 36,
    "user_added": 7
  },
  {
    "id": 5,
    "name": "bread",
    "price": 2.5,
    "quantity": 2,
    "user_added": 7
  }
]

### /split/{split_id}/delete/ - Delete an item from the split
curl -X 'DELETE' \
  'https://roommate-app-gs9w.onrender.com/split/11/delete/' \
  -H 'accept: application/json' \
  -H 'access_token: ad6db9c3b176f5cf7e72ad357f2b139f'

Response:
{
  "success": "ok"
}
