from nada_dsl import *

class Order:
    def __init__(self, order_id, trader, amount, price, is_buy):
        self.order_id = order_id
        self.trader = trader
        self.amount = amount
        self.price = price
        self.is_buy = is_buy

def nada_main():
    num_orders = 10
    traders = [Party(name=f"Trader{i}") for i in range(num_orders)]
    party_official = Party(name="Official")
    
    orders_list = []
    for i in range(num_orders):
        order_id = Integer(i + 1)
        trader = traders[i]
        amount = SecretInteger(Input(name=f"amount_{i}", party=trader))
        price = SecretInteger(Input(name=f"price_{i}", party=trader))
        is_buy = SecretBoolean(Input(name=f"is_buy_{i}", party=trader))
        
        orders_list.append(Order(order_id, trader, amount, price, is_buy))

    matched_orders = []
    for i in range(num_orders):
        buy_order = orders_list[i]
        for j in range(num_orders):
            sell_order = orders_list[j]

            # Check if the current order is a match (maintaining privacy)
            is_match = buy_order.is_buy.if_else(
                sell_order.is_buy.if_else(
                    Boolean(False),  # If sell_order is also a buy, no match
                    buy_order.price <= sell_order.price  # Match if buy price >= sell price
                ),
                Boolean(False)  # If not a buy order, no match
            )

            # Store matched order IDs using conditional outputs
            match_result = is_match.if_else((buy_order.order_id, sell_order.order_id), (Integer(0), Integer(0)))
            matched_orders.append(match_result)

    output_list = []
    for idx, match in enumerate(matched_orders):
        output_list.append(Output(match[0], f"buy_order_{idx}", party_official))
        output_list.append(Output(match[1], f"sell_order_{idx}", party_official))

    return output_list

if __name__ == "__main__":
    nada_main()
