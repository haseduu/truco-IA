from dataclasses import dataclass
from typing import List, Dict, Optional, Union, Literal
from enum import Enum
import random
from abc import ABC, abstractmethod

class CardValue(Enum):
    FOUR = 1
    FIVE = 2
    SIX = 3
    SEVEN = 4
    QUEEN = 5
    JACK = 6
    KING = 7
    ACE = 8
    TWO = 9
    THREE = 10

class Suit(Enum):
    OUROS = 1
    ESPADAS = 2
    COPAS = 3
    PAUS = 4

    def __str__(self) -> str:
        return self.name.capitalize()

@dataclass
class Card:
    value: CardValue
    suit: Suit
    is_manilha: bool = False
    is_hidden: bool = False

    @property
    def display_value(self) -> str:
        value_map = {
            CardValue.FOUR: "4",
            CardValue.FIVE: "5",
            CardValue.SIX: "6",
            CardValue.SEVEN: "7",
            CardValue.QUEEN: "Q",
            CardValue.JACK: "J",
            CardValue.KING: "K",
            CardValue.ACE: "Ás",
            CardValue.TWO: "2",
            CardValue.THREE: "3"
        }
        return value_map[self.value]

    def __str__(self) -> str:
        if self.is_hidden:
            return "Carta escondida"
        return f"{self.display_value} de {self.suit}"

    def get_power(self) -> int:
        if self.is_hidden:
            return 0
        if self.is_manilha:
            return 20 + self.suit.value
        return self.value.value

class Deck:
    def __init__(self):
        self.cards: List[Card] = [
            Card(value, suit)
            for value in CardValue
            for suit in Suit
        ]
        self.shuffle()

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self, count: int = 1) -> List[Card]:
        if count > len(self.cards):
            raise ValueError("Not enough cards in the deck")
        drawn = self.cards[:count]
        self.cards = self.cards[count:]
        return drawn

    def draw_vira(self) -> Card:
        return self.draw(1)[0]

class Player(ABC):
    def __init__(self, name: str, team: Literal["Team1", "Team2"]):
        self.name = name
        self.team = team
        self.hand: List[Card] = []

    @property
    def team_name(self) -> str:
        return "Time 1" if self.team == "Team1" else "Time 2"

    def add_cards(self, cards: List[Card]) -> None:
        self.hand.extend(cards)

    def clear_hand(self) -> None:
        self.hand = []

    def show_hand(self) -> None:
        print(f"\nMão de {self.name} ({self.team_name}):")
        for i, card in enumerate(self.hand, 1):
            print(f"{i}. {card}")

    @abstractmethod
    def play_card(self, game_state: 'GameState') -> Card:
        pass

    @abstractmethod
    def decide_truco(self, game_state: 'GameState', new_value: int) -> str:
        pass

    @abstractmethod
    def want_to_truco(self, game_state: 'GameState') -> bool:
        pass

class HumanPlayer(Player):
    def play_card(self, game_state: 'GameState') -> Card:
        self.show_hand()
        while True:
            try:
                choice = int(input(f"{self.name} ({self.team_name}), escolha uma carta (1-{len(self.hand)}): ")) - 1
                if 0 <= choice < len(self.hand):
                    card = self.hand.pop(choice)
                    if game_state.round_number >= 2:
                        if input("Quer esconder essa carta? (s/n): ").lower() == 's':
                            card.is_hidden = True
                    return card
                print("Escolha inválida!")
            except ValueError:
                print("Por favor, digite um número válido!")

    def decide_truco(self, game_state: 'GameState', new_value: int) -> str:
        self.show_hand()
        while True:
            decision = input(f"{self.name} ({self.team_name}), aceitar {new_value}? (sim/nao/aumentar): ").lower()
            if decision in ['sim', 'nao', 'aumentar']:
                return decision
            print("Opção inválida!")

    def want_to_truco(self, game_state: 'GameState') -> bool:
        if game_state.last_truco_team == self.team:
            return False
        self.show_hand()
        return input(f"{self.name} ({self.team_name}), quer pedir truco? (s/n): ").lower() == 's'

class AIPlayer(Player):
    def evaluate_hand(self, game_state: 'GameState') -> float:
        total_power = sum(card.get_power() for card in self.hand)
        manilhas = sum(1 for card in self.hand if card.is_manilha)
        return total_power + (manilhas * 5)

    def play_card(self, game_state: 'GameState') -> Card:
        if not game_state.table_cards:
            return self.hand.pop(min(range(len(self.hand)), 
                                   key=lambda i: self.hand[i].get_power()))
        
        table_max = max((card.get_power() for card, _ in game_state.table_cards), default=0)
        winning_cards = [(i, card) for i, card in enumerate(self.hand) 
                        if card.get_power() > table_max]
        
        if winning_cards:
            idx = min(winning_cards, key=lambda x: x[1].get_power())[0]
            return self.hand.pop(idx)
        
        return self.hand.pop(min(range(len(self.hand)), 
                               key=lambda i: self.hand[i].get_power()))

    def decide_truco(self, game_state: 'GameState', new_value: int) -> str:
        hand_strength = self.evaluate_hand(game_state)
        print(f"\nIA {self.name} está pensando...")
        if hand_strength > 30:
            decision = "aumentar"
        elif hand_strength > 20:
            decision = "sim"
        elif new_value >= 9 and hand_strength < 15:
            decision = "nao"
        else:
            decision = "sim"
        print(f"IA {self.name} decidiu: {decision}")
        return decision

    def want_to_truco(self, game_state: 'GameState') -> bool:
        if game_state.last_truco_team == self.team:
            return False
        hand_strength = self.evaluate_hand(game_state)
        should_truco = (
            hand_strength > 25 or
            (game_state.round_number == 1 and hand_strength > 20) or
            (len(game_state.table_cards) > 0 and hand_strength > 15)
        )
        if should_truco:
            print(f"\nIA {self.name} decidiu pedir truco!")
        return should_truco

@dataclass
class GameState:
    round_number: int
    table_cards: List[tuple[Card, Player]]
    round_value: int
    team1_score: int
    team2_score: int
    vira: Card
    manilhas: List[Card]
    last_truco_team: Optional[str] = None

class TrucoGame:
    TRUCO_VALUES = {1: 3, 3: 6, 6: 9, 9: 12}

    def __init__(self, team_size: int = 2):
        self.team_size = team_size
        self.team1: List[Player] = []
        self.team2: List[Player] = []
        self.setup_teams()
        self.team1_score = 0
        self.team2_score = 0
        self.current_player_index = 0
        self.hand_starter_index = 0

    def setup_teams(self) -> None:
        for team_num in range(1, 3):
            team = []
            for player_num in range(self.team_size):
                while True:
                    name = input(f"\nNome do jogador {player_num + 1} do Time {team_num}: ")
                    player_type = input("Humano ou IA? (h/i): ").lower()
                    if player_type == 'h':
                        player = HumanPlayer(name, f"Team{team_num}")
                        break
                    elif player_type == 'i':
                        player = AIPlayer(name, f"Team{team_num}")
                        break
                    print("Opção inválida!")
                team.append(player)
            if team_num == 1:
                self.team1 = team
            else:
                self.team2 = team

    def play(self) -> None:
        while max(self.team1_score, self.team2_score) < 12:
            self.play_round()
            print(f"\nPlacar: Time 1: {self.team1_score}, Time 2: {self.team2_score}")
        
        winner = "Time 1" if self.team1_score >= 12 else "Time 2"
        print(f"\n🏆 {winner} venceu o jogo! 🏆")

    def play_round(self) -> None:
        deck = Deck()
        self.deal_cards(deck)
        vira = deck.draw_vira()
        manilhas = self.determine_manilhas(vira)
        
        game_state = GameState(
            round_number=1,
            table_cards=[],
            round_value=1,
            team1_score=self.team1_score,
            team2_score=self.team2_score,
            vira=vira,
            manilhas=manilhas,
            last_truco_team=None
        )
        
        self.current_player_index = self.hand_starter_index
        
        round_winner = self.play_hand(game_state)
        if round_winner == "Team1":
            self.team1_score += game_state.round_value
        elif round_winner == "Team2":
            self.team2_score += game_state.round_value
            
        self.hand_starter_index = (self.hand_starter_index + 1) % (self.team_size * 2)

    def play_hand(self, game_state: GameState) -> Optional[str]:
        team1_wins = 0
        team2_wins = 0
        
        while team1_wins < 2 and team2_wins < 2 and game_state.round_number <= 3:
            self.show_game_state(game_state)
            players = self.get_play_order()
            
            # Check for truco before playing cards
            for player in players:
                if player.want_to_truco(game_state):
                    next_player_index = (players.index(player) + 1) % len(players)
                    next_player = players[next_player_index]
                    
                    if not self.handle_truco(game_state, player, next_player):
                        return player.team  # Return early if truco is rejected
            
            winner_team = self.play_trick(game_state)
            if winner_team == "Team1":
                team1_wins += 1
            elif winner_team == "Team2":
                team2_wins += 1
            
            game_state.round_number += 1
            print(f"\nParcial: Time 1: {team1_wins} vs Time 2: {team2_wins}")
            
        if team1_wins > team2_wins:
            return "Team1"
        elif team2_wins > team1_wins:
            return "Team2"
        return None

    def play_trick(self, game_state: GameState) -> Optional[str]:
        game_state.table_cards = []
        players = self.get_play_order()
        
        for player in players:
            self.show_game_state(game_state)
            card = player.play_card(game_state)
            game_state.table_cards.append((card, player))
            print(f"\n{player.name} ({player.team_name}) jogou {card}")
            
        winner = self.determine_trick_winner(game_state.table_cards)
        if winner:
            print(f"\n{winner.name} ({winner.team_name}) venceu a rodada!")
            self.current_player_index = self.get_all_players().index(winner)
            return winner.team
        print("\nRodada empatou!")
        return None

    def handle_truco(self, game_state: GameState, current_player: Player, next_player: Player) -> bool:
        if game_state.round_value >= 12:
            print("Valor máximo já alcançado!")
            return True

        new_value = self.TRUCO_VALUES[game_state.round_value]
        print(f"\n{current_player.name} ({current_player.team_name}) pediu {new_value}!")

        decision = next_player.decide_truco(game_state, new_value)
        
        if decision == "sim":
            print(f"\n{new_value} aceito!")
            game_state.round_value = new_value
            game_state.last_truco_team = current_player.team
            return True
        elif decision == "nao":
            print("\nRecusado!")
            return False
        elif decision == "aumentar":
            game_state.round_value = new_value
            next_new_value = self.TRUCO_VALUES.get(new_value, new_value)
            print(f"\n{next_player.name} ({next_player.team_name}) quer aumentar para {next_new_value}!")
            return self.handle_truco(game_state, next_player, current_player)
        
        return True

    def determine_trick_winner(self, table_cards: List[tuple[Card, Player]]) -> Optional[Player]:
        if not table_cards:
            return None
            
        max_power = max(card.get_power() for card, _ in table_cards)
        winners = [(card, player) for card, player in table_cards 
                  if card.get_power() == max_power]
        
        if len(winners) == 1:
            return winners[0][1]
        return None

    def determine_manilhas(self, vira: Card) -> List[Card]:
        next_value = list(CardValue)[list(CardValue).index(vira.value) + 1 
                                   if vira.value != CardValue.THREE 
                                   else 0]
        manilhas = []
        for suit in Suit:
            manilha = Card(next_value, suit, is_manilha=True)
            manilhas.append(manilha)
        return manilhas

    def deal_cards(self, deck: Deck) -> None:
        for player in self.team1 + self.team2:
            player.clear_hand()
            player.add_cards(deck.draw(3))

    def get_all_players(self) -> List[Player]:
        all_players = []
        for i in range(len(self.team1)):
            all_players.append(self.team1[i])
            all_players.append(self.team2[i])
        return all_players

    def get_play_order(self) -> List[Player]:
        all_players = self.get_all_players()
        return all_players[self.current_player_index:] + all_players[:self.current_player_index]

    def show_game_state(self, game_state: GameState) -> None:
        print(f"\n{'=' * 50}")
        print(f"Rodada: {game_state.round_number} | Valor: {game_state.round_value}")
        print(f"Vira: {game_state.vira}")
        if game_state.table_cards:
            print("\nCartas na mesa:")
            for card, player in game_state.table_cards:
                print(f"{player.name}: {card}")
        print(f"{'=' * 50}")

if __name__ == "__main__":
    game = TrucoGame()
    game.play()