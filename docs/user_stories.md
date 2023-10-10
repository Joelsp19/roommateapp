Roommate App User Stories

1. As a roommate, I want to be able to create an account on the app so I can connect with my roommates
2. As a roommate, I want to be able to designate other users/accounts as my roommates so I can share information with them
3. As a roommate, I want to be able to create tasks that my roommates can see and access so that my roommates can understand and do their respective tasks
4. As a roommate, I want to be able to see a history of who has done what chores in the past so I can tell who is not doing their part or who is doing more than expected
5. As a roommate, I want to be able to see a complete list of currently unfinished tasks so I can prioritize what to do
6. As a roommate, I want to be able to mark tasks as done to notify my roommates
7. As a roommate, I want to mark certain tasks as high priority to indicate they must be done first.
8. As a roommate, I want to be able to mark important dates on a shared calendar for all roommates to see
9. As a roommate, I want to earn points for the tasks I complete to compare to my roommates
10. As a roommate, I want to be able to track grocery expenses broken down by each roommate to know how much I owe
11. As a roommate, I want to be able to add grocery items to a list of grocery expenses to split evenly among my roommates. 
12. As a roommate, I want to easily pay off expenses in weekly or monthly increments using a “Venmo” integration
13. As a roommate, I want to be able to view the calendar events of my roommates to see their schedule as well as add my own events
14. As a roommate, I want to have the ability to request super roommate privileges to streamline tasks such as user removal


Exceptions

1. Database Connection Issues:
Provide a message to inform users that there is some connectivity issue, and to check their internet connection

2. Invalid User Input:
If a user enters invalid or unexpected input while entering groceries, chores, or calendar events, the database will return the error message and prompt them to enter the value again

3. Calendar Event Conflicts:
 If there is a scheduling conflict when attempting to add a calendar event, the app should inform the user about the conflict and ask them to select another time.
 
4. Duplicate User:
Database should handle cases where a user attempts to create an account with an email or username that already exists, providing a message to the user to choose a unique identifier.

6. Unauthorized Access / Permissions:
Database should display an error message if a user tries modifying any information that is not theirs such as events, expenses, or chores of another user.

7. Unavailable / Down Calendar API:
If the calendar service / API we use happens to become inactive temporarily, the database should freeze the calendar or indicate the error clearly for the user to understand the issue

8. Expenses Splitting Error:
If the expenses are too small (ex: splitting $0.02 into 4 people, it wouldn’t be possible since there’s no currency lower than $0.01). In this case, the database should prompt the user to change the amount to make sure it’s splittable.

9. Incomplete Chore / Groceries / Calendar Information:
Database should send an error message if a user tries to add a chore or grocery or calendar item without providing all the necessary information (such as title, price, description, date, etc, depending on the type). Then, the user should be prompted to re-enter the item.

10. Duplicate Chore / Groceries / Calendar Event:
Database shall send an error message if a user tries to create a chore/grocery/calendar event that is a duplicate of an already existing one and prompt the user to change the details.

11. Invalid Calendar Duration:
If the user enters a time period that is unrealistically long the app should prompt the user to double-check their times

12. Unavailable “Venmo” API:
If our Venmo/payment API stops working, the database should clearly let the user know that this functionality is down. 

13. User Removal Request:
If a user decides to remove another roommate from the app, the user should be prompted to confirm this decision and the request must be confirmed by all other roommates or the “super” roommate. 
