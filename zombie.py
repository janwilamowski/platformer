from Character import Character

zombie_states = [
    'Idle',
    'Walk',
    'Dead',
    'Attack',
]

class Zombie(Character):

    def __init__(self, position, screen, is_male=True):
        gender = 'male' if is_male else 'female'
        super(Zombie, self).__init__('gfx/zombie/' + gender, zombie_states, position, screen)
