-- Create login if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'Externe')
BEGIN
    CREATE LOGIN [Externe] WITH PASSWORD = 'Secur3P@ssw0rd!', DEFAULT_DATABASE = [master], CHECK_POLICY = ON
END
GO

-- Create user for the login
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'Externe')
BEGIN
    CREATE USER [Externe] FOR LOGIN [Externe]
END
GO

-- Add user to db_owner role
ALTER ROLE db_owner ADD MEMBER [Externe]
GO

-- Grant permissions
GRANT CONNECT SQL TO [Externe]
GO