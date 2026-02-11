import aiosqlite

DB_NAME = 'bot_database.db'

async def create_tables():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS products (
                key TEXT PRIMARY KEY,
                name TEXT,
                file_id TEXT,
                file_id_mac TEXT,
                description TEXT,
                version TEXT,
                version_mac TEXT,
                db_file_id TEXT,
                db_version TEXT
            )
        ''')
        # Migrate: add missing columns for macOS builds if DB existed before
        async with db.execute('PRAGMA table_info(products)') as cursor:
            columns = {row[1] for row in await cursor.fetchall()}
        if 'file_id_mac' not in columns:
            await db.execute('ALTER TABLE products ADD COLUMN file_id_mac TEXT')
        if 'version_mac' not in columns:
            await db.execute('ALTER TABLE products ADD COLUMN version_mac TEXT')
        # Insert default products if not exist
        scout_scope_desc = (
            '*Представь:* все данные об игроках - в одном клике.\n'
            '• Возраст и роль\n'
            '• Steam-профиль и пул карт\n'
            '• Автосбор и порядок в карточках\n'
            'Быстро. Четко. По делу.'
        )
        crm_desc = (
            '*Представь:* ты держишь под контролем все, что ведет к победе.\n'
            '• Эмоции и настрой\n'
            '• Психологическая устойчивость\n'
            '• Игровые аспекты и дисциплина\n'
            'Все собрано в одной системе.'
        )
        await db.execute('INSERT OR IGNORE INTO products (key, name, description) VALUES (?, ?, ?)',
                         ('scout_scope', 'ScoutScope', scout_scope_desc))
        await db.execute('INSERT OR IGNORE INTO products (key, name, description) VALUES (?, ?, ?)',
                         ('crm', 'PerformanceCoach CRM', crm_desc))
        await db.execute('INSERT OR IGNORE INTO products (key, name, description) VALUES (?, ?, ?)',
                         ('cis_bot', 'CIS FINDER BOT', 'Бот для поиска.'))
        await db.execute('UPDATE products SET description = ? WHERE key = ?', (scout_scope_desc, 'scout_scope'))
        await db.execute('UPDATE products SET description = ? WHERE key = ?', (crm_desc, 'crm'))
        await db.commit()

async def add_user(user_id, username, full_name):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)', 
                         (user_id, username, full_name))
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT user_id FROM users') as cursor:
            return [row[0] for row in await cursor.fetchall()]

async def update_product_file(key, file_id, version):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE products SET file_id = ?, version = ? WHERE key = ?', (file_id, version, key))
        await db.commit()

async def update_product_file_mac(key, file_id, version):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE products SET file_id_mac = ?, version_mac = ? WHERE key = ?', (file_id, version, key))
        await db.commit()

async def update_product_db(key, db_file_id, db_version):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE products SET db_file_id = ?, db_version = ? WHERE key = ?', (db_file_id, db_version, key))
        await db.commit()

async def clear_product_file(key):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE products SET file_id = NULL, version = NULL WHERE key = ?', (key,))
        await db.commit()

async def clear_product_file_mac(key):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE products SET file_id_mac = NULL, version_mac = NULL WHERE key = ?', (key,))
        await db.commit()

async def clear_product_db(key):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE products SET db_file_id = NULL, db_version = NULL WHERE key = ?', (key,))
        await db.commit()

async def get_product(key):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM products WHERE key = ?', (key,)) as cursor:
            return await cursor.fetchone()

async def get_all_products():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM products') as cursor:
            return await cursor.fetchall()

async def get_user_count():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT COUNT(*) FROM users') as cursor:
            result = await cursor.fetchone()
            return result[0]
