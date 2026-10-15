from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db import get_db
from app.dependencies import current_user
from app.models import Category, Product, User
from app.schemas import ProductCreate, ProductOutput, ProductUpdate

router = APIRouter(prefix="/api/products", tags=["Produtos"])

@router.get("", response_model=list[ProductOutput])
def list_products(
    search: str | None = Query(default=None, max_length=180),
    active: bool | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(current_user),
):
    query = db.query(Product)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter((Product.name.ilike(term)) | (Product.barcode.ilike(term)))
    if active is not None:
        query = query.filter(Product.active == active)
    return query.order_by(Product.name).offset(offset).limit(limit).all()

@router.post("", response_model=ProductOutput, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db), _: User = Depends(current_user)):
    if data.category_id is not None and not db.get(Category, data.category_id):
        raise HTTPException(status_code=400, detail="Categoria não encontrada")
    product = Product(**data.model_dump())
    db.add(product)
    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe produto com este código de barras")
    return product

@router.get("/{product_id}", response_model=ProductOutput)
def get_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(current_user)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product

@router.patch("/{product_id}", response_model=ProductOutput)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), _: User = Depends(current_user)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    changes = data.model_dump(exclude_unset=True)
    if changes.get("category_id") is not None and not db.get(Category, changes["category_id"]):
        raise HTTPException(status_code=400, detail="Categoria não encontrada")
    for key, value in changes.items():
        setattr(product, key, value)
    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe produto com este código de barras")
    return product
