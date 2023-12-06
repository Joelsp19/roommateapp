**Fake Data Modeling:**
The file for constructing the million rows is src/fakedata.py. At the time of testing, it took a parameter
of the POSTGRES_URI of the local database.

The following represents the split of 1 million rows by table:
- Rooms: 50,000
- Calendars: 100,000
- Users: 200,000
- Events: 150,000
- Chores: 200,000
- Splits: 300,000

We tried to pick the most reasonable split of data based on how the data might scale overall. After brainstorming, we
realized that most users would end up trying out the app once or twice and then maybe not using it anymore, and the number of dedicated users would be far less, especially for a new product/service.

Thus, we wanted to try and portray that, so we decided to start of with 50k rooms. Each room will have a group calendar, as well as a portion of users having their own calendar for their events, so we choose 25% of users to have a personal calendar, making a total of 100k calendars. Each room will have 4 users, thus, 200k users. For events, we choose to have 1 event per group room calendar and 2 events for each user with a personal calendar, for a total of 150k events. We decided to show what the first week of chores would look like, so all the users are just assigned 1 chore each, and for splits, we decided to pick 75% of users to have 2 item splits each, thus having 300k total split items.

Our focus for this testing was near the start of the renting period, so there are fewer calendar events and chores, and since most roommate will bring shared items at the start, we decided to have more items in the split.

**Performance Results for Each Endpoint:**
Rooms:
- POST /rooms/ - 60.1ms
- GET /rooms/{room_id} - 67.9ms
- PUT /rooms/{room_id} - 70.8ms
- GET /rooms/{room_id}/users - 225ms
- GET /rooms/{room_id}/free_time - 260ms
- POST /rooms/reward - 368ms

Users:
- POST /users/ - 113ms
- GET /users/{id} - 87.6ms
- PUT /users/{id} - 100.3ms
- DELETE /users/{id} - 228ms

Chores:
- GET /chores/ - 202ms
- POST /chores/ - 81.9ms
- GET /chores/completed - 4.88s
- POST /chores/{chore_id}/claim/{user_id} - 129ms
- GET /chores/{id} - 315ms
- GET /chores/{chore_id}/duration - 105ms
- POST /chores/{chore_id}/completed - 114ms

Splits:
- POST /splits/ - 138ms
- PUT /splits/{split_id}/update/ - 125ms
- GET /splits/{split_id}/ - 84.1ms
- GET /splits/{user_id}/ - 355ms
- GET /splits/{user_id}/pay/ - 6.07s
- DELETE /splits/{split_id}/delete/ - 188ms

Calendars:
- GET /calendars/ - 2.41s
- POST /calendars/ - 87.5ms
- GET /calendars/{calendar_id} - 81.2ms
- PUT /calendars/{calendar_id} - 73.8ms
- GET /calendars/{calendar_id}/event - 500ms
- POST /calendars/{calendar_id}/event - 166ms
- GET /calendars/{calendar_id}/event/{event_id} - 118.3ms
- PUT /calendars/{calendar_id}/event/{event_id} - 111ms
- DELETE /calendars/{calendar_id}/event/{event_id} - 280ms

The three slowest endpoints starting from the slowest are:
1. GET /splits/{user_id}/pay - 6.07s
2. GET /chores/completed - 4.88s
3. GET /calendars/ - 2.41s

**Performance Tuning:**
1. GET /splits/{user_id}/pay

This has 3 queries:
postgres=> EXPLAIN SELECT id, name, price, quantity, user_added
                        FROM split
                        WHERE user_added != 3000;
                          QUERY PLAN
--------------------------------------------------------------
 Seq Scan on split  (cost=0.00..6411.00 rows=299998 width=33)
   Filter: (user_added <> 3000)
(2 rows)

postgres=> EXPLAIN SELECT users.room_id
postgres->                         FROM users
postgres->                         WHERE users.id = 3000;
                               QUERY PLAN
------------------------------------------------------------------------
 Index Scan using users_pkey on users  (cost=0.42..8.44 rows=1 width=8)
   Index Cond: (id = 3000)
(2 rows)

postgres=> EXPLAIN SELECT COUNT(*)
postgres->                         FROM users
postgres->                         WHERE users.room_id = 3000;
                          QUERY PLAN
--------------------------------------------------------------
 Aggregate  (cost=4450.01..4450.02 rows=1 width=8)
   ->  Seq Scan on users  (cost=0.00..4450.00 rows=4 width=0)
         Filter: (room_id = 3000)
(3 rows)

The explains are basically telling us that the first query sequentially scans on the split table for the user_added column which isn't really efficient. The second query does an indexscan using users_pkey in the users table, which is more efficient as its using an index. The third query scans the entire users table to count rows that match the room_id condition, which isn't efficient.

We can add the following indexes:
CREATE INDEX idx_room_id ON users(room_id);
CREATE INDEX idx_user_added ON split(user_added);

Running EXPLAIN again shows the query now using an index scan instead of sequential scan:
postgres=> EXPLAIN SELECT COUNT(*)
                        FROM users
                        WHERE users.room_id = 3000;
                                     QUERY PLAN
------------------------------------------------------------------------------------
 Aggregate  (cost=8.50..8.51 rows=1 width=8)
   ->  Index Only Scan using idx_room_id on users  (cost=0.42..8.49 rows=4 width=0)
         Index Cond: (room_id = 3000)
(3 rows)

The new performance was 1.8s after applying the index, this is still a large time likely due to the sheer amount of data in the table and that the queries themselves can be changed to have better performance.

2. GET /chores/completed

postgres=> EXPLAIN SELECT chores.id, chore_name, completed, name as assigned_user_name, chores.points
postgres->                             FROM chores
postgres->                             LEFT JOIN users on users.id = assigned_user_id
postgres->                             WHERE completed=true;
                                QUERY PLAN
--------------------------------------------------------------------------
 Hash Left Join  (cost=7622.02..15396.41 rows=98813 width=61)
   Hash Cond: (chores.assigned_user_id = users.id)
   ->  Seq Scan on chores  (cost=0.00..4413.00 rows=98813 width=55)
         Filter: completed
   ->  Hash  (cost=3950.01..3950.01 rows=200001 width=22)
         ->  Seq Scan on users  (cost=0.00..3950.01 rows=200001 width=22)
(6 rows)

The explain queries display that there is a jash left join taking place between chores and users tables, and that there's a suquential scan on chores table with a filter of completed=true and a sequential scan of the users table with no filter.

We can add the following indexes:
CREATE INDEX idx_completed ON chores(completed);
CREATE INDEX idx_assigned_user_id ON chores(assigned_user_id);
CREATE INDEX idx_users_id ON users(id);
CREATE INDEX idx_completed_true ON chores(id) WHERE completed = true;

Running EXPLAIN provides the following result which displays that the sequential scan for chores is now replaced by an index scan using the last partial index with the completed=true condition:
postgres=> EXPLAIN SELECT chores.id, chore_name, completed, name as assigned_user_name, chores.points
                            FROM chores
                            LEFT JOIN users on users.id = assigned_user_id
                            WHERE completed=true;
                                          QUERY PLAN
-----------------------------------------------------------------------------------------------
 Hash Left Join  (cost=7622.32..14753.93 rows=98815 width=61)
   Hash Cond: (chores.assigned_user_id = users.id)
   ->  Index Scan using idx_completed_true on chores  (cost=0.29..3770.52 rows=98815 width=55)
   ->  Hash  (cost=3950.01..3950.01 rows=200001 width=22)
         ->  Seq Scan on users  (cost=0.00..3950.01 rows=200001 width=22)
(5 rows)

The new performance was 2.3s, which is now almost twice as fast and could work for the service, but as users increase, this would definitely need to be further improved in order to decrease computational usage and wait times.

3. GET /calendars/

postgres=> EXPLAIN SELECT id, name
postgres->                 FROM calendar;
                           QUERY PLAN
-----------------------------------------------------------------
 Seq Scan on calendar  (cost=0.00..1868.15 rows=100115 width=30)
(1 row)

This is a pretty simple query, and the explain shows the obvious that there is a sequential scan happening on the calendar table.

We can add the following indexes:
CREATE INDEX idx_calendar_name ON calendar(name);
CREATE INDEX idx_calendar_id_name ON calendar(id, name);

Even though we added the name index and composite index for name and column, there really won't be any effect, because this query is just defined in such a way where the index wouldn't be beneficial. This is displayed by the results:
postgres=> EXPLAIN SELECT id, name
                FROM calendar;
                           QUERY PLAN
-----------------------------------------------------------------
 Seq Scan on calendar  (cost=0.00..1867.15 rows=100015 width=30)
(1 row)

The new performance was basically the same at 2.02s, as the indexes didn't make a difference for this endpoint because of the non-compatible query design with the process of indexing. For future steps, we'd try and improve the query design to support such indexing for this endpoint and a couple of other ones.