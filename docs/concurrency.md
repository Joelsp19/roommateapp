### Concurrency Issues

## 1
One possible concurrency issue that our endpoints have is when two roommates try to claim a chore at the same time. One transaction would check if the chore has nobody assigned to it and before it finishes another transaction would update the same chore and assign it the another roommate. 
Then, the first transaction would assign the first roommate to the task because it is still under the assumption that no one is assigned to the task. This would mean the previous update would be lost. 
![Diagram 1](Concurrency1.jpg)
