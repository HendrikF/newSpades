# Connect

- Click on Connect Button
- Client connects to server
- Server creates new Connection instance (active = False)
- Server sends Map, Models, Teams, Tools, Players
- If Client received everything, it displays a list of teams, players, tools and lets the Player choose
- Client sends a JoinMsg with username, team and tool chosen
- Server sets Connection to active = True and stores a Player instance
