CREATE FILE FORMAT IF NOT EXISTS csv_format
  TYPE = 'CSV'
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE;

CREATE OR REPLACE STAGE snowstage
  FILE_FORMAT = csv_format
  URL = 's3://sp500-companies-analysis/source/';

-- Copy from AWS S3 to Snowflake tables in staging

COPY INTO COMPANIES
FROM @snowstage
FILES = ('companies.csv')
CREDENTIALS = (
    AWS_KEY_ID = 'your_id_here',
    AWS_SECRET_KEY = 'your_key_here'
);

COPY INTO PRICES_WEEKLY
FROM @snowstage
FILES = ('prices_weekly.csv')
CREDENTIALS = (
    AWS_KEY_ID = 'your_id_here',
    AWS_SECRET_KEY = 'your_key_here'
);

COPY INTO INCOME_STMT
FROM @snowstage
FILES = ('income_stmt.csv')
CREDENTIALS = (
    AWS_KEY_ID = 'your_id_here',
    AWS_SECRET_KEY = 'your_key_here'
);

COPY INTO BALANCE_SHEET
FROM @snowstage
FILES = ('balance_sheet.csv')
CREDENTIALS = (
    AWS_KEY_ID = 'your_id_here',
    AWS_SECRET_KEY = 'your_key_here'
);

COPY INTO CASHFLOW
FROM @snowstage
FILES = ('cashflow.csv')
CREDENTIALS = (
    AWS_KEY_ID = 'your_id_here',
    AWS_SECRET_KEY = 'your_key_here'
);

COPY INTO ANALYST_ESTIMATES
FROM @snowstage
FILES = ('analyst_estimates.csv')
CREDENTIALS = (
    AWS_KEY_ID = 'your_id_here',
    AWS_SECRET_KEY = 'your_key_here'
);
