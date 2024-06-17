import random

# Definição dos valores das cartas e dos naipes
cartas = {"4": 1, "5": 2, "6": 3, "7": 4, "Q": 5, "J": 6, "K": 7, "Ás": 8, "2": 9, "3": 10}
naipes = {"Ouros": 1, "Espadas": 2, "Copas": 3, "Paus": 4}
members_in_team = 2

class Carta:
    def __init__(self, num, naipe, manilha=False):
        self.carta_num = num
        self.carta_naipe = naipe
        self.value = cartas[num]
        self.carta = f"{num} de {naipe}"
        self.manilha = manilha

    def __repr__(self):
        return self.carta

class Baralho:
    def __init__(self):
        self.cartas = [Carta(num, naipe) for num in cartas for naipe in naipes]
        self.embaralhar()

    def embaralhar(self):
        random.shuffle(self.cartas)

    def distribuir(self, num_cartas):
        if num_cartas > len(self.cartas):
            raise ValueError("Não há cartas suficientes no baralho.")
        mao = self.cartas[:num_cartas]
        self.cartas = self.cartas[num_cartas:]
        return mao

    def virar_carta(self):
        # Vira a última carta do baralho como a "vira"
        return self.cartas.pop()

class Player:
    def __init__(self, name, team):
        self.team = team
        self.name = name
        self.hand = []
        self.ia = False
    def add_card(self, carta):
        self.hand.append(carta)

    def show_hand(self):
        print(f"\nMão de {self.name}:")
        for i, card in enumerate(self.hand):
            print(f"{i+1}. {card.carta}")


class IA(Player):
    def __init__(self, name, team):
        super().__init__(name, team)
        self.ia = True

    def choose_best_card(self, cards_played):
        manilhacounter = 0
        highest_card = None
        highest_card_v = -1
        lowest_card = None
        lowest_card_v = float('inf')
        highest_card_in_table = -1
        
        for card_p in cards_played:
            if card_p.value > highest_card_in_table:
                highest_card_in_table = card_p.value
        
        for card in self.hand:
            if card.manilha:
                manilhacounter += 1
            if card.value >= highest_card_v:
                highest_card_v = card.value
                highest_card = card
            if card.value <= lowest_card_v:
                lowest_card_v = card.value
                lowest_card = card
        
        if manilhacounter >= 2:
            return random.choice(self.hand)
        
        if len(cards_played) == 0:
            return lowest_card
        
        if len(cards_played) == 1:
            if highest_card_in_table < highest_card.value:
                return highest_card
            return lowest_card
        
        if len(cards_played) >= 2:
            if highest_card_in_table < highest_card.value:
                return highest_card
            return lowest_card
        
        return lowest_card

    def should_ask_truco(self, round_number, points, cards_played):
        manilhacounter = 0
        strong_cards = 0
        threshold = 5
        
        for card in self.hand:
            if card.manilha:
                manilhacounter += 1
            if card.value >= threshold:
                strong_cards += 1
        
        if points >= 8:
            return True
        
        if manilhacounter >= 1 and strong_cards >= 2:
            return True
        
        if round_number == 1 and strong_cards >= 2:
            return True
        
        if round_number == 2 and strong_cards >= 1:
            return True
        
        if len(cards_played) >= 1:
            highest_card_in_table = max(card.value for card in cards_played)
            if highest_card_in_table < max(card.value for card in self.hand):
                return True
        
        return False

        
   
        






            

    
class Game:
    def __init__(self):
        self.team1_len = members_in_team
        self.team2_len = members_in_team
        self.team1 = []
        self.team2 = []
        self.baralho = Baralho()
        
        while len(self.team1) < self.team1_len:
            name = input("\nDigite o nome do jogador do time 1: ")
            if name == "IA":
                player = IA(name, "time1")
            else:
                player = Player(name, "time1")
            self.team1.append(player)

        while len(self.team2) < self.team2_len:
            name = input("\nDigite o nome do jogador do time 2: ")
            if name == "IA":
                player = IA(name, "time2")
            else:
                player = Player(name, "time2")
            self.team2.append(player)

        self.team1_score = 0
        self.team2_score = 0
        self.index = 0
        self.round_value = 1  # Valor inicial da rodada
        self.last_truco_team = None  # Controle do último time que trucou
        self.vira = None
        self.manilhas = []
    def game(self):
        while self.team1_score < 12 or self.team2_score < 12:
            self.play_round()
        if self.team1_score >= 12:
            print(f"------------------------------------\nO time vencedor foi o time 1\n ------------------------------------")
        if self.team2_score >= 12:
            print(f"------------------------------------\nO time vencedor foi o time 2\n ------------------------------------")
    def determinar_manilhas(self):
        vira_index = list(cartas.values()).index(self.vira.value)
        manilha_index = (vira_index + 1) % len(cartas)
        manilha_num = list(cartas.keys())[manilha_index]
        self.manilhas = [Carta(manilha_num, naipe, manilha=True) for naipe in naipes]
        # Set manilha attribute to True for each manilha card
        
        print(f"\nVira: {self.vira.carta}")
        print(f"Manilhas: {', '.join([manilha.carta for manilha in self.manilhas])}")
        
    def manilha_valor(self, carta):
        
        if carta.manilha:
            return 20 + naipes[carta.carta_naipe]
        return carta.value

    def generate_cards(self):
        for player in self.team1 + self.team2:
            for _ in range(3):
                carta = self.baralho.distribuir(1)[0]
                player.add_card(carta)

    def clear_cards(self):
        for player in self.team1 + self.team2:
            player.hand = []

    def truco(self, current_player):
        if self.round_value == 1:
            new_value = 3
        elif self.round_value == 3:
            new_value = 6
        elif self.round_value == 6:
            new_value = 9
        elif self.round_value == 9:
            new_value = 12
        else:
            return True  # Já está em 12, não pode trucar mais

        # Apenas permitir truco se o oponente trucou
        if self.last_truco_team == current_player.team:
            print(f"\n{current_player.name}, seu time já pediu truco, não pode pedir de novo.")
            return True

        print(f"\n{current_player.name} pede {new_value}!")

        decision = input(f"Aceitar {new_value}? (sim/nao): ").lower()

        if decision == "sim":
            print(f"\n{new_value} aceito!")
            self.round_value = new_value
            self.last_truco_team = current_player.team
        elif decision == "nao":
            print("\nRecusado! Oponente ganha a rodada.")
            if current_player.team == "time1":
                self.team2_score += self.round_value
            else:
                self.team1_score += self.round_value
            return False  # Rodada encerrada devido a recusa
        return True

    def play_round(self):
        team1_partial_score = 0
        team2_partial_score = 0
        base_order = [self.team1[0], self.team2[0], self.team1[1], self.team2[1]]
        self.generate_cards()
        self.round_value = 1  # Reiniciar valor da rodada
        self.last_truco_team = None  # Reiniciar controle de truco

        # Definir vira e manilhas
        self.vira = self.baralho.virar_carta()
        self.determinar_manilhas()

        while team1_partial_score < 2 and team2_partial_score < 2:
            order = base_order[self.index:] + base_order[:self.index]
            cards_played = []
            current_highest_card = None
            current_highest_card_value = -1
            winner = None
            round_number = 0
            for player in order:
                if player.ia:
                    if player.team == "time1":
                        points = self.team1_score
                    else:
                        points = self.team2_score
                    truco = player.should_ask_truco(round_number, points, cards_played)
                    if truco:
                        if self.round_value < 12 and self.last_truco_team != player.team:
                            if self.round_value > 1:
                                truco_prompt = f"{player.name}, quer aumentar para {self.round_value * 2}? (sim/não): "
                            else:
                                truco_prompt = f"{player.name}, quer pedir truco? (sim/não): "
                            if not self.truco(player):
                                return 
                    played_card = player.choose_best_card(cards_played)
                    

                else:
                    if cards_played:
                        print("\n------------------CARTAS DA MESA------------------")
                        for card in cards_played:
                            print(f"\n{card.carta}")
                        print("\n--------------------------------------------------")
                    player.show_hand()

                    # Verificar se o jogador quer aumentar a aposta
                    if self.round_value < 12 and self.last_truco_team != player.team:
                        if self.round_value > 1:
                            truco_prompt = f"{player.name}, quer aumentar para {self.round_value * 2}? (sim/não): "
                        else:
                            truco_prompt = f"{player.name}, quer pedir truco? (sim/não): "
                        
                        if input(truco_prompt).lower() == "sim":
                            if not self.truco(player):
                                return  # Rodada encerrada devido a recusa de truco

                        choice = int(input("Escolha uma carta para jogar (1-3): ")) - 1
                        while 0 > choice or choice >= len(player.hand):
                            print("Escolha inválida")
                            choice = int(input("Escolha uma carta para jogar (1-3): ")) - 1
                        
                        played_card = player.hand.pop(choice)
                        print(f"{player.name} joga {played_card.carta}.")
                cards_played.append(played_card)
                
                played_card_value = self.manilha_valor(played_card)
                if played_card_value > current_highest_card_value:
                    current_highest_card = played_card
                    current_highest_card_value = played_card_value
                    winner = player
                elif played_card_value == current_highest_card_value and winner.team != player.team:
                    winner = None  # Empate entre times

            if winner:
                team_winner = winner.team
                print(f"\nO vencedor foi o {team_winner} com a carta {current_highest_card.carta}")
                if team_winner == "time1":
                    team1_partial_score += 1
                else:
                    team2_partial_score += 1
            else:
                print("\nA rodada melou")
                team1_partial_score += 1
                team2_partial_score += 1
            self.index += 1
            round_number += 1
            print(f"\nPontuação: Time 1: {team1_partial_score}, Time 2: {team2_partial_score}")
        

        if team1_partial_score > team2_partial_score:
            self.team1_score += self.round_value
        elif team2_partial_score > team1_partial_score:
            self.team2_score += self.round_value
        else:
            print("Rodada empatou, ninguém ganhou pontos!")
       
if __name__ == "__main__":
    game = Game()
    game.game()
