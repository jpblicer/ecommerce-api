# E-Commerce API
## Introduction
E-commerce Backend API written with Python(3.10.12) / Django(5.1.2 latest at time of creation) and serves back JSON responses from SQLite database based on RESTful HTTP requests.

**Key Features:**
- Versioned
- Retrieve a list of Items each with name, price and quantity
- allow users to add items to cart
- allow users to checkout items from cart
- supports authenticated or anonymous users
- maintain a reliable count of item quantity
- keep logs to track item purchases with quantities 
- Bilingual message responses (English / Japanese)

## Local Installation

1. clone the repo
`git clone https://github.com/jpblicer/ecommerce-api.git`
2. navigate to the directory
`cd ecommerce-api/ecommerce`/
3. Create the virtual enviornment
`python -m venv venv`
4. Active the virtual enviornment
`source venv/bin/activate`
5. Install required packages
`pip install -r requirements.txt`
6. Run migrations
`python manage.py migrate`

You can then run the server locally with :
`python manage.py runserver`


## Routes
This API provides the following routes which can be accessed by built in Django development tools or others of choice. This Documentation uses curl.

`host/api/v1/items`
`host/api/v1/cart`
`host/api/v1/cart/checkout`

Where host is either a local or remote server location. 
For example if you are running on local host port 8000 and wanted to access the cart you would use the following url
`http://localhost:8000/api/v1/cart/`

More detail about each of the routes provided below.

### Items
Items consist of:
	id : unique provided by database
	name : max length of 100 characters
	price : assumed to be yen and provided as whole integers
	quantity : defaults to zero if not provided
	
To retrieve a list of items from the database you can call a **GET** request on the items route.
```
curl -X GET <HOST>/api/v1/items/

# Would return something like :
[
	{"id":958,"name":"Apple","price":500,"quantity":15},
	{"id":959,"name":"Orange","price":600,"quantity":7}
]
```

**Note:** It will only return Items that have a quantity greater than 0 


### Cart
Cart consist of:
	id : unique provided by database
	user : allowed to be anonymous in this version
	items : which is connected through a join table that keeps the instance of the item and the quantity added to the cart
	
To retrieve a list of items and their quantities in the current users cart you can call a **GET** request on the Cart route.
```
curl -X GET <HOST>/api/v1/cart/

# Would return something like :
[{"item":995,"quantity":1},{"item":992,"quantity":2}]
```


To add an item to the current users cart you can call a **POST** request on the Cart route with the appropriate json header, and the values of item id and quantity.
```
curl -X POST http://localhost:8000/api/v1/cart/ -H "Content-Type: application/json" -d '{"quantity": 2, "item": 992}'

# Would return a respoonse of the item and quantity and store it in the users cart, such as :
{"item":995,"quantity":1},{"item":992,"quantity":2}
```


#### Exceptions
Users will be given alerts for the following cases:
- Tries to request an item not available / or listed
- Tries to request quantity higher than available 
- Tries to request quantity greater than what is possible with current cart quantity and item quantity 

### Checkout
Checkout is a nested route inside of the Cart route and only takes a **POST** request without needing the specify the body or headers.
`curl -X POST http://localhost:8000/api/v1/cart/checkout/`
This will return a checkout successful message or a cart empty message depending on status of users cart; and remove the quantity from the Items table.

#### Exceptions
Users will be given alerts for the following cases:
- Tries to checkout a cart with more quantity than currently in stock

#### Logs
Logs are tracking each cart checkout of the item and quantity purchased as Purchase Records. The logs can be accessed through the Django Admin account or from the server output.

## Messages
Any time responses come back with a message such as in the case of an error; they are provided in Japanese and English.
They can be accessed by the Response data followed by the type of message and preferred language code.
```
Response.data['error']['en']
# Might return : "An error occurred while fetching items."

# The same error with another language code might look like:

Response.data['error']['ja']
# Might return : "アイテムを取得中にエラーが発生しました。" 
```
