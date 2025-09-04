#!/bin/bash
set -e

# Determine sqlcmd path and flags
SQLCMD=""
if [ -x "/opt/mssql-tools18/bin/sqlcmd" ]; then
  # Tools 18 require -C to trust server cert and -No for non-interactive
  SQLCMD="/opt/mssql-tools18/bin/sqlcmd -C -No"
elif [ -x "/opt/mssql-tools/bin/sqlcmd" ]; then
  SQLCMD="/opt/mssql-tools/bin/sqlcmd"
else
  echo "ERROR: sqlcmd not found in /opt/mssql-tools18/bin or /opt/mssql-tools/bin" >&2
  exit 1
fi

# Start SQL Server in the background
/opt/mssql/bin/sqlservr &

# Function to check if SQL Server is ready
function wait_for_sql_server() {
    echo "Waiting for SQL Server to start..."
    for i in {1..60}; do
        # Check if SQL Server is accepting connections
        if $SQLCMD -S localhost -U sa -P "$SA_PASSWORD" -Q "SELECT 1" -l 3 &> /dev/null; then
            echo "SQL Server is up and running."
            return 0
        fi
        echo "Waiting for SQL Server to start (attempt $i/60)..."
        sleep 1
    done
    echo "Timed out waiting for SQL Server to start."
    return 1
}

# Wait for SQL Server to be ready
wait_for_sql_server

# Run the initialization script
echo "Running initialization script..."
$SQLCMD -S localhost -U sa -P "$SA_PASSWORD" -d master -i /init-db.sql -l 5

# Verify that the Externe user was created successfully
echo "Verifying Externe user creation..."
for i in {1..10}; do
    if $SQLCMD -S localhost -U Externe -P "Secur3P@ssw0rd!" -Q "SELECT 1" -l 3 &> /dev/null; then
        echo "Externe user verified successfully!"
        break
    fi
    echo "Waiting for Externe user to be fully available (attempt $i/10)..."
    sleep 2
    if [ $i -eq 10 ]; then
        echo "Warning: Could not verify Externe user. The application might not work correctly."
    fi
done

# Confirmation message
echo "Initialization script completed successfully!"
echo "Database is now ready to use."

# Keep the container running
wait
