import aiomysql
import asyncio
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await aiomysql.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            autocommit=True,
            maxsize=10
        )
        await self._init_tables()

    async def _init_tables(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id BIGINT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    deadline DATE,
                    reminder_type ENUM('standard', 'custom') NOT NULL DEFAULT 'standard',
                    custom_time TIME,
                    custom_days VARCHAR(50),
                    custom_dates TEXT
                );
                """)

    async def add_task(self, user_id, name, description, deadline,
                       reminder_type, custom_time, custom_days, custom_dates):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                INSERT INTO tasks (user_id, name, description, deadline, reminder_type, custom_time, custom_days, custom_dates)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, name, description, deadline, reminder_type, custom_time, custom_days, custom_dates))
                return cur.lastrowid

    async def get_tasks(self, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SELECT * FROM tasks WHERE user_id=%s ORDER BY deadline IS NULL, deadline", (user_id,))
                return await cur.fetchall()

    async def get_task(self, task_id, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SELECT * FROM tasks WHERE id=%s AND user_id=%s", (task_id, user_id))
                return await cur.fetchone()

    async def update_task(self, task_id, user_id, **kwargs):
        fields = []
        values = []
        for key, val in kwargs.items():
            fields.append(f"{key}=%s")
            values.append(val)
        values.extend([task_id, user_id])
        sql = f"UPDATE tasks SET {', '.join(fields)} WHERE id=%s AND user_id=%s"
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, values)

    async def delete_task(self, task_id, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM tasks WHERE id=%s AND user_id=%s", (task_id, user_id))

    async def get_all_tasks(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SELECT * FROM tasks")
                return await cur.fetchall()
