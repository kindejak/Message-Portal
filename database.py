import sqlite3
import json


class Database:
    # initialize the database for the discord bot
    def __init__(self):
        self.conn = sqlite3.connect("database.db")
        self.create_table_channels()
        self.create_table_server_settings()
        self.default_settings = json.load(open("config.json", "r"))
        

    def create_table_channels(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS channels (server_id INTEGER, server_name TEXT, channel_id INTEGER, channel_name TEXT)")
        self.conn.commit()
        c.close()

    def create_table_server_settings(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS server_settings (server_id INTEGER, settings TEXT)")
        self.conn.commit()
        c.close()

    def set_server_settings(self, server_id, settings):
        json_settings = json.dumps(settings)
        c = self.conn.cursor()
        c.execute("INSERT OR REPLACE INTO server_settings VALUES (?, ?)", (server_id, json_settings))
        self.conn.commit()
        c.close()
        

    def get_server_settings(self, server_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM server_settings WHERE server_id = ?", (server_id,))
        settings = c.fetchone()
        c.close()
        if settings is None:
            self.set_server_settings(server_id, self.default_settings)
            return self.default_settings
        else:
            return json.loads(settings[1])

    def set_channel(self,server_id, server_name, channel_id, channel_name):
        c = self.conn.cursor()
        c.execute("INSERT OR REPLACE INTO channels VALUES (?, ?, ?, ?)", (server_id, server_name, channel_id, channel_name))
        self.conn.commit()
        c.close()

    def get_channel(self, server_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM channels WHERE server_id = ?", (server_id,))
        channel = c.fetchone()
        c.close()
        return channel

    def get_channels(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM channels")
        channels = c.fetchall()
        c.close()
        return channels

    def close(self):
        self.conn.close()