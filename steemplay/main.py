import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import WebKit2
from random import Random

import markdown
from steem.steemd import Steemd


steemd_nodes = [
    'https://gtg.steem.house:8090',
]

def big(text):
    return "<big>" + text + "</big>"


class ListBoxRowItem(Gtk.ListBoxRow):
    def __init__(self, entry_id, author, title):
        super(Gtk.ListBoxRow, self).__init__()

        self.entry_id = entry_id

        label_author = Gtk.Label(author)
        label_title = Gtk.Label()

        label_title.set_markup(big(title))
        label_title.set_line_wrap(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        box.pack_start(label_author, True, True, 0)
        box.pack_start(label_title, True, True, 0)

        self.add(box)

class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Steemplay")
        self.addWidgets()
        self.setupSteem()
        self.oldest_entry = 0
        self.feed = []

    def addWidgets(self):
        hbox = Gtk.Box()

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Steemplay"
        self.set_titlebar(hb)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="mail-send-receive-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        hb.pack_end(button)

        button.connect("clicked", self.on_button_clicked)

        self.listbox = Gtk.ListBox()
        self.listbox.connect("row_activated", self.on_row_activated)

        self.content_webview = WebKit2.WebView()

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.content_webview)

        scrolled_window1 = Gtk.ScrolledWindow()
        scrolled_window1.set_min_content_width(350)
        #scrolled_window1.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window1.add(self.listbox)

        hbox.pack_start(scrolled_window1, False, True, 0)
        hbox.pack_start(scrolled_window, True, True, 0)

        self.add(hbox)

    def setupSteem(self):
        self.std = Steemd(nodes=steemd_nodes)

    def on_button_clicked(self, widget):
        self.update_new()

    def on_row_activated(self, listbox, listboxrow):
        i = listboxrow.get_index()
        print(i)
        self.update_webview(i)

    def update_new(self):
        new_feed = self.std.get_feed("dereisele", self.oldest_entry, 6)

        if new_feed == None:
            print("Feed is None")
            return

        print("oldest_entry", self.oldest_entry)
        self.oldest_entry = new_feed[-1]["entry_id"] -1
        self.feed.extend(new_feed)

        for f in new_feed:
            author = f["comment"]["author"]
            title = f["comment"]["title"]
            entry_id = f["entry_id"]

            row = ListBoxRowItem(entry_id, author, title)
            self.listbox.add(row)

        self.listbox.show_all()

    def update_webview(self, id):
        content = self.feed[id]["comment"]["body"]
        html = markdown.markdown(text=content, output_format="html5")
        self.content_webview.load_html(html, "")


if __name__ == "__main__":
    win = MyWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
