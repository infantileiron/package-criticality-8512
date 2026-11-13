import os
DATABASE_URL=os.getenv('DATABASE_URL','mysql+pymysql://schedule:schedule-demo@db/schedule?charset=utf8mb4')
REDIS_URL=os.getenv('REDIS_URL','redis://redis:6379/0')
JWT_SECRET=os.getenv('JWT_SECRET','package-criticality-development-secret-change')
SEED_DEMO=os.getenv('SEED_DEMO','true').lower()=='true'
