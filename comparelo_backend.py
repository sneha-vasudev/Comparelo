from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

# Dummy user store (replace with database)
users = {
    "test@example.com": "password123"
}

# Scraper for Amazon (public search simulation)
def get_amazon_data(product_name):
    search_url = f"https://www.amazon.in/s?k={product_name.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    result = soup.find("div", {"data-component-type": "s-search-result"})
    if result:
        title = result.h2.text.strip()
        link = "https://www.amazon.in" + result.h2.a["href"]
        price_tag = result.find("span", class_="a-price-whole")
        price = price_tag.text.strip().replace(",", "") if price_tag else "0"
        return {"retailer": "Amazon", "title": title, "price": float(price), "link": link}
    return {"retailer": "Amazon", "title": "Not found", "price": 0.0, "link": search_url}

# Scraper for Flipkart (basic search simulation)
def get_flipkart_data(product_name):
    search_url = f"https://www.flipkart.com/search?q={product_name.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    result = soup.find("a", {"class": "_1fQZEK"})
    if result:
        title = result.find("div", class_="_4rR01T").text.strip()
        link = "https://www.flipkart.com" + result["href"]
        price_tag = result.find("div", class_="_30jeq3 _1_WHN1")
        price = price_tag.text.strip().replace("₹", "").replace(",", "") if price_tag else "0"
        return {"retailer": "Flipkart", "title": title, "price": float(price), "link": link}
    return {"retailer": "Flipkart", "title": "Not found", "price": 0.0, "link": search_url}

# Dummy Myntra data (no open search allowed)
def get_myntra_data(product_name):
    return {
        "retailer": "Myntra",
        "title": product_name.title() + " (Demo)",
        "price": 1599.00,
        "link": f"https://www.myntra.com/{product_name.replace(' ', '-')}"
    }

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    if email in users and users[email] == password:
        return jsonify({"status": "success", "message": "Login successful."})
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route('/compare', methods=['POST'])
def compare_products():
    data = request.json
    product_name = data.get("product_name")
    if not product_name:
        return jsonify({"status": "error", "message": "No product name provided"}), 400
    amazon = get_amazon_data(product_name)
    flipkart = get_flipkart_data(product_name)
    myntra = get_myntra_data(product_name)
    comparison = sorted([amazon, flipkart, myntra], key=lambda x: x["price"])
    return jsonify({"status": "success", "product": product_name, "comparison": comparison})

@app.route('/redirect', methods=['POST'])
def redirect_to_retailer():
    data = request.json
    url = data.get("url")
    if url:
        return redirect(url)
    return jsonify({"status": "error", "message": "No URL provided"}), 400

if __name__ == '__main__':
    app.run(debug=True)