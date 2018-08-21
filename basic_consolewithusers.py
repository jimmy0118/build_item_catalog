#!/usr/bin/python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Console, Game, User

engine = create_engine('sqlite:///consolegameswithusers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


user1 = User(name="Jimmy", email="test@gmail.com", picture="https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png")
session.add(user1)
session.commit()

# Create  games of console ps4
console1 = Console(user_id=1, name="PlayStation 4")
session.add(console1)
session.commit()

game1 = Game(user_id=1,
             name="Bloodborne",
             date="2015-03-24",
             type="action role-playing video game",
             developer="FROM SOFTWARE",
             console=console1)
session.add(game1)
session.commit()

game2 = Game(user_id=1,
             name="The Last of Us Remastered",
             date="2014-07-29",
             type="action-adventure survival horror video game",
             developer="Naughty Dog",
             console=console1)
session.add(game2)
session.commit()

game3 = Game(user_id=1,
             name="Uncharted 4: A Thief's End",
             date="2016-05-10",
             type="action-adventure video game",
             developer="Naughty Dog",
             console=console1)
session.add(game3)
session.commit()

game4 = Game(user_id=1,
             name="Horizon:Zero Dawn",
             date="2017-02-28",
             type="action role-playing video game",
             developer="Guerrilla Games",
             console=console1)
session.add(game4)
session.commit()

game5 = Game(user_id=1,
             name="GOD OF WAR",
             date="2018-04-20",
             type="action-adventure video game",
             developer="Santa Monica Studio",
             console=console1)
session.add(game5)
session.commit()

# Create games of console xbox one
console2 = Console(user_id=1, name="Xbox One")
session.add(console2)
session.commit()

game1 = Game(user_id=1,
             name="Halo 5: Guardians",
             date="2015-10-27",
             type="first-person shooter video game",
             developer="343 Industries",
             console=console2)
session.add(game1)
session.commit()

game2 = Game(user_id=1,
             name="Gears of War 4",
             date="2016-10-11",
             type="third-person shooter video game",
             developer="The Coalition",
             console=console2)
session.add(game2)
session.commit()

game3 = Game(user_id=1,
             name="Quantum Break",
             date="2016-04-05",
             type="third-person shooter video game",
             developer="Remedy Entertainment",
             console=console2)
session.add(game3)
session.commit()

game4 = Game(user_id=1,
             name="TitanFall",
             date="2014-03-11",
             type="multiplayer first-person shooter video game",
             developer="Respawn Entertainment",
             console=console2)
session.add(game4)
session.commit()

game5 = Game(user_id=1,
             name="Forza Motorsport 6",
             date="2015-09-15",
             type="racing video game",
             developer="Turn 10 Studios",
             console=console2)
session.add(game5)
session.commit()

# Create games of console NS
console3 = Console(user_id=1, name="Nintendo Switch")
session.add(console3)
session.commit()

game1 = Game(user_id=1,
             name="Super Mario Odyssey",
             date="2017-10-27",
             type="platform video game",
             developer="Nintendo",
             console=console3)
session.add(game1)
session.commit()

game2 = Game(user_id=1,
             name="The Legend of Zelda: Breath of the Wild",
             date="2017-03-03",
             type="action-adventure video game",
             developer="Nintendo",
             console=console3)
session.add(game2)
session.commit()

game3 = Game(user_id=1,
             name="Xenoblade Chronicles 2",
             date="2017-12-01",
             type="action role-playing video game",
             developer="Monolith Soft",
             console=console3)
session.add(game3)
session.commit()

game4 = Game(user_id=1,
             name="Splatoon2",
             date="2017-07-21",
             type="team-based third-person shooter video game",
             developer="Nintendo",
             console=console3)
session.add(game4)
session.commit()

game5 = Game(user_id=1,
             name="Mario Kart 8 Deluxe",
             date="2017-04-28",
             type="racing video game",
             developer="Nintendo",
             console=console3)
session.add(game5)
session.commit()

print "added basic consoles and games!!!"
