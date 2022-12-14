https://developer.riotgames.com/apis

RuneterraWeekly gives weekly deckbuilding prompts for the game Legends of Runeterra.
Using the API users can submit and save their recent games, saving a record of the ones that met the challenge.

Eventually it will be hosted at runeterraweekly.com

Most of the social elements had to be delayed till a reimplementation in React. What I chose to implement was the core functionality, 
which can later be expanded upon with things like leaderboards, goals, streaks, and other small gamification that can make the project more engaging, as well as
tools to manage upcoming prompts.

The standard flow of the website:
    - Visit to see the weekly prompt
        -> play games
    - return and enter their username/tag/region to submit the games
    - get a match-history of the performance of their deck
        * compare it to others

