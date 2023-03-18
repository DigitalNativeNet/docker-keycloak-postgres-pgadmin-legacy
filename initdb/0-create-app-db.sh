#!/bin/bash

psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'app'" | grep -q 1 || psql -U postgres -c "CREATE DATABASE app"
