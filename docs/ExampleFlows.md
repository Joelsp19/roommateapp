# EXAMPLE FLOWS

## Example 1

### “As a roommate, I want to be able 
- to create tasks that my roommates can see and access so that my roommates can understand and do their respective tasks.
- to be able to see a history of who has done what chores in the past so I can tell who is not doing their part or who is doing more than expected”

#### Scenario: My roommates are Roxanne (user_id = 2) and Fred (user_id = 3). I want Fred to do the dishes and Roxanne to take out the trash. Then I want to see everyone’s chores to be completed. I also want to see what chores have been completed in the past.

+ I can call **POST `/chore/`** and add information about doing the dishes to be completed and set the person to complete to be Fred. This returns an id of 2001.
+ Then I call **POST `/chore/`** again and create a take out trash task but forget to indicate that Roxanne should be doing it. This returns an id of 2002.
+ Then, I can call **PUT `/chore/2002/claim/2`** to claim the task for Roxanne.
+ Anyone can see all chores to be completed by calling **GET `/chore`**
+ To see all chores that have been completed I can call **GET `/chore/all`**. Fred has been slacking!!!


## Example 2
### “As a roommate, I want to be able 
- to see a complete list of currently unfinished tasks so I can prioritize what to do
- to be able to mark tasks as done to notify my roommates”

#### Scenario: My roommates are Roxanne (user_id = 2) and Fred (user_id = 3). From the previous scenario, Fred has a task to do the dishes and Roxanne has a task to take out the trash. Fred wants to see what tasks that he has to do. Roxanne completed her task to take out the trash so she wants to mark it as done.  

+ Fred can call **GET `/chore/3`**  to see his chores. Now he can prioritize his tasks. 
+ Roxanne has taken out the trash so she calls **POST `/chore/2002/completed`**. 

## Example 3
### “As a roommate, I want to be able
- to track grocery expenses broken down by each roommate to know how much I owe
- to add grocery items to a list of grocery expenses to split evenly among my roommates.” 

#### Scenario: My roommates are Roxanne (user_id = 2) and Fred (user_id = 3). I just went grocery shopping and bought some milk and eggs to be shared with everyone. Now I want to split the price among my roommates. 

+ To add milk and eggs to the split tab I can call **POST `/split/`** and pass in “milk” and its price(say $6).
+ And then call **POST `/split/`** again and pass in “eggs” and its price (say $12)
+ Now Roxanne wants to see how much she owes me. So she calls **GET `/split/2/pay/`** which then shows her {“milk”: $2, “eggs”: $4}.
+ Fred was sussed out by the expensive price for eggs and wants to see what the original price was. He calls **GET `/split/`** and the original result is displayed - {“milk”: $6, “eggs”: $12}. He realizes that eggs are expensive!!

## Example 4
### "As a roommate, I want to be able
- to create a room and add myself as a user
- to see a specific user in my room
- to update a specifc user in my room
- to delete a user from my room 

- ### Scenario: I just created an account on the roommate app, now I want to to create a room and add my roommates, Roxanne and Fred. Unfortunetely, a couple days later, I received news that Fred had passed away(as a barrel owner, his manager works him really hard). Now I want to remove Fred from the room - RIP Fred! 


+ To create a room I can call **POST `/room/`** and give my room a name - "POTION PEEPS", this returns a unique room_id, say 1
+ Now I want to add myself so I can call **POST `/room/user`** and pass in my name ("Roommate") and room id (1), this returns a user_id, say 4. I also add Roxanne and Fred by passing in their names to **POST `/room/user`** with a room_id (1), this returns their user ids - say 5 for Roxanne, and 6 for Fred
+ Now, I realized I mispelled Roxanne's name, so to update this name I can run **POST `/room/user/{id}`** and pass in the correct spelling
+ I want to see Fred's information, so I can call **GET `/room/user/{id}`** and this will return all of his information - "name": Fred, "room_id": 1, "points": 0, "id": 6}
+ Now, Fred is dead. Time to remove him from our room. I can run **DELETE `/room/user/{id}`** by passing in Fred's id (6)
+ 
+  
+ 


