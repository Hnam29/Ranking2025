# EdTech Ranking 2025 - Vietnam Market Analysis

A comprehensive ranking system for Vietnamese EdTech platforms, analyzing both websites and mobile applications across multiple criteria.

## 🚀 Features

- **Multi-criteria Evaluation**: Speed, Security, Accessibility, Authority, and Readability
- **Dual Platform Support**: Website and mobile app analysis
- **Interactive Dashboard**: Streamlit-based web interface
- **Secure Database**: MySQL cloud database with environment-based configuration
- **Automated Data Collection**: Web scraping and API integration
- **Vietnamese Market Focus**: Specialized for Vietnamese EdTech landscape

## 🛠️ Technology Stack

- **Backend**: Python, SQLAlchemy, MySQL (Aiven Cloud)
- **Frontend**: Streamlit
- **Data Collection**: BeautifulSoup, Selenium, API integrations
- **Database**: MySQL with SSL encryption
- **Security**: Environment variables for credential management

## 📋 Prerequisites

- Python 3.8+
- MySQL database (Aiven Cloud recommended)
- SSL certificate for database connection

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Hnam29/Ranking2025.git
   cd Ranking2025
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Configure Environment Variables**
   Edit `.env` file with your credentials:
   ```
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_HOST=your_database_host
   DB_DATABASE=your_database_name
   DB_PORT=your_database_port
   SSL_CA_PATH=/path/to/your/ca.pem
   ```

## 🚀 Usage

### Test Database Connection
```bash
python test_env_config.py
```

### Run Streamlit Dashboard
```bash
streamlit run webpages/app.py
```

### Execute Data Collection Scripts
```bash
python Main.py
```

## 📊 Database Schema

The system uses MySQL with the following key tables:
- `dim_ranking_web`: Website evaluation data
- `dim_ranking_app`: Mobile app evaluation data
- `fact_ranking_web`: Aggregated web ranking results
- `fact_ranking_app`: Aggregated app ranking results
- `fact_ranking_app_review`: App reviews data



## 🔒 Security Features

- **Environment Variables**: All sensitive credentials stored in `.env`
- **SSL Encryption**: Secure database connections
- **Gitignore Protection**: Sensitive files excluded from version control
- **Input Validation**: Parameterized queries to prevent SQL injection

## 📁 Project Structure

```
├── webpages/           # Streamlit dashboard
├── Criteria-Scrapers/  # Data collection scripts
├── get_data_from_db.py # Database connection module
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
└── README.md          # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

- **Hnam29** - Initial work and development

## 🙏 Acknowledgments

- Vietnamese EdTech community
- Aiven for cloud database hosting
- Streamlit for the dashboard framework
