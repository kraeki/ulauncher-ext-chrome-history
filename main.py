from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.Event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.LaunchAction import LaunchAction
import os
import sqlite3
import time

class ChromeHistoryExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener)

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument() or ""
        items = []

        db_path = os.path.expanduser("~/.config/google-chrome/Default/History")
        if not os.path.exists(db_path):
            return [ExtensionResultItem(icon='images/icon.png',
                                        name='Chrome History not found',
                                        description='Ensure Chrome has been used.',
                                        on_enter=LaunchAction("chrome"))]

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT url, title, last_visit_time
                FROM urls
                WHERE title LIKE ? OR url LIKE ?
                ORDER BY last_visit_time DESC
                LIMIT 10;
            """, (f"%{query}%", f"%{query}%"))
            results = cursor.fetchall()
            conn.close()

            for url, title, visit_time in results:
                items.append(
                    ExtensionResultItem(icon='images/icon.png',
                                        name=title if title else url,
                                        description=url,
                                        on_enter=LaunchAction(url))
                )
        except Exception as e:
            items.append(
                ExtensionResultItem(icon='images/icon.png',
                                    name='Error',
                                    description=str(e),
                                    on_enter=LaunchAction("echo 'error'"))
            )

        return items

if __name__ == '__main__':
    ChromeHistoryExtension().run()

