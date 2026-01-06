## Project 


Day 3: Text2SQL + guardrails + API endpount 

schema introspection (so the LLM knows tables/columns)

Text2SQL generator (LLM produces SQL only)

SQL validation (SELECT-only + safe keywords)

/ask endpoint: user question → SQL → results


Day 3: Test successfully 

change gitignore from data/ to *.xlsx


Day 4: Update for work computer
4.1 Plot chart
Take 1st column is X, 2nd is Y.
Constrains: 1. Empty data or only 1 column -> no chart
            2. If Y isn't number -> no chart
            3. If X is datetime -> line chart
                else -> bar chart
        *Now, if more than 2 columns, do nothing