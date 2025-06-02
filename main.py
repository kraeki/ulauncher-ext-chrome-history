from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.LaunchAction import LaunchAction
from ulauncher.api.client.Event import KeywordQueryEvent

import os
import sqlite3
import logging

logger = logging.getLogger(__name__)

class ChromeHistoryExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, ChromeHistoryQueryEventListener)

class ChromeHistoryQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = (event.get_argument() or "").strip()
        if not query:
            return []

        db_path = os.path.expanduser("~/.config/google-chrome/Default/History")
        if not os.path.exists(db_path):
            return [ExtensionResultItem(
                icon='icon.png',
                name='Chrome History not found',
                description='Make sure Google Chrome has been used.',
                on_enter=LaunchAction("chrome")
            )]

        try:
            # Kopiere die DB (Chrome sperrt im Betrieb)
            tmp_db = "/tmp/chrome_history_copy"
            with open(db_path, "rb") as src, open(tmp_db, "wb") as dst:
                dst.write(src.read())

            conn = sqlite3.connect(tmp_db)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT url, title
                FROM urls
                WHERE title LIKE ? OR url LIKE ?
                ORDER BY last_visit_time DESC
                LIMIT 10;
            """, (f"%{query}%", f"%{query}%"))
            results = cursor.fetchall()
            conn.close()

            items = []
            for url, title in results:
                items.append(
                    ExtensionResultItem(
                        icon='icon.png',
                        name=title if title else url,
                        description=url,
                        on_enter=LaunchAction(url)
                    )
                )
            return items

        except Exception as e:
            logger.exception("Failed to fetch history")
            return [ExtensionResultItem(
                icon='icon.png',
                name='Error',
                description=str(e),
                on_enter=LaunchAction("echo error")
            )]

if __name__ == '__main__':
    ChromeHistoryExtension().run()

