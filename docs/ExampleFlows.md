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
