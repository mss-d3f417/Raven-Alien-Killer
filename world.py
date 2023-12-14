import pygame
from ship import Ship
from alien import Alien
from settings import HEIGHT, WIDTH, ENEMY_SPEED, CHARACTER_SIZE, BULLET_SIZE, NAV_THICKNESS
from bullet import Bullet
from display import Display

class World:
	def __init__(self, screen):
		self.screen = screen

		self.player = pygame.sprite.GroupSingle()
		self.aliens = pygame.sprite.Group()
		self.display = Display(self.screen)

		self.game_over = False
		self.player_score = 0
		self.game_level = 1

		self._generate_world()


	def _generate_aliens(self):
		
		alien_cols = (WIDTH // CHARACTER_SIZE) // 2
		alien_rows = 3
		for y in range(alien_rows):
			for x in range(alien_cols):
				my_x = CHARACTER_SIZE * x
				my_y = CHARACTER_SIZE * y
				specific_pos = (my_x, my_y)
				self.aliens.add(Alien(specific_pos, CHARACTER_SIZE, y))
		
	
	def _generate_world(self):
		
		player_x, player_y = WIDTH // 2, HEIGHT - CHARACTER_SIZE
		center_size = CHARACTER_SIZE // 2
		player_pos = (player_x - center_size, player_y)
		self.player.add(Ship(player_pos, CHARACTER_SIZE))

		self._generate_aliens()


	def add_additionals(self):
		
		nav = pygame.Rect(0, HEIGHT, WIDTH, NAV_THICKNESS)
		pygame.draw.rect(self.screen, pygame.Color("gray"), nav)

		
		self.display.show_life(self.player.sprite.life)
		self.display.show_score(self.player_score)
		self.display.show_level(self.game_level)


	def player_move(self, attack = False):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_a] and not self.game_over or keys[pygame.K_LEFT] and not self.game_over:
			if self.player.sprite.rect.left > 0:
				self.player.sprite.move_left()
		if keys[pygame.K_d] and not self.game_over or keys[pygame.K_RIGHT] and not self.game_over:
			if self.player.sprite.rect.right < WIDTH:
				self.player.sprite.move_right()
		if keys[pygame.K_w] and not self.game_over or keys[pygame.K_UP] and not self.game_over:
			if self.player.sprite.rect.top > 0:
				self.player.sprite.move_up()		
		if keys[pygame.K_s] and not self.game_over or keys[pygame.K_DOWN] and not self.game_over:
			if self.player.sprite.rect.bottom < HEIGHT:
				self.player.sprite.move_bottom()

		
		if keys[pygame.K_r]:
			self.game_over = False
			self.player_score = 0
			self.game_level = 1
			for alien in self.aliens.sprites():
				alien.kill()
			self._generate_world()

		if attack and not self.game_over:
			self.player.sprite._shoot()


	def _detect_collisions(self):
		
		player_attack_collision = pygame.sprite.groupcollide(self.aliens, self.player.sprite.player_bullets, True, True)
		if player_attack_collision:
			self.player_score += 10

		
		for alien in self.aliens.sprites():	
			alien_attack_collision = pygame.sprite.groupcollide(alien.bullets, self.player, True, False)
			if alien_attack_collision:
				self.player.sprite.life -= 1
				break

		
		alien_to_player_collision = pygame.sprite.groupcollide(self.aliens, self.player, True, False)
		if alien_to_player_collision:
			self.player.sprite.life -= 1


	def _alien_movement(self):
		move_sideward = False
		move_forward = False

		for alien in self.aliens.sprites():
			if alien.to_direction == "right" and alien.rect.right < WIDTH or alien.to_direction == "left" and alien.rect.left > 0:
				move_sideward = True
				move_forward = False
			else:
				move_sideward = False
				move_forward = True
				alien.to_direction = "left" if alien.to_direction == "right" else "right"
				break

		for alien in self.aliens.sprites():
			if move_sideward and not move_forward:
				if alien.to_direction == "right":
					alien.move_right()
				if alien.to_direction == "left":
					alien.move_left()
			if not move_sideward and move_forward:
					alien.move_bottom()


	def _alien_shoot(self):
		for alien in self.aliens.sprites():
			if (WIDTH - alien.rect.x) // CHARACTER_SIZE == (WIDTH - self.player.sprite.rect.x) // CHARACTER_SIZE:
				alien._shoot()
				break


	def _check_game_state(self):
		
		if self.player.sprite.life <= 0:
			self.game_over = True
			self.display.game_over_message()
		for alien in self.aliens.sprites():
			if alien.rect.top >= HEIGHT:
				self.game_over = True
				self.display.game_over_message()
				break

		
		if len(self.aliens) == 0 and self.player.sprite.life > 0:
			self.game_level += 1
			self._generate_aliens()
			for alien in self.aliens.sprites():
				alien.move_speed += self.game_level - 1


	def update(self):
		
		self._detect_collisions()

		
		self._alien_movement()

		
		self._alien_shoot()

		
		self.player.sprite.player_bullets.update()
		self.player.sprite.player_bullets.draw(self.screen)

		[alien.bullets.update() for alien in self.aliens.sprites()]
		[alien.bullets.draw(self.screen) for alien in self.aliens.sprites()]

		
		self.player.update()
		self.player.draw(self.screen)

		
		self.aliens.draw(self.screen)

		
		self.add_additionals()

		
		self._check_game_state()