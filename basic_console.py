from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Console, Game

engine = create_engine('sqlite:///consolegames.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create  games of console ps4
console1 = Console(name="PlayStation 4")
session.add(console1)
session.commit()

game1 = Game(name="Bloodborne",
             date="2015-03-24",
             type="action role-playing video game",
             developer="FROM SOFTWARE",
             console=console1)
session.add(game1)
session.commit()

game2 = Game(name="The Last of Us Remastered",
             date="2014-07-29",
             type="action-adventure survival horror video game",
             developer="Naughty Dog",
             console=console1)
session.add(game2)
session.commit()

game3 = Game(name="Uncharted 4: A Thief's End",
             date="2016-05-10",
             type="action-adventure video game",
             developer="Naughty Dog",
             console=console1)
session.add(game3)
session.commit()

game4 = Game(name="Horizon:Zero Dawn",
             date="2017-02-28",
             type="action role-playing video game",
             developer="Guerrilla Games",
             console=console1)
session.add(game4)
session.commit()

game5 = Game(name="GOD OF WAR",
             date="2018-04-20",
             type="action-adventure video game",
             developer="Santa Monica Studio",
             console=console1)
session.add(game5)
session.commit()

# Create games of console xbox one
console2 = Console(name="Xbox One")
session.add(console2)
session.commit()

game1 = Game(name="Halo 5: Guardians",
             date="2015-10-27",
             type="first-person shooter video game",
             developer="343 Industries",
             console=console2)
session.add(game1)
session.commit()

game2 = Game(name="Gears of War 4",
             date="2016-10-11",
             type="third-person shooter video game",
             developer="The Coalition",
             console=console2)
session.add(game2)
session.commit()

game3 = Game(name="Quantum Break",
             date="2016-04-05",
             type="third-person shooter video game",
             developer="Remedy Entertainment",
             console=console2)
session.add(game3)
session.commit()

game4 = Game(name="TitanFall",
             date="2014-03-11",
             type="multiplayer first-person shooter video game",
             developer="Respawn Entertainment",
             console=console2)
session.add(game4)
session.commit()

game5 = Game(name="Forza Motorsport 6",
             date="2015-09-15",
             type="racing video game",
             developer="Turn 10 Studios",
             console=console2)
session.add(game5)
session.commit()

# Create games of console NS
console3 = Console(name="Nintendo Switch")
session.add(console3)
session.commit()

game1 = Game(name="Super Mario Odyssey",
             date="2017-10-27",
             type="platform video game",
             developer="Nintendo",
             console=console3)
session.add(game1)
session.commit()

game2 = Game(name="The Legend of Zelda: Breath of the Wild",
             date="2017-03-03",
             type="action-adventure video game",
             developer="Nintendo",
             console=console3)
session.add(game2)
session.commit()

game3 = Game(name="Xenoblade Chronicles 2",
             date="2017-12-01",
             type="action role-playing video game",
             developer="Monolith Soft",
             console=console3)
session.add(game3)
session.commit()

game4 = Game(name="Splatoon2",
             date="2017-07-21",
             type="team-based third-person shooter video game",
             developer="Nintendo",
             console=console3)
session.add(game4)
session.commit()

game5 = Game(name="Mario Kart 8 Deluxe",
             date="2017-04-28",
             type="racing video game",
             developer="Nintendo",
             console=console3)
session.add(game5)
session.commit()

print "added basic consoles and games!!!"
