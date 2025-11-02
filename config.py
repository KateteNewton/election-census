import os

class Config:
    # MySQL database configuration for XAMPP
    MYSQL_HOST = 'nkatete.mysql.pythonanywhere-services.com'
    MYSQL_USER = 'nkatete'  
    MYSQL_PASSWORD = 'CensusSICT3'  
    MYSQL_DB = 'nkatete$election_census'
    MYSQL_PORT = 3306
    
    # Secret key for session management
    SECRET_KEY = 'census'
    
    
    ADMIN_USERNAME = 'SICT3Rep'
    ADMIN_PASSWORD = 'Zambia2005@'