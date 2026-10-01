# WEB_REST

A simple REST API project built using **Python, Django, and Django REST Framework**.

## Features

* Add products
* View products
* Product description
* Product price
* Product stock
* Product image upload using Cloudinary

## Technologies

* Python
* Django
* Django REST Framework
* SQLite
* Cloudinary
* Postman

## API

### Add Product

```text
POST /api/add-product/
```

Example:

```json
{
  "name": "Cotton Shirt",
  "description": "Premium cotton shirt",
  "price": "899.00",
  "stock": 50
}
```

### View Products

```text
GET /api/products/
```

## Run Project

```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Server:

```text
http://127.0.0.1:8000/
```


