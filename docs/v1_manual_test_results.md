## Example Workflow
### "As a roommate, I want to be able
- to create a room and add myself as a user
- to see a specific user in my room
- to update a specifc user in my room
- to delete a user from my room 

- #### Scenario: I just created an account on the roommate app, now I want to to create a room and add my roommates, Roxanne and Fred. Unfortunately, a couple days later, I received news that Fred had passed away(as a barrel owner, his manager works him really hard). Now I want to remove Fred from the room - RIP Fred! 

+ To create a room I can call **POST `/room/`** and give my room a name - "POTION PEEPS", this returns a unique room_id, say 1
+ Now I want to add myself so I can call **POST `/room/user`** and pass in my name ("Roommate") and room id (1), this returns a user_id, say 4. I also add Roxanne and Fred by passing in their names to **POST `/room/user`** with a room_id (1), this returns their user ids - say 5 for Roxanne, and 6 for Fred
+ Now, I realized I mispelled Roxanne's name, so to update this name I can run **POST `/room/user/{id}`** and pass in the correct spelling
+ I want to see Fred's information, so I can call **GET `/room/user/{id}`** and this will return all of his information - "name": Fred, "room_id": 1, "points": 0, "id": 6}
+ Now, Fred is dead. Time to remove him from our room. I can run **DELETE `/room/user/{id}`** by passing in Fred's id (6). No more Fred. 

## Testing Results

<add curl commands here> 

