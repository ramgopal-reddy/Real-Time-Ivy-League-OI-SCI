# Real-Time Ivy League Opportunity Intelligence & Student Competency

A comprehensive platform that aggregates real-time academic opportunities from Ivy League universities and matches them to student profiles using AI-powered analysis.

## 🏗️ Architecture

### Backend (FastAPI)
- **RSS Feed Scraper**: Automatically scrapes Ivy League university news feeds
- **AI Analysis**: Uses Google Gemini API to extract structured opportunity data
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Scheduler**: Background tasks for hourly feed updates

### Frontend (Django)
- **User Authentication**: Student registration and login system
- **Opportunity Matching**: AI-powered matching based on student domains
- **Dashboard**: Personalized opportunity recommendations
- **Responsive UI**: Bootstrap-based modern interface

## 🚀 Features

### Backend Features
- **Multi-University Support**: Harvard, Yale, Cornell RSS feeds
- **Smart Filtering**: Keyword-based opportunity detection
- **AI-Enhanced Data**: Gemini API for domain/sub-domain classification
- **Deadline Extraction**: Regex-based deadline parsing
- **RESTful API**: Clean endpoints for frontend integration

### Frontend Features
- **Student Profiles**: Domain and sub-domain specialization tracking
- **Personalized Matching**: Opportunity filtering based on student interests
- **Real-time Updates**: Live data from backend API
- **User-Friendly Interface**: Modern, responsive design

## 📋 Requirements

### Backend Dependencies
```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
apscheduler
python-dotenv
google-genai
feedparser
requests
beautifulsoup4
```

### Frontend Dependencies
```
Django==5.2.11
gunicorn==21.2.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
requests==2.32.5
dj-database-url==2.1.0
```

## 🛠️ Installation & Setup

### Backend Setup
1. Navigate to Backend directory
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key
   DATABASE_URL=your_database_url
   ```
4. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Navigate to Frontend directory
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables:
   ```bash
   SECRET_KEY=your_secret_key
   DEBUG=True
   BACKEND_URL=http://localhost:8000
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Start the server:
   ```bash
   python manage.py runserver
   ```

## 🌐 Deployment

### Render Deployment (Backend)
1. Push Backend folder to GitHub repository
2. Connect to Render
3. Set environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `DATABASE_URL`: PostgreSQL connection string
   - `PYTHON_VERSION`: 3.11.10

### Render Deployment (Frontend)
1. Push Frontend folder to GitHub repository
2. Connect to Render
3. Set environment variables:
   - `BACKEND_URL`: Your deployed backend URL
   - `SECRET_KEY`: Django secret key
   - `PYTHON_VERSION`: 3.11.10

## 📊 Database Schema

### Backend Models
**Opportunity**
- title: String
- university: String
- category: String (internship, research, scholarship, etc.)
- domain: String (AI, ML, Biology, etc.)
- sub_domain: String
- deadline: String
- eligibility: Text
- skills_required: Text
- application_link: String

### Frontend Models
**Student**
- user: One-to-One with Django User
- domain: String (student's academic domain)
- sub_domain: String (specialization)
- created_at: DateTime

## 🔧 API Endpoints

### Backend Endpoints
- `GET /`: Health check
- `GET /opportunities`: Get all opportunities
- `GET /scrape-now`: Manual RSS scrape trigger

### Frontend Routes
- `/`: Home page
- `/register/`: User registration
- `/login/`: User login
- `/dashboard/`: Personalized opportunity dashboard
- `/opportunities/`: Filtered opportunities
- `/all-opportunities/`: All opportunities unfiltered

## 🤖 AI Integration

The system uses Google Gemini API for:
- **Domain Classification**: Categorizing opportunities into academic domains
- **Sub-domain Identification**: Identifying specific specializations
- **Eligibility Analysis**: Extracting eligibility criteria
- **Skills Extraction**: Identifying required skills

## 🔄 Automated Workflow

1. **RSS Scraping** (Every hour):
   - Fetch feeds from Ivy League universities
   - Filter for opportunity-related content
   - Extract basic information

2. **AI Processing** (Limited to 5 calls per scrape):
   - Send opportunity data to Gemini API
   - Extract structured information
   - Update database with enhanced data

3. **Frontend Updates** (Real-time):
   - Fetch opportunities from backend API
   - Filter based on student profiles
   - Display personalized recommendations

## 🎯 Opportunity Categories

- **Internships**: Professional work experience
- **Research**: Academic research positions
- **Scholarships**: Financial aid opportunities
- **Fellowships**: Advanced study programs
- **Conferences**: Academic events and summits
- **Competitions**: Academic contests
- **Events**: Workshops and seminars

## 🔍 Smart Filtering

### Keyword Detection
The system identifies opportunities using keywords like:
- "applications open", "apply now", "call for applications"
- "deadline", "submit application", "register now"

### University Sources
- **Harvard University**: Harvard Gazette RSS feed
- **Yale University**: Yale News RSS feed  
- **Cornell University**: Cornell News RSS feed

## 🚀 Performance Features

- **Rate Limiting**: Gemini API calls limited to prevent overages
- **Caching**: Database caching for frequent requests
- **Error Handling**: Robust error recovery mechanisms
- **Background Processing**: Non-blocking scheduled tasks

## 📱 User Experience

- **Responsive Design**: Works on all devices
- **Real-time Updates**: Live opportunity feeds
- **Personalization**: Custom matching algorithms
- **Easy Navigation**: Intuitive user interface

## 🔐 Security

- **Environment Variables**: Sensitive data in env files
- **CSRF Protection**: Django security features
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **API Key Security**: Secure Gemini API integration

## 📈 Scalability

- **Modular Architecture**: Separate backend/frontend services
- **Database Optimization**: Efficient queries and indexing
- **Load Balancing Ready**: Render auto-scaling support
- **Microservice Pattern**: Independent service deployment

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
- Check the documentation
- Review the code comments
- Create an issue on GitHub

---

**Built with ❤️ for students seeking Ivy League opportunities**
