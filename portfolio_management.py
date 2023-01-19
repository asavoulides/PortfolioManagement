import tkinter as tk
from tkinter import ttk
import requests
import json
import matplotlib.pyplot as plt
import datetime

class Portfolio:
    def __init__(self):
        self.api_key = "ZOFF8JEDW0TCPKSS"
        self.portfolio = {}
        self.root = tk.Tk()
        self.plot_all_button = tk.Button(self.root, text="Plot All", command=self.plot_all)
        self.plot_all_button.pack()
        self.create_gui()
        
    def add_stock(self, symbol, shares):
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        response = requests.get(url, params=params)
        data = json.loads(response.text)
        price = float(data["Global Quote"]["05. price"])
        self.portfolio[symbol] = {"shares": shares, "price": price}
    def plot_all(self):
        now = datetime.datetime.now()
        six_months_ago = now - datetime.timedelta(days=182)
        symbols = list(self.portfolio.keys())
        fig, axs = plt.subplots(len(symbols), 1, figsize=(10, 5*len(symbols)))

        for i, symbol in enumerate(symbols):
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_DAILY_ADJUSTED",
                "symbol": symbol,
                "apikey": self.api_key,
                "outputsize": "compact",
                "datatype": "json"
            }
            response = requests.get(url, params=params)
            data = json.loads(response.text)

            history = data["Time Series (Daily)"]
            dates = []
            values = []
            for date in history:
                if datetime.datetime.strptime(date, "%Y-%m-%d") < six_months_ago:
                    break
                dates.append(date)
                values.append(float(history[date]["4. close"]))

            axs[i].plot(dates, values)
            axs[i].set_title(symbol)

        plt.show()
    def remove_stock(self, symbol):
        del self.portfolio[symbol]
        
    def update_portfolio(self):
        for symbol in self.portfolio.keys():
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            response = requests.get(url, params=params)
            data = json.loads(response.text)
            self.portfolio[symbol]["price"] = float(data["Global Quote"]["05. price"])
            
    def get_portfolio_value(self):
        total_value = 0
        for symbol in self.portfolio.keys():
            total_value += self.portfolio[symbol]["shares"] * self.portfolio[symbol]["price"]
        return total_value

    def create_gui(self):
        self.root = tk.Tk()
        self.root.title("Portfolio Management Tool")

        self.tree = ttk.Treeview(self.root)
        self.tree["columns"] = ("symbol", "shares", "price", "value")
        self.tree.heading("symbol", text="Symbol")
        self.tree.heading("shares", text="Shares")
        self.tree.heading("price", text="Price")
        self.tree.heading("value", text="Value")

        self.tree.column("symbol", width=100)
        self.tree.column("shares", width=100)
        self.tree.column("price", width=100)
        self.tree.column("value", width=100)

        self.tree.pack()

        self.add_button = tk.Button(self.root, text="Add Stock", command=self.add_stock_gui)
        self.add_button.pack()

        self.remove_button = tk.Button(self.root, text="Remove Stock", command=self.remove_stock_gui)
        self.remove_button.pack()

        self.update_button = tk.Button(self.root, text="Update Portfolio", command=self.update_portfolio)
        self.update_button.pack()

        self.root.mainloop()

    def add_stock_gui(self):
        self.add_window = tk.Toplevel()
        self.add_window.title("Add Stock")

        symbol_label = tk.Label(self.add_window, text="Symbol:")
        symbol_label.grid(row=0, column=0)

        shares_label = tk.Label(self.add_window, text="Shares:")
        shares_label.grid(row=1, column=0)

        self.symbol_entry = tk.Entry(self.add_window)
        self.symbol_entry.grid(row=0, column=1)

        self.shares_entry = tk.Entry(self.add_window)
        self.shares_entry.grid(row=1, column=1)

        add_button = tk.Button(self.add_window, text="Add", command=self.add_stock_action)
        add_button.grid(row=2, column=1)

    def add_stock_action(self):
        symbol = self.symbol_entry.get()
        shares = int(self.shares_entry.get())
        self.add_stock(symbol, shares)
        self.update_tree()
        self.add_window.destroy()

    def remove_stock_gui(self):
        self.remove_window = tk.Toplevel()
        self.remove_window.title("Remove Stock")

        symbol_label = tk.Label(self.remove_window, text="Symbol:")
        symbol_label.grid(row=0, column=0)

        self.symbol_entry = tk.Entry(self.remove_window)
        self.symbol_entry.grid(row=0, column=1)

        remove_button = tk.Button(self.remove_window, text="Remove", command=self.remove_stock_action)
        remove_button.grid(row=1, column=1)

    def remove_stock_action(self):
        symbol = self.symbol_entry.get()
        self.remove_stock(symbol)
        self.update_tree()
        self.remove_window.destroy()

    def update_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for symbol in self.portfolio.keys():
            value = self.portfolio[symbol]["shares"] * self.portfolio[symbol]["price"]
            self.tree.insert("", "end", text=symbol, values=(symbol, self.portfolio[symbol]["shares"], self.portfolio[symbol]["price"], value))

portfolio = Portfolio()
portfolio.create_gui()
