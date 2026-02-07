### To run FastAPI app: uvicorn main:app --reload

### GET REQ
#  curl -X 'GET' \
#  'http://127.0.0.1:8000/products/' \
#  -H 'accept: application/json'

### POST REQ
#  curl -X 'POST' \
#  'http://127.0.0.1:8000/products/' \
#  -H 'Content-Type: application/json' \
#  -d '{
#    "id": 3,
#    "name": "Super Gadget",
#    "category": "Electronics",
#    "description": "A gadget that does everything",
#    "price": 99.99
#   }'

### PUT REQ
#   curl -X 'PUT' \
#  'http://127.0.0.1:8000/products/1' \
#  -H 'Content-Type: application/json' \
#  -d '{
#    "name": "Updated Widget Pro",
#    "category": "Widgets",
#    "description": "Now with even more features!",
#    "price": 35.99
#   }'

### DELETE REQ
#  curl -X 'DELETE' 'http://127.0.0.1:8000/products/1'

from contextlib import asynccontextmanager
from typing import Annotated, List
from models import Product, ProductRequest
from fastapi import FastAPI, Depends, Path, Query, HTTPException, status
from sql import create_db_and_tables, get_session
from sqlmodel import Session, select


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    print("Starting up resources...")
    yield
    print("Cleaning up resources...")
    # teardown if needed

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(lifespan=lifespan)

# helper to handle pydantic v1/v2 differences
def pydantic_to_dict(pydantic_obj):
    try:
        return pydantic_obj.model_dump()   # pydantic v2
    except AttributeError:
        return pydantic_obj.dict()         # pydantic v1

# Example products list
# PRODUCTS = [
#     Product(1, 'Widget Pro', 'Widgets', 'A high-quality widget', 29.99),
#     Product(2, 'Gadget Max', 'Gadgets', 'A versatile gadget for all your needs', 49.99)
# ]

# Create a product
#@app.post('/products/', status_code=status.HTTP_201_CREATED)
    ### ** is dictonary unpacking -> it takes the keys and values from
    ### a dictionary and "unpacks them as if you had typed them out as
    # named arguments in the function 
    ###"Take every key in this dictionary and match it to the input 
    ### names in the Product class."
    ### .model_dump -> a pydantic method that takes and object and turns
    ### it into a dict
##async def create_product(product_request: ProductRequest):
    ##new_product = Product(**product_request.model_dump())
    #PRODUCTS.append(new_product)

@app.post('/products/', status_code=status.HTTP_201_CREATED)
def create_product(product_request: ProductRequest, session: SessionDep) -> Product:
    product = Product(**product_request.model_dump())  
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

# Read all products
# @app.get('/products/', status_code=status.HTTP_200_OK)
# async def read_all_products():
#     return PRODUCTS

@app.get('/products/', status_code=status.HTTP_200_OK)
def read_all_products(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Product]:
    products = session.exec(select(Product).offset(offset).limit(limit)).all()
    return products

# Read a product by ID
# @app.get('/products/{product_id}', status_code=status.HTTP_200_OK)
# def read_product(product_id: int = Path(gt=0)):
#     for product in PRODUCTS:
#         if product.id == product_id:
#             return product
#     raise HTTPException(status_code=404, detail='Product not found')

@app.get('/products/{product_id}', status_code=status.HTTP_200_OK)
def read_product(product_id: int, session: SessionDep) -> Product:
    product = session.get(Product, product_id)
    if not product: 
        raise HTTPException(status_code=404, detail="Hero not found")
    return product


# Update a product
# @app.put('/products/{product_id}', status_code=status.HTTP_200_OK)
# def update_product(product_id: int, product_request: ProductRequest):
#     for i, product in enumerate(PRODUCTS):
#         if product.id == product_id:
#             updated_product = Product(id=product_id, **product_request.model_dump())
#             PRODUCTS[i] = updated_product
#             return updated_product
#     raise HTTPException(status_code=404, detail='Product not found')

@app.put('/products/{product_id}', status_code=status.HTTP_200_OK)
def update_product(product_id: int, product_data: Product, session: SessionDep):
    # 1. Fetch existing product
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 2. Replace all data
    ### if was going to do patch: update_data = product_data.model_dump(exclude_unset=True)
    update_data = product_data.model_dump()

    # Overwrite every field
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    # 3. Save and return
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product



# Delete a product
# @app.delete('/products/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
# def delete_product(product_id: int):
#     for i, product in enumerate(PRODUCTS):
#         if product.id == product_id:
#             PRODUCTS.pop(i)
#             return
#     raise HTTPException(status_code=404, detail='Product not found')


@app.delete('/products/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()
    return {"ok": True}