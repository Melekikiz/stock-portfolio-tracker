import tkinter as tk
from tkinter import messagebox
import yfinance as yf
import json
import os
import matplotlib.pyplot as plt


portfolio=[]

def load_portfolio():
    global portfolio
    if os.path.exists("portfolio.json"):
        try:
            with open("portfolio.json", "r") as file:
                portfolio_data =json.load(file)
                portfolio.clear()
                portfolio.extend(portfolio_data)
        except json.JSONDecodeError:
            portfolio.clear()

def save_portfolio():
    with open("portfolio.json", "w") as file:
        json.dump(portfolio, file, indent=4)


def get_current_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist =ticker.history(period="1d")
        if not hist.empty:
            return hist["Close"].iloc[-1]
        else:
            return None
    except Exception:
        return None
    

def fetch_portfolio_value():
    output_text.delete("1.0", tk.END)
    listbox.delete(0, tk.END)
    total_value=0

    for stock in portfolio:
        symbol = stock['symbol']
        amount = stock['amount']
        price = get_current_price(symbol)

        if price is not None:
            value= price*amount
            total_value += value
            output_text.insert(tk.END, f"{symbol}: {amount} shares x ${price:.2f} = ${value:.2f}\n")
            listbox.insert(tk.END, f"{symbol} - {amount} shares")

        else:
            output_text.insert(tk.END, f"{symbol}: Price data not available\n")
            listbox.insert(tk.END, f"{symbol} - ERROR")

    output_text.insert(tk.END, f"\nTotal Portfolio Value: ${total_value:.2f}")


def add_stock():
    symbol = entry_symbol.get().strip().upper()
    amount = entry_amount.get().strip()

    if not symbol or not amount:
        messagebox.showwarning("Warning", "Please enter both symbol and amound.")
        return
    try:
        amount=int(amount)
        for stock in portfolio:
            if stock['symbol']==symbol:
                stock['amount']+= amount
                break
        else:
                portfolio.append({'symbol': symbol, 'amount': amount})

            
        entry_symbol.delete(0, tk.END)
        entry_amount.delete(0, tk.END)
        save_portfolio() 
        fetch_portfolio_value()

    except ValueError:
        messagebox.showerror("Error", "Amount must be a number.")

    
def delete_stock():
    selected_index= listbox.curselection()
    if selected_index:
        index= selected_index[0]
        del portfolio[index]
        save_portfolio()
        fetch_portfolio_value()

    else:
        messagebox.showinfo("Info", "Please select astock to delete.")
       

def edit_stock():
    selected_index= listbox.curselection()
    if selected_index:
        index = selected_index[0]
        new_amount =entry_amount.get().strip()
        if not new_amount:
            messagebox.showinfo("Info", "Please enter the new aount.")
            return
        try:
            new_amount = int(new_amount)
            portfolio[index]['amount'] = new_amount
            entry_symbol.delete(0, tk.END)
            entry_amount.delete(0, tk.END)
            save_portfolio()
            fetch_portfolio_value()
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.")
        else:
            messagebox.showinfo("Info", "Please select a stock to edit.")


def show_portfolio_chart():
    labels =[]
    sizes =[]

    for stock in portfolio:
        symbol = stock['symbol']
        amount = stock['amount']
        price = get_current_price(symbol)
        if price is not None:
            total_value = price*amount
            labels.append(symbol)
            sizes.append(total_value)

    if sizes:
        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title('Portfolio Distribution')
        plt.axis('equal')
        plt.show()

    else:
        messagebox.showinfo("Info", "No valid data to display.")

def auto_refresh():
    fetch_portfolio_value()
    root.after(30000, auto_refresh)


root = tk.Tk()
root.title("Stock Portfolio Tracker")

tk.Label(root, text="Stock Symbol (AAPL, BTC)").pack()
entry_symbol = tk.Entry(root, width=20)
entry_symbol.pack(pady=5)

tk.Label(root, text="Amount of Shares").pack()
entry_amount = tk.Entry(root, width=20)
entry_amount.pack(pady=5)

tk.Button(root, text="Add Stock", command=add_stock).pack(pady=3)
tk.Button(root, text="Edit Stock", command=edit_stock).pack(pady=3)
tk.Button(root, text="Delete Stock", command=delete_stock).pack(pady=3)
tk.Button(root, text="Refresh Prices", command=fetch_portfolio_value).pack(pady=3)
tk.Button(root, text="Show Chart", command=show_portfolio_chart).pack(pady=3)

listbox = tk.Listbox(root, width=40, height=6)
listbox.pack(pady=10)

output_text= tk.Text(root, height=15, width=50)
output_text.pack(pady=10)

load_portfolio()
fetch_portfolio_value()
auto_refresh()

root.mainloop() 