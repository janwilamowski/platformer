from character import Character, Dir

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
        self.state = 'Walk'
        self.velocity.x = 1


    def update(self, level):
        super(Zombie, self).update(level)
        if Dir.right in self.collisions or Dir.left in self.collisions:
            # bumped into something, turn around
            self.facing_right = not self.facing_right
            self.velocity.x *= -1
