from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db
from pathlib import Path

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Quantum Contact API",
    description="Backend for Quantum Revolution contact forms",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create templates directory if it doesn't exist
templates_dir = Path("templates")
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Quantum Contact API</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                padding: 3rem;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            h1 {
                font-size: 3rem;
                margin-bottom: 1rem;
                background: linear-gradient(45deg, #ffd700, #ff6b6b);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            a {
                color: #ffd700;
                text-decoration: none;
                margin: 0 1rem;
                padding: 0.5rem 1rem;
                border: 2px solid #ffd700;
                border-radius: 25px;
                transition: all 0.3s ease;
            }
            a:hover {
                background: #ffd700;
                color: #333;
            }
            .links {
                margin: 2rem 0;
            }
            .endpoints {
                background: rgba(0,0,0,0.3);
                padding: 1.5rem;
                border-radius: 10px;
                margin-top: 2rem;
                text-align: left;
            }
            .endpoint {
                margin: 0.5rem 0;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Quantum Contact API</h1>
            <p style="font-size: 1.2rem; margin-bottom: 2rem;">Welcome to the Quantum Revolution backend system</p>
            
            <div class="links">
                <a href="/docs">📚 API Documentation</a>
                <a href="/admin">👨‍💼 Admin Dashboard</a>
                <a href="/api/contacts/">📋 View Contacts</a>
            </div>
            
            <div class="endpoints">
                <h3>🛣️ Available Endpoints:</h3>
                <div class="endpoint">📮 POST /api/contact/ - Submit contact form</div>
                <div class="endpoint">📨 GET /api/contacts/ - Get all contacts</div>
                <div class="endpoint">🔍 GET /api/contacts/{id} - Get specific contact</div>
                <div class="endpoint">✏️ PUT /api/contacts/{id} - Update contact status</div>
                <div class="endpoint">🗑️ DELETE /api/contacts/{id} - Delete contact</div>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Quantum API is running"}

@app.post("/api/contact/", response_model=schemas.Contact)
async def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    db_contact = models.Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.get("/api/contacts/", response_model=list[schemas.Contact])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = db.query(models.Contact).order_by(models.Contact.created_at.desc()).offset(skip).limit(limit).all()
    return contacts

@app.get("/api/contacts/{contact_id}", response_model=schemas.Contact)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.put("/api/contacts/{contact_id}", response_model=schemas.Contact)
async def update_contact(contact_id: int, contact_update: schemas.ContactUpdate, db: Session = Depends(get_db)):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    for field, value in contact_update.dict(exclude_unset=True).items():
        setattr(db_contact, field, value)
    
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.delete("/api/contacts/{contact_id}")
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted successfully"}

@app.get("/admin/", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)